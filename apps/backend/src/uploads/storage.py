"""
Storage utilities for uploading files to S3 / Minio.

This module provides a small abstraction layer around boto3 so the rest of the
codebase does not need to know whether we are talking to AWS S3 or a local
Minio instance.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import BinaryIO

import boto3
from botocore.client import BaseClient
from django.conf import settings


def _build_s3_client() -> BaseClient:
    """
    Build a boto3 S3 client pointing either at AWS or at Minio.
    """
    use_minio = getattr(settings, "USE_MINIO", False)
    region_name = getattr(settings, "AWS_S3_REGION_NAME", "eu-central-1")

    access_key = os.environ.get("AWS_ACCESS_KEY_ID", os.environ.get("MINIO_ROOT_USER"))
    secret_key = os.environ.get(
        "AWS_SECRET_ACCESS_KEY",
        os.environ.get("MINIO_ROOT_PASSWORD"),
    )

    client_kwargs = {
        "aws_access_key_id": access_key,
        "aws_secret_access_key": secret_key,
        "region_name": region_name,
    }

    if use_minio:
        endpoint = getattr(settings, "MINIO_ENDPOINT", "http://minio:9000")
        client_kwargs["endpoint_url"] = endpoint

    return boto3.client("s3", **client_kwargs)


@dataclass
class StorageClient:
    """
    Thin wrapper around an S3-compatible bucket.
    """

    bucket_name: str
    client: BaseClient

    def download_fileobj(self, key: str, fileobj: BinaryIO) -> None:
        """
        Download a file from storage into a file-like object.
        """
        self.client.download_fileobj(self.bucket_name, key, fileobj)

    def upload_fileobj(
        self,
        fileobj: BinaryIO,
        key: str,
        content_type: str | None = None,
    ) -> None:
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        self.client.upload_fileobj(
            Fileobj=fileobj,
            Bucket=self.bucket_name,
            Key=key,
            ExtraArgs=extra_args or None,
        )

    def upload_file(
        self,
        file_key: str,
        file_content: bytes,
        content_type: str | None = None,
    ) -> None:
        """
        Upload file content (bytes) to storage.
        """
        import io
        file_obj = io.BytesIO(file_content)
        self.upload_fileobj(file_obj, file_key, content_type)

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Generate a time-limited URL for reading an object.
        For MinIO, we create URLs with the public endpoint (localhost:9000)
        so browsers can access them. Signature is calculated for this endpoint.
        For AWS S3, if a custom domain is provided, we use it as the endpoint
        for the presigned URL. This is useful when behind a CDN.
        """
        use_minio = getattr(settings, "USE_MINIO", False)
        
        client_kwargs = {
            "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID", os.environ.get("MINIO_ROOT_USER")),
            "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY", os.environ.get("MINIO_ROOT_PASSWORD")),
            "region_name": getattr(settings, "AWS_S3_REGION_NAME", "eu-central-1"),
        }

        # By default, use the client that was initialized with the class
        presigned_url_client = self.client
        
        # If a public endpoint is specified (for MinIO or a custom S3 domain),
        # create a new client configured for that public endpoint.
        public_endpoint = None
        if use_minio:
            public_endpoint = getattr(settings, "MINIO_PUBLIC_ENDPOINT", "http://localhost:9000")
        else:
            # For production, we might have a custom domain (e.g., CloudFront)
            public_endpoint = getattr(settings, "AWS_S3_CUSTOM_DOMAIN", None)

        if public_endpoint:
            client_kwargs["endpoint_url"] = public_endpoint
            presigned_url_client = boto3.client("s3", **client_kwargs)

        return presigned_url_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=expires_in,
        )


_storage_client: StorageClient | None = None


def get_storage_client() -> StorageClient:
    """
    Return a singleton StorageClient instance.
    """
    global _storage_client
    if _storage_client is None:
        bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME")
        _storage_client = StorageClient(bucket_name=bucket, client=_build_s3_client())
    return _storage_client


