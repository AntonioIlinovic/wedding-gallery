"""
Models for the gallery application.
"""

from __future__ import annotations

import os
from io import BytesIO
import io

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from PIL import Image
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
        blank=True,
        help_text="Key/path of the thumbnail in object storage (S3/Minio).",
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

    @property
    def image_url(self) -> str:
        """
        Returns a presigned URL to the image file.
        """
        return get_storage_client().generate_presigned_url(self.file_key)

    @property
    def thumbnail_url(self) -> str:
        """
        Returns a presigned URL to the thumbnail file.
        Returns the original image URL if no thumbnail exists.
        """
        if self.thumbnail_key:
            return get_storage_client().generate_presigned_url(self.thumbnail_key)
        return self.image_url

    def save(self, *args, **kwargs):
        """
        Overrides the save method to generate a thumbnail on initial creation.
        """
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new and self.file_key and not self.thumbnail_key:
            self._create_and_upload_thumbnail()

    def _create_and_upload_thumbnail(self):
        """
        Creates a thumbnail from the original image and uploads it to storage.
        """
        storage = get_storage_client()
        try:
            # Download original image into an in-memory buffer
            original_image_data = io.BytesIO()
            storage.download_fileobj(self.file_key, original_image_data)
            original_image_data.seek(0)
            
            img = Image.open(original_image_data)

            # Ensure image is in RGB mode for saving as JPEG
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            
            img.thumbnail(settings.THUMBNAIL_SIZE)

            thumb_io = io.BytesIO()
            img.save(
                thumb_io,
                format="JPEG",
                quality=settings.THUMBNAIL_QUALITY,
                optimize=True,
            )
            thumb_io.seek(0)
            
            # Construct a new key for the thumbnail
            path, filename = os.path.split(self.file_key)
            name, ext = os.path.splitext(filename)
            thumb_filename = f"{name}_thumbnail.jpg"
            thumb_key = os.path.join(path, "thumbnails", thumb_filename)

            # Upload the thumbnail using the correct method
            storage.upload_fileobj(
                fileobj=thumb_io,
                key=thumb_key,
                content_type="image/jpeg"
            )

            # Save the new thumbnail key to the model without calling save() again
            Photo.objects.filter(pk=self.pk).update(thumbnail_key=thumb_key)
            self.thumbnail_key = thumb_key

        except Exception as e:
            # Handle cases where thumbnail generation might fail
            # Log the error, but don't block the main image save.
            print(f"Error creating thumbnail for {self.file_key}: {e}") # noqa

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.original_filename or self.file_key

