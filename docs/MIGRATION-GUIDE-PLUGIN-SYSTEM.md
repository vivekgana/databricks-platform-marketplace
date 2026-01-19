# Migration Guide: Moving to the Plugin System

**Document Version:** 1.0
**Last Updated:** January 18, 2026 12:27 AM
**Prepared by:** AI-SDLC Development Team

## Table of Contents

1. [Overview](#overview)
2. [Why Migrate?](#why-migrate)
3. [Breaking Changes](#breaking-changes)
4. [Migration Steps](#migration-steps)
5. [Code Migration Examples](#code-migration-examples)
6. [Configuration Setup](#configuration-setup)
7. [Testing After Migration](#testing-after-migration)
8. [Troubleshooting](#troubleshooting)
9. [Rollback Plan](#rollback-plan)

---

## Overview

The AI-SDLC system has been redesigned to use a **plugin-based architecture** that makes it completely tool-agnostic. This migration guide helps you transition from the hard-coded Azure DevOps integration to the flexible plugin system.

### What's Changed?

**Before (Hard-coded ADO):**
```python
from plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import AzureDevOpsPlugin

ado_plugin = AzureDevOpsPlugin(organization="myorg", project="myproject", personal_access_token="token")
work_item = ado_plugin.get_work_item("12345", config)
```

**After (Plugin System):**
```python
from ai_sdlc.plugins.manager import PluginManager

plugin_manager = PluginManager()  # Singleton, reads from .aisdlc/config.yaml
agile_plugin = plugin_manager.get_agile_plugin()  # Could be ADO, JIRA, GitHub, or GitLab
work_item = agile_plugin.get_work_item("12345")
```

---

## Why Migrate?

### Benefits of the Plugin System

1. **Tool Flexibility**: Switch from ADO to JIRA or GitHub Issues with just configuration changes
2. **Multi-Tool Support**: Use JIRA for planning + GitHub for code in the same project
3. **Cloud Agnostic**: Works with AWS, Azure, and GCP
4. **Easier Testing**: Mock plugins instead of actual tool integrations
5. **Future-Proof**: Add new tool integrations without changing core code
6. **Standardized API**: All tools use the same interface

---

## Breaking Changes

### 1. Import Paths Changed

| Old Import | New Import |
|------------|------------|
| `from plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import AzureDevOpsPlugin` | `from ai_sdlc.plugins.manager import PluginManager`<br>`from ai_sdlc.plugins.base import WorkItemPlugin` |
| `from plugins.databricks_devops_integrations.sdk.base_plugin import WorkItem` | `from ai_sdlc.plugins.models import WorkItem` |

### 2. Plugin Initialization Changed

**Old Way:**
```python
ado_plugin = AzureDevOpsPlugin(
    organization="myorg",
    project="myproject",
    personal_access_token="token"
)
```

**New Way:**
```python
# Configuration is in .aisdlc/config.yaml
plugin_manager = PluginManager()
agile_plugin = plugin_manager.get_agile_plugin()
```

### 3. WorkflowOrchestrator Signature Changed

**Old:**
```python
orchestrator = WorkflowOrchestrator(
    ado_plugin=ado_plugin,
    config=plugin_config,
    evidence_base_path="path/to/evidence"
)
```

**New:**
```python
orchestrator = WorkflowOrchestrator(
    config=config_dict,  # Plain dict, not PluginConfig
    evidence_base_path="path/to/evidence"
)
```

### 4. State Reader Signature Changed

**Old:**
```python
state_reader = StateReader(ado_plugin, config)
```

**New:**
```python
plugin_manager = PluginManager()
agile_plugin = plugin_manager.get_agile_plugin()
state_reader = StateReader(agile_plugin, config)
```

### 5. Work Item Model Changed

**Old** (ADO-specific):
```python
work_item.status.value  # Enum
work_item.work_item_type.value  # Enum
```

**New** (Universal):
```python
work_item.state  # String
work_item.item_type  # String
work_item.tool_name  # "ado", "jira", "github", etc.
```

---

## Migration Steps

### Step 1: Install Plugin Dependencies

Depending on which tools you'll use, install the required libraries:

```bash
# For Azure DevOps (you probably already have this)
pip install azure-devops

# For JIRA
pip install jira

# For GitHub
pip install PyGithub

# For GitLab
pip install python-gitlab

# For AWS
pip install boto3

# For Azure Cloud Services
pip install azure-storage-blob azure-keyvault-secrets

# For Google Cloud Platform
pip install google-cloud-storage google-cloud-secret-manager
```

### Step 2: Create Configuration Directory

```bash
mkdir -p .aisdlc
cd .aisdlc
```

### Step 3: Choose and Copy Configuration Template

Based on your tool stack, copy the appropriate template:

**Option A: Azure DevOps + Azure Cloud (most common for existing users)**
```bash
cp .aisdlc/config.example-ado-azure.yaml .aisdlc/config.yaml
```

**Option B: JIRA + GitHub + AWS**
```bash
cp .aisdlc/config.example-jira-github-aws.yaml .aisdlc/config.yaml
```

**Option C: GitLab + GCP**
```bash
cp .aisdlc/config.example-gitlab-gcp.yaml .aisdlc/config.yaml
```

**Option D: Multi-Tool Setup (JIRA + GitHub + Azure)**
```bash
cp .aisdlc/config.example-multi-tool.yaml .aisdlc/config.yaml
```

### Step 4: Set Up Environment Variables

```bash
# Copy environment template
cp .aisdlc/.env.example .aisdlc/.env

# Edit .aisdlc/.env with your actual credentials
# NEVER commit .env to version control!
```

### Step 5: Update .gitignore

Add these lines to your `.gitignore`:

```
# AI-SDLC secrets
.aisdlc/.env
.aisdlc/config.yaml  # Optional: if you have secrets in config

# Keep templates in git
!.aisdlc/config.example-*.yaml
!.aisdlc/.env.example
```

### Step 6: Update Your Code

Follow the [Code Migration Examples](#code-migration-examples) section below to update your code.

### Step 7: Test the Configuration

```bash
# Test that plugins load correctly
python -c "from ai_sdlc.plugins.manager import PluginManager; pm = PluginManager(); print('Agile plugin:', pm.get_agile_plugin()); print('Storage plugin:', pm.get_cloud_storage_plugin())"
```

Expected output:
```
Agile plugin: <ADOAdapter object at 0x...>
Storage plugin: <AzureAdapter object at 0x...>
```

### Step 8: Run Integration Tests

```bash
# Run tests to verify everything works
pytest tests/integration/test_plugin_system.py -v
```

---

## Code Migration Examples

### Example 1: Migrating WorkflowOrchestrator Usage

**Before (Old Code):**
```python
from plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import AzureDevOpsPlugin
from plugins.databricks_devops_integrations.sdk.base_plugin import PluginConfig

# Initialize ADO plugin
ado_plugin = AzureDevOpsPlugin(
    organization="myorg",
    project="MyProject",
    personal_access_token="my-pat-token"
)

config = PluginConfig(
    organization="myorg",
    project="MyProject",
    personal_access_token="my-pat-token"
)

# Create orchestrator
from ai_sdlc.orchestration.workflow_orchestrator import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator(
    ado_plugin=ado_plugin,
    config=config,
    evidence_base_path="dbfs:/tmp/audit-cortex/evidence"
)

# Run workflow
result = orchestrator.run_workflow(work_item_id="6340168")
```

**After (Plugin System):**
```python
from ai_sdlc.orchestration.workflow_orchestrator import WorkflowOrchestrator

# Configuration is loaded from .aisdlc/config.yaml automatically
config = {
    "evidence_base_path": "azure://audit-cortex-evidence",
    # Any additional config needed by agents
}

# Create orchestrator (plugin manager initialized internally)
orchestrator = WorkflowOrchestrator(
    config=config,
    evidence_base_path="azure://audit-cortex-evidence"
)

# Run workflow (plugin system handles tool selection automatically)
result = orchestrator.run_workflow(work_item_id="6340168")
```

### Example 2: Migrating Work Item Operations

**Before (Old Code):**
```python
from plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import AzureDevOpsPlugin

ado_plugin = AzureDevOpsPlugin(organization="myorg", project="MyProject", personal_access_token="token")

# Get work item
work_item = ado_plugin.get_work_item("12345", config)
print(f"Title: {work_item.title}")
print(f"Status: {work_item.status.value}")
print(f"Type: {work_item.work_item_type.value}")

# Update work item
ado_plugin.update_work_item(
    work_item_id="12345",
    config=config,
    state="In Development",
    title="Updated Title"
)

# Add comment
ado_plugin.add_comment(work_item_id="12345", config=config, comment="Great progress!")
```

**After (Plugin System):**
```python
from ai_sdlc.plugins.manager import PluginManager
from ai_sdlc.plugins.models import WorkItemUpdate

# Get plugin (automatically uses configured tool)
plugin_manager = PluginManager()
agile_plugin = plugin_manager.get_agile_plugin()

# Get work item
work_item = agile_plugin.get_work_item("12345")
print(f"Title: {work_item.title}")
print(f"Status: {work_item.state}")  # String, not enum
print(f"Type: {work_item.item_type}")
print(f"Tool: {work_item.tool_name}")  # "ado", "jira", "github", etc.

# Update work item
update = WorkItemUpdate(
    state="In Development",
    title="Updated Title"
)
updated_item = agile_plugin.update_work_item("12345", update)

# Add comment
comment = agile_plugin.add_comment(work_item_id="12345", comment="Great progress!")
```

### Example 3: Migrating BaseAgent Usage

**Before (Old Code):**
```python
from ai_sdlc.agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, work_item_id, config, evidence_path):
        super().__init__(work_item_id, config, evidence_path)
        # No plugin manager available

    def execute(self, input_data, timeout_seconds=None):
        # Would need to receive ado_plugin via input_data
        ado_plugin = input_data.get("ado_plugin")
        work_item = ado_plugin.get_work_item(self.work_item_id, self.config)
        ...
```

**After (Plugin System):**
```python
from ai_sdlc.agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, work_item_id, config, evidence_path):
        super().__init__(work_item_id, config, evidence_path)
        # Plugin manager automatically available via self.plugin_manager

    def execute(self, input_data, timeout_seconds=None):
        # Get agile plugin
        agile_plugin = self.get_agile_plugin()

        # Get work item
        work_item = agile_plugin.get_work_item(self.work_item_id)

        # Get cloud storage plugin if needed
        storage_plugin = self.get_cloud_storage_plugin()
        storage_plugin.upload_file("local.txt", "evidence/file.txt")

        # Get secrets plugin if needed
        secrets_plugin = self.get_secrets_plugin()
        api_key = secrets_plugin.get_secret("MY_API_KEY")

        ...
```

### Example 4: Migrating CLI Commands

**Before (Old Code):**
```python
# ai_sdlc/cli/workflow_commands.py
import sys
from plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import AzureDevOpsPlugin

def run_workflow_command(work_item_id: str):
    # Hard-coded ADO plugin
    ado_plugin = AzureDevOpsPlugin(
        organization=os.environ["ADO_ORGANIZATION"],
        project=os.environ["ADO_PROJECT"],
        personal_access_token=os.environ["ADO_PAT"]
    )

    orchestrator = WorkflowOrchestrator(ado_plugin=ado_plugin, ...)
    result = orchestrator.run_workflow(work_item_id)
```

**After (Plugin System):**
```python
# ai_sdlc/cli/workflow_commands.py
from ai_sdlc.plugins.manager import PluginManager

def run_workflow_command(work_item_id: str):
    # Plugin manager uses configuration
    plugin_manager = PluginManager()

    # Verify plugins are configured
    if not plugin_manager.get_agile_plugin():
        print("Error: No agile plugin configured. Check .aisdlc/config.yaml")
        sys.exit(1)

    orchestrator = WorkflowOrchestrator(config={}, ...)
    result = orchestrator.run_workflow(work_item_id)
```

---

## Configuration Setup

### Understanding config.yaml

The `.aisdlc/config.yaml` file has three main sections:

#### 1. Active Plugins

Tells the system which plugins to use for each category:

```yaml
active_plugins:
  agile: ado              # Which tool for work item management
  source_control: github  # Which tool for PRs
  cloud_storage: azure    # Which cloud for evidence storage
  secrets: azure          # Which secrets manager
```

#### 2. Plugin Configurations

Provides credentials and settings for each plugin:

```yaml
plugins:
  ado:
    enabled: true
    type: ado
    config:
      organization: ${ADO_ORGANIZATION}
      project: ${ADO_PROJECT}
      pat: ${ADO_PAT}
```

#### 3. Workflow Settings

Global workflow configuration:

```yaml
workflow:
  evidence_base_path: "azure://audit-cortex-evidence"
  checkpoint_dir: "./.workflow_checkpoints"
  default_timeout_seconds: 1800
```

### Environment Variable Resolution

Use `${VARIABLE_NAME}` syntax in config.yaml to reference environment variables from `.env`:

```yaml
# config.yaml
config:
  pat: ${ADO_PAT}
```

```bash
# .env
ADO_PAT=my-secret-token
```

The plugin manager automatically resolves these references at runtime.

---

## Testing After Migration

### 1. Unit Tests

Ensure all unit tests pass:

```bash
pytest tests/unit/test_plugin_system.py -v
```

### 2. Integration Tests

Test with real tool integrations:

```bash
# Test ADO adapter
pytest tests/integration/test_ado_adapter.py -v

# Test GitHub adapter
pytest tests/integration/test_github_adapter.py -v
```

### 3. End-to-End Test

Run a complete workflow on a test work item:

```bash
python -m ai_sdlc.cli.workflow_commands run-workflow \
  --work-item-id TEST-123 \
  --evidence-path /tmp/test-evidence
```

### 4. Verify Evidence Storage

Check that evidence is stored correctly in your cloud storage:

```bash
# For Azure Blob Storage
az storage blob list --container-name audit-cortex-evidence --account-name youraccount

# For AWS S3
aws s3 ls s3://your-evidence-bucket/

# For Google Cloud Storage
gsutil ls gs://your-evidence-bucket/
```

---

## Troubleshooting

### Problem 1: "No agile plugin configured" Error

**Symptom:**
```
RuntimeError: No agile/work item plugin configured. Check .aisdlc/config.yaml
```

**Solution:**
1. Verify `.aisdlc/config.yaml` exists
2. Check that `active_plugins.agile` is set
3. Verify the referenced plugin is enabled:
   ```yaml
   plugins:
     ado:
       enabled: true  # Must be true
   ```
4. Check environment variables are set in `.aisdlc/.env`

### Problem 2: Plugin Not Loading

**Symptom:**
```
Plugin 'ado' failed to initialize
```

**Solution:**
1. Check credentials are correct in `.env`
2. Test credentials manually:
   ```python
   from ai_sdlc.plugins.adapters.ado_adapter import ADOAdapter
   adapter = ADOAdapter()
   success = adapter.initialize({
       "organization": "myorg",
       "project": "MyProject",
       "pat": "my-token"
   })
   print(f"Initialized: {success}")
   ```
3. Check library is installed: `pip list | grep azure-devops`

### Problem 3: Import Errors

**Symptom:**
```
ImportError: cannot import name 'AzureDevOpsPlugin'
```

**Solution:**
Update imports to use plugin system:
```python
# Old
from plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import AzureDevOpsPlugin

# New
from ai_sdlc.plugins.manager import PluginManager
from ai_sdlc.plugins.base import WorkItemPlugin
```

### Problem 4: Work Item Model Attribute Errors

**Symptom:**
```
AttributeError: 'WorkItem' object has no attribute 'status'
```

**Solution:**
The universal WorkItem model uses different attribute names:

```python
# Old (ADO-specific)
work_item.status.value        # Enum
work_item.work_item_type.value  # Enum

# New (Universal)
work_item.state              # String
work_item.item_type          # String
```

### Problem 5: Configuration Not Found

**Symptom:**
```
FileNotFoundError: .aisdlc/config.yaml not found
```

**Solution:**
1. Create config directory: `mkdir -p .aisdlc`
2. Copy template: `cp .aisdlc/config.example-ado-azure.yaml .aisdlc/config.yaml`
3. Or specify config path:
   ```python
   from ai_sdlc.plugins.config import ConfigManager
   config_manager = ConfigManager(config_path="/path/to/config.yaml")
   ```

---

## Rollback Plan

If you encounter critical issues and need to rollback:

### Quick Rollback (Keep Plugin System, Use ADO Directly)

You can temporarily bypass the plugin system:

```python
# Import ADO plugin directly
from ai_sdlc.plugins.adapters.ado_adapter import ADOAdapter

# Initialize manually
ado_adapter = ADOAdapter()
ado_adapter.initialize({
    "organization": "myorg",
    "project": "MyProject",
    "pat": "my-token"
})

# Use directly
work_item = ado_adapter.get_work_item("12345")
```

### Full Rollback (Revert to Old Code)

If you need to completely revert:

```bash
# Revert to commit before plugin system
git revert <commit-hash-before-plugin-system>

# Or checkout old branch
git checkout -b rollback-temp old-branch-name
```

---

## Need Help?

- **Documentation**: See `docs/PLUGIN-ARCHITECTURE.md` for architecture details
- **Examples**: Check `.aisdlc/config.example-*.yaml` for configuration examples
- **Issues**: Report problems at: https://github.com/yourorg/ai-sdlc/issues

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-18 | AI-SDLC Team | Initial migration guide created |
