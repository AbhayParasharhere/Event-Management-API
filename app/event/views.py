"""
Views for the event api.
"""

from core.models import Event

from rest_framework import viewsets, mixins
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

    def perform_create(self, serializer):
        """Save the authenticated user as the organizer
        before saving in the serializer data."""
        serializer.save(organizer=self.request.user)

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


class GetAllEvents(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Views for getting all events."""
    http_method_names = ['get']
    queryset = Event.objects.all().order_by('-id')
    serializer_class = EventSerializer
