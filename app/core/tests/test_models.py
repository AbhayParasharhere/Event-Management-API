"""
Tests for checking models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Tests for models"""

    def test_create_user_with_valid_data_pass(self):
        """Test creating a user is successful with valid data."""
        user_data = {
            'email': 'test@example.com',
            'name': 'Test Example',
            'bio': 'Test Bio',
            'phone': '1234567890',
        }
        password = 'test123'
        user = get_user_model().objects.create_user(
            **user_data, password=password
        )

        for attr, value in user_data.items():
            self.assertEqual(getattr(user, attr), value)

        self.assertTrue(user.check_password(password))

    def test_user_email_normalized(self):
        """Test that user's email is normalized."""
        sample_emails = [
            ['test1@EXAMPLE.COM', 'test1@example.com'],
            ['test2@ExaMple.com', 'test2@example.com'],
            ['Test3@Example.com', 'Test3@example.com'],
            ['TEST4@example.COM', 'TEST4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email, password='test@123'
            )
            self.assertEqual(user.email, expected)

    def test_create_user_without_email_raises_error(self):
        """Test creating a user without email raises a value error."""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                '',
                password='test1234'
            )

    def test_default_create_user_is_not_super_user(self):
        """Test that users created using create_user
        are not super users by default."""
        user = get_user_model().objects.create_user(
            email='test1@example.com', password='test123'
        )

        self.assertFalse(user.is_superuser)

    def test_create_super_user(self):
        """Test creating super users is successful."""
        user = get_user_model().objects.create_superuser(
            email='test1@example.com', password='test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
