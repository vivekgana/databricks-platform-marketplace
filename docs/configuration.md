# Configuration Reference

**Document Version:** 1.0
**Last Updated:** 2026-01-04 00:33:20
**Prepared by:** Databricks Platform Team

---

## Overview

This reference documents all configuration options for the Databricks Platform Marketplace, including AI-SDLC, DevOps integrations, plugins, and environment variables.

## AI-SDLC Configuration

### Project Configuration File

**Location:** `ai_sdlc/project.yml`

The main configuration file for AI-SDLC workflows.

### Project Settings

```yaml
project:
  name: "Databricks Platform Marketplace"
  default_branch: "develop"           # Default branch for PRs and CI
  release_branch: "main"               # Production release branch
```

**Options:**
- `name` (string): Project display name
- `default_branch` (string): Default base branch for feature branches and PRs
- `release_branch` (string): Production branch for releases

### Code Generation Policy

```yaml
codegen:
  pr_policy:
    default_base_branch: "develop"
    allow_main_direct_pr: false      # Block PRs directly to main
    hotfix_label_allows_main: "ai-sdlc:hotfix"
  policy:
    max_prs_per_run: 3               # Max PRs per AI-SDLC run
    require_plan_review: true        # Require plan approval
    require_tests: true              # Require test coverage
    allowed_change_zones:            # Directories AI can modify
      - "src/"
      - "notebooks/"
      - "tests/"
      - "databricks.yml"
      - "requirements/"
```

**Options:**
- `pr_policy.default_base_branch` (string): Default PR target branch
- `pr_policy.allow_main_direct_pr` (boolean): Allow PRs to main without develop
- `pr_policy.hotfix_label_allows_main` (string): Label that allows main PRs
- `policy.max_prs_per_run` (integer): Maximum PRs per execution
- `policy.require_plan_review` (boolean): Require user approval of plan
- `policy.require_tests` (boolean): Require tests for generated code
- `policy.allowed_change_zones` (list): Allowed directories for code changes

### Repository Configuration

```yaml
repos:
  - id: "marketplace"                           # Unique repository ID
    url: "https://github.com/vivekgana/databricks-platform-marketplace.git"
    default_branch: "develop"
    release_branch: "main"
    scopes:                                     # File paths this repo manages
      - "src/"
      - "notebooks/"
      - "tests/"
      - "databricks.yml"
      - "requirements/"
    signals:                                    # Technology signals
      bundling: "databricks_asset_bundles"
      runtime: "databricks"
    ci:                                         # CI/CD configuration
      provider: "github_actions"
      pr_base_branch: "develop"
      workflows: ["ci.yml", "demo-evidence.yml"]
    deploy:                                     # Deployment configuration
      method: "dab"                             # Databricks Asset Bundles
      targets: ["dev", "stage", "prod"]
```

**Repository Options:**
- `id` (string, required): Unique identifier
- `url` (string, required): Git repository URL
- `default_branch` (string): Default branch (default: "develop")
- `release_branch` (string): Release branch (default: "main")
- `scopes` (list): File paths managed by this repo
- `signals.bundling` (string): Deployment method identifier
- `signals.runtime` (string): Runtime environment identifier
- `ci.provider` (string): CI provider (github_actions, azure_devops)
- `ci.pr_base_branch` (string): Base branch for PRs
- `ci.workflows` (list): Workflow files to trigger
- `deploy.method` (string): Deployment method (dab, cli, api)
- `deploy.targets` (list): Deployment environments

### Routing Rules

```yaml
routing:
  rules:
    - if_contains: ["databricks.yml", "bundle", "job", "notebook", "dlt", "delta live tables"]
      prefer_repos: ["marketplace"]
    - if_contains: ["tests", "pytest", "ruff", "lint"]
      prefer_repos: ["marketplace"]
```

**Routing Options:**
- `if_contains` (list): Keywords to match in requirement content
- `prefer_repos` (list): Repository IDs to route to when matched

### PR Linking

```yaml
pr_linking:
  base_branch: "develop"
  branch_prefix: "ai/"                # Feature branch prefix
  commit_prefix: "[AI-SDLC]"          # Commit message prefix
  issue_labels: ["ai-sdlc:req", "ai-sdlc:defect"]
```

**Options:**
- `base_branch` (string): Base branch for feature branches
- `branch_prefix` (string): Prefix for AI-generated branches
- `commit_prefix` (string): Prefix for AI-generated commits
- `issue_labels` (list): Labels for linked issues

### LLM Configuration

Configure in `ai_sdlc/project.yml` (if extended):

```yaml
ai_sdlc_config:
  llm:
    provider: "anthropic"              # anthropic, openai, azure_openai, databricks
    model: "claude-sonnet-4-5"        # Model identifier
    temperature: 0.2                   # 0.0-1.0, lower = more deterministic
    max_tokens: 8000                   # Max response tokens
    timeout_seconds: 120               # Request timeout
```

**LLM Options:**
- `provider` (string): LLM provider (anthropic, openai, azure_openai, databricks)
- `model` (string): Model identifier
- `temperature` (float): Sampling temperature (0.0-1.0)
- `max_tokens` (integer): Maximum response tokens
- `timeout_seconds` (integer): Request timeout

**Supported Providers & Models:**

| Provider | Models | Environment Variable |
|----------|--------|---------------------|
| Anthropic | claude-sonnet-4-5, claude-opus-4-5 | `ANTHROPIC_API_KEY` |
| OpenAI | gpt-4-turbo, gpt-4, gpt-3.5-turbo | `OPENAI_API_KEY` |
| Azure OpenAI | gpt-4-turbo | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` |
| Databricks | databricks-meta-llama-* | `DATABRICKS_HOST`, `DATABRICKS_TOKEN` |

### Evidence Configuration

```yaml
ai_sdlc_config:
  evidence:
    enabled: true
    base_path: "/dbfs/tmp/demo/"
    timeout_seconds: 3600
    required_formats: ["png", "html", "md"]
```

**Evidence Options:**
- `enabled` (boolean): Enable evidence generation
- `base_path` (string): Base path for evidence artifacts
- `timeout_seconds` (integer): Evidence generation timeout
- `required_formats` (list): Required artifact formats

### Quality Gates

```yaml
ai_sdlc_config:
  gates:
    require_plan_review: true          # Require plan approval
    require_pr_review: true            # Require PR review
    require_demo_evidence: true        # Require demo evidence
    min_reviewers: 1                   # Minimum reviewers
```

**Gate Options:**
- `require_plan_review` (boolean): Require user approval of implementation plan
- `require_pr_review` (boolean): Require PR review before merge
- `require_demo_evidence` (boolean): Require demo evidence artifacts
- `min_reviewers` (integer): Minimum number of reviewers

---

## Environment Variables

### AI-SDLC Environment Variables

```bash
# AI-SDLC Project Configuration
export AI_SDLC_PROJECT_CONFIG="./ai_sdlc/project.yml"
```

### LLM Provider Configuration

#### Anthropic Claude (Recommended)

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
```

**Setup:**
1. Get API key from [console.anthropic.com](https://console.anthropic.com)
2. Set environment variable

#### OpenAI

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

**Setup:**
1. Get API key from [platform.openai.com](https://platform.openai.com)
2. Set environment variable

#### Azure OpenAI

```bash
export AZURE_OPENAI_API_KEY="your-azure-key-here"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
```

**Setup:**
1. Create Azure OpenAI resource
2. Get endpoint and key from Azure Portal
3. Set both environment variables

#### Databricks Foundation Models

```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi-your-token-here"
```

**Setup:**
1. Get workspace URL
2. Generate personal access token
3. Set both environment variables

### DevOps Integration Configuration

#### Azure DevOps

```bash
export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-org"
export AZURE_DEVOPS_PAT="your-52-character-pat-token"
export AZURE_DEVOPS_PROJECT="YourProject"
```

**Setup:** See [AZURE_PAT_SETUP.md](../plugins/databricks-devops-integrations/docs/setup/AZURE_PAT_SETUP.md)

#### JIRA

```bash
export JIRA_URL="https://your-company.atlassian.net"
export JIRA_API_TOKEN="your-24-character-api-token"
export JIRA_EMAIL="your-email@company.com"
export JIRA_PROJECT="PROJ"
```

**Setup:** See [JIRA_TOKEN_SETUP.md](../plugins/databricks-devops-integrations/docs/setup/JIRA_TOKEN_SETUP.md)

#### LLM Provider Selection

```bash
export LLM_PROVIDER="anthropic"                # anthropic, openai, azure_openai, databricks
export LLM_MODEL="claude-sonnet-4-5"           # Model identifier
```

---

## Plugin Configuration

### Databricks Engineering Plugin

**Configuration File:** `plugins/databricks-engineering/.claude-plugin/plugin.json`

**Key Settings:**
- **Commands:** 15 commands for pipeline development
- **Agents:** 18 specialized code review agents
- **Skills:** 8 architecture pattern skills
- **MCP Servers:** 3 Databricks integration servers
- **Templates:** 4 project scaffolds

**Environment Variables:**
```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi-your-token-here"
export DATABRICKS_WORKSPACE_ID="your-workspace-id"
```

### Databricks MLOps Plugin

**Configuration File:** `plugins/databricks-mlops/.claude-plugin/plugin.json`

**Key Settings:**
- **Commands:** 10 MLOps workflow commands
- **Agents:** 9 ML lifecycle agents
- **Skills:** 4 MLOps patterns
- **MCP Servers:** 2 MLflow integration servers

**Environment Variables:**
```bash
export MLFLOW_TRACKING_URI="databricks"
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi-your-token-here"
```

### Databricks Governance Plugin

**Configuration File:** `plugins/databricks-governance/.claude-plugin/plugin.json`

**Key Settings:**
- **Commands:** 8 governance commands
- **Agents:** 12 compliance and security agents
- **Skills:** 4 governance patterns
- **MCP Servers:** 2 governance API servers

**Environment Variables:**
```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi-your-token-here"
export UNITY_CATALOG_ENABLED="true"
```

---

## Databricks Asset Bundles Configuration

### Bundle Configuration File

**Location:** `databricks.yml` (project root)

Example configuration:

```yaml
bundle:
  name: databricks-platform-marketplace

resources:
  jobs:
    my_job:
      name: "My Pipeline Job"
      tasks:
        - task_key: "bronze_ingestion"
          notebook_task:
            notebook_path: "./notebooks/bronze_ingestion"
          new_cluster:
            spark_version: "13.3.x-scala2.12"
            node_type_id: "i3.xlarge"
            num_workers: 2

  pipelines:
    my_dlt_pipeline:
      name: "My DLT Pipeline"
      target: "main"
      libraries:
        - notebook:
            path: "./notebooks/dlt_pipeline.py"
      configuration:
        "spark.databricks.delta.preview.enabled": "true"

targets:
  dev:
    workspace:
      host: "https://your-workspace.cloud.databricks.com"
    variables:
      catalog: "dev"

  prod:
    workspace:
      host: "https://your-workspace.cloud.databricks.com"
    variables:
      catalog: "prod"
```

**Key Sections:**
- `bundle.name` (string): Bundle identifier
- `resources.jobs` (map): Databricks jobs
- `resources.pipelines` (map): Delta Live Tables pipelines
- `targets` (map): Environment-specific configurations

---

## CI/CD Configuration

### GitHub Actions

**Workflow Files:**
- `.github/workflows/ci-cd.yml` - Main CI/CD pipeline
- `.github/workflows/demo-evidence.yml` - Evidence generation
- `.github/workflows/devops-integrations-ci-cd.yml` - DevOps integration tests

**Environment Variables (GitHub Secrets):**
```yaml
secrets:
  DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
  DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  AZURE_DEVOPS_PAT: ${{ secrets.AZURE_DEVOPS_PAT }}
  JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
```

### Azure DevOps Pipelines

**Pipeline File:** `azure-pipelines.yml`

**Environment Variables (Pipeline Variables):**
- `DATABRICKS_HOST` - Databricks workspace URL
- `DATABRICKS_TOKEN` - Databricks PAT
- `AZURE_DEVOPS_PAT` - Azure DevOps PAT
- `JIRA_API_TOKEN` - JIRA API token

---

## Security Configuration

### Secret Management

**Recommended Secret Managers:**

1. **Azure Key Vault**
   ```bash
   az keyvault secret set --vault-name my-vault --name databricks-token --value "dapi-..."
   ```

2. **AWS Secrets Manager**
   ```bash
   aws secretsmanager create-secret --name databricks-token --secret-string "dapi-..."
   ```

3. **HashiCorp Vault**
   ```bash
   vault kv put secret/databricks token="dapi-..."
   ```

4. **Databricks Secrets**
   ```bash
   databricks secrets create-scope --scope my-scope
   databricks secrets put --scope my-scope --key token
   ```

### .env File Template

**Location:** `.env` (add to `.gitignore`)

```bash
# Databricks
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi-your-token-here
DATABRICKS_WORKSPACE_ID=your-workspace-id

# LLM Provider (choose one)
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
# OPENAI_API_KEY=sk-your-key-here
# AZURE_OPENAI_API_KEY=your-azure-key-here
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# DevOps Integration
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/your-org
AZURE_DEVOPS_PAT=your-52-character-pat-token
AZURE_DEVOPS_PROJECT=YourProject

JIRA_URL=https://your-company.atlassian.net
JIRA_API_TOKEN=your-24-character-api-token
JIRA_EMAIL=your-email@company.com
JIRA_PROJECT=PROJ

# LLM Configuration
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-5

# AI-SDLC Configuration
AI_SDLC_PROJECT_CONFIG=./ai_sdlc/project.yml
```

---

## MCP Server Configuration

### Databricks Workspace MCP

**Configuration:** `plugins/databricks-engineering/mcp-servers/databricks-workspace.json`

```json
{
  "mcpServers": {
    "databricks-workspace": {
      "url": "${DATABRICKS_HOST}/api/2.0/mcp",
      "headers": {
        "Authorization": "Bearer ${DATABRICKS_TOKEN}"
      }
    }
  }
}
```

### Unity Catalog MCP

**Configuration:** `plugins/databricks-engineering/mcp-servers/unity-catalog.json`

```json
{
  "mcpServers": {
    "unity-catalog": {
      "url": "${DATABRICKS_HOST}/api/2.1/unity-catalog/mcp",
      "headers": {
        "Authorization": "Bearer ${DATABRICKS_TOKEN}"
      }
    }
  }
}
```

### MLflow Registry MCP

**Configuration:** `plugins/databricks-mlops/mcp-servers/mlflow-registry.json`

```json
{
  "mcpServers": {
    "mlflow-registry": {
      "url": "${DATABRICKS_HOST}/api/2.0/mlflow/mcp",
      "headers": {
        "Authorization": "Bearer ${DATABRICKS_TOKEN}"
      }
    }
  }
}
```

---

## Validation

### Validate AI-SDLC Configuration

```bash
# Validate project.yml
ai-sdlc validate-config

# Check environment variables
ai-sdlc info
```

### Validate Plugin Configuration

```bash
# Engineering plugin
npx claude-plugins validate @vivekgana/databricks-platform-marketplace/databricks-engineering

# MLOps plugin
npx claude-plugins validate @vivekgana/databricks-platform-marketplace/databricks-mlops

# Governance plugin
npx claude-plugins validate @vivekgana/databricks-platform-marketplace/databricks-governance
```

### Validate Databricks Bundle

```bash
# Validate bundle configuration
databricks bundle validate

# Deploy to dev
databricks bundle deploy --target dev

# Run bundle tests
databricks bundle run --target dev
```

---

## Troubleshooting

### Configuration Issues

**Problem:** `FileNotFoundError: project.yml not found`
**Solution:** Set `AI_SDLC_PROJECT_CONFIG` to correct path

**Problem:** `Invalid YAML syntax in project.yml`
**Solution:** Validate YAML syntax with `yamllint project.yml`

**Problem:** `Missing required field: repos`
**Solution:** Ensure `repos` section exists in project.yml

### Environment Variable Issues

**Problem:** `ANTHROPIC_API_KEY not found`
**Solution:** Set environment variable or add to .env file

**Problem:** `Invalid API key format`
**Solution:** Verify key format (Anthropic: starts with `sk-ant-api03-`)

**Problem:** `DATABRICKS_HOST not set`
**Solution:** Set workspace URL including https://

### Plugin Issues

**Problem:** `Plugin not found`
**Solution:** Install plugin with `npx claude-plugins install`

**Problem:** `Command not recognized`
**Solution:** Check plugin is installed and activated

---

## Related Documentation

- [Commands Reference](commands-reference.md)
- [Agents Reference](agents-reference.md)
- [Skills Reference](skills-reference.md)
- [API Reference](api-reference.md)
- [Getting Started Guide](getting-started.md)

---

**Prepared by:** Databricks Platform Team
**Contact:** data-platform@vivekgana.com
