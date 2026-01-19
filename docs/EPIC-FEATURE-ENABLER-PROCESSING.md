# Epic/Feature/Enabler Processing with Wiki Integration

**Document Version:** 1.0
**Last Updated:** 2026-01-17 14:21:02
**Prepared by:** Databricks Platform Team
**Project:** Your Project

---

## Overview

Automatically process Azure DevOps Epics, Features, and Enablers to find existing child PBIs or generate new ones. Supports importing work items directly from wiki design documents.

**Key Features:**
- ✅ Process ADO work item URLs (Epic, Feature, Enabler)
- ✅ Auto-detect existing child PBIs
- ✅ Generate missing child PBIs automatically
- ✅ Import work items from wiki pages
- ✅ Parse wiki markdown for ADO references
- ✅ Link generated PBIs to parent work items

---

## Use Case: Wiki Design Documents

Your Your Project team creates design documents in the wiki with references to Epics, Features, and Enablers. This tool automatically:

1. **Parses the wiki page** to find all ADO work item references
2. **Checks each work item** for existing child PBIs
3. **Generates missing PBIs** based on work item description
4. **Links everything together** in Azure DevOps

**Example Wiki:** [Your Design Document](https://dev.azure.com/your-organization/YourProject/_wiki/wikis/YourProject.wiki/100001/YourFeature-automated-Unit-and-Integration-test-design)

---

## Prerequisites

### Environment Variables

```powershell
# PowerShell
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_ORG_URL', 'https://dev.azure.com/your-organization', 'User')
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', 'your-pat-token', 'User')
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PROJECT', 'Your Project', 'User')
```

---

## CLI Commands

### Process ADO Work Item

**Find existing and generate missing child PBIs:**

```bash
python -m ai_sdlc.cli.epic_commands process-work-item "https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345"
```

**Output:**
```
🔍 Processing ADO work item...

URL: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345

✅ Processed Feature:
   ID: 12345
   Title: Your Design Document
   Total Children: 5
   Existing: 2
   Generated: 3

📋 Existing Child PBIs:
   - 12346: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12346
   - 12347: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12347

🆕 Generated Child PBIs:
   - 12348: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12348
   - 12349: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12349
   - 12350: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12350

✨ Generated 3 new child PBIs
```

**Only find existing (no generation):**

```bash
python -m ai_sdlc.cli.epic_commands process-work-item "https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345" --no-generate
```

### Process Wiki Page

**Import all work items from wiki and process:**

```bash
python -m ai_sdlc.cli.epic_commands process-wiki "https://dev.azure.com/your-organization/YourProject/_wiki/wikis/YourProject.wiki/100001/YourFeature-automated-Unit-and-Integration-test-design"
```

**Output:**
```
📖 Processing Wiki Page...

Project: Your Project
Page: Your Design Document
URL: https://dev.azure.com/your-organization/YourProject/_wiki/wikis/YourProject.wiki/100001/...

🔍 Found 3 work items in wiki

1. Feature 12345: Your Design Document
   Existing children: 2
   Generated children: 3
      - Created 12348: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12348
      - Created 12349: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12349
      - Created 12350: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12350

2. Enabler 12351: Automated testing framework setup
   Existing children: 0
   Generated children: 2
      - Created 12355: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12355
      - Created 12356: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12356

3. Epic 6340100: Test Automation Initiative
   Existing children: 5
   Generated children: 0

📊 Summary:
   Total work items: 3
   Existing child PBIs: 7
   Generated child PBIs: 5
   Total child PBIs: 12
```

### Generate from Epic

**Generate child PBIs from Epic:**

```bash
python -m ai_sdlc.cli.epic_commands generate-from-epic 6340100
```

### List Children

**List all child work items:**

```bash
python -m ai_sdlc.cli.epic_commands list-children 12345
```

**Output:**
```
🔍 Finding child work items for 12345...

✅ Found 5 child work items:

   - 12346: Implement unit test framework
     URL: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12346
     Status: Active

   - 12347: Set up integration test environment
     URL: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12347
     Status: New

   ...
```

---

## Wiki Reference Formats

The tool recognizes multiple wiki reference formats:

### Format 1: Simple Work Item ID

```markdown
## Related Work Items
- [[12345]]
- [[12351]]
- [[6340100]]
```

### Format 2: Full URLs

```markdown
## Design References
- https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345
- https://dev.azure.com/your-organization/YourProject/_workitems/edit/12351
```

### Format 3: Named Links

```markdown
## Work Items
- [[Feature: Test Design|12345]]
- [[Enabler: Test Framework|12351]]
- [[Epic: Test Automation|6340100]]
```

All formats are automatically detected and processed.

---

## Auto-Generation Logic

### How Child PBIs are Generated

The system analyzes the parent work item description and generates child PBIs based on structured content:

#### Pattern 1: Explicit Child Items

```markdown
# Epic Description

Child items to implement:
- [Enabler] Set up test automation framework
- [Feature] Dashboard for test results
- [Enabler] CI/CD integration
- [Feature] Test reporting system
```

**Result:** Generates 4 PBIs (2 Enablers, 2 Features)

#### Pattern 2: Numbered List

```markdown
# Feature Description

Implementation tasks:
1. Build REST API endpoints
2. Create database schema
3. Implement authentication
4. Add monitoring and logging
```

**Result:** Generates 4 PBIs (auto-detects type from title)

#### Pattern 3: Default Single PBI

If no structured format found, generates one child PBI with:
- **Title:** "Implement {Parent Title}"
- **Description:** Full parent description
- **Type:** Same as parent (Enabler → Enabler, Feature → Feature)
- **Story Points:** 8

### Type Detection

Child PBI type is auto-detected from title:

**Enabler if contains:**
- api, framework, pipeline
- setup, infrastructure, tooling
- ci/cd, automation, testing

**Feature otherwise**

---

## Python API Usage

### Process Work Item

```python
from ai_sdlc.generators import EpicFeatureGenerator, PBIGenerator
from plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import AzureDevOpsPlugin
from plugins.databricks_devops_integrations.sdk.base_plugin import PluginConfig

# Configure for Your Project
config = PluginConfig(
    api_endpoint="https://dev.azure.com/your-organization",
    api_key="your-pat-token",
    organization="your-organization",
    project="Your Project"
)

# Initialize
ado_plugin = AzureDevOpsPlugin()
ado_plugin.authenticate(config)

pbi_generator = PBIGenerator(ado_plugin, config)
epic_generator = EpicFeatureGenerator(ado_plugin, config, pbi_generator)

# Process work item
ado_url = "https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345"
result = epic_generator.process_work_item_url(ado_url, auto_generate=True)

print(f"Parent: {result.parent_type.value} {result.parent_id}")
print(f"Existing children: {len(result.existing_children)}")
print(f"Generated children: {len(result.generated_children)}")
```

### Process Wiki Page

```python
# Process wiki page
wiki_url = "https://dev.azure.com/your-organization/YourProject/_wiki/wikis/YourProject.wiki/100001/YourFeature-automated-Unit-and-Integration-test-design"

results = epic_generator.process_wiki_url(wiki_url, auto_generate=True)

for result in results:
    print(f"{result.parent_type.value} {result.parent_id}: {result.parent_title}")
    print(f"  Generated {len(result.generated_children)} child PBIs")
```

### Generate from Epic

```python
# Generate child PBIs from Epic
epic_id = "6340100"
pbi_ids = epic_generator.generate_pbis_from_epic(epic_id)

print(f"Generated {len(pbi_ids)} PBIs from Epic {epic_id}")
for pbi_id in pbi_ids:
    print(f"  - PBI {pbi_id}")
```

---

## Example Workflows

### Workflow 1: Design Document → Auto-Generate PBIs

**Scenario:** Team creates design document in wiki with Epic/Feature references

```bash
# 1. Team creates wiki page with design and ADO references
# Wiki URL: https://dev.azure.com/your-organization/YourProject/_wiki/wikis/YourProject.wiki/100001/YourFeature-automated-Unit-and-Integration-test-design

# Wiki content includes:
# ## Related Work Items
# - [[12345]] - Feature: Test Design
# - [[12351]] - Enabler: Test Framework
# - [[6340100]] - Epic: Test Automation

# 2. Process wiki to generate all child PBIs
python -m ai_sdlc.cli.epic_commands process-wiki "https://dev.azure.com/your-organization/YourProject/_wiki/wikis/YourProject.wiki/100001/YourFeature-automated-Unit-and-Integration-test-design"

# Output: Processes all 3 work items, generates missing PBIs, links everything

# 3. Review generated PBIs in Azure DevOps
# All PBIs are now linked to parent work items and ready for sprint planning
```

### Workflow 2: Epic Breakdown

**Scenario:** Epic exists but needs child PBIs

```bash
# 1. Create Epic in ADO with description:
# Epic: Test Automation Initiative
#
# Child items:
# - [Enabler] Test automation framework
# - [Feature] Test dashboard
# - [Enabler] CI/CD integration
# - [Feature] Test reporting

# 2. Generate child PBIs
python -m ai_sdlc.cli.epic_commands process-work-item "https://dev.azure.com/your-organization/YourProject/_workitems/edit/6340100"

# Output: Creates 4 PBIs linked to Epic

# 3. Or use direct Epic generation
python -m ai_sdlc.cli.epic_commands generate-from-epic 6340100
```

### Workflow 3: Feature with Existing Children

**Scenario:** Feature has some PBIs, need to add more

```bash
# 1. Check existing children
python -m ai_sdlc.cli.epic_commands list-children 12345

# 2. Process Feature (only generates missing PBIs)
python -m ai_sdlc.cli.epic_commands process-work-item "https://dev.azure.com/your-organization/YourProject/_workitems/edit/12345"

# Output: Finds 2 existing, generates 3 new PBIs
```

### Workflow 4: Sprint Planning from Wiki

**Scenario:** Use wiki design docs for sprint planning

```bash
# 1. Product owner creates wiki page with all Features/Enablers for sprint
# 2. Process wiki to generate all PBIs
python -m ai_sdlc.cli.epic_commands process-wiki "https://dev.azure.com/your-organization/YourProject/_wiki/wikis/YourProject.wiki/100002/Sprint-4-Planning"

# 3. All PBIs now exist in backlog
# 4. Team can estimate and commit in sprint planning meeting
```

---

## Work Item Description Format

### Best Practice for Parent Work Items

Structure your Epic/Feature/Enabler descriptions for optimal PBI generation:

```markdown
# Feature: Audit Trail Dashboard

## Overview
Build interactive dashboard for compliance team to view audit trails.

## Child Items
- [Feature] Dashboard UI with filters
- [Enabler] REST API for audit data
- [Feature] PDF export functionality
- [Enabler] Real-time data refresh pipeline

## Additional Details
...
```

**Result:** Generates 4 properly typed PBIs

### Alternative Format (Numbered List)

```markdown
# Enabler: Test Automation Framework

## Implementation Steps

1. Set up pytest framework with Databricks fixtures
2. Create unit test templates
3. Build integration test environment
4. Configure CI pipeline for test execution
5. Set up code coverage reporting

## Technical Details
...
```

**Result:** Generates 5 PBIs (auto-detected as Enablers from parent type)

---

## Integration with Your Project Workflows

### 1. Design Phase → Wiki

```
Design Document (Wiki)
  ↓
Contains ADO work item references
  ↓
process-wiki command
  ↓
Generates all child PBIs
  ↓
Linked in Azure DevOps
```

### 2. Epic Planning → PBIs

```
Epic Created
  ↓
Description with child items
  ↓
process-work-item command
  ↓
Child PBIs generated
  ↓
Ready for sprint planning
```

### 3. Sprint Preparation

```
Wiki: Sprint Planning Doc
  ↓
References Epics/Features
  ↓
process-wiki command
  ↓
All PBIs in backlog
  ↓
Team estimates in sprint planning
```

---

## Troubleshooting

### Issue: "No work items found in wiki"

**Cause:** Wiki page doesn't contain recognized ADO references

**Solution:** Add work item references in wiki:
```markdown
## Related Work Items
- [[12345]]
- https://dev.azure.com/.../workitems/edit/12351
```

### Issue: "No child PBIs generated"

**Cause:** Work item already has all expected children

**Solution:** Check with `--no-generate` flag first:
```bash
python -m ai_sdlc.cli.epic_commands process-work-item <URL> --no-generate
```

### Issue: "Generated wrong PBI type"

**Cause:** Auto-detection from title didn't work

**Solution:** Use explicit format in parent description:
```markdown
- [Enabler] Your title here
- [Feature] Your title here
```

### Issue: "Can't fetch wiki content"

**Cause:** PAT token doesn't have wiki read permission

**Solution:** Regenerate PAT with "Wiki: Read" permission

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Process Design Wiki

on:
  workflow_dispatch:
    inputs:
      wiki_url:
        description: 'Wiki URL to process'
        required: true

jobs:
  process-wiki:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install azure-devops PyYAML requests

      - name: Process Wiki
        env:
          AZURE_DEVOPS_ORG_URL: https://dev.azure.com/your-organization
          AZURE_DEVOPS_PAT: ${{ secrets.AZURE_DEVOPS_PAT }}
          AZURE_DEVOPS_PROJECT: Your Project
        run: |
          python -m ai_sdlc.cli.epic_commands process-wiki "${{ github.event.inputs.wiki_url }}"
```

---

## Best Practices

### 1. Structure Parent Work Item Descriptions

Use explicit `[Enabler]` and `[Feature]` tags:
```markdown
- [Enabler] API framework
- [Feature] User dashboard
```

### 2. Use Wiki for Design Documents

Create wiki pages with ADO references:
```markdown
## Architecture
Design overview...

## Work Items
- [[Epic: Test Automation|6340100]]
- [[Feature: Test Dashboard|12345]]
```

### 3. Check Before Generating

Use `--no-generate` first to see what exists:
```bash
python -m ai_sdlc.cli.epic_commands process-work-item <URL> --no-generate
```

### 4. Link Wiki to Work Items

Add wiki URL to work item descriptions:
```markdown
Design: https://dev.azure.com/.../wiki/.../100001/Design-Doc
```

### 5. Use Consistent Naming

Prefix work items with type:
- Epic: "Test Automation Initiative"
- Feature: "Audit Trail Dashboard"
- Enabler: "Test Framework Setup"

---

## Related Documentation

- [PBI Generation Guide](PBI-GENERATION-GUIDE.md)
- [ADO Requirement Integration](ADO-REQUIREMENT-INTEGRATION.md)
- [API Reference](api-reference.md)

---

**Project:** Your Project
**Organization:** your-organization
**Contact:** data-platform@vivekgana.com
