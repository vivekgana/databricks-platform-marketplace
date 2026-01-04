# Commands Reference

**Document Version:** 1.0
**Last Updated:** 2026-01-04 00:29:00
**Prepared by:** Databricks Platform Team

---

## Overview

This document provides a comprehensive reference for all commands available in the Databricks Platform Marketplace plugins.

## Databricks Engineering Plugin - Commands

### Pipeline Management

#### `/work-pipeline`
Create and manage Delta Live Tables (DLT) pipelines with automated Bronze-Silver-Gold architecture.

**Usage:**
```
/work-pipeline create --name customer-360 --type bronze-silver-gold
```

**Features:**
- Automated pipeline scaffolding
- Bronze layer ingestion templates
- Silver layer transformation templates
- Gold layer aggregation templates
- Data quality checks
- Unity Catalog integration

**Documentation:** [plugins/databricks-engineering/commands/work-pipeline.md](../plugins/databricks-engineering/commands/work-pipeline.md)

---

#### `/generate-dlt-pipeline`
Generate Delta Live Tables pipeline with expectations and quality checks.

**Usage:**
```
/generate-dlt-pipeline --source bronze --target silver --expectations high
```

**Features:**
- DLT pipeline configuration
- Expectation definitions
- Quality metrics
- SLA tracking

**Documentation:** [plugins/databricks-engineering/commands/generate-dlt-pipeline.md](../plugins/databricks-engineering/commands/generate-dlt-pipeline.md)

---

### Data Products

#### `/create-data-product`
Create data products with contracts, SLAs, and monitoring.

**Usage:**
```
/create-data-product --name customer-analytics --contract data-contract.json
```

**Features:**
- Data contract enforcement
- SLA definitions
- Consumer management
- Quality monitoring
- Lineage tracking

**Documentation:** [plugins/databricks-engineering/commands/create-data-product.md](../plugins/databricks-engineering/commands/create-data-product.md)

---

#### `/publish-data-product`
Publish data products to consumers with access control.

**Usage:**
```
/publish-data-product --product customer-analytics --consumers team-a,team-b
```

**Documentation:** [plugins/databricks-engineering/commands/publish-data-product.md](../plugins/databricks-engineering/commands/publish-data-product.md)

---

#### `/monitor-data-product`
Monitor data product health, usage, and SLA compliance.

**Usage:**
```
/monitor-data-product --product customer-analytics --metrics all
```

**Documentation:** [plugins/databricks-engineering/commands/monitor-data-product.md](../plugins/databricks-engineering/commands/monitor-data-product.md)

---

### Delta Sharing

#### `/configure-delta-share`
Configure Delta Sharing for external data sharing.

**Usage:**
```
/configure-delta-share --table customers --recipients partner-a
```

**Documentation:** [plugins/databricks-engineering/commands/configure-delta-share.md](../plugins/databricks-engineering/commands/configure-delta-share.md)

---

#### `/manage-consumers`
Manage Delta Sharing consumers and permissions.

**Usage:**
```
/manage-consumers --share customer-share --action grant --recipient partner-a
```

**Documentation:** [plugins/databricks-engineering/commands/manage-consumers.md](../plugins/databricks-engineering/commands/manage-consumers.md)

---

### Deployment & Validation

#### `/deploy-bundle`
Deploy Databricks Asset Bundles to target environments.

**Usage:**
```
/deploy-bundle --target prod --validate
```

**Features:**
- Multi-environment deployment
- Pre-deployment validation
- Rollback capability
- Deployment history

**Documentation:** [plugins/databricks-engineering/commands/deploy-bundle.md](../plugins/databricks-engineering/commands/deploy-bundle.md)

---

#### `/validate-deployment`
Validate deployment health and configuration.

**Usage:**
```
/validate-deployment --environment prod --comprehensive
```

**Documentation:** [plugins/databricks-engineering/commands/validate-deployment.md](../plugins/databricks-engineering/commands/validate-deployment.md)

---

#### `/deploy-workflow`
Deploy workflow orchestrations with dependencies.

**Usage:**
```
/deploy-workflow --name etl-pipeline --schedule daily
```

**Documentation:** [plugins/databricks-engineering/commands/deploy-workflow.md](../plugins/databricks-engineering/commands/deploy-workflow.md)

---

### Testing & Quality

#### `/test-data-quality`
Run comprehensive data quality tests.

**Usage:**
```
/test-data-quality --table customers --profile full
```

**Features:**
- Schema validation
- Data profiling
- Anomaly detection
- Quality metrics
- Great Expectations integration

**Documentation:** [plugins/databricks-engineering/commands/test-data-quality.md](../plugins/databricks-engineering/commands/test-data-quality.md)

---

#### `/review-pipeline`
Review pipeline code and configuration for best practices.

**Usage:**
```
/review-pipeline --pipeline customer-etl --checks all
```

**Documentation:** [plugins/databricks-engineering/commands/review-pipeline.md](../plugins/databricks-engineering/commands/review-pipeline.md)

---

### Cost Optimization

#### `/optimize-costs`
Analyze and optimize Databricks costs.

**Usage:**
```
/optimize-costs --scope workspace --recommendations
```

**Features:**
- Cluster right-sizing
- Job optimization
- Storage optimization
- Cost forecasting
- Savings recommendations

**Documentation:** [plugins/databricks-engineering/commands/optimize-costs.md](../plugins/databricks-engineering/commands/optimize-costs.md)

---

### Project Setup

#### `/scaffold-project`
Scaffold new Databricks projects with best practices.

**Usage:**
```
/scaffold-project --name data-platform --template bronze-silver-gold
```

**Features:**
- Project templates
- CI/CD setup
- Testing framework
- Documentation
- Best practices

**Documentation:** [plugins/databricks-engineering/commands/scaffold-project.md](../plugins/databricks-engineering/commands/scaffold-project.md)

---

## Databricks MLOps Plugin - Commands

### Model Training

#### `/train-model`
Train ML models with experiment tracking.

**Usage:**
```
/train-model --config model-config.yaml --track mlflow
```

**Documentation:** [plugins/databricks-mlops/commands/train-model.md](../plugins/databricks-mlops/commands/train-model.md)

---

### Model Registry

#### `/register-model`
Register models to MLflow Model Registry.

**Usage:**
```
/register-model --name customer-churn --version v1.0
```

**Documentation:** [plugins/databricks-mlops/commands/register-model.md](../plugins/databricks-mlops/commands/register-model.md)

---

#### `/promote-model`
Promote models through stages (Staging → Production).

**Usage:**
```
/promote-model --name customer-churn --stage production
```

**Documentation:** [plugins/databricks-mlops/commands/promote-model.md](../plugins/databricks-mlops/commands/promote-model.md)

---

### Model Serving

#### `/deploy-model`
Deploy models for real-time or batch inference.

**Usage:**
```
/deploy-model --name customer-churn --endpoint prod
```

**Documentation:** [plugins/databricks-mlops/commands/deploy-model.md](../plugins/databricks-mlops/commands/deploy-model.md)

---

#### `/batch-inference`
Run batch inference on large datasets.

**Usage:**
```
/batch-inference --model customer-churn --input data/predictions
```

**Documentation:** [plugins/databricks-mlops/commands/batch-inference.md](../plugins/databricks-mlops/commands/batch-inference.md)

---

### Feature Store

#### `/create-feature-table`
Create feature tables in Databricks Feature Store.

**Usage:**
```
/create-feature-table --name customer-features --keys customer_id
```

**Documentation:** [plugins/databricks-mlops/commands/create-feature-table.md](../plugins/databricks-mlops/commands/create-feature-table.md)

---

### ML Pipeline

#### `/create-ml-pipeline`
Create end-to-end ML pipelines.

**Usage:**
```
/create-ml-pipeline --name churn-prediction --stages all
```

**Documentation:** [plugins/databricks-mlops/commands/create-ml-pipeline.md](../plugins/databricks-mlops/commands/create-ml-pipeline.md)

---

### Monitoring

#### `/setup-monitoring`
Set up model monitoring and alerting.

**Usage:**
```
/setup-monitoring --model customer-churn --metrics drift,performance
```

**Documentation:** [plugins/databricks-mlops/commands/setup-monitoring.md](../plugins/databricks-mlops/commands/setup-monitoring.md)

---

### Hyperparameter Tuning

#### `/run-hyperparameter-tuning`
Run distributed hyperparameter tuning.

**Usage:**
```
/run-hyperparameter-tuning --config tuning-config.yaml --trials 100
```

**Documentation:** [plugins/databricks-mlops/commands/run-hyperparameter-tuning.md](../plugins/databricks-mlops/commands/run-hyperparameter-tuning.md)

---

### Model Validation

#### `/validate-model`
Validate model performance and compliance.

**Usage:**
```
/validate-model --model customer-churn --tests all
```

**Documentation:** [plugins/databricks-mlops/commands/validate-model.md](../plugins/databricks-mlops/commands/validate-model.md)

---

## Databricks Governance Plugin - Commands

### Access Control

#### `/configure-access-control`
Configure Unity Catalog access controls.

**Usage:**
```
/configure-access-control --catalog prod --policy least-privilege
```

**Documentation:** [plugins/databricks-governance/commands/configure-access-control.md](../plugins/databricks-governance/commands/configure-access-control.md)

---

#### `/audit-permissions`
Audit current permissions and access patterns.

**Usage:**
```
/audit-permissions --scope workspace --report detailed
```

**Documentation:** [plugins/databricks-governance/commands/audit-permissions.md](../plugins/databricks-governance/commands/audit-permissions.md)

---

### Data Classification

#### `/setup-data-classification`
Set up data classification and tagging.

**Usage:**
```
/setup-data-classification --catalog prod --auto-detect
```

**Documentation:** [plugins/databricks-governance/commands/setup-data-classification.md](../plugins/databricks-governance/commands/setup-data-classification.md)

---

#### `/scan-pii-data`
Scan for PII and sensitive data.

**Usage:**
```
/scan-pii-data --table customers --action report
```

**Documentation:** [plugins/databricks-governance/commands/scan-pii-data.md](../plugins/databricks-governance/commands/scan-pii-data.md)

---

### Compliance

#### `/generate-compliance-report`
Generate compliance reports for audits.

**Usage:**
```
/generate-compliance-report --standard gdpr --format pdf
```

**Documentation:** [plugins/databricks-governance/commands/generate-compliance-report.md](../plugins/databricks-governance/commands/generate-compliance-report.md)

---

### Data Lineage

#### `/enforce-data-lineage`
Enforce and track data lineage.

**Usage:**
```
/enforce-data-lineage --catalog prod --track-all
```

**Documentation:** [plugins/databricks-governance/commands/enforce-data-lineage.md](../plugins/databricks-governance/commands/enforce-data-lineage.md)

---

### Security

#### `/configure-encryption`
Configure encryption for data at rest and in transit.

**Usage:**
```
/configure-encryption --scope workspace --type cmk
```

**Documentation:** [plugins/databricks-governance/commands/configure-encryption.md](../plugins/databricks-governance/commands/configure-encryption.md)

---

#### `/setup-data-masking`
Set up data masking for sensitive fields.

**Usage:**
```
/setup-data-masking --table customers --fields ssn,email
```

**Documentation:** [plugins/databricks-governance/commands/setup-data-masking.md](../plugins/databricks-governance/commands/setup-data-masking.md)

---

### Auditing

#### `/audit-data-access`
Audit data access patterns and anomalies.

**Usage:**
```
/audit-data-access --timeframe 30d --anomaly-detection
```

**Documentation:** [plugins/databricks-governance/commands/audit-data-access.md](../plugins/databricks-governance/commands/audit-data-access.md)

---

### Data Retention

#### `/manage-data-retention`
Manage data retention policies.

**Usage:**
```
/manage-data-retention --catalog prod --policy retention-policy.yaml
```

**Documentation:** [plugins/databricks-governance/commands/manage-data-retention.md](../plugins/databricks-governance/commands/manage-data-retention.md)

---

## Command Categories Summary

| Category | Engineering | MLOps | Governance |
|----------|------------|-------|------------|
| **Pipeline** | 2 | 1 | - |
| **Data Products** | 3 | - | - |
| **Deployment** | 3 | 2 | - |
| **Testing** | 2 | 2 | - |
| **Monitoring** | 1 | 1 | - |
| **Security** | - | - | 4 |
| **Compliance** | - | - | 3 |
| **Optimization** | 1 | 1 | - |
| **Setup** | 1 | - | 2 |

---

## Related Documentation

- [Getting Started Guide](getting-started.md)
- [Agents Reference](agents-reference.md)
- [Skills & Templates](skills-reference.md)
- [Configuration Reference](configuration.md)
- [API Documentation](api-reference.md)

---

**Prepared by:** Databricks Platform Team
**Contact:** data-platform@vivekgana.com
