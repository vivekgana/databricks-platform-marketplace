# AI-SDLC Plugin System - Implementation Guide

**Document Version:** 1.0
**Prepared by:** AI-SDLC Development Team
**Last Updated:** January 18, 2026 12:15 AM
**Contact:** AI-SDLC Support Team

## Implementation Summary

The AI-SDLC system has been redesigned with a plugin architecture that makes it completely agnostic to:
- Agile/project management tools (ADO, JIRA, GitHub Issues, GitLab Issues, Linear, Asana)
- Source control systems (GitHub, GitLab, Bitbucket, Azure Repos)
- CI/CD platforms (Azure Pipelines, GitHub Actions, GitLab CI, Jenkins, CircleCI)
- Cloud providers (AWS, Azure, GCP - for storage, secrets, etc.)
- Artifact registries (Azure Artifacts, GitHub Packages, GitLab Registry, AWS ECR, JFrog Artifactory)

## Implementation Status

### ✅ Completed

1. **Architecture Design** ([docs/PLUGIN-ARCHITECTURE.md](PLUGIN-ARCHITECTURE.md))
   - Comprehensive plugin architecture
   - Interface definitions
   - Configuration system design
   - Multi-tool and multi-cloud support

2. **Core Plugin System**:
   - `ai_sdlc/plugins/models.py` - Universal data models
   - `ai_sdlc/plugins/base.py` - Base plugin interfaces
   - `ai_sdlc/plugins/config.py` - Configuration management
   - `ai_sdlc/plugins/manager.py` - Plugin lifecycle management

3. **Plugin Interfaces**:
   - `WorkItemPlugin` - Agile/issue management
   - `PullRequestPlugin` - Source control
   - `ArtifactPlugin` - Artifact storage
   - `PipelinePlugin` - CI/CD execution
   - `CloudStoragePlugin` - Cloud file storage
   - `SecretsPlugin` - Secrets management

### 🚧 To Be Implemented

1. **Plugin Adapters**:
   - `ai_sdlc/plugins/adapters/ado_adapter.py` - Azure DevOps
   - `ai_sdlc/plugins/adapters/jira_adapter.py` - JIRA
   - `ai_sdlc/plugins/adapters/github_adapter.py` - GitHub
   - `ai_sdlc/plugins/adapters/gitlab_adapter.py` - GitLab
   - `ai_sdlc/plugins/adapters/aws_adapter.py` - AWS (S3, Secrets Manager)
   - `ai_sdlc/plugins/adapters/azure_adapter.py` - Azure (Blob, Key Vault)
   - `ai_sdlc/plugins/adapters/gcp_adapter.py` - GCP (Cloud Storage, Secret Manager)

2. **Core System Updates**:
   - Update `BaseAgent` to use `PluginManager`
   - Update all agents to use plugin system
   - Update generators to use plugin system
   - Update CLI commands to use plugin system
   - Update workflow orchestration to use plugin system

3. **Configuration**:
   - Default configuration templates for all tools
   - Configuration validation and migration tools
   - CLI commands for configuration management

4. **Testing**:
   - Unit tests for all adapters
   - Integration tests with mock plugins
   - End-to-end tests with multiple tool combinations

5. **Documentation**:
   - Adapter implementation guides
   - Migration guide from existing code
   - Tool-specific setup guides

## Quick Start for Plugin Development

### Step 1: Implement an Adapter

Example: ADO Adapter wrapping existing integration

```python
# ai_sdlc/plugins/adapters/ado_adapter.py
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add plugins directory to path for imports
sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent.parent / "plugins" / "databricks-devops-integrations")
)

from integrations.azure_devops.azure_devops_plugin import AzureDevOpsPlugin
from ai_sdlc.plugins.base import WorkItemPlugin, PullRequestPlugin, ArtifactPlugin, PluginType, PluginCapability
from ai_sdlc.plugins.models import WorkItem, WorkItemUpdate, PullRequest, Artifact

class ADOAdapter(WorkItemPlugin, PullRequestPlugin, ArtifactPlugin):
    """Azure DevOps plugin adapter."""

    def __init__(self):
        super().__init__()
        self.ado_plugin = None

    def get_name(self) -> str:
        return "ado"

    def get_type(self) -> PluginType:
        return PluginType.AGILE

    def get_capabilities(self) -> List[PluginCapability]:
        return [
            PluginCapability.WORK_ITEM_MANAGEMENT,
            PluginCapability.PULL_REQUEST,
            PluginCapability.ARTIFACT_STORAGE,
        ]

    def validate_config(self, config: Dict[str, Any]) -> bool:
        required = ["organization", "project", "pat"]
        return all(k in config for k in required)

    def initialize(self, config: Dict[str, Any]) -> bool:
        try:
            self.ado_plugin = AzureDevOpsPlugin(
                organization=config["organization"],
                project=config["project"],
                pat=config["pat"],
            )
            self.config = config
            self.initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize ADO plugin: {e}")
            return False

    def get_work_item(self, work_item_id: str) -> WorkItem:
        """Get work item from ADO."""
        ado_item = self.ado_plugin.get_work_item(work_item_id)

        return WorkItem(
            id=str(ado_item["id"]),
            title=ado_item["fields"]["System.Title"],
            description=ado_item["fields"].get("System.Description", ""),
            state=ado_item["fields"]["System.State"],
            assigned_to=ado_item["fields"].get("System.AssignedTo", {}).get("displayName"),
            created_date=self._parse_date(ado_item["fields"]["System.CreatedDate"]),
            updated_date=self._parse_date(ado_item["fields"]["System.ChangedDate"]),
            item_type=ado_item["fields"]["System.WorkItemType"],
            parent_id=str(ado_item["fields"].get("System.Parent")) if "System.Parent" in ado_item["fields"] else None,
            tags=ado_item["fields"].get("System.Tags", "").split("; ") if ado_item["fields"].get("System.Tags") else [],
            custom_fields={k: v for k, v in ado_item["fields"].items() if k.startswith("Custom.")},
            url=ado_item["_links"]["html"]["href"],
            tool_name="ado",
        )

    # Implement remaining methods...
```

### Step 2: Register in Plugin Manager

Already done in `manager.py` - adapters are auto-discovered.

### Step 3: Configure

Create `.aisdlc/config.yaml`:

```yaml
version: "1.0"

active_plugins:
  agile: ado
  source_control: azure_repos
  artifacts: azure_artifacts

plugins:
  ado:
    type: ado
    enabled: true
    config:
      organization: symphonyvsts
      project: "Audit Cortex 2"
      pat_secret: ADO_PAT  # References secret named ADO_PAT

secrets:
  provider: databricks
  config:
    scope: ai-sdlc-secrets
```

### Step 4: Use in Agents

```python
from ai_sdlc.plugins import PluginManager

class MyAgent(BaseAgent):
    def execute(self, input_data):
        # Get plugin manager
        manager = PluginManager()

        # Get agile plugin (tool-agnostic!)
        agile = manager.get_agile_plugin()

        # Use standard interface
        work_item = agile.get_work_item(self.work_item_id)
        print(f"Working on: {work_item.title}")

        # Do work...

        # Update work item (works with any tool!)
        agile.add_comment(
            self.work_item_id,
            f"Completed processing with {len(results)} results"
        )
```

## Implementation Priority

### Phase 1: Core Adapters (Week 1)
1. ADO Adapter (wraps existing integration)
2. Configuration system integration
3. Update BaseAgent to support plugin manager
4. Update one agent (e.g., EvidenceCollectorAgent) as proof of concept

### Phase 2: Additional Adapters (Week 2)
1. JIRA Adapter
2. GitHub Adapter
3. GitLab Adapter
4. Update remaining agents

### Phase 3: Cloud Providers (Week 3)
1. AWS Adapter (S3, Secrets Manager)
2. Azure Adapter (Blob Storage, Key Vault)
3. GCP Adapter (Cloud Storage, Secret Manager)

### Phase 4: Testing & Documentation (Week 4)
1. Comprehensive unit tests
2. Integration tests
3. Migration guide
4. Tool-specific documentation

## Configuration Examples

### ADO + Azure

```yaml
active_plugins:
  agile: ado
  source_control: azure_repos
  artifacts: azure_artifacts
  cloud_storage: azure
  secrets: azure

plugins:
  ado:
    type: ado
    config:
      organization: ${ADO_ORG}
      project: ${ADO_PROJECT}
      pat_secret: ADO_PAT

  azure:
    type: azure
    config:
      storage_account: ${AZURE_STORAGE_ACCOUNT}
      container: evidence
      key_vault_url: ${AZURE_KEYVAULT_URL}
```

### JIRA + GitHub + AWS

```yaml
active_plugins:
  agile: jira
  source_control: github
  artifacts: github_packages
  cloud_storage: aws
  secrets: aws

plugins:
  jira:
    type: jira
    config:
      url: https://company.atlassian.net
      project_key: PROJ
      api_token_secret: JIRA_API_TOKEN
      email: ${JIRA_EMAIL}

  github:
    type: github
    config:
      owner: vivekgana
      repository: databricks-platform-marketplace
      token_secret: GITHUB_TOKEN

  aws:
    type: aws
    config:
      region: us-east-1
      s3_bucket: ai-sdlc-evidence
      secrets_region: us-east-1
```

### GitLab + GCP

```yaml
active_plugins:
  agile: gitlab
  source_control: gitlab
  artifacts: gitlab
  cloud_storage: gcp
  secrets: gcp

plugins:
  gitlab:
    type: gitlab
    config:
      url: https://gitlab.com
      project_id: 12345
      token_secret: GITLAB_TOKEN

  gcp:
    type: gcp
    config:
      project_id: my-project
      bucket: ai-sdlc-evidence
      secret_project_id: my-project
```

## Migration Path

### For Existing Code

1. **Agents**: Add plugin manager initialization
   ```python
   # Before
   from integrations.azure_devops import AzureDevOpsPlugin
   ado = AzureDevOpsPlugin(...)

   # After
   from ai_sdlc.plugins import PluginManager
   manager = PluginManager()
   agile = manager.get_agile_plugin()
   ```

2. **CLI**: Use tool-agnostic work item IDs
   ```bash
   # Before: Tool-specific URL
   --work-item-url "https://dev.azure.com/org/proj/_workitems/edit/12345"

   # After: Generic ID (tool determined by config)
   --work-item-id "12345"  # For ADO
   --work-item-id "PROJ-123"  # For JIRA
   --work-item-id "123"  # For GitHub/GitLab
   ```

3. **Configuration**: One-time setup
   ```bash
   # Initialize configuration
   aisdlc init --tool ado

   # Or manually create .aisdlc/config.yaml
   ```

## Benefits

1. **Tool Agnostic**: Switch tools without code changes
2. **Multi-Tool**: Use JIRA for agile, GitHub for source control
3. **Multi-Cloud**: Use AWS S3 for storage, Azure Key Vault for secrets
4. **Testable**: Mock plugins for testing
5. **Extensible**: Easy to add new tools
6. **Backward Compatible**: Existing integrations wrapped as plugins

## Next Steps

1. Implement ADO adapter (highest priority)
2. Update BaseAgent to use plugin manager
3. Update one agent end-to-end
4. Create configuration templates
5. Create CLI commands for config management
6. Implement remaining adapters
7. Comprehensive testing
8. Documentation and migration guides

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-18 | AI-SDLC Team | Initial implementation guide |
