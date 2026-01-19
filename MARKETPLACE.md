# Databricks Data Platform Suite - Claude Marketplace

> Enterprise data engineering, MLOps, and governance with AI-powered SDLC workflows

[![npm version](https://img.shields.io/npm/v/@vivekgana/databricks-platform-marketplace)](https://www.npmjs.com/package/@vivekgana/databricks-platform-marketplace)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Plugin](https://img.shields.io/badge/Claude-Plugin-blue)](https://claude.com)

## 🚀 Quick Install

```bash
npx claude-plugins install @vivekgana/databricks-platform-marketplace/databricks-engineering
```

Or via Claude CLI:

```bash
/plugin marketplace add https://github.com/vivekgana/databricks-platform-marketplace
/plugin install databricks-engineering
```

## ✨ What's Included

### 🏗️ Data Engineering (Core Plugin)
- **15 Commands** for complete pipeline lifecycle
- **18 AI Agents** for code review and optimization
- **8 Skill Templates** for common patterns
- **3 MCP Servers** for Databricks integration

### 🤖 MLOps (Optional)
- Model training and deployment automation
- MLflow experiment tracking
- Feature store management
- Model monitoring and drift detection

### 🔒 Governance (Optional)
- Unity Catalog access control
- Compliance reporting (GDPR, CCPA, HIPAA)
- Data lineage tracking
- PII detection and masking

### 🔧 DevOps Integrations (Optional)
- Azure DevOps (work items, PRs, artifacts)
- Jira (issues, epics, sprints)
- GitHub/GitLab workflows
- CI/CD automation

## 🎯 Key Features

### AI-Powered SDLC
- **Automated PBI Generation** from Azure DevOps wikis
- **Epic Processing** with automatic task breakdown
- **AI Code Review** with multiple specialized agents
- **Test Generation** (unit, integration, e2e)
- **Performance Analysis** and optimization suggestions

### DevOps Integration
- **Jira Integration**: Create issues, link commits, update statuses
- **Azure DevOps**: Manage work items, PRs, and artifacts
- **GitHub/GitLab**: Create PRs/MRs, run workflows
- **Evidence Management**: Track artifacts and metrics

### Data Platform
- **Medallion Architecture**: Bronze/Silver/Gold patterns
- **Delta Live Tables**: Streaming pipeline templates
- **Delta Sharing**: External data distribution
- **Data Products**: Contract and SLA templates
- **Unity Catalog**: Governance and permissions

## 📦 Installation

### Prerequisites

```bash
# Required environment variables
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-databricks-token"

# Optional (for full functionality)
export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-organization"
export AZURE_DEVOPS_EXT_PAT="your-ado-pat-token"
export JIRA_HOST="https://your-domain.atlassian.net"
export JIRA_API_TOKEN="your-jira-api-token"
export GITHUB_TOKEN="your-github-token"
```

### System Requirements

- Node.js >= 18.0.0
- Python >= 3.10
- Claude 3.5 or higher

## 🎬 Quick Start

### 1. Create a Data Pipeline

```bash
# Plan a new pipeline
claude /databricks:plan-pipeline "Build customer 360 with real-time updates"

# Implement the pipeline
claude /databricks:work-pipeline plans/customer-360.md

# Review before merging
claude /databricks:review-pipeline https://github.com/your-org/repo/pull/42
```

### 2. Deploy to Production

```bash
# Deploy using Databricks Asset Bundles
claude /databricks:deploy-bundle --environment prod

# Monitor data quality
claude /databricks:monitor-data-product customer-360
```

### 3. Generate PBIs from Wiki

```bash
# Process Azure DevOps wiki page
python -m ai_sdlc.cli.epic_commands process-wiki "https://dev.azure.com/your-organization/YourProject/_wiki/..."

# Generates structured PBIs with tasks
```

## 📚 Documentation

- [Getting Started Guide](https://github.com/vivekgana/databricks-platform-marketplace/blob/main/docs/getting-started.md)
- [Integration Configuration](https://github.com/vivekgana/databricks-platform-marketplace/blob/main/docs/INTEGRATION-CONFIGURATION-GUIDE.md)
- [Commands Reference](https://github.com/vivekgana/databricks-platform-marketplace/blob/main/docs/commands-reference.md)
- [Agents Reference](https://github.com/vivekgana/databricks-platform-marketplace/blob/main/docs/agents-reference.md)
- [Marketplace Submission](https://github.com/vivekgana/databricks-platform-marketplace/blob/main/docs/CLAUDE-MARKETPLACE-SUBMISSION.md)

## 🔑 Keywords

**Primary**: databricks, data-engineering, pyspark, mlops, delta-lake, unity-catalog, ci-cd

**DevOps**: azure-devops, jira, github, gitlab, workflow-orchestration, pbi-generation, epic-planning

**AI-SDLC**: ai-sdlc, code-review, automated-testing, test-generation, performance-analysis

**Data Platform**: medallion-architecture, delta-live-tables, delta-sharing, data-products, lakehouse

**MLOps**: mlflow, feature-engineering, model-deployment, model-monitoring, experiment-tracking

**Governance**: data-governance, compliance, gdpr, ccpa, hipaa, pii-detection, data-lineage

**Total**: 159 comprehensive keywords for maximum discoverability

## 🤝 Support

- **Issues**: https://github.com/vivekgana/databricks-platform-marketplace/issues
- **Discussions**: https://github.com/vivekgana/databricks-platform-marketplace/discussions
- **Email**: support@vivekgana.com

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🌟 Show Your Support

If you find this plugin useful, please:
- ⭐ Star the repository
- 📢 Share with your team
- 🐛 Report issues
- 🤝 Contribute improvements

---

**Built for Claude Code by Ganapathi Ekambaram**
