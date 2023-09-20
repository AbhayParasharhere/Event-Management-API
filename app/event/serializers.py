"""
Serialziers for the event api.
"""

from rest_framework import serializers
from core.models import Event


class EventSerializer(serializers.ModelSerializer):
    """Serializer for the event model."""
    class Meta:
        model = Event
        fields = ['id', 'title', 'organizer',
                  'venue', 'ticket_price', 'date', 'time']
        read_only_fields = ['id']


class EventDetailSerializer(EventSerializer):
    """Detail serializer for the event model.
       Includes additional fields like description,
       EVent image."""
    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['description']
