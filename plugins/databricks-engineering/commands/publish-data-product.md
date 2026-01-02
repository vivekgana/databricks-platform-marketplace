# Publish Data Product Command

## Description
Publish data products to Unity Catalog with documentation, access controls, lineage tracking, and consumer discovery capabilities. Makes data products discoverable and consumable across the organization.

## Usage
```bash
/databricks-engineering:publish-data-product [product-name] [--catalog catalog] [--visibility visibility]
```

## Parameters

- `product-name` (required): Name of the data product to publish
- `--catalog` (optional): Target catalog (default: "main_production")
- `--visibility` (optional): "public", "internal", "private" (default: "internal")
- `--generate-docs` (optional): Auto-generate documentation (default: true)
- `--enable-lineage` (optional): Enable lineage tracking (default: true)
- `--create-sample-data` (optional): Generate sample dataset (default: true)
- `--register-metadata` (optional): Register in data catalog (default: true)

## Examples

### Example 1: Publish with default settings
```bash
/databricks-engineering:publish-data-product customer-360
```

### Example 2: Publish to specific catalog
```bash
/databricks-engineering:publish-data-product customer-360 \
  --catalog analytics_prod \
  --visibility internal
```

### Example 3: Publish with full documentation
```bash
/databricks-engineering:publish-data-product sales-analytics \
  --generate-docs \
  --create-sample-data \
  --enable-lineage
```

## What This Command Does

### Phase 1: Pre-Publishing Validation (5 minutes)
- Validates product definition completeness
- Checks data quality metrics
- Verifies access control configuration
- Tests SLA monitoring setup
- Validates documentation

### Phase 2: Catalog Registration (10 minutes)
- Creates Unity Catalog schema
- Registers tables with metadata
- Applies tags and classifications
- Configures access controls
- Enables change data feed

### Phase 3: Documentation Generation (15 minutes)
- Generates data dictionary
- Creates lineage diagrams
- Produces API documentation
- Generates sample queries
- Creates consumer guides

### Phase 4: Discovery Setup (5 minutes)
- Registers in data catalog
- Creates search metadata
- Configures recommendations
- Publishes to data marketplace
- Notifies potential consumers

## Generated Artifacts

### Product Metadata Registration
```python
# Generated registration script
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import *

w = WorkspaceClient()

# Register product schema
schema_info = w.schemas.create(
    catalog_name="main_production",
    name="customer_360",
    comment="Customer 360 data product - comprehensive customer view",
    properties={
        "data_product": "customer-360",
        "version": "1.0.0",
        "owner": "marketing-data@company.com",
        "domain": "marketing",
        "tier": "gold",
        "sla": "high",
        "sensitivity": "confidential"
    }
)

# Register tables with extended metadata
for table_def in product_tables:
    table_info = w.tables.create(
        catalog_name="main_production",
        schema_name="customer_360",
        name=table_def["name"],
        table_type=TableType.MANAGED,
        data_source_format=DataSourceFormat.DELTA,
        columns=table_def["columns"],
        comment=table_def["description"],
        properties={
            "data_product": "customer-360",
            "refresh_frequency": "daily",
            "quality_score": "99.5"
        }
    )

    # Apply data classification tags
    w.tables.update(
        full_name=f"main_production.customer_360.{table_def['name']}",
        tags={
            "PII": "true",
            "Confidential": "true",
            "GDPR": "true"
        }
    )

# Configure access controls
w.grants.update(
    catalog="main_production",
    schema="customer_360",
    table="customers",
    changes=[
        PermissionsChange(
            add=[
                Privilege.SELECT
            ],
            principal="marketing-analysts"
        )
    ]
)
```

### Lineage Tracking Setup
```sql
-- Enable lineage tracking
ALTER TABLE main_production.customer_360.customers
SET TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.enableLineage' = 'true'
);

-- Create lineage view
CREATE OR REPLACE VIEW main_production.customer_360.lineage_info AS
SELECT
  table_catalog,
  table_schema,
  table_name,
  source_type,
  source_name,
  transformation_logic,
  refresh_frequency,
  last_refresh_time
FROM system.information_schema.lineage
WHERE table_schema = 'customer_360';
```

### Auto-Generated Documentation
```markdown
# Customer 360 Data Product

**Status**: Published
**Version**: 1.0.0
**Owner**: marketing-data@company.com
**Published Date**: 2024-12-31

## Overview
Comprehensive customer view combining demographic, behavioral, transactional data.

## Tables

### main_production.customer_360.customers
**Description**: Core customer demographic and account information
**Row Count**: ~5M
**Update Frequency**: Daily
**Quality Score**: 99.5%

#### Schema
| Column | Type | Nullable | Description | PII |
|--------|------|----------|-------------|-----|
| customer_id | STRING | No | Unique customer identifier | No |
| email | STRING | No | Customer email address | Yes |
| first_name | STRING | Yes | Customer first name | Yes |
| last_name | STRING | Yes | Customer last name | Yes |
| country | STRING | No | Country code (ISO 3166) | No |
| account_status | STRING | No | Account status | No |
| lifetime_value | DECIMAL(10,2) | Yes | Customer LTV in USD | No |

#### Sample Queries
```sql
-- Get active customers by country
SELECT country, COUNT(*) as customer_count
FROM main_production.customer_360.customers
WHERE account_status = 'active'
GROUP BY country;

-- Calculate average customer value
SELECT AVG(lifetime_value) as avg_ltv
FROM main_production.customer_360.customers
WHERE account_status = 'active';
```

## Data Lineage
```
[CRM System] -> [Bronze] -> [Silver: Customers] -> [Gold: Customer 360]
                             ↓
                    [Silver: Transactions]
                             ↓
                      [Gold: Metrics]
```

## SLA Commitments
- **Freshness**: < 4 hours
- **Quality**: > 99%
- **Availability**: 99.9%
- **Performance**: < 5s P95

## Access Request
Contact: marketing-data@company.com
Slack: #customer-360-support
```

### Discovery Metadata
```json
{
  "product_id": "customer-360",
  "display_name": "Customer 360 View",
  "description": "Comprehensive customer data for analytics",
  "domain": "marketing",
  "tags": ["customer", "360", "marketing", "analytics"],
  "owner": {
    "team": "Marketing Data Team",
    "email": "marketing-data@company.com"
  },
  "catalog_location": {
    "catalog": "main_production",
    "schema": "customer_360"
  },
  "use_cases": [
    "Customer segmentation",
    "Churn prediction",
    "Personalization",
    "Campaign optimization"
  ],
  "consumers": [],
  "quality_score": 99.5,
  "freshness_score": 98.2,
  "popularity_score": 85,
  "published_date": "2024-12-31",
  "last_updated": "2024-12-31",
  "version": "1.0.0",
  "sla_tier": "high",
  "sensitivity": "confidential",
  "documentation_url": "https://wiki.company.com/customer-360",
  "sample_queries": [
    {
      "title": "Active customers by country",
      "query": "SELECT country, COUNT(*) FROM main_production.customer_360.customers WHERE account_status = 'active' GROUP BY country"
    }
  ]
}
```

## Publication Checklist

### Pre-Publication
- [ ] Product definition complete
- [ ] Data quality validated (>95% score)
- [ ] Access controls configured
- [ ] SLA monitoring active
- [ ] Documentation reviewed and approved
- [ ] Sample data generated
- [ ] Security scan completed
- [ ] Compliance approval obtained

### Publication
- [ ] Unity Catalog schema created
- [ ] Tables registered with metadata
- [ ] Tags and classifications applied
- [ ] Access controls applied
- [ ] Lineage tracking enabled
- [ ] Documentation generated
- [ ] Sample queries tested
- [ ] Discovery metadata published

### Post-Publication
- [ ] Verify product discoverable in catalog
- [ ] Test access request workflow
- [ ] Validate documentation links
- [ ] Announce to organization
- [ ] Monitor initial usage
- [ ] Gather consumer feedback

## Monitoring Dashboard

```sql
-- Product usage metrics
CREATE OR REPLACE VIEW main_production.monitoring.customer_360_usage AS
SELECT
  DATE(request_time) as usage_date,
  user_name,
  query_type,
  COUNT(*) as query_count,
  AVG(execution_time_ms) as avg_execution_time,
  SUM(bytes_scanned) as total_bytes_scanned
FROM system.access.table_lineage
WHERE table_schema = 'customer_360'
  AND request_time >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY DATE(request_time), user_name, query_type;

-- Quality metrics over time
CREATE OR REPLACE VIEW main_production.monitoring.customer_360_quality AS
SELECT
  check_date,
  table_name,
  quality_score,
  completeness_score,
  accuracy_score,
  consistency_score,
  freshness_hours
FROM main_production.monitoring.quality_metrics
WHERE product_name = 'customer-360'
  AND check_date >= CURRENT_DATE - INTERVAL 90 DAYS
ORDER BY check_date DESC;
```

## Consumer Onboarding Workflow

### 1. Discovery
```sql
-- Search data catalog
SELECT
  product_name,
  description,
  domain,
  owner,
  quality_score,
  documentation_url
FROM main_production.data_catalog.products
WHERE tags LIKE '%customer%'
  AND sensitivity IN ('public', 'internal')
ORDER BY popularity_score DESC;
```

### 2. Access Request
```python
# Request access programmatically
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

access_request = w.data_products.request_access(
    product_id="customer-360",
    justification="Marketing campaign analysis for Q1",
    duration_days=90,
    requested_permissions=["SELECT"]
)

print(f"Access request submitted: {access_request.request_id}")
print(f"Status: {access_request.status}")
print(f"Expected approval: {access_request.expected_approval_date}")
```

### 3. Approval Workflow
```python
# Auto-approval for authorized consumers
def process_access_request(request):
    """Process data product access request"""
    if request.user in authorized_groups:
        # Auto-approve
        grant_access(request)
        notify_requester(request, "approved")
    else:
        # Require manager approval
        notify_manager(request)
        wait_for_approval(request)
```

### 4. Access Grant
```sql
-- Grant access to approved consumer
GRANT SELECT ON SCHEMA main_production.customer_360
TO `approved-user@company.com`;

-- Or grant to group
GRANT SELECT ON SCHEMA main_production.customer_360
TO `data-analysts`;
```

## Best Practices

1. **Documentation First**: Complete documentation before publishing
2. **Quality Gates**: Enforce minimum quality thresholds
3. **Gradual Rollout**: Publish to limited audience first
4. **Monitor Usage**: Track consumption patterns and performance
5. **Gather Feedback**: Collect consumer feedback regularly
6. **Version Control**: Use semantic versioning for changes
7. **Deprecation Policy**: Provide adequate notice for breaking changes
8. **Support Model**: Define clear support channels and SLAs

## Troubleshooting

**Issue**: Product not appearing in catalog search
**Solution**: Verify discovery metadata published, check visibility settings, refresh catalog

**Issue**: Access requests not reaching approvers
**Solution**: Verify workflow configuration, check email settings, validate approval groups

**Issue**: Documentation links broken
**Solution**: Verify wiki/confluence permissions, update documentation URLs, republish metadata

**Issue**: Lineage not showing correctly
**Solution**: Verify change data feed enabled, check lineage configuration, refresh lineage view

## Security Considerations

1. **Data Classification**: Apply appropriate sensitivity tags
2. **Access Control**: Use least-privilege principle
3. **PII Protection**: Mask PII fields in views
4. **Audit Logging**: Enable comprehensive audit trails
5. **Compliance**: Verify regulatory compliance before publishing
6. **Encryption**: Ensure data encrypted at rest and in transit

## Related Commands

- `/databricks-engineering:create-data-product` - Create new data product
- `/databricks-engineering:configure-delta-share` - Enable external sharing
- `/databricks-engineering:manage-consumers` - Manage consumer access
- `/databricks-engineering:monitor-data-product` - Set up monitoring

---

**Last Updated**: 2024-12-31
**Version**: 1.0.0
**Category**: Data Products
**Prepared by**: gekambaram
