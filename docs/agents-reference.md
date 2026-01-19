# Agents Reference

**Document Version:** 1.0
**Last Updated:** 2026-01-04 00:29:00
**Prepared by:** Databricks Platform Team

---

## Overview

AI agents in the Databricks Platform Marketplace provide intelligent code review, optimization recommendations, and expert guidance for data engineering, MLOps, and governance workflows.

## Databricks Engineering Agents

### Pipeline & Architecture Agents

#### Pipeline Architect
Expert in designing and optimizing data pipelines with best practices.

**Capabilities:**
- Pipeline design review
- Architecture recommendations
- Performance optimization
- Error handling strategies
- Scalability analysis

**Documentation:** [plugins/databricks-engineering/agents/pipeline-architect.md](../plugins/databricks-engineering/agents/pipeline-architect.md)

---

#### Delta Lake Expert
Specialist in Delta Lake optimization and best practices.

**Capabilities:**
- Table optimization (OPTIMIZE, Z-ORDER)
- Partition strategy
- Liquid clustering recommendations
- Vacuum optimization
- Time travel queries

**Documentation:** [plugins/databricks-engineering/agents/delta-lake-expert.md](../plugins/databricks-engineering/agents/delta-lake-expert.md)

---

#### Unity Catalog Expert
Expert in Unity Catalog configuration and governance.

**Capabilities:**
- Catalog structure design
- Access control best practices
- Schema organization
- Table migration strategies
- External location setup

**Documentation:** [plugins/databricks-engineering/agents/unity-catalog-expert.md](../plugins/databricks-engineering/agents/unity-catalog-expert.md)

---

### Quality & Testing Agents

#### Data Quality Sentinel
Automated data quality monitoring and validation.

**Capabilities:**
- Schema validation
- Data profiling
- Anomaly detection
- Quality metrics tracking
- Great Expectations integration

**Documentation:** [plugins/databricks-engineering/agents/data-quality-sentinel.md](../plugins/databricks-engineering/agents/data-quality-sentinel.md)

---

#### Security Guardian
Security best practices and vulnerability detection.

**Capabilities:**
- Security scan
- Secret detection
- Access control review
- Encryption validation
- Compliance checking

**Documentation:** [plugins/databricks-engineering/agents/security-guardian.md](../plugins/databricks-engineering/agents/security-guardian.md)

---

### Cost & Performance Agents

#### Cost Analyzer
Cost optimization and resource efficiency analysis.

**Capabilities:**
- Cluster cost analysis
- Storage optimization
- Job cost breakdown
- Right-sizing recommendations
- Savings projections

**Documentation:** [plugins/databricks-engineering/agents/cost-analyzer.md](../plugins/databricks-engineering/agents/cost-analyzer.md)

---

#### Streaming Specialist
Real-time streaming pipeline expert.

**Capabilities:**
- Structured Streaming design
- Watermark configuration
- Checkpoint management
- Auto Loader setup
- Performance tuning

**Documentation:** [plugins/databricks-engineering/agents/streaming-specialist.md](../plugins/databricks-engineering/agents/streaming-specialist.md)

---

### Data Products Agents

#### Data Product Architect
Design and implement data products with contracts and SLAs.

**Capabilities:**
- Data contract design
- SLA definition
- Consumer management
- Quality monitoring
- Lineage tracking

**Documentation:** [plugins/databricks-engineering/agents/data-product-architect.md](../plugins/databricks-engineering/agents/data-product-architect.md)

---

#### Data Contract Validator
Validate data contracts and ensure compliance.

**Capabilities:**
- Schema validation
- Contract enforcement
- Version compatibility
- Breaking change detection
- Documentation generation

**Documentation:** [plugins/databricks-engineering/agents/data-contract-validator.md](../plugins/databricks-engineering/agents/data-contract-validator.md)

---

### Monitoring & Operations Agents

#### SLA Guardian
Monitor and enforce SLA compliance.

**Capabilities:**
- SLA tracking
- Alert configuration
- Performance monitoring
- Availability checks
- Incident response

**Documentation:** [plugins/databricks-engineering/agents/sla-guardian.md](../plugins/databricks-engineering/agents/sla-guardian.md)

---

## Databricks MLOps Agents

### Model Development Agents

#### MLflow Expert
MLflow experiment tracking and model registry specialist.

**Capabilities:**
- Experiment design
- Model logging best practices
- Registry management
- Model versioning
- Artifact tracking

**Documentation:** [plugins/databricks-mlops/agents/mlflow-expert.md](../plugins/databricks-mlops/agents/mlflow-expert.md)

---

#### Feature Store Specialist
Feature engineering and feature store management.

**Capabilities:**
- Feature table design
- Feature serving patterns
- Point-in-time lookups
- Feature versioning
- Feature monitoring

**Documentation:** [plugins/databricks-mlops/agents/feature-store-specialist.md](../plugins/databricks-mlops/agents/feature-store-specialist.md)

---

### Model Deployment Agents

#### Model Serving Specialist
Model deployment and serving optimization.

**Capabilities:**
- Endpoint configuration
- Autoscaling setup
- A/B testing
- Canary deployments
- Performance optimization

**Documentation:** [plugins/databricks-mlops/agents/model-serving-specialist.md](../plugins/databricks-mlops/agents/model-serving-specialist.md)

---

#### Model Monitoring Expert
Monitor model performance and detect drift.

**Capabilities:**
- Drift detection
- Performance monitoring
- Data quality checks
- Alerting setup
- Remediation strategies

**Documentation:** [plugins/databricks-mlops/agents/model-monitoring-expert.md](../plugins/databricks-mlops/agents/model-monitoring-expert.md)

---

### ML Pipeline Agents

#### ML Pipeline Architect
Design end-to-end ML pipelines.

**Capabilities:**
- Pipeline orchestration
- Feature engineering integration
- Model training automation
- Deployment workflows
- Monitoring integration

**Documentation:** [plugins/databricks-mlops/agents/ml-pipeline-architect.md](../plugins/databricks-mlops/agents/ml-pipeline-architect.md)

---

#### Hyperparameter Optimizer
Optimize model hyperparameters efficiently.

**Capabilities:**
- Search space design
- Distributed tuning
- Early stopping strategies
- Result analysis
- Best model selection

**Documentation:** [plugins/databricks-mlops/agents/hyperparameter-optimizer.md](../plugins/databricks-mlops/agents/hyperparameter-optimizer.md)

---

### AutoML & Security Agents

#### AutoML Expert
Automated machine learning and model selection.

**Capabilities:**
- AutoML configuration
- Model comparison
- Feature importance
- Hyperparameter tuning
- Deployment preparation

**Documentation:** [plugins/databricks-mlops/agents/automl-expert.md](../plugins/databricks-mlops/agents/automl-expert.md)

---

#### ML Security Guardian
ML model security and privacy protection.

**Capabilities:**
- Model vulnerability scanning
- Privacy impact assessment
- Adversarial attack detection
- Model explainability
- Compliance checking

**Documentation:** [plugins/databricks-mlops/agents/ml-security-guardian.md](../plugins/databricks-mlops/agents/ml-security-guardian.md)

---

## Databricks Governance Agents

### Compliance & Audit Agents

#### Compliance Auditor
Ensure regulatory compliance and generate audit reports.

**Capabilities:**
- GDPR compliance
- HIPAA validation
- SOC 2 requirements
- Audit trail generation
- Policy enforcement

**Documentation:** [plugins/databricks-governance/agents/compliance-auditor.md](../plugins/databricks-governance/agents/compliance-auditor.md)

---

#### Audit Log Analyzer
Analyze access patterns and security events.

**Capabilities:**
- Access pattern analysis
- Anomaly detection
- Security event correlation
- Compliance reporting
- Forensics support

**Documentation:** [plugins/databricks-governance/agents/audit-log-analyzer.md](../plugins/databricks-governance/agents/audit-log-analyzer.md)

---

### Access Control Agents

#### Access Control Specialist
Configure and optimize access controls.

**Capabilities:**
- Role-based access control
- Attribute-based access control
- Least privilege enforcement
- Permission auditing
- Access reviews

**Documentation:** [plugins/databricks-governance/agents/access-control-specialist.md](../plugins/databricks-governance/agents/access-control-specialist.md)

---

#### Policy Enforcer
Enforce organizational policies and standards.

**Capabilities:**
- Policy definition
- Automated enforcement
- Violation detection
- Remediation workflows
- Policy reporting

**Documentation:** [plugins/databricks-governance/agents/policy-enforcer.md](../plugins/databricks-governance/agents/policy-enforcer.md)

---

### Data Protection Agents

#### Data Privacy Guardian
Protect sensitive and PII data.

**Capabilities:**
- PII detection
- Data masking
- Anonymization strategies
- Privacy impact assessment
- Consent management

**Documentation:** [plugins/databricks-governance/agents/data-privacy-guardian.md](../plugins/databricks-governance/agents/data-privacy-guardian.md)

---

#### Data Classification Expert
Classify and tag sensitive data.

**Capabilities:**
- Automated classification
- Sensitivity labeling
- Metadata tagging
- Classification rules
- Tag propagation

**Documentation:** [plugins/databricks-governance/agents/data-classification-expert.md](../plugins/databricks-governance/agents/data-classification-expert.md)

---

#### Encryption Specialist
Configure and manage encryption.

**Capabilities:**
- Encryption at rest
- Encryption in transit
- Key management
- Customer-managed keys
- Encryption auditing

**Documentation:** [plugins/databricks-governance/agents/encryption-specialist.md](../plugins/databricks-governance/agents/encryption-specialist.md)

---

### Lineage & Tracking Agents

#### Lineage Tracker
Track and visualize data lineage.

**Capabilities:**
- Column-level lineage
- Impact analysis
- Dependency mapping
- Lineage visualization
- Change propagation

**Documentation:** [plugins/databricks-governance/agents/lineage-tracker.md](../plugins/databricks-governance/agents/lineage-tracker.md)

---

## Agent Categories Summary

| Category | Engineering | MLOps | Governance | Total |
|----------|-------------|-------|------------|-------|
| **Architecture & Design** | 3 | 1 | - | 4 |
| **Quality & Testing** | 2 | - | - | 2 |
| **Security** | 1 | 1 | 3 | 5 |
| **Cost & Performance** | 2 | - | - | 2 |
| **Data Products** | 2 | - | - | 2 |
| **Monitoring** | 1 | 1 | 1 | 3 |
| **Compliance** | - | - | 2 | 2 |
| **Model Management** | - | 4 | - | 4 |
| **Data Protection** | - | - | 3 | 3 |
| **ML Pipeline** | - | 2 | - | 2 |
| **Access Control** | - | - | 2 | 2 |
| **Lineage** | - | - | 1 | 1 |
| **Total** | **11** | **9** | **12** | **32** |

---

## Using Agents

### General Syntax

```bash
# Ask an agent for review
@agent-name review [file/code]

# Ask for recommendations
@agent-name recommend [context]

# Ask for analysis
@agent-name analyze [target]
```

### Examples

```bash
# Pipeline review
@pipeline-architect review notebooks/etl_pipeline.py

# Delta optimization
@delta-lake-expert optimize table customers

# Security scan
@security-guardian scan workspace

# Cost analysis
@cost-analyzer analyze cluster-costs --period 30d

# Model monitoring
@model-monitoring-expert check customer-churn-model

# Compliance audit
@compliance-auditor report --standard gdpr
```

---

## Related Documentation

- [Commands Reference](commands-reference.md)
- [Skills & Templates](skills-reference.md)
- [Getting Started Guide](getting-started.md)
- [Configuration Reference](configuration.md)

---

**Prepared by:** Databricks Platform Team
**Contact:** data-platform@vivekgana.com
