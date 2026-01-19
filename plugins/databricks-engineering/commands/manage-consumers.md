# Manage Consumers Command

## Description
Manage data product consumers, access requests, permissions, usage tracking, and consumer lifecycle. Provides self-service access management with approval workflows.

## Usage
```bash
/databricks-engineering:manage-consumers [product-name] [--action action] [--consumer consumer-id]
```

## Parameters

- `product-name` (required): Name of data product
- `--action` (optional): "list", "approve", "revoke", "audit", "report" (default: "list")
- `--consumer` (optional): Specific consumer identifier
- `--status` (optional): Filter by status - "active", "pending", "revoked" (default: "all")
- `--generate-report` (optional): Generate consumer analytics report (default: false)

## Examples

### Example 1: List all consumers
```bash
/databricks-engineering:manage-consumers customer-360 --action list
```

### Example 2: Approve pending access request
```bash
/databricks-engineering:manage-consumers customer-360 \
  --action approve \
  --consumer user@company.com
```

### Example 3: Revoke access
```bash
/databricks-engineering:manage-consumers customer-360 \
  --action revoke \
  --consumer external-partner
```

### Example 4: Generate usage report
```bash
/databricks-engineering:manage-consumers customer-360 \
  --action report \
  --generate-report
```

## What This Command Does

### List Consumers
- Shows all current consumers
- Displays access permissions
- Shows last access times
- Lists usage statistics
- Identifies inactive consumers

### Approve Access
- Reviews access request details
- Validates business justification
- Applies appropriate permissions
- Sends approval notification
- Logs approval decision

### Revoke Access
- Removes consumer permissions
- Sends revocation notification
- Archives access history
- Updates audit logs
- Validates no active sessions

### Audit
- Reviews all access grants
- Identifies stale access
- Reports compliance status
- Tracks permission changes
- Generates audit reports

## Generated Management Interface

### Consumer Management Dashboard
```sql
-- Consumer overview
CREATE OR REPLACE VIEW data_products.customer_360_consumers AS
SELECT
  c.consumer_id,
  c.consumer_name,
  c.consumer_type,
  c.access_granted_date,
  c.access_expires_date,
  c.granted_by,
  c.justification,
  u.last_access_date,
  u.total_queries,
  u.total_bytes_scanned,
  CASE
    WHEN c.access_expires_date < CURRENT_DATE THEN 'expired'
    WHEN u.last_access_date < CURRENT_DATE - INTERVAL 90 DAYS THEN 'inactive'
    ELSE 'active'
  END as status
FROM data_products.consumer_access c
LEFT JOIN data_products.consumer_usage u
  ON c.consumer_id = u.consumer_id
WHERE c.product_name = 'customer-360'
ORDER BY u.total_queries DESC;
```

### Access Request Approval Workflow
```python
# scripts/approve_access_request.py
from databricks.sdk import WorkspaceClient
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ConsumerAccessManager:
    """Manage data product consumer access"""

    def __init__(self, workspace_url: str, token: str):
        self.client = WorkspaceClient(host=workspace_url, token=token)

    def list_pending_requests(self, product_name: str) -> list:
        """List pending access requests"""
        query = f"""
            SELECT
                request_id,
                consumer_id,
                consumer_name,
                requested_date,
                justification,
                requested_permissions,
                business_unit
            FROM data_products.access_requests
            WHERE product_name = '{product_name}'
              AND status = 'pending'
            ORDER BY requested_date ASC
        """
        return self.client.sql_exec(query).fetchall()

    def approve_request(
        self,
        request_id: str,
        approver: str,
        duration_days: int = 365,
        conditions: dict = None
    ) -> dict:
        """Approve access request"""
        logger.info(f"Approving request {request_id}")

        # Get request details
        request = self._get_request_details(request_id)

        # Grant permissions
        self._grant_permissions(
            consumer=request['consumer_id'],
            product=request['product_name'],
            permissions=request['requested_permissions'],
            expires=datetime.now() + timedelta(days=duration_days)
        )

        # Update request status
        self._update_request_status(
            request_id=request_id,
            status='approved',
            approver=approver,
            approved_date=datetime.now()
        )

        # Send notification
        self._send_approval_notification(request, approver)

        # Log approval
        self._log_approval(request_id, approver, conditions)

        logger.info(f"✓ Request approved: {request_id}")

        return {
            "request_id": request_id,
            "status": "approved",
            "approver": approver,
            "expires": duration_days
        }

    def revoke_access(
        self,
        consumer_id: str,
        product_name: str,
        reason: str,
        revoked_by: str
    ) -> dict:
        """Revoke consumer access"""
        logger.info(f"Revoking access for {consumer_id}")

        # Remove permissions
        self._revoke_permissions(consumer_id, product_name)

        # Update records
        self._update_consumer_status(
            consumer_id=consumer_id,
            product_name=product_name,
            status='revoked',
            revoked_date=datetime.now(),
            revoked_by=revoked_by,
            revocation_reason=reason
        )

        # Send notification
        self._send_revocation_notification(consumer_id, reason)

        # Log revocation
        self._log_revocation(consumer_id, product_name, reason, revoked_by)

        logger.info(f"✓ Access revoked: {consumer_id}")

        return {
            "consumer_id": consumer_id,
            "status": "revoked",
            "revoked_by": revoked_by
        }

    def audit_access(self, product_name: str) -> dict:
        """Audit consumer access"""
        logger.info(f"Auditing access for {product_name}")

        # Get all consumers
        consumers = self._get_all_consumers(product_name)

        # Identify issues
        issues = {
            "expired_access": [],
            "inactive_consumers": [],
            "excessive_permissions": [],
            "missing_justification": []
        }

        for consumer in consumers:
            # Check expiration
            if consumer['expires'] < datetime.now():
                issues["expired_access"].append(consumer)

            # Check activity
            if consumer['last_access'] < datetime.now() - timedelta(days=90):
                issues["inactive_consumers"].append(consumer)

            # Check permissions
            if self._has_excessive_permissions(consumer):
                issues["excessive_permissions"].append(consumer)

            # Check justification
            if not consumer.get('justification'):
                issues["missing_justification"].append(consumer)

        # Generate report
        report = self._generate_audit_report(product_name, issues)

        return report

    def generate_usage_report(
        self,
        product_name: str,
        period_days: int = 30
    ) -> dict:
        """Generate consumer usage report"""
        query = f"""
            SELECT
                c.consumer_name,
                COUNT(DISTINCT u.query_id) as total_queries,
                SUM(u.bytes_scanned) / POW(1024, 3) as total_gb_scanned,
                AVG(u.execution_time_ms) / 1000 as avg_query_time_sec,
                MAX(u.query_time) as last_query_time
            FROM data_products.consumers c
            JOIN data_products.usage_logs u
              ON c.consumer_id = u.consumer_id
            WHERE c.product_name = '{product_name}'
              AND u.query_time >= CURRENT_DATE - INTERVAL {period_days} DAYS
            GROUP BY c.consumer_name
            ORDER BY total_queries DESC
        """

        results = self.client.sql_exec(query).fetchall()

        return {
            "product_name": product_name,
            "period_days": period_days,
            "total_consumers": len(results),
            "consumer_stats": results
        }

    def _grant_permissions(
        self,
        consumer: str,
        product: str,
        permissions: list,
        expires: datetime
    ):
        """Grant permissions to consumer"""
        # Implementation would use Unity Catalog grants
        pass

    def _revoke_permissions(self, consumer_id: str, product_name: str):
        """Revoke consumer permissions"""
        # Implementation would revoke Unity Catalog grants
        pass

    def _send_approval_notification(self, request: dict, approver: str):
        """Send approval notification to consumer"""
        # Implementation would send email/slack notification
        pass

    def _send_revocation_notification(self, consumer_id: str, reason: str):
        """Send revocation notification"""
        # Implementation would send notification
        pass


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("product_name")
    parser.add_argument("--action", choices=["list", "approve", "revoke", "audit", "report"])
    parser.add_argument("--consumer")
    parser.add_argument("--reason")

    args = parser.parse_args()

    manager = ConsumerAccessManager(
        workspace_url=os.getenv("DATABRICKS_HOST"),
        token=os.getenv("DATABRICKS_TOKEN")
    )

    if args.action == "list":
        requests = manager.list_pending_requests(args.product_name)
        print(f"Pending requests: {len(requests)}")
        for req in requests:
            print(f"  - {req['consumer_name']}: {req['justification']}")

    elif args.action == "approve":
        result = manager.approve_request(
            request_id=args.consumer,
            approver="current-user"
        )
        print(f"✓ Access approved for {result['request_id']}")

    elif args.action == "revoke":
        result = manager.revoke_access(
            consumer_id=args.consumer,
            product_name=args.product_name,
            reason=args.reason or "Access no longer required",
            revoked_by="current-user"
        )
        print(f"✓ Access revoked for {result['consumer_id']}")

    elif args.action == "audit":
        report = manager.audit_access(args.product_name)
        print(f"Audit Report:")
        print(f"  Expired access: {len(report['issues']['expired_access'])}")
        print(f"  Inactive consumers: {len(report['issues']['inactive_consumers'])}")

    elif args.action == "report":
        report = manager.generate_usage_report(args.product_name)
        print(f"Usage Report ({report['period_days']} days):")
        print(f"  Total consumers: {report['total_consumers']}")
```

## Consumer Lifecycle Management

### Access Request Form
```yaml
# Consumer Access Request
product_name: customer-360
consumer_info:
  name: John Doe
  email: john.doe@company.com
  business_unit: Marketing
  role: Data Analyst

access_details:
  justification: "Need customer data for Q1 campaign analysis and segmentation"
  use_cases:
    - Customer segmentation
    - Campaign targeting
  requested_permissions:
    - SELECT on customers table
    - SELECT on customer_metrics table
  duration_days: 365
  data_sensitivity_acknowledged: true

approvals:
  manager: jane.manager@company.com
  data_owner: data-team@company.com

compliance:
  training_completed: true
  policy_acknowledged: true
  nda_signed: true
```

### Automated Access Review
```sql
-- Quarterly access review
CREATE OR REPLACE PROCEDURE quarterly_access_review(product_name STRING)
AS
BEGIN
  -- Find consumers with no activity in 90 days
  DECLARE inactive_consumers ARRAY<STRING>;

  SET inactive_consumers = (
    SELECT COLLECT_LIST(consumer_id)
    FROM data_products.consumer_usage
    WHERE product_name = product_name
      AND last_access_date < CURRENT_DATE - INTERVAL 90 DAYS
  );

  -- Send review requests
  FOR consumer IN inactive_consumers DO
    CALL send_access_review_notification(consumer, product_name);
  END FOR;

  -- Generate review report
  INSERT INTO data_products.access_reviews
  SELECT
    product_name,
    CURRENT_DATE as review_date,
    COUNT(*) as total_consumers,
    SUM(CASE WHEN last_access_date < CURRENT_DATE - INTERVAL 90 DAYS THEN 1 ELSE 0 END) as inactive_count
  FROM data_products.consumer_usage
  WHERE product_name = product_name;
END;
```

## Monitoring and Analytics

### Consumer Analytics Dashboard
```sql
-- Top consumers by usage
SELECT
  consumer_name,
  COUNT(DISTINCT query_id) as query_count,
  SUM(bytes_scanned) / POW(1024, 3) as gb_scanned,
  AVG(execution_time_ms) as avg_time_ms,
  MAX(query_time) as last_query
FROM data_products.usage_logs
WHERE product_name = 'customer-360'
  AND query_time >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY consumer_name
ORDER BY query_count DESC
LIMIT 20;

-- Consumer growth over time
SELECT
  DATE_TRUNC('month', access_granted_date) as month,
  COUNT(*) as new_consumers,
  SUM(COUNT(*)) OVER (ORDER BY DATE_TRUNC('month', access_granted_date)) as cumulative_consumers
FROM data_products.consumer_access
WHERE product_name = 'customer-360'
GROUP BY DATE_TRUNC('month', access_granted_date)
ORDER BY month;

-- Access pattern analysis
SELECT
  HOUR(query_time) as hour_of_day,
  DAYOFWEEK(query_time) as day_of_week,
  COUNT(*) as query_count
FROM data_products.usage_logs
WHERE product_name = 'customer-360'
  AND query_time >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY HOUR(query_time), DAYOFWEEK(query_time)
ORDER BY query_count DESC;
```

## Best Practices

1. **Regular Reviews**: Conduct quarterly access reviews
2. **Least Privilege**: Grant minimum necessary permissions
3. **Time Limits**: Set expiration dates on all access grants
4. **Track Justification**: Require business justification
5. **Monitor Usage**: Track and analyze consumption patterns
6. **Automate Reviews**: Use automated workflows for renewals
7. **Audit Trails**: Maintain comprehensive audit logs
8. **Self-Service**: Enable self-service with approval workflows

## Security Considerations

1. **Approval Workflows**: Require manager and data owner approval
2. **Access Expiration**: Automatically revoke expired access
3. **Activity Monitoring**: Alert on unusual access patterns
4. **Audit Logging**: Log all access grants and revocations
5. **Compliance**: Verify training and policy acknowledgment
6. **Segregation of Duties**: Separate approval from granting

## Troubleshooting

**Issue**: Consumer cannot access after approval
**Solution**: Verify permissions applied, check Unity Catalog grants, validate token

**Issue**: Approval workflow not triggering
**Solution**: Check workflow configuration, verify email settings, validate approver groups

**Issue**: Usage metrics not updating
**Solution**: Verify system tables access, check data pipeline, refresh materialized views

## Related Commands

- `/databricks-engineering:create-data-product` - Create data product
- `/databricks-engineering:publish-data-product` - Publish product
- `/databricks-engineering:configure-delta-share` - Set up external sharing
- `/databricks-engineering:monitor-data-product` - Monitor product usage

---

**Last Updated**: 2024-12-31
**Version**: 1.0.0
**Category**: Access Management
**Prepared by**: Data Platform Team
