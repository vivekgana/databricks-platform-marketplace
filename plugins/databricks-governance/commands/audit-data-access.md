# Audit Data Access Command

## Description
Analyze Unity Catalog audit logs for data access patterns, anomaly detection, compliance monitoring, and forensic investigations.

## Usage
```bash
claude /databricks-governance:audit-data-access [options]
```

## Examples

```bash
# Audit last 30 days of access
claude /databricks-governance:audit-data-access --days 30

# Detect anomalies
claude /databricks-governance:audit-data-access \
  --anomaly-detection \
  --sensitivity high

# User access review
claude /databricks-governance:audit-data-access \
  --user john.doe@company.com \
  --days 90

# PII access audit
claude /databricks-governance:audit-data-access \
  --pii-access-only \
  --export-report
```

## What It Does

1. **Access Pattern Analysis** - Who accessed what, when
2. **Anomaly Detection** - Unusual access patterns
3. **Compliance Monitoring** - Audit log completeness
4. **Forensic Investigation** - Detailed access trails
5. **Reporting** - Automated compliance reports

## Audit Log Analysis

```python
def analyze_audit_logs(days: int = 30):
    """Analyze Unity Catalog audit logs."""
    logs = spark.read.table("system.access.audit") \
        .filter(F.col("event_date") >= F.date_sub(F.current_date(), days))

    analysis = {
        "total_accesses": logs.count(),
        "unique_users": logs.select("user_identity").distinct().count(),
        "pii_accesses": logs.filter("is_pii = true").count(),
        "failed_accesses": logs.filter("action_name = 'ACCESS_DENIED'").count(),
        "after_hours": logs.filter("hour(event_time) NOT BETWEEN 8 AND 18").count()
    }

    return analysis
```

## Anomaly Detection

```python
def detect_anomalies(threshold: float = 3.0):
    """Detect anomalous access patterns."""
    # Volume anomalies
    daily_volume = calculate_daily_volume_per_user()
    volume_anomalies = detect_statistical_outliers(daily_volume, threshold)

    # Time anomalies
    unusual_hours = find_after_hours_access()

    # Access pattern anomalies
    new_table_access = find_first_time_table_access()

    return {
        "volume_anomalies": volume_anomalies,
        "unusual_hours": unusual_hours,
        "new_access_patterns": new_table_access
    }
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--days` | Days to analyze | 30 |
| `--user` | Specific user | All |
| `--table` | Specific table | All |
| `--anomaly-detection` | Detect anomalies | False |
| `--pii-access-only` | PII access only | False |
| `--export-report` | Export report | False |

## Related Commands
- `/databricks-governance:audit-permissions` - Permission audit
- `/databricks-governance:generate-compliance-report` - Compliance reporting
