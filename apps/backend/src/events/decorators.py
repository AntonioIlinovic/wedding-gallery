"""
Decorators for event-based authentication.
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .models import Event


def require_event_token(token_location='data'):
    """
    Decorator to validate event access token.
    
    Args:
        token_location: Where to find the token - 'data' for POST body, 'query' for GET params
    
    The validated event will be passed as 'event' kwarg to the view function.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get access token from appropriate location
            if token_location == 'query':
                access_token = request.query_params.get('access_token')
            else:  # 'data'
                access_token = request.data.get('access_token')
            
            if not access_token:
                return Response({
                    'error': 'access_token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate event
            try:
                event = Event.objects.get(access_token=access_token, is_active=True)
            except Event.DoesNotExist:
                return Response({
                    'error': 'Invalid or inactive access token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Pass event to the view
            kwargs['event'] = event
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator

