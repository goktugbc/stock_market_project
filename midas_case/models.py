import datetime

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.utils import timezone


class AppleUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            username=self.username,
        )

        user.set_password(password)
        user.save()
        return user


class AppleUser(AbstractBaseUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        "username",
        max_length=150,
        unique=True,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[username_validator],
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )
    number_of_apples = models.PositiveIntegerField(default=0)
    objects = AppleUserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username