# Delta Live Tables Pipeline Template

**Document Version:** 1.0
**Last Updated:** 2026-01-01
**Template Type:** DLT Pipeline with Data Quality

## Overview

This template provides a production-ready Delta Live Tables (DLT) pipeline with comprehensive data quality expectations, testing framework, and deployment configuration.

## Features

- **Declarative Pipeline Development**: Python-based DLT pipeline definitions
- **Built-in Data Quality**: Expectations with automatic quarantine
- **Schema Evolution**: Automatic schema detection and evolution
- **Incremental Processing**: Efficient incremental data processing
- **Monitoring & Observability**: Built-in metrics and logging
- **Testing Framework**: Unit and integration tests for DLT pipelines

## Project Structure

```
delta-live-tables/
├── README.md
├── dlt_pipeline.py              # Main DLT pipeline definition
├── dlt_config.yaml              # Pipeline configuration
├── expectations/
│   ├── __init__.py
│   ├── bronze_expectations.py  # Bronze layer expectations
│   ├── silver_expectations.py  # Silver layer expectations
│   └── gold_expectations.py    # Gold layer expectations
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_dlt_pipeline.py
├── databricks.yml               # Asset Bundle configuration
└── requirements.txt
```

## Quick Start

### 1. Create DLT Pipeline

```bash
# Deploy the bundle
databricks bundle deploy -t dev

# Create the DLT pipeline
databricks pipelines create --config dlt_config.yaml
```

### 2. Start Pipeline

```bash
# Start the pipeline
databricks pipelines start --pipeline-id <pipeline-id>

# Or trigger via API
databricks pipelines run --pipeline-id <pipeline-id>
```

### 3. Monitor Pipeline

```bash
# Check pipeline status
databricks pipelines get --pipeline-id <pipeline-id>

# View event logs
databricks pipelines events --pipeline-id <pipeline-id>
```

## Pipeline Architecture

```
Source Data → Bronze (Raw) → Silver (Cleaned) → Gold (Aggregated)
                ↓               ↓                  ↓
             Expectations    Expectations      Expectations
                ↓               ↓                  ↓
             Quarantine      Quarantine         Quarantine
```

## Data Quality Expectations

### Bronze Layer
- Non-null required fields
- Valid data types
- Source file tracking

### Silver Layer
- Business rule validation
- Referential integrity
- Data format validation
- Deduplication

### Gold Layer
- Aggregation validity
- Metric accuracy
- SLA compliance

## Usage Examples

### Define Bronze Table

```python
import dlt
from pyspark.sql.functions import current_timestamp

@dlt.table(
    name="bronze_events",
    comment="Raw event data from source",
    table_properties={
        "quality": "bronze",
        "pipelines.autoOptimize.managed": "true"
    }
)
@dlt.expect_all_or_drop({
    "valid_id": "id IS NOT NULL",
    "valid_timestamp": "timestamp IS NOT NULL"
})
def bronze_events():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("/mnt/source/events/")
        .withColumn("ingestion_time", current_timestamp())
    )
```

### Define Silver Table

```python
@dlt.table(
    name="silver_events",
    comment="Cleaned and validated events"
)
@dlt.expect_all({
    "valid_user_id": "user_id IS NOT NULL",
    "valid_event_type": "event_type IN ('click', 'view', 'purchase')",
    "valid_amount": "amount >= 0"
})
def silver_events():
    return (
        dlt.read_stream("bronze_events")
        .select("id", "user_id", "event_type", "amount", "timestamp")
        .dropDuplicates(["id"])
    )
```

### Define Gold Table

```python
@dlt.table(
    name="gold_daily_metrics",
    comment="Daily aggregated metrics"
)
def gold_daily_metrics():
    return (
        dlt.read("silver_events")
        .groupBy("date", "event_type")
        .agg(
            count("*").alias("event_count"),
            sum("amount").alias("total_amount"),
            avg("amount").alias("avg_amount")
        )
    )
```

## Configuration

### dlt_config.yaml

```yaml
name: "my-dlt-pipeline"
storage: "/mnt/dlt/storage"
target: "my_catalog.my_schema"

configuration:
  pipelines.enableAutoOptimization: true
  pipelines.enableChangeDataCapture: true

libraries:
  - file:
      path: "./dlt_pipeline.py"

clusters:
  - label: "default"
    autoscale:
      min_workers: 1
      max_workers: 5
      mode: "ENHANCED"
```

## Testing

Run tests locally:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test
pytest tests/test_dlt_pipeline.py::test_bronze_expectations -v
```

## Deployment

### Development Environment

```bash
databricks bundle deploy -t dev
databricks pipelines update --pipeline-id <id> --settings dlt_config.yaml
```

### Production Environment

```bash
databricks bundle deploy -t prod
databricks pipelines update --pipeline-id <id> --settings dlt_config.yaml
```

## Monitoring and Alerts

### Built-in Metrics
- Records processed per minute
- Data quality violations
- Pipeline latency
- Error rates

### Custom Alerts

```python
# Set up alerts for quality violations
@dlt.expect_or_fail("critical_validation", "status = 'valid'")
def critical_data():
    return dlt.read("source_table")
```

## Best Practices

1. **Expectations**: Use `expect_all` for warnings, `expect_all_or_drop` for filtering, `expect_or_fail` for critical validations
2. **Incremental Processing**: Use `@dlt.table` with streaming for continuous processing
3. **Partitioning**: Partition large tables by date for optimal performance
4. **Schema Evolution**: Enable `pipelines.autoSchemaEvolution` for flexible schemas
5. **Cost Optimization**: Use autoscaling and spot instances

## Troubleshooting

### Pipeline Fails to Start
- Check cluster configuration
- Verify library dependencies
- Review event logs

### Data Quality Violations
- Review expectations in event log
- Check quarantine tables
- Adjust expectation thresholds

### Performance Issues
- Enable autoOptimization
- Adjust cluster size
- Review partitioning strategy

## Advanced Features

- **Change Data Capture (CDC)**: Track table changes
- **Schema Evolution**: Automatic schema updates
- **Multi-hop Architecture**: Bronze/Silver/Gold layers
- **Data Lineage**: Automatic lineage tracking
- **Time Travel**: Query historical data

## Documentation

- [Delta Live Tables Documentation](https://docs.databricks.com/delta-live-tables/)
- [Data Quality Expectations](https://docs.databricks.com/delta-live-tables/expectations.html)
- [Pipeline Monitoring](https://docs.databricks.com/delta-live-tables/observability.html)

## License

This template is provided for use with Databricks Delta Live Tables.
