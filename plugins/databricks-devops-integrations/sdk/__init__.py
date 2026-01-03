"""
DevOps Integration Plugin SDK

This SDK provides the base interface and utilities for creating
DevOps integration plugins for the Databricks Platform Marketplace.
"""

from .base_plugin import (
    DevOpsIntegrationPlugin,
    WorkItem,
    PluginConfig,
    PluginRegistry,
    PluginMetadata,
    WorkItemStatus,
    WorkItemPriority,
)
from .exceptions import (
    PluginError,
    AuthenticationError,
    ConfigurationError,
    WorkItemNotFoundError,
    IntegrationError,
)

__version__ = "1.0.0"

__all__ = [
    "DevOpsIntegrationPlugin",
    "WorkItem",
    "PluginConfig",
    "PluginRegistry",
    "PluginMetadata",
    "WorkItemStatus",
    "WorkItemPriority",
    "PluginError",
    "AuthenticationError",
    "ConfigurationError",
    "WorkItemNotFoundError",
    "IntegrationError",
]
