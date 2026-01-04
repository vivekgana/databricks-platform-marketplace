# Azure DevOps Personal Access Token (PAT) Setup Guide

**Document Version:** 1.0
**Last Updated:** 2026-01-03 11:11:20
**Prepared by:** Databricks Platform Team

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Creating a Personal Access Token](#creating-a-personal-access-token)
4. [Configuring Token Scopes](#configuring-token-scopes)
5. [Security Best Practices](#security-best-practices)
6. [Configuration for DevOps Plugins](#configuration-for-devops-plugins)
7. [Token Management](#token-management)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Overview

A Personal Access Token (PAT) is required to authenticate with Azure DevOps REST APIs. This guide walks you through creating and configuring a PAT for use with the Databricks DevOps Integration plugins.

### What is a PAT?

A Personal Access Token is an alternative to using passwords for authentication to Azure DevOps. PATs:
- Provide fine-grained access control
- Can be scoped to specific operations
- Can have expiration dates
- Can be revoked at any time
- Are organization-specific

---

## Prerequisites

Before creating a PAT, ensure you have:

1. **Azure DevOps Account**
   - Active Azure DevOps organization
   - User account with appropriate permissions
   - Access to the target project(s)

2. **Required Permissions**
   - Project Administrator (recommended) OR
   - Stakeholder with specific permissions:
     - Work Items: Read & Write
     - Code: Read
     - Build: Read
     - Release: Read

3. **Web Browser**
   - Modern browser (Chrome, Firefox, Edge, Safari)
   - Logged into Azure DevOps

4. **Environment Variables Setup**

   After creating your PAT, you'll need to configure these environment variables:

   **Windows (PowerShell):**
   ```powershell
   # Azure DevOps Configuration
   [System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_ORG_URL', 'https://dev.azure.com/your-org', 'User')
   [System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', 'your-52-character-pat-token', 'User')
   [System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PROJECT', 'YourProject', 'User')
   ```

   **Linux/Mac (Bash/Zsh):**
   ```bash
   # Azure DevOps Configuration
   export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-org"
   export AZURE_DEVOPS_PAT="your-52-character-pat-token"
   export AZURE_DEVOPS_PROJECT="YourProject"

   # Add to ~/.bashrc or ~/.zshrc for persistence
   echo 'export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-org"' >> ~/.bashrc
   echo 'export AZURE_DEVOPS_PAT="your-52-character-pat-token"' >> ~/.bashrc
   echo 'export AZURE_DEVOPS_PROJECT="YourProject"' >> ~/.bashrc
   ```

   **Docker/Container Environment:**
   ```bash
   # In docker-compose.yml or .env file
   AZURE_DEVOPS_ORG_URL=https://dev.azure.com/your-org
   AZURE_DEVOPS_PAT=your-52-character-pat-token
   AZURE_DEVOPS_PROJECT=YourProject
   ```

   **Environment Variable Descriptions:**
   - `AZURE_DEVOPS_ORG_URL`: Your Azure DevOps organization URL
   - `AZURE_DEVOPS_PAT`: The Personal Access Token you'll create (52 characters)
   - `AZURE_DEVOPS_PROJECT`: The project name you want to access

   **Security Note:** Never commit these values to version control. Use `.env` files that are in `.gitignore` or secure secret management systems.

---

## Creating a Personal Access Token

### Step 1: Navigate to Security Settings

1. Sign in to your Azure DevOps organization:
   ```
   https://dev.azure.com/{your-organization}
   ```

2. Click on your **profile picture** in the top right corner

3. Select **Personal access tokens** from the dropdown menu

   ![Azure DevOps Profile Menu](../images/ado-profile-menu.png)

### Step 2: Create New Token

1. Click the **+ New Token** button

2. Fill in the token details:

   **Name**: `Databricks DevOps Integration`
   - Use a descriptive name to identify the token's purpose
   - Example: "Databricks DevOps Plugin - Production"

   **Organization**: Select your organization
   - Choose the organization you want to access
   - Can be set to "All accessible organizations" for multi-org access

   **Expiration**: Set token expiration
   - **Recommended**: 90 days (good balance of security and convenience)
   - **Maximum**: 1 year
   - **For testing**: 30 days
   - **For production**: 90-180 days with renewal reminders

### Step 3: Configure Scopes

Select the appropriate scopes based on your needs:

#### Minimum Required Scopes ✅

```
✅ Work Items: Read & Write
✅ Code: Read
```

#### Recommended Scopes for Full Functionality ⭐

```
✅ Work Items: Read & Write
✅ Code: Read
✅ Build: Read
✅ Release: Read
✅ Project and Team: Read
✅ Graph: Read (for user lookups)
```

#### Optional Scopes (for Advanced Features)

```
○ Code: Read & Write (if creating branches/commits)
○ Build: Read & Execute (if triggering builds)
○ Release: Read & Execute (if triggering deployments)
○ Notifications: Read & Write (for webhook management)
```

### Step 4: Create and Copy Token

1. Click **Create** button

2. **IMPORTANT**: Copy the token immediately!
   ```
   Token will look like: 52-character alphanumeric string
   Example: abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmn
   ```

3. **Store securely** - You won't be able to see it again!
   - Use a password manager (1Password, LastPass, etc.)
   - Or store in secure credential vault
   - Never commit to source control

---

## Configuring Token Scopes

### Detailed Scope Descriptions

#### Work Items (Required)

| Scope | Permission | Use Case |
|-------|-----------|----------|
| **Read** | View work items | - Search and retrieve work items<br>- Get work item details<br>- Query work items |
| **Write** | Create/Update work items | - Create new bugs/tasks<br>- Update work item fields<br>- Add comments<br>- Link work items |

**Why Required**: Core functionality for defect management and work item tracking.

#### Code (Recommended)

| Scope | Permission | Use Case |
|-------|-----------|----------|
| **Read** | View repository code | - Link work items to commits<br>- Analyze code changes<br>- View file contents |
| **Write** | Modify repository | - Create branches (optional)<br>- Push commits (optional) |

**Why Recommended**: Enables linking work items to code changes and PR integration.

#### Build (Recommended)

| Scope | Permission | Use Case |
|-------|-----------|----------|
| **Read** | View build pipelines | - Link work items to builds<br>- Track CI/CD status<br>- Get build artifacts |
| **Execute** | Trigger builds | - Automatically trigger builds (optional) |

**Why Recommended**: For CI/CD integration and automated testing.

#### Release (Recommended)

| Scope | Permission | Use Case |
|-------|-----------|----------|
| **Read** | View releases | - Track deployment status<br>- Link work items to releases |
| **Execute** | Trigger releases | - Automated deployments (optional) |

#### Project and Team (Recommended)

| Scope | Permission | Use Case |
|-------|-----------|----------|
| **Read** | View projects/teams | - Get project metadata<br>- List team members<br>- Calculate team velocity |

#### Graph (Optional)

| Scope | Permission | Use Case |
|-------|-----------|----------|
| **Read** | Access user graph | - User lookups<br>- Auto-assignment features |

---

## Security Best Practices

### 1. Token Storage

**✅ DO:**
- Store in environment variables
- Use secret management tools (Azure Key Vault, AWS Secrets Manager)
- Use password managers for development
- Encrypt tokens at rest

**❌ DON'T:**
- Commit to Git repositories
- Share via email or chat
- Store in plain text files
- Hard-code in application code

### 2. Token Rotation

```bash
# Set up rotation schedule
# Production: Rotate every 90 days
# Development: Rotate every 30 days

# Add to calendar reminders
# 7 days before expiration: Generate new token
# 3 days before expiration: Update configuration
# On expiration: Remove old token
```

### 3. Principle of Least Privilege

Only grant necessary scopes:

```yaml
# Good: Minimal scopes
scopes:
  - Work Items: Read & Write
  - Code: Read

# Avoid: Excessive scopes
scopes:
  - Full access  # Too permissive!
```

### 4. Token Auditing

Monitor token usage:

```bash
# Regular audit checklist
□ Review active tokens monthly
□ Revoke unused tokens
□ Check access logs for suspicious activity
□ Verify token scopes match requirements
□ Update documentation when tokens change
```

### 5. Incident Response

If token is compromised:

1. **Immediate Actions**:
   ```bash
   # Revoke token immediately
   # Navigate to: Azure DevOps → User Settings → Personal Access Tokens
   # Click token → Revoke
   ```

2. **Investigation**:
   - Check access logs
   - Identify what was accessed
   - Assess impact

3. **Recovery**:
   - Generate new token
   - Update all configurations
   - Notify team

4. **Prevention**:
   - Review security practices
   - Update documentation
   - Add monitoring

---

## Configuration for DevOps Plugins

### Environment Variables Method (Recommended)

```bash
# Linux/Mac
export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-organization"
export AZURE_DEVOPS_PAT="your-52-character-pat-token"
export AZURE_DEVOPS_PROJECT="YourProjectName"

# Windows PowerShell
$env:AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-organization"
$env:AZURE_DEVOPS_PAT="your-52-character-pat-token"
$env:AZURE_DEVOPS_PROJECT="YourProjectName"

# Windows Command Prompt
set AZURE_DEVOPS_ORG_URL=https://dev.azure.com/your-organization
set AZURE_DEVOPS_PAT=your-52-character-pat-token
set AZURE_DEVOPS_PROJECT=YourProjectName
```

### Configuration File Method

Create `config/azure_devops_config.yaml`:

```yaml
azure_devops:
  # Organization URL
  org_url: "https://dev.azure.com/your-organization"

  # Personal Access Token (use environment variable reference)
  pat: "${AZURE_DEVOPS_PAT}"

  # Default project
  project: "YourProjectName"

  # Optional: Additional settings
  api_version: "7.0"
  timeout: 30
  retry_attempts: 3
  verify_ssl: true

  # Team configuration (optional)
  default_team: "Platform Team"
  area_path: "YourProjectName\\Platform"
  iteration_path: "YourProjectName\\Sprint 1"
```

### Python Configuration

```python
from sdk import PluginConfig
import os

# Method 1: From environment variables
config = PluginConfig(
    plugin_id="azure-devops",
    api_endpoint=os.getenv("AZURE_DEVOPS_ORG_URL"),
    api_key=os.getenv("AZURE_DEVOPS_PAT"),
    organization=os.getenv("AZURE_DEVOPS_ORG_URL").split("/")[-1],
    project=os.getenv("AZURE_DEVOPS_PROJECT"),
)

# Method 2: Direct configuration (development only)
config = PluginConfig(
    plugin_id="azure-devops",
    api_endpoint="https://dev.azure.com/your-org",
    api_key="your-pat-token",  # ⚠️ Never commit this!
    organization="your-org",
    project="YourProject",
)

# Method 3: From config file
import yaml

with open("config/azure_devops_config.yaml") as f:
    cfg = yaml.safe_load(f)

config = PluginConfig(
    plugin_id="azure-devops",
    api_endpoint=cfg["azure_devops"]["org_url"],
    api_key=os.getenv(cfg["azure_devops"]["pat"].strip("${}")),
    organization=cfg["azure_devops"]["org_url"].split("/")[-1],
    project=cfg["azure_devops"]["project"],
)
```

### Validation

Test your configuration:

```python
from integrations.azure_devops import AzureDevOpsPlugin

# Initialize plugin
plugin = AzureDevOpsPlugin()

# Test authentication
try:
    authenticated = plugin.authenticate(config)
    if authenticated:
        print("✅ Authentication successful!")

        # Test basic operations
        work_item = plugin.get_work_item("12345", config)
        print(f"✅ Successfully retrieved work item: {work_item.title}")
    else:
        print("❌ Authentication failed")
except Exception as e:
    print(f"❌ Error: {e}")
```

---

## Token Management

### Viewing Active Tokens

1. Navigate to **User Settings** → **Personal access tokens**
2. View all active tokens with:
   - Name
   - Creation date
   - Expiration date
   - Scopes
   - Last used date

### Revoking Tokens

To revoke a token:

1. Go to **Personal access tokens** page
2. Find the token to revoke
3. Click **Revoke** button
4. Confirm revocation

**When to revoke:**
- Token is compromised
- Token is no longer needed
- Before team member leaves
- During security audit

### Regenerating Tokens

Tokens cannot be regenerated. To replace:

1. Create new token with same scopes
2. Update all configurations
3. Test new token
4. Revoke old token

### Token Expiration Handling

```python
# Automated expiration handling
from datetime import datetime, timedelta

def check_token_expiration(expiration_date):
    """Check if token is expiring soon"""
    days_until_expiration = (expiration_date - datetime.now()).days

    if days_until_expiration <= 7:
        print(f"⚠️  Token expires in {days_until_expiration} days!")
        print("Action required: Generate new token")
        return True
    elif days_until_expiration <= 30:
        print(f"ℹ️  Token expires in {days_until_expiration} days")
        print("Consider generating new token soon")
    return False

# Usage
expiration = datetime(2026, 04, 01)  # Your token expiration
check_token_expiration(expiration)
```

---

## Troubleshooting

### Common Issues

#### 1. "Unauthorized" Error (401)

**Symptoms:**
```
Error: 401 Unauthorized
Authentication failed
```

**Causes & Solutions:**

**Issue**: Token expired
```bash
# Solution: Generate new token
# Check expiration: User Settings → Personal access tokens
```

**Issue**: Token revoked
```bash
# Solution: Create new token
```

**Issue**: Incorrect token format
```bash
# Solution: Verify token is 52-character string
# No spaces or special characters
echo "$AZURE_DEVOPS_PAT" | wc -c  # Should be 52
```

#### 2. "Forbidden" Error (403)

**Symptoms:**
```
Error: 403 Forbidden
Access denied to resource
```

**Causes & Solutions:**

**Issue**: Insufficient scopes
```bash
# Solution: Recreate token with correct scopes
# Required: Work Items (Read & Write), Code (Read)
```

**Issue**: User lacks project permissions
```bash
# Solution: Project admin must grant permissions
# Settings → Permissions → Add user
```

#### 3. "Not Found" Error (404)

**Symptoms:**
```
Error: 404 Not Found
Project or organization not found
```

**Causes & Solutions:**

**Issue**: Incorrect organization URL
```bash
# Wrong
https://dev.azure.com/yourorg/  # Trailing slash
https://yourorg.visualstudio.com/  # Old format

# Correct
https://dev.azure.com/yourorg
```

**Issue**: Incorrect project name
```bash
# Project names are case-sensitive
Project name: "MyProject"
Not: "myproject" or "MYPROJECT"
```

#### 4. Token Not Working After Creation

**Checklist:**
```bash
□ Token copied completely (52 characters)
□ No extra spaces before/after token
□ Correct scopes selected
□ Token not expired
□ Organization URL correct
□ Project name correct (case-sensitive)
□ User has project access
```

### Debug Mode

Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Now run your code
plugin.authenticate(config)
# Will show detailed authentication flow
```

### Testing Token Manually

```bash
# Using curl
curl -u :YOUR_PAT_TOKEN \
  https://dev.azure.com/YOUR_ORG/_apis/projects?api-version=7.0

# Expected: List of projects
# If error: Check token and permissions
```

```powershell
# Using PowerShell
$token = "YOUR_PAT_TOKEN"
$base64Token = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$token"))

$headers = @{
    Authorization = "Basic $base64Token"
}

Invoke-RestMethod -Uri "https://dev.azure.com/YOUR_ORG/_apis/projects?api-version=7.0" `
    -Headers $headers
```

---

## FAQ

### Q1: How long should I set the token expiration?

**A**:
- **Production**: 90 days (with rotation reminders)
- **Development**: 30 days
- **Testing**: 7-14 days
- **Maximum**: 1 year (not recommended)

### Q2: Can I use the same token for multiple projects?

**A**: Yes! When creating the token:
- Set Organization to "All accessible organizations"
- The token will work across all projects you have access to

### Q3: What happens when my token expires?

**A**:
- All API calls will fail with 401 Unauthorized
- You must generate a new token
- Update all configurations with new token
- Old token cannot be renewed

### Q4: Can I have multiple active tokens?

**A**: Yes! You can create multiple PATs:
- One for each environment (dev, staging, prod)
- One for each application
- One for each team member
- Maximum: 200 tokens per organization

### Q5: How do I rotate tokens without downtime?

**A**:
```bash
# 1. Generate new token (7 days before expiration)
NEW_TOKEN="new-52-char-token"

# 2. Test new token
test_authentication $NEW_TOKEN

# 3. Update configuration
update_config $NEW_TOKEN

# 4. Deploy updated configuration

# 5. Verify services using new token

# 6. Revoke old token
```

### Q6: Can I use Azure CLI credentials instead of PAT?

**A**: No, the DevOps plugins require PAT for authentication. Azure CLI credentials are not supported.

### Q7: Is my PAT encrypted?

**A**:
- PATs are encrypted in transit (HTTPS)
- Store encrypted at rest (use Key Vault)
- Never store in plain text
- Use environment variables

### Q8: Can I automate PAT creation?

**A**: No, PATs must be created manually through the web interface for security reasons.

### Q9: What if someone else needs access?

**A**:
- Don't share your PAT!
- Each person should create their own PAT
- Use service accounts for shared automation
- Grant project access to new users

### Q10: How do I audit PAT usage?

**A**:
1. Navigate to Organization Settings
2. Select "Auditing"
3. Filter by "Token" events
4. Review access logs

---

## Additional Resources

### Official Documentation
- [Azure DevOps PAT Documentation](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate)
- [Azure DevOps REST API](https://docs.microsoft.com/en-us/rest/api/azure/devops)
- [Security Best Practices](https://docs.microsoft.com/en-us/azure/devops/organizations/security/security-best-practices)

### Related Guides
- [JIRA Token Setup Guide](JIRA_TOKEN_SETUP.md)
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
