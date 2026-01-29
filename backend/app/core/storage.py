import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

import aiofiles

from app.config import get_settings

settings = get_settings()


class BaseStorageService(ABC):
    """Abstract base class for storage services."""

    @abstractmethod
    async def save_raw_file(self, content: bytes, original_filename: str) -> str:
        pass

    @abstractmethod
    async def save_text_file(self, content: str, candidate_id: str) -> str:
        pass

    @abstractmethod
    async def save_evidence_file(self, content: str, candidate_id: str) -> str:
        pass

    @abstractmethod
    async def read_file(self, uri: str) -> bytes:
        pass

    @abstractmethod
    async def read_text_file(self, uri: str) -> str:
        pass

    @abstractmethod
    async def delete_file(self, uri: str) -> bool:
        pass


class LocalStorageService(BaseStorageService):
    """Local file storage service for documents and extracted content."""

    def __init__(self):
        self.base_path = Path(settings.storage_path)
        self.raw_path = self.base_path / "raw"
        self.text_path = self.base_path / "text"
        self.evidence_path = self.base_path / "evidence"

        # Ensure directories exist
        for path in [self.raw_path, self.text_path, self.evidence_path]:
            path.mkdir(parents=True, exist_ok=True)

    def _generate_filename(self, original_filename: str) -> str:
        """Generate a unique filename while preserving extension."""
        ext = Path(original_filename).suffix
        return f"{uuid.uuid4()}{ext}"

    async def save_raw_file(self, content: bytes, original_filename: str) -> str:
        """Save an uploaded raw file and return its URI."""
        filename = self._generate_filename(original_filename)
        filepath = self.raw_path / filename

        async with aiofiles.open(filepath, "wb") as f:
            await f.write(content)

        return f"raw/{filename}"

    async def save_text_file(self, content: str, candidate_id: str) -> str:
        """Save extracted text content and return its URI."""
        filename = f"{candidate_id}_{uuid.uuid4()}.txt"
        filepath = self.text_path / filename

        async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
            await f.write(content)

        return f"text/{filename}"

    async def save_evidence_file(self, content: str, candidate_id: str) -> str:
        """Save evidence JSON and return its URI."""
        filename = f"{candidate_id}_{uuid.uuid4()}.json"
        filepath = self.evidence_path / filename

        async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
            await f.write(content)

        return f"evidence/{filename}"

    async def read_file(self, uri: str) -> bytes:
        """Read a file by its URI."""
        filepath = self.base_path / uri

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {uri}")

        async with aiofiles.open(filepath, "rb") as f:
            return await f.read()

    async def read_text_file(self, uri: str) -> str:
        """Read a text file by its URI."""
        filepath = self.base_path / uri

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {uri}")

        async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
            return await f.read()

    async def delete_file(self, uri: str) -> bool:
        """Delete a file by its URI."""
        filepath = self.base_path / uri

        if filepath.exists():
            os.remove(filepath)
            return True
        return False

    def get_full_path(self, uri: str) -> Path:
        """Get the full filesystem path for a URI."""
        return self.base_path / uri


class GCSStorageService(BaseStorageService):
    """Google Cloud Storage service for documents and extracted content."""

    def __init__(self):
        from google.cloud import storage
        self.client = storage.Client()
        self.bucket_name = settings.gcs_bucket
        self.bucket = self.client.bucket(self.bucket_name)

    def _generate_filename(self, original_filename: str) -> str:
        """Generate a unique filename while preserving extension."""
        ext = Path(original_filename).suffix
        return f"{uuid.uuid4()}{ext}"

    async def save_raw_file(self, content: bytes, original_filename: str) -> str:
        """Save an uploaded raw file and return its URI."""
        filename = self._generate_filename(original_filename)
        blob_name = f"raw/{filename}"
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(content)
        return blob_name

    async def save_text_file(self, content: str, candidate_id: str) -> str:
        """Save extracted text content and return its URI."""
        filename = f"{candidate_id}_{uuid.uuid4()}.txt"
        blob_name = f"text/{filename}"
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(content, content_type="text/plain; charset=utf-8")
        return blob_name

    async def save_evidence_file(self, content: str, candidate_id: str) -> str:
        """Save evidence JSON and return its URI."""
        filename = f"{candidate_id}_{uuid.uuid4()}.json"
        blob_name = f"evidence/{filename}"
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(content, content_type="application/json")
        return blob_name

    async def read_file(self, uri: str) -> bytes:
        """Read a file by its URI."""
        blob = self.bucket.blob(uri)
        if not blob.exists():
            raise FileNotFoundError(f"File not found: {uri}")
        return blob.download_as_bytes()

    async def read_text_file(self, uri: str) -> str:
        """Read a text file by its URI."""
        blob = self.bucket.blob(uri)
        if not blob.exists():
            raise FileNotFoundError(f"File not found: {uri}")
        return blob.download_as_text()

    async def delete_file(self, uri: str) -> bool:
        """Delete a file by its URI."""
        blob = self.bucket.blob(uri)
        if blob.exists():
            blob.delete()
            return True
        return False


# Alias for backwards compatibility
StorageService = LocalStorageService


def get_storage() -> BaseStorageService:
    """Dependency that provides the storage service based on environment."""
    if settings.gcs_bucket:
        return GCSStorageService()
    return LocalStorageService()
