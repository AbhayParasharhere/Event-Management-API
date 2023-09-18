"""
Tests for the user API.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(email='test@example.com', password='test123',
                name='Test User', **extra_args):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password,
                                                name=name, **extra_args)


class PublicUserAPITests(TestCase):
    """Tests for the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'test123',
            'name': 'Test User',
            'bio': 'Test Bio',
            'phone': '1234567890'
        }
        res = self.client.post(USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', res.data)
        self.assertTrue(get_user_model().objects.get(
            email=payload['email']).check_password(payload['password']))
        for attr, value in payload.items():
            if attr != 'password':
                self.assertEqual(res.data[attr], value)

    def test_with_email_exists_error(self):
        """Test that creating user with existing email returns error."""
        email = 'test1@example.com'
        create_user(email=email)

        payload = {
            'email': email,
            'password': 'testPass123',
            'name': 'Test Pass'
        }

        res = self.client.post(USER_URL, payload)

        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(get_user_model().objects.filter(
            email=email).count(), 1)

    def test_password_too_short_error(self):
        """Test short password less than 5 chars returns an error"""
        payload = {
            'email': 'test@example.com',
            'password': '123',
            'name': 'test user'
        }

        res = self.client.post(USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(get_user_model().objects.filter(
            email=payload['email']).exists())

    def test_create_token(self):
        """Test creating a user with the user details."""
        email = 'test@example.com'
        password = 'test1234'
        payload = {
            'email': email,
            'password': password
        }
        create_user(email=email, password=password)

        res = self.client.post(TOKEN_URL, payload)

        self.assertTrue(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_bad_credentials(self):
        """Test token is not created with bad credentials."""
        create_user(email='test@example.com', password='test1234')

        payload = {
            'email': 'test@example.com',
            'password': 'test123'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_blank_password(self):
        """Test creating a token fails on blank password."""
        create_user(email='test@example.com', password='test1234')
        payload = {
            'email': 'test@example.com',
            'password': ''
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)
