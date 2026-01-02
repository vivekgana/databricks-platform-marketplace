# Create Data Product Command

## Description
Design and create a data product with well-defined interfaces, contracts, SLAs, governance policies, and consumer management. Implements data mesh principles with self-serve data infrastructure.

## Usage
```bash
/databricks-engineering:create-data-product [product-name] [--domain domain] [--tier tier]
```

## Parameters

- `product-name` (required): Name of the data product (e.g., "customer-360", "sales-analytics")
- `--domain` (optional): Business domain - "marketing", "sales", "finance", "operations" (default: "general")
- `--tier` (optional): Data tier - "gold", "platinum" (default: "gold")
- `--owner` (optional): Product owner email (default: current user)
- `--sla` (optional): SLA level - "critical", "high", "medium", "low" (default: "medium")
- `--sensitivity` (optional): Data sensitivity - "public", "internal", "confidential", "restricted" (default: "internal")

## Examples

### Example 1: Create basic data product
```bash
/databricks-engineering:create-data-product customer-360 --domain marketing
```

### Example 2: Create platinum tier product with strict SLA
```bash
/databricks-engineering:create-data-product real-time-fraud-detection \
  --domain finance \
  --tier platinum \
  --sla critical \
  --sensitivity confidential
```

### Example 3: Create sales analytics product
```bash
/databricks-engineering:create-data-product sales-analytics \
  --domain sales \
  --owner sales-team@company.com \
  --sla high
```

## What This Command Does

### Phase 1: Product Definition (10-15 minutes)

1. **Discovery and Requirements**
   - Interactive questionnaire about product purpose
   - Identify target consumers and use cases
   - Define data sources and lineage
   - Establish SLA requirements
   - Determine data retention policies

2. **Schema Design**
   - Design product schema and tables
   - Define data contracts
   - Establish naming conventions
   - Create data quality rules
   - Document field definitions

3. **Governance Setup**
   - Define access policies
   - Set up data classification tags
   - Establish lineage tracking
   - Configure audit logging
   - Define compliance requirements

### Phase 2: Product Creation (15-20 minutes)

1. **Unity Catalog Setup**
   - Create dedicated schema for product
   - Set up table structures
   - Configure access controls
   - Apply governance tags
   - Enable audit logging

2. **Data Contract Creation**
   - Generate contract specification
   - Define versioning strategy
   - Create schema evolution rules
   - Document breaking vs non-breaking changes
   - Set up contract validation

3. **SLA Configuration**
   - Define freshness requirements
   - Set quality thresholds
   - Establish availability targets
   - Configure performance metrics
   - Set up SLA monitoring

4. **Documentation Generation**
   - Create product README
   - Generate API documentation
   - Create consumer onboarding guide
   - Document data dictionary
   - Generate sample queries

### Phase 3: Testing and Validation (5-10 minutes)

1. **Validate product structure**
2. **Test access controls**
3. **Verify data contracts**
4. **Validate SLA monitoring**
5. **Generate sample data**

## Generated Structure

```
data-products/
├── customer-360/
│   ├── product.yaml                    # Product manifest
│   ├── contract.yaml                   # Data contract specification
│   ├── sla.yaml                        # SLA definitions
│   ├── governance.yaml                 # Governance policies
│   ├── schemas/
│   │   ├── customers_v1.sql           # Table DDL
│   │   ├── customer_metrics_v1.sql
│   │   └── customer_segments_v1.sql
│   ├── quality/
│   │   ├── expectations.yaml          # Data quality rules
│   │   └── validation_rules.py
│   ├── monitoring/
│   │   ├── sla_dashboard.sql
│   │   ├── quality_dashboard.sql
│   │   └── alerts.yaml
│   ├── docs/
│   │   ├── README.md                  # Product overview
│   │   ├── data-dictionary.md         # Field definitions
│   │   ├── consumer-guide.md          # How to consume
│   │   ├── sample-queries.sql         # Example usage
│   │   └── changelog.md               # Version history
│   └── tests/
│       ├── contract_tests.py
│       └── integration_tests.py
```

## Product Manifest

```yaml
# data-products/customer-360/product.yaml
product_metadata:
  name: customer-360
  display_name: "Customer 360 View"
  version: "1.0.0"
  domain: marketing
  tier: gold
  owner:
    name: "Marketing Data Team"
    email: marketing-data@company.com
    slack_channel: "#marketing-data"
  created_date: "2024-12-31"
  last_updated: "2024-12-31"

description: |
  Comprehensive view of customer data combining demographic, behavioral,
  transactional, and engagement data. Provides single source of truth
  for customer analytics and segmentation.

use_cases:
  - Customer segmentation and targeting
  - Personalization and recommendations
  - Churn prediction and prevention
  - Customer lifetime value analysis
  - Marketing campaign optimization

data_sources:
  - name: CRM System
    type: Salesforce
    frequency: Daily
  - name: Web Analytics
    type: Google Analytics
    frequency: Hourly
  - name: Transaction Database
    type: PostgreSQL
    frequency: Real-time
  - name: Customer Support
    type: Zendesk
    frequency: Daily

catalog_location:
  catalog: main_production
  schema: customer_360
  tables:
    - name: customers
      description: "Core customer demographic and account information"
      row_count: ~5M
      update_frequency: Daily
    - name: customer_metrics
      description: "Aggregated customer behavior and transaction metrics"
      row_count: ~5M
      update_frequency: Daily
    - name: customer_segments
      description: "Customer segments and classifications"
      row_count: ~500K
      update_frequency: Weekly

sla:
  freshness:
    target: "< 4 hours"
    measurement: "Time from source update to availability"
  quality:
    target: "> 99%"
    measurement: "Percentage of records passing all quality checks"
  availability:
    target: "99.9%"
    measurement: "Uptime percentage"
  performance:
    target: "< 5 seconds"
    measurement: "P95 query latency for standard queries"

data_classification:
  sensitivity: confidential
  contains_pii: true
  pii_fields:
    - email
    - phone_number
    - full_address
  compliance:
    - GDPR
    - CCPA
    - SOX
  retention_period: "7 years"

quality_metrics:
  completeness:
    critical_fields:
      - customer_id
      - email
      - created_date
    target: 100%
  accuracy:
    validation_rules: 15
    target: 99.5%
  consistency:
    cross_table_checks: 8
    target: 99.9%

access_control:
  default_access: DENY
  approved_consumers:
    - group: marketing-analysts
      permission: SELECT
    - group: data-scientists
      permission: SELECT
    - service_principal: reporting-service
      permission: SELECT
  approval_required: true
  approval_workflow: manager-approval

monitoring:
  enabled: true
  dashboards:
    - sla_tracking
    - quality_metrics
    - usage_analytics
  alerts:
    - sla_breach
    - quality_degradation
    - unusual_access_patterns

support:
  documentation_url: https://wiki.company.com/customer-360
  slack_channel: "#customer-360-support"
  on_call_rotation: marketing-data-oncall
  escalation_contact: data-platform@company.com

tags:
  cost_center: marketing
  project: customer-analytics
  criticality: high
  data_mesh_domain: marketing
```

## Data Contract Specification

```yaml
# data-products/customer-360/contract.yaml
contract_version: "1.0.0"
schema_version: "1.0.0"
last_updated: "2024-12-31"

tables:
  customers:
    description: "Core customer information"
    schema:
      fields:
        - name: customer_id
          type: STRING
          nullable: false
          description: "Unique customer identifier"
          primary_key: true
          constraints:
            - type: format
              pattern: "^CUST-[0-9]{10}$"

        - name: email
          type: STRING
          nullable: false
          description: "Customer email address"
          pii: true
          constraints:
            - type: format
              pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
            - type: unique
              scope: global

        - name: first_name
          type: STRING
          nullable: true
          description: "Customer first name"
          pii: true

        - name: last_name
          type: STRING
          nullable: true
          description: "Customer last name"
          pii: true

        - name: phone_number
          type: STRING
          nullable: true
          description: "Customer phone number"
          pii: true
          masked_view: true

        - name: date_of_birth
          type: DATE
          nullable: true
          description: "Customer date of birth"
          pii: true
          constraints:
            - type: range
              min: "1900-01-01"
              max: "current_date"

        - name: country
          type: STRING
          nullable: false
          description: "Customer country code (ISO 3166-1 alpha-2)"
          constraints:
            - type: enum
              values: [US, CA, UK, DE, FR, AU, JP]

        - name: account_status
          type: STRING
          nullable: false
          description: "Current account status"
          constraints:
            - type: enum
              values: [active, inactive, suspended, closed]

        - name: customer_since
          type: DATE
          nullable: false
          description: "Date customer account was created"

        - name: lifetime_value
          type: DECIMAL(10,2)
          nullable: true
          description: "Calculated customer lifetime value in USD"
          constraints:
            - type: range
              min: 0
              max: 1000000

        - name: last_purchase_date
          type: DATE
          nullable: true
          description: "Date of most recent purchase"

        - name: total_orders
          type: INTEGER
          nullable: false
          description: "Total number of orders placed"
          default: 0
          constraints:
            - type: range
              min: 0

        - name: created_at
          type: TIMESTAMP
          nullable: false
          description: "Record creation timestamp"

        - name: updated_at
          type: TIMESTAMP
          nullable: false
          description: "Record last update timestamp"

    primary_key: [customer_id]
    partitioned_by: [country, account_status]
    clustered_by: [customer_id]

    quality_expectations:
      - name: no_null_customer_id
        type: not_null
        column: customer_id
        severity: critical

      - name: unique_customer_id
        type: unique
        column: customer_id
        severity: critical

      - name: valid_email_format
        type: regex
        column: email
        pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        severity: high

      - name: valid_account_status
        type: in_set
        column: account_status
        values: [active, inactive, suspended, closed]
        severity: critical

      - name: reasonable_lifetime_value
        type: range
        column: lifetime_value
        min: 0
        max: 1000000
        severity: medium

versioning:
  strategy: semantic
  breaking_changes:
    - Removing columns
    - Changing column data types
    - Adding NOT NULL constraints to existing columns
    - Changing primary key
  non_breaking_changes:
    - Adding new columns
    - Relaxing constraints
    - Adding indexes
    - Documentation updates

  deprecation_policy:
    notice_period_days: 90
    support_period_days: 180
    communication_channels:
      - email
      - slack
      - documentation

backward_compatibility:
  guaranteed_versions: 2
  migration_scripts_provided: true
  dual_running_period_days: 30
```

## SLA Definition

```yaml
# data-products/customer-360/sla.yaml
sla_version: "1.0.0"
effective_date: "2024-12-31"
review_frequency: quarterly

freshness:
  description: "Data must be updated within defined time windows"
  metrics:
    - table: customers
      target_latency: 4 hours
      measurement_method: "max(updated_at) compared to source system"
      breach_threshold: 6 hours
      measurement_frequency: "Every 30 minutes"

    - table: customer_metrics
      target_latency: 4 hours
      measurement_method: "max(calculation_date) compared to current date"
      breach_threshold: 8 hours
      measurement_frequency: "Every 30 minutes"

quality:
  description: "Data must meet quality standards"
  metrics:
    - name: completeness
      target: 99.5%
      measurement: "Percentage of non-null values in required fields"
      breach_threshold: 98%

    - name: accuracy
      target: 99.5%
      measurement: "Percentage of records passing validation rules"
      breach_threshold: 98%

    - name: consistency
      target: 99.9%
      measurement: "Percentage of records with consistent cross-table references"
      breach_threshold: 99%

availability:
  description: "Product must be accessible during defined hours"
  target: 99.9%
  measurement: "Uptime percentage"
  measurement_window: monthly
  planned_maintenance:
    window: "Sunday 02:00-04:00 UTC"
    notification_period: "7 days advance notice"
    max_frequency: "Monthly"

performance:
  description: "Query performance targets"
  metrics:
    - query_type: "Simple SELECT on primary key"
      target_latency_p95: "< 1 second"
      target_latency_p99: "< 2 seconds"

    - query_type: "Aggregation on partition columns"
      target_latency_p95: "< 5 seconds"
      target_latency_p99: "< 10 seconds"

    - query_type: "Complex multi-table JOIN"
      target_latency_p95: "< 30 seconds"
      target_latency_p99: "< 60 seconds"

support:
  description: "Support response times"
  levels:
    - severity: critical
      description: "Product unavailable or data corruption"
      response_time: "15 minutes"
      resolution_target: "2 hours"
      communication: "Every 30 minutes"

    - severity: high
      description: "SLA breach or significant quality issues"
      response_time: "1 hour"
      resolution_target: "8 hours"
      communication: "Every 2 hours"

    - severity: medium
      description: "Minor issues not affecting core functionality"
      response_time: "4 hours"
      resolution_target: "2 business days"
      communication: "Daily"

    - severity: low
      description: "Questions, enhancements, documentation"
      response_time: "1 business day"
      resolution_target: "5 business days"
      communication: "As needed"

monitoring:
  dashboards:
    - name: "SLA Tracking Dashboard"
      url: "/sql/dashboards/customer-360-sla"
      refresh_frequency: "5 minutes"

  alerts:
    - name: "Freshness SLA Breach"
      condition: "Data age > 6 hours"
      severity: high
      notification_channels: [email, slack, pagerduty]

    - name: "Quality SLA Breach"
      condition: "Quality score < 98%"
      severity: high
      notification_channels: [email, slack]

    - name: "Availability Issue"
      condition: "Query failures > 5 in 10 minutes"
      severity: critical
      notification_channels: [email, slack, pagerduty]

consequences:
  sla_breach:
    reporting: "Automatic incident report generated"
    review: "Root cause analysis within 48 hours"
    improvement_plan: "Action items identified and tracked"

  repeated_breaches:
    threshold: "3 breaches in 30 days"
    action: "Executive review and remediation plan required"
```

## Generated Code Examples

### Table Creation DDL
```sql
-- schemas/customers_v1.sql
CREATE TABLE IF NOT EXISTS main_production.customer_360.customers (
  customer_id STRING NOT NULL COMMENT 'Unique customer identifier (Format: CUST-XXXXXXXXXX)',
  email STRING NOT NULL COMMENT 'Customer email address (PII)',
  first_name STRING COMMENT 'Customer first name (PII)',
  last_name STRING COMMENT 'Customer last name (PII)',
  phone_number STRING COMMENT 'Customer phone number (PII)',
  date_of_birth DATE COMMENT 'Customer date of birth (PII)',
  country STRING NOT NULL COMMENT 'Customer country code (ISO 3166-1 alpha-2)',
  account_status STRING NOT NULL COMMENT 'Current account status (active, inactive, suspended, closed)',
  customer_since DATE NOT NULL COMMENT 'Date customer account was created',
  lifetime_value DECIMAL(10,2) COMMENT 'Calculated customer lifetime value in USD',
  last_purchase_date DATE COMMENT 'Date of most recent purchase',
  total_orders INT NOT NULL DEFAULT 0 COMMENT 'Total number of orders placed',
  created_at TIMESTAMP NOT NULL COMMENT 'Record creation timestamp',
  updated_at TIMESTAMP NOT NULL COMMENT 'Record last update timestamp',

  CONSTRAINT pk_customers PRIMARY KEY (customer_id)
)
USING DELTA
PARTITIONED BY (country, account_status)
CLUSTER BY (customer_id)
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.columnMapping.mode' = 'name',
  'delta.minReaderVersion' = '2',
  'delta.minWriterVersion' = '5',
  'data_product' = 'customer-360',
  'data_product_version' = '1.0.0',
  'owner' = 'marketing-data@company.com',
  'sensitivity' = 'confidential',
  'contains_pii' = 'true'
);

-- Row-level security for PII
CREATE OR REPLACE VIEW main_production.customer_360.customers_masked AS
SELECT
  customer_id,
  CASE
    WHEN is_member('marketing-analysts') THEN email
    ELSE CONCAT(SUBSTRING(email, 1, 3), '***@***')
  END AS email,
  first_name,
  last_name,
  CASE
    WHEN is_member('marketing-analysts') THEN phone_number
    ELSE '***-***-****'
  END AS phone_number,
  NULL AS date_of_birth,  -- Always masked
  country,
  account_status,
  customer_since,
  lifetime_value,
  last_purchase_date,
  total_orders,
  created_at,
  updated_at
FROM main_production.customer_360.customers;

-- Apply tags for data classification
ALTER TABLE main_production.customer_360.customers
SET TAGS ('PII' = 'email,phone_number,date_of_birth');

-- Grant access
GRANT SELECT ON TABLE main_production.customer_360.customers TO `marketing-analysts`;
GRANT SELECT ON VIEW main_production.customer_360.customers_masked TO `all-users`;
```

### Consumer Onboarding Guide
```markdown
# Customer 360 Data Product - Consumer Guide

## Overview
The Customer 360 data product provides a comprehensive view of customer data,
combining demographic, behavioral, transactional, and engagement information.

## Quick Start

### 1. Request Access
```bash
# Request access through the data portal
databricks data-product request-access \
  --product customer-360 \
  --justification "Marketing campaign analysis" \
  --duration 90days
```

### 2. Verify Access
```sql
-- Check your access level
SHOW GRANTS ON TABLE main_production.customer_360.customers;
```

### 3. Sample Queries

#### Get customer profile
```sql
SELECT *
FROM main_production.customer_360.customers
WHERE customer_id = 'CUST-1234567890';
```

#### Find active customers by country
```sql
SELECT country, COUNT(*) as customer_count
FROM main_production.customer_360.customers
WHERE account_status = 'active'
GROUP BY country
ORDER BY customer_count DESC;
```

#### Calculate average customer metrics
```sql
SELECT
  account_status,
  AVG(lifetime_value) as avg_ltv,
  AVG(total_orders) as avg_orders,
  COUNT(*) as customer_count
FROM main_production.customer_360.customers
GROUP BY account_status;
```

## SLA Commitments
- **Freshness**: Data updated within 4 hours
- **Quality**: >99% data quality score
- **Availability**: 99.9% uptime
- **Performance**: <5 second P95 query latency

## Data Classification
- **Sensitivity**: Confidential
- **PII Fields**: email, phone_number, date_of_birth
- **Compliance**: GDPR, CCPA, SOX compliant

## Support
- **Slack**: #customer-360-support
- **Email**: marketing-data@company.com
- **Documentation**: https://wiki.company.com/customer-360
```

## Best Practices

1. **Product Naming**: Use clear, descriptive names (customer-360, not cust_v2)
2. **Schema Design**: Follow naming conventions, use appropriate data types
3. **Documentation**: Maintain comprehensive, up-to-date documentation
4. **Versioning**: Use semantic versioning (major.minor.patch)
5. **Access Control**: Default deny, explicit grants
6. **Monitoring**: Set up proactive monitoring and alerting
7. **Testing**: Validate contracts, quality, and performance
8. **Communication**: Maintain changelog, notify consumers of changes

## Troubleshooting

**Issue**: Cannot access product tables
**Solution**: Request access through data portal, verify group membership

**Issue**: Query performance slower than SLA
**Solution**: Check partition pruning, use clustered columns, review query plan

**Issue**: Data freshness SLA breach
**Solution**: Check upstream pipeline status, review monitoring dashboards

## Related Commands

- `/databricks-engineering:publish-data-product` - Publish product to catalog
- `/databricks-engineering:configure-delta-share` - Enable external sharing
- `/databricks-engineering:manage-consumers` - Manage consumer access
- `/databricks-engineering:monitor-data-product` - Set up monitoring

---

**Last Updated**: 2024-12-31
**Version**: 1.0.0
**Category**: Data Products
**Prepared by**: gekambaram
