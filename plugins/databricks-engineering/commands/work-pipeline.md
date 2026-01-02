# Work Pipeline

## Description
Execute pipeline implementation with Bronze/Silver/Gold layers and comprehensive testing. This command guides you through implementing a complete medallion architecture pipeline with data quality checks, unit tests, and integration tests.

## Usage
```bash
/databricks-engineering:work-pipeline [pipeline-name]
```

## What This Command Does

1. **Analyzes existing plan** - Reads pipeline specification from planning phase
2. **Generates Bronze layer** - Raw data ingestion with schema validation
3. **Generates Silver layer** - Cleaned and enriched data with business logic
4. **Generates Gold layer** - Aggregated business metrics and KPIs
5. **Creates data quality tests** - Great Expectations validation suites
6. **Creates unit tests** - pytest fixtures and test cases
7. **Creates integration tests** - End-to-end pipeline validation
8. **Generates documentation** - API docs and data lineage diagrams

## Prerequisites

- Completed pipeline planning with `/databricks-engineering:plan-pipeline`
- Databricks workspace configured
- Python 3.10+ with databricks-sdk installed
- Access to source data locations

## Parameters

- `pipeline-name` (required): Name of the pipeline to implement (from plan)
- `--layer` (optional): Implement specific layer only (bronze|silver|gold)
- `--skip-tests` (optional): Skip test generation
- `--no-quality-checks` (optional): Skip data quality validation setup

## Examples

### Example 1: Implement complete pipeline
```bash
/databricks-engineering:work-pipeline customer-360
```

### Example 2: Implement only Bronze layer
```bash
/databricks-engineering:work-pipeline customer-360 --layer bronze
```

### Example 3: Quick implementation without tests
```bash
/databricks-engineering:work-pipeline customer-360 --skip-tests
```

## Implementation Steps

### Step 1: Read Pipeline Specification
The command reads the plan from `plans/[pipeline-name]-plan.md` which includes:
- Source systems and data formats
- Transformation requirements
- Data quality rules
- Target schema definitions

### Step 2: Generate Bronze Layer
Creates raw ingestion code with:
- Schema enforcement (schema on read)
- Data validation (nullability, type checks)
- Metadata capture (source, timestamp, batch_id)
- Error handling and dead letter queues
- Incremental loading patterns

**Generated files:**
- `src/bronze/[pipeline-name]_bronze.py`
- `src/bronze/schemas/[source]_schema.py`
- `tests/bronze/test_[pipeline-name]_bronze.py`

### Step 3: Generate Silver Layer
Creates transformation logic with:
- Data cleansing (deduplication, standardization)
- Business logic (calculated fields, lookups)
- Data enrichment (joins, aggregations)
- SCD Type 2 handling (if needed)
- Change data capture

**Generated files:**
- `src/silver/[pipeline-name]_silver.py`
- `src/silver/transformations/[domain]_transforms.py`
- `tests/silver/test_[pipeline-name]_silver.py`

### Step 4: Generate Gold Layer
Creates business aggregations with:
- Dimension and fact tables
- Pre-aggregated metrics
- Business KPIs
- Reporting views
- Data marts

**Generated files:**
- `src/gold/[pipeline-name]_gold.py`
- `src/gold/metrics/[domain]_metrics.py`
- `tests/gold/test_[pipeline-name]_gold.py`

### Step 5: Create Data Quality Tests
Generates Great Expectations suites:
- Schema validation
- Data completeness checks
- Distribution checks
- Referential integrity
- Custom business rules

**Generated files:**
- `great_expectations/expectations/[layer]_suite.json`
- `src/quality/[pipeline-name]_quality.py`

### Step 6: Create Unit Tests
Generates pytest test suite:
- Fixtures for sample data
- Transformation unit tests
- Edge case validation
- Error handling tests

**Generated files:**
- `tests/unit/test_[pipeline-name].py`
- `tests/fixtures/[pipeline-name]_fixtures.py`

### Step 7: Create Integration Tests
Generates end-to-end tests:
- Full pipeline execution
- Data lineage validation
- Performance benchmarks
- Idempotency tests

**Generated files:**
- `tests/integration/test_[pipeline-name]_integration.py`

### Step 8: Generate Documentation
Creates comprehensive documentation:
- Pipeline architecture diagram
- Data flow diagrams
- Schema documentation
- API reference
- Runbook

**Generated files:**
- `docs/[pipeline-name]/README.md`
- `docs/[pipeline-name]/architecture.md`
- `docs/[pipeline-name]/schemas.md`

## Code Structure

The command generates this structure:
```
src/
├── bronze/
│   ├── [pipeline-name]_bronze.py
│   └── schemas/
├── silver/
│   ├── [pipeline-name]_silver.py
│   └── transformations/
├── gold/
│   ├── [pipeline-name]_gold.py
│   └── metrics/
└── quality/
    └── [pipeline-name]_quality.py

tests/
├── unit/
│   └── test_[pipeline-name].py
├── integration/
│   └── test_[pipeline-name]_integration.py
└── fixtures/
    └── [pipeline-name]_fixtures.py

docs/[pipeline-name]/
├── README.md
├── architecture.md
└── schemas.md
```

## Generated Code Features

### Bronze Layer Features
- Configurable source connectors (S3, ADLS, GCS, JDBC)
- Schema evolution handling
- Incremental load with watermarks
- Audit columns (load_timestamp, source_system, batch_id)
- Error handling with retry logic

### Silver Layer Features
- Deduplication strategies
- Data type standardization
- Business rule validation
- Lookup enrichment
- SCD Type 2 implementation (optional)

### Gold Layer Features
- Star schema design
- Pre-aggregations for performance
- Slowly changing dimensions
- Business metrics calculations
- Materialized views

### Testing Features
- PySpark session fixtures
- Sample data generators
- Assertion helpers for DataFrames
- Performance benchmarking utilities
- Mock external dependencies

## Configuration

The command uses configuration from `.databricks-plugin-config.yaml`:
```yaml
pipeline:
  bronze:
    checkpoint_location: /mnt/checkpoints/bronze
    bad_records_path: /mnt/errors/bronze
  silver:
    checkpoint_location: /mnt/checkpoints/silver
  gold:
    checkpoint_location: /mnt/checkpoints/gold

testing:
  unit_test_framework: pytest
  integration_test_framework: pytest
  quality_framework: great_expectations
```

## Next Steps

After implementation:
1. Run unit tests: `pytest tests/unit/`
2. Run integration tests: `pytest tests/integration/`
3. Validate data quality: `great_expectations checkpoint run`
4. Review code: `/databricks-engineering:review-pipeline [pipeline-name]`
5. Deploy: `/databricks-engineering:deploy-workflow [pipeline-name]`

## Related Commands

- `/databricks-engineering:plan-pipeline` - Create pipeline specification
- `/databricks-engineering:review-pipeline` - Multi-agent code review
- `/databricks-engineering:test-data-quality` - Run quality tests
- `/databricks-engineering:deploy-workflow` - Deploy to Databricks

## Troubleshooting

**Issue**: Schema conflicts during Silver layer transformation
**Solution**: Check Bronze layer schema definitions and Silver layer expectations

**Issue**: Tests fail with PySpark initialization errors
**Solution**: Ensure SPARK_HOME is set and pytest-spark plugin is installed

**Issue**: Great Expectations validation failures
**Solution**: Review expectations in great_expectations/expectations/ and adjust thresholds

## Best Practices

1. **Incremental Processing**: Use watermarks for large datasets
2. **Idempotency**: Ensure pipeline can be safely re-run
3. **Error Handling**: Implement dead letter queues for bad records
4. **Testing**: Write tests before implementation (TDD approach)
5. **Documentation**: Keep docs in sync with code changes
6. **Version Control**: Commit after each layer implementation
7. **Code Review**: Use automated agents for quality checks

## Performance Considerations

- **Partitioning**: Partition large tables by date or key columns
- **Z-Ordering**: Use Z-ORDER on frequently filtered columns
- **Caching**: Cache intermediate DataFrames when reused
- **Broadcasting**: Broadcast small lookup tables
- **Shuffle Optimization**: Minimize shuffles in transformations

## Security Best Practices

- **PII Handling**: Implement masking/hashing in Bronze layer
- **Access Control**: Use Unity Catalog for fine-grained permissions
- **Secrets Management**: Store credentials in Databricks secrets
- **Audit Logging**: Enable table audit logs
- **Data Lineage**: Leverage Unity Catalog lineage

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0
**Category**: Development
