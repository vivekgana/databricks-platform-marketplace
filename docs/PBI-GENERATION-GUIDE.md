# PBI Generation Guide for Your Project

**Document Version:** 1.0
**Last Updated:** 2026-01-05 11:00:00
**Prepared by:** Databricks Platform Team
**Project:** Your Project

---

## Overview

This guide explains how to automatically generate Azure DevOps Product Backlog Items (PBIs) for **Enablers** and **Features** from requirement files for the Your Project project.

**Reference:** [Your Design Document](https://dev.azure.com/your-organization/YourProject/_wiki/wikis/YourProject.wiki/100001/YourFeature-automated-Unit-and-Integration-test-design)

---

## PBI Types

### Enabler PBI
**Purpose:** Technical infrastructure and platform work

**Examples:**
- Build REST API framework
- Set up CI/CD pipeline for Your Project
- Create automated test infrastructure
- Implement logging and monitoring system
- Design data pipeline architecture
- Set up Unity Catalog for audit data

**Characteristics:**
- Technical focus
- Enables other features
- No direct user-facing value
- Infrastructure, tooling, or platform work

### Feature PBI
**Purpose:** User-facing functionality and business capabilities

**Examples:**
- Audit trail dashboard for compliance team
- Automated report generation
- Data classification and tagging
- Real-time monitoring alerts
- Data export capabilities
- User authentication and authorization

**Characteristics:**
- User-facing
- Business value delivery
- Has user personas
- Directly impacts end users

---

## Prerequisites

### 1. Environment Configuration

Set up Azure DevOps for Your Project:

```powershell
# PowerShell
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_ORG_URL', 'https://dev.azure.com/your-organization', 'User')
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', 'your-pat-token', 'User')
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PROJECT', 'Your Project', 'User')
```

### 2. Python Dependencies

```bash
pip install azure-devops PyYAML
```

---

## CLI Commands

### Generate PBIs from Requirement

**Auto-detect PBI type and generate:**

```bash
python -m ai_sdlc.cli.pbi_commands generate-pbis requirements/REQ-101.md
```

**Force Enabler PBI:**

```bash
python -m ai_sdlc.cli.pbi_commands generate-pbis requirements/REQ-101.md --type enabler
```

**Force Feature PBI:**

```bash
python -m ai_sdlc.cli.pbi_commands generate-pbis requirements/REQ-101.md --type feature
```

**Generate PBI with child tasks:**

```bash
python -m ai_sdlc.cli.pbi_commands generate-pbis requirements/REQ-101.md --with-tasks
```

### Batch Generate PBIs

**Generate PBIs for all requirements:**

```bash
python -m ai_sdlc.cli.pbi_commands batch-generate requirements/
```

**With tasks and output report:**

```bash
python -m ai_sdlc.cli.pbi_commands batch-generate requirements/ --with-tasks --output pbi-report.md
```

### Generate Custom Enabler PBI

```bash
python -m ai_sdlc.cli.pbi_commands generate-enabler \
  --title "Set up automated testing framework for Your Project" \
  --description "Build comprehensive test automation infrastructure" \
  --technical-details "Implement pytest framework with Databricks fixtures" \
  --acceptance-criteria "Unit tests run in CI;Integration tests with test catalog;Code coverage > 80%" \
  --components "test_framework;ci_pipeline;databricks_fixtures" \
  --story-points 8 \
  --priority high \
  --tags "testing,infrastructure,audit-cortex"
```

### Generate Custom Feature PBI

```bash
python -m ai_sdlc.cli.pbi_commands generate-feature \
  --title "Audit trail dashboard for compliance team" \
  --description "Interactive dashboard showing audit events and compliance status" \
  --user-story "As a compliance officer, I want to view audit trails so that I can ensure regulatory compliance" \
  --acceptance-criteria "Dashboard shows last 30 days;Filterable by user and event type;Export to PDF" \
  --business-value "Enables compliance team to quickly review audit activities" \
  --personas "Compliance Officer,Auditor,Security Admin" \
  --story-points 13 \
  --priority critical \
  --tags "audit,compliance,dashboard"
```

---

## Auto-Detection Rules

The system automatically detects PBI type based on requirement content:

### Enabler Detection Keywords
- **Title/Description contains:**
  - api, framework, infrastructure
  - pipeline, ci/cd, cicd
  - setup, tooling, library
  - sdk, integration, platform
  - testing framework, automation

### Feature Detection Indicators
- Has user personas defined
- Contains user story format: "As a [user], I want [goal] so that [benefit]"
- Business-focused language

### Default
- If unclear, defaults to **Feature PBI**

---

## Generated PBI Structure

### Enabler PBI Format

```
Title: [Enabler] Set up automated testing framework

Description:
  ├─ Description
  ├─ Technical Details
  ├─ Acceptance Criteria (AC-1, AC-2, ...)
  ├─ Dependencies
  ├─ Affected Components
  └─ Estimated Story Points

Work Item Type: Product Backlog Item
Custom Fields:
  ├─ PBIType: Enabler
  ├─ TechnicalDetails: [technical description]
  └─ Tags: enabler, technical, [requirement tags]

Story Points: Auto-calculated (3-13)
Priority: Mapped from requirement (P1=Critical, P2=High, P3=Medium)
```

### Feature PBI Format

```
Title: [Feature] Audit trail dashboard

Description:
  ├─ User Story ("As a... I want... so that...")
  ├─ Description
  ├─ Business Value
  ├─ User Personas
  ├─ Acceptance Criteria (AC-1, AC-2, ...)
  ├─ Dependencies
  └─ Estimated Story Points

Work Item Type: Product Backlog Item
Custom Fields:
  ├─ PBIType: Feature
  ├─ BusinessValue: [business value]
  ├─ UserPersonas: [persona1, persona2]
  └─ Tags: feature, user-facing, [requirement tags]

Story Points: Auto-calculated (3-13)
Priority: Mapped from requirement
```

### Child Tasks (with --with-tasks)

For each Acceptance Criterion, generates a Task:

```
Title: Implement AC-1: [AC summary]

Description:
  ├─ Given: [condition]
  ├─ When: [action]
  ├─ Then: [expected result]
  └─ Verification: [test/job/query/manual]

Work Item Type: Task
Story Points: 1-3 (based on complexity)
Linked to: Parent PBI
```

---

## Story Points Estimation

### PBI Story Points

**Formula:**
```
Base: 3 points
+ 1 per acceptance criterion
+ 2 if > 5 functional requirements
+ 1 if demo required
+ 1 per Databricks object (max 3)
= Total (capped at 13)
```

**Examples:**

| Scenario | Calculation | Total |
|----------|-------------|-------|
| Simple API endpoint | 3 + 2 ACs + 0 + 0 + 0 | **5 points** |
| Complex dashboard | 3 + 5 ACs + 2 (>5 FRs) + 1 (demo) + 2 (objects) | **13 points** |
| Test framework | 3 + 3 ACs + 2 (>5 FRs) + 0 + 1 (object) | **9 points** |

### Task Story Points

**Formula:**
```
Base: 1 point
+ 0.5 for automated test verification
+ 1.0 for Databricks job verification
+ 0.5 for SQL query verification
+ 1.0 for manual verification
+ 0.5 if demo evidence required
= Total (capped at 3)
```

---

## Example Workflows

### Workflow 1: Generate PBI for Test Automation Enabler

```bash
# 1. Create requirement file for test automation
cat > requirements/REQ-TEST-001.md << 'EOF'
---
req_id: REQ-TEST-001
title: Automated testing framework for Your Project
owner: test.engineer@company.com
product: Your Project
team: Platform Engineering
priority: P1
status: In Dev
target_release: v1.0.0
created: 2026-01-05
updated: 2026-01-05

links:
  ado: null
---

## 1. Problem statement

We need a comprehensive automated testing framework for Your Project to ensure quality and enable CI/CD.

## 4. Functional requirements

- Pytest framework with Databricks fixtures
- Unit tests for all Python modules
- Integration tests with test Unity Catalog
- CI pipeline integration
- Code coverage reporting
- Mock data generators

## 5. Acceptance criteria

### AC-1
**Given** a test catalog exists
**When** tests are executed
**Then** all tests use isolated test data
**Verify:**
- test: tests/test_framework.py::test_catalog_isolation

### AC-2
**Given** code changes are committed
**When** CI pipeline runs
**Then** all tests pass with >80% coverage
**Verify:**
- job: bundle_run: ci_test_job
EOF

# 2. Generate Enabler PBI with tasks
python -m ai_sdlc.cli.pbi_commands generate-pbis requirements/REQ-TEST-001.md --with-tasks

# Output:
# ✅ Created Enabler PBI:
#    ID: 12351
#    Title: [Enabler] Automated testing framework for Your Project
#    URL: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12351
#
#    📋 Generating child tasks...
#    ✅ Created 2 tasks
#       - Task 12352: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12352
#       - Task 12353: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12353
```

### Workflow 2: Generate PBI for Audit Dashboard Feature

```bash
# 1. Create requirement file for dashboard
cat > requirements/REQ-DASH-001.md << 'EOF'
---
req_id: REQ-DASH-001
title: Audit trail dashboard for compliance team
owner: product.manager@company.com
product: Your Project
team: Data Products
priority: P1
status: Approved
target_release: v1.0.0
created: 2026-01-05
updated: 2026-01-05
---

## 1. Problem statement

Compliance officers need a centralized dashboard to view and analyze audit trails for regulatory compliance.

## 2. Personas and users

- Compliance Officer: Reviews audit activities daily
- Auditor: Investigates specific audit events
- Security Admin: Monitors security-related audits

## 5. Acceptance criteria

### AC-1
**Given** I am a compliance officer
**When** I open the dashboard
**Then** I see audit events from last 30 days
**Verify:**
- test: tests/test_dashboard.py::test_date_range

### AC-2
**Given** audit events are displayed
**When** I apply filters (user, event type, date)
**Then** only matching events are shown
**Verify:**
- test: tests/test_dashboard.py::test_filtering

### AC-3
**Given** filtered audit events
**When** I click Export to PDF
**Then** a PDF report is generated
**Verify:**
- manual: screenshot
EOF

# 2. Generate Feature PBI with tasks
python -m ai_sdlc.cli.pbi_commands generate-pbis requirements/REQ-DASH-001.md --with-tasks

# Output:
# ✅ Created Feature PBI:
#    ID: 12354
#    Title: [Feature] Audit trail dashboard for compliance team
#    URL: https://dev.azure.com/your-organization/YourProject/_workitems/edit/12354
#
#    📋 Generating child tasks...
#    ✅ Created 3 tasks
#       - Task 6340204: Implement AC-1 (2.0 points)
#       - Task 6340205: Implement AC-2 (1.5 points)
#       - Task 6340206: Implement AC-3 (2.0 points)
```

### Workflow 3: Batch Generate for Your Project

```bash
# Generate PBIs for all requirements in Your Project
python -m ai_sdlc.cli.pbi_commands batch-generate requirements/ --with-tasks --output audit-cortex-pbis.md

# Output:
# 🔧 Found 15 requirement files
#
# 📄 Processing REQ-TEST-001: Automated testing framework
#    ✅ Created Enabler PBI 12351
#       📋 Created 2 tasks
#
# 📄 Processing REQ-DASH-001: Audit trail dashboard
#    ✅ Created Feature PBI 12354
#       📋 Created 3 tasks
#
# 📄 Processing REQ-API-001: Audit API endpoints
#    ✅ Created Enabler PBI 6340206
#       📋 Created 4 tasks
#
# ...
#
# 📊 Summary: 15/15 PBIs created
# 📝 Report written to: audit-cortex-pbis.md
```

---

## Integration with Your Project Wiki

The PBI generation system integrates with your Your Project wiki structure:

**Wiki Reference:** [Your Design Document](https://dev.azure.com/your-organization/YourProject/_wiki/wikis/YourProject.wiki/100001/YourFeature-automated-Unit-and-Integration-test-design)

### Linking PBIs to Wiki Pages

1. **Generate PBI** from requirement
2. **Get PBI URL** from output
3. **Add PBI link** to wiki page:
   ```markdown
   ## Related Work Items
   - [[12345]] - Automated Unit and Integration Test Design
   - [[12351]] - Automated Testing Framework
   ```

### Referencing Wiki in PBIs

Add wiki references to PBI descriptions:

```python
# In custom PBI generation
description = f"""
Build automated testing framework for Your Project.

Reference: https://dev.azure.com/your-organization/YourProject/_wiki/wikis/YourProject.wiki/100001/YourFeature-automated-Unit-and-Integration-test-design
"""
```

---

## Python API Usage

### Generate PBIs Programmatically

```python
from ai_sdlc.generators import PBIGenerator, PBIType, EnablerPBI, FeaturePBI
from ai_sdlc.parsers.requirement_parser import RequirementParser
from plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import AzureDevOpsPlugin
from plugins.databricks_devops_integrations.sdk.base_plugin import PluginConfig, WorkItemPriority

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

# Generate from requirement
req_parser = RequirementParser()
requirement = req_parser.parse_file("requirements/REQ-TEST-001.md")

# Auto-detect and generate
results = pbi_generator.generate_from_requirement(requirement, auto_detect=True)

for result in results:
    print(f"Created {result.pbi_type.value} PBI: {result.work_item_url}")

    # Generate child tasks
    if result.success:
        task_ids = pbi_generator.generate_child_tasks(result.work_item_id, requirement)
        print(f"  Created {len(task_ids)} tasks")
```

### Create Custom Enabler for Your Project

```python
# Create custom Enabler PBI
enabler = EnablerPBI(
    title="Set up audit log ingestion pipeline",
    description="Build real-time pipeline to ingest audit logs from multiple sources",
    technical_details="Use Delta Live Tables with autoloader, Unity Catalog for governance",
    acceptance_criteria=[
        "Pipeline ingests from Azure Event Hub",
        "Data lands in Bronze layer (raw)",
        "Silver layer applies transformations",
        "Gold layer aggregates for reporting",
        "All tables in Unity Catalog audit schema"
    ],
    dependencies=[
        "Unity Catalog must be configured",
        "Event Hub connection established"
    ],
    affected_components=["audit_bronze", "audit_silver", "audit_gold"],
    story_points=13.0,
    priority=WorkItemPriority.CRITICAL,
    tags=["audit-cortex", "data-pipeline", "dlt"]
)

result = pbi_generator.generate_enabler_pbi(enabler)
print(f"Created: {result.work_item_url}")
```

### Create Custom Feature for Your Project

```python
# Create custom Feature PBI
feature = FeaturePBI(
    title="Compliance report generation",
    description="Automated generation of compliance reports from audit data",
    user_story="As a compliance officer, I want to generate monthly compliance reports so that I can submit regulatory filings",
    acceptance_criteria=[
        "Generate report for selected date range",
        "Include all audit events by category",
        "Export to PDF and Excel formats",
        "Email report to stakeholders",
        "Schedule recurring reports"
    ],
    business_value="Reduces manual report generation time from 2 days to 5 minutes",
    user_personas=["Compliance Officer", "Regulatory Affairs Manager"],
    dependencies=["Dashboard must be implemented first"],
    story_points=8.0,
    priority=WorkItemPriority.HIGH,
    tags=["audit-cortex", "compliance", "reporting"]
)

result = pbi_generator.generate_feature_pbi(feature)
print(f"Created: {result.work_item_url}")
```

---

## Best Practices for Your Project

### 1. Use Consistent Naming Convention

```
Enablers: [Enabler] {Technical Component} for Your Project
Features: [Feature] {User Capability} for compliance/auditing

Examples:
- [Enabler] Automated testing framework for Your Project
- [Feature] Audit trail dashboard for compliance team
```

### 2. Tag All PBIs with Project Identifier

```python
tags=["audit-cortex", "compliance", ...]
```

### 3. Link to Wiki Documentation

Include wiki references in PBI descriptions:
```
Reference: https://dev.azure.com/your-organization/YourProject/_wiki/wikis/YourProject.wiki/...
```

### 4. Generate Tasks for All ACs

Always use `--with-tasks` to create granular tasks:
```bash
python -m ai_sdlc.cli.pbi_commands generate-pbis REQ-001.md --with-tasks
```

### 5. Use Batch Generation for Sprints

```bash
# Generate all PBIs for upcoming sprint
python -m ai_sdlc.cli.pbi_commands batch-generate requirements/sprint-4/ --with-tasks --output sprint-4-pbis.md
```

---

## Troubleshooting

### Issue: "Auto-detection creates wrong PBI type"

**Solution:** Force PBI type explicitly
```bash
python -m ai_sdlc.cli.pbi_commands generate-pbis REQ-001.md --type enabler
```

### Issue: "Story points seem incorrect"

**Solution:** Override with custom PBI:
```bash
python -m ai_sdlc.cli.pbi_commands generate-enabler --title "..." --story-points 8
```

### Issue: "Task generation fails"

**Solution:** Ensure acceptance criteria follow Given/When/Then format and include verification

### Issue: "Custom fields not appearing in ADO"

**Solution:** Create custom fields in Azure DevOps:
1. Project Settings → Work → Process
2. Add custom fields: `PBIType`, `TechnicalDetails`, `BusinessValue`, `UserPersonas`

---

## CI/CD Integration

### GitHub Actions for Your Project

```yaml
name: Generate PBIs - Your Project

on:
  push:
    paths:
      - 'requirements/REQ-*.md'

jobs:
  generate-pbis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install azure-devops PyYAML

      - name: Generate PBIs
        env:
          AZURE_DEVOPS_ORG_URL: https://dev.azure.com/your-organization
          AZURE_DEVOPS_PAT: ${{ secrets.AZURE_DEVOPS_PAT }}
          AZURE_DEVOPS_PROJECT: Your Project
        run: |
          git diff --name-only HEAD~1 HEAD | grep 'requirements/REQ-.*\.md' | while read req; do
            echo "Generating PBI for $req..."
            python -m ai_sdlc.cli.pbi_commands generate-pbis "$req" --with-tasks
          done
```

---

## Related Documentation

- [ADO Requirement Integration](ADO-REQUIREMENT-INTEGRATION.md)
- [API Reference](api-reference.md)
- [Requirement Parser](api-reference.md#requirement-parser)
- [Azure DevOps Plugin](api-reference.md#azure-devops-plugin)

---

**Project:** Your Project
**Organization:** your-organization
**Contact:** data-platform@vivekgana.com
