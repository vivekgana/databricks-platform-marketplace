"""
Plugin configuration management.

Handles loading and validation of plugin configurations.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class PluginConfig:
    """Plugin configuration."""

    name: str
    type: str
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """
    Manages AI-SDLC configuration files.

    Loads configuration from:
    1. .aisdlc/config.yaml in project root
    2. Environment variables
    3. Databricks secrets (if available)
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to config file (default: .aisdlc/config.yaml)
        """
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()

    def _find_config_file(self) -> str:
        """
        Find configuration file in project hierarchy.

        Returns:
            Path to config file
        """
        # Check current directory
        current_dir = Path.cwd()
        config_file = current_dir / ".aisdlc" / "config.yaml"

        if config_file.exists():
            return str(config_file)

        # Check parent directories
        for parent in current_dir.parents:
            config_file = parent / ".aisdlc" / "config.yaml"
            if config_file.exists():
                return str(config_file)

        # Use default location
        return str(current_dir / ".aisdlc" / "config.yaml")

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        Returns:
            Configuration dictionary
        """
        if not os.path.exists(self.config_path):
            return self._get_default_config()

        try:
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)
                return self._resolve_env_vars(config)
        except Exception as e:
            print(f"Warning: Failed to load config from {self.config_path}: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.

        Returns:
            Default configuration dictionary
        """
        return {
            "version": "1.0",
            "active_plugins": {
                "agile": "ado",
                "source_control": "azure_repos",
                "artifacts": "azure_artifacts",
                "ci_cd": "azure_pipelines",
            },
            "plugins": {},
            "secrets": {"provider": "env", "config": {}},
            "evidence": {
                "storage_type": "plugin",
                "retention_days": 90,
                "compression": True,
            },
        }

    def _resolve_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve environment variables in configuration.

        Replaces ${VAR_NAME} with environment variable values.

        Args:
            config: Configuration dictionary

        Returns:
            Configuration with resolved variables
        """
        if isinstance(config, dict):
            return {k: self._resolve_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._resolve_env_vars(item) for item in config]
        elif (
            isinstance(config, str) and config.startswith("${") and config.endswith("}")
        ):
            var_name = config[2:-1]
            return os.environ.get(var_name, config)
        else:
            return config

    def get_active_plugin(self, plugin_type: str) -> str:
        """
        Get active plugin name for a type.

        Args:
            plugin_type: Plugin type (agile, source_control, etc.)

        Returns:
            Active plugin name
        """
        return self.config.get("active_plugins", {}).get(plugin_type, "")

    def get_plugin_config(self, plugin_name: str) -> Optional[PluginConfig]:
        """
        Get configuration for a plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            PluginConfig or None if not found
        """
        plugin_data = self.config.get("plugins", {}).get(plugin_name)
        if not plugin_data:
            return None

        return PluginConfig(
            name=plugin_name,
            type=plugin_data.get("type", plugin_name),
            enabled=plugin_data.get("enabled", True),
            config=plugin_data.get("config", {}),
        )

    def get_secret(self, secret_name: str) -> Optional[str]:
        """
        Get secret value.

        Args:
            secret_name: Secret identifier

        Returns:
            Secret value or None
        """
        secrets_config = self.config.get("secrets", {})
        provider = secrets_config.get("provider", "env")

        if provider == "env":
            return os.environ.get(secret_name)
        elif provider == "databricks":
            try:
                from databricks.sdk import WorkspaceClient

                w = WorkspaceClient()
                scope = secrets_config.get("config", {}).get("scope", "ai-sdlc-secrets")
                return w.secrets.get_secret(scope=scope, key=secret_name).value
            except Exception as e:
                print(f"Warning: Failed to get Databricks secret {secret_name}: {e}")
                return None
        else:
            print(f"Warning: Unsupported secrets provider: {provider}")
            return None

    def save_config(self) -> bool:
        """
        Save configuration to file.

        Returns:
            True if successful
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

            with open(self.config_path, "w") as f:
                yaml.safe_dump(
                    self.config, f, default_flow_style=False, sort_keys=False
                )
            return True
        except Exception as e:
            print(f"Error: Failed to save config to {self.config_path}: {e}")
            return False

    def set_value(self, key_path: str, value: Any) -> bool:
        """
        Set configuration value using dot notation.

        Args:
            key_path: Dot-separated key path (e.g., "active_plugins.agile")
            value: Value to set

        Returns:
            True if successful

        Example:
            config.set_value("active_plugins.agile", "jira")
        """
        keys = key_path.split(".")
        current = self.config

        # Navigate to parent
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set value
        current[keys[-1]] = value
        return True

    def get_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key_path: Dot-separated key path
            default: Default value if not found

        Returns:
            Configuration value

        Example:
            agile_type = config.get_value("active_plugins.agile")
        """
        keys = key_path.split(".")
        current = self.config

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default

        return current
