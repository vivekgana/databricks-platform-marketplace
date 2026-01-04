# Getting Started with Databricks Platform Marketplace

Welcome! This guide will help you get up and running with the Databricks Platform Marketplace plugins.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [First Pipeline](#your-first-pipeline)
- [Available Commands](#available-commands)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required

- **Claude Code**: Latest version
- **Python**: 3.10 or higher
- **Databricks Workspace**: With Unity Catalog enabled
- **Databricks Token**: Personal access token or service principal

### Optional

- **Git**: For version control
- **Docker**: For containerized development
- **Node.js 18+**: For NPM installation

## Installation

### Method 1: NPX (Recommended)

```bash
npx claude-plugins install @vivekgana/databricks-platform-marketplace/databricks-engineering
```

### Method 2: Claude Code Native

```bash
# Add marketplace
/plugin marketplace add https://github.com/yourcompany/databricks-platform-marketplace

# Install plugin
/plugin install databricks-engineering
```

### Method 3: Development Setup

```bash
# Clone repository
git clone https://github.com/yourcompany/databricks-platform-marketplace.git
cd databricks-platform-marketplace

# Run setup script
./setup.sh

# Add as local marketplace
claude /plugin marketplace add file://$(pwd)
claude /plugin install databricks-engineering
```

## Configuration

### 1. Get Databricks Credentials

1. Log into your Databricks workspace
2. Go to **User Settings** → **Access Tokens**
3. Click **Generate New Token**
4. Copy the token (you'll only see it once!)

### 2. Set Environment Variables

```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi..."
export DATABRICKS_WAREHOUSE_ID="your-warehouse-id"  # Optional
```

### 3. Configure Plugin

Create `.databricks-plugin-config.yaml`:

```yaml
databricks:
  host: "${DATABRICKS_HOST}"
  token: "${DATABRICKS_TOKEN}"
  default_catalog: "dev_catalog"
  default_schema: "default"

plugins:
  databricks_engineering:
    auto_format_code: true
    run_tests_on_save: false
    generate_documentation: true
```

## Your First Pipeline

Let's create a simple customer data pipeline!

### Step 1: Plan the Pipeline

```bash
claude /databricks:plan-pipeline "Build customer analytics pipeline:
- Ingest customer data from CSV
- Cleanse and standardize
- Calculate customer lifetime value
- Output to Unity Catalog"
```

This generates a detailed plan including:
- Medallion architecture (Bronze/Silver/Gold)
- Data quality checks
- Cost estimation
- Implementation steps

### Step 2: Review the Plan

The plan is saved to `plans/customer-analytics-pipeline.md`. Review it and make any adjustments.

### Step 3: Implement the Pipeline

```bash
claude /databricks:work-pipeline plans/customer-analytics-pipeline.md
```

This will:
- Create Bronze/Silver/Gold notebooks
- Generate data quality tests
- Set up monitoring
- Create deployment configuration

### Step 4: Test Locally

```bash
# Run unit tests
pytest tests/unit/ -v

# Run data quality checks
claude /databricks:test-data-quality customer_analytics
```

### Step 5: Review Code

```bash
# Review the implementation
claude /databricks:review-pipeline

# Address any findings
claude /databricks:triage
```

### Step 6: Deploy

```bash
# Validate deployment
claude /databricks:validate-deployment --target dev

# Deploy to dev
claude /databricks:deploy-bundle --environment dev

# Monitor the pipeline
claude /databricks:monitor-data-product customer_analytics
```

## Available Commands

### Planning & Design
- `/databricks:plan-pipeline` - Plan data pipeline with architecture
- `/databricks:create-data-product` - Design data product with SLAs
- `/databricks:scaffold-project` - Scaffold new project

### Development
- `/databricks:work-pipeline` - Execute pipeline implementation
- `/databricks:generate-dlt-pipeline` - Generate Delta Live Tables
- `/databricks:test-data-quality` - Generate quality tests

### Code Review & Quality
- `/databricks:review-pipeline` - Multi-agent code review
- `/databricks:triage` - Review and address findings
- `/databricks:optimize-costs` - Cost optimization analysis

### Deployment
- `/databricks:validate-deployment` - Pre-deployment validation
- `/databricks:deploy-bundle` - Deploy with Asset Bundles
- `/databricks:deploy-workflow` - Deploy job workflow

### Data Products & Sharing
- `/databricks:publish-data-product` - Publish to Unity Catalog
- `/databricks:configure-delta-share` - Setup Delta Sharing
- `/databricks:manage-consumers` - Manage data consumers
- `/databricks:monitor-data-product` - Setup monitoring

## Examples

### Example 1: Real-Time Analytics

```bash
# Plan streaming pipeline
claude /databricks:plan-pipeline "Real-time user activity tracking:
- Stream from Kafka
- Enrich with user profiles
- Aggregate by session
- Output to Delta tables"

# Generate DLT pipeline
claude /databricks:generate-dlt-pipeline \
  --source kafka \
  --sink delta \
  --with-quality-checks
```

### Example 2: ML Feature Platform

```bash
# Create feature store
claude /databricks:create-data-product feature-store \
  --type feature-platform \
  --with-monitoring

# Deploy features
claude /databricks:deploy-bundle --environment prod
```

### Example 3: Data Sharing

```bash
# Configure external sharing
claude /databricks:configure-delta-share \
  "Share customer insights with Partner ABC:
   - customer_summary table (read-only)
   - Rate limit: 1000 queries/day
   - Expire after 90 days"
```

## Common Workflows

### Daily Development Workflow

```bash
# 1. Start your day
git pull origin main

# 2. Create feature branch
git checkout -b feature/customer-segmentation

# 3. Plan your work
claude /databricks:plan-pipeline "Add customer segmentation"

# 4. Implement
claude /databricks:work-pipeline plans/customer-segmentation.md

# 5. Test
pytest tests/ -v

# 6. Review
claude /databricks:review-pipeline

# 7. Commit and push
git add .
git commit -m "feat: add customer segmentation pipeline"
git push origin feature/customer-segmentation

# 8. Create PR and deploy
```

### Production Deployment Workflow

```bash
# 1. Validate changes
claude /databricks:validate-deployment --target prod --check-costs

# 2. Run full test suite
pytest tests/ --cov=plugins

# 3. Deploy to staging first
claude /databricks:deploy-bundle --environment staging

# 4. Smoke test in staging
claude /databricks:monitor-data-product --environment staging

# 5. If all good, deploy to prod
claude /databricks:deploy-bundle --environment prod

# 6. Monitor production
claude /databricks:monitor-data-product --environment prod
```

## Troubleshooting

### Common Issues

**Issue**: "Could not connect to Databricks"
```bash
# Solution: Check credentials
echo $DATABRICKS_HOST
echo $DATABRICKS_TOKEN | head -c 10

# Test connection
databricks auth describe
```

**Issue**: "Permission denied" errors
```bash
# Solution: Check Unity Catalog permissions
# Ensure your token has:
# - CREATE TABLE on catalog
# - USE SCHEMA on schemas
# - CREATE CLUSTER (for job deployment)
```

**Issue**: "Plugin not found"
```bash
# Solution: Reinstall plugin
claude /plugin uninstall databricks-engineering
claude /plugin install databricks-engineering
```

**Issue**: "Tests failing"
```bash
# Solution: Check PySpark installation
python -c "from pyspark.sql import SparkSession; print('OK')"

# Reinstall if needed
pip install --force-reinstall pyspark delta-spark
```

### Getting Help

- 📖 **Documentation**: Full docs in `/docs` directory
- 💬 **Slack**: [Join our community](https://yourcompany.slack.com/data-platform)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourcompany/databricks-platform-marketplace/issues)
- 📧 **Email**: data-platform@vivekgana.com

### Debug Mode

Enable detailed logging:

```yaml
# In .databricks-plugin-config.yaml
advanced:
  log_level: "DEBUG"
  log_to_file: true
  log_file_path: "logs/debug.log"
```

Then check logs:
```bash
tail -f logs/debug.log
```

## Next Steps

1. **Explore Examples**: Check out `/examples` directory for complete projects
2. **Read Skills**: Learn patterns in `/plugins/databricks-engineering/skills`
3. **Customize Agents**: Modify agent behavior in `/plugins/databricks-engineering/agents`
4. **Join Community**: Connect with other users on Slack
5. **Contribute**: See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines

## Resources

- [Databricks Documentation](https://docs.databricks.com)
- [Delta Lake Guide](https://docs.delta.io)
- [Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog)
- [MLflow](https://mlflow.org/docs/latest/index.html)

---

**Happy building!** 🚀
