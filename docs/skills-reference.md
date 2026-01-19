# Skills & Templates Reference

**Document Version:** 1.0
**Last Updated:** 2026-01-04 00:29:00
**Prepared by:** Databricks Platform Team

---

## Overview

Skills provide reusable architecture patterns, templates, and best practices for common Databricks workflows. Each skill includes complete examples, templates, and documentation.

## Databricks Engineering Skills

### 1. Delta Live Tables (DLT)

Build production-grade data pipelines with Delta Live Tables using medallion architecture.

**Includes:**
- Bronze layer ingestion templates
- Silver layer transformation patterns
- Gold layer aggregation examples
- Complete e-commerce pipeline
- DLT expectations and quality checks
- Configuration templates

**Templates:**
- `bronze_ingestion_template.py` (296 lines)
- `silver_transformation_template.py` (407 lines)
- `gold_aggregation_template.py` (488 lines)
- `complete_ecommerce_pipeline.py` (564 lines)
- `dlt_pipeline_config.yaml` (335 lines)

**Documentation:** [plugins/databricks-engineering/skills/delta-live-tables/](../plugins/databricks-engineering/skills/delta-live-tables/)

**Quick Start:**
```bash
# Use skill to generate DLT pipeline
/use-skill delta-live-tables --template bronze-silver-gold
```

---

### 2. Data Products

Create self-service data products with contracts, SLAs, and monitoring.

**Includes:**
- Data product definition templates
- Data contract schemas
- Product metadata management
- Consumer management
- Quality monitoring
- SLA tracking

**Templates:**
- `data_product_definition.yaml`
- `data_contract_schema.json`
- `product_metadata.py`
- `customer360_product.py`

**Documentation:** [plugins/databricks-engineering/skills/data-products/](../plugins/databricks-engineering/skills/data-products/)

**Quick Start:**
```bash
# Create data product
/use-skill data-products --name customer-360
```

---

### 3. Data Quality

Implement comprehensive data quality with automated validation and profiling.

**Includes:**
- Great Expectations integration
- Custom validators
- Data profiling templates
- DLT quality checks
- Anomaly detection
- Quality metrics tracking

**Templates:**
- `great_expectations_suite.py` (169 lines)
- `custom_validators.py` (59 lines)
- `data_profiling.py` (37 lines)
- `dlt_quality_checks.py` (32 lines)

**Documentation:** [plugins/databricks-engineering/skills/data-quality/](../plugins/databricks-engineering/skills/data-quality/)

**Quick Start:**
```bash
# Set up data quality
/use-skill data-quality --table customers --profile full
```

---

### 4. Databricks Asset Bundles (DAB)

Deploy and manage Databricks assets with bundles.

**Includes:**
- Bundle configuration templates
- Multi-environment deployment
- CI/CD integration
- Deployment workflows
- Environment-specific configs

**Templates:**
- `databricks.yml` (40 lines)
- `environments-dev.yml` (14 lines)
- `environments-prod.yml` (17 lines)
- `deployment_workflow.py` (46 lines)

**Documentation:** [plugins/databricks-engineering/skills/databricks-asset-bundles/](../plugins/databricks-engineering/skills/databricks-asset-bundles/)

**Quick Start:**
```bash
# Initialize bundle
/use-skill databricks-asset-bundles --init
```

---

### 5. Delta Sharing

Share data securely with external organizations using Delta Sharing.

**Includes:**
- Share configuration templates
- Recipient management
- Usage monitoring
- External data sharing patterns
- Access control

**Templates:**
- `share_configuration.py` (37 lines)
- `recipient_management.py` (33 lines)
- `usage_monitoring.py` (29 lines)
- `external_data_sharing.py` (47 lines)

**Documentation:** [plugins/databricks-engineering/skills/delta-sharing/](../plugins/databricks-engineering/skills/delta-sharing/)

**Quick Start:**
```bash
# Configure Delta Sharing
/use-skill delta-sharing --table customers --recipient partner-a
```

---

### 6. CI/CD Workflows

Implement automated testing and deployment pipelines.

**Includes:**
- GitHub Actions templates
- Deployment scripts
- Test runners
- Validation workflows
- Release automation

**Templates:**
- `.github-workflows-ci.yml` (40 lines)
- `.github-workflows-deploy.yml` (37 lines)
- `deployment_script.py` (47 lines)
- `test_runner.sh` (16 lines)

**Documentation:** [plugins/databricks-engineering/skills/cicd-workflows/](../plugins/databricks-engineering/skills/cicd-workflows/)

**Quick Start:**
```bash
# Set up CI/CD
/use-skill cicd-workflows --provider github-actions
```

---

### 7. Testing Patterns

Comprehensive testing patterns for Databricks pipelines.

**Includes:**
- Pytest fixtures for Spark
- DataFrame assertions
- Integration test templates
- Test data generation
- Mock patterns

**Templates:**
- `conftest.py` (27 lines)
- `spark_fixtures.py` (33 lines)
- `dataframe_assertions.py` (27 lines)
- `test_transformation_pipeline.py` (20 lines)

**Documentation:** [plugins/databricks-engineering/skills/testing-patterns/](../plugins/databricks-engineering/skills/testing-patterns/)

**Quick Start:**
```bash
# Set up testing
/use-skill testing-patterns --framework pytest
```

---

## Databricks MLOps Skills

### 1. MLflow Tracking

Experiment tracking and model management with MLflow.

**Includes:**
- Experiment tracking templates
- Model logging patterns
- Artifact management
- Parameter tracking
- Metric visualization

**Templates:**
- `experiment_tracking_template.py` (99 lines)
- `sklearn_classification.py` (108 lines)

**Documentation:** [plugins/databricks-mlops/skills/mlflow-tracking/](../plugins/databricks-mlops/skills/mlflow-tracking/)

**Quick Start:**
```bash
# Set up MLflow tracking
/use-skill mlflow-tracking --experiment customer-churn
```

---

### 2. Feature Engineering

Feature store patterns and feature engineering workflows.

**Includes:**
- Feature table templates
- Time series features
- Feature serving patterns
- Feature monitoring

**Templates:**
- `feature_table_template.py` (36 lines)
- `time_series_features.py` (27 lines)

**Documentation:** [plugins/databricks-mlops/skills/feature-engineering/](../plugins/databricks-mlops/skills/feature-engineering/)

**Quick Start:**
```bash
# Create feature table
/use-skill feature-engineering --table customer-features
```

---

### 3. Model Serving

Model deployment and serving patterns.

**Includes:**
- Endpoint deployment templates
- A/B testing patterns
- Canary deployments
- Load balancing

**Templates:**
- `endpoint_deployment_template.py` (51 lines)
- `ab_testing_deployment.py` (41 lines)

**Documentation:** [plugins/databricks-mlops/skills/model-serving/](../plugins/databricks-mlops/skills/model-serving/)

**Quick Start:**
```bash
# Deploy model endpoint
/use-skill model-serving --model customer-churn --endpoint prod
```

---

### 4. ML Monitoring

Monitor model performance and detect drift.

**Includes:**
- Drift detection templates
- Performance monitoring
- Alert configuration
- Remediation workflows

**Templates:**
- `monitoring_setup_template.py` (31 lines)
- `drift_detection.py` (38 lines)

**Documentation:** [plugins/databricks-mlops/skills/ml-monitoring/](../plugins/databricks-mlops/skills/ml-monitoring/)

**Quick Start:**
```bash
# Set up monitoring
/use-skill ml-monitoring --model customer-churn --metrics drift,performance
```

---

## Databricks Governance Skills

### 1. Unity Catalog Governance

Unity Catalog configuration and governance patterns.

**Includes:**
- Catalog structure templates
- Access control patterns
- Schema organization
- External locations
- Data lineage setup

**Documentation:** [plugins/databricks-governance/skills/unity-catalog-governance/](../plugins/databricks-governance/skills/unity-catalog-governance/)

**Quick Start:**
```bash
# Set up Unity Catalog
/use-skill unity-catalog-governance --catalog prod
```

---

### 2. Data Classification

Automated data classification and tagging.

**Includes:**
- Classification rules
- Sensitivity labeling
- Metadata tagging
- PII detection
- Tag propagation

**Documentation:** [plugins/databricks-governance/skills/data-classification/](../plugins/databricks-governance/skills/data-classification/)

**Quick Start:**
```bash
# Classify data
/use-skill data-classification --catalog prod --auto-detect
```

---

### 3. Access Management

Role-based access control and permissions.

**Includes:**
- RBAC templates
- Permission matrices
- Access reviews
- Least privilege patterns

**Documentation:** [plugins/databricks-governance/skills/access-management/](../plugins/databricks-governance/skills/access-management/)

**Quick Start:**
```bash
# Configure access
/use-skill access-management --policy least-privilege
```

---

### 4. Compliance Automation

Automated compliance checking and reporting.

**Includes:**
- GDPR compliance
- HIPAA validation
- SOC 2 requirements
- Audit automation

**Documentation:** [plugins/databricks-governance/skills/compliance-automation/](../plugins/databricks-governance/skills/compliance-automation/)

**Quick Start:**
```bash
# Run compliance check
/use-skill compliance-automation --standard gdpr
```

---

## Project Templates

Complete project scaffolding with best practices.

### 1. Bronze-Silver-Gold Medallion Architecture

Complete medallion architecture implementation.

**Includes:**
- Bronze layer ingestion (390 lines)
- Silver layer transformations (475 lines)
- Gold layer aggregations (166 lines)
- Data quality checks (91 lines)
- Complete test suite (121 lines)
- CI/CD configuration (165 lines)

**Location:** [plugins/databricks-engineering/templates/bronze-silver-gold/](../plugins/databricks-engineering/templates/bronze-silver-gold/)

**Files:** 14 files, 2,000+ lines

---

### 2. Data Product Template

Production-ready data product with contracts and monitoring.

**Includes:**
- Data contracts (194 lines)
- Product definition (116 lines)
- Quality checks (94 lines)
- Monitoring setup (112 lines)
- Pipeline implementation (97 lines)
- SLA definitions (189 lines)

**Location:** [plugins/databricks-engineering/templates/data-product/](../plugins/databricks-engineering/templates/data-product/)

**Files:** 11 files, 800+ lines

---

### 3. Delta Live Tables Project

Complete DLT project with expectations.

**Includes:**
- DLT pipeline (343 lines)
- Bronze/Silver/Gold expectations (54 lines)
- Configuration (72 lines + 46 lines)
- Test suite (55 lines)

**Location:** [plugins/databricks-engineering/templates/delta-live-tables/](../plugins/databricks-engineering/templates/delta-live-tables/)

**Files:** 11 files, 600+ lines

---

### 4. MLflow Project

End-to-end ML project with tracking and serving.

**Includes:**
- Model training (139 lines)
- Feature engineering (150 lines)
- Model serving (69 lines)
- Monitoring (75 lines)
- Notebooks (77 lines)
- Configuration (128 lines)

**Location:** [plugins/databricks-engineering/templates/mlflow-project/](../plugins/databricks-engineering/templates/mlflow-project/)

**Files:** 11 files, 650+ lines

---

## Skills Summary

| Plugin | Skills | Templates | Total Lines |
|--------|--------|-----------|-------------|
| **Engineering** | 7 | 4 | 10,000+ |
| **MLOps** | 4 | 1 | 2,000+ |
| **Governance** | 4 | - | 1,500+ |
| **Total** | **15** | **5** | **13,500+** |

---

## Using Skills

### General Syntax

```bash
# Use a skill
/use-skill <skill-name> [options]

# List available skills
/list-skills

# Get skill documentation
/skill-info <skill-name>
```

### Examples

```bash
# Generate DLT pipeline
/use-skill delta-live-tables --template bronze-silver-gold --name customer-etl

# Create data product
/use-skill data-products --name customer-360 --contract schema.json

# Set up testing
/use-skill testing-patterns --framework pytest --coverage 90

# Deploy with bundles
/use-skill databricks-asset-bundles --environment prod

# Configure CI/CD
/use-skill cicd-workflows --provider github-actions --deploy-on push
```

---

## Related Documentation

- [Commands Reference](commands-reference.md)
- [Agents Reference](agents-reference.md)
- [Getting Started Guide](getting-started.md)
- [Configuration Reference](configuration.md)

---

**Prepared by:** Databricks Platform Team
**Contact:** data-platform@vivekgana.com
