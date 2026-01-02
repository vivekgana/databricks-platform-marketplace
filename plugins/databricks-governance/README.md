# Databricks Governance Plugin

## Overview

Comprehensive data governance toolkit for Databricks Unity Catalog covering compliance, security, access control, data classification, and audit automation. Implement GDPR, HIPAA, SOC2, and CCPA compliance with production-ready patterns and best practices.

## Features

### 10 Governance Commands
- **audit-permissions**: Audit Unity Catalog permissions and identify security gaps
- **setup-data-classification**: Configure data classification and tagging framework
- **enforce-data-lineage**: Track and validate data lineage for compliance
- **configure-access-control**: Set up RBAC/ABAC with row filters and masking
- **scan-pii-data**: Automated PII detection with remediation recommendations
- **generate-compliance-report**: GDPR, HIPAA, SOC2, CCPA compliance reports
- **setup-data-masking**: Column-level masking and dynamic data masking
- **manage-data-retention**: Retention policies and lifecycle management
- **audit-data-access**: Analyze audit logs and detect anomalies
- **configure-encryption**: Encryption at rest/transit and key management

### 8 Specialized Agents
- **compliance-auditor**: Expert in GDPR, HIPAA, SOC2, CCPA standards
- **data-privacy-guardian**: PII protection and consent management
- **access-control-specialist**: IAM, RBAC, ABAC implementation
- **data-classification-expert**: Classification strategies and tagging
- **lineage-tracker**: Data lineage and impact analysis
- **encryption-specialist**: Encryption and key management
- **audit-log-analyzer**: Log analysis and anomaly detection
- **policy-enforcer**: Policy automation and enforcement

### 4 Comprehensive Skills
- **unity-catalog-governance**: Governance patterns and security models
- **data-classification**: Classification frameworks and automation
- **compliance-automation**: Automated compliance checks and monitoring
- **access-management**: RBAC/ABAC patterns and access reviews

### 2 MCP Servers
- **governance-api**: Unity Catalog governance API integration
- **audit-logs**: Audit log query and analysis

## Quick Start

### Install Plugin

```bash
# Install via Claude CLI
claude plugin install databricks-governance

# Or clone from repository
git clone https://github.com/yourcompany/databricks-platform-marketplace
cd plugins/databricks-governance
```

### Environment Setup

```bash
# Set environment variables
export DATABRICKS_HOST="https://your-workspace.databricks.com"
export DATABRICKS_TOKEN="your-access-token"

# Verify connectivity
databricks workspace list
```

### Basic Usage

```bash
# Audit permissions
claude /databricks-governance:audit-permissions --catalog production

# Setup data classification
claude /databricks-governance:setup-data-classification --init --catalog production

# Scan for PII
claude /databricks-governance:scan-pii-data --catalog production --deep-scan

# Generate compliance report
claude /databricks-governance:generate-compliance-report --standard gdpr --catalog production
```

## Common Use Cases

### 1. GDPR Compliance Implementation

```bash
# Step 1: Data inventory and classification
claude /databricks-governance:setup-data-classification --catalog production --auto-classify

# Step 2: PII detection and protection
claude /databricks-governance:scan-pii-data --catalog production --auto-remediate

# Step 3: Access control and masking
claude /databricks-governance:configure-access-control --catalog production --init-rbac
claude /databricks-governance:setup-data-masking --catalog production --auto-mask-pii

# Step 4: Data lineage for deletion cascades
claude /databricks-governance:enforce-data-lineage --catalog production --validate

# Step 5: Compliance validation
claude /databricks-governance:generate-compliance-report --standard gdpr --catalog production
```

### 2. HIPAA PHI Protection

```bash
# Identify PHI data
claude /databricks-governance:scan-pii-data --catalog healthcare --sensitivity restricted

# Encryption setup
claude /databricks-governance:configure-encryption --catalog healthcare --enable-cmk

# Access controls for PHI
claude /databricks-governance:configure-access-control \
  --catalog healthcare \
  --row-filter regional_access \
  --mask-column ssn

# Audit logging
claude /databricks-governance:audit-data-access --pii-access-only --days 90
```

### 3. SOC2 Security Controls

```bash
# Audit all permissions
claude /databricks-governance:audit-permissions --catalog production --compliance-standard soc2

# Enforce least privilege
claude /databricks-governance:configure-access-control --enforce-least-privilege

# Enable encryption
claude /databricks-governance:configure-encryption --catalog production --validate --standard soc2

# Continuous monitoring
claude /databricks-governance:audit-data-access --anomaly-detection --sensitivity high
```

### 4. Regular Governance Reviews

```bash
# Quarterly access review
claude /databricks-governance:audit-permissions --catalog production --export-report

# PII scan for new tables
claude /databricks-governance:scan-pii-data --catalog production

# Compliance posture check
claude /databricks-governance:generate-compliance-report \
  --standards gdpr,hipaa,soc2 \
  --catalog production \
  --full-audit
```

## Architecture

### Plugin Structure

```
databricks-governance/
├── .claude-plugin/
│   └── plugin.json              # Plugin metadata
├── commands/                    # 10 governance commands
│   ├── audit-permissions.md
│   ├── setup-data-classification.md
│   ├── enforce-data-lineage.md
│   ├── configure-access-control.md
│   ├── scan-pii-data.md
│   ├── generate-compliance-report.md
│   ├── setup-data-masking.md
│   ├── manage-data-retention.md
│   ├── audit-data-access.md
│   └── configure-encryption.md
├── agents/                      # 8 specialized agents
│   ├── compliance-auditor.md
│   ├── data-privacy-guardian.md
│   ├── access-control-specialist.md
│   ├── data-classification-expert.md
│   ├── lineage-tracker.md
│   ├── encryption-specialist.md
│   ├── audit-log-analyzer.md
│   └── policy-enforcer.md
├── skills/                      # 4 comprehensive skills
│   ├── unity-catalog-governance/
│   ├── data-classification/
│   ├── compliance-automation/
│   └── access-management/
├── mcp-servers/                 # 2 MCP servers
│   ├── governance-api.json
│   └── audit-logs.json
└── README.md                    # This file
```

### Integration Points

- **Unity Catalog**: Permissions, tags, lineage, metadata
- **System Tables**: Audit logs, access patterns, lineage
- **Databricks APIs**: Workspace, SQL, clusters, jobs
- **External Tools**: SIEM, GRC platforms, ticketing systems

## Best Practices

### Security
1. **Least Privilege**: Grant minimum required permissions
2. **Separation of Duties**: No single user has complete control
3. **Regular Audits**: Weekly permission audits in production
4. **Encryption Everywhere**: At-rest and in-transit encryption
5. **Zero Trust**: Verify every access request

### Compliance
1. **Data Inventory**: Complete catalog of personal data
2. **Classification**: Tag all data by sensitivity
3. **Access Controls**: RBAC with row filters and masking
4. **Audit Trails**: Comprehensive logging and retention
5. **Regular Reviews**: Quarterly compliance assessments

### Operations
1. **Automate Everything**: Manual processes introduce errors
2. **Monitor Continuously**: Real-time compliance monitoring
3. **Document Decisions**: Maintain audit trail of changes
4. **Test Regularly**: Validate controls quarterly
5. **Incident Response**: Documented breach procedures

## Configuration

### Plugin Configuration

```yaml
# .databricks-governance-config.yaml
databricks:
  host: ${DATABRICKS_HOST}
  token: ${DATABRICKS_TOKEN}

governance:
  default_catalog: production
  classification:
    auto_classify: true
    deep_scan: false
    sample_rate: 0.01
  compliance:
    standards: [gdpr, hipaa, soc2]
    alert_on_violations: true
  audit:
    retention_days: 365
    anomaly_detection: true
```

### Environment Variables

```bash
# Databricks connectivity
export DATABRICKS_HOST="https://your-workspace.databricks.com"
export DATABRICKS_TOKEN="your-access-token"

# Governance settings
export DATABRICKS_GOVERNANCE_DEFAULT_CATALOG="production"
export DATABRICKS_GOVERNANCE_AUTO_REMEDIATE="false"
export DATABRICKS_GOVERNANCE_ALERT_EMAIL="governance-team@company.com"
```

## Compliance Standards Supported

### GDPR (General Data Protection Regulation)
- Article 5: Data processing principles
- Article 17: Right to erasure
- Article 30: Records of processing
- Article 32: Security measures
- Article 33: Breach notification

### HIPAA (Health Insurance Portability)
- Administrative safeguards
- Physical safeguards
- Technical safeguards
- PHI protection requirements

### SOC2 (Service Organization Control 2)
- Security
- Availability
- Processing integrity
- Confidentiality
- Privacy

### CCPA (California Consumer Privacy Act)
- Right to know
- Right to delete
- Right to opt-out
- Data minimization

### PCI-DSS (Payment Card Industry)
- Cardholder data protection
- Encryption requirements
- Access controls
- Audit logging

## Troubleshooting

### Common Issues

**Issue: Permission denied errors**
```bash
# Verify token has metastore admin privileges
databricks unity-catalog metastores list

# Check user is metastore admin
databricks unity-catalog metastore-admins list
```

**Issue: Classification not detecting PII**
```bash
# Run deep scan with content sampling
claude /databricks-governance:scan-pii-data \
  --catalog production \
  --deep-scan \
  --sample-rate 0.1
```

**Issue: Compliance report shows gaps**
```bash
# Run detailed audit to identify specific issues
claude /databricks-governance:audit-permissions \
  --catalog production \
  --compliance-standard gdpr \
  --export-format json
```

## Support

- Documentation: [Plugin Documentation](./docs/)
- Issues: [GitHub Issues](https://github.com/yourcompany/databricks-platform-marketplace/issues)
- Email: data-platform@yourcompany.com
- Slack: #databricks-governance

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](../../LICENSE) for details.

## Changelog

### v1.0.0 (2026-01-02)
- Initial release
- 10 governance commands
- 8 specialized agents
- 4 comprehensive skills
- 2 MCP servers
- Full GDPR, HIPAA, SOC2, CCPA support
