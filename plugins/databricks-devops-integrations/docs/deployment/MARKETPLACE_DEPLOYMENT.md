# Claude Marketplace Deployment Guide

**Document Version:** 1.0
**Last Updated:** 2026-01-03 11:11:20
**Prepared by:** Databricks Platform Team

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation from Marketplace](#installation-from-marketplace)
4. [Manual Installation](#manual-installation)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Agent Deployment](#agent-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This guide explains how to deploy the Databricks DevOps Integration plugins and agents from the Claude Marketplace, including the Defect Management Agent.

---

## Prerequisites

### 1. Claude Code CLI

Ensure Claude Code CLI is installed:

```bash
# Check installation
claude --version

# If not installed, install from:
# https://docs.claude.com/claude-code/installation
```

### 2. Required Credentials

Before installation, prepare these credentials:

#### For JIRA Integration:
- [ ] JIRA Cloud URL (e.g., `https://your-company.atlassian.net`)
- [ ] JIRA API Token ([Setup Guide](../setup/JIRA_TOKEN_SETUP.md))
- [ ] JIRA Email address
- [ ] JIRA Project Key

#### For Azure DevOps Integration:
- [ ] Azure DevOps Organization URL
- [ ] Personal Access Token (PAT) ([Setup Guide](../setup/AZURE_PAT_SETUP.md))
- [ ] Azure DevOps Project Name

#### For LLM/AI Features:
- [ ] LLM Provider API Key ([Setup Guide](../setup/LLM_REQUIREMENTS.md))
  - Anthropic Claude (recommended)
  - OpenAI GPT-4
  - Azure OpenAI
  - Databricks Foundation Models

### 3. System Requirements

```yaml
Hardware:
  CPU: 2+ cores
  RAM: 4GB minimum, 8GB recommended
  Disk: 500MB free space

Software:
  Python: 3.9, 3.10, or 3.11
  pip: Latest version
  Git: 2.x or later
  Operating System: Linux, macOS, or Windows
```

---

## Installation from Marketplace

### Option 1: Direct Installation (Recommended)

```bash
# Install DevOps integrations plugin
npx claude-plugins install @databricks/devops-integrations

# Or using Claude CLI
claude /plugin install databricks-devops-integrations
```

### Option 2: Add Marketplace First

```bash
# Add the Databricks marketplace
claude /plugin marketplace add https://github.com/vivekgana/databricks-platform-marketplace

# List available plugins
claude /plugin list-available

# Install specific plugin
claude /plugin install databricks-devops-integrations
```

### What Gets Installed

```
~/.claude/plugins/databricks-devops-integrations/
├── sdk/                    # Plugin SDK framework
├── integrations/
│   ├── jira/              # JIRA integration
│   └── azure_devops/      # Azure DevOps integration
├── agents/
│   └── defect-management-agent.md  # Defect management agent
├── examples/              # Sample projects
├── tests/                 # Test suite
└── config/                # Configuration templates
```

---

## Manual Installation

If marketplace installation isn't available:

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/vivekgana/databricks-platform-marketplace.git

# Navigate to plugin directory
cd databricks-platform-marketplace/plugins/databricks-devops-integrations
```

### Step 2: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "from sdk import PluginRegistry; print('✅ SDK installed')"
python -c "from integrations.jira import JiraPlugin; print('✅ JIRA plugin installed')"
python -c "from integrations.azure_devops import AzureDevOpsPlugin; print('✅ Azure DevOps plugin installed')"
```

### Step 3: Set Up Plugin in Claude

```bash
# Create plugin symlink (Linux/Mac)
ln -s $(pwd) ~/.claude/plugins/databricks-devops-integrations

# Or copy files (Windows)
xcopy /E /I . "%USERPROFILE%\.claude\plugins\databricks-devops-integrations\"
```

---

## Configuration

### Step 1: Set Up Environment Variables

#### Linux/macOS

Create `~/.claude/env`:

```bash
# JIRA Configuration
export JIRA_URL="https://your-company.atlassian.net"
export JIRA_API_TOKEN="your-24-character-api-token"
export JIRA_EMAIL="your-email@company.com"
export JIRA_PROJECT="PROJ"

# Azure DevOps Configuration
export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-org"
export AZURE_DEVOPS_PAT="your-52-character-pat-token"
export AZURE_DEVOPS_PROJECT="YourProject"

# LLM Configuration
export LLM_PROVIDER="claude"
export ANTHROPIC_API_KEY="sk-ant-api03-..."
export LLM_MODEL="claude-3-5-sonnet-20241022"
```

Load environment:
```bash
source ~/.claude/env
```

#### Windows

Create `%USERPROFILE%\.claude\env.bat`:

```batch
@echo off
rem JIRA Configuration
set JIRA_URL=https://your-company.atlassian.net
set JIRA_API_TOKEN=your-24-character-api-token
set JIRA_EMAIL=your-email@company.com
set JIRA_PROJECT=PROJ

rem Azure DevOps Configuration
set AZURE_DEVOPS_ORG_URL=https://dev.azure.com/your-org
set AZURE_DEVOPS_PAT=your-52-character-pat-token
set AZURE_DEVOPS_PROJECT=YourProject

rem LLM Configuration
set LLM_PROVIDER=claude
set ANTHROPIC_API_KEY=sk-ant-api03-...
set LLM_MODEL=claude-3-5-sonnet-20241022
```

Load environment:
```batch
call %USERPROFILE%\.claude\env.bat
```

### Step 2: Create Configuration File

Create `~/.claude/plugins/databricks-devops-integrations/config/config.yaml`:

```yaml
# Platform Selection
default_platform: jira  # Options: jira, azure_devops

# JIRA Configuration
jira:
  url: "${JIRA_URL}"
  api_token: "${JIRA_API_TOKEN}"
  email: "${JIRA_EMAIL}"
  project: "${JIRA_PROJECT}"
  timeout: 30
  retry_attempts: 3

# Azure DevOps Configuration
azure_devops:
  org_url: "${AZURE_DEVOPS_ORG_URL}"
  pat: "${AZURE_DEVOPS_PAT}"
  project: "${AZURE_DEVOPS_PROJECT}"
  api_version: "7.0"
  timeout: 30

# LLM Configuration
llm:
  provider: "${LLM_PROVIDER}"
  model: "${LLM_MODEL}"
  api_key: "${ANTHROPIC_API_KEY}"
  temperature: 0.2
  max_tokens: 4096

# Defect Management Agent Settings
defect_management:
  auto_create_from_ci_cd: true
  auto_assign: true
  severity_thresholds:
    critical: ["security", "data_loss", "crash"]
    high: ["performance", "feature_broken"]
    medium: ["ui_issue", "minor_bug"]
  notification_channels:
    - slack
    - email
```

---

## Verification

### Test Plugin Installation

```bash
# List installed plugins
claude /plugin list

# Should show:
# databricks-devops-integrations (v1.0.0)
```

### Test JIRA Integration

```bash
# Run validation script
cd ~/.claude/plugins/databricks-devops-integrations
python examples/validate_jira.py
```

Expected output:
```
🔍 Validating JIRA Configuration...

1. Checking environment variables:
   ✅ JIRA_URL: https://...
   ✅ JIRA_API_TOKEN: Atatt3x...
   ✅ JIRA_EMAIL: user@...
   ✅ JIRA_PROJECT: PROJ

2. Creating plugin configuration:
   ✅ Configuration created

3. Testing authentication:
   ✅ Authentication successful

4. Testing basic operations:
   ✅ Current user: John Doe
   ✅ Found 25 issues in project PROJ

============================================================
✅ All validation checks passed!
============================================================
```

### Test Azure DevOps Integration

```bash
python examples/validate_azure_devops.py
```

### Test Defect Management Agent

```bash
# Test agent in Claude
claude

# In Claude prompt:
/defect-management:analyze-code <path-to-code-file>
```

---

## Agent Deployment

### Deploying Defect Management Agent

#### 1. Enable Agent in Claude

The Defect Management Agent is automatically available after plugin installation.

Verify agent:
```bash
# List available agents
claude /agent list

# Should show:
# defect-management - Automated defect detection and management
```

#### 2. Configure Agent Behavior

Edit `config/agent_config.yaml`:

```yaml
defect_management_agent:
  # Enable/disable features
  features:
    auto_defect_creation: true
    code_analysis: true
    root_cause_analysis: true
    auto_assignment: true
    slack_notifications: true

  # Severity rules
  severity_rules:
    critical:
      keywords: [" security", "vulnerability", "data loss", "crash"]
      auto_notify: true
      sla_hours: 4

    high:
      keywords: ["performance", "broken", "failure"]
      auto_notify: true
      sla_hours: 24

    medium:
      keywords: ["bug", "issue", "problem"]
      auto_notify: false
      sla_hours: 72

  # Auto-assignment rules
  assignment_rules:
    - component: "authentication"
      team: "auth-team"
      assignee: "auth-lead@company.com"

    - component: "api"
      team: "api-team"
      assignee: "api-lead@company.com"

  # Notification settings
  notifications:
    slack:
      enabled: true
      webhook_url: "${SLACK_WEBHOOK_URL}"
      channels:
        critical: "#incidents"
        high: "#bugs"
        medium: "#dev-team"

    email:
      enabled: true
      smtp_host: "smtp.company.com"
      from_address: "devops@company.com"
```

#### 3. Test Agent

Create test code with a defect:

```python
# test_defect.py
def process_payment(amount):
    return api.charge(amount)  # No error handling - should be flagged!
```

Analyze with agent:
```bash
claude /defect-management:analyze-code test_defect.py
```

Expected output:
```
🔍 Analyzing code for defects...

Critical Defect Found:
- Severity: HIGH
- Line: 2
- Issue: Missing error handling in payment processing
- Risk: Unhandled exceptions can cause payment failures

Recommendation:
```python
def process_payment(amount):
    try:
        return api.charge(amount)
    except PaymentError as e:
        logger.error(f"Payment failed: {e}")
        raise PaymentProcessingError(str(e))
```

Create JIRA ticket? (y/n):
```

---

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/defect-management.yml`:

```yaml
name: Automated Defect Management

on:
  pull_request:
    types: [opened, synchronize]
  push:
    branches: [main, develop]

jobs:
  defect-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Analyze code for defects
        env:
          JIRA_URL: ${{ secrets.JIRA_URL }}
          JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
          JIRA_EMAIL: ${{ secrets.JIRA_EMAIL }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python -m agents.defect_management analyze --pr ${{ github.event.pull_request.number }}

      - name: Create defect tickets
        if: failure()
        run: |
          python -m agents.defect_management create-tickets
```

### Azure Pipelines

Create `azure-pipelines.yml`:

```yaml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.10'

- script: |
    pip install -r requirements.txt
  displayName: 'Install dependencies'

- script: |
    python -m agents.defect_management analyze --pr $(System.PullRequest.PullRequestNumber)
  env:
    AZURE_DEVOPS_PAT: $(AZURE_DEVOPS_PAT)
    ANTHROPIC_API_KEY: $(ANTHROPIC_API_KEY)
  displayName: 'Analyze for defects'
```

---

## Troubleshooting

### Common Installation Issues

#### 1. Plugin Not Found

```bash
# Error: Plugin 'databricks-devops-integrations' not found

# Solution: Check plugin installation
claude /plugin list

# If not listed, reinstall
claude /plugin install databricks-devops-integrations
```

#### 2. Import Errors

```python
# Error: ModuleNotFoundError: No module named 'sdk'

# Solution: Install dependencies
pip install -r requirements.txt

# Verify Python path
export PYTHONPATH="${PYTHONPATH}:~/.claude/plugins/databricks-devops-integrations"
```

#### 3. Authentication Failures

```bash
# Error: 401 Unauthorized

# Solution: Verify credentials
python -c "import os; print(os.getenv('JIRA_API_TOKEN'))"

# Re-set if needed
export JIRA_API_TOKEN="your-token"
```

#### 4. Agent Not Responding

```bash
# Error: Agent timeout or no response

# Solution: Check LLM configuration
python -c "import os; print(os.getenv('ANTHROPIC_API_KEY'))"

# Test LLM connection
python -m agents.test_llm
```

### Getting Help

- **Documentation**: Full docs in `docs/` directory
- **Examples**: Sample code in `examples/` directory
- **Issues**: Report at https://github.com/vivekgana/databricks-platform-marketplace/issues
- **Slack**: #devops-integrations
- **Email**: platform-team@yourcompany.com

---

## Next Steps

1. **Explore Examples**: Check `examples/investment-asset-plan/` for complete working example
2. **Review Agents**: See `agents/defect-management-agent.md` for agent documentation
3. **Configure CI/CD**: Integrate with your build pipelines
4. **Monitor Usage**: Track defect metrics and team velocity
5. **Provide Feedback**: Help us improve by sharing your experience

---

**Maintained by**: Databricks Platform Team
