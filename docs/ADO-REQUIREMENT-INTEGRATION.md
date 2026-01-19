# Azure DevOps Work Item <-> Requirement Integration

**Document Version:** 1.0
**Last Updated:** 2026-01-05 10:45:00
**Prepared by:** Databricks Platform Team

---

## Overview

This guide explains how to integrate REQ-*.md requirement files with Azure DevOps work items, enabling bidirectional synchronization between documentation and tracking systems.

## Features

✅ **Link Requirements to ADO Work Items**
- Automatically create ADO work items from requirements
- Link existing requirements to ADO work items
- Parse ADO URLs and extract work item details

✅ **Bidirectional Sync**
- Sync requirement changes → ADO work items
- Sync ADO work item changes → requirements
- Detect and report changes

✅ **Validation**
- Validate ADO links in requirements
- Check work item existence and accessibility
- Verify organization and project match

✅ **Search and Discovery**
- Search ADO work items by requirement ID
- Find linked work items automatically

---

## Prerequisites

### 1. Environment Variables

Set these environment variables:

```powershell
# PowerShell
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_ORG_URL', 'https://dev.azure.com/your-organization', 'User')
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', 'your-52-character-pat-token', 'User')
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PROJECT', 'Your Project', 'User')
```

```bash
# Linux/Mac
export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-organization"
export AZURE_DEVOPS_PAT="your-52-character-pat-token"
export AZURE_DEVOPS_PROJECT="Your Project"
```

### 2. Azure DevOps PAT Token

Generate a Personal Access Token with these scopes:
- **Work Items**: Read, Write, Manage
- **Project and Team**: Read

See [AZURE_PAT_SETUP.md](../plugins/databricks-devops-integrations/docs/setup/AZURE_PAT_SETUP.md) for detailed instructions.

### 3. Python Dependencies

```bash
pip install azure-devops PyYAML
```

---

## Requirement File Format

Requirements must include an optional `ado` field in the YAML frontmatter:

```markdown
---
req_id: REQ-101
title: Implement user authentication
owner: john.doe@company.com
product: Platform
team: Engineering
priority: P1
status: In Dev
target_release: v1.0.0
created: 2026-01-01
updated: 2026-01-05

links:
  ado: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345
  jira: null
  pr: null
  docs: https://docs.company.com/req-101

repos:
  - repo: marketplace
    base_branch: develop
    release_branch: main
---

## 1. Problem statement
...
```

---

## CLI Commands

### Link Requirement to ADO

**Link existing requirement to ADO work item (creates if missing):**

```bash
python -m ai_sdlc.cli.ado_commands link-requirement requirements/REQ-101.md --create
```

**Output:**
```
✅ Requirement REQ-101 linked to ADO:
   https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345

💡 Add this to your requirement frontmatter:
   ado: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345
```

**Options:**
- `--create`: Create ADO work item if `ado_link` is missing in requirement

### Sync Requirement to ADO

**Push requirement changes to Azure DevOps:**

```bash
python -m ai_sdlc.cli.ado_commands sync-to-ado requirements/REQ-101.md
```

**What gets synced:**
- Title: `[REQ-101] {title}`
- Description: Problem statement, acceptance criteria
- Status: Mapped from requirement status
- Priority: Mapped from requirement priority (P1/P2/P3)
- Assignee: Requirement owner
- Tags: `requirement`, `REQ-101`, product, team
- Story Points: Estimated from complexity

**Output:**
```
✅ Synced requirement REQ-101 to ADO
   https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345
```

### Sync ADO to Requirement

**Pull changes from Azure DevOps back to requirement:**

```bash
python -m ai_sdlc.cli.ado_commands sync-from-ado requirements/REQ-101.md
```

**What gets detected:**
- Status changes
- Assignee changes
- Priority changes

**Output:**
```
📥 Changes detected from ADO:
   status: In Dev → In QA
   owner: john.doe@company.com → jane.smith@company.com

💡 To apply changes, add --apply flag
```

**Apply changes automatically:**

```bash
python -m ai_sdlc.cli.ado_commands sync-from-ado requirements/REQ-101.md --apply
```

### Validate ADO Link

**Verify that ADO link in requirement is valid:**

```bash
python -m ai_sdlc.cli.ado_commands validate-link requirements/REQ-101.md
```

**Output:**
```
✅ ADO link is valid:
   https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345

📋 Work Item Details:
   Organization: your-organization
   Project: Your Project
   Work Item ID: 12345
   Title: [REQ-101] Implement user authentication
   Status: Active
   Assignee: john.doe@company.com
```

### Search ADO by Requirement ID

**Find ADO work item by requirement ID:**

```bash
python -m ai_sdlc.cli.ado_commands search REQ-101
```

**Output:**
```
✅ Found ADO work item for REQ-101:
   ID: 12345
   Title: [REQ-101] Implement user authentication
   Status: Active
   Assignee: john.doe@company.com
   URL: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345
```

---

## Python API Usage

### Basic Usage

```python
from ai_sdlc.integrations.ado_requirement_sync import ADORequirementSync, ADOWorkItemReference
from ai_sdlc.parsers.requirement_parser import RequirementParser
from plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import AzureDevOpsPlugin
from plugins.databricks_devops_integrations.sdk.base_plugin import PluginConfig

# Configure ADO
config = PluginConfig(
    api_endpoint="https://dev.azure.com/your-organization",
    api_key="your-pat-token",
    organization="your-organization",
    project="Your Project"
)

# Initialize components
ado_plugin = AzureDevOpsPlugin()
ado_plugin.authenticate(config)

req_parser = RequirementParser()
sync = ADORequirementSync(ado_plugin, config, req_parser)

# Parse requirement
requirement = req_parser.parse_file("requirements/REQ-101.md")

# Link to ADO (creates if missing)
ado_url = sync.link_requirement_to_ado(requirement, create_if_missing=True)
print(f"Linked to: {ado_url}")

# Sync changes to ADO
success = sync.sync_requirement_to_ado(requirement, ado_url)
print(f"Synced: {success}")

# Validate link
is_valid, error = sync.validate_ado_link(ado_url)
print(f"Valid: {is_valid}, Error: {error}")
```

### Parse ADO URL

```python
from ai_sdlc.integrations.ado_requirement_sync import ADOWorkItemReference

ado_url = "https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345"

ado_ref = ADOWorkItemReference.parse_url(ado_url)
print(f"Organization: {ado_ref.organization}")
print(f"Project: {ado_ref.project}")
print(f"Work Item ID: {ado_ref.work_item_id}")

# Output:
# Organization: your-organization
# Project: Your Project
# Work Item ID: 12345
```

### Search for Work Item

```python
# Search by requirement ID
work_item = sync.search_ado_by_requirement_id("REQ-101")

if work_item:
    print(f"Found: {work_item.title}")
    print(f"Status: {work_item.status}")
    print(f"URL: {work_item.url}")
```

---

## Mapping Rules

### Status Mapping

| Requirement Status | ADO Work Item State |
|-------------------|---------------------|
| Draft | New |
| In Review | Resolved |
| Approved | New |
| In Dev | Active |
| In QA | Resolved |
| Ready for Demo | Resolved |
| Done | Closed |

### Priority Mapping

| Requirement Priority | ADO Priority |
|---------------------|--------------|
| P1 | Critical (1) |
| P2 | High (2) |
| P3 | Medium (3) |

### Story Points Estimation

Automatic story points estimation based on:
- **Base**: 3 points
- **+1** for each acceptance criterion
- **+2** if > 5 functional requirements
- **+1** if demo evidence required
- **Max**: 13 points (Fibonacci)

**Example:**
```
Requirement with:
- 3 acceptance criteria = +3
- 7 functional requirements = +2
- Demo evidence = +1
Total: 3 + 3 + 2 + 1 = 9 story points
```

---

## ADO Work Item Structure

When creating an ADO work item from a requirement, the following structure is used:

### Title
```
[REQ-101] Implement user authentication
```

### Description (HTML)
```html
<h2>Implement user authentication</h2>

<h3>Problem Statement</h3>
<p>Users need secure authentication...</p>

<h3>Acceptance Criteria</h3>
<ul>
  <li><strong>AC-1:</strong> Given a valid user / When they login / Then they are authenticated</li>
  <li><strong>AC-2:</strong> Given an invalid user / When they login / Then they see an error</li>
</ul>

<p><em>Requirement ID:</em> <strong>REQ-101</strong></p>
<p><em>Target Release:</em> v1.0.0</p>
<p><a href="https://docs.company.com/req-101">View full requirement documentation</a></p>
```

### Fields
- **System.Title**: `[REQ-101] Implement user authentication`
- **System.Description**: HTML content (above)
- **System.State**: `Active` (based on status mapping)
- **System.AssignedTo**: Requirement owner
- **Microsoft.VSTS.Common.Priority**: `2` (based on priority mapping)
- **Microsoft.VSTS.Scheduling.StoryPoints**: `9.0` (estimated)
- **System.Tags**: `requirement; REQ-101; Platform; Engineering`
- **Custom.RequirementID**: `REQ-101` (custom field)
- **Custom.TargetRelease**: `v1.0.0` (custom field)

---

## Workflows

### Workflow 1: Create New Requirement with ADO Work Item

```bash
# 1. Create requirement file
vim requirements/REQ-102.md

# 2. Link to ADO (creates work item automatically)
python -m ai_sdlc.cli.ado_commands link-requirement requirements/REQ-102.md --create

# 3. Add ADO URL to requirement frontmatter
# (Copy URL from step 2 output)

# 4. Commit requirement file
git add requirements/REQ-102.md
git commit -m "Add REQ-102 with ADO link"
```

### Workflow 2: Sync Existing Requirement to ADO

```bash
# 1. Update requirement file
vim requirements/REQ-101.md

# 2. Sync changes to ADO
python -m ai_sdlc.cli.ado_commands sync-to-ado requirements/REQ-101.md

# 3. Verify in Azure DevOps
# Open: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345
```

### Workflow 3: Pull ADO Changes to Requirement

```bash
# 1. Team member updates ADO work item (status, assignee, etc.)

# 2. Sync changes from ADO
python -m ai_sdlc.cli.ado_commands sync-from-ado requirements/REQ-101.md

# 3. Review changes and apply if needed
python -m ai_sdlc.cli.ado_commands sync-from-ado requirements/REQ-101.md --apply

# 4. Commit updated requirement
git add requirements/REQ-101.md
git commit -m "Sync REQ-101 from ADO: Status → In QA"
```

### Workflow 4: Validate All Requirements

```bash
# Validate all requirement ADO links
for req in requirements/REQ-*.md; do
    echo "Validating $req..."
    python -m ai_sdlc.cli.ado_commands validate-link "$req"
done
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Sync Requirements to ADO

on:
  push:
    paths:
      - 'requirements/REQ-*.md'

jobs:
  sync-ado:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install azure-devops PyYAML

      - name: Sync to Azure DevOps
        env:
          AZURE_DEVOPS_ORG_URL: ${{ secrets.AZURE_DEVOPS_ORG_URL }}
          AZURE_DEVOPS_PAT: ${{ secrets.AZURE_DEVOPS_PAT }}
          AZURE_DEVOPS_PROJECT: ${{ secrets.AZURE_DEVOPS_PROJECT }}
        run: |
          # Sync all changed requirements
          git diff --name-only HEAD~1 HEAD | grep 'requirements/REQ-.*\.md' | while read req; do
            echo "Syncing $req to ADO..."
            python -m ai_sdlc.cli.ado_commands sync-to-ado "$req"
          done
```

### Azure DevOps Pipelines

```yaml
trigger:
  paths:
    include:
      - requirements/REQ-*.md

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.10'

  - script: |
      pip install azure-devops PyYAML
    displayName: 'Install dependencies'

  - script: |
      # Sync all changed requirements
      git diff --name-only HEAD~1 HEAD | grep 'requirements/REQ-.*\.md' | while read req; do
        echo "Syncing $req to ADO..."
        python -m ai_sdlc.cli.ado_commands sync-to-ado "$req"
      done
    displayName: 'Sync to Azure DevOps'
    env:
      AZURE_DEVOPS_ORG_URL: $(AZURE_DEVOPS_ORG_URL)
      AZURE_DEVOPS_PAT: $(AZURE_DEVOPS_PAT)
      AZURE_DEVOPS_PROJECT: $(AZURE_DEVOPS_PROJECT)
```

---

## Troubleshooting

### Issue: "Invalid ADO URL format"

**Problem:** ADO URL is not recognized

**Solution:**
- Ensure URL format: `https://dev.azure.com/{org}/{project}/_workitems/edit/{id}`
- URL encode spaces in project name (e.g., "Your Project" → "YourProject")

### Issue: "Organization mismatch"

**Problem:** URL organization doesn't match config

**Solution:**
```bash
# Check environment variable
echo $AZURE_DEVOPS_ORG_URL
# Should be: https://dev.azure.com/your-organization

# Update if needed
export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-organization"
```

### Issue: "Work item not found"

**Problem:** Work item ID doesn't exist or no access

**Solution:**
1. Verify work item exists in Azure DevOps
2. Check PAT token has "Work Items: Read" permission
3. Verify you have access to the project

### Issue: "Authentication failed"

**Problem:** PAT token is invalid or expired

**Solution:**
1. Generate new PAT token in Azure DevOps
2. Update environment variable:
   ```bash
   export AZURE_DEVOPS_PAT="new-pat-token"
   ```
3. Verify token has required scopes

---

## Best Practices

### 1. Always Include ADO Link in Requirements

```markdown
links:
  ado: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345
```

### 2. Sync After Every Requirement Update

```bash
# After editing requirement
python -m ai_sdlc.cli.ado_commands sync-to-ado requirements/REQ-101.md
```

### 3. Validate Links Before Commits

```bash
# Pre-commit hook
python -m ai_sdlc.cli.ado_commands validate-link requirements/REQ-101.md
```

### 4. Use Consistent Work Item Types

- **Requirements** → User Story
- **Bugs** → Bug
- **Technical Tasks** → Task

### 5. Keep ADO and Requirements in Sync

- Run `sync-from-ado` periodically to pull ADO changes
- Set up CI/CD to auto-sync on requirement changes

---

## Example: Your ADO Work Item

**URL:** https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345

**Parsed Details:**
```python
organization: your-organization
project: Your Project
work_item_id: 12345
```

**To link this to a requirement:**

```bash
# If requirement already exists
# Add to frontmatter:
links:
  ado: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345

# Validate
python -m ai_sdlc.cli.ado_commands validate-link requirements/REQ-101.md

# Sync
python -m ai_sdlc.cli.ado_commands sync-to-ado requirements/REQ-101.md
```

---

## Related Documentation

- [Requirement Parser API](api-reference.md#requirement-parser)
- [Azure DevOps Plugin](api-reference.md#azure-devops-plugin)
- [Azure PAT Setup](../plugins/databricks-devops-integrations/docs/setup/AZURE_PAT_SETUP.md)
- [Configuration Reference](configuration.md)

---

**Prepared by:** Databricks Platform Team
**Contact:** data-platform@vivekgana.com
