# Investment Asset Plan - DevOps Integration Example

This example demonstrates how to use the DevOps integration plugins (JIRA and Azure DevOps) to manage an investment asset planning and tracking system.

## Overview

This project showcases:
- **Automated work item creation** from investment opportunities
- **Integration with JIRA** for agile tracking
- **Integration with Azure DevOps** for enterprise workflows
- **CI/CD pipeline** for automated deployment
- **Testing framework** with pytest and mocks
- **Demo deployment** scripts

## Use Case

Investment teams need to track:
- Investment opportunities (deal flow)
- Due diligence tasks
- Portfolio monitoring
- Risk assessments
- Regulatory compliance
- Team velocity and capacity

## Architecture

```
Investment Asset Plan System
├── Work Item Creation (from opportunities)
├── JIRA Integration (agile teams)
├── Azure DevOps Integration (enterprise)
├── Automated Incident Handling
├── Team Velocity Tracking
└── Webhook Processing
```

## Features

### 1. Opportunity Tracking
- Create work items from investment opportunities
- Link to due diligence documents
- Track approval workflows

### 2. Due Diligence Management
- Break down diligence into tasks
- Assign to team members
- Track completion status

### 3. Portfolio Monitoring
- Create incidents from alerts
- Auto-assign to responsible teams
- Track resolution time

### 4. Compliance Tracking
- Generate compliance checklists
- Track regulatory requirements
- Audit trail integration

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export JIRA_URL="https://your-company.atlassian.net"
export JIRA_API_TOKEN="your-jira-token"
export JIRA_EMAIL="your-email@company.com"

# Or for Azure DevOps
export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-org"
export AZURE_DEVOPS_PAT="your-personal-access-token"
export AZURE_DEVOPS_PROJECT="your-project"
```

### Run the Example

```bash
# Run with JIRA
python src/main.py --platform jira

# Run with Azure DevOps
python src/main.py --platform azure_devops

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Example Usage

### Create Work Item from Investment Opportunity

```python
from src.investment_tracker import InvestmentTracker
from sdk import PluginRegistry, PluginConfig

# Initialize tracker
tracker = InvestmentTracker(platform="jira")

# Create opportunity
opportunity = {
    "title": "Series A Investment - TechStartup Inc",
    "description": "Cloud infrastructure SaaS, $10M round",
    "amount": 10000000,
    "stage": "due_diligence",
    "sector": "Enterprise Software",
    "risk_level": "medium"
}

# Creates work item with automated breakdown
work_item_id = tracker.create_from_opportunity(opportunity)
print(f"Created work item: {work_item_id}")
```

### Track Due Diligence Tasks

```python
# Get due diligence checklist
tasks = tracker.get_due_diligence_tasks("TechStartup Inc")

# Update task status
tracker.update_task(
    task_id="DD-123",
    status="completed",
    findings="Strong financials, scalable architecture"
)
```

### Monitor Portfolio

```python
# Create incident from alert
alert = {
    "portfolio_company": "TechStartup Inc",
    "alert_type": "revenue_decline",
    "severity": "high",
    "details": "Q3 revenue down 15% YoY"
}

incident_id = tracker.create_incident(alert)
```

## Configuration

### config/jira_config.yaml

```yaml
plugin_id: "jira-investment-tracker"
api_endpoint: "${JIRA_URL}"
api_key: "${JIRA_API_TOKEN}"
organization: "${JIRA_EMAIL}"
project: "INVEST"

custom_settings:
  issue_types:
    opportunity: "Epic"
    due_diligence: "Story"
    task: "Task"
    incident: "Bug"

  priority_mapping:
    critical: "Highest"
    high: "High"
    medium: "Medium"
    low: "Low"

  custom_fields:
    investment_amount: "customfield_10030"
    sector: "customfield_10031"
    risk_level: "customfield_10032"
```

### config/azure_devops_config.yaml

```yaml
plugin_id: "ado-investment-tracker"
api_endpoint: "${AZURE_DEVOPS_ORG_URL}"
api_key: "${AZURE_DEVOPS_PAT}"
organization: "your-org"
project: "${AZURE_DEVOPS_PROJECT}"

custom_settings:
  work_item_types:
    opportunity: "Feature"
    due_diligence: "User Story"
    task: "Task"
    incident: "Bug"

  area_path: "Investment Management"
  iteration_path: "Investment Management\\Sprint 1"
```

## Testing

### Unit Tests

```bash
# Test plugin SDK
pytest tests/test_plugin_sdk.py -v

# Test JIRA integration
pytest tests/test_jira_plugin.py -v

# Test Azure DevOps integration
pytest tests/test_azure_devops_plugin.py -v

# Test investment tracker
pytest tests/test_investment_tracker.py -v
```

### Integration Tests

```bash
# Run integration tests (requires credentials)
pytest tests/integration/ -v --run-integration

# Test end-to-end workflow
pytest tests/integration/test_e2e_workflow.py -v
```

## CI/CD Pipeline

This project includes GitHub Actions workflow for:
- Automated testing on every commit
- Code quality checks (black, pylint, mypy)
- Security scanning
- Automated deployment to dev/staging/prod

See `.github/workflows/ci-cd.yml` for details.

## Deployment

### Deploy to Development

```bash
./scripts/deploy.sh dev
```

### Deploy to Production

```bash
./scripts/deploy.sh prod
```

## Monitoring

### Health Checks

```bash
# Check plugin health
python src/health_check.py

# Check all registered plugins
python src/health_check.py --all
```

### Metrics

```bash
# Get team velocity
python src/metrics.py --team "Investment Team" --days 30

# Get incident statistics
python src/metrics.py --incidents --days 90
```

## Documentation

- [Plugin SDK Documentation](../../sdk/README.md)
- [JIRA Plugin Guide](../../integrations/jira/README.md)
- [Azure DevOps Plugin Guide](../../integrations/azure_devops/README.md)
- [API Reference](docs/API.md)

## Support

- Issues: https://github.com/yourcompany/databricks-platform-marketplace/issues
- Slack: #devops-integrations
- Email: platform-team@vivekgana.com

## License

MIT License - see [LICENSE](../../../../LICENSE) for details

---

**Last Updated:** January 2, 2026
**Version:** 1.0.0
**Prepared by:** Databricks Platform Team
