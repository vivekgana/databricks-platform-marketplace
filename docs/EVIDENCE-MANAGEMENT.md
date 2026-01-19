# AI-SDLC Evidence Management Guide

**Document Version:** 1.0
**Last Updated:** 2026-01-17
**Prepared by:** AI-SDLC Platform Team

---

## Table of Contents

1. [Overview](#overview)
2. [Evidence Architecture](#evidence-architecture)
3. [Evidence Categories](#evidence-categories)
4. [Evidence Collection](#evidence-collection)
5. [Azure Blob Storage](#azure-blob-storage)
6. [Evidence Formatting](#evidence-formatting)
7. [Screenshot Management](#screenshot-management)
8. [ADO Integration](#ado-integration)
9. [Best Practices](#best-practices)
10. [Reference](#reference)

---

## Overview

### What is Evidence Management?

The AI-SDLC Evidence Management system provides a comprehensive audit trail of all workflow activities. Evidence includes:

- Implementation plans
- Generated code
- Test results and coverage reports
- Screenshots from QA testing
- Performance metrics
- Integration test results
- Summary reports

### Why Evidence Matters

**Compliance & Audit:**
- Complete audit trail for regulatory compliance
- Traceable decision-making process
- Verification of quality standards

**Quality Assurance:**
- Proof that tests were run
- Visual evidence of functionality
- Performance benchmarks

**Knowledge Transfer:**
- Documentation for future maintainers
- Examples of AI-generated artifacts
- Historical record of development

---

## Evidence Architecture

### Component Overview

```
Evidence Management System
├── EvidenceCollector
│   ├── Collects artifacts from all stages
│   ├── Categorizes by type
│   ├── Tracks metadata
│   └── Generates summaries
├── EvidenceStorage
│   ├── AzureBlobEvidenceStorage
│   │   ├── Upload to Azure Blob
│   │   ├── Generate SAS URLs
│   │   └── List and retrieve files
│   └── LocalFileEvidenceStorage
│       ├── Store to local filesystem
│       └── Organize by structure
├── EvidenceFormatter
│   ├── Format for ADO comments (HTML/Markdown)
│   ├── Generate summary reports
│   └── Create evidence catalogs
└── ScreenshotManager
    ├── Compress screenshots
    ├── Select top screenshots
    └── Manage screenshot metadata
```

### Evidence Flow

```
Agent executes
    ↓
Agent produces artifacts
    ├─ Code files
    ├─ Test results
    ├─ Screenshots
    ├─ Reports
    └─ Logs
    ↓
EvidenceCollector collects artifacts
    ├─ Categorize by type
    ├─ Add metadata
    └─ Track in inventory
    ↓
EvidenceStorage uploads to Azure Blob
    ├─ Organize by work_item_id/stage/
    ├─ Generate unique paths
    └─ Store metadata
    ↓
EvidenceFormatter creates summaries
    ├─ Stage-specific comments
    ├─ Workflow summary
    └─ Evidence catalog
    ↓
ADO Integration updates work item
    ├─ Add rich comments
    ├─ Upload top 3 attachments
    └─ Update custom fields
```

---

## Evidence Architecture

### Evidence Storage Structure

All evidence is organized in Azure Blob Storage:

```
Container: audit-cortex-evidence
├── PBI-6340168/
│   ├── planning/
│   │   ├── implementation-plan.md
│   │   ├── requirements-analysis.json
│   │   └── metadata.json
│   ├── code_generation/
│   │   ├── audit_service.py
│   │   ├── audit_service_spark.py
│   │   ├── queries.sql
│   │   ├── code-quality-report.json
│   │   └── metadata.json
│   ├── unit_testing/
│   │   ├── test_audit_service.py
│   │   ├── test_audit_service_spark.py
│   │   ├── coverage.json
│   │   ├── pytest-report.html
│   │   ├── test-execution.log
│   │   └── metadata.json
│   ├── qa_testing/
│   │   ├── playwright_tests.py
│   │   ├── screenshots/
│   │   │   ├── dashboard-home.png
│   │   │   ├── dashboard-filters.png
│   │   │   ├── dashboard-export.png
│   │   │   ├── dashboard-navigation.png
│   │   │   └── dashboard-error-handling.png
│   │   ├── playwright-report.html
│   │   ├── console-logs.txt
│   │   └── metadata.json
│   ├── integration_testing/
│   │   ├── integration_tests.py
│   │   ├── api-test-results.json
│   │   ├── db-integration-results.json
│   │   ├── integration-report.html
│   │   └── metadata.json
│   ├── performance_testing/
│   │   ├── load_tests.py
│   │   ├── performance-metrics.json
│   │   ├── load-test-report.html
│   │   └── metadata.json
│   └── evidence_collection/
│       ├── summary.md
│       ├── evidence-catalog.json
│       └── metadata.json
```

### Metadata Structure

Each evidence item includes metadata:

```json
{
  "evidence_id": "PBI-6340168/qa_testing/screenshots/dashboard-home.png",
  "work_item_id": "6340168",
  "stage": "qa_testing",
  "category": "screenshot",
  "filename": "dashboard-home.png",
  "description": "Main dashboard homepage",
  "size_bytes": 245678,
  "mime_type": "image/png",
  "created_at": "2026-01-17T10:30:45Z",
  "uploaded_at": "2026-01-17T10:31:02Z",
  "storage_url": "https://storage.blob.core.windows.net/audit-cortex-evidence/PBI-6340168/qa_testing/screenshots/dashboard-home.png",
  "checksum": "sha256:abc123...",
  "metadata": {
    "resolution": "1920x1080",
    "browser": "chromium",
    "viewport": "desktop"
  }
}
```

---

## Evidence Categories

### EvidenceCategory Enum

```python
from enum import Enum

class EvidenceCategory(Enum):
    """Categories of evidence artifacts."""
    PLAN = "plan"
    CODE = "code"
    TEST = "test"
    SCREENSHOT = "screenshot"
    REPORT = "report"
    LOG = "log"
    DATA = "data"
    DOCUMENTATION = "documentation"
```

### Category Descriptions

| Category | Description | Examples |
|----------|-------------|----------|
| PLAN | Implementation plans and specifications | implementation-plan.md, requirements-analysis.json |
| CODE | Generated source code | *.py, *.sql, *.scala |
| TEST | Test files and test data | test_*.py, fixtures/, mocks/ |
| SCREENSHOT | UI screenshots from testing | *.png, *.jpg |
| REPORT | Test reports and summaries | pytest-report.html, coverage.html |
| LOG | Execution logs and traces | test-execution.log, console-logs.txt |
| DATA | Test data and sample datasets | sample-data.json, test-dataset.csv |
| DOCUMENTATION | Generated documentation | README.md, API-DOCS.md |

### Category Usage by Stage

| Stage | Primary Categories |
|-------|-------------------|
| Planning | PLAN, DOCUMENTATION |
| Code Generation | CODE, REPORT |
| Unit Testing | TEST, REPORT, LOG |
| QA Testing | TEST, SCREENSHOT, REPORT, LOG |
| Integration Testing | TEST, REPORT, LOG, DATA |
| Performance Testing | REPORT, LOG, DATA |
| Evidence Collection | REPORT, DOCUMENTATION |

---

## Evidence Collection

### EvidenceCollector Class

The `EvidenceCollector` manages evidence throughout the workflow:

```python
from ai_sdlc.evidence import EvidenceCollector, EvidenceCategory

# Initialize collector
collector = EvidenceCollector(
    work_item_id="6340168",
    base_path="azure-blob://audit-cortex-evidence"
)

# Add evidence items
collector.add_evidence(
    path="/path/to/implementation-plan.md",
    category=EvidenceCategory.PLAN,
    stage="planning",
    description="Implementation plan for audit dashboard"
)

# Add screenshot
collector.add_screenshot(
    path="/path/to/dashboard-home.png",
    stage="qa_testing",
    description="Dashboard homepage screenshot"
)

# Add report
collector.add_report(
    path="/path/to/pytest-report.html",
    stage="unit_testing",
    description="Unit test execution report"
)

# Get evidence by category
screenshots = collector.get_screenshots()
reports = collector.get_reports()

# Get evidence by stage
qa_evidence = collector.get_evidence_by_stage("qa_testing")

# Get summary
summary = collector.get_summary()
# {
#     "work_item_id": "6340168",
#     "total_items": 23,
#     "by_category": {
#         "screenshot": 5,
#         "report": 7,
#         "code": 4,
#         ...
#     },
#     "by_stage": {
#         "planning": 2,
#         "code_generation": 4,
#         "unit_testing": 5,
#         ...
#     },
#     "total_size_bytes": 5242880,
#     "screenshots_count": 5,
#     "reports_count": 7
# }

# Export metadata
metadata = collector.export_metadata()
```

### EvidenceItem Structure

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EvidenceItem:
    """Represents a single evidence artifact."""
    path: str                      # File path
    category: EvidenceCategory     # Evidence category
    stage: str                     # Workflow stage
    filename: str                  # File name
    description: Optional[str]     # Description
    size_bytes: Optional[int]      # File size
    created_at: datetime           # Creation timestamp
    metadata: Dict[str, Any]       # Additional metadata

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "path": self.path,
            "category": self.category.value,
            "stage": self.stage,
            "filename": self.filename,
            "description": self.description,
            "size_bytes": self.size_bytes,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }
```

---

## Azure Blob Storage

### AzureBlobEvidenceStorage

The primary storage backend for production:

```python
from ai_sdlc.evidence import AzureBlobEvidenceStorage

# Initialize with connection string
storage = AzureBlobEvidenceStorage(
    container_name="audit-cortex-evidence",
    connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING")
)

# OR initialize with account name/key
storage = AzureBlobEvidenceStorage(
    container_name="audit-cortex-evidence",
    account_name=os.getenv("AZURE_STORAGE_ACCOUNT_NAME"),
    account_key=os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
)

# Upload file
url = storage.upload_file(
    local_path="/path/to/file.py",
    remote_path="PBI-6340168/code_generation/audit_service.py",
    metadata={
        "work_item_id": "6340168",
        "stage": "code_generation",
        "category": "code"
    }
)

# Download file
storage.download_file(
    remote_path="PBI-6340168/code_generation/audit_service.py",
    local_path="./downloaded_audit_service.py"
)

# List files with prefix
files = storage.list_files(prefix="PBI-6340168/qa_testing/screenshots/")
# ['PBI-6340168/qa_testing/screenshots/dashboard-home.png',
#  'PBI-6340168/qa_testing/screenshots/dashboard-filters.png', ...]

# Get file URL
url = storage.get_file_url("PBI-6340168/code_generation/audit_service.py")

# Generate SAS URL for temporary access (24 hours)
sas_url = storage.generate_sas_url(
    remote_path="PBI-6340168/qa_testing/screenshots/dashboard-home.png",
    expiry_hours=24
)

# Delete file
storage.delete_file("PBI-6340168/old_file.txt")
```

### Configuration

**Environment Variables:**
```bash
# Option 1: Connection string (recommended)
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"

# Option 2: Account name + key
export AZURE_STORAGE_ACCOUNT_NAME="mystorageaccount"
export AZURE_STORAGE_ACCOUNT_KEY="abc123..."

# Container name (optional, defaults to audit-cortex-evidence)
export EVIDENCE_CONTAINER="audit-cortex-evidence"
```

### Access Control

**Container must allow:**
- Blob read/write access for service principal
- Optional: Public read access for attachments (not recommended)
- Recommended: Use SAS URLs for temporary read access

**IAM Roles:**
- Storage Blob Data Contributor (for workflow service)
- Storage Blob Data Reader (for read-only access)

---

## Evidence Formatting

### EvidenceFormatter Class

Formats evidence for presentation in Azure DevOps:

```python
from ai_sdlc.evidence import EvidenceFormatter, ADOCommentFormat

# Initialize formatter
formatter = EvidenceFormatter(work_item_id="6340168")

# Format stage comment (Markdown)
comment_md = formatter.format_stage_comment(
    stage="unit_testing",
    status="passed",
    duration_seconds=12.5,
    evidence_items=evidence_items,
    metrics={"coverage": 85.5, "tests_passed": 42},
    format_type=ADOCommentFormat.MARKDOWN
)

# Format stage comment (HTML)
comment_html = formatter.format_stage_comment(
    stage="unit_testing",
    status="passed",
    duration_seconds=12.5,
    evidence_items=evidence_items,
    metrics={"coverage": 85.5, "tests_passed": 42},
    format_type=ADOCommentFormat.HTML
)

# Format workflow summary
summary_md = formatter.format_workflow_summary(
    collector=collector,
    stage_results=stage_results,
    format_type=ADOCommentFormat.MARKDOWN
)
```

### Format Types

**ADOCommentFormat.MARKDOWN** - GitHub-flavored Markdown:
```markdown
## ✅ Stage: Unit Testing

**Status:** PASSED
**Duration:** 12.5s
**Timestamp:** 2026-01-17 10:30:45

### Metrics

- **Test Coverage:** 85.5%
- **Tests Passed:** 42

### Evidence (5 files)

**Test:**
- `test_audit_service.py` - Unit test suite
- `test_audit_service_spark.py` - PySpark unit tests

**Report:**
- `coverage.json` - Coverage report
- `pytest-report.html` - Test execution report

---
*Generated by AI-SDLC Workflow Orchestrator*
```

**ADOCommentFormat.HTML** - Rich HTML:
```html
<div style="border: 1px solid #ddd; border-radius: 5px; padding: 15px; background: #f9f9f9;">
    <h3 style="color: #4CAF50;">✅ Unit Testing</h3>
    <table style="width: 100%;">
        <tr>
            <td><strong>Status:</strong></td>
            <td style="color: #4CAF50;">PASSED</td>
        </tr>
        <tr>
            <td><strong>Duration:</strong></td>
            <td>12.5s</td>
        </tr>
    </table>
    <h4>Metrics</h4>
    <ul>
        <li><strong>Test Coverage:</strong> 85.5%</li>
        <li><strong>Tests Passed:</strong> 42</li>
    </ul>
    <h4>Evidence (5 files)</h4>
    <ul>
        <li><code>test_audit_service.py</code> - Unit test suite</li>
        <li><code>coverage.json</code> - Coverage report</li>
    </ul>
    <p style="color: #666;"><em>Generated by AI-SDLC Workflow Orchestrator</em></p>
</div>
```

**ADOCommentFormat.PLAIN_TEXT** - Plain text:
```
[PASS] Stage: Unit Testing

Status: PASSED
Duration: 12.5s
Timestamp: 2026-01-17 10:30:45

Metrics:
  - Test Coverage: 85.5%
  - Tests Passed: 42

Evidence (5 files):
  - test_audit_service.py - Unit test suite
  - coverage.json - Coverage report

---
Generated by AI-SDLC Workflow Orchestrator
```

---

## Screenshot Management

### ScreenshotManager Class

Manages screenshot evidence with compression and selection:

```python
from ai_sdlc.evidence import ScreenshotManager

manager = ScreenshotManager()

# Compress screenshot (PNG optimization)
compressed_path = manager.compress_screenshot(
    input_path="/path/to/large-screenshot.png",
    output_path="/path/to/compressed-screenshot.png",
    max_size_kb=500  # Target max 500KB
)

# Select top screenshots (for ADO attachment)
screenshots = [
    {
        "filename": "dashboard-home.png",
        "path": "/path/to/dashboard-home.png",
        "size_bytes": 245678,
        "description": "Main dashboard"
    },
    {
        "filename": "dashboard-filters.png",
        "path": "/path/to/dashboard-filters.png",
        "size_bytes": 198765,
        "description": "Filter panel"
    },
    {
        "filename": "error-page.png",
        "path": "/path/to/error-page.png",
        "size_bytes": 156789,
        "description": "Error handling"
    },
    # ... more screenshots
]

# Select top 3 most important screenshots
top_screenshots = manager.select_top_screenshots(
    screenshots=screenshots,
    max_count=3
)

# Selection criteria:
# - Priority keywords: "dashboard", "home", "main", "error", "result"
# - File size (larger = more detail)
# - Balanced selection across different areas
```

### Screenshot Priorities

Screenshots are prioritized based on keywords:

| Priority | Keywords |
|----------|----------|
| High (10 points) | dashboard, home, main, error, result |
| Medium (7 points) | filter, search, form, table |
| Normal (5 points) | navigation, menu, settings |
| Low (3 points) | footer, header, sidebar |

### Screenshot Best Practices

1. **Capture key user flows** - Login, main operations, error states
2. **Use descriptive filenames** - `dashboard-home.png` not `screenshot1.png`
3. **Full page screenshots** - Use `full_page=True` in Playwright
4. **Consistent resolution** - Use 1920x1080 viewport
5. **Compress large files** - Target < 500KB per screenshot
6. **Annotate if needed** - Add arrows/boxes to highlight areas

---

## ADO Integration

### Updating Work Items with Evidence

```python
from plugins.databricks_devops_integrations.integrations.azure_devops import AzureDevOpsPlugin

# Initialize ADO plugin
ado_plugin = AzureDevOpsPlugin()
ado_plugin.authenticate(config)

# Add rich comment with stage results
ado_plugin.add_rich_comment(
    work_item_id="6340168",
    html_content=formatted_comment_html,
    config=config
)

# Update work item with evidence summary
ado_plugin.update_work_item_with_evidence(
    work_item_id="6340168",
    evidence_summary={
        "evidence_items": collector.get_evidence_by_stage("unit_testing"),
        "metrics": {"coverage": 85.5, "tests_passed": 42},
        "duration_seconds": 12.5
    },
    stage="unit_testing",
    status="passed",
    config=config
)

# Upload evidence package (top 3 screenshots/reports)
result = ado_plugin.upload_evidence_package(
    work_item_id="6340168",
    evidence_items=collector.get_all_evidence(),
    max_attachments=3,
    config=config
)

# result = {
#     "uploaded_count": 3,
#     "uploaded_urls": ["https://...", "https://...", "https://..."],
#     "skipped_count": 20
# }
```

### Evidence in ADO Work Items

**What Gets Uploaded:**

1. **Comments:**
   - Rich HTML comments for each stage
   - Workflow summary with all stages
   - Evidence catalog with file list

2. **Attachments (Top 3):**
   - Priority: Screenshots from QA testing
   - Fallback: Reports (coverage, performance)
   - Selected using ScreenshotManager

3. **Custom Fields:**
   - `Custom.LastWorkflowStage` - Last executed stage
   - `Custom.LastWorkflowStatus` - Stage status (passed/failed)
   - `Custom.LastWorkflowUpdate` - Timestamp

**Example ADO Work Item After Workflow:**

```
Work Item #6340168: Implement Audit Dashboard

State: Done
Assigned To: AI-SDLC System

History:
├─ [2026-01-17 10:15] ✅ Stage: Planning (12.3s)
│  Metrics: Requirements covered: 8/8, Risks identified: 3
│  Evidence: implementation-plan.md, requirements-analysis.json
│
├─ [2026-01-17 10:18] ✅ Stage: Code Generation (45.7s)
│  Metrics: Files generated: 4, Code quality: 0.92
│  Evidence: audit_service.py, audit_service_spark.py, queries.sql
│
├─ [2026-01-17 10:22] ✅ Stage: Unit Testing (12.5s)
│  Metrics: Coverage: 85.5%, Tests passed: 42/42
│  Evidence: test_audit_service.py, coverage.json, pytest-report.html
│
├─ [2026-01-17 10:30] ✅ Stage: QA Testing (67.2s)
│  Metrics: UI tests passed: 15/15, Screenshots: 5
│  Evidence: playwright_tests.py, screenshots/, playwright-report.html
│
├─ [2026-01-17 10:35] ✅ Stage: Integration Testing (34.8s)
│  Metrics: API tests passed: 8/8, DB tests passed: 6/6
│  Evidence: integration_tests.py, api-test-results.json
│
├─ [2026-01-17 10:40] ✅ Stage: Performance Testing (89.5s)
│  Metrics: Max response time: 1250ms, Success rate: 98.5%
│  Evidence: load_tests.py, performance-metrics.json
│
└─ [2026-01-17 10:42] ✅ Stage: Evidence Collection (8.3s)
   Total evidence: 23 files (5.0 MB)
   Storage: azure-blob://audit-cortex-evidence/PBI-6340168/

Attachments:
📎 dashboard-home.png (245 KB)
📎 dashboard-filters.png (198 KB)
📎 coverage.json (12 KB)

Custom Fields:
- Last Workflow Stage: evidence_collection
- Last Workflow Status: passed
- Last Workflow Update: 2026-01-17T10:42:15Z
```

---

## Best Practices

### 1. Evidence Organization

- **Consistent structure** - Follow standard directory layout
- **Descriptive names** - Use clear, meaningful filenames
- **Complete metadata** - Include all relevant context
- **Proper categorization** - Use appropriate EvidenceCategory

### 2. Storage Management

- **Compression** - Compress large files before upload
- **Retention policy** - Clean up old evidence (30-90 days)
- **Access control** - Use SAS URLs for temporary access
- **Backup** - Ensure Azure Blob has geo-redundancy

### 3. Screenshot Quality

- **High resolution** - Use 1920x1080 or higher
- **Full page** - Capture entire page, not just viewport
- **Meaningful captures** - Show key functionality
- **Compress** - Optimize file size without losing quality

### 4. Evidence Completeness

- **Every stage** - Capture evidence at each workflow stage
- **Key artifacts** - Ensure critical files are saved
- **Execution logs** - Include logs for debugging
- **Metadata** - Document context and configuration

### 5. ADO Integration

- **Rich formatting** - Use HTML for better readability
- **Top attachments** - Upload most important evidence
- **Stage comments** - Add comment after each stage
- **Summary** - Provide complete workflow summary

---

## Reference

### Complete Evidence Workflow Example

```python
"""
Complete evidence workflow example.
"""

from ai_sdlc.evidence import (
    EvidenceCollector,
    EvidenceCategory,
    AzureBlobEvidenceStorage,
    EvidenceFormatter,
    ADOCommentFormat,
    ScreenshotManager
)
from plugins.databricks_devops_integrations.integrations.azure_devops import AzureDevOpsPlugin

# 1. Initialize components
work_item_id = "6340168"
collector = EvidenceCollector(
    work_item_id=work_item_id,
    base_path="azure-blob://audit-cortex-evidence"
)

storage = AzureBlobEvidenceStorage(container_name="audit-cortex-evidence")
formatter = EvidenceFormatter(work_item_id)
screenshot_manager = ScreenshotManager()
ado_plugin = AzureDevOpsPlugin()

# 2. Collect evidence from workflow stages
# Planning stage
collector.add_evidence(
    path="./evidence/planning/implementation-plan.md",
    category=EvidenceCategory.PLAN,
    stage="planning",
    description="Implementation plan"
)

# Code generation stage
collector.add_evidence(
    path="./evidence/code_generation/audit_service.py",
    category=EvidenceCategory.CODE,
    stage="code_generation",
    description="Generated Python service"
)

# QA testing stage
for screenshot_file in ["dashboard-home.png", "dashboard-filters.png"]:
    collector.add_screenshot(
        path=f"./evidence/qa_testing/screenshots/{screenshot_file}",
        stage="qa_testing",
        description=f"Screenshot: {screenshot_file}"
    )

# 3. Upload evidence to Azure Blob Storage
for evidence_item in collector.get_all_evidence():
    storage.upload_file(
        local_path=evidence_item.path,
        remote_path=f"{work_item_id}/{evidence_item.stage}/{evidence_item.filename}",
        metadata={
            "work_item_id": work_item_id,
            "stage": evidence_item.stage,
            "category": evidence_item.category.value,
        }
    )

# 4. Format evidence for ADO
stage_comment = formatter.format_stage_comment(
    stage="qa_testing",
    status="passed",
    duration_seconds=67.2,
    evidence_items=collector.get_evidence_by_stage("qa_testing"),
    metrics={"ui_tests_passed": 15, "screenshots": 5},
    format_type=ADOCommentFormat.HTML
)

workflow_summary = formatter.format_workflow_summary(
    collector=collector,
    stage_results=all_stage_results,
    format_type=ADOCommentFormat.MARKDOWN
)

# 5. Update Azure DevOps work item
ado_plugin.add_rich_comment(work_item_id, stage_comment, config=config)

upload_result = ado_plugin.upload_evidence_package(
    work_item_id=work_item_id,
    evidence_items=collector.get_all_evidence(),
    max_attachments=3,
    config=config
)

print(f"Uploaded {upload_result['uploaded_count']} attachments to ADO")

# 6. Generate final summary
summary = collector.get_summary()
print(f"Total evidence collected: {summary['total_items']} files")
print(f"Total size: {summary['total_size_bytes'] / 1024 / 1024:.2f} MB")
```

---

## Document History

| Version | Date       | Author                | Changes                        |
|---------|------------|-----------------------|--------------------------------|
| 1.0     | 2026-01-17 | AI-SDLC Platform Team | Initial evidence management    |

---

**Need Help?**
- Report issues: [GitHub Issues](https://github.com/your-org/ai-sdlc/issues)
- Slack: #ai-sdlc-support
- Email: ai-sdlc-support@yourcompany.com
