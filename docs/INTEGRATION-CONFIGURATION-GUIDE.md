# Integration Configuration Guide

**Document Version:** 1.0
**Prepared by:** gekambaram
**Last Updated:** 2026-01-19 14:52:00
**Contact:** data-platform@vivekgana.com

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Azure DevOps (ADO) Configuration](#azure-devops-ado-configuration)
4. [Jira Configuration](#jira-configuration)
5. [Source Control Configuration](#source-control-configuration)
6. [CI/CD Pipeline Configuration](#cicd-pipeline-configuration)
7. [Claude CLI Integration](#claude-cli-integration)
8. [Validation Commands](#validation-commands)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Overview

This guide provides step-by-step instructions for configuring Jira, Azure DevOps, source control systems, and CI/CD pipelines to work seamlessly with Claude CLI after npm installation.

### Integration Architecture

:::mermaid
graph TB
    A[Claude CLI] --> B[Azure DevOps]
    A --> C[Jira]
    A --> D[Git/GitHub/GitLab]
    A --> E[CI/CD Pipelines]
    B --> F[Work Items]
    B --> G[Repositories]
    B --> H[Pipelines]
    C --> I[Issues/Stories]
    C --> J[Epics]
    D --> K[Code Repository]
    E --> L[Build Pipeline]
    E --> M[Release Pipeline]
:::

---

## Prerequisites

### System Requirements

- Node.js >= 18.0.0
- npm >= 9.0.0
- Python >= 3.8 (for CLI tools)
- Git >= 2.30.0
- Azure CLI >= 2.50.0
- Claude CLI installed

### Installation Verification

```bash
# Verify Node.js installation
node --version

# Verify npm installation
npm --version

# Verify Python installation
python --version

# Verify Git installation
git --version

# Verify Azure CLI installation
az --version

# Verify Claude CLI installation
claude --version
```

### Required Access Permissions

- Azure DevOps: Project Administrator or Contributor
- Jira: Project Admin or Developer role
- Git Repository: Write access
- CI/CD: Pipeline creation and execution permissions

---

## Azure DevOps (ADO) Configuration

### Step 1: Install Azure CLI

```bash
# Windows (via Chocolatey)
choco install azure-cli

# Or via MSI installer from:
# https://aka.ms/installazurecliwindows

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# macOS
brew install azure-cli
```

### Step 2: Install Azure DevOps Extension

```bash
# Install the Azure DevOps extension for Azure CLI
az extension add --name azure-devops

# Verify installation
az extension list --output table
```

### Step 3: Authenticate with Azure DevOps

```bash
# Interactive login with device code
az login --use-device-code

# Alternative: Login with service principal
az login --service-principal \
  --username <app-id> \
  --password <password-or-cert> \
  --tenant <tenant-id>
```

### Step 4: Configure Azure DevOps Defaults

```bash
# Set default organization
az devops configure --defaults organization=https://dev.azure.com/YourOrganization

# Set default project
az devops configure --defaults project=YourProject

# View current configuration
az devops configure --list
```

### Step 5: Create Personal Access Token (PAT)

1. Navigate to Azure DevOps: `https://dev.azure.com/YourOrganization`
2. Click on User Settings (top right) → Personal Access Tokens
3. Click "New Token"
4. Configure token:
   - Name: `Claude-CLI-Integration`
   - Organization: `YourOrganization`
   - Expiration: 90 days (or custom)
   - Scopes:
     - ✅ Code (Read, Write, Manage)
     - ✅ Work Items (Read, Write)
     - ✅ Build (Read, Execute)
     - ✅ Release (Read, Write, Execute)
     - ✅ Pull Request (Read, Write, Contribute)
5. Copy the generated token

### Step 6: Store PAT Securely

```bash
# Windows - Store in environment variable
setx AZURE_DEVOPS_EXT_PAT "your-pat-token-here"

# Linux/macOS - Add to ~/.bashrc or ~/.zshrc
echo 'export AZURE_DEVOPS_EXT_PAT="your-pat-token-here"' >> ~/.bashrc
source ~/.bashrc

# Verify PAT is set
echo $AZURE_DEVOPS_EXT_PAT
```

### Step 7: Configure ADO for Claude CLI

Create ADO configuration file:

```bash
# Create .ado-config.json in project root
cat > .ado-config.json << 'EOF'
{
  "organization": "https://dev.azure.com/YourOrganization",
  "project": "YourProject",
  "repository": "YourRepository",
  "defaultBranch": "main",
  "workItemTypes": {
    "epic": "Epic",
    "feature": "Feature",
    "userStory": "User Story",
    "task": "Task",
    "bug": "Bug"
  },
  "areaPath": "YourProject\\YourTeam",
  "iterationPath": "YourProject\\Sprint 1",
  "pullRequestSettings": {
    "autoComplete": false,
    "deleteSourceBranch": true,
    "squashMerge": false,
    "transitionWorkItems": true,
    "requireReviewers": true,
    "minimumReviewers": 2
  }
}
EOF
```

### Validation Commands for ADO

```bash
# Validate Azure CLI authentication
az account show

# Validate Azure DevOps extension
az devops project list --organization https://dev.azure.com/YourOrganization

# Validate repository access
az repos list --organization https://dev.azure.com/YourOrganization --project YourProject

# Validate work item access
az boards work-item create \
  --title "Test Work Item - Claude CLI" \
  --type Task \
  --organization https://dev.azure.com/YourOrganization \
  --project YourProject

# Validate PR creation capability
az repos pr list \
  --organization https://dev.azure.com/YourOrganization \
  --project YourProject

# Validate pipeline access
az pipelines list \
  --organization https://dev.azure.com/YourOrganization \
  --project YourProject
```

---

## Jira Configuration

### Step 1: Install Jira CLI

```bash
# Install via npm
npm install -g jira-cli

# Or install Python-based jira-python
pip install jira

# Or install Atlassian CLI
npm install -g @atlassian/jira-cli
```

### Step 2: Create Jira API Token

1. Navigate to: `https://id.atlassian.com/manage-profile/security/api-tokens`
2. Click "Create API token"
3. Label: `Claude-CLI-Integration`
4. Copy the generated token

### Step 3: Configure Jira Credentials

```bash
# Create .jira-config.json in project root
cat > .jira-config.json << 'EOF'
{
  "host": "https://your-domain.atlassian.net",
  "username": "your-email@company.com",
  "apiToken": "your-api-token-here",
  "defaultProject": "PROJ",
  "issueTypes": {
    "epic": "Epic",
    "story": "Story",
    "task": "Task",
    "bug": "Bug",
    "subtask": "Sub-task"
  },
  "customFields": {
    "storyPoints": "customfield_10016",
    "sprint": "customfield_10020",
    "epic": "customfield_10014"
  },
  "workflow": {
    "todo": "To Do",
    "inProgress": "In Progress",
    "codeReview": "Code Review",
    "done": "Done"
  }
}
EOF

# Store credentials securely in environment variables
# Windows
setx JIRA_HOST "https://your-domain.atlassian.net"
setx JIRA_USERNAME "your-email@company.com"
setx JIRA_API_TOKEN "your-api-token-here"

# Linux/macOS
echo 'export JIRA_HOST="https://your-domain.atlassian.net"' >> ~/.bashrc
echo 'export JIRA_USERNAME="your-email@company.com"' >> ~/.bashrc
echo 'export JIRA_API_TOKEN="your-api-token-here"' >> ~/.bashrc
source ~/.bashrc
```

### Step 4: Configure Jira for Claude CLI

Create Jira integration script:

```bash
# Create jira-integration.sh (Linux/macOS) or jira-integration.ps1 (Windows)
cat > jira-integration.sh << 'EOF'
#!/bin/bash

# Jira Integration Helper for Claude CLI

JIRA_HOST="${JIRA_HOST:-https://your-domain.atlassian.net}"
JIRA_USERNAME="${JIRA_USERNAME}"
JIRA_API_TOKEN="${JIRA_API_TOKEN}"

# Function to create Jira issue
create_jira_issue() {
  local issue_type=$1
  local summary=$2
  local description=$3
  local project=$4

  curl -X POST \
    -H "Content-Type: application/json" \
    -u "${JIRA_USERNAME}:${JIRA_API_TOKEN}" \
    "${JIRA_HOST}/rest/api/3/issue" \
    -d "{
      \"fields\": {
        \"project\": {\"key\": \"${project}\"},
        \"summary\": \"${summary}\",
        \"description\": {
          \"type\": \"doc\",
          \"version\": 1,
          \"content\": [{
            \"type\": \"paragraph\",
            \"content\": [{\"type\": \"text\", \"text\": \"${description}\"}]
          }]
        },
        \"issuetype\": {\"name\": \"${issue_type}\"}
      }
    }"
}

# Function to transition Jira issue
transition_jira_issue() {
  local issue_key=$1
  local transition_id=$2

  curl -X POST \
    -H "Content-Type: application/json" \
    -u "${JIRA_USERNAME}:${JIRA_API_TOKEN}" \
    "${JIRA_HOST}/rest/api/3/issue/${issue_key}/transitions" \
    -d "{\"transition\": {\"id\": \"${transition_id}\"}}"
}

# Function to add comment to Jira issue
add_jira_comment() {
  local issue_key=$1
  local comment=$2

  curl -X POST \
    -H "Content-Type: application/json" \
    -u "${JIRA_USERNAME}:${JIRA_API_TOKEN}" \
    "${JIRA_HOST}/rest/api/3/issue/${issue_key}/comment" \
    -d "{
      \"body\": {
        \"type\": \"doc\",
        \"version\": 1,
        \"content\": [{
          \"type\": \"paragraph\",
          \"content\": [{\"type\": \"text\", \"text\": \"${comment}\"}]
        }]
      }
    }"
}

# Export functions
export -f create_jira_issue
export -f transition_jira_issue
export -f add_jira_comment
EOF

chmod +x jira-integration.sh
```

### Validation Commands for Jira

```bash
# Test Jira API connection
curl -u your-email@company.com:your-api-token \
  https://your-domain.atlassian.net/rest/api/3/myself

# Test project access
curl -u your-email@company.com:your-api-token \
  https://your-domain.atlassian.net/rest/api/3/project

# Test issue creation
curl -X POST \
  -H "Content-Type: application/json" \
  -u your-email@company.com:your-api-token \
  https://your-domain.atlassian.net/rest/api/3/issue \
  -d '{
    "fields": {
      "project": {"key": "PROJ"},
      "summary": "Test Issue - Claude CLI",
      "issuetype": {"name": "Task"},
      "description": {
        "type": "doc",
        "version": 1,
        "content": [{
          "type": "paragraph",
          "content": [{"type": "text", "text": "Test issue created by Claude CLI"}]
        }]
      }
    }
  }'

# Verify transitions available for an issue
curl -u your-email@company.com:your-api-token \
  https://your-domain.atlassian.net/rest/api/3/issue/PROJ-123/transitions

# Test search functionality
curl -u your-email@company.com:your-api-token \
  'https://your-domain.atlassian.net/rest/api/3/search?jql=project=PROJ&maxResults=5'
```

---

## Source Control Configuration

### GitHub Configuration

#### Step 1: Install GitHub CLI

```bash
# Windows (via Chocolatey)
choco install gh

# Or via Scoop
scoop install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# macOS
brew install gh
```

#### Step 2: Authenticate GitHub CLI

```bash
# Authenticate with GitHub
gh auth login

# Select options:
# - GitHub.com
# - HTTPS
# - Yes (authenticate Git with GitHub credentials)
# - Login with a web browser (or paste authentication token)

# Verify authentication
gh auth status
```

#### Step 3: Configure Git

```bash
# Configure Git user
git config --global user.name "Your Name"
git config --global user.email "your-email@company.com"

# Configure default branch
git config --global init.defaultBranch main

# Configure pull strategy
git config --global pull.rebase false

# Configure credential helper
git config --global credential.helper store

# Verify configuration
git config --list
```

#### Step 4: Create GitHub Personal Access Token

1. Navigate to: `https://github.com/settings/tokens`
2. Click "Generate new token (classic)"
3. Name: `Claude-CLI-Integration`
4. Scopes:
   - ✅ repo (Full control of private repositories)
   - ✅ workflow (Update GitHub Action workflows)
   - ✅ write:packages (Upload packages to GitHub Package Registry)
   - ✅ read:org (Read org and team membership)
5. Generate and copy token

```bash
# Store GitHub token
# Windows
setx GITHUB_TOKEN "your-github-token-here"

# Linux/macOS
echo 'export GITHUB_TOKEN="your-github-token-here"' >> ~/.bashrc
source ~/.bashrc
```

### GitLab Configuration

#### Step 1: Install GitLab CLI

```bash
# Install glab CLI
# Windows (via Scoop)
scoop install glab

# Linux
curl -s https://raw.githubusercontent.com/gitlab-cli/gitlab-cli/main/install.sh | sudo bash

# macOS
brew install glab
```

#### Step 2: Authenticate GitLab CLI

```bash
# Authenticate with GitLab
glab auth login

# Follow prompts to authenticate

# Verify authentication
glab auth status
```

#### Step 3: Create GitLab Personal Access Token

1. Navigate to: `https://gitlab.com/-/profile/personal_access_tokens`
2. Name: `Claude-CLI-Integration`
3. Scopes:
   - ✅ api
   - ✅ read_api
   - ✅ read_repository
   - ✅ write_repository
4. Create and copy token

```bash
# Store GitLab token
# Windows
setx GITLAB_TOKEN "your-gitlab-token-here"

# Linux/macOS
echo 'export GITLAB_TOKEN="your-gitlab-token-here"' >> ~/.bashrc
source ~/.bashrc
```

### Validation Commands for Source Control

```bash
# GitHub validation
gh auth status
gh repo list
gh pr list
gh workflow list

# GitLab validation
glab auth status
glab repo list
glab mr list
glab ci status

# Git validation
git config --list
git remote -v
git status
git log --oneline -5
```

---

## CI/CD Pipeline Configuration

### Azure Pipelines Configuration

#### Step 1: Create Pipeline YAML

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop
      - feature/*

pool:
  vmImage: 'ubuntu-latest'

variables:
  PYTHON_VERSION: '3.9'
  NODE_VERSION: '18.x'

stages:
  - stage: Build
    displayName: 'Build and Test'
    jobs:
      - job: BuildJob
        displayName: 'Build Application'
        steps:
          - task: NodeTool@0
            inputs:
              versionSpec: $(NODE_VERSION)
            displayName: 'Install Node.js'

          - task: UsePythonVersion@0
            inputs:
              versionSpec: $(PYTHON_VERSION)
            displayName: 'Use Python $(PYTHON_VERSION)'

          - script: |
              npm install
              npm run validate
            displayName: 'Install npm dependencies'

          - script: |
              pip install -r requirements-dev.txt
              pytest tests/ -v --cov=plugins --cov-report=xml
            displayName: 'Run tests'

          - task: PublishCodeCoverageResults@1
            inputs:
              codeCoverageTool: 'Cobertura'
              summaryFileLocation: 'coverage.xml'
            displayName: 'Publish code coverage'

  - stage: Deploy
    displayName: 'Deploy to Production'
    dependsOn: Build
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: DeployProduction
        displayName: 'Deploy to Production'
        environment: 'production'
        strategy:
          runOnce:
            deploy:
              steps:
                - script: |
                    npm run build
                    npm publish --access public
                  displayName: 'Build and publish package'
```

#### Step 2: Configure Pipeline Variables

```bash
# Set pipeline variables via Azure CLI
az pipelines variable create \
  --name DATABRICKS_HOST \
  --value "https://your-workspace.cloud.databricks.com" \
  --pipeline-name "databricks-platform-marketplace" \
  --organization https://dev.azure.com/YourOrganization \
  --project YourProject

az pipelines variable create \
  --name DATABRICKS_TOKEN \
  --value "your-databricks-token" \
  --secret true \
  --pipeline-name "databricks-platform-marketplace" \
  --organization https://dev.azure.com/YourOrganization \
  --project YourProject
```

### GitHub Actions Configuration

#### Step 1: Create Workflow YAML

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]
        python-version: [3.8, 3.9, '3.10']

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}

      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          npm install
          pip install -r requirements-dev.txt

      - name: Run validation
        run: npm run validate

      - name: Run tests
        run: |
          pytest tests/ -v --cov=plugins --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella

  publish:
    needs: build-and-test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18.x'
          registry-url: 'https://registry.npmjs.org'

      - name: Install dependencies
        run: npm install

      - name: Build
        run: npm run build

      - name: Publish to npm
        run: npm publish --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

#### Step 2: Configure GitHub Secrets

```bash
# Add secrets via GitHub CLI
gh secret set NPM_TOKEN --body "your-npm-token-here"
gh secret set DATABRICKS_HOST --body "https://your-workspace.cloud.databricks.com"
gh secret set DATABRICKS_TOKEN --body "your-databricks-token"

# Verify secrets
gh secret list
```

### GitLab CI Configuration

#### Step 1: Create .gitlab-ci.yml

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  PYTHON_VERSION: "3.9"
  NODE_VERSION: "18"

test:
  stage: test
  image: python:$PYTHON_VERSION
  before_script:
    - apt-get update -qy
    - apt-get install -y nodejs npm
    - npm install -g npm@9
    - pip install -r requirements-dev.txt
  script:
    - npm install
    - npm run validate
    - pytest tests/ -v --cov=plugins --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

build:
  stage: build
  image: node:$NODE_VERSION
  script:
    - npm install
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

deploy:
  stage: deploy
  image: node:$NODE_VERSION
  only:
    - main
  script:
    - echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > .npmrc
    - npm publish --access public
  environment:
    name: production
```

#### Step 2: Configure CI/CD Variables

In GitLab:
1. Navigate to Settings → CI/CD → Variables
2. Add variables:
   - `NPM_TOKEN` (Masked, Protected)
   - `DATABRICKS_HOST` (Masked, Protected)
   - `DATABRICKS_TOKEN` (Masked, Protected)

### Validation Commands for CI/CD

```bash
# Azure Pipelines validation
az pipelines list \
  --organization https://dev.azure.com/YourOrganization \
  --project YourProject

az pipelines run \
  --name "databricks-platform-marketplace" \
  --organization https://dev.azure.com/YourOrganization \
  --project YourProject

az pipelines runs list \
  --organization https://dev.azure.com/YourOrganization \
  --project YourProject

# GitHub Actions validation
gh workflow list
gh workflow view ci-cd.yml
gh run list
gh run watch

# GitLab CI validation
glab ci status
glab ci view
glab ci list
```

---

## Claude CLI Integration

### Step 1: Install Claude CLI

```bash
# Install Claude CLI via npm
npm install -g @anthropic/claude-cli

# Verify installation
claude --version
```

### Step 2: Configure Claude CLI

```bash
# Initialize Claude CLI configuration
claude init

# Configure API key
claude config set api-key "your-anthropic-api-key"

# Configure default model
claude config set model "claude-opus-4.5"

# View configuration
claude config list
```

### Step 3: Create Claude CLI Integration Config

```bash
# Create .claude-cli-config.json
cat > .claude-cli-config.json << 'EOF'
{
  "integrations": {
    "azureDevOps": {
      "enabled": true,
      "organization": "https://dev.azure.com/YourOrganization",
      "project": "YourProject",
      "patEnvVar": "AZURE_DEVOPS_EXT_PAT"
    },
    "jira": {
      "enabled": true,
      "host": "https://your-domain.atlassian.net",
      "credentialsEnvVars": {
        "username": "JIRA_USERNAME",
        "apiToken": "JIRA_API_TOKEN"
      }
    },
    "github": {
      "enabled": true,
      "tokenEnvVar": "GITHUB_TOKEN"
    },
    "gitlab": {
      "enabled": false,
      "tokenEnvVar": "GITLAB_TOKEN"
    },
    "cicd": {
      "provider": "azure-pipelines",
      "pipelineName": "databricks-platform-marketplace",
      "triggerOnCommit": true,
      "waitForCompletion": false
    }
  },
  "workflows": {
    "createWorkItem": {
      "provider": "azureDevOps",
      "linkToCommit": true,
      "linkToPR": true
    },
    "createIssue": {
      "provider": "jira",
      "defaultProject": "PROJ",
      "defaultIssueType": "Task"
    },
    "createPR": {
      "provider": "github",
      "defaultBase": "main",
      "autoAssignReviewers": true,
      "runCI": true
    }
  }
}
EOF
```

### Step 4: Create Integration Scripts

```bash
# Create integration helper scripts directory
mkdir -p scripts/integrations

# Create ADO integration script
cat > scripts/integrations/ado-helper.sh << 'EOF'
#!/bin/bash
# Azure DevOps Integration Helper

create_work_item() {
  local title=$1
  local type=$2
  local description=$3

  az boards work-item create \
    --title "$title" \
    --type "$type" \
    --description "$description" \
    --organization "$ADO_ORGANIZATION" \
    --project "$ADO_PROJECT"
}

create_pr_with_work_item() {
  local title=$1
  local description=$2
  local source_branch=$3
  local target_branch=$4
  local work_item_id=$5

  pr_id=$(az repos pr create \
    --title "$title" \
    --description "$description" \
    --source-branch "$source_branch" \
    --target-branch "$target_branch" \
    --organization "$ADO_ORGANIZATION" \
    --project "$ADO_PROJECT" \
    --query "pullRequestId" -o tsv)

  az repos pr work-item add \
    --id "$pr_id" \
    --work-items "$work_item_id" \
    --organization "$ADO_ORGANIZATION"
}

export -f create_work_item
export -f create_pr_with_work_item
EOF

chmod +x scripts/integrations/ado-helper.sh

# Create Jira integration script
cat > scripts/integrations/jira-helper.sh << 'EOF'
#!/bin/bash
# Jira Integration Helper

create_jira_issue() {
  local project=$1
  local issue_type=$2
  local summary=$3
  local description=$4

  curl -X POST \
    -H "Content-Type: application/json" \
    -u "$JIRA_USERNAME:$JIRA_API_TOKEN" \
    "$JIRA_HOST/rest/api/3/issue" \
    -d "{
      \"fields\": {
        \"project\": {\"key\": \"$project\"},
        \"summary\": \"$summary\",
        \"description\": {
          \"type\": \"doc\",
          \"version\": 1,
          \"content\": [{
            \"type\": \"paragraph\",
            \"content\": [{\"type\": \"text\", \"text\": \"$description\"}]
          }]
        },
        \"issuetype\": {\"name\": \"$issue_type\"}
      }
    }" | jq -r '.key'
}

link_jira_to_commit() {
  local issue_key=$1
  local commit_sha=$2
  local repo_url=$3

  curl -X POST \
    -H "Content-Type: application/json" \
    -u "$JIRA_USERNAME:$JIRA_API_TOKEN" \
    "$JIRA_HOST/rest/api/3/issue/$issue_key/remotelink" \
    -d "{
      \"object\": {
        \"url\": \"$repo_url/commit/$commit_sha\",
        \"title\": \"Commit $commit_sha\"
      }
    }"
}

export -f create_jira_issue
export -f link_jira_to_commit
EOF

chmod +x scripts/integrations/jira-helper.sh
```

### Step 5: Create Unified Workflow Script

```bash
# Create unified workflow script
cat > scripts/claude-workflow.sh << 'EOF'
#!/bin/bash
# Unified Claude CLI Workflow Script

set -e

# Source integration helpers
source scripts/integrations/ado-helper.sh
source scripts/integrations/jira-helper.sh

# Configuration
ADO_ORGANIZATION="${ADO_ORGANIZATION:-https://dev.azure.com/YourOrganization}"
ADO_PROJECT="${ADO_PROJECT:-YourProject}"
JIRA_HOST="${JIRA_HOST}"
JIRA_USERNAME="${JIRA_USERNAME}"
JIRA_API_TOKEN="${JIRA_API_TOKEN}"

# Main workflow function
execute_workflow() {
  local workflow_type=$1
  shift

  case $workflow_type in
    "feature")
      workflow_feature "$@"
      ;;
    "bugfix")
      workflow_bugfix "$@"
      ;;
    "pr-review")
      workflow_pr_review "$@"
      ;;
    *)
      echo "Unknown workflow: $workflow_type"
      exit 1
      ;;
  esac
}

# Feature workflow
workflow_feature() {
  local feature_name=$1
  local description=$2

  echo "Creating feature workflow for: $feature_name"

  # Create work item in ADO
  work_item_id=$(create_work_item "$feature_name" "User Story" "$description")
  echo "Created ADO work item: $work_item_id"

  # Create feature branch
  branch_name="feature/${work_item_id}-${feature_name// /-}"
  git checkout -b "$branch_name"

  # Use Claude to implement feature
  claude chat "Implement feature: $feature_name. Description: $description"

  # Commit changes
  git add .
  git commit -m "[${work_item_id}] $feature_name

$description

Co-Authored-By: Claude <noreply@anthropic.com>"

  # Push branch
  git push -u origin "$branch_name"

  # Create PR
  pr_id=$(create_pr_with_work_item \
    "[${work_item_id}] $feature_name" \
    "$description" \
    "$branch_name" \
    "main" \
    "$work_item_id")

  echo "Created PR: $pr_id"
}

# Bugfix workflow
workflow_bugfix() {
  local bug_title=$1
  local bug_description=$2

  echo "Creating bugfix workflow for: $bug_title"

  # Create bug work item
  work_item_id=$(create_work_item "$bug_title" "Bug" "$bug_description")
  echo "Created bug work item: $work_item_id"

  # Create bugfix branch
  branch_name="bugfix/${work_item_id}-${bug_title// /-}"
  git checkout -b "$branch_name"

  # Use Claude to fix bug
  claude chat "Fix bug: $bug_title. Description: $bug_description"

  # Commit and push
  git add .
  git commit -m "[${work_item_id}] Fix: $bug_title

$bug_description

Co-Authored-By: Claude <noreply@anthropic.com>"

  git push -u origin "$branch_name"

  # Create PR
  create_pr_with_work_item \
    "[${work_item_id}] Fix: $bug_title" \
    "$bug_description" \
    "$branch_name" \
    "main" \
    "$work_item_id"
}

# PR review workflow
workflow_pr_review() {
  local pr_id=$1

  echo "Reviewing PR: $pr_id"

  # Get PR details
  pr_details=$(az repos pr show --id "$pr_id" --organization "$ADO_ORGANIZATION")

  # Use Claude for code review
  claude chat "Review this pull request: $(echo $pr_details | jq -r '.sourceRefName')"

  # Post review comments
  echo "Review completed. Check Claude's output for findings."
}

# Execute workflow
if [ $# -lt 2 ]; then
  echo "Usage: $0 <workflow-type> <args...>"
  echo "Workflows: feature, bugfix, pr-review"
  exit 1
fi

execute_workflow "$@"
EOF

chmod +x scripts/claude-workflow.sh
```

---

## Validation Commands

### Comprehensive Validation Script

```bash
# Create comprehensive validation script
cat > scripts/validate-integrations.sh << 'EOF'
#!/bin/bash
# Comprehensive Integration Validation Script

set +e  # Don't exit on errors, we want to see all validation results

echo "================================"
echo "Integration Validation Report"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Validation function
validate() {
  local test_name=$1
  local command=$2

  echo -n "Testing $test_name... "
  if eval "$command" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASSED${NC}"
    return 0
  else
    echo -e "${RED}✗ FAILED${NC}"
    return 1
  fi
}

# Track results
total_tests=0
passed_tests=0

# System prerequisites
echo "=== System Prerequisites ==="
validate "Node.js installation" "node --version" && ((passed_tests++))
((total_tests++))

validate "npm installation" "npm --version" && ((passed_tests++))
((total_tests++))

validate "Python installation" "python --version" && ((passed_tests++))
((total_tests++))

validate "Git installation" "git --version" && ((passed_tests++))
((total_tests++))

validate "Azure CLI installation" "az --version" && ((passed_tests++))
((total_tests++))

echo ""

# Azure DevOps validation
echo "=== Azure DevOps Integration ==="
validate "Azure DevOps extension" "az extension show --name azure-devops" && ((passed_tests++))
((total_tests++))

validate "Azure authentication" "az account show" && ((passed_tests++))
((total_tests++))

validate "ADO PAT configured" "test -n \"\$AZURE_DEVOPS_EXT_PAT\"" && ((passed_tests++))
((total_tests++))

validate "ADO project access" "az devops project list --organization \$ADO_ORGANIZATION" && ((passed_tests++))
((total_tests++))

validate "ADO repository access" "az repos list --organization \$ADO_ORGANIZATION --project \$ADO_PROJECT" && ((passed_tests++))
((total_tests++))

echo ""

# Jira validation
echo "=== Jira Integration ==="
validate "Jira host configured" "test -n \"\$JIRA_HOST\"" && ((passed_tests++))
((total_tests++))

validate "Jira credentials configured" "test -n \"\$JIRA_USERNAME\" -a -n \"\$JIRA_API_TOKEN\"" && ((passed_tests++))
((total_tests++))

validate "Jira API connection" "curl -s -u \"\$JIRA_USERNAME:\$JIRA_API_TOKEN\" \"\$JIRA_HOST/rest/api/3/myself\"" && ((passed_tests++))
((total_tests++))

echo ""

# GitHub validation
echo "=== GitHub Integration ==="
validate "GitHub CLI installation" "gh --version" && ((passed_tests++))
((total_tests++))

validate "GitHub authentication" "gh auth status" && ((passed_tests++))
((total_tests++))

validate "GitHub token configured" "test -n \"\$GITHUB_TOKEN\"" && ((passed_tests++))
((total_tests++))

echo ""

# Git configuration
echo "=== Git Configuration ==="
validate "Git user name" "git config user.name" && ((passed_tests++))
((total_tests++))

validate "Git user email" "git config user.email" && ((passed_tests++))
((total_tests++))

validate "Git remote configured" "git remote -v" && ((passed_tests++))
((total_tests++))

echo ""

# Claude CLI validation
echo "=== Claude CLI ==="
validate "Claude CLI installation" "claude --version" && ((passed_tests++))
((total_tests++))

validate "Claude API key configured" "claude config get api-key" && ((passed_tests++))
((total_tests++))

echo ""

# CI/CD validation
echo "=== CI/CD Pipelines ==="
validate "Pipeline YAML exists" "test -f azure-pipelines.yml -o -f .github/workflows/ci-cd.yml -o -f .gitlab-ci.yml" && ((passed_tests++))
((total_tests++))

validate "Pipeline variables configured" "az pipelines variable list --pipeline-name databricks-platform-marketplace --organization \$ADO_ORGANIZATION --project \$ADO_PROJECT || gh secret list || true" && ((passed_tests++))
((total_tests++))

echo ""

# Configuration files
echo "=== Configuration Files ==="
validate "ADO config file" "test -f .ado-config.json" && ((passed_tests++))
((total_tests++))

validate "Jira config file" "test -f .jira-config.json" && ((passed_tests++))
((total_tests++))

validate "Claude CLI config file" "test -f .claude-cli-config.json" && ((passed_tests++))
((total_tests++))

echo ""

# Summary
echo "================================"
echo "Validation Summary"
echo "================================"
echo "Total tests: $total_tests"
echo -e "Passed: ${GREEN}$passed_tests${NC}"
echo -e "Failed: ${RED}$((total_tests - passed_tests))${NC}"
echo "Success rate: $(( passed_tests * 100 / total_tests ))%"
echo ""

if [ $passed_tests -eq $total_tests ]; then
  echo -e "${GREEN}All validations passed! ✓${NC}"
  exit 0
else
  echo -e "${YELLOW}Some validations failed. Please review the output above.${NC}"
  exit 1
fi
EOF

chmod +x scripts/validate-integrations.sh
```

### Run Validation

```bash
# Run comprehensive validation
./scripts/validate-integrations.sh

# Or run individual validations
./scripts/validate-integrations.sh 2>&1 | grep "Azure DevOps"
./scripts/validate-integrations.sh 2>&1 | grep "Jira"
./scripts/validate-integrations.sh 2>&1 | grep "GitHub"
```

### Quick Validation Commands

```bash
# Quick system check
echo "=== Quick System Validation ==="
node --version && echo "✓ Node.js OK" || echo "✗ Node.js FAILED"
npm --version && echo "✓ npm OK" || echo "✗ npm FAILED"
python --version && echo "✓ Python OK" || echo "✗ Python FAILED"
git --version && echo "✓ Git OK" || echo "✗ Git FAILED"
az --version && echo "✓ Azure CLI OK" || echo "✗ Azure CLI FAILED"
claude --version && echo "✓ Claude CLI OK" || echo "✗ Claude CLI FAILED"

# Quick ADO check
echo "=== Azure DevOps Validation ==="
az devops project list --organization $ADO_ORGANIZATION && echo "✓ ADO OK" || echo "✗ ADO FAILED"

# Quick Jira check
echo "=== Jira Validation ==="
curl -s -u "$JIRA_USERNAME:$JIRA_API_TOKEN" "$JIRA_HOST/rest/api/3/myself" && echo "✓ Jira OK" || echo "✗ Jira FAILED"

# Quick GitHub check
echo "=== GitHub Validation ==="
gh auth status && echo "✓ GitHub OK" || echo "✗ GitHub FAILED"

# Quick Git check
echo "=== Git Validation ==="
git config user.name && git config user.email && echo "✓ Git configured OK" || echo "✗ Git configuration FAILED"
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Azure CLI Authentication Fails

**Symptom:**
```
ERROR: Please run 'az login' to setup account.
```

**Solution:**
```bash
# Clear cached credentials
az account clear

# Re-authenticate
az login --use-device-code

# Verify authentication
az account show
```

#### Issue 2: Azure DevOps PAT Not Recognized

**Symptom:**
```
TF401019: The Git repository with name or identifier does not exist
```

**Solution:**
```bash
# Verify PAT is set
echo $AZURE_DEVOPS_EXT_PAT

# If empty, set it again
export AZURE_DEVOPS_EXT_PAT="your-pat-token"

# Test with explicit PAT
AZURE_DEVOPS_EXT_PAT="your-pat-token" az devops project list
```

#### Issue 3: Jira API Connection Fails

**Symptom:**
```
curl: (401) Unauthorized
```

**Solution:**
```bash
# Verify credentials
echo $JIRA_USERNAME
echo $JIRA_API_TOKEN

# Test with explicit credentials
curl -u "your-email@company.com:your-api-token" \
  https://your-domain.atlassian.net/rest/api/3/myself

# Regenerate API token if needed
# Visit: https://id.atlassian.com/manage-profile/security/api-tokens
```

#### Issue 4: GitHub CLI Authentication Fails

**Symptom:**
```
gh: To use GitHub CLI, please authenticate
```

**Solution:**
```bash
# Log out and re-authenticate
gh auth logout
gh auth login

# Follow the authentication flow
# Select: GitHub.com → HTTPS → Yes → Web browser

# Verify
gh auth status
```

#### Issue 5: Git Credentials Not Saved

**Symptom:**
```
Username for 'https://github.com':
Password for 'https://user@github.com':
```

**Solution:**
```bash
# Configure credential helper
git config --global credential.helper store

# Or use manager-core (Windows)
git config --global credential.helper manager-core

# Update stored credentials
git credential reject
# Then perform git operation to re-enter credentials
```

#### Issue 6: Pipeline Fails with Permission Error

**Symptom:**
```
ERROR: The pipeline does not have permission to access resource
```

**Solution:**
```bash
# Grant pipeline access to resources (Azure DevOps)
# Navigate to: Project Settings → Pipelines → Service connections
# Select connection → Security → Grant access

# Or via CLI
az devops service-endpoint list --organization $ADO_ORGANIZATION --project $ADO_PROJECT
```

#### Issue 7: Claude CLI Configuration Issues

**Symptom:**
```
Error: API key not configured
```

**Solution:**
```bash
# Reconfigure Claude CLI
claude config set api-key "your-anthropic-api-key"

# Verify configuration
claude config list

# Test connection
claude chat "Hello"
```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Azure CLI debug
az devops project list --debug

# GitHub CLI debug
gh pr list --log-level debug

# GitLab CLI debug
glab mr list --verbose

# Git debug
GIT_TRACE=1 git push
GIT_CURL_VERBOSE=1 git push
```

---

## Best Practices

### Security Best Practices

1. **Never Commit Credentials**
   ```bash
   # Add to .gitignore
   cat >> .gitignore << 'EOF'
   .ado-config.json
   .jira-config.json
   .claude-cli-config.json
   *.token
   *.pat
   .env
   .env.local
   EOF
   ```

2. **Use Environment Variables**
   - Store all credentials in environment variables
   - Use secret management tools (Azure Key Vault, GitHub Secrets)
   - Rotate tokens regularly (every 90 days)

3. **Limit Token Scopes**
   - Only grant necessary permissions
   - Use read-only tokens when possible
   - Create separate tokens for different purposes

4. **Enable MFA**
   - Enable multi-factor authentication on all services
   - Use authenticator apps, not SMS

### Workflow Best Practices

1. **Branch Naming Convention**
   ```
   feature/[work-item-id]-[short-description]
   bugfix/[work-item-id]-[short-description]
   hotfix/[work-item-id]-[short-description]
   release/[version]
   ```

2. **Commit Message Format**
   ```
   [WORK-ITEM-ID] Type: Brief description

   Detailed description of changes

   Co-Authored-By: Claude <noreply@anthropic.com>
   ```

3. **PR Description Template**
   - Always include test results
   - Link to work items
   - Document breaking changes
   - Include screenshots for UI changes

4. **Code Review Checklist**
   - Run all tests before creating PR
   - Perform security scan
   - Check code coverage
   - Verify documentation is updated

### Integration Best Practices

1. **Automated Workflows**
   - Link commits to work items automatically
   - Trigger CI/CD on PR creation
   - Auto-transition work items on merge

2. **Monitoring and Alerts**
   - Set up pipeline failure notifications
   - Monitor token expiration dates
   - Track integration health metrics

3. **Documentation**
   - Keep integration docs up to date
   - Document custom workflows
   - Maintain troubleshooting guides

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-19 | gekambaram | Initial comprehensive integration configuration guide created |

---

## Additional Resources

### Documentation Links

- [Azure DevOps CLI Documentation](https://docs.microsoft.com/en-us/cli/azure/devops)
- [Jira REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitLab CLI Documentation](https://glab.readthedocs.io/)
- [Claude API Documentation](https://docs.anthropic.com/)

### Support Channels

- Email: data-platform@vivekgana.com
- GitHub Issues: https://github.com/vivekgana/databricks-platform-marketplace/issues
- Documentation: See [docs/](../docs/) directory

### Quick Reference Card

```bash
# Quick Setup Commands
az login --use-device-code
gh auth login
claude config set api-key "your-key"

# Quick Validation
./scripts/validate-integrations.sh

# Quick Workflow
./scripts/claude-workflow.sh feature "Feature Name" "Description"

# Quick PR Creation
az repos pr create --title "[ID] Title" --description "Desc"
gh pr create --title "[ID] Title" --body "Desc"
```

---

**End of Document**
