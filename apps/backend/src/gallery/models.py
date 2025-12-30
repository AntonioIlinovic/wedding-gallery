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
    fullscreen_key = models.CharField(
        max_length=512,
        blank=True,
        help_text="Key/path of the fullscreen image in object storage (S3/Minio).",
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
    def original_image_url(self) -> str:
        """
        Returns a presigned URL to the original image file.
        """
        return get_storage_client().generate_presigned_url(self.file_key)

    @property
    def fullscreen_url(self) -> str:
        """
        Returns a presigned URL to the fullscreen image file.
        Returns the original image URL if no fullscreen image exists.
        """
        if self.fullscreen_key:
            return get_storage_client().generate_presigned_url(self.fullscreen_key)
        return self.original_image_url

    @property
    def thumbnail_url(self) -> str:
        """
        Returns a presigned URL to the thumbnail file.
        Returns the fullscreen image URL if no thumbnail exists.
        """
        if self.thumbnail_key:
            return get_storage_client().generate_presigned_url(self.thumbnail_key)
        return self.fullscreen_url

    def save(self, *args, **kwargs):
        """
        Overrides the save method to generate a thumbnail and a fullscreen image
        on initial creation.
        """
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new and self.file_key:
            if not self.thumbnail_key:
                self._create_and_upload_thumbnail()
            if not self.fullscreen_key:
                self._create_and_upload_fullscreen()

    def _create_and_upload_fullscreen(self):
        """
        Creates a fullscreen-optimized image and uploads it to storage.
        """
        storage = get_storage_client()
        try:
            original_image_data = io.BytesIO()
            storage.download_fileobj(self.file_key, original_image_data)
            original_image_data.seek(0)
            
            img = Image.open(original_image_data)

            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            
            img.thumbnail(settings.FULLSCREEN_SIZE)

            fullscreen_io = io.BytesIO()
            img.save(
                fullscreen_io,
                format="JPEG",
                quality=settings.FULLSCREEN_QUALITY,
                optimize=True,
            )
            fullscreen_io.seek(0)
            
            event_code = self.file_key.split('/')[0]
            filename = os.path.basename(self.file_key)
            name, ext = os.path.splitext(filename)
            fullscreen_filename = f"{name}_fullscreen.jpg"
            fullscreen_key = os.path.join(event_code, "fullscreen", fullscreen_filename)

            storage.upload_fileobj(
                fileobj=fullscreen_io,
                key=fullscreen_key,
                content_type="image/jpeg"
            )

            Photo.objects.filter(pk=self.pk).update(fullscreen_key=fullscreen_key)
            self.fullscreen_key = fullscreen_key

        except Exception as e:
            print(f"Error creating fullscreen image for {self.file_key}: {e}")

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
            event_code = self.file_key.split('/')[0]
            filename = os.path.basename(self.file_key)
            name, ext = os.path.splitext(filename)
            thumb_filename = f"{name}_thumbnail.jpg"
            thumb_key = os.path.join(event_code, "thumbnails", thumb_filename)

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

