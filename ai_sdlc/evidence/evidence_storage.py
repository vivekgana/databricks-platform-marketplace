"""
Evidence Storage

Provides storage backends for evidence artifacts including Azure Blob Storage.
"""

import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class EvidenceStorage(ABC):
    """
    Abstract base class for evidence storage backends.
    """

    @abstractmethod
    def upload_file(
        self, local_path: str, remote_path: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload a file to storage.

        Args:
            local_path: Local file path
            remote_path: Remote path in storage
            metadata: Optional metadata

        Returns:
            URL or path to uploaded file
        """
        pass

    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """
        Download a file from storage.

        Args:
            remote_path: Remote path in storage
            local_path: Local file path to save to

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def list_files(self, prefix: str) -> List[str]:
        """
        List files in storage with given prefix.

        Args:
            prefix: Path prefix

        Returns:
            List of file paths
        """
        pass

    @abstractmethod
    def get_file_url(self, remote_path: str) -> str:
        """
        Get URL for a file in storage.

        Args:
            remote_path: Remote path in storage

        Returns:
            URL to access the file
        """
        pass

    @abstractmethod
    def delete_file(self, remote_path: str) -> bool:
        """
        Delete a file from storage.

        Args:
            remote_path: Remote path in storage

        Returns:
            True if successful, False otherwise
        """
        pass


class AzureBlobEvidenceStorage(EvidenceStorage):
    """
    Azure Blob Storage backend for evidence.

    Stores evidence artifacts in Azure Blob Storage for the Audit Cortex 2 project.
    """

    def __init__(
        self,
        container_name: str = "audit-cortex-evidence",
        connection_string: Optional[str] = None,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
    ):
        """
        Initialize Azure Blob Storage.

        Args:
            container_name: Blob container name (default: audit-cortex-evidence)
            connection_string: Azure Storage connection string
            account_name: Storage account name (alternative to connection_string)
            account_key: Storage account key (alternative to connection_string)
        """
        self.container_name = container_name
        self.connection_string = connection_string or os.getenv(
            "AZURE_STORAGE_CONNECTION_STRING"
        )
        self.account_name = account_name or os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self.account_key = account_key or os.getenv("AZURE_STORAGE_ACCOUNT_KEY")

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Initialize Azure Blob Storage client
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Azure Blob Storage client."""
        try:
            from azure.storage.blob import BlobServiceClient

            if self.connection_string:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    self.connection_string
                )
            elif self.account_name and self.account_key:
                account_url = f"https://{self.account_name}.blob.core.windows.net"
                self.blob_service_client = BlobServiceClient(
                    account_url=account_url, credential=self.account_key
                )
            else:
                self.logger.warning(
                    "No Azure credentials provided. Storage will not be available."
                )
                self.blob_service_client = None
                return

            # Get or create container
            self.container_client = self.blob_service_client.get_container_client(
                self.container_name
            )

            # Create container if it doesn't exist
            if not self.container_client.exists():
                self.container_client.create_container()
                self.logger.info(f"Created container: {self.container_name}")

        except ImportError:
            self.logger.error(
                "azure-storage-blob package not installed. "
                "Install with: pip install azure-storage-blob"
            )
            self.blob_service_client = None
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure Blob Storage: {e}")
            self.blob_service_client = None

    def upload_file(
        self, local_path: str, remote_path: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload a file to Azure Blob Storage.

        Args:
            local_path: Local file path
            remote_path: Remote blob path (e.g., PBI-123/planning/plan.md)
            metadata: Optional metadata to attach to blob

        Returns:
            URL to the uploaded blob
        """
        if not self.blob_service_client:
            raise RuntimeError("Azure Blob Storage client not initialized")

        try:
            # Get blob client
            blob_client = self.container_client.get_blob_client(remote_path)

            # Read file
            with open(local_path, "rb") as data:
                # Upload with metadata
                blob_client.upload_blob(
                    data, overwrite=True, metadata=metadata or {}
                )

            url = blob_client.url
            self.logger.info(f"Uploaded {local_path} to {url}")

            return url

        except Exception as e:
            self.logger.error(f"Failed to upload {local_path}: {e}")
            raise

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """
        Download a file from Azure Blob Storage.

        Args:
            remote_path: Remote blob path
            local_path: Local file path to save to

        Returns:
            True if successful, False otherwise
        """
        if not self.blob_service_client:
            self.logger.error("Azure Blob Storage client not initialized")
            return False

        try:
            # Get blob client
            blob_client = self.container_client.get_blob_client(remote_path)

            # Download blob
            with open(local_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())

            self.logger.info(f"Downloaded {remote_path} to {local_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to download {remote_path}: {e}")
            return False

    def list_files(self, prefix: str) -> List[str]:
        """
        List files in Azure Blob Storage with given prefix.

        Args:
            prefix: Path prefix (e.g., PBI-123/planning/)

        Returns:
            List of blob paths
        """
        if not self.blob_service_client:
            self.logger.error("Azure Blob Storage client not initialized")
            return []

        try:
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            return [blob.name for blob in blobs]

        except Exception as e:
            self.logger.error(f"Failed to list files with prefix {prefix}: {e}")
            return []

    def get_file_url(self, remote_path: str) -> str:
        """
        Get URL for a blob.

        Args:
            remote_path: Remote blob path

        Returns:
            URL to access the blob
        """
        if not self.blob_service_client:
            raise RuntimeError("Azure Blob Storage client not initialized")

        blob_client = self.container_client.get_blob_client(remote_path)
        return blob_client.url

    def delete_file(self, remote_path: str) -> bool:
        """
        Delete a file from Azure Blob Storage.

        Args:
            remote_path: Remote blob path

        Returns:
            True if successful, False otherwise
        """
        if not self.blob_service_client:
            self.logger.error("Azure Blob Storage client not initialized")
            return False

        try:
            blob_client = self.container_client.get_blob_client(remote_path)
            blob_client.delete_blob()

            self.logger.info(f"Deleted blob: {remote_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete {remote_path}: {e}")
            return False

    def generate_sas_url(
        self, remote_path: str, expiry_hours: int = 24
    ) -> Optional[str]:
        """
        Generate a SAS URL for temporary access to a blob.

        Args:
            remote_path: Remote blob path
            expiry_hours: Hours until SAS token expires (default: 24)

        Returns:
            SAS URL or None if failed
        """
        if not self.blob_service_client:
            self.logger.error("Azure Blob Storage client not initialized")
            return None

        try:
            from azure.storage.blob import generate_blob_sas, BlobSasPermissions
            from datetime import datetime, timedelta

            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=self.container_name,
                blob_name=remote_path,
                account_key=self.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours),
            )

            # Construct full URL with SAS token
            blob_client = self.container_client.get_blob_client(remote_path)
            sas_url = f"{blob_client.url}?{sas_token}"

            return sas_url

        except Exception as e:
            self.logger.error(f"Failed to generate SAS URL for {remote_path}: {e}")
            return None


class LocalFileEvidenceStorage(EvidenceStorage):
    """
    Local filesystem storage backend for evidence.

    Stores evidence artifacts in local filesystem for development/testing.
    """

    def __init__(self, base_path: str):
        """
        Initialize local file storage.

        Args:
            base_path: Base directory for evidence storage
        """
        self.base_path = Path(base_path)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Create base directory
        self.base_path.mkdir(parents=True, exist_ok=True)

    def upload_file(
        self, local_path: str, remote_path: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Copy file to local storage.

        Args:
            local_path: Source file path
            remote_path: Destination relative path
            metadata: Optional metadata (stored as JSON sidecar)

        Returns:
            Path to the stored file
        """
        try:
            # Create destination path
            dest_path = self.base_path / remote_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            import shutil

            shutil.copy2(local_path, dest_path)

            # Save metadata if provided
            if metadata:
                metadata_path = dest_path.with_suffix(dest_path.suffix + ".meta.json")
                import json

                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)

            self.logger.info(f"Copied {local_path} to {dest_path}")

            return str(dest_path)

        except Exception as e:
            self.logger.error(f"Failed to copy {local_path}: {e}")
            raise

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """
        Copy file from local storage.

        Args:
            remote_path: Source relative path
            local_path: Destination file path

        Returns:
            True if successful, False otherwise
        """
        try:
            source_path = self.base_path / remote_path

            if not source_path.exists():
                self.logger.error(f"File not found: {source_path}")
                return False

            # Copy file
            import shutil

            shutil.copy2(source_path, local_path)

            self.logger.info(f"Copied {source_path} to {local_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to copy {remote_path}: {e}")
            return False

    def list_files(self, prefix: str) -> List[str]:
        """
        List files with given prefix.

        Args:
            prefix: Path prefix

        Returns:
            List of relative file paths
        """
        try:
            prefix_path = self.base_path / prefix
            if not prefix_path.exists():
                return []

            # Find all files under prefix
            files = []
            for path in prefix_path.rglob("*"):
                if path.is_file() and not path.name.endswith(".meta.json"):
                    rel_path = path.relative_to(self.base_path)
                    files.append(str(rel_path))

            return files

        except Exception as e:
            self.logger.error(f"Failed to list files with prefix {prefix}: {e}")
            return []

    def get_file_url(self, remote_path: str) -> str:
        """
        Get file URL (local file path).

        Args:
            remote_path: Relative path

        Returns:
            Absolute file path
        """
        file_path = self.base_path / remote_path
        return f"file://{file_path.absolute()}"

    def delete_file(self, remote_path: str) -> bool:
        """
        Delete a file from local storage.

        Args:
            remote_path: Relative path

        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.base_path / remote_path

            if not file_path.exists():
                self.logger.warning(f"File not found: {file_path}")
                return False

            file_path.unlink()

            # Delete metadata if exists
            metadata_path = file_path.with_suffix(file_path.suffix + ".meta.json")
            if metadata_path.exists():
                metadata_path.unlink()

            self.logger.info(f"Deleted file: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete {remote_path}: {e}")
            return False
