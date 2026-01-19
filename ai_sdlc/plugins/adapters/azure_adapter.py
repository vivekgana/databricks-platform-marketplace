"""
Azure Plugin Adapter.

Integrates with Azure services (Blob Storage, Key Vault, ACR).
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta

from ai_sdlc.plugins.base import (
    CloudStoragePlugin,
    SecretsPlugin,
    PluginType,
    PluginCapability,
)

logger = logging.getLogger(__name__)


class AzureAdapter(CloudStoragePlugin, SecretsPlugin):
    """Azure services plugin adapter."""

    def __init__(self):
        super().__init__()
        self.blob_service_client = None
        self.secret_client = None
        self.container_name = None
        self.storage_account = None
        self.key_vault_url = None

    def get_name(self) -> str:
        return "azure"

    def get_type(self) -> PluginType:
        return PluginType.CLOUD_STORAGE

    def get_capabilities(self) -> List[PluginCapability]:
        return [
            PluginCapability.FILE_STORAGE,
            PluginCapability.SECRETS_MANAGEMENT,
        ]

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Azure configuration."""
        # Either connection string or storage account name required
        has_storage = "connection_string" in config or "storage_account" in config
        return has_storage

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize Azure clients."""
        try:
            from azure.storage.blob import BlobServiceClient
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential

            self.container_name = config.get("container", "evidence")

            # Initialize Blob Storage client
            if "connection_string" in config:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    config["connection_string"]
                )
            else:
                self.storage_account = config.get("storage_account", "")
                account_url = f"https://{self.storage_account}.blob.core.windows.net"

                if "storage_key" in config:
                    from azure.storage.blob import BlobServiceClient

                    self.blob_service_client = BlobServiceClient(
                        account_url=account_url, credential=config["storage_key"]
                    )
                else:
                    # Use Azure AD authentication
                    credential = DefaultAzureCredential()
                    self.blob_service_client = BlobServiceClient(
                        account_url=account_url, credential=credential
                    )

            # Ensure container exists
            try:
                self.blob_service_client.create_container(self.container_name)
            except Exception:
                pass  # Container already exists

            # Initialize Key Vault client if configured
            if "key_vault_url" in config:
                self.key_vault_url = config["key_vault_url"]
                credential = DefaultAzureCredential()
                self.secret_client = SecretClient(
                    vault_url=self.key_vault_url, credential=credential
                )

            self.config = config
            self.initialized = True
            logger.info(
                f"Initialized Azure adapter for storage account {self.storage_account}"
            )
            return True

        except ImportError:
            logger.error(
                "Azure SDK not installed. Install with: pip install azure-storage-blob azure-keyvault-secrets azure-identity"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Azure adapter: {e}")
            return False

    # Cloud Storage (Blob Storage) methods
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Upload file to Azure Blob Storage."""
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=remote_path
        )

        with open(local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True, metadata=metadata or {})

        url = blob_client.url
        logger.info(f"Uploaded {local_path} to {url}")
        return url

    def download_file(self, remote_path: str, local_path: str) -> str:
        """Download file from Azure Blob Storage."""
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=remote_path
        )

        with open(local_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        logger.info(f"Downloaded {remote_path} to {local_path}")
        return local_path

    def list_files(self, prefix: str = "") -> List[str]:
        """List files in Azure Blob Storage."""
        container_client = self.blob_service_client.get_container_client(
            self.container_name
        )

        blobs = container_client.list_blobs(name_starts_with=prefix)
        return [blob.name for blob in blobs]

    def delete_file(self, remote_path: str) -> bool:
        """Delete file from Azure Blob Storage."""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=remote_path
            )
            blob_client.delete_blob()

            logger.info(f"Deleted {remote_path} from Azure Blob Storage")
            return True

        except Exception as e:
            logger.error(f"Failed to delete {remote_path}: {e}")
            return False

    def get_signed_url(self, remote_path: str, expiration_seconds: int = 3600) -> str:
        """Get SAS URL for temporary access."""
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions

        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=remote_path
        )

        # Generate SAS token
        sas_token = generate_blob_sas(
            account_name=self.storage_account,
            container_name=self.container_name,
            blob_name=remote_path,
            account_key=self.config.get("storage_key", ""),
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(seconds=expiration_seconds),
        )

        return f"{blob_client.url}?{sas_token}"

    # Secrets Management (Key Vault) methods
    def get_secret(self, secret_name: str) -> str:
        """Get secret from Azure Key Vault."""
        if not self.secret_client:
            raise RuntimeError("Key Vault not configured")

        try:
            secret = self.secret_client.get_secret(secret_name)
            return secret.value

        except Exception as e:
            logger.error(f"Failed to get secret {secret_name}: {e}")
            raise

    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Set secret in Azure Key Vault."""
        if not self.secret_client:
            raise RuntimeError("Key Vault not configured")

        try:
            self.secret_client.set_secret(secret_name, secret_value)
            logger.info(f"Set secret {secret_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to set secret {secret_name}: {e}")
            return False

    def delete_secret(self, secret_name: str) -> bool:
        """Delete secret from Azure Key Vault."""
        if not self.secret_client:
            raise RuntimeError("Key Vault not configured")

        try:
            poller = self.secret_client.begin_delete_secret(secret_name)
            poller.wait()

            logger.info(f"Deleted secret {secret_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete secret {secret_name}: {e}")
            return False

    def list_secrets(self) -> List[str]:
        """List all secrets in Key Vault."""
        if not self.secret_client:
            raise RuntimeError("Key Vault not configured")

        try:
            secrets = self.secret_client.list_properties_of_secrets()
            return [secret.name for secret in secrets]

        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
