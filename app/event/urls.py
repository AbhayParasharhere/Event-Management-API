"""
Urls for the event api.
"""

from django.urls import (
    path,
    include
)
from rest_framework.routers import DefaultRouter

from event import views

router = DefaultRouter()
router.register('organized-events', views.OrganizedEventViewSet)

app_name = 'event'

urlpatterns = [
    path('organized-events/', include(router.urls)),
]
