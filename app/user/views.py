"""
Views for the user api.
"""

from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """View for creating new users."""
    serializer_class = UserSerializer


class CreateUserToken(ObtainAuthToken):
    """View for creating new user token."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserViews(generics.RetrieveUpdateAPIView):
    """View for updating the user profile and retrieving the user profile."""
    http_method_names = ['get', 'patch']  # to just support get and patch

    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """ Get and return the current authenticated user."""
        return self.request.user
