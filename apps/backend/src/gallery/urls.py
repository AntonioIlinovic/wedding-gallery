"""URL patterns for the gallery application."""
from django.urls import path
from . import views

app_name = "gallery"

urlpatterns = [
    path('upload/', views.upload_photo, name='upload'),
    path('photos/', views.list_photos, name='list'),
    path('upload-limit/', views.get_upload_limit, name='upload-limit'),
]

