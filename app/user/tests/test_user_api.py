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
ME_URL = reverse('user:me')


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

    def test_retrieve_user_details_unauthorized_fails(self):
        """Test retreiving user details in unauthorized request fails. """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('email', res.data)


class PrivateUserApiTests(TestCase):
    """Authorized requests test for the user api."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retreive_user_details(self):
        """Test retreiving user details for the authenticated user."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name,
            'bio': self.user.bio,
            'phone': self.user.phone
        })

    def test_post_me_not_allowed(self):
        """Test that a post request is not allowed for the me url."""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_me_not_allowed(self):
        """Test that a put request is not allowed for the me url."""
        res = self.client.put(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_profile(self):
        """Test that users can update their profile data apart from email."""
        self.user.bio = 'Prev Bio'
        self.user.phone = '1234567890'

        payload = {
            'name': 'New Name',
            'password': 'newPass123',
            'bio': 'New Bio',
            'phone': '0123456789'
        }
        res = self.client.patch(ME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()

        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.bio, payload['bio'])
        self.assertEqual(self.user.phone, payload['phone'])
        self.assertTrue(self.user.check_password(payload['password']))

    def test_update_email_fails(self):
        """Test updating an email is not allowed."""

        payload = {
            'email': 'updated@example.com'
        }

        res = self.client.patch(ME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'test@example.com')
