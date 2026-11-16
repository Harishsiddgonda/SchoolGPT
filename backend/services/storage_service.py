"""
Cloud S3-Compatible Object Storage Service for SchoolGPT
Supports AWS S3, Cloudflare R2, MinIO, and local filesystem fallback.
RSR Technologies
"""

import os
from pathlib import Path
from typing import Tuple, Optional
import boto3
from botocore.exceptions import ClientError
from backend.config import settings

class StorageService:
    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "")
        self.endpoint_url = os.getenv("S3_ENDPOINT_URL", None)
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID", "")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.local_upload_dir = Path("./data/documents")
        self.local_upload_dir.mkdir(parents=True, exist_ok=True)
        self._s3_client = None
        self._init_client()

    def _init_client(self):
        if self.bucket_name and self.access_key and self.secret_key:
            try:
                self._s3_client = boto3.client(
                    "s3",
                    endpoint_url=self.endpoint_url,
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region,
                )
            except Exception as e:
                print(f"Notice: S3 Client init failed: {e}")
                self._s3_client = None

    def is_cloud_storage(self) -> bool:
        return self._s3_client is not None and bool(self.bucket_name)

    def upload_file(self, file_bytes: bytes, filename: str, content_type: str = "application/pdf") -> Tuple[str, str]:
        """
        Uploads file to S3 bucket or persists to local disk.
        Returns (storage_path_or_url, storage_type: 's3' | 'local').
        """
        # Save local copy for parsing
        local_path = self.local_upload_dir / filename
        with open(local_path, "wb") as f:
            f.write(file_bytes)

        if self.is_cloud_storage():
            s3_key = f"documents/{filename}"
            try:
                self._s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=file_bytes,
                    ContentType=content_type,
                )
                storage_url = f"s3://{self.bucket_name}/{s3_key}"
                return storage_url, "s3"
            except Exception as e:
                print(f"Notice: S3 upload failed, falling back to local: {e}")

        return str(local_path), "local"

    def delete_file(self, file_path_or_url: str) -> bool:
        """Deletes file from S3 or local storage."""
        if file_path_or_url.startswith("s3://") and self.is_cloud_storage():
            try:
                key = file_path_or_url.replace(f"s3://{self.bucket_name}/", "")
                self._s3_client.delete_object(Bucket=self.bucket_name, Key=key)
                return True
            except Exception:
                pass
        elif os.path.exists(file_path_or_url):
            try:
                os.remove(file_path_or_url)
                return True
            except Exception:
                pass
        return False

storage_service = StorageService()
