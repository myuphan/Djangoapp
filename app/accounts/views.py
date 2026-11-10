"""
views.py: the logic behind each page.
A view receives a request and returns a response (usually an HTML page).

Login and logout use Django's built-in views (see accounts/urls.py),
so you only write two views here.
"""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import AvatarForm, SignUpForm

# ACTION: click signup button and def signup run hit render


def signup(request):  # form already existed

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():  # check typed data in the form
            user = form.save()  # call User.objects.create_user(...)
            login(request, user)  # log user in now
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})  # use request to fill in html


# click login -> log in run hit render
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request, username=username, password=password
        )  # compare with db in setting #this replace form

        if user is not None:  # after correct credentials
            login(request, user)  # session cookie
            return redirect("home")
        messages.error(
            request, "invalid username or password."
        )  # save the error note on the new render page
    return render(request, "login.html")  # when method is not "POST" --> "GET"

    # log_in-- give a cookies


@login_required
def home(request):  # just opened the page: show the form

    return render(request, "home.html")


@login_required
def change_profile_picture(request):
    if request.method == "POST":
        form = AvatarForm(
            request.POST,  # CSRF token
            request.FILES,  # file submit
            instance=request.user,  # create a whole user object for modelform in form to save
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Profile picture updated!")
            return redirect("home")

    else:
        form = AvatarForm(instance=request.user)

    return render(request, "change_profile_picture.html", {"form": form})


@login_required
def delete_profile_picture(request):
    if request.method == "POST" and request.user.profile_picture:
        request.user.profile_picture.delete(save=True)
        messages.success(request, "Profile picture removed.")
    return redirect("home")


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("login")


class PasswordReset(auth_views.PasswordResetView):
    template_name = "password_reset.html"


class PasswordResetSent(auth_views.PasswordChangeDoneView):
    template_name = "password_reset_sent.html"


class PasswordResetConfirm(auth_views.PasswordResetConfirmView):
    template_name = "password_reset_confirm.html"


class PasswordResetComplete(auth_views.PasswordResetCompleteView):
    template_name = "password_reset_complete.html"
