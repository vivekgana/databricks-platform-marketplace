"""
Base Plugin Interface for DevOps Integrations

This module defines the standard interface that all DevOps integration plugins
must implement to ensure consistent behavior across different platforms.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class WorkItemStatus(Enum):
    """Standard work item statuses"""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


class WorkItemPriority(Enum):
    """Standard work item priorities"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class WorkItem:
    """Universal work item model that works across all platforms"""

    id: str
    title: str
    description: str
    status: WorkItemStatus
    assignee: Optional[str] = None
    priority: WorkItemPriority = WorkItemPriority.MEDIUM
    labels: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    url: Optional[str] = None
    parent_id: Optional[str] = None
    story_points: Optional[float] = None


@dataclass
class PluginConfig:
    """Plugin configuration container"""

    plugin_id: str
    api_endpoint: str
    api_key: str
    organization: str
    project: str
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 30
    retry_attempts: int = 3
    verify_ssl: bool = True


@dataclass
class PluginMetadata:
    """Metadata about the plugin"""

    name: str
    version: str
    description: str
    author: str
    supported_features: List[str]
    requires_auth: bool = True
    documentation_url: Optional[str] = None


class DevOpsIntegrationPlugin(ABC):
    """
    Base class for all DevOps integration plugins

    Every plugin must implement these methods to provide consistent
    functionality across different DevOps platforms.
    """

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass

    @abstractmethod
    def authenticate(self, config: PluginConfig) -> bool:
        """
        Authenticate with the DevOps platform

        Args:
            config: Plugin configuration including credentials

        Returns:
            True if authentication successful, False otherwise

        Raises:
            AuthenticationError: If authentication fails
        """
        pass

    @abstractmethod
    def validate_config(self, config: PluginConfig) -> bool:
        """
        Validate plugin configuration

        Args:
            config: Plugin configuration to validate

        Returns:
            True if configuration is valid

        Raises:
            ConfigurationError: If configuration is invalid
        """
        pass

    @abstractmethod
    def create_work_item(
        self, work_item: WorkItem, config: PluginConfig
    ) -> str:
        """
        Create a new work item

        Args:
            work_item: Work item to create
            config: Plugin configuration

        Returns:
            ID of the created work item

        Raises:
            IntegrationError: If creation fails
        """
        pass

    @abstractmethod
    def update_work_item(
        self, item_id: str, updates: Dict[str, Any], config: PluginConfig
    ) -> bool:
        """
        Update existing work item

        Args:
            item_id: ID of work item to update
            updates: Dictionary of fields to update
            config: Plugin configuration

        Returns:
            True if update successful

        Raises:
            WorkItemNotFoundError: If work item not found
            IntegrationError: If update fails
        """
        pass

    @abstractmethod
    def get_work_item(
        self, item_id: str, config: PluginConfig
    ) -> WorkItem:
        """
        Retrieve work item details

        Args:
            item_id: ID of work item to retrieve
            config: Plugin configuration

        Returns:
            WorkItem object with details

        Raises:
            WorkItemNotFoundError: If work item not found
        """
        pass

    @abstractmethod
    def search_work_items(
        self, query: str, config: PluginConfig, limit: int = 100
    ) -> List[WorkItem]:
        """
        Search for work items

        Args:
            query: Search query string
            config: Plugin configuration
            limit: Maximum number of results

        Returns:
            List of matching work items
        """
        pass

    @abstractmethod
    def link_to_commit(
        self,
        item_id: str,
        commit_sha: str,
        repo_url: str,
        config: PluginConfig,
    ) -> bool:
        """
        Link work item to git commit

        Args:
            item_id: Work item ID
            commit_sha: Git commit SHA
            repo_url: Repository URL
            config: Plugin configuration

        Returns:
            True if link created successfully
        """
        pass

    @abstractmethod
    def link_to_pull_request(
        self, item_id: str, pr_url: str, config: PluginConfig
    ) -> bool:
        """
        Link work item to pull request

        Args:
            item_id: Work item ID
            pr_url: Pull request URL
            config: Plugin configuration

        Returns:
            True if link created successfully
        """
        pass

    @abstractmethod
    def create_from_incident(
        self, incident: Dict[str, Any], config: PluginConfig
    ) -> str:
        """
        Auto-create work item from production incident

        Args:
            incident: Incident details dictionary
            config: Plugin configuration

        Returns:
            ID of created work item
        """
        pass

    @abstractmethod
    def get_team_velocity(
        self, team_id: str, timeframe_days: int, config: PluginConfig
    ) -> Dict[str, float]:
        """
        Calculate team velocity metrics

        Args:
            team_id: Team identifier
            timeframe_days: Number of days to analyze
            config: Plugin configuration

        Returns:
            Dictionary with velocity metrics
        """
        pass

    @abstractmethod
    def webhook_handler(
        self, event_type: str, payload: Dict[str, Any], config: PluginConfig
    ) -> Dict[str, Any]:
        """
        Handle incoming webhooks from platform

        Args:
            event_type: Type of webhook event
            payload: Event payload
            config: Plugin configuration

        Returns:
            Response dictionary
        """
        pass

    def health_check(self, config: PluginConfig) -> Dict[str, Any]:
        """
        Check health of integration

        Args:
            config: Plugin configuration

        Returns:
            Health status dictionary
        """
        try:
            self.authenticate(config)
            return {
                "status": "healthy",
                "plugin": self.get_metadata().name,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "plugin": self.get_metadata().name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


class PluginRegistry:
    """Registry for managing installed plugins"""

    def __init__(self):
        self.plugins: Dict[str, DevOpsIntegrationPlugin] = {}
        self._configs: Dict[str, PluginConfig] = {}

    def register(
        self, plugin_id: str, plugin: DevOpsIntegrationPlugin, config: PluginConfig
    ):
        """
        Register a new plugin

        Args:
            plugin_id: Unique plugin identifier
            plugin: Plugin instance
            config: Plugin configuration
        """
        self.plugins[plugin_id] = plugin
        self._configs[plugin_id] = config

    def unregister(self, plugin_id: str):
        """
        Unregister a plugin

        Args:
            plugin_id: Plugin identifier to remove
        """
        if plugin_id in self.plugins:
            del self.plugins[plugin_id]
        if plugin_id in self._configs:
            del self._configs[plugin_id]

    def get_plugin(self, plugin_id: str) -> Optional[DevOpsIntegrationPlugin]:
        """
        Get a registered plugin

        Args:
            plugin_id: Plugin identifier

        Returns:
            Plugin instance or None
        """
        return self.plugins.get(plugin_id)

    def get_config(self, plugin_id: str) -> Optional[PluginConfig]:
        """
        Get plugin configuration

        Args:
            plugin_id: Plugin identifier

        Returns:
            Plugin configuration or None
        """
        return self._configs.get(plugin_id)

    def list_plugins(self) -> List[str]:
        """
        List all registered plugins

        Returns:
            List of plugin identifiers
        """
        return list(self.plugins.keys())

    def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Run health checks on all registered plugins

        Returns:
            Dictionary mapping plugin IDs to health status
        """
        results = {}
        for plugin_id, plugin in self.plugins.items():
            config = self._configs.get(plugin_id)
            if config:
                results[plugin_id] = plugin.health_check(config)
        return results
