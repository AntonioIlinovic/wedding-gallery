"""
Serializers for the gallery application.
"""
from rest_framework import serializers
from .models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    """Serializer for Photo model with presigned URL."""
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Photo
        fields = ['id', 'original_filename', 'uploaded_at', 'file_size', 
                  'content_type', 'url']
        read_only_fields = ['id', 'uploaded_at']
    
    def get_url(self, obj):
        """Generate presigned URL for photo viewing."""
        from src.uploads.storage import get_storage_client
        storage = get_storage_client()
        # Presigned URL valid for 1 hour
        return storage.generate_presigned_url(obj.file_key, expires_in=3600)



class PhotoUploadSerializer(serializers.Serializer):
    """Serializer for photo upload."""
    access_token = serializers.CharField(required=True, max_length=64)
    photo = serializers.FileField(required=True)
    
    def validate_photo(self, value):
        """Validate that the uploaded file is an image."""
        # Check file extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        ext = value.name.lower().split('.')[-1]
        if f'.{ext}' not in valid_extensions:
            raise serializers.ValidationError(
                f'File type not supported. Allowed types: {", ".join(valid_extensions)}'
            )
        return value

