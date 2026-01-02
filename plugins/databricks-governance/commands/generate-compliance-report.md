# Generate Compliance Report Command

## Description
Generate comprehensive compliance reports for GDPR, HIPAA, SOC2, CCPA regulations with evidence collection, gap analysis, and remediation roadmaps.

## Usage
```bash
claude /databricks-governance:generate-compliance-report --standard [gdpr|hipaa|soc2|ccpa] [options]
```

## Examples

```bash
# GDPR compliance report
claude /databricks-governance:generate-compliance-report --standard gdpr --catalog production

# Multi-standard audit
claude /databricks-governance:generate-compliance-report --standards gdpr,hipaa,soc2 --full-audit

# Quick compliance check
claude /databricks-governance:generate-compliance-report --standard gdpr --quick-check
```

## Compliance Standards

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
- Audit controls

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

## Report Structure

```markdown
# Compliance Report: GDPR
**Report Date**: 2026-01-02
**Scope**: production catalog
**Compliance Score**: 78/100 (Needs Improvement)

## Executive Summary
- **Compliant Controls**: 34/45 (76%)
- **Critical Gaps**: 3
- **High Priority Items**: 8
- **Estimated Remediation**: 6-8 weeks

## Compliance Assessment

### GDPR Article 5: Data Processing Principles
**Status**: ⚠️ Partial Compliance
**Score**: 70/100

#### Lawfulness, Fairness, Transparency
✅ **Compliant**: Privacy notices documented
✅ **Compliant**: Legal basis documented for processing
⚠️ **Gap**: Consent mechanisms not implemented for marketing data
❌ **Critical**: No transparency reports for data subjects

#### Purpose Limitation
✅ **Compliant**: Data purposes documented in metadata
❌ **Critical**: Production data used in non-production environments

#### Data Minimization
⚠️ **Gap**: Collecting unnecessary PII (12 tables identified)
⚠️ **Gap**: Retention periods exceed business need

### GDPR Article 17: Right to Erasure
**Status**: ❌ Non-Compliant
**Score**: 40/100

❌ **Critical**: No automated deletion process
❌ **Critical**: Data lineage incomplete for deletion cascades
⚠️ **Gap**: 45-day response time exceeds 30-day requirement
```

## Compliance Checks

### GDPR Checks
```python
GDPR_CHECKS = {
    "data_inventory": "Complete inventory of personal data",
    "legal_basis": "Legal basis documented for each processing activity",
    "consent_management": "Consent capture and withdrawal mechanisms",
    "data_minimization": "Only necessary data collected",
    "purpose_limitation": "Data used only for documented purposes",
    "accuracy": "Data accuracy and correction processes",
    "storage_limitation": "Retention policies implemented",
    "security": "Appropriate technical and organizational measures",
    "right_to_access": "Data subject access request process",
    "right_to_erasure": "Automated deletion capabilities",
    "right_to_portability": "Data export in machine-readable format",
    "dpia": "Data Protection Impact Assessments for high-risk processing",
    "breach_notification": "72-hour breach notification process"
}
```

### HIPAA Checks
```python
HIPAA_CHECKS = {
    "access_control": "Unique user identification and authentication",
    "audit_controls": "Hardware, software, and procedural audit logs",
    "integrity_controls": "Policies to ensure PHI is not altered",
    "transmission_security": "Encryption for PHI in transit",
    "encryption": "Encryption for PHI at rest",
    "automatic_logoff": "Session timeout mechanisms",
    "emergency_access": "Emergency access procedures",
    "business_associate": "Business Associate Agreements in place"
}
```

## Automated Evidence Collection

```python
def collect_gdpr_evidence(catalog: str) -> Dict:
    """Collect evidence for GDPR compliance."""
    evidence = {
        "data_inventory": collect_data_inventory(catalog),
        "access_controls": audit_access_controls(catalog),
        "encryption_status": check_encryption(catalog),
        "retention_policies": get_retention_policies(catalog),
        "deletion_capabilities": test_deletion_process(catalog),
        "audit_logs": collect_audit_logs(catalog, days=90),
        "data_lineage": validate_lineage_completeness(catalog),
        "pii_protection": scan_pii_protection(catalog)
    }
    return evidence
```

## Gap Analysis and Remediation

```markdown
## Critical Gaps and Remediation Plan

### Gap 1: Right to Erasure Not Implemented
**Regulation**: GDPR Article 17
**Risk Level**: CRITICAL
**Business Impact**: Regulatory fines up to 4% of revenue
**Remediation Steps**:
1. Implement deletion cascade logic (2 weeks)
2. Create data subject deletion API (1 week)
3. Test deletion across all systems (2 weeks)
4. Document deletion procedures (1 week)
**Estimated Cost**: $50,000
**Target Completion**: 2026-02-15

### Gap 2: Incomplete Data Lineage
**Regulation**: GDPR Article 30
**Risk Level**: HIGH
**Remediation Steps**:
1. Map complete data flows (3 weeks)
2. Implement lineage tracking (2 weeks)
3. Validate lineage accuracy (1 week)
**Target Completion**: 2026-02-28
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--standard` | Compliance standard | Required |
| `--standards` | Multiple standards (comma-separated) | Single |
| `--catalog` | Catalog scope | All |
| `--full-audit` | Comprehensive audit | False |
| `--quick-check` | High-level assessment | False |
| `--evidence-path` | Evidence collection path | ./compliance-evidence/ |
| `--export-format` | pdf, html, markdown | markdown |

## Output Files

```
compliance-reports/
├── gdpr-compliance-report-{date}.md
├── evidence-collection-{date}.json
├── gap-analysis-{date}.csv
├── remediation-roadmap-{date}.md
└── executive-summary-{date}.pdf
```

## Related Commands
- `/databricks-governance:audit-permissions` - Access control audit
- `/databricks-governance:scan-pii-data` - PII detection
- `/databricks-governance:enforce-data-lineage` - Lineage validation
- `/databricks-governance:manage-data-retention` - Retention policies
