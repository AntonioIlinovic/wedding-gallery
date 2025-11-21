"""
Models for the events application.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone
from secrets import token_urlsafe


class Event(models.Model):
    """
    A single wedding event.

    For this project we only need one active event, but the model is flexible
    enough to support multiple events in the future.
    """

    code = models.SlugField(
        max_length=50,
        unique=True,
        help_text="Short identifier for this event (used in storage paths).",
    )
    name = models.CharField(max_length=255, help_text="Display name of the event.")
    access_token = models.CharField(
        max_length=128,
        unique=True,
        editable=False,
        help_text="Secret token embedded in the QR code for guest access.",
    )
    description = models.TextField(
        blank=True,
        help_text="Welcome text shown on the landing page for this event.",
    )
    date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name or self.code

    def regenerate_access_token(self) -> None:
        """
        Generate a new random access token.

        This is used when initially creating the event and can also be called
        from the admin if the QR code URL ever needs to be rotated.
        """
        self.access_token = token_urlsafe(32)

    def save(self, *args, **kwargs):
        # Automatically generate an access token the first time the event is saved.
        if not self.access_token:
            self.regenerate_access_token()
        super().save(*args, **kwargs)

