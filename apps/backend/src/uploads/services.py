from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from src.events.models import Event


@dataclass
class PresignedUpload:
    upload_url: str
    expires_at: datetime
    token: str


def create_presigned_upload(event: Event, ttl_minutes: int = 30) -> PresignedUpload:
    """Placeholder for generating presigned upload URLs."""
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
    token = token_urlsafe(32)
    upload_url = f"https://storage.example.com/uploads/{event.code}/{token}"
    return PresignedUpload(upload_url=upload_url, expires_at=expires_at, token=token)

