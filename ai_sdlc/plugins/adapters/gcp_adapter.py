"""
GCP Plugin Adapter.

Integrates with Google Cloud Platform services (Cloud Storage, Secret Manager, GCR).
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


class GCPAdapter(CloudStoragePlugin, SecretsPlugin):
    """Google Cloud Platform services plugin adapter."""

    def __init__(self):
        super().__init__()
        self.storage_client = None
        self.secrets_client = None
        self.bucket = None
        self.project_id = None

    def get_name(self) -> str:
        return "gcp"

    def get_type(self) -> PluginType:
        return PluginType.CLOUD_STORAGE

    def get_capabilities(self) -> List[PluginCapability]:
        return [
            PluginCapability.FILE_STORAGE,
            PluginCapability.SECRETS_MANAGEMENT,
        ]

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate GCP configuration."""
        required = ["project_id"]
        return all(k in config for k in required)

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize GCP clients."""
        try:
            from google.cloud import storage
            from google.cloud import secretmanager

            self.project_id = config["project_id"]
            self.bucket = config.get("bucket", "")

            # Set credentials if provided
            if "credentials_file" in config:
                import os

                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config[
                    "credentials_file"
                ]

            # Initialize Cloud Storage client
            self.storage_client = storage.Client(project=self.project_id)

            # Ensure bucket exists
            if self.bucket:
                try:
                    self.storage_client.create_bucket(self.bucket)
                except Exception:
                    pass  # Bucket already exists

            # Initialize Secret Manager client
            secret_project = config.get("secret_project_id", self.project_id)
            self.secrets_client = secretmanager.SecretManagerServiceClient()
            self.secret_project_path = f"projects/{secret_project}"

            self.config = config
            self.initialized = True
            logger.info(f"Initialized GCP adapter for project {self.project_id}")
            return True

        except ImportError:
            logger.error(
                "GCP SDK not installed. Install with: pip install google-cloud-storage google-cloud-secret-manager"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to initialize GCP adapter: {e}")
            return False

    # Cloud Storage methods
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Upload file to Google Cloud Storage."""
        bucket = self.storage_client.bucket(self.bucket)
        blob = bucket.blob(remote_path)

        if metadata:
            blob.metadata = {k: str(v) for k, v in metadata.items()}

        blob.upload_from_filename(local_path)

        url = f"gs://{self.bucket}/{remote_path}"
        logger.info(f"Uploaded {local_path} to {url}")
        return url

    def download_file(self, remote_path: str, local_path: str) -> str:
        """Download file from Google Cloud Storage."""
        bucket = self.storage_client.bucket(self.bucket)
        blob = bucket.blob(remote_path)

        blob.download_to_filename(local_path)

        logger.info(f"Downloaded {remote_path} to {local_path}")
        return local_path

    def list_files(self, prefix: str = "") -> List[str]:
        """List files in Google Cloud Storage bucket."""
        bucket = self.storage_client.bucket(self.bucket)
        blobs = bucket.list_blobs(prefix=prefix)

        return [blob.name for blob in blobs]

    def delete_file(self, remote_path: str) -> bool:
        """Delete file from Google Cloud Storage."""
        try:
            bucket = self.storage_client.bucket(self.bucket)
            blob = bucket.blob(remote_path)
            blob.delete()

            logger.info(f"Deleted {remote_path} from GCS")
            return True

        except Exception as e:
            logger.error(f"Failed to delete {remote_path}: {e}")
            return False

    def get_signed_url(self, remote_path: str, expiration_seconds: int = 3600) -> str:
        """Get signed URL for temporary access."""
        bucket = self.storage_client.bucket(self.bucket)
        blob = bucket.blob(remote_path)

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(seconds=expiration_seconds),
            method="GET",
        )

        return url

    # Secrets Management methods
    def get_secret(self, secret_name: str) -> str:
        """Get secret from Google Secret Manager."""
        try:
            # Build the resource name
            name = f"{self.secret_project_path}/secrets/{secret_name}/versions/latest"

            # Access the secret version
            response = self.secrets_client.access_secret_version(request={"name": name})

            # Return the decoded payload
            return response.payload.data.decode("UTF-8")

        except Exception as e:
            logger.error(f"Failed to get secret {secret_name}: {e}")
            raise

    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Set secret in Google Secret Manager."""
        try:
            # Check if secret exists
            secret_path = f"{self.secret_project_path}/secrets/{secret_name}"

            try:
                self.secrets_client.get_secret(request={"name": secret_path})
                secret_exists = True
            except Exception:
                secret_exists = False

            # Create secret if it doesn't exist
            if not secret_exists:
                from google.cloud import secretmanager

                self.secrets_client.create_secret(
                    request={
                        "parent": self.secret_project_path,
                        "secret_id": secret_name,
                        "secret": {
                            "replication": {"automatic": {}},
                        },
                    }
                )

            # Add secret version
            self.secrets_client.add_secret_version(
                request={
                    "parent": secret_path,
                    "payload": {"data": secret_value.encode("UTF-8")},
                }
            )

            logger.info(f"Set secret {secret_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to set secret {secret_name}: {e}")
            return False

    def delete_secret(self, secret_name: str) -> bool:
        """Delete secret from Google Secret Manager."""
        try:
            secret_path = f"{self.secret_project_path}/secrets/{secret_name}"
            self.secrets_client.delete_secret(request={"name": secret_path})

            logger.info(f"Deleted secret {secret_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete secret {secret_name}: {e}")
            return False

    def list_secrets(self) -> List[str]:
        """List all secrets in Secret Manager."""
        try:
            secrets = self.secrets_client.list_secrets(
                request={"parent": self.secret_project_path}
            )

            return [secret.name.split("/")[-1] for secret in secrets]

        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
