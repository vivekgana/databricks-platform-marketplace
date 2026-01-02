# Configure Encryption Command

## Description
Set up encryption at rest and in transit, manage encryption keys, configure customer-managed keys (CMK), and implement encryption best practices for Unity Catalog.

## Usage
```bash
claude /databricks-governance:configure-encryption [options]
```

## Examples

```bash
# Audit encryption status
claude /databricks-governance:configure-encryption --audit

# Enable encryption for catalog
claude /databricks-governance:configure-encryption \
  --catalog production \
  --enable-cmk

# Setup key rotation
claude /databricks-governance:configure-encryption \
  --setup-key-rotation \
  --rotation-period 90days

# Validate encryption compliance
claude /databricks-governance:configure-encryption \
  --validate \
  --standard hipaa
```

## Encryption Types

### 1. Encryption at Rest
- Delta table data encrypted on storage
- Metadata encrypted in Unity Catalog
- Backup and archive encryption

### 2. Encryption in Transit
- TLS 1.2+ for all connections
- Encrypted notebook communication
- Secure data transfer between clusters

### 3. Customer-Managed Keys (CMK)
- Bring your own encryption keys
- Key rotation policies
- Key access auditing

## Implementation

```sql
-- Enable encryption for catalog
ALTER CATALOG production
SET ENCRYPTION (
  method = 'CUSTOMER_MANAGED',
  key_provider = 'AWS_KMS',
  key_id = 'arn:aws:kms:us-east-1:123456789012:key/abcd-1234'
);

-- Set encryption for table
CREATE TABLE production.sensitive_data (
  id BIGINT,
  data STRING
)
USING DELTA
TBLPROPERTIES (
  'delta.encryption.enabled' = 'true',
  'delta.encryption.keyId' = 'arn:aws:kms:us-east-1:123456789012:key/abcd-1234'
);
```

## Key Management

```python
def setup_key_rotation(catalog: str, rotation_days: int = 90):
    """Setup automatic key rotation."""
    # Schedule key rotation job
    rotation_schedule = f"0 0 */{rotation_days} * *"  # Cron format

    job_config = {
        "name": f"key_rotation_{catalog}",
        "schedule": rotation_schedule,
        "task": "rotate_encryption_keys",
        "parameters": {"catalog": catalog}
    }

    create_job(job_config)
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--audit` | Audit encryption status | False |
| `--catalog` | Target catalog | All |
| `--enable-cmk` | Enable customer-managed keys | False |
| `--setup-key-rotation` | Setup rotation | False |
| `--rotation-period` | Rotation period | 90days |
| `--validate` | Validate compliance | False |
| `--standard` | hipaa, pci, sox | None |

## Related Commands
- `/databricks-governance:setup-data-masking` - Data masking
- `/databricks-governance:generate-compliance-report` - Compliance validation
