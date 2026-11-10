"""
tests.py: automatic checks that the site works. CI runs these on every PR.
Run them with:  pytest

Pattern for every test:
  1. ARRANGE: set things up (e.g. create a user)
  2. ACT:     do the thing (e.g. post to /login/)
  3. ASSERT:  check the result (status code, database, session)

`client` is a fake browser pytest-django gives you.
Status codes: 200 = page shown, 302 = redirected, 400 = bad request.
"""

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from accounts.models import User

PASSWORD = "S3cure-Passw0rd!"


# A "fixture": any test that lists `user` as a parameter gets this user created.
@pytest.fixture
def user(db):
    return User.objects.create_user(username="alex", email="alex@example.com", password=PASSWORD)


# --- EXAMPLE (given): copy this pattern for the TODO tests -----------------------
@pytest.mark.django_db  # this test touches the database
def test_signup_creates_user_and_logs_in(client):
    # ACT
    response = client.post(
        "/signup/",
        {
            "username": "newuser",
            "email": "new@example.com",
            "password1": PASSWORD,
            "password2": PASSWORD,
        },
    )
    print(response.status_code, response.get("Location"))
    # ASSERT
    assert response.status_code == 302  # redirected = success signup valid form SUBMIT
    assert User.objects.filter(
        username="newuser"
    ).exists()  # ORM query make sure username now in db(check accoutn created)
    assert (
        client.get("/").status_code == 200
    )  # the sign up also logged user in, plus wrist band + fake browser


def test_signup_rejects_duplicate_email(client, user):
    response = client.post(
        "/signup/",
        {
            "username": "failuser",
            "email": "alex@example.com",
            "password1": PASSWORD,
            "password2": PASSWORD,
        },
    )
    assert response.status_code == 200  # return dup?
    assert not User.objects.filter(username="failuser").exists()  # python--user db #PRINT MESSGAE?


#     Sign up with email "NHI@example.com" (same as the fixture, different case).
#     Expect: status 200 (form shown again with error), still only 1 user.
def test_login_works(client, user):
    response = client.post(
        "/login/",
        {"username": "alex", "password": PASSWORD},
    )
    assert response.status_code == 302  # redirect


def test_login_wrong_password(client, user):
    response = client.post("/login/", {"username": "alex", "password": "wrongpassword"})
    assert response.status_code == 200  # log in page show again
    assert b"invalid username or password." in response.content
    assert "_auth_user_id" not in client.session  # not logged in (bandwrist)


# When user enter / home url without log in
@pytest.mark.django_db
def test_not_login_direct(client):
    response = client.get("/")
    assert "_auth_user_id" not in client.session
    assert response.status_code == 302  # redirect to login
    assert "/login/" in response.url


def test_health_works_with_private_ip(client):
    response = client.get("/health/", HTTP_HOST="10.0.1.23")  # pretend to be the AWS load balancer
    assert response.status_code == 200
    assert response.content == b"ok"


def test_other_pages_reject_unknown_host(client):
    response = client.get("/signup/", HTTP_HOST="bad.example.com")
    assert response.status_code == 400


def test_upload_picture(client, user, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path  # test pictures go to a temp folder
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), "red").save(buffer, format="PNG")
    image = SimpleUploadedFile("pic.png", buffer.getvalue(), content_type="image/png")

    client.force_login(user)
    response = client.post("/profile/picture/", {"profile_picture": image})

    assert response.status_code == 302  # saved → redirected home
    user.refresh_from_db()
    assert user.profile_picture.name.startswith("avatars/")
