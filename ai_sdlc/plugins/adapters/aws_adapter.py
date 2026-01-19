"""
AWS Plugin Adapter.

Integrates with AWS services (S3, Secrets Manager, ECR).
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from ai_sdlc.plugins.base import (
    CloudStoragePlugin,
    SecretsPlugin,
    PluginType,
    PluginCapability,
)

logger = logging.getLogger(__name__)


class AWSAdapter(CloudStoragePlugin, SecretsPlugin):
    """AWS services plugin adapter."""

    def __init__(self):
        super().__init__()
        self.s3_client = None
        self.secrets_client = None
        self.bucket = None
        self.region = None

    def get_name(self) -> str:
        return "aws"

    def get_type(self) -> PluginType:
        return PluginType.CLOUD_STORAGE

    def get_capabilities(self) -> List[PluginCapability]:
        return [
            PluginCapability.FILE_STORAGE,
            PluginCapability.SECRETS_MANAGEMENT,
        ]

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate AWS configuration."""
        required = ["region"]
        return all(k in config for k in required)

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize AWS clients."""
        try:
            import boto3

            self.region = config["region"]
            self.bucket = config.get("s3_bucket", "")

            # Initialize S3 client
            if "access_key" in config and "secret_key" in config:
                self.s3_client = boto3.client(
                    "s3",
                    region_name=self.region,
                    aws_access_key_id=config["access_key"],
                    aws_secret_access_key=config["secret_key"],
                )

                secrets_region = config.get("secrets_region", self.region)
                self.secrets_client = boto3.client(
                    "secretsmanager",
                    region_name=secrets_region,
                    aws_access_key_id=config["access_key"],
                    aws_secret_access_key=config["secret_key"],
                )
            else:
                # Use default credentials (IAM role, environment, etc.)
                self.s3_client = boto3.client("s3", region_name=self.region)
                secrets_region = config.get("secrets_region", self.region)
                self.secrets_client = boto3.client(
                    "secretsmanager", region_name=secrets_region
                )

            self.config = config
            self.initialized = True
            logger.info(f"Initialized AWS adapter for region {self.region}")
            return True

        except ImportError:
            logger.error("boto3 library not installed. Install with: pip install boto3")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize AWS adapter: {e}")
            return False

    # Cloud Storage (S3) methods
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Upload file to S3."""
        extra_args = {}
        if metadata:
            extra_args["Metadata"] = {k: str(v) for k, v in metadata.items()}

        self.s3_client.upload_file(
            local_path, self.bucket, remote_path, ExtraArgs=extra_args
        )

        url = f"s3://{self.bucket}/{remote_path}"
        logger.info(f"Uploaded {local_path} to {url}")
        return url

    def download_file(self, remote_path: str, local_path: str) -> str:
        """Download file from S3."""
        self.s3_client.download_file(self.bucket, remote_path, local_path)

        logger.info(f"Downloaded {remote_path} to {local_path}")
        return local_path

    def list_files(self, prefix: str = "") -> List[str]:
        """List files in S3 bucket."""
        response = self.s3_client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)

        files = []
        if "Contents" in response:
            files = [obj["Key"] for obj in response["Contents"]]

        return files

    def delete_file(self, remote_path: str) -> bool:
        """Delete file from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=remote_path)
            logger.info(f"Deleted {remote_path} from S3")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {remote_path}: {e}")
            return False

    def get_signed_url(self, remote_path: str, expiration_seconds: int = 3600) -> str:
        """Get signed URL for temporary access."""
        url = self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": remote_path},
            ExpiresIn=expiration_seconds,
        )

        return url

    # Secrets Management methods
    def get_secret(self, secret_name: str) -> str:
        """Get secret from AWS Secrets Manager."""
        try:
            response = self.secrets_client.get_secret_value(SecretId=secret_name)

            if "SecretString" in response:
                return response["SecretString"]
            else:
                # Binary secret
                import base64

                return base64.b64decode(response["SecretBinary"]).decode("utf-8")

        except Exception as e:
            logger.error(f"Failed to get secret {secret_name}: {e}")
            raise

    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Set secret in AWS Secrets Manager."""
        try:
            # Try to update existing secret
            try:
                self.secrets_client.update_secret(
                    SecretId=secret_name, SecretString=secret_value
                )
            except self.secrets_client.exceptions.ResourceNotFoundException:
                # Secret doesn't exist, create it
                self.secrets_client.create_secret(
                    Name=secret_name, SecretString=secret_value
                )

            logger.info(f"Set secret {secret_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to set secret {secret_name}: {e}")
            return False

    def delete_secret(self, secret_name: str) -> bool:
        """Delete secret from AWS Secrets Manager."""
        try:
            self.secrets_client.delete_secret(
                SecretId=secret_name, ForceDeleteWithoutRecovery=True
            )
            logger.info(f"Deleted secret {secret_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete secret {secret_name}: {e}")
            return False

    def list_secrets(self) -> List[str]:
        """List all secrets."""
        try:
            response = self.secrets_client.list_secrets()
            return [secret["Name"] for secret in response.get("SecretList", [])]

        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
