"""
Admin registrations for the gallery application.
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import Photo


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    """Admin interface for Photo model."""

    list_display = [
        "image_thumbnail",
        "original_filename",
        "event",
        "uploaded_at",
    ]
    list_filter = ["event", "uploaded_at"]
    search_fields = ["original_filename", "event__name"]
    readonly_fields = ("file_key", "uploaded_at")

    def image_thumbnail(self, obj):
        if obj.file_key:
            return format_html(
                '<img src="{}" style="width: 200px; height: 200px; object-fit: cover; border-radius: 4px;" />',
                obj.image_url,
            )
        return "No Image"

    image_thumbnail.short_description = "Thumbnail"
