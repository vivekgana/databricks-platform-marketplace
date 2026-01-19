"""
Plugin Manager for AI-SDLC.

Handles plugin discovery, loading, and lifecycle management.
"""

import logging
from typing import Dict, List, Optional, Type, Any

from .base import (
    BasePlugin,
    WorkItemPlugin,
    PullRequestPlugin,
    ArtifactPlugin,
    PipelinePlugin,
    CloudStoragePlugin,
    SecretsPlugin,
    PluginType,
)
from .config import ConfigManager, PluginConfig

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Manages plugin lifecycle and provides unified interface.

    Singleton pattern - only one instance per process.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize plugin manager.

        Args:
            config_path: Path to configuration file
        """
        if self._initialized:
            return

        self.config_manager = ConfigManager(config_path)
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_registry: Dict[str, Type[BasePlugin]] = {}
        self._register_built_in_plugins()
        self._initialized = True

    def _register_built_in_plugins(self):
        """Register built-in plugins."""
        # Import and register plugins here
        # This is done lazily to avoid import errors if dependencies are missing

        try:
            from .adapters.ado_adapter import ADOAdapter

            self.register_plugin("ado", ADOAdapter)
        except ImportError:
            logger.debug("ADO adapter not available")

        try:
            from .adapters.jira_adapter import JiraAdapter

            self.register_plugin("jira", JiraAdapter)
        except ImportError:
            logger.debug("JIRA adapter not available")

        try:
            from .adapters.github_adapter import GitHubAdapter

            self.register_plugin("github", GitHubAdapter)
        except ImportError:
            logger.debug("GitHub adapter not available")

        try:
            from .adapters.gitlab_adapter import GitLabAdapter

            self.register_plugin("gitlab", GitLabAdapter)
        except ImportError:
            logger.debug("GitLab adapter not available")

        try:
            from .adapters.aws_adapter import AWSAdapter

            self.register_plugin("aws", AWSAdapter)
        except ImportError:
            logger.debug("AWS adapter not available")

        try:
            from .adapters.azure_adapter import AzureAdapter

            self.register_plugin("azure", AzureAdapter)
        except ImportError:
            logger.debug("Azure adapter not available")

        try:
            from .adapters.gcp_adapter import GCPAdapter

            self.register_plugin("gcp", GCPAdapter)
        except ImportError:
            logger.debug("GCP adapter not available")

    def register_plugin(self, name: str, plugin_class: Type[BasePlugin]):
        """
        Register a plugin class.

        Args:
            name: Plugin name
            plugin_class: Plugin class
        """
        self.plugin_registry[name] = plugin_class
        logger.debug(f"Registered plugin: {name}")

    def load_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        Load and initialize a plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            Initialized plugin or None if failed
        """
        # Check if already loaded
        if plugin_name in self.plugins:
            return self.plugins[plugin_name]

        # Get plugin configuration
        plugin_config = self.config_manager.get_plugin_config(plugin_name)
        if not plugin_config or not plugin_config.enabled:
            logger.warning(f"Plugin {plugin_name} is not enabled or not configured")
            return None

        # Get plugin class
        plugin_class = self.plugin_registry.get(plugin_config.type)
        if not plugin_class:
            logger.error(f"Plugin type {plugin_config.type} not found in registry")
            return None

        try:
            # Instantiate plugin
            plugin = plugin_class()

            # Resolve secrets in config
            resolved_config = self._resolve_secrets(plugin_config.config)

            # Initialize plugin
            if not plugin.initialize(resolved_config):
                logger.error(f"Failed to initialize plugin {plugin_name}")
                return None

            # Cache plugin
            self.plugins[plugin_name] = plugin
            logger.info(f"Loaded plugin: {plugin_name}")
            return plugin

        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name}: {e}")
            return None

    def _resolve_secrets(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve secret references in configuration.

        Args:
            config: Configuration dictionary

        Returns:
            Configuration with resolved secrets
        """
        resolved = {}
        for key, value in config.items():
            if isinstance(value, dict):
                resolved[key] = self._resolve_secrets(value)
            elif isinstance(value, str) and key.endswith("_secret"):
                # This is a secret reference - get actual value
                secret_name = value
                secret_value = self.config_manager.get_secret(secret_name)
                if secret_value:
                    # Store without _secret suffix
                    resolved[key.replace("_secret", "")] = secret_value
                else:
                    logger.warning(f"Could not resolve secret: {secret_name}")
            else:
                resolved[key] = value
        return resolved

    def get_plugin(self, capability: str) -> Optional[BasePlugin]:
        """
        Get plugin for a capability.

        Args:
            capability: Capability type (agile, source_control, artifacts, ci_cd, etc.)

        Returns:
            Plugin instance or None

        Example:
            # Get agile plugin (could be ADO, JIRA, etc.)
            agile = manager.get_plugin("agile")
            work_item = agile.get_work_item("12345")
        """
        # Get active plugin name for this capability
        plugin_name = self.config_manager.get_active_plugin(capability)
        if not plugin_name:
            logger.warning(f"No active plugin configured for {capability}")
            return None

        # Load and return plugin
        return self.load_plugin(plugin_name)

    def get_agile_plugin(self) -> Optional[WorkItemPlugin]:
        """
        Get agile/work item management plugin.

        Returns:
            WorkItemPlugin instance or None
        """
        return self.get_plugin("agile")

    def get_source_control_plugin(self) -> Optional[PullRequestPlugin]:
        """
        Get source control/pull request plugin.

        Returns:
            PullRequestPlugin instance or None
        """
        return self.get_plugin("source_control")

    def get_artifacts_plugin(self) -> Optional[ArtifactPlugin]:
        """
        Get artifact storage plugin.

        Returns:
            ArtifactPlugin instance or None
        """
        return self.get_plugin("artifacts")

    def get_pipeline_plugin(self) -> Optional[PipelinePlugin]:
        """
        Get CI/CD pipeline plugin.

        Returns:
            PipelinePlugin instance or None
        """
        return self.get_plugin("ci_cd")

    def get_cloud_storage_plugin(self) -> Optional[CloudStoragePlugin]:
        """
        Get cloud storage plugin.

        Returns:
            CloudStoragePlugin instance or None
        """
        return self.get_plugin("cloud_storage")

    def get_secrets_plugin(self) -> Optional[SecretsPlugin]:
        """
        Get secrets management plugin.

        Returns:
            SecretsPlugin instance or None
        """
        return self.get_plugin("secrets")

    def list_plugins(self) -> List[str]:
        """
        List all registered plugin names.

        Returns:
            List of plugin names
        """
        return list(self.plugin_registry.keys())

    def list_loaded_plugins(self) -> List[str]:
        """
        List currently loaded plugin names.

        Returns:
            List of loaded plugin names
        """
        return list(self.plugins.keys())

    def reload_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        Reload a plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            Reloaded plugin or None
        """
        # Unload if already loaded
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            plugin.shutdown()
            del self.plugins[plugin_name]

        # Load again
        return self.load_plugin(plugin_name)

    def shutdown(self):
        """Shutdown all plugins."""
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.shutdown()
                logger.info(f"Shutdown plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"Error shutting down plugin {plugin_name}: {e}")

        self.plugins.clear()

    def get_config_manager(self) -> ConfigManager:
        """
        Get configuration manager.

        Returns:
            ConfigManager instance
        """
        return self.config_manager
