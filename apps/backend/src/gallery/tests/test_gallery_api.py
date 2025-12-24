import pytest
import io
from PIL import Image # Import Image
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
        class MockStorage:
            def upload_file(self, file_key, file_content, content_type=None):
                # Mock implementation that does nothing
                pass
            def generate_presigned_url(self, key, expires_in=3600):
                return "http://mock-url/" + key # Return a more realistic mock URL
        
        # Mock where it's used:
        # - views imports get_storage_client directly
        # - serializers import it from the storage module at call time
        mock_storage_instance = MockStorage()
        monkeypatch.setattr("src.gallery.views.get_storage_client", lambda: mock_storage_instance)
        monkeypatch.setattr("src.uploads.storage.get_storage_client", lambda: mock_storage_instance)
        monkeypatch.setattr("src.gallery.models.get_storage_client", lambda: mock_storage_instance) # Add this line

        url = reverse('gallery:upload')
        
        # Create a real dummy image file in memory
        image_buffer = io.BytesIO()
        Image.new('RGB', (1000, 750), color = 'red').save(image_buffer, format='JPEG')
        image_buffer.seek(0)
        
        image = SimpleUploadedFile(
            "test_image.jpg", 
            image_buffer.read(), 
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
        assert photo.moderation_status == Photo.ModerationStatus.APPROVED
        assert photo.file_key.startswith(f"{event.code}/") # Check original key
        assert photo.thumbnail_key.startswith(f"{event.code}/") # Check thumbnail key
        assert photo.display_key.startswith(f"{event.code}/") # Check display key
        assert photo.thumbnail_key.endswith(".webp") # Check format
        assert photo.display_key.endswith(".webp") # Check format
        assert photo.get_image_url(size="original") == f"http://mock-url/{photo.file_key}"
        assert photo.get_image_url(size="thumbnail") == f"http://mock-url/{photo.thumbnail_key}"
        assert photo.get_image_url(size="display") == f"http://mock-url/{photo.display_key}"

    def test_list_photos(self, client, event, monkeypatch):
        """Test listing photos for an event."""
        # Mock storage for presigned URLs
        class MockStorage:
            def generate_presigned_url(self, key, expires_in=3600):
                return "http://mock-url"
        
        # Mock at the source where it's defined
        mock_storage_instance = MockStorage()
        monkeypatch.setattr("src.uploads.storage.get_storage_client", lambda: mock_storage_instance)
        
        # Create some photos
        Photo.objects.create(
            event=event,
            file_key=f"{event.code}/photo1.jpg",
            original_filename="photo1.jpg",
            moderation_status=Photo.ModerationStatus.APPROVED
        )
        Photo.objects.create(
            event=event,
            file_key=f"{event.code}/photo2.jpg",
            original_filename="photo2.jpg",
            moderation_status=Photo.ModerationStatus.APPROVED
        )
        
        url = reverse('gallery:list')
        response = client.get(url, {'access_token': event.access_token})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        assert response.data['results'][0]['original_filename'] in ['photo1.jpg', 'photo2.jpg']

