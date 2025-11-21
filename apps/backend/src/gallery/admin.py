"""
Admin registrations for the gallery application.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Photo


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    """Admin interface for Photo model."""
    
    list_display = ['thumbnail_preview', 'original_filename', 'event', 'uploaded_at', 'file_size_display']
    list_filter = ['event', 'uploaded_at', 'content_type']
    search_fields = ['original_filename', 'event__name', 'event__code']
    readonly_fields = ['file_key', 'uploaded_at', 'file_size', 'content_type', 'preview']
    
    fieldsets = (
        ('Photo Information', {
            'fields': ('event', 'original_filename', 'preview')
        }),
        ('Storage Details', {
            'fields': ('file_key', 'thumbnail_key', 'file_size', 'content_type'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
    
    def thumbnail_preview(self, obj):
        """Display thumbnail in list view."""
        try:
            from src.uploads.storage import get_storage_client
            storage = get_storage_client()
            url = storage.generate_presigned_url(obj.file_key, expiration=3600)
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                url
            )
        except Exception:
            return '-'
    thumbnail_preview.short_description = 'Preview'
    
    def preview(self, obj):
        """Display full preview in detail view."""
        if obj.pk:
            try:
                from src.uploads.storage import get_storage_client
                storage = get_storage_client()
                url = storage.generate_presigned_url(obj.file_key, expiration=3600)
                return mark_safe(
                    f'<img src="{url}" style="max-width: 500px; max-height: 500px; border-radius: 8px;" />'
                )
            except Exception as e:
                return f"Error loading preview: {str(e)}"
        return "Save the photo first"
    preview.short_description = 'Preview'
    
    def file_size_display(self, obj):
        """Display file size in human-readable format."""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    file_size_display.short_description = 'Size'
    
    actions = ['delete_selected']
    
    def delete_queryset(self, request, queryset):
        """Custom bulk delete to also delete from storage."""
        from src.uploads.storage import get_storage_client
        storage = get_storage_client()
        
        for photo in queryset:
            try:
                storage.delete_file(photo.file_key)
                if photo.thumbnail_key:
                    storage.delete_file(photo.thumbnail_key)
            except Exception:
                pass  # Continue even if storage deletion fails
        
        queryset.delete()

