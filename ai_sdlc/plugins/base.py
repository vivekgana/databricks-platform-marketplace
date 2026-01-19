"""
Base plugin interfaces for AI-SDLC.

All tool integrations must implement these interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum

from .models import (
    WorkItem,
    WorkItemUpdate,
    PullRequest,
    Artifact,
    PipelineRun,
    Comment,
    Attachment,
)


class PluginType(Enum):
    """Types of plugins supported."""

    AGILE = "agile"
    SOURCE_CONTROL = "source_control"
    CI_CD = "ci_cd"
    ARTIFACT_STORAGE = "artifact_storage"
    COMMUNICATION = "communication"
    CLOUD_STORAGE = "cloud_storage"
    SECRETS = "secrets"


class PluginCapability(Enum):
    """Capabilities that plugins can provide."""

    WORK_ITEM_MANAGEMENT = "work_item_management"
    ARTIFACT_STORAGE = "artifact_storage"
    PULL_REQUEST = "pull_request"
    PIPELINE_EXECUTION = "pipeline_execution"
    NOTIFICATION = "notification"
    FILE_STORAGE = "file_storage"
    SECRETS_MANAGEMENT = "secrets_management"
    CONTAINER_REGISTRY = "container_registry"


class BasePlugin(ABC):
    """Base class for all AI-SDLC plugins."""

    def __init__(self):
        """Initialize plugin."""
        self.config = {}
        self.initialized = False

    @abstractmethod
    def get_name(self) -> str:
        """Return plugin name."""
        pass

    @abstractmethod
    def get_type(self) -> PluginType:
        """Return plugin type."""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[PluginCapability]:
        """Return list of capabilities this plugin provides."""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize plugin with configuration.

        Args:
            config: Plugin-specific configuration

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate plugin configuration.

        Args:
            config: Configuration to validate

        Returns:
            True if configuration is valid
        """
        pass

    def shutdown(self):
        """Cleanup resources on shutdown."""
        pass


class WorkItemPlugin(BasePlugin):
    """Plugin for work item/issue management."""

    @abstractmethod
    def get_work_item(self, work_item_id: str) -> WorkItem:
        """
        Get work item by ID.

        Args:
            work_item_id: Work item identifier

        Returns:
            WorkItem object
        """
        pass

    @abstractmethod
    def create_work_item(
        self,
        title: str,
        description: str,
        item_type: str,
        parent_id: Optional[str] = None,
        assigned_to: Optional[str] = None,
        **kwargs,
    ) -> WorkItem:
        """
        Create new work item.

        Args:
            title: Work item title
            description: Work item description
            item_type: Type (epic, feature, story, task, bug)
            parent_id: Parent work item ID
            assigned_to: Assignee
            **kwargs: Additional tool-specific fields

        Returns:
            Created WorkItem
        """
        pass

    @abstractmethod
    def update_work_item(self, work_item_id: str, update: WorkItemUpdate) -> WorkItem:
        """
        Update work item.

        Args:
            work_item_id: Work item identifier
            update: Update specification

        Returns:
            Updated WorkItem
        """
        pass

    @abstractmethod
    def add_comment(self, work_item_id: str, comment: str) -> Comment:
        """
        Add comment to work item.

        Args:
            work_item_id: Work item identifier
            comment: Comment text

        Returns:
            Created Comment
        """
        pass

    @abstractmethod
    def attach_file(
        self, work_item_id: str, file_path: str, comment: Optional[str] = None
    ) -> Attachment:
        """
        Attach file to work item.

        Args:
            work_item_id: Work item identifier
            file_path: Path to file
            comment: Optional comment

        Returns:
            Attachment object
        """
        pass

    @abstractmethod
    def get_children(self, work_item_id: str) -> List[WorkItem]:
        """
        Get child work items.

        Args:
            work_item_id: Parent work item identifier

        Returns:
            List of child WorkItems
        """
        pass

    @abstractmethod
    def link_work_items(self, source_id: str, target_id: str, link_type: str) -> bool:
        """
        Create link between work items.

        Args:
            source_id: Source work item ID
            target_id: Target work item ID
            link_type: Link type (related, parent, child, blocks, etc.)

        Returns:
            True if successful
        """
        pass

    def search_work_items(self, query: str, max_results: int = 100) -> List[WorkItem]:
        """
        Search work items.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of matching WorkItems
        """
        raise NotImplementedError("Search not implemented for this plugin")


class PullRequestPlugin(BasePlugin):
    """Plugin for pull request/merge request management."""

    @abstractmethod
    def create_pull_request(
        self,
        title: str,
        description: str,
        source_branch: str,
        target_branch: str,
        work_item_ids: Optional[List[str]] = None,
        reviewers: Optional[List[str]] = None,
    ) -> PullRequest:
        """
        Create pull request.

        Args:
            title: PR title
            description: PR description
            source_branch: Source branch name
            target_branch: Target branch name
            work_item_ids: Associated work item IDs
            reviewers: Reviewer usernames

        Returns:
            Created PullRequest
        """
        pass

    @abstractmethod
    def get_pull_request(self, pr_id: str) -> PullRequest:
        """
        Get pull request by ID.

        Args:
            pr_id: Pull request identifier

        Returns:
            PullRequest object
        """
        pass

    @abstractmethod
    def add_comment(self, pr_id: str, comment: str) -> Comment:
        """
        Add comment to pull request.

        Args:
            pr_id: Pull request identifier
            comment: Comment text

        Returns:
            Created Comment
        """
        pass

    @abstractmethod
    def link_work_items(self, pr_id: str, work_item_ids: List[str]) -> bool:
        """
        Link work items to pull request.

        Args:
            pr_id: Pull request identifier
            work_item_ids: Work item identifiers

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def get_changed_files(self, pr_id: str) -> List[str]:
        """
        Get list of changed files in pull request.

        Args:
            pr_id: Pull request identifier

        Returns:
            List of file paths
        """
        pass

    def approve_pull_request(self, pr_id: str, comment: Optional[str] = None) -> bool:
        """
        Approve pull request.

        Args:
            pr_id: Pull request identifier
            comment: Optional approval comment

        Returns:
            True if successful
        """
        raise NotImplementedError("Approval not implemented for this plugin")

    def merge_pull_request(self, pr_id: str, merge_method: str = "merge") -> bool:
        """
        Merge pull request.

        Args:
            pr_id: Pull request identifier
            merge_method: Merge method (merge, squash, rebase)

        Returns:
            True if successful
        """
        raise NotImplementedError("Merge not implemented for this plugin")


class ArtifactPlugin(BasePlugin):
    """Plugin for artifact storage and versioning."""

    @abstractmethod
    def upload_artifact(
        self,
        name: str,
        version: str,
        files: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        """
        Upload artifact package.

        Args:
            name: Artifact name
            version: Semantic version
            files: List of file paths to include
            metadata: Optional metadata

        Returns:
            Created Artifact
        """
        pass

    @abstractmethod
    def download_artifact(self, name: str, version: str, destination: str) -> str:
        """
        Download artifact.

        Args:
            name: Artifact name
            version: Version to download
            destination: Local destination path

        Returns:
            Path to downloaded artifact
        """
        pass

    @abstractmethod
    def list_versions(self, artifact_name: str) -> List[str]:
        """
        List all versions of an artifact.

        Args:
            artifact_name: Artifact name

        Returns:
            List of version strings
        """
        pass

    def link_to_work_item(self, artifact: Artifact, work_item_id: str) -> bool:
        """
        Link artifact to work item.

        Args:
            artifact: Artifact to link
            work_item_id: Work item identifier

        Returns:
            True if successful
        """
        # Default implementation - may not be supported by all plugins
        return False

    def delete_artifact(self, name: str, version: str) -> bool:
        """
        Delete artifact version.

        Args:
            name: Artifact name
            version: Version to delete

        Returns:
            True if successful
        """
        raise NotImplementedError("Delete not implemented for this plugin")


class PipelinePlugin(BasePlugin):
    """Plugin for CI/CD pipeline execution."""

    @abstractmethod
    def trigger_pipeline(
        self,
        pipeline_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        branch: Optional[str] = None,
    ) -> PipelineRun:
        """
        Trigger pipeline execution.

        Args:
            pipeline_name: Pipeline name/ID
            parameters: Pipeline parameters
            branch: Branch to run on

        Returns:
            PipelineRun object
        """
        pass

    @abstractmethod
    def get_pipeline_run(self, run_id: str) -> PipelineRun:
        """
        Get pipeline run status.

        Args:
            run_id: Pipeline run identifier

        Returns:
            PipelineRun object
        """
        pass

    @abstractmethod
    def get_logs(self, run_id: str) -> str:
        """
        Get pipeline execution logs.

        Args:
            run_id: Pipeline run identifier

        Returns:
            Log text
        """
        pass

    @abstractmethod
    def cancel_run(self, run_id: str) -> bool:
        """
        Cancel pipeline run.

        Args:
            run_id: Pipeline run identifier

        Returns:
            True if successful
        """
        pass

    def list_pipelines(self) -> List[Dict[str, Any]]:
        """
        List available pipelines.

        Returns:
            List of pipeline definitions
        """
        raise NotImplementedError("List pipelines not implemented for this plugin")


class CloudStoragePlugin(BasePlugin):
    """Plugin for cloud file storage (S3, Azure Blob, GCS)."""

    @abstractmethod
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Upload file to cloud storage.

        Args:
            local_path: Local file path
            remote_path: Remote path/key
            metadata: Optional metadata

        Returns:
            Remote URL
        """
        pass

    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> str:
        """
        Download file from cloud storage.

        Args:
            remote_path: Remote path/key
            local_path: Local destination path

        Returns:
            Local file path
        """
        pass

    @abstractmethod
    def list_files(self, prefix: str = "") -> List[str]:
        """
        List files in cloud storage.

        Args:
            prefix: Path prefix to filter

        Returns:
            List of remote paths
        """
        pass

    @abstractmethod
    def delete_file(self, remote_path: str) -> bool:
        """
        Delete file from cloud storage.

        Args:
            remote_path: Remote path/key

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def get_signed_url(self, remote_path: str, expiration_seconds: int = 3600) -> str:
        """
        Get signed URL for temporary access.

        Args:
            remote_path: Remote path/key
            expiration_seconds: URL expiration time

        Returns:
            Signed URL
        """
        pass


class SecretsPlugin(BasePlugin):
    """Plugin for secrets management (Key Vault, Secrets Manager, etc.)."""

    @abstractmethod
    def get_secret(self, secret_name: str) -> str:
        """
        Get secret value.

        Args:
            secret_name: Secret identifier

        Returns:
            Secret value
        """
        pass

    @abstractmethod
    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """
        Set secret value.

        Args:
            secret_name: Secret identifier
            secret_value: Secret value

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def delete_secret(self, secret_name: str) -> bool:
        """
        Delete secret.

        Args:
            secret_name: Secret identifier

        Returns:
            True if successful
        """
        pass

    def list_secrets(self) -> List[str]:
        """
        List available secret names.

        Returns:
            List of secret names
        """
        raise NotImplementedError("List secrets not implemented for this plugin")
