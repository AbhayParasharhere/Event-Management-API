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
ALL_EVENTS_URL = reverse('event:all-events')


def event_detail_url(event_id):
    """Get and return a detail event url."""
    return reverse('event:event-detail', args=[event_id])


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
        self.user = create_user()

    def test_auth_required(self):
        """Test auth is required for the event api."""
        res = self.client.get(EVENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_view_all_events(self):
        """Test that the user can view can existing events."""
        e1 = create_event(organizer=self.user)
        user2 = create_user(
            email='test2@example.com',
            name='Test User 2'
        )
        e2 = create_event(organizer=user2)
        res = self.client.get(ALL_EVENTS_URL)

        events = Event.objects.all().order_by('-id')
        serializer = serializers.EventSerializer(events, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0]['title'], e2.title)
        self.assertEqual(res.data[1]['title'], e1.title)


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

    def test_get_event_detail(self):
        """Test retrieving event details."""
        event = create_event(
            organizer=self.user,
            description="Sample description"
        )
        url = event_detail_url(event.id)

        res = self.client.get(url)

        serializer = serializers.EventDetailSerializer(event)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data['description'], event.description)

    def test_create_event(self):
        """Test that an event is created."""
        payload = {
            'title': 'Sample Event',
            'time': '23:00',
            'date': '2023-03-14',
            'venue': 'Online',
            'ticket_price': Decimal('12.65')
        }
        res = self.client.post(EVENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        event = Event.objects.get(organizer=self.user)
        serializer = serializers.EventDetailSerializer(event)

        self.assertEqual(serializer.data, res.data)
        for attr, value in payload.items():
            if attr != 'time' and attr != 'date':
                self.assertEqual(getattr(event, attr), value)
            elif attr == 'date':
                self.assertEqual(
                    getattr(event, attr).strftime('%Y-%m-%d'), value
                )
            elif attr == 'time':
                self.assertEqual(
                    getattr(event, attr).strftime('%H:%M'), value
                )

    def test_partial_updates(self):
        """Test partial updates of event."""
        original_venue = 'Online'
        event = create_event(
            organizer=self.user,
            venue=original_venue,
        )
        payload = {
            'title': 'Updated Event'
        }

        url = event_detail_url(event.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], payload['title'])
        self.assertEqual(res.data['venue'], original_venue)

    def test_full_update(self):
        """Test updating all properties of an event."""
        event = create_event(
            organizer=self.user,
            title='Event 1',
            venue='Online',
            ticket_price=Decimal('12.65'),
            date='2023-03-14',
            time='23:00',
            max_attendees=10,
        )
        payload = {
            'title': 'Updated Event',
            'venue': 'Zoom',
            'ticket_price': Decimal('15.65'),
            'date': '2023-03-15',
            'time': '23:30',
            'max_attendees': 20,
        }
        url = event_detail_url(event.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        event.refresh_from_db()

        for attr, value in payload.items():
            if attr != 'time' and attr != 'date':
                self.assertEqual(getattr(event, attr), value)
            if attr == 'time':
                self.assertEqual(getattr(event, attr).strftime('%H:%M'), value)
            if attr == 'date':
                self.assertEqual(
                    getattr(event, attr).strftime('%Y-%m-%d'), value)
        self.assertEqual(event.organizer, self.user)

    def test_delete_event(self):
        """Test deleting an event."""
        event = create_event(organizer=self.user)
        url = event_detail_url(event.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        events_filter = Event.objects.filter(organizer=self.user)
        self.assertEqual(len(events_filter), 0)

    def test_delete_other_user_event_fails(self):
        """Test that the user cannot delete other user's event."""
        user2 = create_user(
            email='test2@example.com',
            name='Test User 2'
        )

        event = create_event(organizer=user2)
        url = event_detail_url(event.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Event.objects.filter(organizer=user2).exists())
