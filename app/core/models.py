"""
Models definition for APIs.
"""

from django.db import models
from django.conf import settings
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
    bio = models.TextField(blank=True, default='')
    phone = models.CharField(max_length=10, blank=True, default='')

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Event(models.Model):
    """Model for event."""
    title = models.CharField(max_length=255)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    description = models.TextField(blank=True, default='')
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=255)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2,)
    max_attendees = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.title
