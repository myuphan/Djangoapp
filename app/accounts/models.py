# this file describe data table
from django.contrib.auth.models import (
    AbstractUser,  # Abtractuser come with username,email and password filed
)
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=16, blank=True)
    profile_picture = models.ImageField(
        upload_to="avatars/", blank=True
    )  # subfolder inside MEDIA_ROOT in setting
