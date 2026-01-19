# Persistent Artifacts in Azure DevOps Guide

**Document Version:** 1.0
**Last Updated:** 2026-01-17 22:43:33
**Prepared by:** AI-SDLC Platform Team

---

## Table of Contents

1. [Overview](#overview)
2. [Persistent Artifacts vs Attachments](#persistent-artifacts-vs-attachments)
3. [Azure Artifacts Universal Packages](#azure-artifacts-universal-packages)
4. [Implementation Architecture](#implementation-architecture)
5. [Usage Guide](#usage-guide)
6. [CLI Commands](#cli-commands)
7. [API Reference](#api-reference)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Examples](#examples)

---

## Overview

The AI-SDLC platform now supports **persistent artifacts** in Azure DevOps through Azure Artifacts Universal Packages. This feature enables versioned, permanent storage of evidence packages that can be:

- Versioned (semantic versioning: 1.0.0, 1.1.0, 2.0.0)
- Shared across multiple work items
- Downloaded and restored independently
- Managed with retention policies
- Tracked with full audit trail

### Key Benefits

✅ **Versioning** - Multiple versions of evidence packages (e.g., v1.0.0, v2.0.0)
✅ **Permanence** - Artifacts persist independently of work items
✅ **Reusability** - Link same artifact to multiple work items
✅ **Size** - No file size limits (unlike attachments which have 60MB limit)
✅ **Organization** - Structured storage with manifest.json metadata
✅ **Audit Trail** - Full history of artifact versions and changes

---

## Persistent Artifacts vs Attachments

| Feature | Attachments | Persistent Artifacts |
|---------|------------|---------------------|
| **Storage Location** | Work Item | Azure Artifacts Feed |
| **Versioning** | No | Yes (semantic versioning) |
| **Size Limit** | 60MB per file | Unlimited |
| **Reusability** | One work item only | Multiple work items |
| **Lifecycle** | Tied to work item | Independent |
| **Download** | Manual from ADO UI | API + CLI download |
| **Organization** | Flat list | Package structure with manifest |
| **Search** | Basic | Advanced (by name, version, metadata) |
| **Best For** | Quick screenshots, small files | Complete evidence packages, code artifacts |

### When to Use Which

**Use Attachments When:**
- Quick upload of 1-3 key files (screenshots, reports)
- Files needed for immediate review in ADO UI
- Small files (< 10MB each)
- Files specific to one work item

**Use Persistent Artifacts When:**
- Complete evidence packages with many files
- Need versioning (v1.0.0 → v2.0.0)
- Large file collections (> 60MB total)
- Evidence needs to be shared across work items
- Need programmatic download/restore capability
- Compliance requires permanent audit trail

---

## Azure Artifacts Universal Packages

### What Are Universal Packages?

Universal Packages are a package format in Azure Artifacts that allows storing any set of files as a versioned package. They use:

- **Package Name**: Unique identifier (e.g., "pbi-6340168-evidence")
- **Version**: Semantic versioning (e.g., "1.0.0", "2.1.3")
- **Feed**: Collection/repository for packages (e.g., "ai-sdlc-evidence")
- **Manifest**: JSON metadata describing package contents

### Package Structure

```
pbi-6340168-evidence:1.0.0
├── manifest.json (metadata)
├── planning/
│   ├── implementation-plan.md
│   └── requirements-analysis.json
├── code_generation/
│   ├── audit_service.py
│   ├── test_audit_service.py
│   └── code-quality-report.json
├── unit_testing/
│   ├── pytest-report.html
│   ├── coverage.json
│   └── coverage-report.html
├── qa_testing/
│   ├── screenshot-1.png
│   ├── screenshot-2.png
│   └── playwright-report.html
└── ... (other stages)
```

### Manifest Format

```json
{
  "work_item_id": "6340168",
  "created_at": "2026-01-17T22:30:00",
  "artifact_name": "pbi-6340168-evidence",
  "version": "1.0.0",
  "total_files": 23,
  "files": [
    {
      "filename": "implementation-plan.md",
      "category": "plan",
      "stage": "planning",
      "size_bytes": 4562
    },
    {
      "filename": "audit_service.py",
      "category": "code",
      "stage": "code_generation",
      "size_bytes": 15234
    }
    // ... more files
  ]
}
```

---

## Implementation Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│          Evidence Collector Agent                        │
│  - Collects evidence from all workflow stages            │
│  - Creates manifest.json                                 │
│  - Calls ADO plugin to create artifact                   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│       Azure DevOps Plugin (artifact methods)             │
│  - create_artifact_package()                             │
│  - link_existing_artifact()                              │
│  - get_work_item_artifacts()                             │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│     Azure Artifacts Universal Package API                │
│  - Upload package (tar.gz)                               │
│  - Create version                                         │
│  - Link to work item                                     │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│        Azure DevOps Work Item                            │
│  - ArtifactLink relation added                           │
│  - Link visible in ADO UI                                │
└─────────────────────────────────────────────────────────┘
```

### Key Classes and Methods

**Evidence Collector Agent** (`ai_sdlc/agents/evidence_collector_agent.py`)

```python
class EvidenceCollectorAgent(BaseAgent):
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Collect evidence from all stages
        # Optionally create persistent artifact
        if input_data.get("create_persistent_artifact"):
            artifact_info = self._create_persistent_artifact(...)

    def _create_persistent_artifact(
        self, all_evidence, previous_stages, input_data
    ) -> Optional[Dict[str, Any]]:
        # Creates artifact package via ADO plugin
        pass
```

**Azure DevOps Plugin** (`plugins/.../azure_devops_plugin.py`)

```python
class AzureDevOpsPlugin:
    def create_artifact_package(
        self, work_item_id, artifact_name, artifact_version, evidence_items, config
    ) -> Dict[str, Any]:
        # Creates tar.gz package
        # Uploads to Azure Artifacts
        # Links to work item
        pass

    def link_existing_artifact(
        self, work_item_id, artifact_url, artifact_name, comment, config
    ) -> bool:
        # Links existing artifact to work item
        pass

    def get_work_item_artifacts(
        self, work_item_id, config
    ) -> List[Dict[str, Any]]:
        # Retrieves all artifact links
        pass
```

---

## Usage Guide

### Prerequisites

1. **Azure Artifacts Feed Created**
   ```bash
   # Create feed via Azure DevOps UI or CLI
   az artifacts universal package create \
     --organization https://dev.azure.com/your-org \
     --project "Audit Cortex 2" \
     --feed "ai-sdlc-evidence"
   ```

2. **Permissions Configured**
   - Contributor access to Azure Artifacts feed
   - Work item edit permissions

3. **Environment Variables Set**
   ```bash
   export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-org"
   export AZURE_DEVOPS_PAT="your-pat-token"
   export AZURE_DEVOPS_PROJECT="Audit Cortex 2"
   ```

### Basic Usage - Workflow Integration

**Option 1: Enable in Workflow Execution**

```python
from ai_sdlc.orchestration import WorkflowOrchestrator
from plugins.databricks_devops_integrations.integrations.azure_devops import AzureDevOpsPlugin

# Initialize
orchestrator = WorkflowOrchestrator(work_item_id="6340168")
ado_plugin = AzureDevOpsPlugin()
ado_config = PluginConfig(...)

# Run workflow with persistent artifact creation
result = orchestrator.run_workflow(
    work_item_id="6340168",
    create_persistent_artifact=True,  # Enable persistent artifacts
    artifact_version="1.0.0",
    ado_plugin=ado_plugin,
    ado_config=ado_config
)

# Access artifact info
artifact_info = result["stages"]["evidence_collection"]["artifact_package"]
print(f"Artifact URL: {artifact_info['package_url']}")
print(f"Files included: {artifact_info['files_count']}")
```

**Option 2: Direct Agent Usage**

```python
from ai_sdlc.agents import EvidenceCollectorAgent
from ai_sdlc.evidence import EvidenceCollector

# Collect evidence from previous stages
agent = EvidenceCollectorAgent(work_item_id="6340168")

input_data = {
    "previous_stages": {
        "planning": {...},
        "code_generation": {...},
        # ... other stages
    },
    "create_persistent_artifact": True,
    "artifact_version": "1.0.0",
    "ado_plugin": ado_plugin,
    "ado_config": ado_config
}

result = agent.execute(input_data)

if result["success"]:
    artifact_info = result["data"]["artifact_package"]
    print(f"Created artifact: {artifact_info['package_url']}")
```

### Advanced Usage - Direct API Calls

**Creating Artifact Package Manually**

```python
from plugins.databricks_devops_integrations.integrations.azure_devops import AzureDevOpsPlugin
from ai_sdlc.evidence import EvidenceItem, EvidenceCategory, EvidenceCollector

# Collect evidence
collector = EvidenceCollector(work_item_id="6340168", base_path="./evidence")

# Add evidence items
collector.add_evidence("./plan.md", EvidenceCategory.PLAN, "planning")
collector.add_evidence("./service.py", EvidenceCategory.CODE, "code_generation")
collector.add_screenshot("./dashboard.png", "qa_testing")

# Get evidence items
evidence_items = collector.get_all_evidence()

# Create persistent artifact
ado_plugin = AzureDevOpsPlugin()
artifact_info = ado_plugin.create_artifact_package(
    work_item_id="6340168",
    artifact_name="pbi-6340168-evidence",
    artifact_version="1.0.0",
    evidence_items=evidence_items,
    config=ado_config
)

print(f"Package ID: {artifact_info['package_id']}")
print(f"Package URL: {artifact_info['package_url']}")
print(f"Files included: {artifact_info['files_count']}")
```

**Linking Existing Artifact to Another Work Item**

```python
# Link same artifact to multiple work items
ado_plugin.link_existing_artifact(
    work_item_id="6340200",  # Different work item
    artifact_url=artifact_info['artifact_link'],
    artifact_name="Shared Evidence Package v1.0.0",
    comment="Reusing evidence from PBI-6340168",
    config=ado_config
)
```

**Retrieving Work Item Artifacts**

```python
# Get all artifacts linked to work item
artifacts = ado_plugin.get_work_item_artifacts(
    work_item_id="6340168",
    config=ado_config
)

for artifact in artifacts:
    print(f"Artifact: {artifact['name']}")
    print(f"URL: {artifact['url']}")
    print(f"Comment: {artifact['comment']}")
```

---

## CLI Commands

### Create Persistent Artifact from Workflow

```bash
# Run workflow with persistent artifact creation
python -m ai_sdlc.cli.workflow_commands run-workflow \
  --work-item-id 6340168 \
  --create-persistent-artifact \
  --artifact-version 1.0.0 \
  --evidence-path "./evidence"
```

### Create Artifact from Evidence Directory

```bash
# Create artifact package from existing evidence
python -m ai_sdlc.cli.evidence_commands create-artifact \
  --work-item-id 6340168 \
  --evidence-dir "./evidence/PBI-6340168" \
  --artifact-name "pbi-6340168-evidence" \
  --version 1.0.0
```

### Link Existing Artifact

```bash
# Link existing artifact to another work item
python -m ai_sdlc.cli.evidence_commands link-artifact \
  --work-item-id 6340200 \
  --artifact-url "https://dev.azure.com/org/_apis/packaging/..." \
  --artifact-name "Shared Evidence v1.0.0"
```

### List Work Item Artifacts

```bash
# List all artifacts linked to work item
python -m ai_sdlc.cli.evidence_commands list-artifacts \
  --work-item-id 6340168
```

### Download Artifact Package

```bash
# Download artifact package for review
az artifacts universal download \
  --organization https://dev.azure.com/your-org \
  --project "Audit Cortex 2" \
  --scope project \
  --feed "ai-sdlc-evidence" \
  --name "pbi-6340168-evidence" \
  --version "1.0.0" \
  --path "./downloaded-evidence"
```

---

## API Reference

### `create_artifact_package()`

**Purpose:** Create and upload a versioned artifact package to Azure Artifacts.

**Signature:**
```python
def create_artifact_package(
    self,
    work_item_id: str,
    artifact_name: str,
    artifact_version: str,
    evidence_items: List[EvidenceItem],
    config: Optional[PluginConfig] = None,
) -> Dict[str, Any]
```

**Parameters:**
- `work_item_id` (str): Work item ID to link artifact to
- `artifact_name` (str): Package name (e.g., "pbi-6340168-evidence")
- `artifact_version` (str): Semantic version (e.g., "1.0.0", "2.1.3")
- `evidence_items` (List[EvidenceItem]): List of evidence items to include
- `config` (PluginConfig): Azure DevOps configuration

**Returns:**
```python
{
    "package_id": "abc123...",
    "package_url": "https://dev.azure.com/org/project/_packaging?...",
    "version": "1.0.0",
    "files_count": 23,
    "artifact_link": "https://dev.azure.com/org/_apis/packaging/...",
    "files": [
        {"filename": "plan.md", "category": "plan", "stage": "planning", "size_bytes": 4562},
        ...
    ]
}
```

**Raises:**
- `IntegrationError`: If upload fails or package version already exists

**Example:**
```python
artifact_info = ado_plugin.create_artifact_package(
    work_item_id="6340168",
    artifact_name="pbi-6340168-evidence",
    artifact_version="1.0.0",
    evidence_items=evidence_items,
    config=ado_config
)
```

---

### `link_existing_artifact()`

**Purpose:** Link an existing artifact package to a work item.

**Signature:**
```python
def link_existing_artifact(
    self,
    work_item_id: str,
    artifact_url: str,
    artifact_name: str,
    comment: Optional[str] = None,
    config: Optional[PluginConfig] = None,
) -> bool
```

**Parameters:**
- `work_item_id` (str): Work item ID to link to
- `artifact_url` (str): URL of existing artifact package
- `artifact_name` (str): Display name for the link
- `comment` (str, optional): Comment for the link
- `config` (PluginConfig): Azure DevOps configuration

**Returns:**
- `bool`: True if successful

**Raises:**
- `IntegrationError`: If linking fails

**Example:**
```python
success = ado_plugin.link_existing_artifact(
    work_item_id="6340200",
    artifact_url="https://dev.azure.com/org/_apis/packaging/feeds/...",
    artifact_name="Shared Evidence Package v1.0.0",
    comment="Reusing evidence from PBI-6340168",
    config=ado_config
)
```

---

### `get_work_item_artifacts()`

**Purpose:** Retrieve all artifacts linked to a work item.

**Signature:**
```python
def get_work_item_artifacts(
    self,
    work_item_id: str,
    config: Optional[PluginConfig] = None,
) -> List[Dict[str, Any]]
```

**Parameters:**
- `work_item_id` (str): Work item ID
- `config` (PluginConfig): Azure DevOps configuration

**Returns:**
```python
[
    {
        "url": "https://dev.azure.com/org/_apis/packaging/...",
        "name": "Evidence Package 1.0.0",
        "comment": "Persistent artifact package with 23 evidence files",
        "rel": "ArtifactLink"
    },
    ...
]
```

**Raises:**
- `IntegrationError`: If retrieval fails

**Example:**
```python
artifacts = ado_plugin.get_work_item_artifacts(
    work_item_id="6340168",
    config=ado_config
)

for artifact in artifacts:
    print(f"Artifact: {artifact['name']}")
```

---

## Best Practices

### Naming Conventions

**Artifact Names:**
- Use work item prefix: `pbi-{work_item_id}-evidence`
- For specific types: `pbi-{work_item_id}-{type}` (e.g., `pbi-6340168-screenshots`)
- Lowercase with hyphens

**Versions:**
- Follow semantic versioning: `MAJOR.MINOR.PATCH`
- Initial release: `1.0.0`
- Bug fixes: `1.0.1`, `1.0.2`
- New features: `1.1.0`, `1.2.0`
- Breaking changes: `2.0.0`

### Versioning Strategy

**When to Increment Version:**

| Change Type | Version Update | Example |
|-------------|---------------|---------|
| Add new evidence files | MINOR (1.0.0 → 1.1.0) | Added integration test results |
| Fix/replace incorrect file | PATCH (1.0.0 → 1.0.1) | Corrected screenshot |
| Restructure package | MAJOR (1.0.0 → 2.0.0) | Changed directory structure |
| Update metadata only | PATCH (1.0.0 → 1.0.1) | Updated manifest.json |

### Storage Management

**Feed Organization:**
- Use dedicated feed: `ai-sdlc-evidence`
- Separate feeds for dev/staging/prod if needed
- Configure retention policies (e.g., keep last 10 versions)

**Retention Policies:**
```yaml
# Recommended retention
- Keep all versions for: 90 days
- Keep minimum versions: 3
- Delete versions older than: 1 year
```

### Performance Optimization

**Package Size:**
- Aim for < 100MB per package
- Use compression (tar.gz)
- Exclude unnecessary files (.DS_Store, __pycache__, etc.)

**Upload Optimization:**
```python
# Don't include huge files
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

evidence_items_filtered = [
    item for item in evidence_items
    if item.size_bytes < MAX_FILE_SIZE
]
```

### Security Considerations

**Access Control:**
- Restrict feed permissions to necessary users/groups
- Use PAT tokens with minimal scopes
- Rotate PAT tokens regularly (90 days)

**Sensitive Data:**
- Never include credentials or secrets in artifacts
- Sanitize logs before packaging
- Review evidence before upload

**Audit Trail:**
- Log all artifact creations
- Track who created each version
- Monitor artifact downloads

---

## Troubleshooting

### Common Issues

#### Issue 1: "Package version already exists"

**Error:**
```
IntegrationError: Artifact package pbi-6340168-evidence:1.0.0 already exists. Use a different version.
```

**Solution:**
```python
# Increment version
artifact_version = "1.0.1"  # or "1.1.0", "2.0.0"

# Or check existing versions first
artifacts = ado_plugin.get_work_item_artifacts(work_item_id, config)
latest_version = parse_latest_version(artifacts)
new_version = increment_version(latest_version)
```

---

#### Issue 2: "Feed not found"

**Error:**
```
IntegrationError: Failed to upload artifact package: HTTP 404 - Feed 'ai-sdlc-evidence' not found
```

**Solution:**
```bash
# Create feed via Azure DevOps UI
# Navigate to: Artifacts → Create Feed → "ai-sdlc-evidence"

# Or via CLI
az artifacts universal package create \
  --organization https://dev.azure.com/your-org \
  --feed "ai-sdlc-evidence" \
  --scope project
```

---

#### Issue 3: "Permission denied"

**Error:**
```
IntegrationError: Failed to upload artifact package: HTTP 403 - Forbidden
```

**Solution:**
1. Verify PAT token has "Packaging (Read & Write)" scope
2. Check user has Contributor role on feed
3. Verify organization URL is correct

```bash
# Test PAT permissions
az login --pat-token YOUR_PAT_TOKEN
az artifacts universal package list --feed "ai-sdlc-evidence"
```

---

#### Issue 4: "Upload timeout"

**Error:**
```
IntegrationError: Failed to upload artifact package: Connection timeout
```

**Solution:**
```python
# Increase timeout
response = requests.put(
    upload_url,
    headers=headers,
    auth=auth,
    data=package_data,
    timeout=600  # 10 minutes instead of 5
)

# Or split into smaller packages
if len(evidence_items) > 100:
    # Create multiple packages
    for i, chunk in enumerate(chunks(evidence_items, 50)):
        artifact_name = f"pbi-{work_item_id}-evidence-part{i+1}"
        create_artifact_package(...)
```

---

#### Issue 5: "Artifact link not visible in ADO"

**Problem:** Artifact uploaded but not showing in work item

**Solution:**
```python
# Verify link was created
artifacts = ado_plugin.get_work_item_artifacts(work_item_id, config)
print(f"Found {len(artifacts)} artifacts")

# If empty, manually link
ado_plugin.link_existing_artifact(
    work_item_id=work_item_id,
    artifact_url=artifact_info['artifact_link'],
    artifact_name="Evidence Package 1.0.0",
    config=ado_config
)
```

---

### Debugging Tips

**Enable Debug Logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Will show detailed API requests/responses
ado_plugin.create_artifact_package(...)
```

**Verify Package Structure:**
```python
# Before uploading, check package contents
import tarfile

with tarfile.open(package_file, "r:gz") as tar:
    tar.list()  # Print all files

    # Verify manifest
    manifest = tar.extractfile("manifest.json")
    print(json.load(manifest))
```

**Test Upload with Small Package:**
```python
# Test with minimal evidence
test_items = evidence_items[:3]  # Only 3 files

artifact_info = ado_plugin.create_artifact_package(
    work_item_id=work_item_id,
    artifact_name="pbi-test-package",
    artifact_version="0.1.0",
    evidence_items=test_items,
    config=ado_config
)
```

---

## Examples

### Example 1: Complete Workflow with Persistent Artifact

```python
from ai_sdlc.orchestration import WorkflowOrchestrator
from plugins.databricks_devops_integrations.integrations.azure_devops import AzureDevOpsPlugin, PluginConfig

# Configure
work_item_id = "6340168"
ado_config = PluginConfig(
    api_endpoint="https://dev.azure.com/symphonyvsts",
    api_key=os.getenv("AZURE_DEVOPS_PAT"),
    organization="symphonyvsts",
    project="Audit Cortex 2"
)
ado_plugin = AzureDevOpsPlugin()

# Run workflow
orchestrator = WorkflowOrchestrator(work_item_id=work_item_id)

result = orchestrator.run_workflow(
    work_item_id=work_item_id,
    create_persistent_artifact=True,  # Enable persistent artifacts
    artifact_version="1.0.0",
    ado_plugin=ado_plugin,
    ado_config=ado_config
)

# Check results
if result["success"]:
    artifact_info = result["stages"]["evidence_collection"]["artifact_package"]

    print(f"✅ Workflow Complete!")
    print(f"📦 Artifact Package Created:")
    print(f"   - Name: {artifact_info['artifact_name']}")
    print(f"   - Version: {artifact_info['version']}")
    print(f"   - Files: {artifact_info['files_count']}")
    print(f"   - URL: {artifact_info['package_url']}")

    # View in browser
    import webbrowser
    webbrowser.open(artifact_info['package_url'])
```

---

### Example 2: Create Artifact from Existing Evidence

```python
from pathlib import Path
from ai_sdlc.evidence import EvidenceCollector, EvidenceCategory
from plugins.databricks_devops_integrations.integrations.azure_devops import AzureDevOpsPlugin

# Collect evidence from directory
evidence_dir = Path("./evidence/PBI-6340168")
collector = EvidenceCollector(work_item_id="6340168", base_path=str(evidence_dir))

# Add all files in directory
for file_path in evidence_dir.rglob("*"):
    if file_path.is_file():
        # Determine category and stage from path
        parts = file_path.relative_to(evidence_dir).parts
        stage = parts[0] if len(parts) > 1 else "unknown"

        # Determine category
        if file_path.suffix == ".png":
            category = EvidenceCategory.SCREENSHOT
        elif file_path.suffix == ".py":
            category = EvidenceCategory.CODE
        elif "report" in file_path.name:
            category = EvidenceCategory.REPORT
        else:
            category = EvidenceCategory.DOCUMENTATION

        collector.add_evidence(
            str(file_path),
            category,
            stage,
            description=f"{stage} - {file_path.name}"
        )

# Get all evidence
evidence_items = collector.get_all_evidence()
print(f"Collected {len(evidence_items)} evidence files")

# Create persistent artifact
ado_plugin = AzureDevOpsPlugin()
artifact_info = ado_plugin.create_artifact_package(
    work_item_id="6340168",
    artifact_name="pbi-6340168-evidence",
    artifact_version="1.0.0",
    evidence_items=evidence_items,
    config=ado_config
)

print(f"✅ Created artifact package: {artifact_info['package_url']}")
```

---

### Example 3: Version Incrementing

```python
def get_next_version(work_item_id: str, ado_plugin, ado_config) -> str:
    """Get next semantic version for artifact package."""

    # Get existing artifacts
    artifacts = ado_plugin.get_work_item_artifacts(work_item_id, ado_config)

    # Filter artifacts for this work item
    package_name = f"pbi-{work_item_id}-evidence"
    versions = []

    for artifact in artifacts:
        if package_name in artifact['name']:
            # Extract version from name (e.g., "Evidence Package 1.2.3")
            import re
            match = re.search(r'(\d+\.\d+\.\d+)', artifact['name'])
            if match:
                versions.append(match.group(1))

    if not versions:
        return "1.0.0"  # Initial version

    # Parse latest version
    latest = max(versions, key=lambda v: tuple(map(int, v.split('.'))))
    major, minor, patch = map(int, latest.split('.'))

    # Increment patch version
    return f"{major}.{minor}.{patch + 1}"

# Usage
next_version = get_next_version("6340168", ado_plugin, ado_config)
print(f"Next version: {next_version}")

artifact_info = ado_plugin.create_artifact_package(
    work_item_id="6340168",
    artifact_name="pbi-6340168-evidence",
    artifact_version=next_version,
    evidence_items=evidence_items,
    config=ado_config
)
```

---

### Example 4: Sharing Artifacts Across Work Items

```python
# Create artifact for original work item
artifact_info = ado_plugin.create_artifact_package(
    work_item_id="6340168",
    artifact_name="audit-dashboard-evidence",
    artifact_version="1.0.0",
    evidence_items=evidence_items,
    config=ado_config
)

print(f"Created artifact for PBI-6340168")

# Link same artifact to related work items
related_work_items = ["6340200", "6340201", "6340202"]

for related_id in related_work_items:
    success = ado_plugin.link_existing_artifact(
        work_item_id=related_id,
        artifact_url=artifact_info['artifact_link'],
        artifact_name="Shared Audit Dashboard Evidence v1.0.0",
        comment=f"Shared evidence from PBI-6340168",
        config=ado_config
    )

    if success:
        print(f"✅ Linked artifact to PBI-{related_id}")
```

---

### Example 5: Download and Inspect Artifact

```bash
# Download artifact package
az artifacts universal download \
  --organization https://dev.azure.com/symphonyvsts \
  --project "Audit Cortex 2" \
  --scope project \
  --feed "ai-sdlc-evidence" \
  --name "pbi-6340168-evidence" \
  --version "1.0.0" \
  --path "./downloaded-evidence"

# Extract and inspect
cd downloaded-evidence
tar -xzf pbi-6340168-evidence-1.0.0.tar.gz

# View manifest
cat pbi-6340168-evidence/manifest.json | jq .

# View files
tree pbi-6340168-evidence/

# Review evidence
open pbi-6340168-evidence/qa_testing/screenshot-1.png
open pbi-6340168-evidence/unit_testing/coverage-report.html
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-17 | AI-SDLC Platform Team | Initial documentation for persistent artifacts feature |

---

**For questions or support:**
- Slack: #ai-sdlc-support
- Email: ai-sdlc-support@yourcompany.com
- Documentation: `docs/` directory
