"""
Admin panel page.
"""

from django.contrib import admin  # noqa
from core import models

admin.site.register(models.User)
admin.site.register(models.Event)
