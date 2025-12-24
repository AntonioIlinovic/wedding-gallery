"""
Models for the gallery application.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone
from src.events.models import Event
from src.uploads.storage import get_storage_client

class Photo(models.Model):
    """
    A single uploaded photo belonging to an event.
    """

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="photos",
    )
    file_key = models.CharField(
        max_length=512,
        help_text="Key/path of the file in object storage (S3/Minio).",
    )
    thumbnail_key = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        help_text="Key/path of the thumbnail image in object storage.",
    )
    display_key = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        help_text="Key/path of the display-sized image in object storage.",
    )
    original_filename = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now, editable=False)
    
    class ModerationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    moderation_status = models.CharField(
        max_length=10,
        choices=ModerationStatus.choices,
        default=ModerationStatus.APPROVED,
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    content_type = models.CharField(max_length=255, blank=True)

    def get_image_url(self, size: str = "original") -> str:
        """
        Returns a presigned URL to the image file of the specified size.
        Valid sizes are "original", "thumbnail", and "display".
        """
        key_to_use = self.file_key
        if size == "thumbnail" and self.thumbnail_key:
            key_to_use = self.thumbnail_key
        elif size == "display" and self.display_key:
            key_to_use = self.display_key
        
        return get_storage_client().generate_presigned_url(key_to_use)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.original_filename or self.file_key

