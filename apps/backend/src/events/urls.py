"""URL patterns for the events application."""
from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path('validate/', views.validate_token, name='validate'),
    path('<str:access_token>/', views.event_details, name='details'),
]

