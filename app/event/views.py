"""
Views for the event api.
"""

from core.models import Event

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from event.serializers import (
    EventSerializer,
    EventDetailSerializer
)


class OrganizedEventViewSet(viewsets.ModelViewSet):
    """Viewset for the organised events by the user."""
    queryset = Event.objects.all()
    serializer_class = EventDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Overrides queryset to be used for the specified methods."""
        if self.action == 'list':
            return EventSerializer
        return self.serializer_class

    def get_queryset(self):
        """Overrides the queryset based on the specifications provided."""
        return self.queryset.filter(
            organizer=self.request.user
        ).order_by('-id')
