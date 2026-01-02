# Scan PII Data Command

## Description
Automated PII and sensitive data discovery across Unity Catalog using pattern matching, ML-based detection, and content analysis with automated remediation recommendations.

## Usage
```bash
claude /databricks-governance:scan-pii-data [options]
```

## Examples

```bash
# Scan entire catalog for PII
claude /databricks-governance:scan-pii-data --catalog production

# Deep scan with content sampling
claude /databricks-governance:scan-pii-data --catalog production --deep-scan --sample-rate 0.1

# Scan and auto-remediate
claude /databricks-governance:scan-pii-data --catalog production --auto-remediate --apply-masking
```

## What It Does

1. **Schema-Based Detection** - Analyzes column names and types
2. **Pattern Matching** - Regex patterns for SSN, credit cards, emails
3. **Content Sampling** - Samples data to detect actual PII
4. **ML Classification** - Uses ML models to identify PII
5. **Remediation Planning** - Generates masking and encryption recommendations

## PII Categories Detected

### Direct Identifiers
- Full names, email addresses, phone numbers
- SSN, passport numbers, driver's licenses
- IP addresses, device IDs

### Quasi-Identifiers
- Zip codes, dates of birth, gender
- Geographic locations, employment info

### Sensitive Attributes
- Health conditions, racial/ethnic origin
- Religious beliefs, political opinions
- Biometric data, genetic information

### Financial Data
- Credit card numbers, bank accounts
- Payment information, salary data

## Detection Methods

### Pattern-Based Detection
```python
PII_PATTERNS = {
    'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
    'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
}
```

### Content Sampling
```python
def sample_column_for_pii(table: str, column: str, sample_rate: float = 0.01):
    """Sample column content to detect PII."""
    sample_data = spark.table(table) \
        .select(column) \
        .sample(sample_rate) \
        .limit(1000) \
        .collect()

    pii_matches = []
    for row in sample_data:
        for pii_type, pattern in PII_PATTERNS.items():
            if re.match(pattern, str(row[0])):
                pii_matches.append(pii_type)

    return list(set(pii_matches))
```

## Output Report

```markdown
# PII Scan Report - production catalog
**Date**: 2026-01-02 15:30:00
**Tables Scanned**: 247
**PII Instances Found**: 1,834

## High Risk Findings

### 1. Unprotected SSN Column
**Table**: production.customers.profiles
**Column**: social_security_number
**PII Type**: SSN (Direct Identifier)
**Risk Level**: CRITICAL
**Current Protection**: None
**Recommendation**: Apply full masking function
**Remediation**:
```sql
ALTER TABLE production.customers.profiles
ALTER COLUMN social_security_number
SET MASK governance.masks.ssn_full_redact;
```

### 2. Plain Text Email Addresses
**Table**: production.marketing.contacts
**Column**: email_address
**PII Type**: Email (Direct Identifier)
**Risk Level**: HIGH
**Current Protection**: None
**Recommendation**: Apply conditional masking based on access level
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--catalog` | Catalog to scan | Required |
| `--schema` | Specific schema | All |
| `--deep-scan` | Sample actual data | False |
| `--sample-rate` | Data sampling percentage | 0.01 |
| `--auto-remediate` | Apply remediation | False |
| `--apply-masking` | Auto-apply masking | False |
| `--export-path` | Report output path | ./pii-scans/ |

## Remediation Actions

1. **Immediate**: Apply masking to critical PII
2. **Short-term**: Implement row filters
3. **Long-term**: Re-architect to eliminate unnecessary PII storage

## Related Commands
- `/databricks-governance:setup-data-masking` - Configure masking
- `/databricks-governance:setup-data-classification` - Classify data
- `/databricks-governance:generate-compliance-report` - Compliance validation
