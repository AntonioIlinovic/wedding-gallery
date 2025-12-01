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
        "thumbnail_preview",
        "moderation_status",
        "original_filename",
        "event",
        "content_type",
        "file_size_display",
        "uploaded_at",
    ]
    list_filter = ("event", "uploaded_at", "content_type", "moderation_status")
    search_fields = ("original_filename", "event__name")
    readonly_fields = ("file_key", "uploaded_at", "file_size", "content_type", "moderated_at")
    actions = ["approve_photos", "reject_photos"]

    def approve_photos(self, request, queryset):
        queryset.update(moderation_status=Photo.ModerationStatus.APPROVED)
    approve_photos.short_description = "Approve selected photos"

    def reject_photos(self, request, queryset):
        queryset.update(moderation_status=Photo.ModerationStatus.REJECTED)
    reject_photos.short_description = "Reject selected photos"

    def thumbnail_preview(self, obj):
        if obj.file_key:
            return format_html(
                '<img src="{}" style="width: 300px; height: 300px; object-fit: contain; border-radius: 4px;" />',
                obj.image_url,
            )
        return "No Image"
    thumbnail_preview.short_description = "Preview"

    def file_size_display(self, obj):
        """Display file size in human-readable format."""
        if obj.file_size is None:
            return "-"
        size = obj.file_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    file_size_display.short_description = "Size"
