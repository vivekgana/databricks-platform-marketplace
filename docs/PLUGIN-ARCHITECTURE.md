# AI-SDLC Plugin Architecture

**Document Version:** 1.0
**Prepared by:** AI-SDLC Development Team
**Last Updated:** January 18, 2026 12:02 AM
**Contact:** AI-SDLC Support Team

## Table of Contents

- [Overview](#overview)
- [Architecture Design](#architecture-design)
- [Plugin Interface](#plugin-interface)
- [Supported Tools](#supported-tools)
- [Configuration System](#configuration-system)
- [Plugin Development](#plugin-development)
- [Migration Guide](#migration-guide)
- [Examples](#examples)

## Overview

The AI-SDLC system is redesigned to be completely agnostic to agile project management, DevOps, and source code management tools. This plugin architecture allows seamless integration with:

- **Agile Tools**: Azure DevOps, JIRA, Linear, Asana
- **Source Control**: GitHub, GitLab, Bitbucket, Azure Repos
- **CI/CD**: Azure Pipelines, GitHub Actions, GitLab CI, Jenkins
- **Communication**: Slack, Teams, Discord

### Design Principles

1. **Tool Agnostic**: Core agents, generators, and workflows have no direct dependencies on specific tools
2. **Plugin-Based**: All tool integrations implemented as plugins with unified interface
3. **Configuration-Driven**: Tool selection via configuration files, not code changes
4. **Extensible**: Easy to add new tool integrations without modifying core code
5. **Backward Compatible**: Existing integrations continue to work through adapters

## Architecture Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI-SDLC Core System                           │
│                                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐  │
│  │  Agents    │  │ Generators │  │ Workflows  │  │   CLI    │  │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘  │
│         │               │                │              │        │
│         └───────────────┴────────────────┴──────────────┘        │
│                            │                                     │
│                   ┌────────▼────────┐                            │
│                   │  Plugin Manager │                            │
│                   └────────┬────────┘                            │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│ Agile Plugins  │  │ Source Control  │  │  CI/CD Plugins │
│                │  │    Plugins      │  │                │
│ • ADO          │  │ • GitHub        │  │ • AzurePipeline│
│ • JIRA         │  │ • GitLab        │  │ • GitHub Action│
│ • Linear       │  │ • Bitbucket     │  │ • GitLab CI    │
│ • Asana        │  │ • Azure Repos   │  │ • Jenkins      │
└────────────────┘  └─────────────────┘  └────────────────┘
```

## Plugin Interface

All plugins implement standard interfaces for different capabilities:

### Base Plugin Interface

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum

class PluginType(Enum):
    """Types of plugins supported."""
    AGILE = "agile"
    SOURCE_CONTROL = "source_control"
    CI_CD = "ci_cd"
    COMMUNICATION = "communication"

class PluginCapability(Enum):
    """Capabilities that plugins can provide."""
    WORK_ITEM_MANAGEMENT = "work_item_management"
    ARTIFACT_STORAGE = "artifact_storage"
    PULL_REQUEST = "pull_request"
    PIPELINE_EXECUTION = "pipeline_execution"
    NOTIFICATION = "notification"

class BasePlugin(ABC):
    """Base class for all AI-SDLC plugins."""

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
        """Initialize plugin with configuration."""
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        pass
```

### Work Item Management Interface

```python
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class WorkItem:
    """Universal work item representation."""
    id: str
    title: str
    description: str
    state: str
    assigned_to: Optional[str]
    created_date: datetime
    updated_date: datetime
    item_type: str  # Epic, Feature, Story, Task, Bug
    parent_id: Optional[str]
    tags: List[str]
    custom_fields: Dict[str, Any]
    url: str

@dataclass
class WorkItemUpdate:
    """Work item update request."""
    state: Optional[str] = None
    assigned_to: Optional[str] = None
    comment: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

class WorkItemPlugin(BasePlugin):
    """Plugin for work item management."""

    @abstractmethod
    def get_work_item(self, work_item_id: str) -> WorkItem:
        """Get work item by ID."""
        pass

    @abstractmethod
    def create_work_item(
        self,
        title: str,
        description: str,
        item_type: str,
        parent_id: Optional[str] = None,
        **kwargs
    ) -> WorkItem:
        """Create new work item."""
        pass

    @abstractmethod
    def update_work_item(
        self,
        work_item_id: str,
        update: WorkItemUpdate
    ) -> WorkItem:
        """Update work item."""
        pass

    @abstractmethod
    def add_comment(self, work_item_id: str, comment: str) -> bool:
        """Add comment to work item."""
        pass

    @abstractmethod
    def attach_file(
        self,
        work_item_id: str,
        file_path: str,
        comment: Optional[str] = None
    ) -> str:
        """Attach file to work item. Returns attachment URL."""
        pass

    @abstractmethod
    def get_children(self, work_item_id: str) -> List[WorkItem]:
        """Get child work items."""
        pass

    @abstractmethod
    def link_work_items(
        self,
        source_id: str,
        target_id: str,
        link_type: str
    ) -> bool:
        """Create link between work items."""
        pass
```

### Pull Request Interface

```python
@dataclass
class PullRequest:
    """Universal pull request representation."""
    id: str
    title: str
    description: str
    source_branch: str
    target_branch: str
    state: str  # open, merged, closed
    author: str
    created_date: datetime
    updated_date: datetime
    url: str
    work_item_ids: List[str]

class PullRequestPlugin(BasePlugin):
    """Plugin for pull request management."""

    @abstractmethod
    def create_pull_request(
        self,
        title: str,
        description: str,
        source_branch: str,
        target_branch: str,
        work_item_ids: Optional[List[str]] = None
    ) -> PullRequest:
        """Create pull request."""
        pass

    @abstractmethod
    def get_pull_request(self, pr_id: str) -> PullRequest:
        """Get pull request by ID."""
        pass

    @abstractmethod
    def add_comment(self, pr_id: str, comment: str) -> bool:
        """Add comment to pull request."""
        pass

    @abstractmethod
    def link_work_items(self, pr_id: str, work_item_ids: List[str]) -> bool:
        """Link work items to pull request."""
        pass

    @abstractmethod
    def get_changed_files(self, pr_id: str) -> List[str]:
        """Get list of changed files in pull request."""
        pass
```

### Artifact Storage Interface

```python
@dataclass
class Artifact:
    """Universal artifact representation."""
    name: str
    version: str
    url: str
    size_bytes: int
    created_date: datetime
    metadata: Dict[str, Any]

class ArtifactPlugin(BasePlugin):
    """Plugin for artifact storage."""

    @abstractmethod
    def upload_artifact(
        self,
        name: str,
        version: str,
        files: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Artifact:
        """Upload artifact package."""
        pass

    @abstractmethod
    def download_artifact(
        self,
        name: str,
        version: str,
        destination: str
    ) -> str:
        """Download artifact. Returns local path."""
        pass

    @abstractmethod
    def link_to_work_item(
        self,
        artifact: Artifact,
        work_item_id: str
    ) -> bool:
        """Link artifact to work item."""
        pass

    @abstractmethod
    def list_versions(self, artifact_name: str) -> List[str]:
        """List all versions of an artifact."""
        pass
```

### CI/CD Pipeline Interface

```python
@dataclass
class PipelineRun:
    """Universal pipeline run representation."""
    id: str
    pipeline_name: str
    status: str  # pending, running, succeeded, failed
    started_date: Optional[datetime]
    completed_date: Optional[datetime]
    url: str

class PipelinePlugin(BasePlugin):
    """Plugin for CI/CD pipeline execution."""

    @abstractmethod
    def trigger_pipeline(
        self,
        pipeline_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> PipelineRun:
        """Trigger pipeline execution."""
        pass

    @abstractmethod
    def get_pipeline_run(self, run_id: str) -> PipelineRun:
        """Get pipeline run status."""
        pass

    @abstractmethod
    def get_logs(self, run_id: str) -> str:
        """Get pipeline execution logs."""
        pass

    @abstractmethod
    def cancel_run(self, run_id: str) -> bool:
        """Cancel pipeline run."""
        pass
```

## Supported Tools

### Azure DevOps (ADO)

**Capabilities**:
- Work Item Management
- Pull Requests (Azure Repos)
- Artifact Storage (Azure Artifacts)
- Pipeline Execution (Azure Pipelines)

**Configuration**:
```yaml
plugins:
  agile:
    type: ado
    config:
      organization: symphonyvsts
      project: "Audit Cortex 2"
      pat_secret: ADO_PAT

  source_control:
    type: azure_repos
    config:
      organization: symphonyvsts
      project: "Audit Cortex 2"
      repository: cortexpy
      pat_secret: ADO_PAT

  artifacts:
    type: azure_artifacts
    config:
      organization: symphonyvsts
      project: "Audit Cortex 2"
      feed: audit-cortex-evidence
      pat_secret: ADO_PAT
```

### JIRA

**Capabilities**:
- Work Item Management (Issues, Epics, Stories)

**Configuration**:
```yaml
plugins:
  agile:
    type: jira
    config:
      url: https://yourcompany.atlassian.net
      project_key: PROJ
      api_token_secret: JIRA_API_TOKEN
      email: user@company.com
```

### GitHub

**Capabilities**:
- Pull Requests
- Artifact Storage (GitHub Packages)
- Pipeline Execution (GitHub Actions)
- Work Item Management (GitHub Issues/Projects)

**Configuration**:
```yaml
plugins:
  source_control:
    type: github
    config:
      owner: vivekgana
      repository: databricks-platform-marketplace
      token_secret: GITHUB_TOKEN

  artifacts:
    type: github_packages
    config:
      owner: vivekgana
      repository: databricks-platform-marketplace
      token_secret: GITHUB_TOKEN

  agile:
    type: github_issues
    config:
      owner: vivekgana
      repository: databricks-platform-marketplace
      token_secret: GITHUB_TOKEN
```

### GitLab

**Capabilities**:
- Work Item Management (Issues, Epics)
- Pull Requests (Merge Requests)
- Artifact Storage (GitLab Package Registry)
- Pipeline Execution (GitLab CI)

**Configuration**:
```yaml
plugins:
  agile:
    type: gitlab
    config:
      url: https://gitlab.com
      project_id: 12345
      token_secret: GITLAB_TOKEN

  source_control:
    type: gitlab
    config:
      url: https://gitlab.com
      project_id: 12345
      token_secret: GITLAB_TOKEN
```

## Configuration System

### Configuration File Structure

**Location**: `.aisdlc/config.yaml` in project root

```yaml
# AI-SDLC Configuration
version: "1.0"

# Active plugin configuration
active_plugins:
  agile: ado
  source_control: azure_repos
  artifacts: azure_artifacts
  ci_cd: azure_pipelines

# Plugin configurations
plugins:
  # Azure DevOps
  ado:
    type: ado
    enabled: true
    config:
      organization: ${ADO_ORGANIZATION}
      project: ${ADO_PROJECT}
      pat_secret: ADO_PAT
      api_version: "7.0"

  azure_repos:
    type: azure_repos
    enabled: true
    config:
      organization: ${ADO_ORGANIZATION}
      project: ${ADO_PROJECT}
      repository: ${REPO_NAME}
      pat_secret: ADO_PAT

  azure_artifacts:
    type: azure_artifacts
    enabled: true
    config:
      organization: ${ADO_ORGANIZATION}
      project: ${ADO_PROJECT}
      feed: ${ARTIFACTS_FEED}
      pat_secret: ADO_PAT

  azure_pipelines:
    type: azure_pipelines
    enabled: true
    config:
      organization: ${ADO_ORGANIZATION}
      project: ${ADO_PROJECT}
      pat_secret: ADO_PAT

  # JIRA
  jira:
    type: jira
    enabled: false
    config:
      url: ${JIRA_URL}
      project_key: ${JIRA_PROJECT_KEY}
      api_token_secret: JIRA_API_TOKEN
      email: ${JIRA_EMAIL}

  # GitHub
  github:
    type: github
    enabled: false
    config:
      owner: ${GITHUB_OWNER}
      repository: ${GITHUB_REPO}
      token_secret: GITHUB_TOKEN
      api_url: https://api.github.com

  github_packages:
    type: github_packages
    enabled: false
    config:
      owner: ${GITHUB_OWNER}
      repository: ${GITHUB_REPO}
      token_secret: GITHUB_TOKEN

  github_actions:
    type: github_actions
    enabled: false
    config:
      owner: ${GITHUB_OWNER}
      repository: ${GITHUB_REPO}
      token_secret: GITHUB_TOKEN

  # GitLab
  gitlab:
    type: gitlab
    enabled: false
    config:
      url: ${GITLAB_URL}
      project_id: ${GITLAB_PROJECT_ID}
      token_secret: GITLAB_TOKEN

# Secrets management
secrets:
  provider: databricks  # Options: databricks, azure_keyvault, aws_secrets, env
  config:
    scope: ai-sdlc-secrets

# Evidence storage
evidence:
  storage_type: plugin  # Use artifact plugin
  retention_days: 90
  compression: true

# Workflow defaults
workflow:
  default_branch: main
  auto_link_work_items: true
  require_pr_review: true
```

### Environment Variable Support

```bash
# .env file
ADO_ORGANIZATION=symphonyvsts
ADO_PROJECT="Audit Cortex 2"
ADO_PAT=<from-secret-manager>
REPO_NAME=cortexpy
ARTIFACTS_FEED=audit-cortex-evidence

JIRA_URL=https://company.atlassian.net
JIRA_PROJECT_KEY=PROJ
JIRA_EMAIL=user@company.com

GITHUB_OWNER=vivekgana
GITHUB_REPO=databricks-platform-marketplace

GITLAB_URL=https://gitlab.com
GITLAB_PROJECT_ID=12345
```

## Plugin Development

### Creating a New Plugin

1. **Implement Plugin Interface**:

```python
from ai_sdlc.plugins.base import WorkItemPlugin, WorkItem, WorkItemUpdate
from typing import List, Optional, Dict, Any

class LinearPlugin(WorkItemPlugin):
    """Linear.app integration plugin."""

    def get_name(self) -> str:
        return "linear"

    def get_type(self) -> PluginType:
        return PluginType.AGILE

    def get_capabilities(self) -> List[PluginCapability]:
        return [PluginCapability.WORK_ITEM_MANAGEMENT]

    def initialize(self, config: Dict[str, Any]) -> bool:
        self.api_key = config["api_key"]
        self.team_id = config["team_id"]
        # Initialize Linear API client
        return True

    def validate_config(self, config: Dict[str, Any]) -> bool:
        required = ["api_key", "team_id"]
        return all(k in config for k in required)

    def get_work_item(self, work_item_id: str) -> WorkItem:
        # Implement Linear API call
        issue = self._linear_client.get_issue(work_item_id)
        return self._convert_to_work_item(issue)

    # Implement remaining methods...
```

2. **Register Plugin**:

```python
# ai_sdlc/plugins/__init__.py
from .linear_plugin import LinearPlugin

AVAILABLE_PLUGINS = {
    "linear": LinearPlugin,
    # ... other plugins
}
```

3. **Add Configuration Schema**:

```yaml
# ai_sdlc/plugins/schemas/linear.yaml
linear:
  type: linear
  required_fields:
    - api_key
    - team_id
  optional_fields:
    - api_url
  capabilities:
    - work_item_management
```

### Plugin Testing

```python
import pytest
from ai_sdlc.plugins.linear_plugin import LinearPlugin

class TestLinearPlugin:
    """Test suite for Linear plugin."""

    @pytest.fixture
    def plugin(self):
        plugin = LinearPlugin()
        config = {
            "api_key": "test-key",
            "team_id": "test-team"
        }
        plugin.initialize(config)
        return plugin

    def test_get_work_item(self, plugin, mock_linear_api):
        work_item = plugin.get_work_item("PROJ-123")
        assert work_item.id == "PROJ-123"
        assert work_item.title is not None
```

## Migration Guide

### Migrating from Direct ADO Integration

**Before** (Direct dependency):
```python
from integrations.azure_devops.azure_devops_plugin import AzureDevOpsPlugin

ado = AzureDevOpsPlugin(organization="org", project="proj")
work_item = ado.get_work_item("12345")
```

**After** (Plugin system):
```python
from ai_sdlc.plugins import PluginManager

manager = PluginManager()
agile_plugin = manager.get_plugin("agile")
work_item = agile_plugin.get_work_item("12345")
```

### Agent Updates

**Before**:
```python
class MyAgent(BaseAgent):
    def execute(self, input_data):
        # Direct ADO calls
        from integrations.azure_devops import AzureDevOpsPlugin
        ado = AzureDevOpsPlugin(...)
        ado.update_work_item(...)
```

**After**:
```python
class MyAgent(BaseAgent):
    def execute(self, input_data):
        # Use plugin manager
        agile_plugin = self.plugin_manager.get_plugin("agile")
        agile_plugin.update_work_item(...)
```

### CLI Updates

**Before**:
```bash
python -m ai_sdlc.cli.workflow_commands run-workflow \
  --work-item-url "https://dev.azure.com/org/proj/_workitems/edit/12345"
```

**After** (works with any tool):
```bash
# Configure tool once
aisdlc config set agile.type jira
aisdlc config set agile.project_key PROJ

# Use generic work item ID
python -m ai_sdlc.cli.workflow_commands run-workflow \
  --work-item-id "PROJ-123"
```

## Examples

### Example 1: Multi-Tool Setup

Use JIRA for agile, GitHub for source control:

```yaml
active_plugins:
  agile: jira
  source_control: github
  artifacts: github_packages
  ci_cd: github_actions

plugins:
  jira:
    type: jira
    enabled: true
    config:
      url: https://company.atlassian.net
      project_key: PROJ
      api_token_secret: JIRA_API_TOKEN

  github:
    type: github
    enabled: true
    config:
      owner: company
      repository: project
      token_secret: GITHUB_TOKEN
```

**Usage**:
```python
# Get work item from JIRA
work_item = agile_plugin.get_work_item("PROJ-123")

# Create PR in GitHub
pr = source_control_plugin.create_pull_request(
    title=f"[{work_item.id}] {work_item.title}",
    description=work_item.description,
    source_branch="feature/proj-123",
    target_branch="main",
    work_item_ids=[work_item.id]
)
```

### Example 2: Switching Tools

Switch from ADO to GitLab:

```bash
# Update configuration
aisdlc config set active_plugins.agile gitlab
aisdlc config set active_plugins.source_control gitlab
aisdlc config set active_plugins.ci_cd gitlab

# Set GitLab credentials
aisdlc config set plugins.gitlab.config.url https://gitlab.com
aisdlc config set plugins.gitlab.config.project_id 12345
aisdlc secret set GITLAB_TOKEN <token>

# No code changes needed - workflows continue to work
python -m ai_sdlc.cli.workflow_commands run-workflow --work-item-id "123"
```

### Example 3: Plugin in Agent

```python
from ai_sdlc.agents.base_agent import BaseAgent
from ai_sdlc.plugins import PluginManager

class MyCustomAgent(BaseAgent):
    def __init__(self, work_item_id: str, config: Dict[str, Any]):
        super().__init__(work_item_id, config)
        self.plugin_manager = PluginManager()

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Get agile plugin (could be ADO, JIRA, etc.)
        agile = self.plugin_manager.get_plugin("agile")

        # Get work item (works regardless of tool)
        work_item = agile.get_work_item(self.work_item_id)

        # Do work...

        # Update work item
        agile.add_comment(
            self.work_item_id,
            f"Completed processing: {result}"
        )

        # Upload evidence
        artifacts = self.plugin_manager.get_plugin("artifacts")
        if artifacts:
            artifact = artifacts.upload_artifact(
                name=f"evidence-{self.work_item_id}",
                version="1.0.0",
                files=evidence_files
            )
            artifacts.link_to_work_item(artifact, self.work_item_id)

        return result
```

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-18 | AI-SDLC Team | Initial version - plugin architecture design |
