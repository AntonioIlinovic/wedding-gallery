"""
Views for the events application.
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Event
from .serializers import EventValidationSerializer, EventDetailSerializer


@api_view(['POST'])
def validate_token(request):
    """
    Validate an event access token.
    Returns event details if token is valid.
    """
    serializer = EventValidationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    access_token = serializer.validated_data['access_token']
    
    try:
        event = Event.objects.get(access_token=access_token, is_active=True)
        event_serializer = EventDetailSerializer(event)
        return Response({
            'valid': True,
            'event': event_serializer.data
        })
    except Event.DoesNotExist:
        return Response({
            'valid': False,
            'error': 'Invalid or inactive access token'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def event_details(request, access_token):
    """
    Get event details by access token.
    """
    try:
        event = Event.objects.get(access_token=access_token, is_active=True)
        serializer = EventDetailSerializer(event)
        return Response(serializer.data)
    except Event.DoesNotExist:
        return Response({
            'error': 'Invalid or inactive access token'
        }, status=status.HTTP_404_NOT_FOUND)

