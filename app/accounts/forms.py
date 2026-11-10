"""
forms.py: the sign-up form.

Django already has UserCreationForm (username + password + confirm password,
with password checks built in). We extend it to also ask for an email.
"""

from django import forms
from django.contrib.auth.password_validation import validate_password

from .models import User


# this form read request coming in and convert it to .get("username,...")
class SignUpForm(
    forms.Form
):  # form.Forms is built-in Django that provide cleaned_data, {{form.as_p}},...
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(label="password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="confirm password", widget=forms.PasswordInput)
    phone = forms.CharField(max_length=16, required=False)  # ← ADD
    profile_picture = forms.ImageField(required=False, label="Profile picture")  # ← ADD

    def clean_username(self):
        username = self.cleaned_data["username"]  # dictionary with cleaned data is value
        if User.objects.filter(
            username__iexact=username
        ).exists():  # ORM django -> select SQL in POSTGRES
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email is already exists.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError("The two passwords don't match. Try again")
        validate_password(
            password2
        )  # validate rule from setting.py, Django function that have pw rule
        return password2

    def clean_profile_picture(self):  # Django looks for clean_ + the field name
        profile_picture = self.cleaned_data.get("profile_picture")
        if profile_picture and profile_picture.size > 2 * 1024 * 1024:  # 2 MB max
            raise forms.ValidationError("Image must be smaller than 2 MB.")
        return profile_picture

    def save(self):  # Usertable in models. (import models above)
        return User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
            phone=self.cleaned_data["phone"],  #
        )


class AvatarForm(forms.ModelForm):  # modelform is a class Meta that have save()
    class Meta:
        model = User  # which user id to save
        fields = ["profile_picture"]  # which field to save
        widgets = {
            "profile_picture": forms.FileInput(
                attrs={
                    "accept": "image/*",
                    "onchange": "this.form.submit()",
                }
            ),
        }  # only the picture

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get("profile_picture")
        if profile_picture and profile_picture.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Image must be smaller than 2 MB.")
        return profile_picture
