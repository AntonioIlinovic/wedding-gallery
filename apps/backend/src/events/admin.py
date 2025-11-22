"""
Admin registrations for the events application.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin interface for Event model."""
    
    list_display = ['name', 'code', 'date', 'is_active', 'photo_count', 'created_at']
    list_filter = ['is_active', 'date', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['access_token', 'created_at', 'updated_at', 'qr_code_info', 'access_url']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'date', 'is_active')
        }),
        ('Access Information', {
            'fields': ('access_token', 'access_url', 'qr_code_info'),
            'description': 'Share the access URL or QR code with guests'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def photo_count(self, obj):
        """Display number of photos uploaded for this event."""
        count = obj.photos.count()
        return count
    photo_count.short_description = 'Photos'
    
    def qr_code_info(self, obj):
        """Display information about generating QR code."""
        if obj.pk:
            return format_html(
                '<p>To generate a QR code for this event, run:</p>'
                '<code>python manage.py generate_qr {}</code>',
                obj.code
            )
        return "Save the event first to generate QR code"
    qr_code_info.short_description = 'QR Code Generation'
    
    def access_url(self, obj):
        """Display the access URL that should be embedded in QR code."""
        if obj.pk:
            # This will be the frontend URL with token
            url = f"http://localhost:3000/?token={obj.access_token}"
            return format_html(
                '<a href="{}" target="_blank">{}</a><br>'
                '<small>Copy this URL for the QR code</small>',
                url, url
            )
        return "Save the event first"
    access_url.short_description = 'Access URL'

