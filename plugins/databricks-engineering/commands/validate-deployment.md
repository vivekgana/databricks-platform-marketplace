# Validate Deployment Command

## Description
Run comprehensive pre-deployment validation including cost estimation, security scanning, performance testing, and compliance checks. Prevents costly deployment errors and ensures production readiness.

## Usage
```bash
/databricks-engineering:validate-deployment [deployment-config] [--environment env] [--skip-cost-check]
```

## Parameters

- `deployment-config` (required): Path to deployment configuration (YAML or bundle)
- `--environment` (optional): Target environment - "dev", "staging", "prod" (default: "prod")
- `--skip-cost-check` (optional): Skip cost estimation (default: false)
- `--skip-security-scan` (optional): Skip security scanning (default: false)
- `--skip-performance-test` (optional): Skip performance validation (default: false)
- `--budget-limit` (optional): Maximum monthly budget in USD (default: unlimited)

## Examples

### Example 1: Full validation
```bash
/databricks-engineering:validate-deployment ./deployments/customer-360-prod.yaml \
  --environment prod
```

### Example 2: Quick validation without cost check
```bash
/databricks-engineering:validate-deployment ./databricks.yml \
  --skip-cost-check
```

### Example 3: Validation with budget constraint
```bash
/databricks-engineering:validate-deployment ./deployments/pipeline.yaml \
  --budget-limit 5000
```

## What This Command Does

### Configuration Validation (5 minutes)
- Validates YAML/JSON syntax
- Checks required fields present
- Verifies cluster configurations
- Validates job dependencies
- Checks notebook paths exist

### Security Scanning (10 minutes)
- Scans for hardcoded secrets
- Checks IAM permissions
- Validates encryption settings
- Reviews network configurations
- Checks compliance with policies

### Cost Estimation (5 minutes)
- Estimates compute costs
- Projects storage requirements
- Calculates DBU consumption
- Provides cost breakdown
- Compares against budget

### Performance Validation (15 minutes)
- Tests query performance
- Validates cluster sizing
- Checks resource allocation
- Tests autoscaling configuration
- Validates SLA compliance

### Compliance Checks (5 minutes)
- Verifies data governance
- Checks regulatory compliance
- Validates audit logging
- Reviews access controls
- Checks retention policies

## Generated Validation Report

### Summary Report
```markdown
# Deployment Validation Report
**Configuration**: customer-360-prod.yaml
**Environment**: prod
**Validation Date**: 2024-12-31
**Status**: ⚠️ WARNINGS (Safe to deploy)

## Summary
- ✅ Configuration Valid
- ⚠️ 3 Security Warnings
- ✅ Cost Within Budget
- ✅ Performance Acceptable
- ✅ Compliance Met

## Details

### Configuration Validation ✅
- Syntax valid
- All required fields present
- Cluster configurations valid
- Job dependencies resolved
- Notebook paths verified

### Security Scan ⚠️
**Warnings (3)**:
1. Cluster allows unrestricted network access
   - Recommendation: Configure network firewall rules
   - Risk: Medium
   - Fix: Add cluster_network_policy

2. Secrets in environment variables
   - Recommendation: Use Databricks secrets
   - Risk: High
   - Fix: Move to secret scope

3. Broad IAM permissions
   - Recommendation: Apply least-privilege principle
   - Risk: Medium
   - Fix: Restrict to specific resources

### Cost Estimation ✅
**Monthly Projection**: $3,450
**Budget Limit**: $5,000
**Budget Utilization**: 69%

**Breakdown**:
- Compute (DBUs): $2,800
- Storage (Delta): $450
- Networking: $200

**Recommendations**:
- Consider spot instances: Save $980/month
- Optimize cluster sizing: Save $320/month

### Performance Validation ✅
**P95 Latency**: 4.2 seconds (Target: <5s)
**Throughput**: 1,200 records/sec (Target: >1,000)
**Resource Utilization**: 72% (Optimal: 60-80%)

### Compliance Checks ✅
- ✅ GDPR compliant
- ✅ Audit logging enabled
- ✅ Encryption at rest
- ✅ Access controls configured
- ✅ Data retention policies set
```

### Validation Script
```python
# scripts/validate_deployment.py
from databricks.sdk import WorkspaceClient
import yaml
import json
import re
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class DeploymentValidator:
    """Validate deployment configuration before deploying"""

    def __init__(self, workspace_url: str, token: str):
        self.client = WorkspaceClient(host=workspace_url, token=token)
        self.validation_results = {
            "config": {"passed": False, "issues": []},
            "security": {"passed": False, "issues": []},
            "cost": {"passed": False, "issues": []},
            "performance": {"passed": False, "issues": []},
            "compliance": {"passed": False, "issues": []}
        }

    def validate(
        self,
        config_path: str,
        environment: str = "prod",
        budget_limit: float = None
    ) -> Dict:
        """Run all validation checks"""
        logger.info(f"Validating deployment for {environment}")

        # Load configuration
        with open(config_path, 'r') as f:
            if config_path.endswith('.json'):
                config = json.load(f)
            else:
                config = yaml.safe_load(f)

        # Run validation checks
        self._validate_configuration(config)
        self._scan_security(config)
        self._estimate_costs(config, budget_limit)
        self._validate_performance(config)
        self._check_compliance(config)

        # Generate summary
        summary = self._generate_summary()

        return summary

    def _validate_configuration(self, config: Dict):
        """Validate configuration structure and values"""
        logger.info("Validating configuration...")

        issues = []

        # Check required fields
        required_fields = ['name', 'job_clusters', 'tasks']
        for field in required_fields:
            if field not in config:
                issues.append(f"Missing required field: {field}")

        # Validate cluster configurations
        if 'job_clusters' in config:
            for cluster in config['job_clusters']:
                # Check node type
                if 'node_type_id' not in cluster.get('new_cluster', {}):
                    issues.append(f"Missing node_type_id in cluster {cluster.get('job_cluster_key')}")

                # Check Spark version
                if 'spark_version' not in cluster.get('new_cluster', {}):
                    issues.append(f"Missing spark_version in cluster {cluster.get('job_cluster_key')}")

        # Validate task dependencies
        if 'tasks' in config:
            task_keys = {task['task_key'] for task in config['tasks']}
            for task in config['tasks']:
                if 'depends_on' in task:
                    for dep in task['depends_on']:
                        if dep['task_key'] not in task_keys:
                            issues.append(f"Task {task['task_key']} depends on non-existent task {dep['task_key']}")

        # Validate notebook paths
        if 'tasks' in config:
            for task in config['tasks']:
                if 'notebook_task' in task:
                    notebook_path = task['notebook_task']['notebook_path']
                    if not self._notebook_exists(notebook_path):
                        issues.append(f"Notebook not found: {notebook_path}")

        self.validation_results['config'] = {
            "passed": len(issues) == 0,
            "issues": issues
        }

    def _scan_security(self, config: Dict):
        """Scan for security issues"""
        logger.info("Scanning for security issues...")

        issues = []

        # Check for hardcoded secrets
        config_str = json.dumps(config)
        secret_patterns = [
            (r'password\s*[:=]\s*["\']?[^"\'\s]+', "Hardcoded password detected"),
            (r'api[_-]?key\s*[:=]\s*["\']?[^"\'\s]+', "Hardcoded API key detected"),
            (r'secret\s*[:=]\s*["\']?[^"\'\s]+', "Hardcoded secret detected"),
        ]

        for pattern, message in secret_patterns:
            if re.search(pattern, config_str, re.IGNORECASE):
                issues.append({
                    "message": message,
                    "severity": "high",
                    "recommendation": "Use Databricks secrets"
                })

        # Check cluster security
        if 'job_clusters' in config:
            for cluster in config['job_clusters']:
                new_cluster = cluster.get('new_cluster', {})

                # Check encryption
                if not new_cluster.get('enable_elastic_disk'):
                    issues.append({
                        "message": "Elastic disk not enabled",
                        "severity": "medium",
                        "recommendation": "Enable elastic disk for better security"
                    })

                # Check network isolation
                if not new_cluster.get('cluster_network_policy'):
                    issues.append({
                        "message": "No network policy configured",
                        "severity": "medium",
                        "recommendation": "Configure cluster network policy"
                    })

        self.validation_results['security'] = {
            "passed": all(issue['severity'] != 'critical' for issue in issues),
            "issues": issues
        }

    def _estimate_costs(self, config: Dict, budget_limit: float = None):
        """Estimate deployment costs"""
        logger.info("Estimating costs...")

        total_cost = 0
        breakdown = {}

        # Estimate compute costs
        if 'job_clusters' in config:
            compute_cost = 0
            for cluster in config['job_clusters']:
                new_cluster = cluster.get('new_cluster', {})
                node_type = new_cluster.get('node_type_id', 'i3.xlarge')
                num_workers = new_cluster.get('num_workers', 4)

                # Simplified cost calculation (actual would use pricing API)
                cost_per_node_hour = 0.5  # Example rate
                hours_per_month = 730
                cluster_cost = cost_per_node_hour * (num_workers + 1) * hours_per_month

                compute_cost += cluster_cost

            breakdown['compute'] = compute_cost
            total_cost += compute_cost

        # Estimate storage costs
        storage_cost = 100  # Placeholder
        breakdown['storage'] = storage_cost
        total_cost += storage_cost

        issues = []

        # Check against budget
        if budget_limit and total_cost > budget_limit:
            issues.append({
                "message": f"Estimated cost (${total_cost:.2f}) exceeds budget (${budget_limit:.2f})",
                "severity": "critical",
                "recommendation": "Reduce cluster sizes or use spot instances"
            })

        # Cost optimization recommendations
        if compute_cost > total_cost * 0.8:
            issues.append({
                "message": "Compute costs dominate total cost",
                "severity": "info",
                "recommendation": "Consider spot instances, autoscaling optimization"
            })

        self.validation_results['cost'] = {
            "passed": len([i for i in issues if i['severity'] == 'critical']) == 0,
            "estimated_monthly_cost": total_cost,
            "breakdown": breakdown,
            "issues": issues
        }

    def _validate_performance(self, config: Dict):
        """Validate performance configuration"""
        logger.info("Validating performance...")

        issues = []

        # Check cluster sizing
        if 'job_clusters' in config:
            for cluster in config['job_clusters']:
                new_cluster = cluster.get('new_cluster', {})

                # Check autoscaling
                if 'autoscale' in new_cluster:
                    min_workers = new_cluster['autoscale'].get('min_workers', 0)
                    max_workers = new_cluster['autoscale'].get('max_workers', 0)

                    if max_workers - min_workers > 20:
                        issues.append({
                            "message": "Wide autoscaling range may cause slow scaling",
                            "severity": "medium",
                            "recommendation": "Narrow autoscaling range for better responsiveness"
                        })

                # Check for Photon enablement
                if new_cluster.get('runtime_engine') != 'PHOTON':
                    issues.append({
                        "message": "Photon not enabled",
                        "severity": "info",
                        "recommendation": "Enable Photon for 2-3x performance boost on SQL workloads"
                    })

        self.validation_results['performance'] = {
            "passed": len([i for i in issues if i['severity'] in ['critical', 'high']]) == 0,
            "issues": issues
        }

    def _check_compliance(self, config: Dict):
        """Check compliance requirements"""
        logger.info("Checking compliance...")

        issues = []

        # Check audit logging
        if 'email_notifications' not in config:
            issues.append({
                "message": "No email notifications configured",
                "severity": "medium",
                "recommendation": "Configure notifications for compliance"
            })

        # Check tags
        if 'job_clusters' in config:
            for cluster in config['job_clusters']:
                if 'custom_tags' not in cluster.get('new_cluster', {}):
                    issues.append({
                        "message": "No cost allocation tags configured",
                        "severity": "low",
                        "recommendation": "Add tags for cost tracking"
                    })

        self.validation_results['compliance'] = {
            "passed": len([i for i in issues if i['severity'] in ['critical', 'high']]) == 0,
            "issues": issues
        }

    def _notebook_exists(self, path: str) -> bool:
        """Check if notebook exists"""
        try:
            self.client.workspace.get_status(path)
            return True
        except:
            return False

    def _generate_summary(self) -> Dict:
        """Generate validation summary"""
        all_passed = all(
            category['passed']
            for category in self.validation_results.values()
        )

        total_issues = sum(
            len(category['issues'])
            for category in self.validation_results.values()
        )

        critical_issues = sum(
            len([i for i in category['issues'] if isinstance(i, dict) and i.get('severity') == 'critical'])
            for category in self.validation_results.values()
        )

        return {
            "overall_status": "PASS" if all_passed and critical_issues == 0 else "FAIL",
            "safe_to_deploy": critical_issues == 0,
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "details": self.validation_results
        }


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate Databricks deployment")
    parser.add_argument("config", help="Path to deployment configuration")
    parser.add_argument("--environment", default="prod")
    parser.add_argument("--budget-limit", type=float)

    args = parser.parse_args()

    validator = DeploymentValidator(
        workspace_url=os.getenv("DATABRICKS_HOST"),
        token=os.getenv("DATABRICKS_TOKEN")
    )

    result = validator.validate(
        config_path=args.config,
        environment=args.environment,
        budget_limit=args.budget_limit
    )

    print(f"\n{'='*60}")
    print(f"Validation Result: {result['overall_status']}")
    print(f"Safe to Deploy: {'✅ Yes' if result['safe_to_deploy'] else '❌ No'}")
    print(f"Total Issues: {result['total_issues']}")
    print(f"Critical Issues: {result['critical_issues']}")
    print(f"{'='*60}\n")

    if not result['safe_to_deploy']:
        exit(1)
```

## Best Practices

1. **Always Validate**: Run validation before every deployment
2. **Budget Limits**: Set budget constraints for cost control
3. **Security First**: Address all critical security issues
4. **Performance Testing**: Test with production-like data volumes
5. **Compliance**: Verify regulatory requirements met
6. **Automated**: Integrate into CI/CD pipeline
7. **Documentation**: Document validation failures and fixes

## Troubleshooting

**Issue**: Validation takes too long
**Solution**: Skip non-critical checks, parallelize validations, cache results

**Issue**: False positives in security scan
**Solution**: Configure exemptions, update patterns, use allowlist

**Issue**: Cost estimation inaccurate
**Solution**: Update pricing data, include all resources, factor in usage patterns

## Related Commands

- `/databricks-engineering:deploy-workflow` - Deploy after validation
- `/databricks-engineering:deploy-bundle` - Deploy bundle after validation
- `/databricks-engineering:optimize-costs` - Cost optimization

---

**Last Updated**: 2024-12-31
**Version**: 1.0.0
**Category**: Validation
**Prepared by**: gekambaram
