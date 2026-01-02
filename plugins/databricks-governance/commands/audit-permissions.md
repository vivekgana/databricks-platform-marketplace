# Audit Permissions Command

## Description
Comprehensive audit of Unity Catalog permissions across catalogs, schemas, tables, views, volumes, and functions. Identifies privilege misconfigurations, excessive permissions, and compliance violations.

## Usage
```bash
claude /databricks-governance:audit-permissions [options]
```

## Examples

### Audit All Catalogs
```bash
claude /databricks-governance:audit-permissions
```

### Audit Specific Catalog
```bash
claude /databricks-governance:audit-permissions --catalog production
```

### Audit with Compliance Check
```bash
claude /databricks-governance:audit-permissions \
  --catalog production \
  --compliance-standard gdpr \
  --output-format json
```

### Find Excessive Permissions
```bash
claude /databricks-governance:audit-permissions \
  --check excessive-access \
  --severity high
```

## What It Does

1. **Permission Discovery**
   - Lists all grants on catalogs, schemas, tables, volumes
   - Identifies direct and inherited permissions
   - Maps user and group access patterns
   - Detects service principal permissions

2. **Privilege Analysis**
   - Checks for ALL PRIVILEGES grants
   - Identifies overly permissive access
   - Detects unused permissions
   - Analyzes ownership chains

3. **Compliance Validation**
   - Validates against least privilege principle
   - Checks separation of duties
   - Identifies privileged access requirements
   - Validates data classification alignment

4. **Anomaly Detection**
   - Finds unusual permission patterns
   - Detects permissions drift
   - Identifies orphaned permissions
   - Flags recent permission changes

5. **Reporting**
   - Generates audit report with findings
   - Creates remediation recommendations
   - Exports permission matrix
   - Produces compliance evidence

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--catalog` | Specific catalog to audit | All catalogs |
| `--schema` | Specific schema to audit | All schemas |
| `--principal` | Filter by user/group | All principals |
| `--compliance-standard` | GDPR, HIPAA, SOC2, CCPA | None |
| `--check` | excessive-access, unused, orphaned | All checks |
| `--severity` | low, medium, high, critical | All |
| `--output-format` | json, csv, markdown, html | markdown |
| `--export-path` | Path to save audit report | ./governance-reports/ |

## Output Files

### Audit Report
```
governance-reports/
├── audit-summary-{timestamp}.md
├── permission-matrix-{timestamp}.csv
├── findings-{timestamp}.json
└── remediation-plan-{timestamp}.md
```

### Report Contents
- **Executive Summary**: High-level findings and risk score
- **Permission Matrix**: Complete grant mapping
- **Findings**: Detailed security issues
- **Remediation Steps**: Prioritized action items
- **Compliance Gaps**: Regulatory violations
- **Trend Analysis**: Permission changes over time

## Audit Checks

### 1. Excessive Permissions
- ALL PRIVILEGES on production catalogs
- MODIFY on sensitive tables by non-owners
- CREATE on catalogs by regular users
- Full table access without row filters

### 2. Privilege Escalation Risks
- OWNERSHIP transfer capabilities
- CREATE FUNCTION with elevated privileges
- External location access
- Storage credential access

### 3. Separation of Duties Violations
- Same user with conflicting roles
- Developers with production MODIFY
- Data consumers with transformation access
- Auditors with data modification rights

### 4. Orphaned Permissions
- Grants to deleted users
- Grants to deleted groups
- Permissions on deleted objects
- Dangling external references

### 5. Compliance Violations
- PII access without authorization
- PHI access without HIPAA compliance
- Production data access by contractors
- Cross-region data access restrictions

## Integration with MCP

This command uses the `governance-api` MCP server to:
- Query effective permissions
- Analyze grant inheritance
- Validate policy compliance
- Track permission changes

## Example Output

```markdown
# Unity Catalog Permission Audit Report
**Date**: 2026-01-02 14:30:00
**Scope**: catalog=production
**Compliance Standard**: GDPR

## Executive Summary
- **Total Objects Audited**: 1,247
- **Risk Score**: 7.2/10 (High)
- **Critical Findings**: 12
- **High Findings**: 34
- **Recommended Actions**: 46

## Critical Findings

### 1. Excessive ALL PRIVILEGES on Production Catalog
**Severity**: Critical
**Principal**: engineering_team
**Object**: production catalog
**Risk**: Unrestricted access to all production data
**Remediation**: Replace with specific grants (USE CATALOG, SELECT on specific schemas)

### 2. Direct MODIFY Access to PII Tables
**Severity**: Critical
**Principal**: analytics_users
**Object**: production.customers.pii_data
**Risk**: GDPR violation - unauthorized PII modification
**Remediation**: Remove MODIFY, implement row filters and masking functions

## Permission Matrix
| Principal | Catalog | Schema | Table | Privileges |
|-----------|---------|--------|-------|------------|
| data_engineers | production | * | * | ALL PRIVILEGES |
| analysts | production | analytics | * | SELECT |
| contractors | production | staging | raw_* | SELECT, MODIFY |
```

## Automated Remediation

The command can generate SQL scripts for remediation:

```sql
-- Remove excessive permissions
REVOKE ALL PRIVILEGES ON CATALOG production FROM `engineering_team`;

-- Grant least privilege access
GRANT USE CATALOG ON CATALOG production TO `engineering_team`;
GRANT USE SCHEMA ON SCHEMA production.bronze TO `engineering_team`;
GRANT SELECT, MODIFY ON SCHEMA production.bronze TO `engineering_team`;

-- Implement row filter for PII protection
CREATE FUNCTION production.pii_filter(user_role STRING)
RETURNS BOOLEAN
RETURN CASE
  WHEN IS_ACCOUNT_GROUP_MEMBER('pii_full_access') THEN TRUE
  WHEN user_role = 'PUBLIC' THEN FALSE
  ELSE TRUE
END;

ALTER TABLE production.customers.pii_data
SET ROW FILTER production.pii_filter(user_role);
```

## Best Practices

1. **Regular Audits**: Run weekly in production
2. **Baseline Comparison**: Track permission drift
3. **Change Justification**: Require approval for privilege escalation
4. **Least Privilege**: Grant minimum required permissions
5. **Time-bound Access**: Use temporary grants for contractors
6. **Audit Trail**: Maintain permission change history

## Related Commands
- `/databricks-governance:configure-access-control` - Set up proper access controls
- `/databricks-governance:generate-compliance-report` - Full compliance report
- `/databricks-governance:audit-data-access` - Analyze actual data access patterns

## Agent Collaboration

This command uses these specialized agents:
- `access-control-specialist` - Permission analysis
- `compliance-auditor` - Regulatory validation
- `audit-log-analyzer` - Change tracking
- `policy-enforcer` - Remediation planning
