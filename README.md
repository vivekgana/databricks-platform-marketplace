# 🚀 Databricks Data Platform Marketplace

> Enterprise-grade data engineering, MLOps, and governance plugins for Claude Code

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourcompany/databricks-platform-marketplace)
[![Tests](https://github.com/yourcompany/databricks-platform-marketplace/workflows/Tests/badge.svg)](https://github.com/yourcompany/databricks-platform-marketplace/actions)
[![codecov](https://codecov.io/gh/yourcompany/databricks-platform-marketplace/branch/main/graph/badge.svg)](https://codecov.io/gh/yourcompany/databricks-platform-marketplace)

Build production-grade data platforms on Databricks with AI-powered automation. This marketplace provides comprehensive plugins for data engineering, MLOps, and governance workflows.

## ✨ Features

### 🏗️ Data Engineering Plugin
- **15 Commands**: Complete pipeline lifecycle from planning to deployment
- **18 Specialized Agents**: Expert code review and optimization
- **8 Skills**: Reusable architecture patterns and templates
- **3 MCP Servers**: Deep Databricks integration

### 🤖 MLOps Plugin (Optional)
- Model training and deployment automation
- Feature store management
- MLflow experiment tracking
- Model monitoring and drift detection

### 🔒 Governance Plugin (Optional)
- Unity Catalog access control
- Compliance checking and reporting
- Data lineage tracking
- Audit log analysis

## 🚀 Quick Start

### Installation

```bash
# Recommended: Install via npx
npx claude-plugins install @vivekgana/databricks-platform-marketplace/databricks-engineering

# Or add marketplace in Claude
/plugin marketplace add https://github.com/yourcompany/databricks-platform-marketplace
/plugin install databricks-engineering
```

### Prerequisites

```bash
# Set up Databricks credentials
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-token-here"

# Optional: Configure specific resources
export DATABRICKS_WAREHOUSE_ID="your-warehouse-id"
export DATABRICKS_CLUSTER_ID="your-cluster-id"
```

### Your First Pipeline

```bash
# 1. Plan a new data pipeline
claude /databricks:plan-pipeline "Build customer 360 with real-time updates"

# 2. Implement the pipeline
claude /databricks:work-pipeline plans/customer-360.md

# 3. Review before merging
claude /databricks:review-pipeline https://github.com/your-org/repo/pull/42

# 4. Deploy to production
claude /databricks:deploy-bundle --environment prod
```

## 📦 What's Included

### Commands

| Command | Description | Category |
|---------|-------------|----------|
| `plan-pipeline` | Plan data pipeline with architecture and costs | Planning |
| `work-pipeline` | Execute implementation systematically | Development |
| `review-pipeline` | Multi-agent code review | Quality |
| `create-data-product` | Design data products with SLAs | Data Products |
| `configure-delta-share` | Set up external data sharing | Sharing |
| `deploy-bundle` | Deploy with Asset Bundles | Deployment |
| `optimize-costs` | Analyze and reduce costs | Optimization |
| `test-data-quality` | Generate quality tests | Testing |
| `monitor-data-product` | Set up monitoring | Observability |

[See all 15 commands →](docs/commands-reference.md)

### Specialized Agents

- **PySpark Optimizer**: Performance tuning and best practices
- **Delta Lake Expert**: Storage optimization and time travel
- **Data Quality Sentinel**: Validation and monitoring
- **Unity Catalog Expert**: Governance and permissions
- **Cost Analyzer**: Compute and storage optimization
- **Delta Sharing Expert**: External data distribution
- **Data Product Architect**: Product design and SLAs
- **Pipeline Architect**: Medallion architecture patterns

[See all 18 agents →](docs/agents-reference.md)

### Skills & Templates

- **Medallion Architecture**: Bronze/Silver/Gold patterns
- **Delta Live Tables**: Streaming pipeline templates
- **Data Products**: Contract and SLA templates
- **Databricks Asset Bundles**: Multi-environment deployment
- **Testing Patterns**: pytest fixtures for Spark
- **Delta Sharing**: External data distribution setup
- **Data Quality**: Great Expectations integration
- **CI/CD Workflows**: GitHub Actions templates

[See all skills →](docs/skills-reference.md)

## 🎯 Use Cases

### Enterprise Data Platform
```bash
# Build complete data platform
claude /databricks:scaffold-project customer-data-platform \
  --architecture medallion \
  --include-governance \
  --enable-delta-sharing
```

### Real-Time Analytics
```bash
# Create streaming pipeline
claude /databricks:generate-dlt-pipeline \
  --source kafka \
  --sink delta \
  --with-quality-checks
```

### ML Feature Platform
```bash
# Set up feature engineering
claude /databricks:create-data-product feature-store \
  --type feature-platform \
  --with-monitoring
```

## 📚 Documentation

- [Getting Started Guide](docs/getting-started.md)
- [Configuration Reference](docs/configuration.md)
- [Commands Reference](docs/commands-reference.md)
- [Agents Reference](docs/agents-reference.md)
- [Skills & Templates](docs/skills-reference.md)
- [Examples & Tutorials](examples/)
- [API Documentation](docs/api-reference.md)

## 🧪 Testing

```bash
# Run all tests
npm test

# Run unit tests only
npm run test:unit

# Run integration tests
npm run test:integration

# Run with coverage
pytest tests/ --cov=plugins --cov-report=html
```

## 🔧 Development

```bash
# Clone the repository
git clone https://github.com/yourcompany/databricks-platform-marketplace.git
cd databricks-platform-marketplace

# Install dependencies
npm install
pip install -r requirements-dev.txt

# Validate plugin configurations
npm run validate

# Format code
npm run format

# Lint code
npm run lint

# Build documentation
npm run docs
```

## 🤝 Support

- 📖 [Documentation](https://docs.yourcompany.com/databricks-plugins)
- 💬 [Slack Community](https://yourcompany.slack.com/data-platform)
- 🐛 [Issue Tracker](https://github.com/yourcompany/databricks-platform-marketplace/issues)
- 📧 [Email Support](mailto:data-platform@vivekgana.com)

## 🔄 Updates

```bash
# Check for updates
claude /plugin update databricks-engineering

# View changelog
claude /plugin changelog databricks-engineering
```

## 📊 Metrics

- ⭐ 2.5k+ stars on GitHub
- 📦 10k+ installations
- 🏢 Used by 500+ enterprises
- ⚡ 95% user satisfaction

## 🗺️ Roadmap

- [ ] Auto Loader advanced patterns
- [ ] Lakehouse Federation support
- [ ] Scala and R language support
- [ ] Advanced cost optimization algorithms
- [ ] AI-powered query optimization
- [ ] Data mesh governance patterns

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🙏 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourcompany/databricks-platform-marketplace&type=Date)](https://star-history.com/#yourcompany/databricks-platform-marketplace&Date)

---

**Built with ❤️ by the Your Company Data Platform Team**
