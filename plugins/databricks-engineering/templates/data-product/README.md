# Data Product Template with Contracts and SLAs

**Document Version:** 1.0
**Last Updated:** 2026-01-01
**Template Type:** Data Product with Governance

## Overview

This template provides a complete data product implementation with data contracts, SLA definitions, quality monitoring, and consumer management capabilities.

## Features

- **Data Contracts**: Schema enforcement and versioning
- **SLA Management**: Uptime, freshness, and quality guarantees
- **Quality Monitoring**: Automated quality checks and alerts
- **Consumer Management**: Track and manage data consumers
- **Delta Sharing**: Share data products securely
- **Lineage Tracking**: Complete data lineage documentation
- **Alerting**: Automated alerts for SLA violations

## Project Structure

```
data-product/
├── README.md
├── data_product_definition.yaml    # Product specification
├── data_contract.json              # Schema contract
├── sla_definition.yaml             # SLA specifications
├── src/
│   ├── __init__.py
│   ├── product_pipeline.py        # Pipeline implementation
│   ├── quality_checks.py          # Quality validation
│   └── monitoring.py              # Monitoring and alerting
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_pipeline.py
│   └── test_quality.py
├── databricks.yml
└── requirements.txt
```

## Quick Start

### 1. Define Your Data Product

Edit `data_product_definition.yaml`:

```yaml
product:
  name: "customer_360"
  version: "1.0.0"
  owner: "data-platform-team"
  description: "Unified customer view"

  sla:
    freshness: "1 hour"
    availability: "99.9%"
    quality_threshold: "95%"

  consumers:
    - name: "marketing-team"
      access_level: "read"
    - name: "analytics-team"
      access_level: "read"
```

### 2. Define Data Contract

Edit `data_contract.json`:

```json
{
  "schema_version": "1.0.0",
  "fields": [
    {
      "name": "customer_id",
      "type": "string",
      "required": true,
      "description": "Unique customer identifier"
    }
  ]
}
```

### 3. Deploy

```bash
databricks bundle deploy -t prod
```

## Data Contract

The data contract defines the schema, guarantees, and versioning:

```json
{
  "contract_version": "1.0",
  "product_name": "customer_360",
  "schema_version": "1.0.0",
  "fields": [...],
  "guarantees": {
    "no_nulls": ["customer_id", "email"],
    "unique_keys": ["customer_id"],
    "value_ranges": {
      "lifetime_value": {"min": 0}
    }
  }
}
```

## SLA Definition

SLAs define service level commitments:

```yaml
sla:
  freshness:
    metric: "data_age"
    threshold: "1 hour"
    measurement: "max(current_timestamp - update_timestamp)"

  quality:
    metric: "quality_score"
    threshold: "95%"
    checks:
      - null_check
      - range_check
      - referential_integrity

  availability:
    metric: "uptime"
    threshold: "99.9%"
```

## Quality Monitoring

Automated quality checks run on every update:

```python
from src.quality_checks import DataQualityValidator

validator = DataQualityValidator(
    catalog="main",
    schema="products",
    table="customer_360"
)

# Run quality checks
report = validator.validate_all()

# Check SLA compliance
compliance = validator.check_sla_compliance()
```

## Usage Examples

### Create Data Product

```python
from src.product_pipeline import DataProductPipeline

pipeline = DataProductPipeline(
    product_name="customer_360",
    catalog="main",
    schema="products"
)

# Build the data product
pipeline.build()

# Validate against contract
pipeline.validate_contract()

# Publish for consumers
pipeline.publish()
```

### Monitor SLA Compliance

```python
from src.monitoring import SLAMonitor

monitor = SLAMonitor(
    product_name="customer_360",
    sla_config="sla_definition.yaml"
)

# Check all SLAs
status = monitor.check_all_slas()

# Send alerts if violations detected
if not status.compliant:
    monitor.send_alerts(status.violations)
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Test contract compliance
pytest tests/test_quality.py::test_contract_compliance -v

# Test SLA checks
pytest tests/test_pipeline.py::test_sla_monitoring -v
```

## Deployment

### Development
```bash
databricks bundle deploy -t dev
```

### Production
```bash
databricks bundle deploy -t prod
```

## Monitoring Dashboard

The template includes monitoring for:

- **Data Freshness**: Track data age
- **Quality Score**: Aggregate quality metrics
- **SLA Compliance**: Track SLA adherence
- **Consumer Usage**: Monitor data product usage
- **Error Rates**: Track failures and errors

## Delta Sharing

Share data products with external consumers:

```python
# Create share
databricks shares create customer_360_share

# Add table to share
databricks shares add-table \
  --share customer_360_share \
  --table main.products.customer_360

# Add recipient
databricks recipients create \
  --name partner_company \
  --sharing-identifier partner@company.com
```

## Best Practices

1. **Version Control**: Use semantic versioning for contracts
2. **Backwards Compatibility**: Maintain compatibility when updating
3. **Clear Documentation**: Document all fields and guarantees
4. **Monitoring**: Set up alerts for SLA violations
5. **Testing**: Test contracts before deployment

## Troubleshooting

### Contract Validation Fails
- Review schema changes
- Check field requirements
- Verify data types

### SLA Violations
- Check pipeline performance
- Review data quality
- Verify resource allocation

## Documentation

- [Data Contracts Guide](https://docs.databricks.com/)
- [SLA Management](https://docs.databricks.com/)
- [Delta Sharing](https://docs.databricks.com/delta-sharing/)
