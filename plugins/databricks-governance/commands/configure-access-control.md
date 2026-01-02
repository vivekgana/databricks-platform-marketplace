# Configure Access Control Command

## Description
Set up comprehensive RBAC (Role-Based Access Control) and ABAC (Attribute-Based Access Control) policies with least privilege principles, separation of duties, and automated access reviews.

## Usage
```bash
claude /databricks-governance:configure-access-control [options]
```

## Examples

### Setup RBAC Framework
```bash
claude /databricks-governance:configure-access-control \
  --init-rbac \
  --catalog production
```

### Configure Row-Level Security
```bash
claude /databricks-governance:configure-access-control \
  --table production.customers.profiles \
  --row-filter region_based \
  --apply
```

### Setup Column Masking
```bash
claude /databricks-governance:configure-access-control \
  --table production.customers.profiles \
  --mask-column email \
  --masking-function conditional_redaction
```

### Implement Least Privilege
```bash
claude /databricks-governance:configure-access-control \
  --audit-mode \
  --enforce-least-privilege \
  --catalog production
```

## What It Does

1. **RBAC Configuration**
   - Defines standard roles (Reader, Writer, Admin, Data Steward)
   - Assigns privileges to roles
   - Maps users/groups to roles
   - Implements role hierarchies

2. **ABAC Implementation**
   - Creates attribute-based policies
   - Configures dynamic access controls
   - Implements context-aware permissions
   - Sets up conditional access

3. **Row-Level Security**
   - Creates row filter functions
   - Applies filters to sensitive tables
   - Implements multi-tenant isolation
   - Configures regional restrictions

4. **Column-Level Security**
   - Sets up masking functions
   - Applies column encryption
   - Configures dynamic data masking
   - Implements tokenization

5. **Access Reviews**
   - Schedules periodic reviews
   - Identifies unused permissions
   - Detects privilege creep
   - Automates access recertification

## RBAC Role Framework

### Standard Roles

```yaml
roles:
  data_reader:
    privileges:
      - USE CATALOG
      - USE SCHEMA
      - SELECT on tables
    description: "Read-only access to data"
    default_for: analysts, data_scientists

  data_writer:
    inherits: data_reader
    additional_privileges:
      - CREATE TABLE
      - MODIFY on owned tables
    description: "Write access for data engineers"
    default_for: data_engineers

  data_steward:
    inherits: data_writer
    additional_privileges:
      - ALTER on schema
      - GRANT/REVOKE privileges
      - APPLY TAG
    description: "Manage schema and metadata"
    default_for: data_stewards, data_owners

  data_admin:
    inherits: data_steward
    additional_privileges:
      - CREATE SCHEMA
      - OWNERSHIP transfer
      - ALL PRIVILEGES
    description: "Full administrative access"
    default_for: platform_admins
```

### Implementation SQL

```sql
-- Create governance schema for functions
CREATE SCHEMA IF NOT EXISTS governance.access_control;

-- Data Reader Setup
GRANT USE CATALOG ON CATALOG production TO `data_readers`;
GRANT USE SCHEMA ON SCHEMA production.* TO `data_readers`;
GRANT SELECT ON SCHEMA production.gold TO `data_readers`;
GRANT SELECT ON SCHEMA production.silver TO `data_readers`;

-- Data Writer Setup
GRANT USE CATALOG ON CATALOG production TO `data_writers`;
GRANT USE SCHEMA ON SCHEMA production.* TO `data_writers`;
GRANT SELECT, MODIFY ON SCHEMA production.bronze TO `data_writers`;
GRANT SELECT, MODIFY ON SCHEMA production.silver TO `data_writers`;
GRANT SELECT ON SCHEMA production.gold TO `data_writers`;

-- Data Steward Setup
GRANT USE CATALOG ON CATALOG production TO `data_stewards`;
GRANT ALL PRIVILEGES ON SCHEMA production.* TO `data_stewards`;

-- Data Admin Setup (minimal - use sparingly)
GRANT ALL PRIVILEGES ON CATALOG production TO `platform_admins`;
```

## Row-Level Security

### Example 1: Regional Access Control
```sql
-- Create row filter function
CREATE OR REPLACE FUNCTION governance.access_control.regional_filter()
RETURNS BOOLEAN
RETURN CASE
  WHEN IS_ACCOUNT_GROUP_MEMBER('global_access') THEN TRUE
  WHEN IS_ACCOUNT_GROUP_MEMBER('us_region') AND region = 'US' THEN TRUE
  WHEN IS_ACCOUNT_GROUP_MEMBER('eu_region') AND region = 'EU' THEN TRUE
  WHEN IS_ACCOUNT_GROUP_MEMBER('apac_region') AND region = 'APAC' THEN TRUE
  ELSE FALSE
END;

-- Apply row filter to table
ALTER TABLE production.customers.orders
SET ROW FILTER governance.access_control.regional_filter ON (region);
```

### Example 2: Multi-Tenant Isolation
```sql
-- Tenant-based row filter
CREATE OR REPLACE FUNCTION governance.access_control.tenant_filter(tenant_id STRING)
RETURNS BOOLEAN
RETURN CASE
  WHEN IS_ACCOUNT_GROUP_MEMBER('super_admin') THEN TRUE
  WHEN CURRENT_USER() LIKE CONCAT(tenant_id, '%') THEN TRUE
  WHEN IS_ACCOUNT_GROUP_MEMBER(CONCAT('tenant_', tenant_id)) THEN TRUE
  ELSE FALSE
END;

-- Apply to multi-tenant table
ALTER TABLE production.saas.customer_data
SET ROW FILTER governance.access_control.tenant_filter ON (tenant_id);
```

### Example 3: Time-Based Access
```sql
-- Business hours only access
CREATE OR REPLACE FUNCTION governance.access_control.business_hours_filter()
RETURNS BOOLEAN
RETURN CASE
  WHEN IS_ACCOUNT_GROUP_MEMBER('24x7_access') THEN TRUE
  WHEN HOUR(NOW()) BETWEEN 8 AND 18 THEN TRUE
  ELSE FALSE
END;

ALTER TABLE production.financial.transactions
SET ROW FILTER governance.access_control.business_hours_filter ON (*);
```

## Column-Level Security

### Example 1: Conditional Masking
```sql
-- Create masking function
CREATE OR REPLACE FUNCTION governance.access_control.mask_email(email STRING)
RETURNS STRING
RETURN CASE
  WHEN IS_ACCOUNT_GROUP_MEMBER('pii_full_access') THEN email
  WHEN IS_ACCOUNT_GROUP_MEMBER('pii_partial_access') THEN
    CONCAT(SUBSTRING(email, 1, 3), '***@', SPLIT(email, '@')[1])
  ELSE 'REDACTED'
END;

-- Apply masking to column
ALTER TABLE production.customers.profiles
ALTER COLUMN email SET MASK governance.access_control.mask_email;
```

### Example 2: SSN Masking
```sql
-- SSN masking function
CREATE OR REPLACE FUNCTION governance.access_control.mask_ssn(ssn STRING)
RETURNS STRING
RETURN CASE
  WHEN IS_ACCOUNT_GROUP_MEMBER('hr_full_access') THEN ssn
  WHEN IS_ACCOUNT_GROUP_MEMBER('hr_partial_access') THEN
    CONCAT('XXX-XX-', SUBSTRING(ssn, -4, 4))
  ELSE 'XXX-XX-XXXX'
END;

ALTER TABLE production.hr.employees
ALTER COLUMN ssn SET MASK governance.access_control.mask_ssn;
```

### Example 3: Salary Banding
```sql
-- Salary banding for privacy
CREATE OR REPLACE FUNCTION governance.access_control.mask_salary(salary DECIMAL(10,2))
RETURNS STRING
RETURN CASE
  WHEN IS_ACCOUNT_GROUP_MEMBER('finance_team') THEN CAST(salary AS STRING)
  WHEN salary < 50000 THEN '< 50K'
  WHEN salary < 100000 THEN '50K-100K'
  WHEN salary < 150000 THEN '100K-150K'
  WHEN salary < 200000 THEN '150K-200K'
  ELSE '200K+'
END;

ALTER TABLE production.hr.employees
ALTER COLUMN salary SET MASK governance.access_control.mask_salary;
```

## ABAC Policies

### Attribute-Based Access Control
```python
from databricks.sdk import WorkspaceClient

class ABACPolicyEngine:
    def __init__(self):
        self.w = WorkspaceClient()

    def create_abac_policy(
        self,
        resource: str,
        attributes: Dict[str, Any],
        conditions: List[Dict]
    ):
        """Create attribute-based access policy."""
        policy = {
            "resource": resource,
            "attributes": attributes,
            "conditions": conditions,
            "effect": "allow"
        }

        # Example: Grant access based on user attributes
        # - Department matches resource owner
        # - User has required clearance level
        # - Request time is during business hours

        policy_sql = self._generate_policy_sql(policy)
        self._apply_policy(policy_sql)

    def _generate_policy_sql(self, policy: Dict) -> str:
        """Generate SQL for ABAC policy."""
        conditions = []

        for condition in policy["conditions"]:
            if condition["type"] == "department_match":
                conditions.append(
                    "IS_ACCOUNT_GROUP_MEMBER(CONCAT('dept_', department))"
                )
            elif condition["type"] == "clearance_level":
                conditions.append(
                    f"clearance_level >= {condition['minimum']}"
                )

        condition_str = " AND ".join(conditions)

        return f"""
        CREATE OR REPLACE FUNCTION abac_filter_{policy['resource']}_filter()
        RETURNS BOOLEAN
        RETURN {condition_str};
        """
```

## Least Privilege Enforcement

### Audit and Remediation
```python
def enforce_least_privilege(catalog: str):
    """Remove excessive permissions and enforce least privilege."""
    # Find overly permissive grants
    excessive_grants = find_excessive_grants(catalog)

    for grant in excessive_grants:
        # Replace ALL PRIVILEGES with specific grants
        if grant["privilege"] == "ALL PRIVILEGES":
            remove_excessive_grant(grant)
            apply_minimal_grants(grant["principal"], grant["resource"])

        # Remove MODIFY from read-only users
        if grant["privilege"] == "MODIFY" and grant["principal"] in readonly_groups:
            revoke_grant(grant)

        # Remove ownership from non-owners
        if grant["privilege"] == "OWN" and grant["principal"] != resource_owner:
            transfer_ownership(grant["resource"], resource_owner)
```

## Access Reviews

### Automated Access Review
```python
def schedule_access_review(catalog: str, frequency: str = "quarterly"):
    """Schedule periodic access reviews."""
    review_tasks = {
        "unused_permissions": find_unused_permissions(catalog),
        "excessive_access": find_excessive_access(catalog),
        "stale_accounts": find_stale_accounts(catalog),
        "privilege_creep": detect_privilege_creep(catalog)
    }

    # Generate review report
    report = generate_review_report(review_tasks)

    # Send to data stewards for approval
    send_for_review(report, data_stewards)

    return report
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--init-rbac` | Initialize RBAC framework | False |
| `--catalog` | Target catalog | Required |
| `--table` | Specific table | All tables |
| `--row-filter` | Row filter type | None |
| `--mask-column` | Column to mask | None |
| `--masking-function` | Masking function name | Default |
| `--audit-mode` | Preview without applying | False |
| `--enforce-least-privilege` | Remove excessive permissions | False |
| `--export-policies` | Export policy definitions | False |

## Best Practices

1. **Least Privilege**: Grant minimum required permissions
2. **Separation of Duties**: No single user has complete control
3. **Regular Reviews**: Quarterly access recertification
4. **Audit Trail**: Log all permission changes
5. **Time-Bound Access**: Temporary grants for contractors
6. **Defense in Depth**: Multiple layers of security

## Related Commands
- `/databricks-governance:audit-permissions` - Permission auditing
- `/databricks-governance:setup-data-masking` - Advanced masking
- `/databricks-governance:generate-compliance-report` - Compliance validation

## Agent Collaboration
- `access-control-specialist` - RBAC/ABAC design
- `data-privacy-guardian` - Privacy requirements
- `compliance-auditor` - Regulatory compliance
- `policy-enforcer` - Policy automation
