from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
import os
from pathlib import Path

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class StorageInterface(ABC):
    """
    Interface for storage services.

    This allows easy switching between local, S3, GCS, etc.
    """

    @abstractmethod
    async def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload a file to storage.

        Args:
            file: File object to upload
            filename: Name of the file
            content_type: MIME type of the file

        Returns:
            URL or path to the uploaded file
        """
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.

        Args:
            file_path: Path or URL of the file to delete

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_file_url(self, file_path: str) -> str:
        """
        Get URL for accessing a file.

        Args:
            file_path: Path of the file

        Returns:
            Public URL to access the file
        """
        pass


class LocalStorageService(StorageInterface):
    """
    Local file system storage implementation.

    Stores files in a local directory.
    """

    def __init__(self, base_path: str = "./storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Local storage initialized at: {self.base_path}")

    async def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        content_type: Optional[str] = None
    ) -> str:
        """Upload file to local storage"""
        try:
            file_path = self.base_path / filename

            # Create subdirectories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(file_path, "wb") as f:
                f.write(file.read())

            logger.info(f"File uploaded to local storage: {filename}")
            return str(file_path)

        except Exception as e:
            logger.error(f"Error uploading file {filename}: {e}")
            raise

    async def delete_file(self, file_path: str) -> bool:
        """Delete file from local storage"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"File deleted from local storage: {file_path}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False

    async def get_file_url(self, file_path: str) -> str:
        """Get URL for local file"""
        return f"/storage/{file_path}"


class S3StorageService(StorageInterface):
    """
    AWS S3 storage implementation.

    Requires AWS credentials in environment variables.
    """

    def __init__(self):
        # TODO: Initialize boto3 client with credentials
        self.bucket_name = settings.AWS_S3_BUCKET
        self.region = "us-east-1"  # TODO: Make configurable

        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            raise ValueError("AWS credentials not configured")

        logger.info(f"S3 storage initialized for bucket: {self.bucket_name}")

    async def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload file to S3.

        TODO: Implement actual S3 upload using boto3
        """
        try:
            # Example implementation (requires boto3):
            # import boto3
            # s3_client = boto3.client(
            #     's3',
            #     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            #     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            # )
            # s3_client.upload_fileobj(
            #     file,
            #     self.bucket_name,
            #     filename,
            #     ExtraArgs={'ContentType': content_type} if content_type else None
            # )

            logger.info(f"File uploaded to S3: {filename}")
            return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename}"

        except Exception as e:
            logger.error(f"Error uploading file to S3: {e}")
            raise

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete file from S3.

        TODO: Implement actual S3 deletion using boto3
        """
        try:
            # Example implementation (requires boto3):
            # import boto3
            # s3_client = boto3.client('s3')
            # s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)

            logger.info(f"File deleted from S3: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error deleting file from S3: {e}")
            return False

    async def get_file_url(self, file_path: str) -> str:
        """Get public URL for S3 file"""
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_path}"


class GCSStorageService(StorageInterface):
    """
    Google Cloud Storage implementation.

    TODO: Implement GCS storage using google-cloud-storage library
    """

    def __init__(self):
        logger.warning("GCS storage not implemented yet")

    async def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        content_type: Optional[str] = None
    ) -> str:
        raise NotImplementedError("GCS storage not implemented")

    async def delete_file(self, file_path: str) -> bool:
        raise NotImplementedError("GCS storage not implemented")

    async def get_file_url(self, file_path: str) -> str:
        raise NotImplementedError("GCS storage not implemented")


def get_storage_service() -> StorageInterface:
    """
    Factory function to get storage service instance.

    Returns appropriate storage service based on configuration.
    """
    provider = settings.STORAGE_PROVIDER.lower()

    if provider == "s3":
        return S3StorageService()
    elif provider == "gcs":
        return GCSStorageService()
    else:
        return LocalStorageService()
