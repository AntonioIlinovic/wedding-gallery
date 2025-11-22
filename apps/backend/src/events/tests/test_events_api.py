import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from src.events.models import Event

@pytest.mark.django_db
class TestEventAPI:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def event(self):
        return Event.objects.create(
            name="Test Wedding",
            code="test-wedding",
            description="Welcome!",
            date="2024-01-01"
        )

    def test_validate_token_success(self, client, event):
        """Test validating a valid access token."""
        url = reverse('events:validate')
        data = {'access_token': event.access_token}
        
        response = client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['valid'] is True
        assert response.data['event']['name'] == event.name
        assert response.data['event']['code'] == event.code

    def test_validate_token_invalid(self, client):
        """Test validating an invalid access token."""
        url = reverse('events:validate')
        data = {'access_token': 'invalid-token'}
        
        response = client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['valid'] is False

    def test_event_details_success(self, client, event):
        """Test retrieving event details."""
        url = reverse('events:details', args=[event.access_token])
        
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == event.name

    def test_event_details_not_found(self, client):
        """Test retrieving event details with invalid token."""
        url = reverse('events:details', args=['invalid-token'])
        
        response = client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

