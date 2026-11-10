# Dockerfile: the recipe for building your app's image.
# Each line is one step. Docker caches steps, so order matters for speed.

# TODO 1: start from an official slim Python 3.12 image.   (FROM ...)
FROM python:3.12-slim


ENV PYTHONDONTWRITEBYTECODE=1 \ 
#do not cache - useless for docker
    PYTHONUNBUFFERED=1
#print log immediately for cloudwatch   


# TODO 2: set the working directory inside the image to /app.   (WORKDIR ...)
WORKDIR /app

# TODO 3: create a non-root user named "app".
# Hint: RUN useradd --system app
RUN useradd --system app


# TODO 4: copy ONLY requirements.txt first, then pip install it.

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .
RUN python manage.py collectstatic 

#chown = change ownership of a file or directory. assign by root
RUN mkdir -p /app/media && chown app:app /app/media 

#dockerfile before user app is owned by root. now app can access the media folder. 
 

USER app 


USER app
EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-"]
#run this when docker compose up 
#front door in django config, wsgi.py file and under application name

#Docker      → starts the container, runs the CMD
#Gunicorn    → receives requests, passes them through the front door. Gunicorn listen on port 8000. docker forward to it
#Django      → (config.wsgi:application) → middleware → urls → views

