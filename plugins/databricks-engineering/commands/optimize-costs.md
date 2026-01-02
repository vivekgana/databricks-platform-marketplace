# Optimize Costs Command

## Description
Analyze and optimize Databricks cluster configurations, job schedules, storage patterns, and compute usage to reduce cloud costs while maintaining performance SLAs. This command provides actionable recommendations with estimated savings and implementation plans.

## Usage
```bash
/databricks-engineering:optimize-costs [scope] [--target-reduction percentage] [--analyze-period days]
```

## Parameters

- `scope` (optional): Analysis scope - "workspace", "pipeline", "job", "cluster", or "all" (default: "all")
- `--target-reduction` (optional): Target cost reduction percentage (default: 20)
- `--analyze-period` (optional): Historical analysis period in days (default: 30)
- `--include-storage` (optional): Include storage optimization analysis (default: true)
- `--output` (optional): Output format - "markdown", "json", "csv" (default: "markdown")
- `--apply` (optional): Automatically apply safe optimizations (default: false)

## Examples

### Example 1: Comprehensive workspace optimization
```bash
/databricks-engineering:optimize-costs all --target-reduction 25 --analyze-period 90
```

### Example 2: Pipeline-specific optimization
```bash
/databricks-engineering:optimize-costs pipeline --pipeline customer-360
```

### Example 3: Cluster right-sizing
```bash
/databricks-engineering:optimize-costs cluster --cluster-id 1234-567890-abc123
```

### Example 4: Storage optimization only
```bash
/databricks-engineering:optimize-costs storage --include-compute false
```

### Example 5: Apply safe optimizations automatically
```bash
/databricks-engineering:optimize-costs all --apply --target-reduction 15
```

## What This Command Does

### Phase 1: Data Collection (5-10 minutes)
1. **Cluster Usage Analysis**
   - Retrieves cluster configurations and usage metrics
   - Analyzes CPU, memory, and I/O utilization
   - Identifies idle and underutilized clusters
   - Reviews autoscaling configurations
   - Examines spot instance usage

2. **Job Execution Analysis**
   - Collects job run history and execution times
   - Analyzes job scheduling patterns
   - Identifies job failures and retries
   - Reviews resource allocation per job
   - Examines concurrent job execution

3. **Storage Analysis**
   - Scans Delta table statistics
   - Analyzes file sizes and small file problems
   - Reviews table partitioning strategies
   - Identifies duplicate and unused tables
   - Examines data retention policies

4. **DBU Consumption Analysis**
   - Retrieves DBU usage by workspace, cluster, and job
   - Calculates cost per pipeline and job
   - Identifies top cost drivers
   - Analyzes DBU usage trends
   - Reviews premium tier usage

### Phase 2: Optimization Analysis (10-15 minutes)

#### Compute Optimizations
1. **Cluster Right-Sizing**
   - Analyzes resource utilization patterns
   - Recommends optimal instance types
   - Suggests memory and CPU configurations
   - Identifies over-provisioned clusters
   - Calculates potential savings

2. **Autoscaling Tuning**
   - Reviews current autoscaling settings
   - Recommends optimal min/max workers
   - Suggests scale-down timeout adjustments
   - Analyzes workload patterns for better scaling
   - Estimates savings from improved autoscaling

3. **Spot Instance Adoption**
   - Identifies fault-tolerant workloads
   - Recommends spot instance usage
   - Calculates spot savings (60-80%)
   - Provides fallback strategies
   - Assesses risk levels

4. **Pool Optimization**
   - Analyzes pool utilization
   - Recommends pool sizing
   - Identifies unnecessary pools
   - Suggests pool consolidation
   - Calculates idle time costs

#### Job Scheduling Optimizations
1. **Schedule Optimization**
   - Identifies overlapping job runs
   - Suggests off-peak scheduling
   - Recommends job consolidation
   - Analyzes dependency chains
   - Proposes parallel execution strategies

2. **Job Clustering**
   - Groups similar workloads
   - Recommends shared cluster usage
   - Identifies single-job clusters
   - Suggests job cluster configurations
   - Calculates cluster reuse savings

3. **Timeout and Retry Optimization**
   - Reviews timeout configurations
   - Analyzes retry patterns
   - Identifies infinite retry loops
   - Recommends optimal timeout values
   - Reduces wasted compute on failures

#### Storage Optimizations
1. **Table Optimization**
   - Identifies tables needing OPTIMIZE
   - Recommends Z-ORDER columns
   - Suggests VACUUM schedules
   - Analyzes small file problems
   - Calculates query performance improvements

2. **Partitioning Strategy**
   - Reviews current partitioning
   - Recommends optimal partition columns
   - Identifies over-partitioned tables
   - Suggests partition consolidation
   - Estimates query cost reductions

3. **Data Lifecycle Management**
   - Identifies unused tables
   - Recommends archival strategies
   - Suggests table expiration policies
   - Analyzes data freshness requirements
   - Calculates storage savings

4. **Compression and File Formats**
   - Reviews file formats (Parquet vs Delta)
   - Recommends compression algorithms
   - Identifies uncompressed data
   - Suggests format conversions
   - Estimates storage cost reduction

### Phase 3: Report Generation (2-5 minutes)

Generates comprehensive optimization report with:

1. **Executive Summary**
   - Current monthly spend
   - Projected savings
   - Top 10 optimization opportunities
   - Risk assessment
   - Implementation timeline

2. **Detailed Findings**
   - Category-wise analysis
   - Resource-specific recommendations
   - Cost-benefit analysis
   - Implementation complexity
   - Expected ROI

3. **Implementation Plan**
   - Prioritized action items
   - Step-by-step instructions
   - Code snippets and configurations
   - Rollback procedures
   - Success metrics

## Output Structure

### Cost Optimization Report
```markdown
# Cost Optimization Report
**Workspace**: production-workspace
**Analysis Period**: Last 90 days
**Generated**: 2024-12-31T10:30:00Z
**Current Monthly Cost**: $45,000
**Potential Monthly Savings**: $11,250 (25%)

## Executive Summary

### Top Opportunities
1. **Cluster Right-Sizing** - Save $4,500/month (10% reduction)
2. **Spot Instance Adoption** - Save $3,600/month (8% reduction)
3. **Storage Optimization** - Save $1,800/month (4% reduction)
4. **Job Schedule Optimization** - Save $1,350/month (3% reduction)

### Risk Assessment
- **High Impact, Low Risk**: $7,200/month in savings
- **High Impact, Medium Risk**: $3,150/month in savings
- **Medium Impact, Low Risk**: $900/month in savings

### Implementation Timeline
- **Week 1**: Quick wins ($3,000 savings)
- **Week 2-4**: Medium complexity ($5,250 savings)
- **Month 2-3**: High complexity ($3,000 savings)

## Detailed Analysis

### 1. Compute Optimizations

#### 1.1 Over-Provisioned Clusters
**Finding**: 12 clusters running with <30% average CPU utilization

**Clusters Identified**:
| Cluster ID | Current Config | Avg CPU | Recommendation | Monthly Savings |
|------------|----------------|---------|----------------|-----------------|
| data-etl-01 | i3.4xlarge x8 | 22% | i3.2xlarge x4 | $1,200 |
| analytics-prod | i3.8xlarge x10 | 18% | i3.4xlarge x5 | $1,800 |
| ml-training-gpu | p3.8xlarge x4 | 25% | p3.2xlarge x2 | $900 |

**Implementation**:
```python
# Update cluster configuration
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Right-size data-etl-01 cluster
w.clusters.edit(
    cluster_id="data-etl-01",
    node_type_id="i3.2xlarge",
    num_workers=4,
    autoscale={
        "min_workers": 2,
        "max_workers": 6
    }
)
```

**Risk**: Low - Can rollback if performance degrades
**Effort**: 2 hours
**Savings**: $4,500/month

#### 1.2 Spot Instance Opportunities
**Finding**: 45 fault-tolerant jobs running on on-demand instances

**Jobs Identified**:
| Job ID | Job Name | Current Cost | Spot Savings | Risk Level |
|--------|----------|--------------|--------------|------------|
| 12345 | daily-aggregations | $800/month | $560/month | Low |
| 23456 | data-quality-checks | $600/month | $420/month | Low |
| 34567 | reporting-refresh | $450/month | $315/month | Low |

**Implementation**:
```python
# Configure job to use spot instances
w.jobs.update(
    job_id=12345,
    new_settings={
        "job_clusters": [{
            "new_cluster": {
                "node_type_id": "i3.xlarge",
                "aws_attributes": {
                    "availability": "SPOT_WITH_FALLBACK",
                    "zone_id": "auto",
                    "spot_bid_price_percent": 100
                },
                "num_workers": 4
            }
        }]
    }
)
```

**Risk**: Low - Fallback to on-demand if spot unavailable
**Effort**: 4 hours
**Savings**: $3,600/month (70% reduction on affected jobs)

#### 1.3 Autoscaling Optimization
**Finding**: Autoscaling ranges too wide, causing slow scale-down

**Current Configuration**:
```yaml
customer-360-cluster:
  min_workers: 2
  max_workers: 20
  scale_down_timeout: 300  # 5 minutes
```

**Recommended Configuration**:
```yaml
customer-360-cluster:
  min_workers: 4
  max_workers: 12
  scale_down_timeout: 120  # 2 minutes
```

**Rationale**:
- Workload typically needs 4-8 workers
- Max of 20 rarely reached (2% of time)
- Faster scale-down reduces idle time
- Slight increase in min improves startup time

**Implementation**:
```python
w.clusters.edit(
    cluster_id="customer-360-cluster",
    autoscale={
        "min_workers": 4,
        "max_workers": 12
    },
    autotermination_minutes=15
)
```

**Risk**: Low - Monitor for 1 week
**Effort**: 1 hour
**Savings**: $900/month

### 2. Job Scheduling Optimizations

#### 2.1 Overlapping Job Execution
**Finding**: 8 jobs scheduled at same time causing resource contention

**Current Schedule**:
```
02:00 AM UTC:
  - customer-360-bronze (30 min, 8 workers)
  - sales-analytics-silver (45 min, 12 workers)
  - inventory-sync (20 min, 6 workers)
  - financial-reports (60 min, 10 workers)
Total peak workers needed: 36
```

**Recommended Schedule**:
```
02:00 AM: customer-360-bronze (8 workers)
02:30 AM: inventory-sync (6 workers)
03:00 AM: sales-analytics-silver (12 workers)
03:45 AM: financial-reports (10 workers)
Peak workers needed: 12
```

**Implementation**:
```python
# Update job schedules to avoid overlap
jobs_schedule = [
    (12345, "0 0 2 * * ?"),  # customer-360-bronze at 2:00 AM
    (23456, "0 30 2 * * ?"), # inventory-sync at 2:30 AM
    (34567, "0 0 3 * * ?"),  # sales-analytics-silver at 3:00 AM
    (45678, "0 45 3 * * ?")  # financial-reports at 3:45 AM
]

for job_id, cron in jobs_schedule:
    w.jobs.update(
        job_id=job_id,
        new_settings={
            "schedule": {
                "quartz_cron_expression": cron,
                "timezone_id": "UTC"
            }
        }
    )
```

**Risk**: Low - Jobs still complete within SLA window
**Effort**: 2 hours
**Savings**: $1,350/month (reduced peak capacity needs)

#### 2.2 Job Cluster Consolidation
**Finding**: 15 single-job clusters that could share resources

**Recommendation**: Create shared job clusters for similar workload types

**Implementation**:
```python
# Create shared cluster for ETL jobs
shared_etl_cluster = {
    "name": "shared-etl-cluster",
    "node_type_id": "i3.2xlarge",
    "autoscale": {
        "min_workers": 4,
        "max_workers": 16
    },
    "spark_conf": {
        "spark.databricks.delta.preview.enabled": "true",
        "spark.databricks.delta.optimizeWrite.enabled": "true"
    }
}

# Update jobs to use shared cluster
for job_id in etl_job_ids:
    w.jobs.update(
        job_id=job_id,
        new_settings={
            "existing_cluster_id": shared_cluster_id
        }
    )
```

**Risk**: Medium - Monitor for resource contention
**Effort**: 6 hours
**Savings**: $1,800/month

### 3. Storage Optimizations

#### 3.1 Small File Problem
**Finding**: 45 tables with >100,000 small files (<10MB each)

**Tables Identified**:
| Table | Files | Avg Size | Recommended Action | Savings |
|-------|-------|----------|-------------------|---------|
| bronze.customer_events | 450K | 2MB | OPTIMIZE + ZORDER | $200/mo |
| silver.transactions | 320K | 5MB | OPTIMIZE | $150/mo |
| gold.daily_metrics | 180K | 8MB | OPTIMIZE | $100/mo |

**Implementation**:
```sql
-- Optimize tables with small files
OPTIMIZE bronze.customer_events
ZORDER BY (customer_id, event_date);

OPTIMIZE silver.transactions
ZORDER BY (transaction_date, customer_id);

OPTIMIZE gold.daily_metrics;

-- Schedule regular optimization
CREATE OR REPLACE FUNCTION optimize_tables()
RETURNS STRING
LANGUAGE PYTHON
AS $$
  from datetime import datetime
  tables = [
    ("bronze.customer_events", ["customer_id", "event_date"]),
    ("silver.transactions", ["transaction_date", "customer_id"]),
    ("gold.daily_metrics", [])
  ]

  for table, zorder_cols in tables:
    if zorder_cols:
      spark.sql(f"OPTIMIZE {table} ZORDER BY ({','.join(zorder_cols)})")
    else:
      spark.sql(f"OPTIMIZE {table}")

  return f"Optimized {len(tables)} tables at {datetime.now()}"
$$;

-- Schedule nightly optimization
CREATE JOB optimize_tables_job
SCHEDULE CRON '0 1 * * *'
AS SELECT optimize_tables();
```

**Risk**: Low - Read-only operation, improves query performance
**Effort**: 4 hours (initial) + 2 hours (automation)
**Savings**: $600/month (query cost reduction) + $200/month (storage)

#### 3.2 Unused Tables
**Finding**: 78 tables not queried in 90+ days

**Implementation**:
```python
# Identify and archive unused tables
from databricks.sdk import WorkspaceClient
from datetime import datetime, timedelta

w = WorkspaceClient()

# Get table lineage and access history
unused_threshold = datetime.now() - timedelta(days=90)
unused_tables = []

for catalog in w.catalogs.list():
    for schema in w.schemas.list(catalog.name):
        for table in w.tables.list(catalog.name, schema.name):
            # Check last access time
            if table.last_accessed < unused_threshold:
                unused_tables.append({
                    "full_name": f"{catalog.name}.{schema.name}.{table.name}",
                    "size_gb": table.storage_size_bytes / (1024**3),
                    "last_accessed": table.last_accessed
                })

# Archive to low-cost storage
for table_info in unused_tables:
    print(f"Archiving {table_info['full_name']} ({table_info['size_gb']:.2f} GB)")

    # Export to S3/ADLS/GCS archive bucket
    spark.sql(f"""
        COPY INTO 's3://archive-bucket/{table_info['full_name']}'
        FROM {table_info['full_name']}
        FILEFORMAT = PARQUET
    """)

    # Drop original table
    spark.sql(f"DROP TABLE IF EXISTS {table_info['full_name']}")
```

**Risk**: Low - Data archived before deletion
**Effort**: 8 hours
**Savings**: $1,200/month

#### 3.3 Data Retention Policies
**Finding**: Many tables retaining data beyond business requirements

**Recommendation**: Implement time-travel retention policies

**Implementation**:
```sql
-- Set retention policies on tables
ALTER TABLE bronze.raw_events
SET TBLPROPERTIES (
  'delta.logRetentionDuration' = '7 days',
  'delta.deletedFileRetentionDuration' = '7 days'
);

ALTER TABLE silver.processed_events
SET TBLPROPERTIES (
  'delta.logRetentionDuration' = '30 days',
  'delta.deletedFileRetentionDuration' = '30 days'
);

ALTER TABLE gold.aggregated_metrics
SET TBLPROPERTIES (
  'delta.logRetentionDuration' = '90 days',
  'delta.deletedFileRetentionDuration' = '90 days'
);

-- Schedule VACUUM operations
CREATE OR REPLACE FUNCTION vacuum_tables()
RETURNS STRING
LANGUAGE SQL
AS $$
  VACUUM bronze.raw_events RETAIN 7 HOURS;
  VACUUM silver.processed_events RETAIN 30 HOURS;
  VACUUM gold.aggregated_metrics RETAIN 90 HOURS;
  SELECT 'Vacuum completed successfully'
$$;
```

**Risk**: Low - Aligns with business retention requirements
**Effort**: 4 hours
**Savings**: $800/month

### 4. Additional Recommendations

#### 4.1 Photon Acceleration
**Finding**: Large-scale SQL queries not using Photon

**Recommendation**: Enable Photon for SQL-heavy workloads (2-3x faster, cost-neutral)

**Implementation**:
```python
w.clusters.edit(
    cluster_id="analytics-cluster",
    runtime_engine="PHOTON"
)
```

**Savings**: Indirect - Faster queries reduce DBU consumption

#### 4.2 Cluster Policies
**Recommendation**: Enforce cluster policies to prevent cost overruns

**Implementation**:
```json
{
  "cluster_type": {
    "type": "fixed",
    "value": "job"
  },
  "node_type_id": {
    "type": "allowlist",
    "values": ["i3.xlarge", "i3.2xlarge", "i3.4xlarge"]
  },
  "autoscale.max_workers": {
    "type": "range",
    "maxValue": 20
  },
  "autotermination_minutes": {
    "type": "fixed",
    "value": 15
  }
}
```

#### 4.3 Budget Alerts
**Recommendation**: Set up cost monitoring and alerts

**Implementation**:
```python
# Create budget alert
from databricks.sdk.service.billing import Budget, BudgetAlert

budget = Budget(
    name="monthly-workspace-budget",
    filter=f"workspace_id = '{workspace_id}'",
    period="1 month",
    start_date="2024-01-01",
    target_amount="45000",
    alerts=[
        BudgetAlert(alert_type="actual_cost", threshold_percent=80),
        BudgetAlert(alert_type="actual_cost", threshold_percent=100),
        BudgetAlert(alert_type="forecasted_cost", threshold_percent=100)
    ]
)

w.budgets.create(budget)
```

## Cost Savings Summary

### Immediate Actions (Week 1)
| Optimization | Effort | Savings | Risk |
|-------------|--------|---------|------|
| Cluster right-sizing | 2 hours | $4,500 | Low |
| Autoscaling tuning | 1 hour | $900 | Low |
| Spot instances (5 jobs) | 2 hours | $1,000 | Low |
| **Subtotal** | **5 hours** | **$6,400/mo** | **Low** |

### Short-term Actions (Month 1)
| Optimization | Effort | Savings | Risk |
|-------------|--------|---------|------|
| Table optimization | 6 hours | $800 | Low |
| Job schedule optimization | 2 hours | $1,350 | Low |
| Spot instances (remaining) | 2 hours | $2,600 | Low |
| **Subtotal** | **10 hours** | **$4,750/mo** | **Low** |

### Medium-term Actions (Month 2-3)
| Optimization | Effort | Savings | Risk |
|-------------|--------|---------|------|
| Job cluster consolidation | 6 hours | $1,800 | Medium |
| Storage archival | 8 hours | $1,200 | Low |
| Retention policies | 4 hours | $800 | Low |
| **Subtotal** | **18 hours** | **$3,800/mo** | **Low-Med** |

### **Total Potential Savings**
- **Monthly**: $11,250 (25% reduction)
- **Annual**: $135,000
- **Implementation Effort**: 33 hours
- **ROI**: 4,091% annually

## Implementation Checklist

### Pre-Implementation
- [ ] Review and approve optimization recommendations
- [ ] Schedule maintenance window for cluster changes
- [ ] Back up cluster configurations
- [ ] Notify stakeholders of upcoming changes
- [ ] Set up monitoring for performance metrics

### Week 1: Quick Wins
- [ ] Right-size over-provisioned clusters
- [ ] Tune autoscaling configurations
- [ ] Enable spot instances for 5 pilot jobs
- [ ] Set autotermination on idle clusters
- [ ] Monitor for performance regressions

### Week 2-4: Job Optimizations
- [ ] Optimize job schedules to reduce overlap
- [ ] Enable spot instances for remaining jobs
- [ ] Run table OPTIMIZE operations
- [ ] Implement VACUUM schedules
- [ ] Set up automated optimization jobs

### Month 2-3: Strategic Changes
- [ ] Consolidate single-job clusters
- [ ] Archive unused tables
- [ ] Implement retention policies
- [ ] Enable Photon on analytics clusters
- [ ] Create cluster policies
- [ ] Set up budget alerts

### Post-Implementation
- [ ] Monitor cost trends for 2 weeks
- [ ] Validate performance SLAs are met
- [ ] Document configuration changes
- [ ] Train team on new cluster policies
- [ ] Schedule quarterly cost reviews

## Monitoring and Validation

### Key Metrics to Track
1. **Daily DBU Consumption**
   - Target: 25% reduction
   - Alert if increase >5% week-over-week

2. **Job Success Rate**
   - Target: >99% (maintain current)
   - Alert if <98%

3. **Query Performance**
   - Target: <10% degradation
   - Alert if P95 latency increases >20%

4. **Storage Growth**
   - Target: Reduce growth rate by 30%
   - Alert if growth exceeds trend

5. **Cluster Utilization**
   - Target: >60% average CPU/memory
   - Alert if <40% for 3+ consecutive days

### Dashboards
```python
# Create cost monitoring dashboard
from databricks.sdk.service.sql import Dashboard, Widget

widgets = [
    Widget(
        name="Daily DBU Cost",
        visualization_id="line-chart",
        query="""
            SELECT date, SUM(dbu_cost) as total_cost
            FROM system.billing.usage
            WHERE date >= CURRENT_DATE - INTERVAL 90 DAYS
            GROUP BY date
            ORDER BY date
        """
    ),
    Widget(
        name="Top Cost Drivers",
        visualization_id="bar-chart",
        query="""
            SELECT cluster_name, SUM(dbu_cost) as cost
            FROM system.billing.usage
            WHERE date >= CURRENT_DATE - INTERVAL 30 DAYS
            GROUP BY cluster_name
            ORDER BY cost DESC
            LIMIT 10
        """
    ),
    Widget(
        name="Cluster Utilization",
        visualization_id="table",
        query="""
            SELECT
                cluster_id,
                AVG(cpu_percent) as avg_cpu,
                AVG(memory_percent) as avg_memory,
                COUNT(*) as measurements
            FROM system.compute.cluster_utilization
            WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL 7 DAYS
            GROUP BY cluster_id
        """
    )
]

dashboard = w.dashboards.create(
    name="Cost Optimization Tracking",
    parent_folder="/Shared/Dashboards",
    widgets=widgets
)
```

## Troubleshooting

### Issue: Performance degradation after cluster downsizing
**Solution**:
1. Check CPU/memory utilization metrics
2. Temporarily increase cluster size
3. Review query execution plans
4. Consider adding more workers vs larger workers

### Issue: Spot instance interruptions
**Solution**:
1. Verify fallback to on-demand is working
2. Adjust spot bid price percentage
3. Consider mixed on-demand/spot configurations
4. Use spot instances only for fault-tolerant workloads

### Issue: Job failures after schedule changes
**Solution**:
1. Check for data dependencies between jobs
2. Review job SLAs and adjust schedules
3. Add explicit job dependencies in workflow
4. Monitor job completion times

### Issue: Queries slower after table optimization
**Solution**:
1. Wait for optimization to complete (can take hours)
2. Check if ZORDER columns match query patterns
3. Update table statistics: `ANALYZE TABLE ... COMPUTE STATISTICS`
4. Review query execution plans

## Best Practices

### 1. Regular Reviews
- Schedule monthly cost review meetings
- Track optimization ROI
- Identify new optimization opportunities
- Adjust targets based on business growth

### 2. Cluster Policies
- Enforce instance type restrictions
- Set maximum cluster sizes
- Require autotermination
- Use preemptible instances by default

### 3. Storage Management
- Run OPTIMIZE weekly on large tables
- VACUUM monthly with appropriate retention
- Archive unused tables quarterly
- Monitor storage growth trends

### 4. Continuous Monitoring
- Set up cost anomaly detection
- Alert on unusual spending patterns
- Track cost per pipeline/job
- Monitor unit economics

### 5. Team Training
- Educate developers on cost implications
- Share optimization best practices
- Provide self-service cost dashboards
- Include cost metrics in code reviews

## Security Considerations

### 1. Access Controls
- Restrict cluster creation permissions
- Use cluster policies to enforce standards
- Audit cluster configuration changes
- Monitor for unauthorized clusters

### 2. Data Protection
- Validate archival/deletion permissions
- Test restore procedures
- Maintain audit logs
- Encrypt archived data

### 3. Compliance
- Ensure retention policies meet regulatory requirements
- Document data lifecycle policies
- Audit table access patterns
- Maintain lineage for archived data

## Related Commands

- `/databricks-engineering:plan-pipeline` - Plan cost-efficient pipelines
- `/databricks-engineering:deploy-workflow` - Deploy with cost controls
- `/databricks-engineering:monitor-data-product` - Monitor costs and performance
- `/databricks-engineering:validate-deployment` - Pre-deployment cost estimation

## References

- [Databricks Cost Optimization Guide](https://docs.databricks.com/administration-guide/account-settings/cost-optimization.html)
- [Cluster Configuration Best Practices](https://docs.databricks.com/clusters/configure.html)
- [Delta Lake Optimization Techniques](https://docs.databricks.com/delta/optimizations/index.html)
- [Spot Instance Pricing](https://docs.databricks.com/clusters/spot-instances.html)

---

**Last Updated**: 2024-12-31
**Version**: 1.0.0
**Category**: Cost Management
**Prepared by**: gekambaram
