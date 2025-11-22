"""
Models for the gallery application.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone

from src.events.models import Event


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
    file_size = models.BigIntegerField(null=True, blank=True)
    content_type = models.CharField(max_length=255, blank=True)
    thumbnail_key = models.CharField(
        max_length=512,
        blank=True,
        help_text="Optional key/path for a thumbnail version of the image.",
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.original_filename or self.file_key

