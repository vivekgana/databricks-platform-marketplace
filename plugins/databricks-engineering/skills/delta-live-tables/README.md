# Delta Live Tables Skill

**Quick Start Guide for Building Declarative Data Pipelines**

## Overview

Delta Live Tables (DLT) is a declarative framework for building reliable, maintainable, and testable data processing pipelines on Databricks. This skill provides production-ready templates, patterns, and examples for implementing DLT pipelines.

## Quick Start

### 1. Create Your First DLT Pipeline

```python
import dlt
from pyspark.sql.functions import *

# Bronze: Ingest raw data
@dlt.table(
    comment="Raw sales data",
    table_properties={"quality": "bronze"}
)
def bronze_sales_raw():
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .load("/mnt/landing/sales/")
            .withColumn("ingestion_time", current_timestamp())
    )

# Silver: Validate and cleanse
@dlt.table(
    comment="Validated sales data",
    table_properties={"quality": "silver"}
)
@dlt.expect_or_drop("valid_amount", "amount > 0")
@dlt.expect_or_drop("valid_date", "sale_date IS NOT NULL")
def silver_sales_validated():
    return (
        dlt.read_stream("bronze_sales_raw")
            .select(
                col("sale_id"),
                col("customer_id"),
                col("amount").cast("decimal(10,2)"),
                to_date(col("sale_date")).alias("sale_date")
            )
    )

# Gold: Aggregate metrics
@dlt.table(
    comment="Daily sales summary",
    table_properties={"quality": "gold"}
)
def gold_daily_sales():
    return (
        dlt.read("silver_sales_validated")
            .groupBy("sale_date")
            .agg(
                sum("amount").alias("total_revenue"),
                count("*").alias("transaction_count")
            )
    )
```

### 2. Deploy the Pipeline

```bash
# Using Databricks CLI
databricks pipelines create --settings dlt_pipeline_config.yaml

# Or using the UI
# 1. Go to Workflows > Delta Live Tables
# 2. Click "Create Pipeline"
# 3. Add your notebook path
# 4. Configure settings
# 5. Click "Create"
```

### 3. Run and Monitor

```bash
# Start pipeline update
databricks pipelines start-update --pipeline-id <pipeline-id>

# Check status
databricks pipelines get --pipeline-id <pipeline-id>
```

## What's Included

### Templates (`/templates/`)

1. **bronze_ingestion_template.py** - 7 Bronze layer patterns
   - Basic ingestion with Auto Loader
   - Schema hints and evolution
   - Multi-source consolidation
   - File notification mode

2. **silver_transformation_template.py** - 7 Silver layer patterns
   - Data validation and quality checks
   - Enrichment and derived columns
   - SCD Type 2 tracking
   - PII masking
   - Deduplication strategies
   - Error quarantine pattern

3. **gold_aggregation_template.py** - 7 Gold layer patterns
   - Daily/hourly aggregations
   - Customer lifetime value
   - Product performance metrics
   - Feature tables for ML
   - Time-series analysis
   - Executive dashboards

4. **dlt_pipeline_config.yaml** - Complete pipeline configuration
   - Production, development, and streaming configs
   - Cluster settings and autoscaling
   - Notifications and scheduling
   - Unity Catalog integration

### Examples (`/examples/`)

1. **complete_ecommerce_pipeline.py** - Full production pipeline
   - 4 Bronze ingestion streams
   - 4 Silver validation layers
   - 4 Gold analytics tables
   - Data quality monitoring

### Documentation

- **SKILL.md** - Comprehensive guide with:
  - Core concepts and patterns
  - Implementation examples
  - Best practices
  - Common pitfalls
  - References

## Key Features

### Declarative Syntax
Define what you want, not how to get it:
```python
@dlt.table
def my_table():
    return dlt.read_stream("source_table").filter(col("active") == True)
```

### Built-in Data Quality
Enforce quality with expectations:
```python
@dlt.expect_or_drop("valid_email", "email LIKE '%@%.%'")
@dlt.expect_or_fail("no_nulls", "id IS NOT NULL")
```

### Automatic Lineage
DLT automatically tracks data lineage across all tables.

### Simplified CDC
Handle change data capture with ease:
```python
dlt.apply_changes(
    target="customers_current",
    source="customers_cdc",
    keys=["customer_id"],
    sequence_by="updated_at",
    stored_as_scd_type=2
)
```

## Common Use Cases

### 1. Streaming ETL
```python
@dlt.table
def streaming_data():
    return spark.readStream.format("kafka").load()
```

### 2. Batch Processing
```python
@dlt.table
def batch_data():
    return spark.read.parquet("/path/to/data")
```

### 3. Multi-Hop Architecture
Bronze → Silver → Gold with automatic dependency resolution.

### 4. Real-time Analytics
Stream processing with watermarking and windowing.

## Best Practices

1. **Layer Separation**
   - Bronze: Minimal transformation, preserve raw data
   - Silver: Validate, cleanse, standardize
   - Gold: Aggregate for specific use cases

2. **Data Quality Strategy**
   - Use `expect_or_fail` for critical fields
   - Use `expect_or_drop` for invalid data
   - Use `expect` for warnings/monitoring

3. **Performance Optimization**
   - Enable Auto Optimize
   - Use Z-Ordering for common filters
   - Implement proper partitioning
   - Use streaming for incremental processing

4. **Error Handling**
   - Create quarantine tables for bad data
   - Monitor expectation violations
   - Set up alerting for failures

## Configuration

### Minimum Configuration
```yaml
name: my_pipeline
target: my_database
storage: /mnt/dlt/my_pipeline
libraries:
  - notebook:
      path: /path/to/notebook
```

### Production Configuration
```yaml
name: production_pipeline
target: prod_db
storage: /mnt/dlt/prod
continuous: false
edition: advanced

clusters:
  - label: default
    autoscale:
      min_workers: 2
      max_workers: 10
    node_type_id: i3.xlarge

notifications:
  - email_recipients:
      - team@company.com
    on_failure: true
```

## Monitoring

### Query Event Log
```python
event_log_path = f"{storage_location}/system/events"
events = spark.read.format("delta").load(event_log_path)

# View data quality metrics
events.filter(col("event_type") == "flow_progress").show()
```

### Track Expectations
```python
quality_metrics = (
    events
        .filter(col("event_type") == "flow_progress")
        .select(
            "timestamp",
            "details.flow_progress.data_quality.expectations"
        )
)
```

## Troubleshooting

### Pipeline Fails on Start
- Check notebook paths in configuration
- Verify storage location permissions
- Review syntax errors in DLT definitions

### Expectation Violations
- Query event log for violation details
- Review dropped records
- Adjust expectation thresholds

### Performance Issues
- Enable Auto Optimize
- Increase cluster size
- Check for skewed data
- Review shuffle partitions

## Next Steps

1. **Read SKILL.md** for comprehensive documentation
2. **Explore templates/** for production-ready code
3. **Run examples/** to see complete pipelines
4. **Check related skills:**
   - `medallion-architecture` for layer design
   - `data-quality` for Great Expectations
   - `testing-patterns` for pipeline testing
   - `cicd-workflows` for deployment automation

## Resources

- [DLT Documentation](https://docs.databricks.com/delta-live-tables/index.html)
- [DLT API Reference](https://docs.databricks.com/dev-tools/api/python/latest/dlt.html)
- [DLT Best Practices](https://docs.databricks.com/delta-live-tables/best-practices.html)
- [DLT Examples](https://github.com/databricks/dlt-examples)

## Support

For questions or issues:
- Review SKILL.md for detailed patterns
- Check examples/ for working code
- Consult Databricks documentation
- Contact your data platform team

---

**Last Updated:** 2026-01-01 19:57:49
**Version:** 1.0.0
**Author:** Databricks Platform Team
