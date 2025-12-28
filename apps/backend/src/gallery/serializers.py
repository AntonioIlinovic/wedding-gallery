"""
Serializers for the gallery application.
"""
from rest_framework import serializers
from .models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    """Serializer for the Photo model, including image and thumbnail URLs."""

    class Meta:
        model = Photo
        fields = [
            'id',
            'original_filename',
            'uploaded_at',
            'file_size',
            'content_type',
            'image_url',
            'thumbnail_url',
        ]
        read_only_fields = fields


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

