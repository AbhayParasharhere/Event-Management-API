"""
Tests for the event api.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Event
from event import serializers

EVENTS_URL = reverse('event:event-list')


def create_user(
        name='Test User',
        email='test@example.com',
        password='test123',
        **extra_args):
    """Create and return a user."""
    return get_user_model().objects.create_user(
        name=name,
        email=email,
        password=password,
        **extra_args
    )


def create_event(organizer, **params):
    """Create and return a sample event."""
    default = {
        'title': 'Event 1',
        'venue': 'Online',
        'ticket_price': Decimal('12.95'),
        'date': '2023-12-22',
        'time': '13:00',
    }

    default.update(params)

    event = Event.objects.create(organizer=organizer, **default)
    return event


class PublicEventApiTests(TestCase):
    """Tests for the unauthozied API requests to the event API."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for the event api."""
        res = self.client.get(EVENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateEventApiTests(TestCase):
    """Tests for the authorized API requests to the event API."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_list_organized_events(self):
        """Test that all events for a user are listed."""
        Event.objects.create(
            title='Event 1',
            organizer=self.user,
            venue='Online',
            ticket_price=Decimal('12.95'),
            date='2023-12-23',
            time='13:00',
        )
        Event.objects.create(
            title='Event 2',
            organizer=self.user,
            venue='Zoom',
            ticket_price=Decimal('14.24'),
            date='2023-12-14',
            time='22:00',
        )

        res = self.client.get(EVENTS_URL)
        events = Event.objects.all().order_by('-id')
        serializer = serializers.EventSerializer(events, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_organized_event_list_limited_to_user(self):
        """Test retrieved list of events organized is limited
        to the authenticated user"""
        Event.objects.create(
            title='Event 1',
            organizer=self.user,
            venue='Online',
            ticket_price=Decimal('12.95'),
            date='2023-12-22',
            time='13:00',
        )
        user2 = create_user(
            name='User 2', email='user2@example.com', password='test123'
        )
        Event.objects.create(
            title='Event 2',
            organizer=user2,
            venue='Zoom',
            ticket_price=Decimal('14.24'),
            date='2023-12-30',
            time='22:00',
        )

        res = self.client.get(EVENTS_URL)
        events = Event.objects.filter(organizer=self.user)
        serializer = serializers.EventSerializer(events, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
