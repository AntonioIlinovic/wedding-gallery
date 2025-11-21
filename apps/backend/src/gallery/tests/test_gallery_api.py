import pytest
import io
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from src.events.models import Event
from src.gallery.models import Photo

@pytest.mark.django_db
class TestGalleryAPI:
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

    def test_upload_photo_success(self, client, event, monkeypatch):
        """Test uploading a photo successfully."""
        # Mock S3 storage
        def mock_upload_file(*args, **kwargs):
            return None
        
        # Using a simple mock for storage client
        class MockStorage:
            def upload_file(self, *args, **kwargs): return None
            def generate_presigned_url(self, *args, **kwargs): return "http://mock-url"
            
        monkeypatch.setattr("src.uploads.storage.get_storage_client", lambda: MockStorage())

        url = reverse('gallery:upload')
        
        # Create a dummy image file
        image_content = b"fake-image-content"
        image = SimpleUploadedFile(
            "test_image.jpg", 
            image_content, 
            content_type="image/jpeg"
        )
        
        data = {
            'access_token': event.access_token,
            'photo': image
        }
        
        response = client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Photo.objects.count() == 1
        photo = Photo.objects.first()
        assert photo.event == event
        assert photo.original_filename == "test_image.jpg"

    def test_list_photos(self, client, event, monkeypatch):
        """Test listing photos for an event."""
        # Mock storage for presigned URLs
        class MockStorage:
            def generate_presigned_url(self, *args, **kwargs): return "http://mock-url"
            
        monkeypatch.setattr("src.uploads.storage.get_storage_client", lambda: MockStorage())
        
        # Create some photos
        Photo.objects.create(
            event=event,
            file_key=f"{event.code}/photo1.jpg",
            original_filename="photo1.jpg"
        )
        Photo.objects.create(
            event=event,
            file_key=f"{event.code}/photo2.jpg",
            original_filename="photo2.jpg"
        )
        
        url = reverse('gallery:list')
        response = client.get(url, {'access_token': event.access_token})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        assert response.data['results'][0]['original_filename'] in ['photo1.jpg', 'photo2.jpg']

