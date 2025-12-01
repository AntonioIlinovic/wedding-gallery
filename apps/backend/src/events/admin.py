"""
Admin registrations for the events application.
"""
from io import BytesIO

import qrcode
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.conf import settings

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin interface for Event model."""

    list_display = ("name", "qr_code_thumbnail", "code", "date", "is_active", "photo_count")
    list_filter = ("is_active", "date", "created_at")
    search_fields = ("name", "code", "description")
    readonly_fields = ("access_token", "created_at", "updated_at", "access_url")

    fieldsets = (
        ("Basic Information", {"fields": ("name", "code", "description", "date", "is_active")}),
        ("Access Information", {"fields": ("access_token", "access_url")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/qr-code/",
                self.admin_site.admin_view(self.serve_qr_code),
                name="events_event_qr_code",
            )
        ]
        return custom_urls + urls

    def serve_qr_code(self, request, object_id):
        event = self.get_object(request, object_id)
        if event is None:
            return HttpResponse(status=404)

        frontend_url = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:3000")
        qr_url = f"{frontend_url}/?token={event.access_token}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, "PNG")
        buffer.seek(0)

        return HttpResponse(buffer, content_type="image/png")

    def qr_code_thumbnail(self, obj):
        """Display QR code in list view."""
        url = reverse("admin:events_event_qr_code", args=[obj.pk])
        return format_html('<img src="{}" style="width: 300px; height: 300px;" />', url)
    qr_code_thumbnail.short_description = "QR Code"

    def photo_count(self, obj):
        """Display number of photos uploaded for this event."""
        return obj.photos.count()

    photo_count.short_description = "Photos"

    def access_url(self, obj):
        """Display the access URL that should be embedded in QR code."""
        if obj.pk:
            frontend_url = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:3000")
            url = f"{frontend_url}/?token={obj.access_token}"
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                url, url
            )
        return "Save the event first"
    access_url.short_description = "Access URL"
