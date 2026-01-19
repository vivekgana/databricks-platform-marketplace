"""
AI-SDLC Plugin System

Provides tool-agnostic interfaces for agile, source control, and CI/CD integrations.
"""

from .base import (
    BasePlugin,
    PluginType,
    PluginCapability,
    WorkItemPlugin,
    PullRequestPlugin,
    ArtifactPlugin,
    PipelinePlugin,
)
from .models import (
    WorkItem,
    WorkItemUpdate,
    PullRequest,
    Artifact,
    PipelineRun,
)
from .manager import PluginManager
from .config import PluginConfig

__all__ = [
    "BasePlugin",
    "PluginType",
    "PluginCapability",
    "WorkItemPlugin",
    "PullRequestPlugin",
    "ArtifactPlugin",
    "PipelinePlugin",
    "WorkItem",
    "WorkItemUpdate",
    "PullRequest",
    "Artifact",
    "PipelineRun",
    "PluginManager",
    "PluginConfig",
]
