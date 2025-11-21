import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
def test_health_check(client):
    """
    GIVEN a Django client
    WHEN the health check URL is requested
    THEN the response should be 200 OK and contain the expected content.
    """
    url = reverse('health')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status': 'ok', 'service': 'backend'}
