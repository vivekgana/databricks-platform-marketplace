# JIRA API Token Setup Guide

**Document Version:** 1.0
**Last Updated:** 2026-01-03 11:11:20
**Prepared by:** Databricks Platform Team

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Creating an API Token](#creating-an-api-token)
4. [Security Best Practices](#security-best-practices)
5. [Configuration for DevOps Plugins](#configuration-for-devops-plugins)
6. [Token Management](#token-management)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Overview

JIRA API Tokens are required to authenticate with Atlassian JIRA Cloud REST APIs. This guide provides step-by-step instructions for creating and managing API tokens for use with the Databricks DevOps Integration plugins.

### What is a JIRA API Token?

A JIRA API Token is a secure authentication method for accessing JIRA Cloud APIs. Key features:
- **Secure**: More secure than using passwords
- **Revocable**: Can be revoked without changing password
- **No expiration**: Tokens don't expire automatically
- **User-specific**: Associated with your JIRA account
- **Full permissions**: Inherits your JIRA permissions

---

## Prerequisites

Before creating an API token, ensure you have:

### 1. JIRA Cloud Account
- Active Atlassian account
- Access to JIRA Cloud instance
- URL format: `https://your-company.atlassian.net`

### 2. Required Permissions
Minimum JIRA permissions needed:
- **Browse Projects**: View issues
- **Create Issues**: Create work items
- **Edit Issues**: Update work items
- **Add Comments**: Add comments to issues
- **Link Issues**: Create links between issues

### 3. Email Address
- Verified email associated with JIRA account
- Used for authentication with API token

### 4. Environment Variables Setup

After creating your API token, you'll need to configure these environment variables:

**Windows (PowerShell):**
```powershell
# JIRA Configuration
[System.Environment]::SetEnvironmentVariable('JIRA_URL', 'https://your-company.atlassian.net', 'User')
[System.Environment]::SetEnvironmentVariable('JIRA_API_TOKEN', 'your-24-character-api-token', 'User')
[System.Environment]::SetEnvironmentVariable('JIRA_EMAIL', 'your-email@company.com', 'User')
[System.Environment]::SetEnvironmentVariable('JIRA_PROJECT', 'PROJ', 'User')
```

**Linux/Mac (Bash/Zsh):**
```bash
# JIRA Configuration
export JIRA_URL="https://your-company.atlassian.net"
export JIRA_API_TOKEN="your-24-character-api-token"
export JIRA_EMAIL="your-email@company.com"
export JIRA_PROJECT="PROJ"

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export JIRA_URL="https://your-company.atlassian.net"' >> ~/.bashrc
echo 'export JIRA_API_TOKEN="your-24-character-api-token"' >> ~/.bashrc
echo 'export JIRA_EMAIL="your-email@company.com"' >> ~/.bashrc
echo 'export JIRA_PROJECT="PROJ"' >> ~/.bashrc
```

**Docker/Container Environment:**
```bash
# In docker-compose.yml or .env file
JIRA_URL=https://your-company.atlassian.net
JIRA_API_TOKEN=your-24-character-api-token
JIRA_EMAIL=your-email@company.com
JIRA_PROJECT=PROJ
```

**Environment Variable Descriptions:**
- `JIRA_URL`: Your JIRA Cloud instance URL (no trailing slash)
- `JIRA_API_TOKEN`: The API token you'll create (24 characters)
- `JIRA_EMAIL`: Your email address associated with the JIRA account
- `JIRA_PROJECT`: The project key (e.g., PROJ, DEV, TEST)

**Security Note:** Never commit these values to version control. Use `.env` files that are in `.gitignore` or secure secret management systems.

---

## Creating an API Token

### Step 1: Access Atlassian Account Settings

1. **Navigate to Atlassian Account**:
   ```
   https://id.atlassian.com/manage-profile/security/api-tokens
   ```

2. **Alternative Access**:
   - Click your profile picture in JIRA
   - Select **Manage account**
   - Navigate to **Security** tab
   - Click **API tokens**

   ![JIRA Security Settings](../images/jira-security-menu.png)

### Step 2: Create New API Token

1. Click the **Create API token** button

2. Enter token details:

   **Label**: Enter a descriptive name
   ```
   ✅ Good examples:
   - "Databricks DevOps Plugin - Production"
   - "Defect Management Agent - Staging"
   - "CI/CD Integration - Development"

   ❌ Avoid:
   - "Token 1"
   - "Test"
   - "API"
   ```

3. Click **Create** button

### Step 3: Copy and Store Token

1. **Copy the token immediately**!
   ```
   Token format: 24-character alphanumeric string
   Example: Atatt3xFfGF0AbCdEfGhIjKlMnOpQrStUvWxYz
   ```

2. **CRITICAL**: You can only see the token once!
   - Store in password manager (1Password, LastPass, etc.)
   - Or store in secure credential vault
   - Never commit to source control
   - Never share via email/chat

3. Click **Close** when done

---

## Security Best Practices

### 1. Token Storage

**✅ DO:**

```bash
# Store in environment variables
export JIRA_API_TOKEN="your-api-token-here"

# Use secure credential storage
# - Azure Key Vault
# - AWS Secrets Manager
# - HashiCorp Vault
# - Password managers (1Password, LastPass)
```

**❌ DON'T:**

```bash
# Never commit to Git
# config.py
JIRA_TOKEN = "Atatt3xFfGF0AbCdEfGhIjKlMnOpQrStUvWxYz"  # ❌ BAD!

# Never share via communication tools
# "Here's my JIRA token: Atatt3x..."  # ❌ BAD!

# Never store in plain text files
# tokens.txt containing API tokens  # ❌ BAD!
```

### 2. Access Control

```yaml
# Principle of Least Privilege
# Only share tokens with:
✅ Authorized team members
✅ Secure automation systems
✅ CI/CD pipelines (using secrets management)

# Never share with:
❌ Contractors without proper access
❌ External systems
❌ Public repositories
```

### 3. Token Rotation

JIRA API tokens don't expire automatically, but should be rotated regularly:

```bash
# Recommended rotation schedule
Production: Every 90 days
Development: Every 30 days
Testing: Every 14 days

# Rotation process
1. Generate new token (7 days before rotation date)
2. Update all configurations
3. Test new token
4. Revoke old token
5. Document change
```

### 4. Monitoring & Auditing

```bash
# Regular audit checklist
□ Review active tokens monthly
□ Revoke unused tokens
□ Check JIRA audit logs for API activity
□ Monitor for suspicious access patterns
□ Update token labels for clarity
□ Document token purpose and usage
```

### 5. Incident Response

If token is compromised:

**Immediate Actions**:
```bash
1. Revoke token immediately
   → https://id.atlassian.com/manage-profile/security/api-tokens
   → Find token → Revoke

2. Check JIRA audit logs
   → JIRA Settings → System → Audit log
   → Filter by your user
   → Review recent activity

3. Generate new token
   → Follow creation steps above
   → Use different label

4. Update all configurations
   → Environment variables
   → CI/CD secrets
   → Application configs

5. Notify team
   → Security team
   → DevOps team
   → Project stakeholders
```

---

## Configuration for DevOps Plugins

### Environment Variables Method (Recommended)

```bash
# Linux/Mac
export JIRA_URL="https://your-company.atlassian.net"
export JIRA_API_TOKEN="your-24-character-api-token"
export JIRA_EMAIL="your-email@company.com"
export JIRA_PROJECT="PROJ"

# Windows PowerShell
$env:JIRA_URL="https://your-company.atlassian.net"
$env:JIRA_API_TOKEN="your-24-character-api-token"
$env:JIRA_EMAIL="your-email@company.com"
$env:JIRA_PROJECT="PROJ"

# Windows Command Prompt
set JIRA_URL=https://your-company.atlassian.net
set JIRA_API_TOKEN=your-24-character-api-token
set JIRA_EMAIL=your-email@company.com
set JIRA_PROJECT=PROJ
```

### .env File Method (Development Only)

Create `.env` file in project root:

```bash
# JIRA Configuration
JIRA_URL=https://your-company.atlassian.net
JIRA_API_TOKEN=your-24-character-api-token
JIRA_EMAIL=your-email@company.com
JIRA_PROJECT=PROJ

# Optional settings
JIRA_TIMEOUT=30
JIRA_RETRY_ATTEMPTS=3
JIRA_VERIFY_SSL=true
```

**⚠️ IMPORTANT**: Add `.env` to `.gitignore`:

```bash
# .gitignore
.env
.env.local
.env.*.local
*.env
```

### Configuration File Method

Create `config/jira_config.yaml`:

```yaml
jira:
  # JIRA Cloud URL
  url: "https://your-company.atlassian.net"

  # Authentication (use environment variable reference)
  email: "${JIRA_EMAIL}"
  api_token: "${JIRA_API_TOKEN}"

  # Default project
  project: "PROJ"

  # Connection settings
  timeout: 30
  retry_attempts: 3
  verify_ssl: true

  # Custom field mappings
  custom_fields:
    story_points: "customfield_10016"
    sprint: "customfield_10020"
    epic_link: "customfield_10014"

  # Issue type mappings
  issue_types:
    feature: "Story"
    bug: "Bug"
    task: "Task"
    epic: "Epic"

  # Priority mapping
  priority_mapping:
    critical: "Highest"
    high: "High"
    medium: "Medium"
    low: "Low"

  # Workflow states
  workflow_states:
    todo: "To Do"
    in_progress: "In Progress"
    in_review: "In Review"
    done: "Done"
```

### Python Configuration

```python
from sdk import PluginConfig
from integrations.jira import JiraPlugin
import os

# Method 1: From environment variables (recommended)
config = PluginConfig(
    plugin_id="jira",
    api_endpoint=os.getenv("JIRA_URL"),
    api_key=os.getenv("JIRA_API_TOKEN"),
    organization=os.getenv("JIRA_EMAIL"),
    project=os.getenv("JIRA_PROJECT"),
    timeout=30,
    retry_attempts=3,
)

# Method 2: Using python-dotenv
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

config = PluginConfig(
    plugin_id="jira",
    api_endpoint=os.getenv("JIRA_URL"),
    api_key=os.getenv("JIRA_API_TOKEN"),
    organization=os.getenv("JIRA_EMAIL"),
    project=os.getenv("JIRA_PROJECT"),
)

# Method 3: From YAML config file
import yaml

with open("config/jira_config.yaml") as f:
    cfg = yaml.safe_load(f)

config = PluginConfig(
    plugin_id="jira",
    api_endpoint=cfg["jira"]["url"],
    api_key=os.getenv(cfg["jira"]["api_token"].strip("${}")),
    organization=os.getenv(cfg["jira"]["email"].strip("${}")),
    project=cfg["jira"]["project"],
)

# Initialize plugin
plugin = JiraPlugin()

# Authenticate
try:
    plugin.authenticate(config)
    print("✅ Authentication successful!")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
```

### Validation Script

Test your configuration:

```python
#!/usr/bin/env python3
"""
JIRA Configuration Validation Script
"""

import os
from sdk import PluginConfig
from integrations.jira import JiraPlugin


def validate_jira_config():
    """Validate JIRA configuration and authentication"""

    print("🔍 Validating JIRA Configuration...")
    print()

    # Check environment variables
    required_vars = {
        "JIRA_URL": os.getenv("JIRA_URL"),
        "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN"),
        "JIRA_EMAIL": os.getenv("JIRA_EMAIL"),
        "JIRA_PROJECT": os.getenv("JIRA_PROJECT"),
    }

    print("1. Checking environment variables:")
    all_set = True
    for var, value in required_vars.items():
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"   ✅ {var}: {masked}")
        else:
            print(f"   ❌ {var}: NOT SET")
            all_set = False

    if not all_set:
        print()
        print("❌ Missing required environment variables!")
        print("   Please set all required variables and try again.")
        return False

    print()

    # Create configuration
    print("2. Creating plugin configuration:")
    try:
        config = PluginConfig(
            plugin_id="jira-validation",
            api_endpoint=required_vars["JIRA_URL"],
            api_key=required_vars["JIRA_API_TOKEN"],
            organization=required_vars["JIRA_EMAIL"],
            project=required_vars["JIRA_PROJECT"],
        )
        print("   ✅ Configuration created")
    except Exception as e:
        print(f"   ❌ Configuration failed: {e}")
        return False

    print()

    # Test authentication
    print("3. Testing authentication:")
    try:
        plugin = JiraPlugin()
        plugin.authenticate(config)
        print("   ✅ Authentication successful")
    except Exception as e:
        print(f"   ❌ Authentication failed: {e}")
        return False

    print()

    # Test basic operations
    print("4. Testing basic operations:")

    # Get current user
    try:
        user = plugin.client.myself()
        print(f"   ✅ Current user: {user['displayName']}")
    except Exception as e:
        print(f"   ❌ Failed to get user: {e}")
        return False

    # Search for issues
    try:
        jql = f"project = {config.project} ORDER BY created DESC"
        issues = plugin.client.search_issues(jql, maxResults=5)
        print(f"   ✅ Found {len(issues)} issues in project {config.project}")
        if issues:
            print(f"   ℹ️  Latest issue: {issues[0].key} - {issues[0].fields.summary}")
    except Exception as e:
        print(f"   ❌ Failed to search issues: {e}")
        return False

    print()
    print("="  * 60)
    print("✅ All validation checks passed!")
    print("="  * 60)
    return True


if __name__ == "__main__":
    import sys

    success = validate_jira_config()
    sys.exit(0 if success else 1)
```

Run validation:

```bash
python validate_jira_config.py
```

---

## Token Management

### Viewing Active Tokens

1. Navigate to: https://id.atlassian.com/manage-profile/security/api-tokens

2. View all active tokens with:
   - Label
   - Creation date
   - Last accessed date

### Revoking Tokens

To revoke a token:

1. Go to API tokens page
2. Find the token to revoke
3. Click **Revoke** button
4. Confirm revocation

**When to revoke:**
- Token is compromised
- Token no longer needed
- Team member leaving
- During security audit
- Before extended leave

### Token Best Practices

```bash
# Token naming convention
Format: {Purpose} - {Environment} - {Date}

Examples:
✅ "DevOps Plugin - Production - 2026-01"
✅ "CI/CD Pipeline - Staging - Jan 2026"
✅ "Defect Management - Dev - 2026-01-03"

# Token inventory
Maintain a list of:
- Token labels
- Creation dates
- Purpose/usage
- Responsible team
- Next rotation date
```

---

## Troubleshooting

### Common Issues

#### 1. "Unauthorized" Error (401)

**Symptoms:**
```python
jira.exceptions.JIRAError: JiraError HTTP 401 url: https://your-company.atlassian.net/rest/api/2/issue/PROJ-123
text: Basic authentication with passwords is deprecated.
```

**Causes & Solutions:**

**Issue**: Using password instead of API token
```bash
# Solution: Use API token, not password
# Get token from: https://id.atlassian.com/manage-profile/security/api-tokens
```

**Issue**: Token format incorrect
```bash
# Token should be 24 characters
# Format: Atatt3xFfGF0AbCdEfGhIjKlMnOp

# Check length
echo "$JIRA_API_TOKEN" | wc -c  # Should be 25 (24 + newline)
```

**Issue**: Wrong email address
```bash
# Must use email associated with JIRA account
# Verify in: JIRA → Profile → Email
```

#### 2. "Forbidden" Error (403)

**Symptoms:**
```python
jira.exceptions.JIRAError: JiraError HTTP 403
text: You do not have permission to perform this operation
```

**Causes & Solutions:**

**Issue**: Insufficient JIRA permissions
```bash
# Solution: Project admin must grant permissions
# Required permissions:
# - Browse Projects
# - Create/Edit Issues
# - Add Comments
```

**Issue**: Project access denied
```bash
# Solution: Request access to project
# JIRA → Project Settings → People → Request access
```

#### 3. "Not Found" Error (404)

**Symptoms:**
```python
jira.exceptions.JIRAError: JiraError HTTP 404
text: Issue Does Not Exist
```

**Causes & Solutions:**

**Issue**: Incorrect JIRA URL
```bash
# Check URL format
# Correct: https://your-company.atlassian.net
# Wrong: https://your-company.atlassian.net/
# Wrong: https://your-company.jira.com
```

**Issue**: Invalid project key
```bash
# Project keys are case-sensitive
# Find correct key: JIRA → Project Settings → Details
```

#### 4. SSL Certificate Errors

**Symptoms:**
```python
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Causes & Solutions:**

**Issue**: Corporate proxy or firewall
```python
# Solution: Disable SSL verification (not recommended for production)
config = PluginConfig(
    ...
    verify_ssl=False  # ⚠️ Only for development!
)
```

**Better solution**: Install corporate SSL certificate
```bash
# Ubuntu/Debian
sudo apt-get install ca-certificates
sudo update-ca-certificates

# macOS
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain corporate-cert.crt
```

### Debug Mode

Enable detailed logging:

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now run your code
plugin.authenticate(config)
# Will show detailed HTTP requests/responses
```

### Manual Testing

Test token with curl:

```bash
# Basic authentication test
curl -u your-email@company.com:YOUR_API_TOKEN \
  -X GET \
  -H "Content-Type: application/json" \
  https://your-company.atlassian.net/rest/api/2/myself

# Expected: Your user profile information
# If error: Check email and token
```

Test with Python:

```python
import requests
from requests.auth import HTTPBasicAuth

email = "your-email@company.com"
api_token = "YOUR_API_TOKEN"
jira_url = "https://your-company.atlassian.net"

# Test authentication
response = requests.get(
    f"{jira_url}/rest/api/2/myself",
    auth=HTTPBasicAuth(email, api_token)
)

if response.status_code == 200:
    print("✅ Authentication successful!")
    print(f"User: {response.json()['displayName']}")
else:
    print(f"❌ Authentication failed: {response.status_code}")
    print(response.text)
```

---

## FAQ

### Q1: Do JIRA API tokens expire?

**A**: No, JIRA API tokens do not expire automatically. However, they should be rotated regularly for security (recommended: every 90 days).

### Q2: Can I use the same token for multiple projects?

**A**: Yes! One token works across all JIRA projects you have access to. Token permissions match your user permissions.

### Q3: What happens if I forget my API token?

**A**: You cannot retrieve a forgotten token. You must:
1. Revoke the old token
2. Create a new token
3. Update all configurations

### Q4: Can I have multiple API tokens?

**A**: Yes! You can create multiple tokens for:
- Different environments (dev, staging, prod)
- Different applications
- Different team members

### Q5: Is it safe to use API tokens?

**A**: Yes, when properly managed:
- More secure than passwords
- Can be revoked without changing password
- Should be stored securely
- Should be rotated regularly

### Q6: Can I regenerate an existing token?

**A**: No, tokens cannot be regenerated. You must:
1. Create a new token
2. Update configurations
3. Revoke old token

### Q7: What's the difference between API token and OAuth?

**A**:
- **API Token**: Simpler, user-based, full user permissions
- **OAuth**: More complex, app-based, granular permissions
- For most use cases, API token is sufficient

### Q8: Can I restrict token permissions?

**A**: No, API tokens inherit your user permissions. To restrict:
- Use a service account with limited permissions
- Create token for that account

### Q9: How do I audit token usage?

**A**:
1. Go to JIRA Settings
2. Select "System"
3. Click "Audit log"
4. Filter by your user
5. Look for API access events

### Q10: What if my token stops working?

**A**: Check these common causes:
- Token revoked accidentally
- User account disabled
- Project permissions changed
- JIRA instance migrated
- Network/firewall issues

---

## Additional Resources

### Official Documentation
- [Atlassian API Tokens](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)
- [JIRA REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/)
- [JIRA Python Library](https://jira.readthedocs.io/)

### Related Guides
- [Azure PAT Setup Guide](AZURE_PAT_SETUP.md)
- [LLM Requirements](LLM_REQUIREMENTS.md)
- [Agent Requirements](AGENT_REQUIREMENTS.md)
- [Marketplace Deployment](../deployment/MARKETPLACE_DEPLOYMENT.md)

### Support
- **Issues**: https://github.com/yourcompany/databricks-platform-marketplace/issues
- **Slack**: #devops-integrations
- **Email**: platform-team@vivekgana.com

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-03 | Databricks Platform Team | Initial documentation |

---

**Maintained by**: Databricks Platform Team
**Last Review**: 2026-01-03
**Next Review**: 2026-04-03
