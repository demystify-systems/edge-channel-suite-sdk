"""
File Loaders - Fetch files from various sources.

Supports:
- HTTP/HTTPS URLs
- Google Cloud Storage (GCS)
- Amazon S3
- Local filesystem
"""

import os
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FileLoaderError(Exception):
    """Base exception for file loading errors."""
    pass


class FileLoader:
    """Base class for file loaders."""

    async def load_file(self, source: str, destination: Optional[str] = None) -> str:
        """
        Load file from source to destination.
        
        Args:
            source: Source location (URL, path, bucket path)
            destination: Local destination path (if None, creates temp file)
            
        Returns:
            Path to downloaded/copied file
            
        Raises:
            FileLoaderError: If loading fails
        """
        raise NotImplementedError


class HTTPFileLoader(FileLoader):
    """Load files from HTTP/HTTPS URLs."""

    def __init__(self, timeout: int = 300, chunk_size: int = 8192):
        """
        Initialize HTTP loader.
        
        Args:
            timeout: Request timeout in seconds
            chunk_size: Download chunk size in bytes
        """
        self.timeout = timeout
        self.chunk_size = chunk_size

    async def load_file(self, source: str, destination: Optional[str] = None) -> str:
        """
        Download file from HTTP URL.
        
        Args:
            source: HTTP/HTTPS URL
            destination: Local file path
            
        Returns:
            Path to downloaded file
        """
        try:
            import aiohttp
        except ImportError:
            raise FileLoaderError(
                "aiohttp not installed. Install with: pip install aiohttp"
            )

        if not destination:
            import tempfile
            fd, destination = tempfile.mkstemp(suffix=".download")
            os.close(fd)

        logger.info(f"Downloading file from {source} to {destination}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    source,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    response.raise_for_status()

                    total_size = int(response.headers.get("content-length", 0))
                    downloaded = 0

                    with open(destination, "wb") as f:
                        async for chunk in response.content.iter_chunked(self.chunk_size):
                            f.write(chunk)
                            downloaded += len(chunk)

                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                if percent % 10 < 0.5:  # Log every ~10%
                                    logger.debug(f"Downloaded {percent:.1f}%")

            logger.info(f"Downloaded {downloaded} bytes to {destination}")
            return destination

        except Exception as e:
            if os.path.exists(destination):
                os.remove(destination)
            raise FileLoaderError(f"HTTP download failed: {e}")


class GCSFileLoader(FileLoader):
    """Load files from Google Cloud Storage."""

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize GCS loader.
        
        Args:
            credentials_path: Path to GCS credentials JSON (or use GOOGLE_APPLICATION_CREDENTIALS env)
        """
        self.credentials_path = credentials_path

    async def load_file(self, source: str, destination: Optional[str] = None) -> str:
        """
        Download file from GCS.
        
        Args:
            source: GCS path in format gs://bucket-name/path/to/file
            destination: Local file path
            
        Returns:
            Path to downloaded file
        """
        try:
            from google.cloud import storage
        except ImportError:
            raise FileLoaderError(
                "google-cloud-storage not installed. Install with: pip install google-cloud-storage"
            )

        if not source.startswith("gs://"):
            raise FileLoaderError(f"Invalid GCS path: {source}. Must start with gs://")

        # Parse bucket and blob path
        source = source[5:]  # Remove gs://
        parts = source.split("/", 1)
        if len(parts) != 2:
            raise FileLoaderError(f"Invalid GCS path format: gs://{source}")

        bucket_name, blob_path = parts

        if not destination:
            import tempfile
            fd, destination = tempfile.mkstemp(suffix=Path(blob_path).suffix)
            os.close(fd)

        logger.info(f"Downloading from GCS: gs://{bucket_name}/{blob_path}")

        try:
            # Initialize client
            if self.credentials_path:
                client = storage.Client.from_service_account_json(self.credentials_path)
            else:
                client = storage.Client()

            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_path)

            # Download to file
            await asyncio.to_thread(blob.download_to_filename, destination)

            file_size = os.path.getsize(destination)
            logger.info(f"Downloaded {file_size} bytes from GCS to {destination}")
            return destination

        except Exception as e:
            if os.path.exists(destination):
                os.remove(destination)
            raise FileLoaderError(f"GCS download failed: {e}")


class S3FileLoader(FileLoader):
    """Load files from Amazon S3."""

    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
    ):
        """
        Initialize S3 loader.
        
        Args:
            aws_access_key_id: AWS access key (or use AWS_ACCESS_KEY_ID env)
            aws_secret_access_key: AWS secret key (or use AWS_SECRET_ACCESS_KEY env)
            region_name: AWS region (or use AWS_DEFAULT_REGION env)
        """
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name

    async def load_file(self, source: str, destination: Optional[str] = None) -> str:
        """
        Download file from S3.
        
        Args:
            source: S3 path in format s3://bucket-name/path/to/file
            destination: Local file path
            
        Returns:
            Path to downloaded file
        """
        try:
            import boto3
        except ImportError:
            raise FileLoaderError(
                "boto3 not installed. Install with: pip install boto3"
            )

        if not source.startswith("s3://"):
            raise FileLoaderError(f"Invalid S3 path: {source}. Must start with s3://")

        # Parse bucket and key
        source = source[5:]  # Remove s3://
        parts = source.split("/", 1)
        if len(parts) != 2:
            raise FileLoaderError(f"Invalid S3 path format: s3://{source}")

        bucket_name, key = parts

        if not destination:
            import tempfile
            fd, destination = tempfile.mkstemp(suffix=Path(key).suffix)
            os.close(fd)

        logger.info(f"Downloading from S3: s3://{bucket_name}/{key}")

        try:
            # Initialize client
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name,
            )

            # Download to file
            await asyncio.to_thread(
                s3_client.download_file, bucket_name, key, destination
            )

            file_size = os.path.getsize(destination)
            logger.info(f"Downloaded {file_size} bytes from S3 to {destination}")
            return destination

        except Exception as e:
            if os.path.exists(destination):
                os.remove(destination)
            raise FileLoaderError(f"S3 download failed: {e}")


class LocalFileLoader(FileLoader):
    """Load files from local filesystem."""

    async def load_file(self, source: str, destination: Optional[str] = None) -> str:
        """
        Copy or reference local file.
        
        Args:
            source: Local file path
            destination: Destination path (if None, returns source path)
            
        Returns:
            Path to file
        """
        if not os.path.exists(source):
            raise FileLoaderError(f"File not found: {source}")

        if not os.path.isfile(source):
            raise FileLoaderError(f"Path is not a file: {source}")

        # If no destination, just return source path
        if not destination:
            logger.info(f"Using local file: {source}")
            return source

        # Copy to destination
        logger.info(f"Copying {source} to {destination}")
        try:
            import shutil
            await asyncio.to_thread(shutil.copy2, source, destination)
            return destination
        except Exception as e:
            raise FileLoaderError(f"Local file copy failed: {e}")


class FileLoaderFactory:
    """Factory to create appropriate file loader based on source type."""

    @staticmethod
    def create_loader(source: str, config: Optional[Dict[str, Any]] = None) -> FileLoader:
        """
        Create appropriate file loader for source.
        
        Args:
            source: File source (URL, path, etc.)
            config: Optional configuration for loader
            
        Returns:
            FileLoader instance
        """
        config = config or {}

        if source.startswith("http://") or source.startswith("https://"):
            return HTTPFileLoader(
                timeout=config.get("timeout", 300),
                chunk_size=config.get("chunk_size", 8192),
            )
        elif source.startswith("gs://"):
            return GCSFileLoader(
                credentials_path=config.get("gcs_credentials_path"),
            )
        elif source.startswith("s3://"):
            return S3FileLoader(
                aws_access_key_id=config.get("aws_access_key_id"),
                aws_secret_access_key=config.get("aws_secret_access_key"),
                region_name=config.get("aws_region"),
            )
        else:
            # Assume local file
            return LocalFileLoader()

    @staticmethod
    async def load_file(
        source: str,
        destination: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Convenience method to load file with automatic loader selection.
        
        Args:
            source: File source
            destination: Destination path
            config: Loader configuration
            
        Returns:
            Path to loaded file
        """
        loader = FileLoaderFactory.create_loader(source, config)
        return await loader.load_file(source, destination)
