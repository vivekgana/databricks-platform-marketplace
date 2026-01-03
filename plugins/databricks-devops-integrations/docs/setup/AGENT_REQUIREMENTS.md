# Agent Requirements and Setup Guide

**Document Version:** 1.0
**Last Updated:** 2026-01-03 11:11:20
**Prepared by:** Databricks Platform Team

---

## Overview

This document outlines all requirements for running DevOps integration agents, including system requirements, dependencies, credentials, and configuration.

---

## System Requirements

### Hardware Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **CPU** | 2 cores | 4+ cores | More cores for parallel processing |
| **RAM** | 4 GB | 8-16 GB | Depends on workload volume |
| **Disk Space** | 500 MB | 2 GB | For logs and temp files |
| **Network** | Stable internet | High-speed | For API calls to JIRA/Azure DevOps |

### Software Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.9, 3.10, or 3.11 | Runtime environment |
| **pip** | Latest | Package management |
| **Git** | 2.x+ | Version control |
| **Claude CLI** | Latest | Claude Code integration |

### Operating System Support

- ✅ Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+)
- ✅ macOS (11.0+)
- ✅ Windows 10/11 (with WSL2 or native)

---

## Python Dependencies

### Core Dependencies

```txt
# Plugin SDK and integrations
jira==3.5.2                   # JIRA API client
azure-devops==7.1.0b4         # Azure DevOps API client
requests==2.31.0              # HTTP client
python-dateutil==2.8.2        # Date utilities

# LLM providers
anthropic==0.18.0             # Claude API
openai==1.12.0                # OpenAI/Azure OpenAI API
databricks-sdk==0.18.0        # Databricks Foundation Models

# Configuration
pyyaml==6.0.1                 # YAML config files
python-dotenv==1.0.0          # Environment variables
pydantic==2.5.3               # Data validation

# Logging and monitoring
structlog==24.1.0             # Structured logging

# Utilities
typing-extensions==4.9.0      # Type hints
jsonschema==4.20.0            # JSON validation
```

### Development Dependencies

```txt
# Testing
pytest==7.4.4                 # Test framework
pytest-cov==4.1.0             # Coverage
pytest-mock==3.12.0           # Mocking
pytest-asyncio==0.23.3        # Async tests

# Code quality
black==23.12.1                # Code formatter
pylint==3.0.3                 # Linter
mypy==1.8.0                   # Type checker
isort==5.13.2                 # Import sorter

# Security
bandit==1.7.6                 # Security scanner
safety==3.0.1                 # Dependency scanner
```

### Installation

```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-dev.txt

# Or install all at once
pip install -r requirements-dev.txt
```

---

## Required Credentials

### 1. JIRA Credentials

**What You Need**:
- JIRA Cloud URL
- API Token
- Email address
- Project key

**Setup Guide**: See [JIRA Token Setup](JIRA_TOKEN_SETUP.md)

**Environment Variables**:
```bash
export JIRA_URL="https://your-company.atlassian.net"
export JIRA_API_TOKEN="your-24-char-token"
export JIRA_EMAIL="your-email@company.com"
export JIRA_PROJECT="PROJ"
```

**Permissions Required**:
- Browse Projects
- Create Issues
- Edit Issues
- Add Comments
- Link Issues

### 2. Azure DevOps Credentials

**What You Need**:
- Organization URL
- Personal Access Token (PAT)
- Project name

**Setup Guide**: See [Azure PAT Setup](AZURE_PAT_SETUP.md)

**Environment Variables**:
```bash
export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-org"
export AZURE_DEVOPS_PAT="your-52-char-pat"
export AZURE_DEVOPS_PROJECT="YourProject"
```

**Required Scopes**:
- Work Items: Read & Write
- Code: Read
- Build: Read (optional)
- Release: Read (optional)

### 3. LLM API Keys

**What You Need**:
- API key from one of:
  - Anthropic (Claude) - Recommended
  - OpenAI (GPT-4)
  - Azure OpenAI
  - Databricks

**Setup Guide**: See [LLM Requirements](LLM_REQUIREMENTS.md)

**Environment Variables**:
```bash
# For Claude (Anthropic)
export LLM_PROVIDER="claude"
export ANTHROPIC_API_KEY="sk-ant-api03-..."
export LLM_MODEL="claude-3-5-sonnet-20241022"

# For OpenAI
export LLM_PROVIDER="openai"
export OPENAI_API_KEY="sk-..."
export LLM_MODEL="gpt-4-turbo-preview"

# For Azure OpenAI
export LLM_PROVIDER="azure_openai"
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://..."
export AZURE_OPENAI_DEPLOYMENT="gpt-4"

# For Databricks
export LLM_PROVIDER="databricks"
export DATABRICKS_HOST="https://..."
export DATABRICKS_TOKEN="dapi..."
```

### 4. Optional: Notification Services

**Slack**:
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
```

**Email (SMTP)**:
```bash
export SMTP_HOST="smtp.company.com"
export SMTP_PORT="587"
export SMTP_USERNAME="devops@company.com"
export SMTP_PASSWORD="..."
export SMTP_FROM="devops@company.com"
```

---

## Configuration Files

### 1. Main Configuration

Create `config/config.yaml`:

```yaml
# Plugin configuration
plugin:
  name: "databricks-devops-integrations"
  version: "1.0.0"

# Platform selection
default_platform: jira  # or azure_devops

# JIRA configuration
jira:
  url: "${JIRA_URL}"
  api_token: "${JIRA_API_TOKEN}"
  email: "${JIRA_EMAIL}"
  project: "${JIRA_PROJECT}"
  timeout: 30
  retry_attempts: 3
  verify_ssl: true

# Azure DevOps configuration
azure_devops:
  org_url: "${AZURE_DEVOPS_ORG_URL}"
  pat: "${AZURE_DEVOPS_PAT}"
  project: "${AZURE_DEVOPS_PROJECT}"
  api_version: "7.0"
  timeout: 30

# LLM configuration
llm:
  provider: "${LLM_PROVIDER}"
  model: "${LLM_MODEL}"
  api_key: "${ANTHROPIC_API_KEY}"
  temperature: 0.2
  max_tokens: 4096
  timeout: 30
  retry_attempts: 3

# Logging configuration
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/agent.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5
```

### 2. Agent Configuration

Create `config/agent_config.yaml`:

```yaml
# Defect Management Agent Configuration
defect_management:
  # Feature flags
  features:
    auto_create_defects: true
    code_analysis: true
    root_cause_analysis: true
    auto_assignment: true
    notifications: true

  # Severity configuration
  severity_rules:
    critical:
      keywords: ["security", "vulnerability", "data loss", "crash", "exploit"]
      auto_create: true
      auto_notify: true
      sla_hours: 4

    high:
      keywords: ["performance", "broken", "failure", "error", "exception"]
      auto_create: true
      auto_notify: true
      sla_hours: 24

    medium:
      keywords: ["bug", "issue", "problem", "incorrect"]
      auto_create: true
      auto_notify: false
      sla_hours: 72

    low:
      keywords: ["typo", "minor", "cosmetic", "suggestion"]
      auto_create: false
      auto_notify: false
      sla_hours: 168

  # Auto-assignment rules
  assignment_rules:
    - component: "authentication"
      team: "auth-team"
      assignee: "auth-lead@company.com"
      labels: ["security", "auth"]

    - component: "api"
      team: "api-team"
      assignee: "api-lead@company.com"
      labels: ["api", "backend"]

    - component: "database"
      team: "data-team"
      assignee: "data-lead@company.com"
      labels: ["database", "data"]

    - component: "ui"
      team: "frontend-team"
      assignee: "frontend-lead@company.com"
      labels: ["ui", "frontend"]

  # Notification configuration
  notifications:
    slack:
      enabled: true
      webhook_url: "${SLACK_WEBHOOK_URL}"
      channels:
        critical: "#incidents"
        high: "#bugs"
        medium: "#dev-team"
        low: "#backlog"

    email:
      enabled: true
      smtp_host: "${SMTP_HOST}"
      smtp_port: 587
      smtp_username: "${SMTP_USERNAME}"
      smtp_password: "${SMTP_PASSWORD}"
      from_address: "devops@company.com"
      recipients:
        critical: ["oncall@company.com", "cto@company.com"]
        high: ["team-leads@company.com"]
        medium: ["dev-team@company.com"]

  # CI/CD integration
  cicd:
    enabled: true
    auto_create_on_failure: true
    link_to_build: true
    link_to_commit: true
```

---

## Environment Setup

### Development Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v
```

### Production Environment

```bash
# Create production virtual environment
python -m venv /opt/devops-agents/venv

# Activate
source /opt/devops-agents/venv/bin/activate

# Install production dependencies only
pip install -r requirements.txt

# Set up systemd service (Linux)
sudo cp deploy/devops-agent.service /etc/systemd/system/
sudo systemctl enable devops-agent
sudo systemctl start devops-agent
```

---

## Validation Checklist

Before running agents, verify all requirements:

```bash
# System requirements
□ Python 3.9+ installed
□ pip latest version
□ Git installed
□ Claude CLI installed

# Dependencies
□ All Python packages installed
□ No dependency conflicts

# Credentials
□ JIRA credentials set and tested
□ Azure DevOps credentials set and tested
□ LLM API key set and tested
□ Optional services configured

# Configuration
□ config.yaml created and validated
□ agent_config.yaml created
□ Environment variables set
□ Log directory created

# Permissions
□ JIRA permissions verified
□ Azure DevOps permissions verified
□ File system permissions correct

# Network
□ Can reach JIRA API
□ Can reach Azure DevOps API
□ Can reach LLM provider API
□ Firewall rules configured
```

### Automated Validation Script

```python
#!/usr/bin/env python3
"""
Complete environment validation script
"""

import os
import sys
from packaging import version

def check_python_version():
    """Check Python version"""
    print("1. Checking Python version...")
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    if version.parse(py_version) >= version.parse("3.9"):
        print(f"   ✅ Python {py_version} (OK)")
        return True
    else:
        print(f"   ❌ Python {py_version} (Need 3.9+)")
        return False

def check_dependencies():
    """Check required packages"""
    print("\n2. Checking dependencies...")
    required = ["jira", "azure.devops", "anthropic", "yaml", "dotenv"]
    all_ok = True
    for pkg in required:
        try:
            __import__(pkg)
            print(f"   ✅ {pkg}")
        except ImportError:
            print(f"   ❌ {pkg} (not installed)")
            all_ok = False
    return all_ok

def check_credentials():
    """Check environment variables"""
    print("\n3. Checking credentials...")
    required = {
        "JIRA_URL": os.getenv("JIRA_URL"),
        "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN"),
        "JIRA_EMAIL": os.getenv("JIRA_EMAIL"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    }

    all_ok = True
    for var, value in required.items():
        if value:
            print(f"   ✅ {var}")
        else:
            print(f"   ❌ {var} (not set)")
            all_ok = False
    return all_ok

def check_network():
    """Check network connectivity"""
    print("\n4. Checking network connectivity...")
    import requests

    endpoints = {
        "JIRA": os.getenv("JIRA_URL"),
        "Anthropic": "https://api.anthropic.com",
    }

    all_ok = True
    for name, url in endpoints.items():
        if url:
            try:
                response = requests.get(url, timeout=5)
                print(f"   ✅ {name} ({response.status_code})")
            except Exception as e:
                print(f"   ❌ {name} ({str(e)})")
                all_ok = False
    return all_ok

def main():
    print("="  * 60)
    print("DevOps Agents - Environment Validation")
    print("="  * 60)
    print()

    checks = [
        check_python_version(),
        check_dependencies(),
        check_credentials(),
        check_network(),
    ]

    print()
    print("="  * 60)
    if all(checks):
        print("✅ All checks passed! Ready to run agents.")
    else:
        print("❌ Some checks failed. Please fix issues above.")
    print("="  * 60)

    return 0 if all(checks) else 1

if __name__ == "__main__":
    sys.exit(main())
```

Run validation:
```bash
python validate_environment.py
```

---

## Troubleshooting

### Common Issues

**Issue**: Import errors
```bash
# Solution
pip install --upgrade -r requirements.txt
```

**Issue**: Permission denied
```bash
# Solution
chmod +x scripts/*.sh
sudo chown -R $USER:$USER ~/.claude/plugins
```

**Issue**: Network timeout
```bash
# Solution: Check firewall/proxy
curl -I https://api.anthropic.com
curl -I $JIRA_URL
```

**Issue**: Configuration not found
```bash
# Solution: Check paths
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## Additional Resources

- [JIRA Token Setup Guide](JIRA_TOKEN_SETUP.md)
- [Azure PAT Setup Guide](AZURE_PAT_SETUP.md)
- [LLM Requirements](LLM_REQUIREMENTS.md)
- [Marketplace Deployment](../deployment/MARKETPLACE_DEPLOYMENT.md)
- [Defect Management Agent](../../agents/defect-management-agent.md)

---

**Maintained by**: Databricks Platform Team
