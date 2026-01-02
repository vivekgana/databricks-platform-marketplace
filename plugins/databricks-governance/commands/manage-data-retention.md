# Manage Data Retention Command

## Description
Configure and enforce data retention policies, lifecycle management, automated archival, and deletion workflows aligned with regulatory requirements and business needs.

## Usage
```bash
claude /databricks-governance:manage-data-retention [options]
```

## Examples

```bash
# Setup retention framework
claude /databricks-governance:manage-data-retention --init

# Set retention policy
claude /databricks-governance:manage-data-retention \
  --table production.orders \
  --retention-period 7years \
  --policy financial

# Audit retention compliance
claude /databricks-governance:manage-data-retention \
  --audit \
  --catalog production

# Execute retention cleanup
claude /databricks-governance:manage-data-retention \
  --execute-cleanup \
  --dry-run
```

## Retention Policies

```yaml
retention_policies:
  financial:
    period: 7_years
    justification: "SOX, tax regulations"
    archive_after: 2_years
    delete_after: 7_years

  customer_data:
    period: 5_years
    justification: "GDPR, business need"
    archive_after: 1_year
    delete_after: 5_years

  operational_logs:
    period: 90_days
    justification: "Operational monitoring"
    archive_after: 30_days
    delete_after: 90_days

  pii_data:
    period: depends_on_consent
    justification: "GDPR Article 5(e)"
    review_frequency: quarterly
    delete_on_request: immediate
```

## Implementation

### Set Retention Properties
```sql
-- Set retention policy on table
ALTER TABLE production.orders
SET TBLPROPERTIES (
  'retention.policy' = 'financial',
  'retention.period' = '7years',
  'retention.archive_date' = '2years',
  'retention.delete_date' = '7years',
  'retention.timestamp_column' = 'order_date'
);

-- Create retention tracking
CREATE TABLE IF NOT EXISTS governance.retention_tracking (
  table_name STRING,
  retention_policy STRING,
  last_cleanup_date TIMESTAMP,
  records_archived BIGINT,
  records_deleted BIGINT,
  next_cleanup_date TIMESTAMP
);
```

### Automated Cleanup Job
```python
from datetime import datetime, timedelta
from pyspark.sql import functions as F

def execute_retention_cleanup(table_name: str, dry_run: bool = True):
    """Execute retention policy cleanup."""
    # Get table properties
    props = spark.sql(f"SHOW TBLPROPERTIES {table_name}").collect()
    retention_days = int(props['retention.period'].replace('years', '')) * 365
    timestamp_col = props['retention.timestamp_column']

    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=retention_days)

    # Find records to delete
    df = spark.table(table_name)
    to_delete = df.filter(F.col(timestamp_col) < cutoff_date)

    record_count = to_delete.count()

    if dry_run:
        print(f"DRY RUN: Would delete {record_count} records from {table_name}")
        return

    # Archive before delete (optional)
    archive_table = f"{table_name}_archive"
    to_delete.write.mode("append").saveAsTable(archive_table)

    # Delete from main table
    spark.sql(f"""
        DELETE FROM {table_name}
        WHERE {timestamp_col} < '{cutoff_date}'
    """)

    # Log cleanup
    log_retention_cleanup(table_name, record_count)
```

## GDPR Right to Erasure

```python
def process_deletion_request(subject_id: str):
    """Process GDPR data subject deletion request."""
    # Find all tables with subject's data
    tables_with_data = find_tables_with_subject(subject_id)

    deletion_report = []

    for table in tables_with_data:
        # Delete from each table
        rows_deleted = spark.sql(f"""
            DELETE FROM {table}
            WHERE customer_id = '{subject_id}'
        """).collect()[0]['num_affected_rows']

        deletion_report.append({
            'table': table,
            'rows_deleted': rows_deleted,
            'timestamp': datetime.now()
        })

    # Log deletion for audit trail
    log_gdpr_deletion(subject_id, deletion_report)

    return deletion_report
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--init` | Initialize retention framework | False |
| `--table` | Target table | All |
| `--catalog` | Catalog scope | All |
| `--retention-period` | Period (e.g., 7years, 90days) | Required |
| `--policy` | Policy name | custom |
| `--audit` | Audit compliance | False |
| `--execute-cleanup` | Run cleanup | False |
| `--dry-run` | Preview only | True |

## Related Commands
- `/databricks-governance:generate-compliance-report` - Retention compliance
- `/databricks-governance:enforce-data-lineage` - Deletion cascades
