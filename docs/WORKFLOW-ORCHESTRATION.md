# AI-SDLC Workflow Orchestration Guide

**Document Version:** 1.0
**Last Updated:** 2026-01-17
**Prepared by:** AI-SDLC Platform Team

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Workflow Stages](#workflow-stages)
4. [State Management](#state-management)
5. [Running Workflows](#running-workflows)
6. [Evidence Collection](#evidence-collection)
7. [Error Handling and Recovery](#error-handling-and-recovery)
8. [Configuration](#configuration)
9. [Integration with Azure DevOps](#integration-with-azure-devops)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The AI-SDLC Workflow Orchestration system automates the entire software development lifecycle from Azure DevOps work items through code generation, testing, and deployment. Each workflow stage is validated with AI-powered evaluations (evals) before proceeding to the next stage.

### Key Features

- **Multi-stage orchestration** - 7 workflow stages from planning to evidence collection
- **AI-powered agents** - Specialized agents for each development phase
- **Quality gates** - Evaluation framework validates each stage before proceeding
- **Evidence management** - Complete audit trail stored in Azure Blob Storage
- **Azure DevOps integration** - Automatic work item updates with rich comments and attachments
- **Resume capability** - Checkpointing allows workflows to resume after interruptions

### Supported Work Item Types

- Epic
- Feature
- Enabler
- Product Backlog Item (PBI)

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Workflow Orchestrator                    │
│  - Stage execution                                           │
│  - Checkpoint management                                     │
│  - Error handling                                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌─────────┐   ┌────────┐   ┌─────────────┐
│  Agents │   │ Evals  │   │  Evidence   │
│ System  │   │ System │   │  Management │
└─────────┘   └────────┘   └─────────────┘
    │              │              │
    └──────────────┴──────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │ Azure DevOps    │
         │ Integration     │
         └─────────────────┘
```

### Component Overview

**WorkflowOrchestrator**
- Coordinates agent execution across all stages
- Manages workflow state and checkpoints
- Handles error recovery and rollback
- Updates Azure DevOps work items

**Agent System**
- BaseAgent: Abstract base class for all agents
- Specialized agents for each workflow stage
- Evidence collection and storage
- LLM integration for AI-powered operations

**Evaluation Framework**
- Quality gates for each stage
- Configurable pass/fail thresholds
- Detailed scoring and issue reporting
- Blocking vs. non-blocking issues

**Evidence Management**
- Azure Blob Storage integration
- Screenshot capture and management
- Report generation
- ADO attachment upload

---

## Workflow Stages

### Complete Workflow Pipeline

```
1. Planning
   ├─> Implementation plan generation
   ├─> Requirements analysis
   └─> Eval: Plan quality (min score: 0.7)
        │
2. Code Generation
   ├─> Python/PySpark/SQL code generation
   ├─> Code quality report
   └─> Eval: Code quality, standards (min score: 0.7)
        │
3. Unit Testing
   ├─> Test generation
   ├─> Test execution
   ├─> Coverage report (min: 80%)
   └─> Eval: Test coverage, quality (min score: 0.7)
        │
4. QA Testing
   ├─> Playwright UI test generation
   ├─> Screenshot capture
   ├─> UI test execution
   └─> Eval: UI tests pass, evidence (min score: 0.7)
        │
5. Integration Testing
   ├─> API endpoint tests
   ├─> Database integration tests
   ├─> External service mocks
   └─> Eval: Integration pass (min score: 0.7)
        │
6. Performance Testing
   ├─> Load testing
   ├─> Response time validation (< 2s)
   ├─> Resource usage monitoring
   └─> Eval: Performance metrics (min score: 0.7)
        │
7. Evidence Collection
   ├─> Aggregate all artifacts
   ├─> Generate summary report
   ├─> Upload to Azure Blob Storage
   ├─> Update ADO with attachments
   └─> Eval: Completeness (min score: 0.7)
```

### Stage 1: Planning

**Purpose:** Create a detailed implementation plan from work item requirements

**Agent:** PlanningAgent

**Inputs:**
- Work item title and description
- Acceptance criteria
- Existing codebase context

**Outputs:**
- `implementation-plan.md` - Detailed implementation plan
- `requirements-analysis.json` - Parsed requirements

**Evaluation Criteria:**
- Implementation approach is clear
- All requirements are covered
- Risks are identified
- Dependencies are listed
- Score threshold: 0.7

**Example Evidence:**
```
evidence/PBI-12345/planning/
├── implementation-plan.md
└── requirements-analysis.json
```

### Stage 2: Code Generation

**Purpose:** Generate production-quality code in Python, PySpark, or SQL

**Agent:** CodeGeneratorAgent

**Inputs:**
- Implementation plan from Stage 1
- Code templates
- Existing code patterns

**Outputs:**
- Generated source code files
- `code-quality-report.json` - Quality metrics

**Evaluation Criteria:**
- Code passes linting (black, ruff)
- No security vulnerabilities (bandit scan)
- Has docstrings and type hints
- Follows project conventions
- Score threshold: 0.7

**Example Evidence:**
```
evidence/PBI-12345/code_generation/
├── audit_service.py
├── audit_service_spark.py
├── queries.sql
└── code-quality-report.json
```

### Stage 3: Unit Testing

**Purpose:** Generate and execute comprehensive unit tests

**Agent:** TestGeneratorAgent

**Inputs:**
- Generated code from Stage 2
- Test templates
- Code coverage requirements (80% minimum)

**Outputs:**
- Test files (pytest format)
- `coverage.json` - Coverage report (must show ≥ 80%)
- `pytest-report.html` - Test execution results

**Evaluation Criteria:**
- Coverage ≥ 80% (REQUIRED)
- All tests pass
- Tests have meaningful assertions
- Edge cases are covered
- Score threshold: 0.7

**Example Evidence:**
```
evidence/PBI-12345/unit_testing/
├── test_audit_service.py
├── coverage.json
├── pytest-report.html
└── test-execution.log
```

### Stage 4: QA Testing

**Purpose:** Run automated UI tests with screenshot evidence

**Agent:** QAAgent

**Inputs:**
- Application endpoints
- UI test scenarios

**Outputs:**
- `playwright_tests.py` - Generated UI tests
- Screenshots (`.png` files)
- `playwright-report.html` - Test results
- `console-logs.txt` - Browser console logs

**Evaluation Criteria:**
- All UI tests pass
- Screenshots are captured
- No console errors
- UI is responsive
- Score threshold: 0.7

**Example Evidence:**
```
evidence/PBI-12345/qa_testing/
├── playwright_tests.py
├── screenshots/
│   ├── dashboard-home.png
│   ├── dashboard-filters.png
│   └── dashboard-export.png
├── playwright-report.html
└── console-logs.txt
```

### Stage 5: Integration Testing

**Purpose:** Test API endpoints and database operations

**Agent:** IntegrationTestAgent

**Inputs:**
- API specifications
- Database schemas
- External service configurations

**Outputs:**
- `integration_tests.py` - Integration test suite
- `api-test-results.json` - API test results
- `db-integration-results.json` - Database test results
- `integration-report.html` - Summary report

**Evaluation Criteria:**
- API endpoints respond correctly
- Database operations succeed
- External integrations work
- Data validation passes
- Score threshold: 0.7

**Example Evidence:**
```
evidence/PBI-12345/integration_testing/
├── integration_tests.py
├── api-test-results.json
├── db-integration-results.json
└── integration-report.html
```

### Stage 6: Performance Testing

**Purpose:** Validate performance under load

**Agent:** PerformanceTestAgent

**Inputs:**
- Performance requirements (< 2s response time)
- Load test scenarios
- Concurrent user targets

**Outputs:**
- `load_tests.py` - Load test scenarios
- `performance-metrics.json` - Performance data
- `load-test-report.html` - Detailed report

**Evaluation Criteria:**
- Response time < 2s (REQUIRED)
- Success rate ≥ 95%
- No memory leaks
- Handles concurrent load
- Score threshold: 0.7

**Example Evidence:**
```
evidence/PBI-12345/performance_testing/
├── load_tests.py
├── performance-metrics.json
└── load-test-report.html
```

### Stage 7: Evidence Collection

**Purpose:** Aggregate all evidence and update Azure DevOps

**Agent:** EvidenceCollectorAgent

**Inputs:**
- All artifacts from previous stages
- Evidence metadata

**Outputs:**
- `summary.md` - Complete workflow summary
- `metadata.json` - Evidence metadata
- Azure Blob Storage upload confirmation
- ADO work item updates

**Evaluation Criteria:**
- All required artifacts present
- Metadata is complete
- Storage upload successful
- ADO updates successful
- Score threshold: 0.7

**Example Evidence:**
```
evidence/PBI-12345/evidence_collection/
├── summary.md
└── metadata.json
```

---

## State Management

### Workflow States

The orchestrator maintains state throughout workflow execution:

```python
class WorkflowState(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
```

### ADO State Mapping

Workflow stages map to Azure DevOps work item states:

| Workflow Stage          | ADO State       |
|-------------------------|-----------------|
| Planning                | Planning        |
| Code Generation         | In Development  |
| Unit Testing            | In Development  |
| QA Testing              | Testing         |
| Integration Testing     | Testing         |
| Performance Testing     | Testing         |
| Evidence Collection     | Testing         |
| Complete                | Done            |

### Checkpointing

The orchestrator saves checkpoints after each successful stage:

**Checkpoint Location:** `./.workflow_checkpoints/{work_item_id}/`

**Checkpoint Contents:**
- Current stage
- Stage results
- Evidence paths
- Timestamp
- Configuration

**Resume Capability:**
Workflows can be resumed from the last successful checkpoint using:
```bash
python -m ai_sdlc.cli.workflow_commands resume-workflow 12345
```

---

## Running Workflows

### Prerequisites

1. **Environment Variables:**
   ```bash
   export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-org"
   export AZURE_DEVOPS_PAT="your-personal-access-token"
   export AZURE_DEVOPS_PROJECT="Your Project"
   export AZURE_STORAGE_CONNECTION_STRING="your-connection-string"
   ```

2. **Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running Complete Workflow

```bash
python -m ai_sdlc.cli.workflow_commands run-workflow 12345 \
  --evidence-path "azure-blob://audit-cortex-evidence" \
  --checkpoint-dir "./.workflow_checkpoints"
```

**Options:**
- `--evidence-path` - Evidence storage path (Azure Blob or local)
- `--use-local-storage` - Use local filesystem instead of Azure Blob
- `--checkpoint-dir` - Directory for checkpoints (default: `./.workflow_checkpoints`)
- `--continue-on-failure` - Continue even if a stage fails
- `-v, --verbose` - Enable verbose logging

### Running Single Stage

```bash
python -m ai_sdlc.cli.workflow_commands run-stage 12345 code_generation
```

### Validating Stage

Run evaluations on a completed stage:

```bash
python -m ai_sdlc.cli.workflow_commands validate-stage 12345 unit_testing
```

### Listing Work Items

Find work items ready for workflow:

```bash
python -m ai_sdlc.cli.workflow_commands list-work-items --type "Feature"
```

### Resuming Workflow

Resume an interrupted workflow:

```bash
python -m ai_sdlc.cli.workflow_commands resume-workflow 12345
```

---

## Evidence Collection

### Evidence Storage Structure

All evidence is stored in Azure Blob Storage with the following structure:

```
Container: audit-cortex-evidence
├── PBI-{work_item_id}/
│   ├── planning/
│   │   ├── implementation-plan.md
│   │   └── requirements-analysis.json
│   ├── code_generation/
│   │   ├── *.py (generated code)
│   │   └── code-quality-report.json
│   ├── unit_testing/
│   │   ├── test_*.py
│   │   ├── coverage.json
│   │   └── pytest-report.html
│   ├── qa_testing/
│   │   ├── playwright_tests.py
│   │   ├── screenshots/*.png
│   │   └── playwright-report.html
│   ├── integration_testing/
│   │   ├── integration_tests.py
│   │   └── *-results.json
│   ├── performance_testing/
│   │   ├── load_tests.py
│   │   └── performance-metrics.json
│   └── evidence_collection/
│       ├── summary.md
│       └── metadata.json
```

### Evidence Categories

```python
class EvidenceCategory(Enum):
    PLAN = "plan"
    CODE = "code"
    TEST = "test"
    SCREENSHOT = "screenshot"
    REPORT = "report"
    LOG = "log"
    DATA = "data"
    DOCUMENTATION = "documentation"
```

### Evidence Metadata

Each evidence item includes:
- Path in Azure Blob Storage
- Category
- Workflow stage
- Filename
- Description
- File size
- Creation timestamp
- Custom metadata

---

## Error Handling and Recovery

### Error Types

**Stage Execution Errors:**
- Agent execution failure
- Timeout (default: 30 minutes per stage)
- Resource constraints

**Evaluation Errors:**
- Score below threshold (0.7)
- Blocking issues identified
- Coverage requirements not met

**Storage Errors:**
- Azure Blob Storage upload failure
- Local filesystem errors

### Recovery Strategies

**1. Automatic Retry:**
- Transient errors are retried automatically
- Configurable retry count and backoff

**2. Checkpointing:**
- Workflow state saved after each successful stage
- Resume from last checkpoint on failure

**3. Manual Intervention:**
- Fix issues identified by evaluations
- Re-run failed stage
- Continue from checkpoint

### Example Error Handling

```python
try:
    result = orchestrator.run_workflow(
        work_item_id="12345",
        stop_on_failure=True,  # Stop on first failure
    )
except Exception as e:
    logger.error(f"Workflow failed: {e}")
    # Review checkpoint for last successful stage
    checkpoint = load_checkpoint("12345")
    logger.info(f"Last successful stage: {checkpoint['current_stage']}")
```

---

## Configuration

### Workflow Configuration

```python
@dataclass
class WorkflowConfig:
    # Stage timeouts (minutes)
    planning_timeout: int = 15
    code_generation_timeout: int = 30
    unit_testing_timeout: int = 20
    qa_testing_timeout: int = 30
    integration_testing_timeout: int = 25
    performance_testing_timeout: int = 30
    evidence_collection_timeout: int = 15

    # Evaluation thresholds
    min_eval_score: float = 0.7
    min_test_coverage: float = 0.8  # 80%
    max_response_time_ms: int = 2000  # 2s

    # Evidence settings
    evidence_base_path: str = "azure-blob://audit-cortex-evidence"
    max_attachments_per_stage: int = 3

    # Checkpoint settings
    checkpoint_dir: str = "./.workflow_checkpoints"
    checkpoint_enabled: bool = True
```

### Agent Configuration

Each agent can be configured with:
- LLM model and parameters
- Temperature settings
- Max tokens
- Retry policies

```python
agent_config = {
    "llm_model": "databricks-claude-sonnet-4-5",
    "temperature": 0.2,
    "max_tokens": 8000,
    "timeout_seconds": 300,
}
```

---

## Integration with Azure DevOps

### Work Item Updates

The orchestrator automatically updates ADO work items with:

1. **Stage Comments:**
   - Rich HTML-formatted comments for each stage
   - Status (passed/failed)
   - Duration
   - Metrics
   - Evidence summary

2. **Attachments:**
   - Top 3 screenshots from QA testing
   - Coverage reports
   - Performance reports

3. **Custom Fields:**
   - `Custom.LastWorkflowStage` - Last executed stage
   - `Custom.LastWorkflowStatus` - Stage status
   - `Custom.LastWorkflowUpdate` - Timestamp

4. **State Transitions:**
   - Work item state automatically updated based on workflow stage

### Example ADO Comment

```html
<h2>✅ Stage: Unit Testing</h2>

<table>
  <tr>
    <td><strong>Status:</strong></td>
    <td style="color: #4CAF50;">PASSED</td>
  </tr>
  <tr>
    <td><strong>Duration:</strong></td>
    <td>12.5s</td>
  </tr>
</table>

<h3>Metrics</h3>
<ul>
  <li><strong>Test Coverage:</strong> 85.5%</li>
  <li><strong>Tests Passed:</strong> 42</li>
  <li><strong>Tests Failed:</strong> 0</li>
</ul>

<h3>Evidence (3 files)</h3>
<ul>
  <li><code>test_audit_service.py</code> - Unit test suite</li>
  <li><code>coverage.json</code> - Coverage report</li>
  <li><code>pytest-report.html</code> - Test results</li>
</ul>

<p><em>Generated by AI-SDLC Workflow Orchestrator</em></p>
```

---

## Troubleshooting

### Common Issues

**1. Authentication Errors**

**Symptom:** `AuthenticationError: Failed to authenticate with Azure DevOps`

**Solutions:**
- Verify `AZURE_DEVOPS_PAT` is valid
- Check PAT has required permissions (Work Items: Read, Write)
- Ensure organization URL is correct

**2. Coverage Not Met**

**Symptom:** `EvalError: Test coverage 75.0% below minimum 80.0%`

**Solutions:**
- Review `coverage.json` for uncovered lines
- Add tests for missing coverage
- Re-run unit testing stage

**3. Stage Timeout**

**Symptom:** `TimeoutError: Stage exceeded timeout of 1800 seconds`

**Solutions:**
- Increase timeout in workflow configuration
- Optimize agent execution
- Check for network/resource issues

**4. Evidence Upload Failed**

**Symptom:** `IntegrationError: Failed to upload evidence to Azure Blob Storage`

**Solutions:**
- Verify `AZURE_STORAGE_CONNECTION_STRING`
- Check Azure Blob Storage permissions
- Retry with local storage: `--use-local-storage`

### Debug Mode

Enable verbose logging:
```bash
python -m ai_sdlc.cli.workflow_commands run-workflow 12345 -v
```

### Checkpoint Inspection

View checkpoint contents:
```bash
cat .workflow_checkpoints/12345/checkpoint.json
```

---

## Best Practices

1. **Always use checkpoints** - Enable checkpointing for long-running workflows
2. **Monitor evidence storage** - Keep an eye on Azure Blob Storage usage
3. **Review eval failures** - Don't ignore evaluation warnings
4. **Set appropriate timeouts** - Balance between patience and efficiency
5. **Use verbose logging** - Enable during initial workflow setup
6. **Test locally first** - Use `--use-local-storage` for testing
7. **Keep ADO credentials secure** - Use environment variables, not hardcoded values

---

## Document History

| Version | Date       | Author              | Changes                   |
|---------|------------|---------------------|---------------------------|
| 1.0     | 2026-01-17 | AI-SDLC Platform Team | Initial documentation     |

---

**Need Help?**
- Report issues: [GitHub Issues](https://github.com/your-org/ai-sdlc/issues)
- Slack: #ai-sdlc-support
- Email: ai-sdlc-support@yourcompany.com
