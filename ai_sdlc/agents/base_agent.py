"""
Base Agent for AI-SDLC

Provides base class and interfaces for all workflow agents.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ai_sdlc.plugins.manager import PluginManager
from ai_sdlc.plugins.base import (
    WorkItemPlugin,
    PullRequestPlugin,
    ArtifactPlugin,
    PipelinePlugin,
    CloudStoragePlugin,
    SecretsPlugin,
)

logger = logging.getLogger(__name__)


@dataclass
class AgentExecutionResult:
    """Result from agent execution."""

    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    evidence_paths: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    execution_time_seconds: float = 0.0

    def add_evidence(self, path: str):
        """Add an evidence file path."""
        self.evidence_paths.append(path)

    def add_log(self, message: str):
        """Add a log message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")


class BaseAgent(ABC):
    """
    Base class for all SDLC agents.

    Each agent is responsible for executing a specific stage of the workflow
    and producing evidence artifacts.
    """

    def __init__(
        self,
        work_item_id: str,
        config: Any,
        evidence_path: str,
    ):
        """
        Initialize the agent.

        Args:
            work_item_id: The work item ID being processed
            config: Plugin configuration
            evidence_path: Path to store evidence artifacts
        """
        self.work_item_id = work_item_id
        self.config = config
        self.evidence_path = evidence_path
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Initialize plugin manager (singleton)
        self.plugin_manager = PluginManager()

        # Create evidence directory
        Path(evidence_path).mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def execute(
        self,
        input_data: Dict[str, Any],
        timeout_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute the agent's task.

        Args:
            input_data: Input data from previous stages
            timeout_seconds: Optional timeout in seconds

        Returns:
            Dictionary with:
            {
                "success": bool,
                "data": Dict[str, Any],
                "evidence_paths": List[str],
                "error_message": Optional[str],
                ...
            }
        """
        pass

    def _get_evidence_file_path(self, filename: str) -> str:
        """
        Get full path for an evidence file.

        Args:
            filename: Name of the evidence file

        Returns:
            Full path to evidence file
        """
        return str(Path(self.evidence_path) / filename)

    def _save_evidence_file(self, filename: str, content: str) -> str:
        """
        Save content to an evidence file.

        Args:
            filename: Name of the file
            content: Content to save

        Returns:
            Path to saved file
        """
        file_path = self._get_evidence_file_path(filename)
        try:
            Path(file_path).write_text(content, encoding="utf-8")
            self.logger.info(f"Saved evidence file: {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Error saving evidence file {file_path}: {e}")
            raise

    def _load_file(self, file_path: str) -> Optional[str]:
        """
        Load content from a file.

        Args:
            file_path: Path to the file

        Returns:
            File content or None if error
        """
        try:
            return Path(file_path).read_text(encoding="utf-8")
        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {e}")
            return None

    def _create_result(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        evidence_paths: Optional[List[str]] = None,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a standardized result dictionary.

        Args:
            success: Whether execution was successful
            data: Output data
            evidence_paths: List of evidence file paths
            error_message: Optional error message

        Returns:
            Result dictionary
        """
        result = AgentExecutionResult(
            success=success,
            data=data or {},
            evidence_paths=evidence_paths or [],
            error_message=error_message,
        )

        return {
            "success": result.success,
            "data": result.data,
            "evidence_paths": result.evidence_paths,
            "error_message": result.error_message,
            "logs": result.logs,
        }

    def _get_work_item_info(self) -> Dict[str, Any]:
        """
        Get work item information from previous stages.

        Returns:
            Dictionary with work item info
        """
        # This would typically fetch from input_data
        return {
            "work_item_id": self.work_item_id,
            "title": "Work Item Title",  # Would come from input_data
            "description": "Work Item Description",
        }

    def _log_start(self):
        """Log agent start."""
        self.logger.info(
            f"Starting {self.__class__.__name__} for work item {self.work_item_id}"
        )
        self.logger.info(f"Evidence path: {self.evidence_path}")

    def _log_complete(self, success: bool):
        """Log agent completion."""
        status = "successfully" if success else "with errors"
        self.logger.info(f"Completed {self.__class__.__name__} {status}")

    # Plugin accessor methods
    def get_agile_plugin(self) -> Optional[WorkItemPlugin]:
        """
        Get the agile/work item management plugin.

        Returns:
            WorkItemPlugin instance or None if not configured
        """
        return self.plugin_manager.get_agile_plugin()

    def get_source_control_plugin(self) -> Optional[PullRequestPlugin]:
        """
        Get the source control/pull request plugin.

        Returns:
            PullRequestPlugin instance or None if not configured
        """
        return self.plugin_manager.get_source_control_plugin()

    def get_artifact_plugin(self) -> Optional[ArtifactPlugin]:
        """
        Get the artifact storage plugin.

        Returns:
            ArtifactPlugin instance or None if not configured
        """
        return self.plugin_manager.get_artifact_plugin()

    def get_pipeline_plugin(self) -> Optional[PipelinePlugin]:
        """
        Get the CI/CD pipeline plugin.

        Returns:
            PipelinePlugin instance or None if not configured
        """
        return self.plugin_manager.get_pipeline_plugin()

    def get_cloud_storage_plugin(self) -> Optional[CloudStoragePlugin]:
        """
        Get the cloud storage plugin.

        Returns:
            CloudStoragePlugin instance or None if not configured
        """
        return self.plugin_manager.get_cloud_storage_plugin()

    def get_secrets_plugin(self) -> Optional[SecretsPlugin]:
        """
        Get the secrets management plugin.

        Returns:
            SecretsPlugin instance or None if not configured
        """
        return self.plugin_manager.get_secrets_plugin()

    def get_plugin(self, plugin_name: str):
        """
        Get a plugin by name.

        Args:
            plugin_name: Name of the plugin to retrieve

        Returns:
            Plugin instance or None if not found
        """
        return self.plugin_manager.get_plugin(plugin_name)
