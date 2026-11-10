"""
settings.py: the main configuration for the whole Django project.

KEY IDEA: anything that is different between your laptop and AWS
(debug mode, secret key, database password...) is read from an
ENVIRONMENT VARIABLE with os.environ.get(). That way the same Docker
image runs everywhere; only the env vars change.

The parts marked "GIVEN" are standard Django boilerplate.
The parts marked TODO are yours to write.
"""

import os
from pathlib import Path

BASE_DIR = (
    Path(__file__).resolve().parent.parent
)  # parent of folder contain settings.py, which is config/, then parent of that, which is app/


DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"  # hide bugs from users
SECRET_KEY = os.environ.get("DJANGO_SECRECT_KEY", "dev-only-insecure-key")  # per web, right to edit
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost, 73.6.72.66").split(",")

# GIVEN: the AWS load balancer handles HTTPS and tells Django via this header.
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)  # The setting ("HTTP_X_FORWARDED_PROTO", "https") tells ALB: “If the X-Forwarded-Proto header equals https, treat the request as secure.”


# if not DEBUG:
# Behind the ALB
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# SECURE_SSL_REDIRECT = True

# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True


# SECURE_HSTS_SECONDS = 3600
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
]


MIDDLEWARE = [
    "config.middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",  # ← this one is missing
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# GIVEN
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"  # where is the front door that take request

TEMPLATES = [  # where is HTML
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",  # info current visit. activate request.path
                "django.contrib.auth.context_processors.auth",  # enable user.username
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

if os.environ.get("POSTGRES_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "app"),
            "USER": os.environ.get("POSTGRES_USER", "app"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
            "HOST": os.environ["POSTGRES_HOST"],
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {  # connect db to sqlite3
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# GIVEN: password rules for sign-up
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]

# Django built in name
LOGIN_URL = "login"  # in account.url
LOGIN_REDIRECT_URL = "home"  # home must exist in account.urls to make redicrect work
LOGOUT_REDIRECT_URL = "login"


# GIVEN: static files (CSS), served by WhiteNoise
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # `collectstatic` copies files here
STATICFILES_DIRS = [BASE_DIR / "static"]  # where YOUR css lives
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

USE_TZ = True
TIME_ZONE = "America/Chicago"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


MEDIA_URL = "media/"  # for user uploaded files, like profile pics. POSTGRES app/media in docker volume. Used by browser to access media files.

MEDIA_ROOT = (
    BASE_DIR / "media"
)  # used by django to store user uploaded files. POSTGRES app/media in docker volume

# for testing purpose
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@signup-app.local"

AUTH_USER_MODEL = "accounts.User"  # point accounts to User table
