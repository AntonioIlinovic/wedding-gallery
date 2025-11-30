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
    original_filename = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now, editable=False)

    @property
    def image_url(self) -> str:
        """
        Returns a presigned URL to the image file.
        """
        return get_storage_client().generate_presigned_url(self.file_key)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.original_filename or self.file_key

