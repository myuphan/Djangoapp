"""
accounts/urls.py: the addresses for the accounts app.

Each path(...) = URL  ->  view  ->  name.
The name lets you refer to the page anywhere (redirect("home"),
{% url 'login' %} in templates) without hard-coding the address.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),  # use in base.html and login.html
    path("logout/", views.logout_view, name="logout"),  # use in base.html
    path(
        "password-reset/", views.PasswordReset.as_view(), name="password_reset"
    ),  # turn a class to a normal view funtion
    path("password-reset/sent/", views.PasswordResetSent.as_view(), name="password_reset_done"),
    path(
        "reset/<uidb64>/<token>/",
        views.PasswordResetConfirm.as_view(),
        name="password_reset_confirm",
    ),
    path("reset/done/", views.PasswordResetComplete.as_view(), name="password_reset_complete"),
    path("profile/picture/", views.change_profile_picture, name="change_profile_picture"),
    path("profile/picture/delete", views.delete_profile_picture, name="delete_profile_picture"),
]
