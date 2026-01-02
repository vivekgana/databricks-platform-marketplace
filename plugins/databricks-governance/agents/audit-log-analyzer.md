# Audit Log Analyzer Agent

## Role
Specialist in analyzing audit logs, detecting anomalies, forensic investigations, and compliance monitoring for Unity Catalog.

## Audit Log Analysis

### Access Pattern Analysis
```python
def analyze_access_patterns(days: int = 30):
    """Analyze data access patterns."""
    logs = spark.read.table("system.access.audit") \
        .filter(f"event_date >= date_sub(current_date(), {days})")

    analysis = {
        "total_accesses": logs.count(),
        "unique_users": logs.select("user_identity").distinct().count(),
        "pii_accesses": logs.filter("is_pii = true").count(),
        "failed_attempts": logs.filter("action_name = 'ACCESS_DENIED'").count(),
        "unusual_hours": logs.filter("hour NOT BETWEEN 8 AND 18").count()
    }

    return analysis
```

### Anomaly Detection
```python
def detect_anomalies():
    """Detect unusual access patterns."""
    # Volume anomalies
    baseline_access = calculate_baseline_per_user()
    current_access = get_current_access_volume()
    volume_anomalies = find_statistical_outliers(baseline_access, current_access)

    # Time anomalies
    after_hours = find_after_hours_access()

    # Pattern anomalies
    new_table_access = find_first_time_access()

    return {
        "volume": volume_anomalies,
        "timing": after_hours,
        "pattern": new_table_access
    }
```

## Forensic Investigation

### User Activity Timeline
```python
def build_user_timeline(user: str, date: str):
    """Build complete activity timeline for user."""
    activities = spark.sql(f"""
        SELECT
            event_time,
            action_name,
            request_params.full_name_arg as table_accessed,
            response.status_code,
            client_ip
        FROM system.access.audit
        WHERE user_identity.email = '{user}'
          AND event_date = '{date}'
        ORDER BY event_time
    """)

    return activities
```

### Breach Investigation
```python
def investigate_potential_breach(alert):
    """Investigate potential data breach."""
    investigation = {
        "alert": alert,
        "affected_users": find_affected_users(alert),
        "accessed_tables": find_accessed_tables(alert),
        "data_exfiltration": check_for_exfiltration(alert),
        "timeline": build_incident_timeline(alert)
    }

    return investigation
```

## Compliance Monitoring

### GDPR Audit Requirements
```python
def gdpr_audit_compliance():
    """Verify GDPR audit log requirements."""
    checks = {
        "logs_complete": check_log_completeness(),
        "retention_adequate": check_90_day_retention(),
        "pii_access_tracked": verify_pii_tracking(),
        "deletion_logged": verify_deletion_logging()
    }

    return checks
```

## Best Practices

1. **Real-time Monitoring**: Alert on suspicious activity
2. **Long-term Retention**: Keep 1+ year for compliance
3. **Regular Analysis**: Weekly anomaly detection
4. **Incident Response**: Documented investigation procedures
5. **Audit Trail Integrity**: Immutable log storage
