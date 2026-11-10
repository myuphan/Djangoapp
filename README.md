# Django Sign-up App: Build Guide

You write the code. Every file you need to fill in has `TODO` comments with hints.
If you get stuck, compare with the same file in the **solution** folder.

## The folder

```
django-signup/
├── app/                      ← the website (goes inside the Docker image)
│   ├── manage.py             GIVEN   Django's command tool
│   ├── config/               project-wide setup
│   │   ├── settings.py       TODO    configuration, read from env vars
│   │   ├── middleware.py     TODO    /health/ for the load balancer
│   │   ├── urls.py           TODO    main URL map
│   │   └── wsgi.py           GIVEN   entry point for gunicorn
│   ├── accounts/             the sign-up / login feature
│   │   ├── forms.py          TODO    sign-up form (adds email)
│   │   ├── views.py          TODO    signup + home pages
│   │   ├── urls.py           TODO    /, /signup/, /login/, /logout/
│   │   └── tests.py          TODO    1 example given, you write 7
│   ├── templates/
│   │   ├── base.html         GIVEN   shared layout (header + nav)
│   │   ├── login.html        TODO
│   │   ├── signup.html       TODO
│   │   └── home.html         TODO
│   └── static/style.css      GIVEN
├── Dockerfile                TODO    recipe for the image
├── docker-compose.yml        TODO    Postgres + web together
├── .env.example              GIVEN   copy to .env
├── requirements.txt          GIVEN   packages the app needs to run
├── requirements-dev.txt      GIVEN   + pytest, ruff (not in the image)
├── pyproject.toml            GIVEN   ruff + pytest settings
├── .gitignore                GIVEN   keeps .env, .venv out of GitHub
└── .dockerignore             GIVEN   keeps junk out of the image
```

`__init__.py` files are empty. They just tell Python "this folder is a package."

## Build order

Do the steps in order. Each one ends with a **check** so you know it works before moving on.

### Step 0: Set up (5 min)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
git init
```

### Step 1: Settings (`app/config/settings.py`)

Do **TODO 1, 2 and 5**. Leave TODO 3 and 4 for later steps.

### Step 2: Health check (`app/config/middleware.py`)

Write the middleware, then do **settings TODO 3** to switch it on.

### Step 3: URLs (`app/config/urls.py`, `app/accounts/urls.py`)

### Step 4: Form and views (`app/accounts/forms.py`, `app/accounts/views.py`)

### Step 5: Templates (`login.html`, `signup.html`, `home.html`)

**Check: run the site on your laptop (SQLite, no Docker yet)**

```bash
cd app
python manage.py migrate
DJANGO_DEBUG=true python manage.py runserver
```

On Windows PowerShell, set the variable first: `$env:DJANGO_DEBUG="true"`.

- http://127.0.0.1:8000/ should send you to the login page.
- Sign up, log out, log back in.
- http://127.0.0.1:8000/health/ should say `ok`.

### Step 6: Tests (`app/accounts/tests.py`)

Read the example test, then write the 7 TODO tests.

**Check** (from the project root, not `app/`):

```bash
pytest
ruff check .
```

All 8 tests should pass, and ruff should report no errors.

### Step 7: Postgres (`settings.py` TODO 4)

Write the `if/else` around `DATABASES`.

**Check:** run `pytest` again. Still passes? Good. With no `POSTGRES_HOST` set, it still uses SQLite.

### Step 8: Dockerfile

**Check:**

```bash
docker build -t django-signup .
docker images                      # you should see django-signup
```

### Step 9: docker-compose.yml

**Check: the full stack**

```bash
cp .env.example .env
docker compose up --build
```

- http://localhost:8000 should work like before, but your users are now saved in Postgres.
- In a second terminal:

```bash
curl http://localhost:8000/health/
docker compose exec db psql -U app -d app -c "select username, email from auth_user;"
```

Stop with `Ctrl+C`, then `docker compose down`. Add `-v` to also delete the database.

### Step 10: Push to GitHub

```bash
git add .
git status            # make sure .env and .venv are NOT listed
git commit -m "Django sign-up app with Docker"
```

Create a repo on GitHub and push. Next up: CI with GitHub Actions.

## Common errors

| Error | Usual cause |
|---|---|
| `TypeError: ... 'ellipsis'` | A `...` placeholder is still in settings.py. |
| `NoReverseMatch: 'home' not found` | URL `name=` missing or misspelled in `accounts/urls.py`. |
| `TemplateDoesNotExist` | Template filename doesn't match what the view renders. |
| `CSRF verification failed` | `{% csrf_token %}` missing inside a `<form>`. |
| `400 Bad Request` | The host isn't in `DJANGO_ALLOWED_HOSTS`. |
| Page loads but has no styling | Run with `DJANGO_DEBUG=true` locally. In Docker, `collectstatic` handles it. |
| `could not translate host name "db"` | You ran Django outside Docker with `POSTGRES_HOST=db` set. Only Docker knows the name `db`. |




Before request
RUN python manage.py runserver
Gunicorn starts
  → config/wsgi.py           "use config.settings"
  → config/settings.py       loads everything: apps, MIDDLEWARE list, database, templates...
  → Django builds the middleware chain (the nesting dolls)
  → ready, waiting on port 8000


Every request
1. Browser
   │  POST /login/  (username + password + CSRF token + cookie)
   ▼
2. [AWS later: Load balancer → container]   [Laptop: Docker port 8000 → container]
   ▼
3. Gunicorn                          receives the raw request on port 8000
   ▼
4. config/wsgi.py                    hands it to Django; Django builds the `request` object
   ▼
5. MIDDLEWARE (going in, top → bottom, from settings.py)
   │  config/middleware.py  HealthCheck   → not /health/ → get_response
   │  SecurityMiddleware
   │  WhiteNoiseMiddleware               → not a CSS file → pass on
   │  SessionMiddleware                  → reads the session cookie
   │  CommonMiddleware
   │  CsrfViewMiddleware                 → checks the CSRF token ✅
   │  AuthenticationMiddleware           → sets request.user (anonymous for now)
   │  MessageMiddleware
   │  XFrameOptionsMiddleware
   ▼
6. config/urls.py                    admin/? no → "" → include accounts.urls decide which function in view is used
   ▼
7. accounts/urls.py                  "login/" → views.login_view
   ▼
8. accounts/views.py return HTML       POST → authenticate(username, password)
   │                                    → database (from settings DATABASES → Postgres)
   │                                    → password correct → login() → session saved
   │                                    → return redirect("home")
   ▼
9. MIDDLEWARE (coming out, bottom → top)
   │  SessionMiddleware                  → sets the new session cookie on the response
   │  SecurityMiddleware                 → adds security headers
   │  ...
   ▼
10. Gunicorn                         sends the response back over the network
   ▼
11. Browser                          gets "redirect to /" → makes a NEW request: GET /

Continue new request(same 1-7)
7. accounts/urls.py      "" → views.home
8. accounts/views.py     home: @login_required → logged in ✅
                         → render(request, "home.html")
   ▼
8b. templates/home.html  extends base.html
                         context processors add `user` → "Welcome, nhi!"
                         {% static 'style.css' %} → adds a link to the CSS file
   ▼
9–11. back through middleware → Gunicorn → browser shows the page


How Logic work in views.py

HTML  ──(knows only a URL)──→  urls.py  ──(links URL to function)──→  views.py

path("signup/", views.signup, name="signup"),

PARTII:
Connect to database
Django (ORM) --> psycopg (driver) --> postgres

Explain settings.AUTH_USER_MODEL

we have Django's app have a folder name auth. Inside auth we have class User that is a table contain password, eamil as parameter. We point AUTH_USER_MODEL in settings (Django) to auth.user for easy to use. 
user is an object like Nhi then user.email
table is auth_user

python manage.py makemigrations accounts //double check on folder accounts what is new
python manage.py migrate// read all migrationfile from every app and ran. ran new one only and translate to SQL
if we add new column need run again


#FORM.py, VIEW.py and html relationship

Form = where you write the rules for the input (and how to save it)
View = runs form.is_valid(), then decides what to send back:

form.is_valid()	View returns
✅ True	usually a redirect to another page (e.g. home)
❌ False	render the same HTML again, with the error messages
(first visit, GET)	render the HTML with an empty form

#CSFR, SECRECT, Cookie (session id and csrf token)
The wristband is created for each user while they log in (abc123)
In view.py login(request,user) -> create a cookie
In settings.py sessionmiddleware carry the cookies all over the website. no need to input login
Cookies follow along the request
SESSION_COOKIE_PATH = "/"

SECRECT
real data+secrect -> signature
Signature is used for password request token and no body can steal them because secrect is generate by auth dev
One key per website and stay the same
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-insecure-key")
store secrect in env.file
load dotenv to read secrect

CSRF : prevent fake form

when use {% csrf_token %} generate a token cookie and hidden box in form.
When submit form must match the cookie ( on every POST  Csrf viewmiddleware check the match)

How password reset link is made?


http://localhost:8000/reset/Mw/d1k2mn-8f3a9c1e.../
                            ↑   ↑      ↑
                          who  time   signature

Create admin

