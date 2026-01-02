# Bronze-Silver-Gold Medallion Architecture Project

**Document Version:** 1.0
**Last Updated:** 2026-01-01
**Template Type:** Data Engineering Pipeline

## Overview

This template provides a complete implementation of the Medallion Architecture (Bronze-Silver-Gold) pattern for Databricks. It includes production-ready code for data ingestion, transformation, and aggregation across three data quality layers.

## Architecture

```
Bronze Layer (Raw Data)
    |
    v
Silver Layer (Cleaned & Validated)
    |
    v
Gold Layer (Business Aggregates)
```

### Layer Definitions

- **Bronze**: Raw data ingestion with minimal transformations
- **Silver**: Cleaned, validated, and deduplicated data
- **Gold**: Business-level aggregates and feature tables

## Project Structure

```
bronze-silver-gold/
├── README.md                      # This file
├── databricks.yml                 # Databricks Asset Bundle configuration
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore patterns
├── src/
│   ├── bronze/
│   │   ├── __init__.py
│   │   ├── ingest_raw_data.py    # Bronze layer ingestion
│   │   └── ingestion_config.py   # Ingestion configuration
│   ├── silver/
│   │   ├── __init__.py
│   │   ├── transform_data.py     # Silver layer transformations
│   │   └── data_quality.py       # Data quality checks
│   └── gold/
│       ├── __init__.py
│       ├── aggregate_metrics.py  # Gold layer aggregations
│       └── business_logic.py     # Business rules
└── tests/
    ├── __init__.py
    ├── conftest.py               # Pytest configuration
    ├── test_bronze_ingestion.py
    ├── test_silver_transformation.py
    └── test_gold_aggregation.py
```

## Prerequisites

- Databricks workspace (AWS, Azure, or GCP)
- Unity Catalog enabled
- Python 3.9+
- Databricks CLI installed
- Appropriate permissions for catalog/schema creation

## Setup Instructions

### 1. Clone and Configure

```bash
# Create your project from this template
cp -r bronze-silver-gold/ my-data-project/
cd my-data-project/

# Configure your environment
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-token"
```

### 2. Update Configuration

Edit `databricks.yml` to match your environment:

```yaml
targets:
  dev:
    workspace:
      host: ${DATABRICKS_HOST}
    variables:
      catalog: dev_catalog
      schema: dev_schema

  prod:
    workspace:
      host: ${DATABRICKS_HOST}
    variables:
      catalog: prod_catalog
      schema: prod_schema
```

### 3. Install Dependencies

```bash
# Install Python dependencies locally
pip install -r requirements.txt

# Or install on Databricks cluster
databricks fs cp requirements.txt dbfs:/FileStore/requirements.txt
```

### 4. Deploy with Databricks Asset Bundles

```bash
# Validate bundle configuration
databricks bundle validate

# Deploy to development
databricks bundle deploy -t dev

# Deploy to production
databricks bundle deploy -t prod
```

### 5. Run the Pipeline

```bash
# Run bronze ingestion
databricks bundle run bronze_ingestion_job -t dev

# Run silver transformation
databricks bundle run silver_transformation_job -t dev

# Run gold aggregation
databricks bundle run gold_aggregation_job -t dev
```

## Usage Examples

### Bronze Layer - Raw Data Ingestion

```python
from src.bronze.ingest_raw_data import BronzeIngestion

# Initialize ingestion
ingestion = BronzeIngestion(
    catalog="my_catalog",
    schema="my_schema",
    source_path="/mnt/data/raw/"
)

# Ingest data
ingestion.ingest_json_data(
    source="events",
    table_name="bronze_events"
)
```

### Silver Layer - Data Transformation

```python
from src.silver.transform_data import SilverTransformation

# Initialize transformation
transformation = SilverTransformation(
    catalog="my_catalog",
    schema="my_schema"
)

# Transform bronze to silver
transformation.clean_and_validate(
    source_table="bronze_events",
    target_table="silver_events"
)
```

### Gold Layer - Business Aggregates

```python
from src.gold.aggregate_metrics import GoldAggregation

# Initialize aggregation
aggregation = GoldAggregation(
    catalog="my_catalog",
    schema="my_schema"
)

# Create business metrics
aggregation.create_daily_metrics(
    source_table="silver_events",
    target_table="gold_daily_metrics"
)
```

## Data Quality

The template includes comprehensive data quality checks at each layer:

### Bronze Layer Quality
- Schema validation
- Null checks for required fields
- Duplicate detection
- Data type validation

### Silver Layer Quality
- Business rule validation
- Referential integrity checks
- Range validation
- Format validation

### Gold Layer Quality
- Aggregation verification
- Metric accuracy checks
- SLA compliance monitoring

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific layer tests
pytest tests/test_bronze_ingestion.py -v
pytest tests/test_silver_transformation.py -v
pytest tests/test_gold_aggregation.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Medallion Pipeline CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Databricks
        run: databricks bundle deploy -t prod
```

## Monitoring and Observability

The template includes built-in monitoring:

- **Pipeline Metrics**: Execution time, record counts, error rates
- **Data Quality Metrics**: Validation pass rates, anomaly detection
- **Cost Tracking**: Compute usage, storage costs
- **Alerting**: Configurable alerts for failures and SLA breaches

## Best Practices

1. **Incremental Processing**: Use Delta Lake time travel for efficient incremental loads
2. **Partitioning**: Partition tables by date for optimal query performance
3. **Z-Ordering**: Apply Z-ORDER on frequently filtered columns
4. **Vacuum**: Regularly vacuum old table versions to manage storage
5. **Optimization**: Run OPTIMIZE on tables after large updates

## Performance Tuning

```python
# Optimize Delta tables
spark.sql(f"""
    OPTIMIZE {catalog}.{schema}.silver_events
    ZORDER BY (event_date, user_id)
""")

# Vacuum old versions (keep 7 days)
spark.sql(f"""
    VACUUM {catalog}.{schema}.silver_events
    RETAIN 168 HOURS
""")
```

## Troubleshooting

### Common Issues

**Issue**: Table not found error
```
Solution: Ensure catalog and schema exist and you have proper permissions
```

**Issue**: Out of memory during processing
```
Solution: Increase cluster size or implement batch processing
```

**Issue**: Slow queries on silver/gold tables
```
Solution: Check partitioning strategy and apply Z-ORDER optimization
```

## Advanced Features

- **Change Data Capture (CDC)**: Process updates and deletes
- **Slowly Changing Dimensions (SCD)**: Track historical changes
- **Data Lineage**: Track data flow across layers
- **Schema Evolution**: Handle schema changes gracefully

## Support and Documentation

- [Databricks Medallion Architecture Guide](https://docs.databricks.com/lakehouse/medallion.html)
- [Delta Lake Best Practices](https://docs.delta.io/latest/best-practices.html)
- [Unity Catalog Documentation](https://docs.databricks.com/data-governance/unity-catalog/index.html)

## License

This template is provided as-is for use with Databricks projects.

## Contributing

Contributions are welcome! Please follow the standard pull request process.
