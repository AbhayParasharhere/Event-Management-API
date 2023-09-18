"""
Models definition for APIs.
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    """Manager for the user model."""

    def create_user(self, email, password=None, **extra_fields):
        """Creates users in the system."""
        if not email:
            raise ValueError('Email is required for user creation')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, **user_data):
        """Creates super user in the system. """
        user = self.create_user(**user_data)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Model for users."""
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=10, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
