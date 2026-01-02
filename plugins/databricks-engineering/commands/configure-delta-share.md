# Configure Delta Share Command

## Description
Set up Delta Sharing to securely share data products with external consumers, partners, and customers. Enables data sharing without copying data, maintaining governance and security controls.

## Usage
```bash
/databricks-engineering:configure-delta-share [product-name] [--recipient recipient-name] [--create-share]
```

## Parameters

- `product-name` (required): Name of data product to share
- `--recipient` (optional): External recipient name/identifier
- `--create-share` (optional): Create new share (default: true)
- `--access-level` (optional): "read-only", "read-with-metadata" (default: "read-only")
- `--expiration-days` (optional): Share expiration in days (default: 365)
- `--enable-cdf` (optional): Enable change data feed (default: true)
- `--generate-credentials` (optional): Generate recipient credentials (default: true)

## Examples

### Example 1: Create share for external partner
```bash
/databricks-engineering:configure-delta-share customer-360 \
  --recipient partner-company \
  --access-level read-with-metadata
```

### Example 2: Set up time-limited share
```bash
/databricks-engineering:configure-delta-share sales-analytics \
  --recipient client-xyz \
  --expiration-days 90 \
  --enable-cdf
```

### Example 3: Create share with multiple tables
```bash
/databricks-engineering:configure-delta-share marketing-insights \
  --recipient agency-abc \
  --tables "customers,campaigns,metrics"
```

## What This Command Does

### Phase 1: Share Configuration (10 minutes)
1. **Share Creation**
   - Creates Delta Share object
   - Configures share permissions
   - Sets up access controls
   - Defines sharing boundaries
   - Configures expiration policies

2. **Table Selection**
   - Identifies tables to share
   - Validates permissions
   - Checks data sensitivity
   - Reviews PII fields
   - Configures column filtering

3. **Recipient Setup**
   - Creates recipient identity
   - Generates credentials
   - Configures authentication
   - Sets up activation URL
   - Defines usage limits

### Phase 2: Security Configuration (15 minutes)
1. **Data Filtering**
   - Row-level filtering setup
   - Column masking configuration
   - PII redaction rules
   - Geographic restrictions
   - Time-based access control

2. **Change Data Feed**
   - Enables CDC if requested
   - Configures retention
   - Sets up streaming access
   - Defines change tracking
   - Configures incremental updates

### Phase 3: Documentation and Testing (10 minutes)
1. **Consumer Documentation**
   - Generates connection guide
   - Creates sample code
   - Documents schema
   - Provides troubleshooting guide
   - Lists support contacts

2. **Validation**
   - Tests share connectivity
   - Validates permissions
   - Verifies data filtering
   - Tests credential generation
   - Validates documentation

## Generated Configuration

### Delta Share Definition
```sql
-- Create share
CREATE SHARE IF NOT EXISTS customer_360_share
COMMENT 'Customer 360 data product shared with external partners';

-- Add tables to share
ALTER SHARE customer_360_share
ADD TABLE main_production.customer_360.customers
COMMENT 'Customer demographic and account information';

ALTER SHARE customer_360_share
ADD TABLE main_production.customer_360.customer_metrics
COMMENT 'Customer behavior and transaction metrics';

-- Configure partition filtering (geographic restriction)
ALTER SHARE customer_360_share
ADD TABLE main_production.customer_360.customers
PARTITION (country = 'US');

-- View share details
DESCRIBE SHARE customer_360_share;
SHOW ALL IN SHARE customer_360_share;
```

### Recipient Configuration
```sql
-- Create recipient
CREATE RECIPIENT IF NOT EXISTS partner_company_recipient
USING ID 'partner-company-123'
COMMENT 'External partner - Partner Company Inc.';

-- Grant share access to recipient
GRANT SELECT ON SHARE customer_360_share
TO RECIPIENT partner_company_recipient;

-- Set expiration
ALTER RECIPIENT partner_company_recipient
SET SHARE_EXPIRATION = INTERVAL 365 DAYS;

-- Generate activation credentials
DESCRIBE RECIPIENT partner_company_recipient;
```

### Row-Level Security View
```sql
-- Create filtered view for sharing
CREATE OR REPLACE VIEW main_production.customer_360.customers_shared AS
SELECT
  customer_id,
  -- Mask email
  CONCAT(SUBSTRING(email, 1, 3), '***@***') AS email,
  first_name,
  last_name,
  -- Mask phone
  '***-***-****' AS phone_number,
  -- Remove date of birth
  NULL AS date_of_birth,
  country,
  account_status,
  customer_since,
  lifetime_value,
  last_purchase_date,
  total_orders,
  created_at,
  updated_at
FROM main_production.customer_360.customers
WHERE country IN ('US', 'CA')  -- Geographic filter
  AND account_status = 'active'  -- Status filter
  AND customer_since >= '2020-01-01';  -- Recency filter

-- Add filtered view to share instead of base table
ALTER SHARE customer_360_share
ADD VIEW main_production.customer_360.customers_shared
AS customers;
```

### Python Configuration Script
```python
# scripts/configure_delta_share.py
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sharing import *
import secrets
import string

class DeltaShareConfigurator:
    """Configure Delta Sharing for data products"""

    def __init__(self, workspace_url: str, token: str):
        self.client = WorkspaceClient(host=workspace_url, token=token)

    def create_share(
        self,
        share_name: str,
        tables: list,
        comment: str = None
    ) -> Share:
        """Create Delta Share"""
        print(f"Creating share: {share_name}")

        share = self.client.shares.create(
            name=share_name,
            comment=comment
        )

        # Add tables to share
        for table in tables:
            self.client.shares.update(
                name=share_name,
                updates=[
                    SharedDataObjectUpdate(
                        action=SharedDataObjectUpdateAction.ADD,
                        data_object=SharedDataObject(
                            name=table["full_name"],
                            comment=table.get("comment"),
                            shared_as=table.get("shared_as"),
                            cdf_enabled=table.get("cdf_enabled", False),
                            partitions=[
                                Partition(values=[
                                    PartitionValue(
                                        name=p["name"],
                                        value=p["value"]
                                    ) for p in table.get("partitions", [])
                                ])
                            ] if table.get("partitions") else None
                        )
                    )
                ]
            )
            print(f"  ✓ Added table: {table['full_name']}")

        return share

    def create_recipient(
        self,
        recipient_name: str,
        sharing_identifier: str,
        comment: str = None,
        expiration_days: int = 365
    ) -> CreateRecipient:
        """Create recipient for external access"""
        print(f"Creating recipient: {recipient_name}")

        recipient = self.client.recipients.create(
            name=recipient_name,
            comment=comment,
            authentication_type=AuthenticationType.TOKEN,
            sharing_code=self._generate_sharing_code(),
            expiration_time=self._get_expiration_timestamp(expiration_days)
        )

        print(f"  ✓ Recipient created: {recipient.name}")
        print(f"  ✓ Activation URL: {recipient.activation_url}")

        return recipient

    def grant_share_to_recipient(
        self,
        share_name: str,
        recipient_name: str
    ):
        """Grant share access to recipient"""
        print(f"Granting share {share_name} to {recipient_name}")

        self.client.grants.update(
            share_name=share_name,
            updates=[
                PermissionUpdate(
                    recipient_name=recipient_name,
                    privilege=Privilege.SELECT
                )
            ]
        )

        print(f"  ✓ Access granted")

    def get_share_credentials(
        self,
        recipient_name: str
    ) -> dict:
        """Get credentials for recipient"""
        recipient = self.client.recipients.get(name=recipient_name)

        return {
            "endpoint": recipient.endpoint,
            "bearer_token": recipient.bearer_token,
            "activation_url": recipient.activation_url,
            "expiration_time": recipient.expiration_time
        }

    def _generate_sharing_code(self) -> str:
        """Generate secure sharing code"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))

    def _get_expiration_timestamp(self, days: int) -> int:
        """Calculate expiration timestamp"""
        from datetime import datetime, timedelta
        expiration = datetime.now() + timedelta(days=days)
        return int(expiration.timestamp() * 1000)

    def setup_change_data_feed(self, table_full_name: str):
        """Enable change data feed for incremental sharing"""
        print(f"Enabling Change Data Feed for {table_full_name}")

        # Enable CDF on table
        self.client.sql_exec(f"""
            ALTER TABLE {table_full_name}
            SET TBLPROPERTIES (
                'delta.enableChangeDataFeed' = 'true',
                'delta.logRetentionDuration' = '365 days',
                'delta.deletedFileRetentionDuration' = '365 days'
            )
        """)

        print(f"  ✓ CDF enabled")


# Example usage
if __name__ == "__main__":
    configurator = DeltaShareConfigurator(
        workspace_url="https://your-workspace.cloud.databricks.com",
        token="your-token"
    )

    # Create share
    share = configurator.create_share(
        share_name="customer_360_share",
        comment="Customer 360 data for external partners",
        tables=[
            {
                "full_name": "main_production.customer_360.customers_shared",
                "comment": "Filtered customer data",
                "shared_as": "customers",
                "cdf_enabled": True,
                "partitions": [
                    {"name": "country", "value": "US"}
                ]
            }
        ]
    )

    # Create recipient
    recipient = configurator.create_recipient(
        recipient_name="partner_company",
        sharing_identifier="partner-company-123",
        comment="Partner Company Inc.",
        expiration_days=365
    )

    # Grant access
    configurator.grant_share_to_recipient(
        share_name="customer_360_share",
        recipient_name="partner_company"
    )

    # Get credentials
    creds = configurator.get_share_credentials("partner_company")
    print("\nRecipient Credentials:")
    print(f"  Endpoint: {creds['endpoint']}")
    print(f"  Activation URL: {creds['activation_url']}")
```

## Consumer Integration Guide

### Python Consumer Example
```python
# consumer_example.py
"""
Example: Consuming Delta Share with Python
"""
import delta_sharing

# Load share profile
profile = delta_sharing.SharingProfile(
    endpoint="https://your-sharing-server.com/delta-sharing",
    bearer_token="your-token-here"
)

# List available shares
client = delta_sharing.SharingClient(profile)
shares = client.list_shares()
print(f"Available shares: {shares}")

# List tables in share
tables = client.list_tables("customer_360_share")
print(f"Available tables: {tables}")

# Load table as pandas DataFrame
df = delta_sharing.load_as_pandas(
    f"{profile}#customer_360_share.default.customers"
)
print(df.head())

# Load with filters
filtered_df = delta_sharing.load_as_pandas(
    f"{profile}#customer_360_share.default.customers",
    filters=[("country", "=", "US")]
)

# Stream changes (if CDF enabled)
for batch in delta_sharing.load_as_streaming_dataframe(
    f"{profile}#customer_360_share.default.customers"
):
    process_batch(batch)
```

### Spark Consumer Example
```python
# spark_consumer_example.py
"""
Example: Consuming Delta Share with Spark
"""
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("DeltaShareConsumer") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Configure Delta Sharing
profile_path = "/path/to/profile.json"

# Read shared table
df = spark.read \
    .format("deltaSharing") \
    .option("profile", profile_path) \
    .option("table", "customer_360_share.default.customers") \
    .load()

# Query data
df.filter("country = 'US'") \
  .groupBy("account_status") \
  .count() \
  .show()

# Read change data feed
cdf_df = spark.read \
    .format("deltaSharing") \
    .option("profile", profile_path) \
    .option("table", "customer_360_share.default.customers") \
    .option("readChangeDataFeed", "true") \
    .option("startingVersion", 0) \
    .load()

cdf_df.show()
```

## Monitoring and Audit

### Share Usage Tracking
```sql
-- Monitor share usage
SELECT
  share_name,
  recipient_name,
  table_name,
  DATE(request_time) as request_date,
  COUNT(*) as request_count,
  SUM(bytes_transferred) as total_bytes,
  AVG(response_time_ms) as avg_response_time
FROM system.access.delta_sharing_requests
WHERE share_name = 'customer_360_share'
  AND request_time >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY share_name, recipient_name, table_name, DATE(request_time)
ORDER BY request_date DESC, request_count DESC;

-- Audit access patterns
SELECT
  recipient_name,
  table_name,
  access_type,
  COUNT(*) as access_count,
  MAX(request_time) as last_access
FROM system.access.delta_sharing_audit
WHERE share_name = 'customer_360_share'
GROUP BY recipient_name, table_name, access_type
ORDER BY access_count DESC;
```

### Alert Configuration
```yaml
# Unusual access pattern alert
alert:
  name: unusual-delta-share-access
  condition: |
    SELECT COUNT(*) as request_count
    FROM system.access.delta_sharing_requests
    WHERE share_name = 'customer_360_share'
      AND request_time >= CURRENT_TIMESTAMP - INTERVAL 1 HOUR
    HAVING request_count > 1000
  severity: medium
  notification: slack, email
```

## Best Practices

1. **Minimize Shared Data**: Only share necessary columns and rows
2. **Use Views**: Create filtered views instead of sharing base tables
3. **Enable CDF**: For incremental data sync
4. **Set Expirations**: Define time limits for external shares
5. **Monitor Usage**: Track access patterns and data transfer
6. **Audit Regularly**: Review recipients and permissions
7. **Document Contract**: Clearly document shared schema
8. **Version Control**: Maintain compatibility across versions

## Security Considerations

1. **Data Filtering**: Always filter sensitive data before sharing
2. **PII Masking**: Mask or remove PII fields
3. **Row-Level Security**: Apply appropriate filters
4. **Token Management**: Rotate bearer tokens regularly
5. **Access Review**: Quarterly access reviews
6. **Audit Logging**: Enable comprehensive logging
7. **Encryption**: Data encrypted in transit
8. **Compliance**: Verify data sharing complies with regulations

## Troubleshooting

**Issue**: Recipient cannot access share
**Solution**: Verify activation URL used, check token not expired, validate network connectivity

**Issue**: Performance issues with large tables
**Solution**: Use partition filters, enable CDF for incremental sync, optimize table structure

**Issue**: Schema evolution breaking consumer
**Solution**: Version shares, maintain backward compatibility, notify consumers of changes

## Related Commands

- `/databricks-engineering:create-data-product` - Create data product
- `/databricks-engineering:publish-data-product` - Publish to catalog
- `/databricks-engineering:manage-consumers` - Manage consumer access
- `/databricks-engineering:monitor-data-product` - Monitor usage

---

**Last Updated**: 2024-12-31
**Version**: 1.0.0
**Category**: Data Sharing
**Prepared by**: gekambaram
