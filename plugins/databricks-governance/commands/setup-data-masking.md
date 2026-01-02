# Setup Data Masking Command

## Description
Configure advanced column-level masking, dynamic data masking, encryption, and tokenization for PII and sensitive data protection in Unity Catalog.

## Usage
```bash
claude /databricks-governance:setup-data-masking [options]
```

## Examples

```bash
# Setup masking framework
claude /databricks-governance:setup-data-masking --init

# Mask specific column
claude /databricks-governance:setup-data-masking \
  --table production.customers.profiles \
  --column email \
  --masking-type conditional

# Bulk masking for catalog
claude /databricks-governance:setup-data-masking \
  --catalog production \
  --auto-mask-pii

# Test masking without applying
claude /databricks-governance:setup-data-masking \
  --table production.customers.profiles \
  --dry-run
```

## Masking Types

### 1. Full Redaction
- Completely hides sensitive data
- Returns fixed value (e.g., "REDACTED", NULL)
- Use for: SSN, passwords, secrets

### 2. Partial Masking
- Shows partial data (first/last characters)
- Example: "john.doe@email.com" → "joh***@email.com"
- Use for: emails, phone numbers, names

### 3. Tokenization
- Replaces with consistent token
- Preserves referential integrity
- Use for: credit cards, account numbers

### 4. Hashing
- One-way cryptographic hash
- Enables matching without revealing data
- Use for: analytics on sensitive fields

### 5. Conditional Masking
- Dynamic based on user role/group
- Different mask levels for different roles
- Use for: multi-level access requirements

## Masking Functions

```sql
-- Full redaction
CREATE FUNCTION governance.masks.full_redact(value STRING)
RETURNS STRING
RETURN 'REDACTED';

-- Conditional email masking
CREATE FUNCTION governance.masks.email_conditional(email STRING)
RETURNS STRING
RETURN CASE
  WHEN IS_ACCOUNT_GROUP_MEMBER('pii_full_access') THEN email
  WHEN IS_ACCOUNT_GROUP_MEMBER('pii_partial_access') THEN
    CONCAT(SUBSTRING(email, 1, 3), '***@', SPLIT(email, '@')[1])
  ELSE 'REDACTED'
END;

-- SSN masking
CREATE FUNCTION governance.masks.ssn_mask(ssn STRING)
RETURNS STRING
RETURN CASE
  WHEN IS_ACCOUNT_GROUP_MEMBER('hr_full_access') THEN ssn
  ELSE CONCAT('XXX-XX-', SUBSTRING(ssn, -4, 4))
END;

-- Credit card tokenization
CREATE FUNCTION governance.masks.cc_tokenize(cc STRING)
RETURNS STRING
RETURN CONCAT('****-****-****-', SUBSTRING(cc, -4, 4));

-- Hash for analytics
CREATE FUNCTION governance.masks.hash_for_analytics(value STRING)
RETURNS STRING
RETURN SHA2(CONCAT(value, 'secret_salt'), 256);
```

## Apply Masking

```sql
-- Apply to columns
ALTER TABLE production.customers.profiles
ALTER COLUMN email SET MASK governance.masks.email_conditional;

ALTER TABLE production.customers.profiles
ALTER COLUMN ssn SET MASK governance.masks.ssn_mask;

ALTER TABLE production.payment.transactions
ALTER COLUMN credit_card SET MASK governance.masks.cc_tokenize;
```

## Testing Masking

```python
def test_masking(table: str, column: str):
    """Test masking function across different user groups."""
    test_users = [
        ('admin_user', 'pii_full_access', 'Should see full value'),
        ('analyst_user', 'pii_partial_access', 'Should see partial value'),
        ('external_user', 'no_access', 'Should see REDACTED')
    ]

    for user, group, expectation in test_users:
        result = execute_as_user(
            f"SELECT {column} FROM {table} LIMIT 1",
            user=user
        )
        print(f"{user}: {result} - {expectation}")
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--init` | Initialize masking framework | False |
| `--table` | Target table | Required |
| `--column` | Specific column | All sensitive |
| `--masking-type` | full, partial, token, hash, conditional | conditional |
| `--catalog` | Bulk mask catalog | None |
| `--auto-mask-pii` | Auto-mask detected PII | False |
| `--dry-run` | Test without applying | False |

## Related Commands
- `/databricks-governance:scan-pii-data` - Detect PII
- `/databricks-governance:configure-access-control` - Row/column security
- `/databricks-governance:setup-data-classification` - Classification framework
