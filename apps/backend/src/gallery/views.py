"""
Views for the gallery application.
"""
import uuid
import os
from io import BytesIO
from PIL import Image

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

def process_image(file_content: bytes, max_dimension: int, quality: int = 80):
    """
    Processes an image: resizes it to fit within max_dimension (maintaining aspect ratio),
    and converts it to WebP format. Returns the processed image bytes and its content type.
    """
    img = Image.open(BytesIO(file_content))
    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
    
    output_buffer = BytesIO()
    img.save(output_buffer, format="WEBP", quality=quality)
    output_buffer.seek(0)
    
    return output_buffer.getvalue(), "image/webp"

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
    # Define target sizes for processed images
    THUMBNAIL_MAX_DIMENSION = 400
    DISPLAY_MAX_DIMENSION = 1920
    IMAGE_QUALITY = 80 # Quality for WEBP conversion
    
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
    
    # Generate unique file key for original
    original_file_extension = os.path.splitext(photo_file.name)[1]
    unique_filename_base = str(uuid.uuid4())
    original_file_key = f"{event.code}/{unique_filename_base}{original_file_extension}"
    
    # Read file content
    if hasattr(photo_file, 'seek'):
        photo_file.seek(0)
    original_file_content = photo_file.read()
    
    # Process images
    thumbnail_content, thumbnail_content_type = process_image(original_file_content, THUMBNAIL_MAX_DIMENSION, IMAGE_QUALITY)
    display_content, display_content_type = process_image(original_file_content, DISPLAY_MAX_DIMENSION, IMAGE_QUALITY)

    # Generate keys for processed images
    thumbnail_file_key = f"{event.code}/{unique_filename_base}_thumbnail.webp"
    display_file_key = f"{event.code}/{unique_filename_base}_display.webp"
    
    # Upload to storage
    try:
        storage = get_storage_client()
        
        # Upload original
        storage.upload_file(
            file_key=original_file_key,
            file_content=original_file_content,
            content_type=photo_file.content_type
        )
        
        # Upload thumbnail
        storage.upload_file(
            file_key=thumbnail_file_key,
            file_content=thumbnail_content,
            content_type=thumbnail_content_type
        )

        # Upload display version
        storage.upload_file(
            file_key=display_file_key,
            file_content=display_content,
            content_type=display_content_type
        )
        
        # Create Photo record
        photo = Photo.objects.create(
            event=event,
            file_key=original_file_key,
            thumbnail_key=thumbnail_file_key,
            display_key=display_file_key,
            original_filename=photo_file.name,
            file_size=photo_file.size, # Note: This is the original file size. We could store processed sizes too if needed.
            content_type=photo_file.content_type # Note: This is the original content type.
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

