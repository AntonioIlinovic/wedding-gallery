"""
Views for the gallery application.
"""
import uuid
import os
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import InMemoryUploadedFile
from src.events.models import Event
from src.events.decorators import require_event_token
from .models import Photo
from .serializers import PhotoSerializer, PhotoUploadSerializer
from src.uploads.storage import get_storage_client


class PhotoPagination(PageNumberPagination):
    """Pagination for photo listings."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@csrf_exempt
@api_view(['POST'])
@require_event_token(token_location='data')
def upload_photo(request, event):
    """
    Upload a photo for an event.
    Requires access_token and photo file.
    Event is validated and passed by the decorator.
    """
    # Get photo file from FILES
    photo_file = request.FILES.get('photo')
    if not photo_file:
        return Response({
            'error': 'photo file is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file type
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    file_ext = os.path.splitext(photo_file.name)[1].lower()
    if file_ext not in valid_extensions:
        return Response({
            'error': f'Invalid file type. Allowed types: {", ".join(valid_extensions)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate unique file key
    file_extension = os.path.splitext(photo_file.name)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_key = f"{event.code}/originals/{unique_filename}"
    
    # Upload to storage
    try:
        storage = get_storage_client()
        
        # Read file content
        # Reset file pointer to beginning in case it was already read
        if hasattr(photo_file, 'seek'):
            photo_file.seek(0)
        file_content = photo_file.read()
        
        # Upload to S3/Minio
        storage.upload_file(
            file_key=file_key,
            file_content=file_content,
            content_type=photo_file.content_type
        )
        
        # Create Photo record
        photo = Photo.objects.create(
            event=event,
            file_key=file_key,
            original_filename=photo_file.name,
            file_size=photo_file.size,
            content_type=photo_file.content_type
        )
        
        # Return photo details
        photo_serializer = PhotoSerializer(photo)
        return Response(photo_serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Failed to upload photo: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@require_event_token(token_location='query')
def list_photos(request, event):
    """
    List all photos for an event.
    Requires access_token as query parameter.
    Event is validated and passed by the decorator.
    """
    # Get photos for this event
    photos = Photo.objects.filter(event=event, moderation_status=Photo.ModerationStatus.APPROVED).order_by('-uploaded_at')
    
    # Paginate results
    paginator = PhotoPagination()
    paginated_photos = paginator.paginate_queryset(photos, request)
    
    serializer = PhotoSerializer(paginated_photos, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def get_upload_limit(request):
    """
    Return the maximum number of photos that can be uploaded at once.
    """
    from django.conf import settings
    return Response({
        'max_upload_limit': settings.MAX_PHOTOS_UPLOAD_LIMIT
    }, status=status.HTTP_200_OK)

