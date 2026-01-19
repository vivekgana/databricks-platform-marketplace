"""
Unit tests for Plugin Manager.

Tests the plugin lifecycle management and configuration loading.
"""

import pytest
import os
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from ai_sdlc.plugins.manager import PluginManager
from ai_sdlc.plugins.config import ConfigManager
from ai_sdlc.plugins.base import WorkItemPlugin


class TestPluginManager:
    """Test Plugin Manager functionality."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary config directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".aisdlc"
            config_dir.mkdir()
            yield config_dir

    @pytest.fixture
    def sample_config(self, temp_config_dir):
        """Create a sample configuration file."""
        config = {
            "active_plugins": {
                "agile": "ado",
                "source_control": "github",
                "cloud_storage": "azure",
            },
            "plugins": {
                "ado": {
                    "enabled": True,
                    "type": "ado",
                    "config": {
                        "organization": "test-org",
                        "project": "TestProject",
                        "pat": "test-token",
                    },
                },
                "github": {
                    "enabled": True,
                    "type": "github",
                    "config": {
                        "owner": "test-owner",
                        "repository": "test-repo",
                        "token": "test-token",
                    },
                },
                "azure": {
                    "enabled": True,
                    "type": "azure",
                    "config": {
                        "storage_account": "testaccount",
                        "container_name": "testcontainer",
                        "storage_key": "testkey",
                    },
                },
            },
        }

        config_file = temp_config_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        return config_file

    def test_singleton_pattern(self):
        """Test that PluginManager is a singleton."""
        # Reset singleton for testing
        PluginManager._instance = None

        manager1 = PluginManager()
        manager2 = PluginManager()

        assert manager1 is manager2

    @patch("ai_sdlc.plugins.manager.ConfigManager")
    def test_get_active_plugin(self, mock_config_manager_class):
        """Test getting active plugin name."""
        # Reset singleton
        PluginManager._instance = None

        # Mock config manager
        mock_config = Mock()
        mock_config.get_active_plugin.return_value = "ado"
        mock_config_manager_class.return_value = mock_config

        manager = PluginManager()
        plugin_name = manager.config_manager.get_active_plugin("agile")

        assert plugin_name == "ado"

    @patch("ai_sdlc.plugins.manager.ConfigManager")
    @patch("ai_sdlc.plugins.adapters.ado_adapter.ADOAdapter")
    def test_load_plugin(self, mock_ado_adapter_class, mock_config_manager_class):
        """Test loading a plugin."""
        # Reset singleton
        PluginManager._instance = None

        # Mock config manager
        mock_config = Mock()
        mock_plugin_config = Mock()
        mock_plugin_config.enabled = True
        mock_plugin_config.type = "ado"
        mock_plugin_config.config = {
            "organization": "test-org",
            "project": "TestProject",
            "pat": "test-token",
        }
        mock_config.get_plugin_config.return_value = mock_plugin_config
        mock_config_manager_class.return_value = mock_config

        # Mock ADO adapter
        mock_adapter = Mock()
        mock_adapter.initialize.return_value = True
        mock_ado_adapter_class.return_value = mock_adapter

        # Create manager
        manager = PluginManager()
        manager.plugin_registry = {"ado": mock_ado_adapter_class}

        # Load plugin
        plugin = manager.load_plugin("ado")

        assert plugin is not None
        assert plugin == mock_adapter
        mock_adapter.initialize.assert_called_once()

    @patch("ai_sdlc.plugins.manager.ConfigManager")
    def test_load_disabled_plugin(self, mock_config_manager_class):
        """Test that disabled plugins are not loaded."""
        # Reset singleton
        PluginManager._instance = None

        # Mock config manager with disabled plugin
        mock_config = Mock()
        mock_plugin_config = Mock()
        mock_plugin_config.enabled = False
        mock_config.get_plugin_config.return_value = mock_plugin_config
        mock_config_manager_class.return_value = mock_config

        manager = PluginManager()
        plugin = manager.load_plugin("ado")

        assert plugin is None

    @patch("ai_sdlc.plugins.manager.ConfigManager")
    @patch("ai_sdlc.plugins.adapters.ado_adapter.ADOAdapter")
    def test_get_agile_plugin(self, mock_ado_adapter_class, mock_config_manager_class):
        """Test getting agile plugin."""
        # Reset singleton
        PluginManager._instance = None

        # Mock config manager
        mock_config = Mock()
        mock_config.get_active_plugin.return_value = "ado"
        mock_plugin_config = Mock()
        mock_plugin_config.enabled = True
        mock_plugin_config.type = "ado"
        mock_plugin_config.config = {}
        mock_config.get_plugin_config.return_value = mock_plugin_config
        mock_config_manager_class.return_value = mock_config

        # Mock ADO adapter
        mock_adapter = Mock(spec=WorkItemPlugin)
        mock_adapter.initialize.return_value = True
        mock_ado_adapter_class.return_value = mock_adapter

        manager = PluginManager()
        manager.plugin_registry = {"ado": mock_ado_adapter_class}

        plugin = manager.get_agile_plugin()

        assert plugin is not None
        assert isinstance(plugin, WorkItemPlugin) or hasattr(plugin, "get_work_item")

    @patch("ai_sdlc.plugins.manager.ConfigManager")
    def test_plugin_caching(self, mock_config_manager_class):
        """Test that plugins are cached after first load."""
        # Reset singleton
        PluginManager._instance = None

        # Mock config manager
        mock_config = Mock()
        mock_config.get_active_plugin.return_value = "ado"
        mock_plugin_config = Mock()
        mock_plugin_config.enabled = True
        mock_plugin_config.type = "ado"
        mock_plugin_config.config = {}
        mock_config.get_plugin_config.return_value = mock_plugin_config
        mock_config_manager_class.return_value = mock_config

        # Mock adapter
        mock_adapter_class = Mock()
        mock_adapter = Mock()
        mock_adapter.initialize.return_value = True
        mock_adapter_class.return_value = mock_adapter

        manager = PluginManager()
        manager.plugin_registry = {"ado": mock_adapter_class}

        # Load plugin twice
        plugin1 = manager.load_plugin("ado")
        plugin2 = manager.load_plugin("ado")

        # Should be the same instance (cached)
        assert plugin1 is plugin2
        # Adapter class should only be called once
        mock_adapter_class.assert_called_once()

    @patch("ai_sdlc.plugins.manager.ConfigManager")
    @patch("ai_sdlc.plugins.adapters.ado_adapter.ADOAdapter")
    def test_failed_initialization(
        self, mock_ado_adapter_class, mock_config_manager_class
    ):
        """Test handling of failed plugin initialization."""
        # Reset singleton
        PluginManager._instance = None

        # Mock config manager
        mock_config = Mock()
        mock_plugin_config = Mock()
        mock_plugin_config.enabled = True
        mock_plugin_config.type = "ado"
        mock_plugin_config.config = {}
        mock_config.get_plugin_config.return_value = mock_plugin_config
        mock_config_manager_class.return_value = mock_config

        # Mock ADO adapter with failed initialization
        mock_adapter = Mock()
        mock_adapter.initialize.return_value = False  # Initialization fails
        mock_ado_adapter_class.return_value = mock_adapter

        manager = PluginManager()
        manager.plugin_registry = {"ado": mock_ado_adapter_class}

        # Load plugin should return None on failed initialization
        plugin = manager.load_plugin("ado")

        assert plugin is None


class TestConfigManager:
    """Test Configuration Manager functionality."""

    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            config = {
                "active_plugins": {"agile": "ado"},
                "plugins": {
                    "ado": {
                        "enabled": True,
                        "type": "ado",
                        "config": {
                            "organization": "${TEST_ORG}",
                            "project": "TestProject",
                        },
                    }
                },
            }
            yaml.dump(config, f)
            temp_path = f.name

        yield temp_path

        # Cleanup
        os.unlink(temp_path)

    def test_load_config(self, temp_config_file):
        """Test loading configuration from file."""
        config_manager = ConfigManager(config_path=temp_config_file)

        assert config_manager.config is not None
        assert "active_plugins" in config_manager.config
        assert config_manager.config["active_plugins"]["agile"] == "ado"

    def test_env_var_resolution(self, temp_config_file):
        """Test environment variable resolution."""
        os.environ["TEST_ORG"] = "resolved-org"

        config_manager = ConfigManager(config_path=temp_config_file)
        plugin_config = config_manager.get_plugin_config("ado")

        assert plugin_config.config["organization"] == "resolved-org"

        # Cleanup
        del os.environ["TEST_ORG"]

    def test_get_active_plugin(self, temp_config_file):
        """Test getting active plugin name."""
        config_manager = ConfigManager(config_path=temp_config_file)
        plugin_name = config_manager.get_active_plugin("agile")

        assert plugin_name == "ado"

    def test_get_plugin_config(self, temp_config_file):
        """Test getting plugin configuration."""
        config_manager = ConfigManager(config_path=temp_config_file)
        plugin_config = config_manager.get_plugin_config("ado")

        assert plugin_config is not None
        assert plugin_config.enabled is True
        assert plugin_config.type == "ado"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
