# Monitor Data Product Command

## Description
Set up comprehensive monitoring, alerting, and SLA tracking for data products. Provides real-time visibility into data quality, freshness, performance, and consumer usage.

## Usage
```bash
/databricks-engineering:monitor-data-product [product-name] [--create-dashboards] [--enable-alerts]
```

## Parameters

- `product-name` (required): Name of data product to monitor
- `--create-dashboards` (optional): Create monitoring dashboards (default: true)
- `--enable-alerts` (optional): Set up alerting (default: true)
- `--sla-tracking` (optional): Enable SLA compliance tracking (default: true)
- `--anomaly-detection` (optional): Enable anomaly detection (default: true)

## Examples

### Example 1: Set up complete monitoring
```bash
/databricks-engineering:monitor-data-product customer-360 \
  --create-dashboards \
  --enable-alerts \
  --sla-tracking
```

### Example 2: Dashboards only
```bash
/databricks-engineering:monitor-data-product customer-360 \
  --create-dashboards \
  --enable-alerts false
```

## What This Command Does

### Phase 1: Dashboard Creation (15 minutes)
- Creates SLA tracking dashboard
- Generates quality metrics dashboard
- Builds usage analytics dashboard
- Creates performance monitoring dashboard
- Sets up cost tracking dashboard

### Phase 2: Alert Configuration (10 minutes)
- Configures freshness alerts
- Sets up quality degradation alerts
- Creates performance alerts
- Configures SLA breach alerts
- Sets up anomaly detection alerts

### Phase 3: SLA Tracking Setup (5 minutes)
- Configures SLA measurement queries
- Sets up automated SLA reports
- Creates compliance tracking
- Configures escalation workflows

## Generated Monitoring Assets

### SLA Tracking Dashboard
```sql
-- dashboards/customer-360-sla-tracking.sql

-- Freshness SLA
CREATE OR REPLACE VIEW monitoring.customer_360_freshness AS
SELECT
  table_name,
  MAX(updated_at) as last_update,
  TIMESTAMPDIFF(HOUR, MAX(updated_at), CURRENT_TIMESTAMP()) as age_hours,
  CASE
    WHEN TIMESTAMPDIFF(HOUR, MAX(updated_at), CURRENT_TIMESTAMP()) <= 4 THEN 'Met'
    WHEN TIMESTAMPDIFF(HOUR, MAX(updated_at), CURRENT_TIMESTAMP()) <= 6 THEN 'Warning'
    ELSE 'Breached'
  END as sla_status,
  4 as target_hours
FROM main_production.customer_360.customers
GROUP BY table_name;

-- Quality SLA
CREATE OR REPLACE VIEW monitoring.customer_360_quality AS
SELECT
  check_date,
  table_name,
  quality_score,
  CASE
    WHEN quality_score >= 99.5 THEN 'Met'
    WHEN quality_score >= 98.0 THEN 'Warning'
    ELSE 'Breached'
  END as sla_status,
  99.5 as target_score
FROM monitoring.quality_metrics
WHERE product_name = 'customer-360'
  AND check_date >= CURRENT_DATE - INTERVAL 7 DAYS;

-- Performance SLA
CREATE OR REPLACE VIEW monitoring.customer_360_performance AS
SELECT
  query_type,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time_ms) as p95_latency_ms,
  CASE
    WHEN query_type = 'simple' AND PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time_ms) <= 1000 THEN 'Met'
    WHEN query_type = 'aggregation' AND PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time_ms) <= 5000 THEN 'Met'
    ELSE 'Breached'
  END as sla_status
FROM system.query.history
WHERE database_name = 'customer_360'
  AND query_start_time >= CURRENT_TIMESTAMP - INTERVAL 24 HOURS
GROUP BY query_type;

-- Overall SLA Summary
CREATE OR REPLACE VIEW monitoring.customer_360_sla_summary AS
SELECT
  'customer-360' as product_name,
  CURRENT_DATE as report_date,
  (SELECT COUNT(*) FROM monitoring.customer_360_freshness WHERE sla_status = 'Met') /
    (SELECT COUNT(*) FROM monitoring.customer_360_freshness) * 100 as freshness_compliance_pct,
  (SELECT AVG(quality_score) FROM monitoring.customer_360_quality) as avg_quality_score,
  (SELECT COUNT(*) FROM monitoring.customer_360_performance WHERE sla_status = 'Met') /
    (SELECT COUNT(*) FROM monitoring.customer_360_performance) * 100 as performance_compliance_pct;
```

### Quality Metrics Dashboard
```sql
-- Data quality trends
CREATE OR REPLACE VIEW monitoring.customer_360_quality_trends AS
SELECT
  check_date,
  AVG(quality_score) as avg_quality,
  AVG(completeness_score) as avg_completeness,
  AVG(accuracy_score) as avg_accuracy,
  AVG(consistency_score) as avg_consistency,
  SUM(failed_records) as total_failures
FROM monitoring.quality_metrics
WHERE product_name = 'customer-360'
  AND check_date >= CURRENT_DATE - INTERVAL 90 DAYS
GROUP BY check_date
ORDER BY check_date;

-- Quality by table
CREATE OR REPLACE VIEW monitoring.customer_360_quality_by_table AS
SELECT
  table_name,
  AVG(quality_score) as avg_quality,
  MIN(quality_score) as min_quality,
  MAX(quality_score) as max_quality,
  STDDEV(quality_score) as quality_stddev
FROM monitoring.quality_metrics
WHERE product_name = 'customer-360'
  AND check_date >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY table_name;
```

### Usage Analytics Dashboard
```sql
-- Consumer usage statistics
CREATE OR REPLACE VIEW monitoring.customer_360_usage_stats AS
SELECT
  consumer_name,
  DATE(query_time) as usage_date,
  COUNT(DISTINCT query_id) as total_queries,
  SUM(bytes_scanned) / POW(1024, 3) as gb_scanned,
  AVG(execution_time_ms) / 1000 as avg_execution_sec,
  COUNT(DISTINCT table_name) as tables_accessed
FROM data_products.usage_logs
WHERE product_name = 'customer-360'
  AND query_time >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY consumer_name, DATE(query_time);

-- Query pattern analysis
CREATE OR REPLACE VIEW monitoring.customer_360_query_patterns AS
SELECT
  DATE_TRUNC('hour', query_time) as hour,
  COUNT(*) as query_count,
  AVG(execution_time_ms) as avg_time_ms,
  SUM(bytes_scanned) / POW(1024, 3) as gb_scanned
FROM data_products.usage_logs
WHERE product_name = 'customer-360'
  AND query_time >= CURRENT_TIMESTAMP - INTERVAL 7 DAYS
GROUP BY DATE_TRUNC('hour', query_time)
ORDER BY hour;

-- Popular tables
CREATE OR REPLACE VIEW monitoring.customer_360_popular_tables AS
SELECT
  table_name,
  COUNT(DISTINCT consumer_name) as unique_consumers,
  COUNT(*) as total_queries,
  AVG(execution_time_ms) as avg_time_ms
FROM data_products.usage_logs
WHERE product_name = 'customer-360'
  AND query_time >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY table_name
ORDER BY total_queries DESC;
```

### Alert Configuration
```yaml
# monitoring/customer-360-alerts.yaml

alerts:
  # Freshness SLA breach
  - name: customer-360-freshness-breach
    description: Data freshness exceeds SLA threshold
    query: |
      SELECT table_name, age_hours
      FROM monitoring.customer_360_freshness
      WHERE sla_status = 'Breached'
    severity: critical
    frequency: every_30_minutes
    notifications:
      - type: email
        recipients:
          - data-engineering@company.com
          - data-platform-oncall@company.com
      - type: slack
        channel: "#data-alerts"
      - type: pagerduty
        service_key: "${PAGERDUTY_SERVICE_KEY}"

  # Quality degradation
  - name: customer-360-quality-degradation
    description: Data quality score below threshold
    query: |
      SELECT table_name, quality_score
      FROM monitoring.customer_360_quality
      WHERE check_date = CURRENT_DATE
        AND quality_score < 98.0
    severity: high
    frequency: hourly
    notifications:
      - type: email
        recipients:
          - data-engineering@company.com
      - type: slack
        channel: "#data-quality"

  # Performance degradation
  - name: customer-360-performance-issue
    description: Query performance exceeding SLA
    query: |
      SELECT query_type, p95_latency_ms
      FROM monitoring.customer_360_performance
      WHERE sla_status = 'Breached'
    severity: medium
    frequency: every_15_minutes
    notifications:
      - type: slack
        channel: "#data-performance"

  # Unusual access pattern
  - name: customer-360-unusual-access
    description: Abnormal query volume detected
    query: |
      SELECT
        consumer_name,
        COUNT(*) as query_count
      FROM data_products.usage_logs
      WHERE product_name = 'customer-360'
        AND query_time >= CURRENT_TIMESTAMP - INTERVAL 1 HOUR
      GROUP BY consumer_name
      HAVING query_count > 1000
    severity: medium
    frequency: hourly
    notifications:
      - type: email
        recipients:
          - security@company.com

  # Data volume anomaly
  - name: customer-360-volume-anomaly
    description: Unexpected change in data volume
    query: |
      WITH daily_counts AS (
        SELECT
          DATE(updated_at) as date,
          COUNT(*) as row_count
        FROM main_production.customer_360.customers
        WHERE updated_at >= CURRENT_DATE - INTERVAL 7 DAYS
        GROUP BY DATE(updated_at)
      )
      SELECT
        date,
        row_count,
        AVG(row_count) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) as avg_prev_7days
      FROM daily_counts
      WHERE ABS(row_count - AVG(row_count) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING)) >
            2 * STDDEV(row_count) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING)
    severity: medium
    frequency: daily
    notifications:
      - type: slack
        channel: "#data-quality"
```

### Anomaly Detection
```python
# monitoring/anomaly_detection.py
import pandas as pd
from databricks.sdk import WorkspaceClient
from sklearn.ensemble import IsolationForest
import logging

logger = logging.getLogger(__name__)


class DataProductAnomalyDetector:
    """Detect anomalies in data product metrics"""

    def __init__(self, workspace_url: str, token: str):
        self.client = WorkspaceClient(host=workspace_url, token=token)

    def detect_quality_anomalies(
        self,
        product_name: str,
        lookback_days: int = 30
    ) -> list:
        """Detect quality score anomalies"""
        # Fetch quality metrics
        query = f"""
            SELECT
                check_date,
                quality_score,
                completeness_score,
                accuracy_score
            FROM monitoring.quality_metrics
            WHERE product_name = '{product_name}'
              AND check_date >= CURRENT_DATE - INTERVAL {lookback_days} DAYS
            ORDER BY check_date
        """
        df = pd.read_sql(query, self.client.get_sql_connection())

        # Prepare features
        features = df[['quality_score', 'completeness_score', 'accuracy_score']]

        # Train isolation forest
        model = IsolationForest(contamination=0.1, random_state=42)
        predictions = model.fit_predict(features)

        # Identify anomalies
        anomalies = df[predictions == -1]

        logger.info(f"Detected {len(anomalies)} quality anomalies")

        return anomalies.to_dict('records')

    def detect_usage_anomalies(
        self,
        product_name: str,
        lookback_days: int = 7
    ) -> list:
        """Detect usage pattern anomalies"""
        query = f"""
            SELECT
                DATE(query_time) as date,
                COUNT(*) as query_count,
                SUM(bytes_scanned) / POW(1024, 3) as gb_scanned,
                COUNT(DISTINCT consumer_name) as unique_consumers
            FROM data_products.usage_logs
            WHERE product_name = '{product_name}'
              AND query_time >= CURRENT_DATE - INTERVAL {lookback_days} DAYS
            GROUP BY DATE(query_time)
        """
        df = pd.read_sql(query, self.client.get_sql_connection())

        # Detect anomalies using Z-score
        for col in ['query_count', 'gb_scanned', 'unique_consumers']:
            mean = df[col].mean()
            std = df[col].std()
            df[f'{col}_zscore'] = (df[col] - mean) / std

        # Flag anomalies (|z-score| > 3)
        anomaly_threshold = 3
        anomalies = df[
            (abs(df['query_count_zscore']) > anomaly_threshold) |
            (abs(df['gb_scanned_zscore']) > anomaly_threshold) |
            (abs(df['unique_consumers_zscore']) > anomaly_threshold)
        ]

        logger.info(f"Detected {len(anomalies)} usage anomalies")

        return anomalies.to_dict('records')

    def detect_freshness_anomalies(
        self,
        product_name: str
    ) -> list:
        """Detect data freshness issues"""
        query = f"""
            SELECT
                table_name,
                MAX(updated_at) as last_update,
                TIMESTAMPDIFF(HOUR, MAX(updated_at), CURRENT_TIMESTAMP()) as age_hours
            FROM main_production.customer_360.customers
            GROUP BY table_name
            HAVING age_hours > 6
        """
        anomalies = self.client.sql_exec(query).fetchall()

        logger.info(f"Detected {len(anomalies)} freshness anomalies")

        return anomalies
```

### SLA Compliance Report
```python
# monitoring/sla_report.py
from datetime import datetime, timedelta
from databricks.sdk import WorkspaceClient


def generate_sla_report(product_name: str, period_days: int = 30):
    """Generate comprehensive SLA compliance report"""
    client = WorkspaceClient()

    # Freshness compliance
    freshness_query = f"""
        SELECT
            DATE(check_time) as date,
            COUNT(*) as total_checks,
            SUM(CASE WHEN age_hours <= 4 THEN 1 ELSE 0 END) as met_sla,
            SUM(CASE WHEN age_hours <= 4 THEN 1 ELSE 0 END) / COUNT(*) * 100 as compliance_pct
        FROM monitoring.freshness_checks
        WHERE product_name = '{product_name}'
          AND check_time >= CURRENT_DATE - INTERVAL {period_days} DAYS
        GROUP BY DATE(check_time)
    """

    # Quality compliance
    quality_query = f"""
        SELECT
            check_date as date,
            AVG(quality_score) as avg_quality,
            SUM(CASE WHEN quality_score >= 99.5 THEN 1 ELSE 0 END) / COUNT(*) * 100 as compliance_pct
        FROM monitoring.quality_metrics
        WHERE product_name = '{product_name}'
          AND check_date >= CURRENT_DATE - INTERVAL {period_days} DAYS
        GROUP BY check_date
    """

    freshness_results = client.sql_exec(freshness_query).fetchall()
    quality_results = client.sql_exec(quality_query).fetchall()

    # Calculate overall compliance
    overall_freshness = sum(r['compliance_pct'] for r in freshness_results) / len(freshness_results)
    overall_quality = sum(r['compliance_pct'] for r in quality_results) / len(quality_results)

    report = {
        "product_name": product_name,
        "report_period": f"{period_days} days",
        "generated_at": datetime.now().isoformat(),
        "sla_compliance": {
            "freshness": {
                "target": "< 4 hours",
                "compliance_pct": round(overall_freshness, 2),
                "status": "Met" if overall_freshness >= 99.0 else "Breached"
            },
            "quality": {
                "target": "> 99.5%",
                "compliance_pct": round(overall_quality, 2),
                "status": "Met" if overall_quality >= 99.0 else "Breached"
            }
        },
        "details": {
            "freshness_by_day": freshness_results,
            "quality_by_day": quality_results
        }
    }

    return report
```

## Best Practices

1. **Proactive Monitoring**: Monitor metrics before SLA breaches
2. **Actionable Alerts**: Alert only on actionable issues
3. **Alert Fatigue**: Tune thresholds to minimize false positives
4. **Escalation**: Define clear escalation paths
5. **Documentation**: Document alert runbooks
6. **Regular Review**: Review and update monitoring quarterly
7. **Automation**: Automate remediation where possible
8. **Dashboards**: Keep dashboards simple and focused

## Troubleshooting

**Issue**: Dashboards not updating
**Solution**: Verify materialized views refreshing, check data pipeline, validate permissions

**Issue**: Alerts not firing
**Solution**: Check alert configuration, verify notification channels, test alert queries

**Issue**: SLA compliance calculation incorrect
**Solution**: Review SLA definition, validate measurement queries, check time zones

## Related Commands

- `/databricks-engineering:create-data-product` - Create data product
- `/databricks-engineering:publish-data-product` - Publish product
- `/databricks-engineering:manage-consumers` - Manage consumers
- `/databricks-engineering:deploy-workflow` - Deploy pipeline

---

**Last Updated**: 2024-12-31
**Version**: 1.0.0
**Category**: Monitoring
**Prepared by**: gekambaram
