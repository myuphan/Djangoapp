from django.contrib import admin  # admin sys
from django.contrib.auth.admin import UserAdmin  # admin page include filter change pw

from .models import User  # for admin register


@admin.register(User)
class CustomUserAdmin(UserAdmin):  # Allow admin edit user -> settin of a screen
    fieldsets = UserAdmin.fieldsets + (("Profile", {"fields": ("phone", "profile_picture")}),)
