"""
Serializers for the events application.
"""
from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model."""
    
    class Meta:
        model = Event
        fields = ['id', 'code', 'name', 'description', 'date', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class EventValidationSerializer(serializers.Serializer):
    """Serializer for validating event access token."""
    access_token = serializers.CharField(required=True, max_length=64)


class EventDetailSerializer(serializers.ModelSerializer):
    """Serializer for event details (without sensitive information)."""
    
    class Meta:
        model = Event
        fields = ['id', 'code', 'name', 'description', 'date']

