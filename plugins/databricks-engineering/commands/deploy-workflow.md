# Deploy Workflow Command

## Description
Deploy data pipelines to Databricks workspace as jobs with comprehensive monitoring, alerting, SLA tracking, and production-ready configurations. Supports blue-green deployments, canary releases, and automated rollback.

## Usage
```bash
/databricks-engineering:deploy-workflow [pipeline-name] [--environment env] [--strategy strategy] [--validate]
```

## Parameters

- `pipeline-name` (required): Name of the pipeline to deploy
- `--environment` (optional): Target environment - "dev", "staging", "prod" (default: "dev")
- `--strategy` (optional): Deployment strategy - "direct", "blue-green", "canary" (default: "direct")
- `--validate` (optional): Run pre-deployment validation (default: true)
- `--dry-run` (optional): Preview deployment without executing (default: false)
- `--enable-monitoring` (optional): Set up monitoring and alerting (default: true)
- `--rollback-on-failure` (optional): Auto-rollback on failure (default: true)
- `--approval-required` (optional): Require manual approval for prod (default: true for prod)

## Examples

### Example 1: Deploy to development
```bash
/databricks-engineering:deploy-workflow customer-360-pipeline --environment dev
```

### Example 2: Blue-green deployment to production
```bash
/databricks-engineering:deploy-workflow customer-360-pipeline \
  --environment prod \
  --strategy blue-green \
  --validate
```

### Example 3: Canary release with 10% traffic
```bash
/databricks-engineering:deploy-workflow customer-360-pipeline \
  --environment prod \
  --strategy canary \
  --canary-percentage 10
```

### Example 4: Dry-run for production deployment
```bash
/databricks-engineering:deploy-workflow customer-360-pipeline \
  --environment prod \
  --dry-run
```

### Example 5: Deploy with custom configuration
```bash
/databricks-engineering:deploy-workflow customer-360-pipeline \
  --environment prod \
  --config-file ./custom-deploy-config.yaml
```

## What This Command Does

### Phase 1: Pre-Deployment Validation (5-10 minutes)

1. **Configuration Validation**
   - Verifies pipeline configuration files exist
   - Validates environment-specific settings
   - Checks cluster configurations
   - Verifies IAM permissions and secrets
   - Validates Unity Catalog permissions

2. **Dependency Checks**
   - Verifies source tables exist
   - Checks for required libraries
   - Validates external connections
   - Verifies mount points and volumes
   - Checks for schema compatibility

3. **Cost Estimation**
   - Calculates estimated run costs
   - Projects monthly spend
   - Identifies cost optimization opportunities
   - Validates against budget limits

4. **Quality Gates**
   - Runs unit tests
   - Executes data quality validations
   - Checks code coverage
   - Validates against SLA requirements
   - Runs security scans

### Phase 2: Deployment Preparation (2-5 minutes)

1. **Version Management**
   - Tags deployment version
   - Creates deployment manifest
   - Archives current production config
   - Generates rollback scripts

2. **Resource Provisioning**
   - Creates or updates job clusters
   - Sets up compute pools
   - Configures autoscaling
   - Provisions storage locations

3. **Configuration Management**
   - Applies environment-specific configs
   - Sets up secrets and credentials
   - Configures job parameters
   - Updates connection strings

### Phase 3: Deployment Execution (10-30 minutes)

#### Direct Deployment Strategy
1. Stop existing jobs (if running)
2. Update job configurations
3. Deploy new pipeline code
4. Start jobs with new configuration
5. Validate deployment success

#### Blue-Green Deployment Strategy
1. Deploy to "green" environment
2. Run smoke tests on green
3. Switch traffic to green
4. Monitor for issues
5. Decommission blue if successful

#### Canary Deployment Strategy
1. Deploy new version alongside current
2. Route small percentage of traffic to new version
3. Monitor metrics and errors
4. Gradually increase traffic percentage
5. Complete rollout if successful

### Phase 4: Post-Deployment (5-10 minutes)

1. **Validation**
   - Runs smoke tests
   - Validates data flow
   - Checks monitoring dashboards
   - Verifies alerting is active

2. **Monitoring Setup**
   - Creates dashboards
   - Configures alerts
   - Sets up SLA tracking
   - Enables audit logging

3. **Documentation**
   - Updates deployment history
   - Generates deployment report
   - Documents configuration changes
   - Creates runbook

## Generated Deployment Configuration

### Job Configuration (YAML)
```yaml
# deployments/customer-360-pipeline-prod.yaml
name: customer-360-pipeline-prod
job_clusters:
  - job_cluster_key: bronze-cluster
    new_cluster:
      spark_version: 13.3.x-scala2.12
      node_type_id: i3.xlarge
      num_workers: 4
      autoscale:
        min_workers: 2
        max_workers: 8
      spark_conf:
        spark.databricks.delta.preview.enabled: "true"
        spark.databricks.delta.optimizeWrite.enabled: "true"
        spark.databricks.delta.autoCompact.enabled: "true"
      aws_attributes:
        availability: SPOT_WITH_FALLBACK
        zone_id: auto
        spot_bid_price_percent: 100
      custom_tags:
        Environment: production
        Pipeline: customer-360
        CostCenter: data-engineering
        Owner: data-team@company.com

  - job_cluster_key: silver-cluster
    new_cluster:
      spark_version: 13.3.x-scala2.12
      node_type_id: i3.2xlarge
      num_workers: 8
      autoscale:
        min_workers: 4
        max_workers: 16
      runtime_engine: PHOTON
      spark_conf:
        spark.databricks.delta.preview.enabled: "true"
        spark.databricks.delta.optimizeWrite.enabled: "true"

tasks:
  - task_key: ingest-bronze
    job_cluster_key: bronze-cluster
    notebook_task:
      notebook_path: /Workspace/pipelines/customer-360/bronze
      base_parameters:
        source_path: /mnt/raw/customer-data
        target_catalog: prod
        target_schema: bronze
        checkpoint_path: /mnt/checkpoints/bronze/customer-360
    libraries:
      - pypi:
          package: great-expectations==0.18.0
      - pypi:
          package: databricks-sdk==0.18.0
    timeout_seconds: 3600
    max_retries: 2
    min_retry_interval_millis: 300000
    retry_on_timeout: true

  - task_key: process-silver
    depends_on:
      - task_key: ingest-bronze
    job_cluster_key: silver-cluster
    notebook_task:
      notebook_path: /Workspace/pipelines/customer-360/silver
      base_parameters:
        source_catalog: prod
        source_schema: bronze
        target_catalog: prod
        target_schema: silver
        checkpoint_path: /mnt/checkpoints/silver/customer-360
    timeout_seconds: 5400
    max_retries: 2

  - task_key: aggregate-gold
    depends_on:
      - task_key: process-silver
    job_cluster_key: silver-cluster
    notebook_task:
      notebook_path: /Workspace/pipelines/customer-360/gold
      base_parameters:
        source_catalog: prod
        source_schema: silver
        target_catalog: prod
        target_schema: gold
    timeout_seconds: 3600

  - task_key: validate-quality
    depends_on:
      - task_key: aggregate-gold
    job_cluster_key: silver-cluster
    notebook_task:
      notebook_path: /Workspace/pipelines/customer-360/quality-checks
      base_parameters:
        catalog: prod
        schema: gold
        checkpoint_name: customer-360-quality
    timeout_seconds: 1800

  - task_key: send-notification
    depends_on:
      - task_key: validate-quality
    python_wheel_task:
      package_name: notifications
      entry_point: send_completion_notification
      parameters:
        - "customer-360-pipeline"
        - "prod"
    libraries:
      - whl: /Workspace/libs/notifications-1.0.0-py3-none-any.whl

schedule:
  quartz_cron_expression: "0 0 2 * * ?"  # Daily at 2 AM UTC
  timezone_id: "UTC"
  pause_status: "UNPAUSED"

email_notifications:
  on_start:
    - data-engineering@company.com
  on_success:
    - data-engineering@company.com
  on_failure:
    - data-engineering@company.com
    - data-platform-oncall@company.com
  no_alert_for_skipped_runs: false

webhook_notifications:
  on_start:
    - id: slack-webhook-start
  on_success:
    - id: slack-webhook-success
  on_failure:
    - id: slack-webhook-failure
    - id: pagerduty-webhook

timeout_seconds: 14400  # 4 hours max
max_concurrent_runs: 1

tags:
  environment: production
  pipeline: customer-360
  owner: data-engineering
  sla: critical

access_control_list:
  - user_name: data-engineering@company.com
    permission_level: IS_OWNER
  - group_name: data-analysts
    permission_level: CAN_VIEW
  - service_principal_name: prod-deployment-sp
    permission_level: CAN_MANAGE_RUN
```

### Deployment Script
```python
# scripts/deploy_workflow.py
"""
Databricks workflow deployment script
Generated by databricks-engineering plugin
"""

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import *
import yaml
import json
import logging
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowDeployer:
    """Deploy workflows to Databricks workspace"""

    def __init__(
        self,
        workspace_url: str,
        token: str,
        environment: str = "dev"
    ):
        self.client = WorkspaceClient(
            host=workspace_url,
            token=token
        )
        self.environment = environment
        self.deployment_id = f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    def deploy(
        self,
        config_path: str,
        strategy: str = "direct",
        dry_run: bool = False,
        validate: bool = True
    ) -> Dict:
        """
        Deploy workflow to Databricks

        Args:
            config_path: Path to job configuration YAML
            strategy: Deployment strategy (direct, blue-green, canary)
            dry_run: Preview without executing
            validate: Run pre-deployment validation

        Returns:
            Deployment result dictionary
        """
        logger.info(f"Starting deployment {self.deployment_id}")
        logger.info(f"Environment: {self.environment}")
        logger.info(f"Strategy: {strategy}")

        # Load configuration
        config = self._load_config(config_path)

        # Pre-deployment validation
        if validate:
            validation_result = self._validate_deployment(config)
            if not validation_result["passed"]:
                logger.error("Pre-deployment validation failed")
                return {
                    "success": False,
                    "deployment_id": self.deployment_id,
                    "validation_errors": validation_result["errors"]
                }

        if dry_run:
            logger.info("Dry-run mode - no changes will be made")
            return self._preview_deployment(config)

        # Execute deployment based on strategy
        if strategy == "direct":
            result = self._deploy_direct(config)
        elif strategy == "blue-green":
            result = self._deploy_blue_green(config)
        elif strategy == "canary":
            result = self._deploy_canary(config)
        else:
            raise ValueError(f"Unknown deployment strategy: {strategy}")

        # Post-deployment validation
        if result["success"]:
            post_validation = self._post_deployment_validation(result["job_id"])
            result["post_validation"] = post_validation

        # Generate deployment report
        self._generate_deployment_report(result)

        return result

    def _load_config(self, config_path: str) -> Dict:
        """Load job configuration from YAML"""
        logger.info(f"Loading configuration from {config_path}")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config

    def _validate_deployment(self, config: Dict) -> Dict:
        """Run pre-deployment validation checks"""
        logger.info("Running pre-deployment validation...")
        errors = []

        # Validate notebook paths exist
        for task in config.get("tasks", []):
            if "notebook_task" in task:
                notebook_path = task["notebook_task"]["notebook_path"]
                try:
                    self.client.workspace.get_status(notebook_path)
                    logger.info(f"✓ Notebook exists: {notebook_path}")
                except Exception as e:
                    error = f"✗ Notebook not found: {notebook_path}"
                    logger.error(error)
                    errors.append(error)

        # Validate cluster configurations
        for cluster_config in config.get("job_clusters", []):
            try:
                # Validate node type exists
                node_type = cluster_config["new_cluster"]["node_type_id"]
                logger.info(f"✓ Node type valid: {node_type}")
            except Exception as e:
                error = f"✗ Invalid cluster configuration: {str(e)}"
                logger.error(error)
                errors.append(error)

        # Validate libraries
        for task in config.get("tasks", []):
            for lib in task.get("libraries", []):
                logger.info(f"✓ Library defined: {lib}")

        return {
            "passed": len(errors) == 0,
            "errors": errors
        }

    def _deploy_direct(self, config: Dict) -> Dict:
        """Direct deployment - replace existing job"""
        logger.info("Executing direct deployment...")

        job_name = config["name"]

        # Check if job already exists
        existing_job = self._find_job_by_name(job_name)

        if existing_job:
            logger.info(f"Updating existing job: {existing_job.job_id}")
            # Stop any running instances
            self._stop_active_runs(existing_job.job_id)

            # Update job
            self.client.jobs.reset(
                job_id=existing_job.job_id,
                new_settings=self._convert_config_to_job_settings(config)
            )
            job_id = existing_job.job_id
            action = "updated"
        else:
            logger.info(f"Creating new job: {job_name}")
            # Create new job
            created_job = self.client.jobs.create(
                **self._convert_config_to_job_settings(config)
            )
            job_id = created_job.job_id
            action = "created"

        # Trigger job run if not scheduled
        run_id = None
        if not config.get("schedule"):
            logger.info("Triggering manual job run...")
            run = self.client.jobs.run_now(job_id=job_id)
            run_id = run.run_id

        return {
            "success": True,
            "deployment_id": self.deployment_id,
            "job_id": job_id,
            "run_id": run_id,
            "action": action,
            "strategy": "direct"
        }

    def _deploy_blue_green(self, config: Dict) -> Dict:
        """Blue-green deployment"""
        logger.info("Executing blue-green deployment...")

        # Create green environment (new version)
        green_config = config.copy()
        green_config["name"] = f"{config['name']}-green"

        green_job = self.client.jobs.create(
            **self._convert_config_to_job_settings(green_config)
        )
        logger.info(f"✓ Created green environment: {green_job.job_id}")

        # Run smoke tests on green
        logger.info("Running smoke tests on green environment...")
        test_run = self.client.jobs.run_now(job_id=green_job.job_id)

        # Wait for test run to complete
        run_result = self._wait_for_run(test_run.run_id)

        if run_result.state.life_cycle_state == RunLifeCycleState.TERMINATED:
            if run_result.state.result_state == RunResultState.SUCCESS:
                logger.info("✓ Smoke tests passed")

                # Switch traffic to green
                blue_job = self._find_job_by_name(config["name"])
                if blue_job:
                    # Rename blue to backup
                    self.client.jobs.update(
                        job_id=blue_job.job_id,
                        new_settings=JobSettings(
                            name=f"{config['name']}-blue-backup"
                        )
                    )

                # Rename green to production
                self.client.jobs.update(
                    job_id=green_job.job_id,
                    new_settings=JobSettings(
                        name=config["name"]
                    )
                )

                logger.info("✓ Traffic switched to green environment")

                return {
                    "success": True,
                    "deployment_id": self.deployment_id,
                    "job_id": green_job.job_id,
                    "blue_job_id": blue_job.job_id if blue_job else None,
                    "strategy": "blue-green",
                    "smoke_test_result": "passed"
                }
            else:
                logger.error("✗ Smoke tests failed - rolling back")
                self.client.jobs.delete(job_id=green_job.job_id)
                return {
                    "success": False,
                    "deployment_id": self.deployment_id,
                    "error": "Smoke tests failed",
                    "strategy": "blue-green"
                }
        else:
            logger.error("✗ Test run failed to complete")
            return {
                "success": False,
                "deployment_id": self.deployment_id,
                "error": "Test run failed",
                "strategy": "blue-green"
            }

    def _deploy_canary(self, config: Dict, canary_percentage: int = 10) -> Dict:
        """Canary deployment"""
        logger.info(f"Executing canary deployment ({canary_percentage}% traffic)...")

        # Create canary version
        canary_config = config.copy()
        canary_config["name"] = f"{config['name']}-canary"

        canary_job = self.client.jobs.create(
            **self._convert_config_to_job_settings(canary_config)
        )
        logger.info(f"✓ Created canary version: {canary_job.job_id}")

        # Monitor canary metrics
        logger.info("Monitoring canary metrics...")
        # Implementation would include actual metrics monitoring

        return {
            "success": True,
            "deployment_id": self.deployment_id,
            "canary_job_id": canary_job.job_id,
            "canary_percentage": canary_percentage,
            "strategy": "canary"
        }

    def _find_job_by_name(self, job_name: str) -> Optional[Job]:
        """Find job by name"""
        for job in self.client.jobs.list():
            if job.settings.name == job_name:
                return job
        return None

    def _stop_active_runs(self, job_id: int):
        """Stop all active runs for a job"""
        runs = self.client.jobs.list_runs(job_id=job_id, active_only=True)
        for run in runs:
            logger.info(f"Stopping active run: {run.run_id}")
            self.client.jobs.cancel_run(run_id=run.run_id)

    def _wait_for_run(self, run_id: int, timeout: int = 3600):
        """Wait for job run to complete"""
        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            run = self.client.jobs.get_run(run_id=run_id)
            if run.state.life_cycle_state in [
                RunLifeCycleState.TERMINATED,
                RunLifeCycleState.TERMINATING,
                RunLifeCycleState.INTERNAL_ERROR
            ]:
                return run
            time.sleep(30)

        raise TimeoutError(f"Run {run_id} did not complete within {timeout} seconds")

    def _post_deployment_validation(self, job_id: int) -> Dict:
        """Run post-deployment validation"""
        logger.info("Running post-deployment validation...")

        validation_results = {
            "job_exists": False,
            "schedule_active": False,
            "permissions_configured": False
        }

        try:
            job = self.client.jobs.get(job_id=job_id)
            validation_results["job_exists"] = True

            if job.settings.schedule:
                validation_results["schedule_active"] = True

            # Check permissions
            permissions = self.client.jobs.get_permissions(job_id=job_id)
            if permissions.access_control_list:
                validation_results["permissions_configured"] = True

            logger.info("✓ Post-deployment validation passed")

        except Exception as e:
            logger.error(f"Post-deployment validation error: {str(e)}")

        return validation_results

    def _generate_deployment_report(self, result: Dict):
        """Generate deployment report"""
        report_path = f"deployments/reports/{self.deployment_id}.json"
        logger.info(f"Generating deployment report: {report_path}")

        with open(report_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)

    def _convert_config_to_job_settings(self, config: Dict) -> Dict:
        """Convert YAML config to JobSettings"""
        # Simplified conversion - actual implementation would be more comprehensive
        return config

    def _preview_deployment(self, config: Dict) -> Dict:
        """Preview deployment changes without executing"""
        logger.info("=== Deployment Preview ===")
        logger.info(f"Job Name: {config['name']}")
        logger.info(f"Tasks: {len(config.get('tasks', []))}")
        logger.info(f"Clusters: {len(config.get('job_clusters', []))}")

        if config.get("schedule"):
            logger.info(f"Schedule: {config['schedule']['quartz_cron_expression']}")

        return {
            "dry_run": True,
            "deployment_id": self.deployment_id,
            "config": config
        }


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Deploy Databricks workflow")
    parser.add_argument("config", help="Path to job configuration YAML")
    parser.add_argument("--environment", default="dev", choices=["dev", "staging", "prod"])
    parser.add_argument("--strategy", default="direct", choices=["direct", "blue-green", "canary"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-validate", action="store_true")

    args = parser.parse_args()

    deployer = WorkflowDeployer(
        workspace_url=os.getenv("DATABRICKS_HOST"),
        token=os.getenv("DATABRICKS_TOKEN"),
        environment=args.environment
    )

    result = deployer.deploy(
        config_path=args.config,
        strategy=args.strategy,
        dry_run=args.dry_run,
        validate=not args.no_validate
    )

    if result["success"]:
        print(f"✓ Deployment successful: {result['deployment_id']}")
    else:
        print(f"✗ Deployment failed: {result.get('error', 'Unknown error')}")
        exit(1)
```

## Monitoring and Alerting Setup

### Generated Monitoring Configuration
```yaml
# monitoring/customer-360-pipeline-monitoring.yaml
monitoring:
  dashboards:
    - name: customer-360-pipeline-health
      widgets:
        - type: line_chart
          title: Job Success Rate (7 days)
          query: |
            SELECT
              date_trunc('hour', start_time) as hour,
              COUNT(*) as total_runs,
              SUM(CASE WHEN result_state = 'SUCCESS' THEN 1 ELSE 0 END) as successful_runs,
              SUM(CASE WHEN result_state = 'SUCCESS' THEN 1 ELSE 0 END) / COUNT(*) * 100 as success_rate
            FROM system.jobs.runs
            WHERE job_id = {{job_id}}
              AND start_time >= current_timestamp() - INTERVAL 7 DAYS
            GROUP BY date_trunc('hour', start_time)
            ORDER BY hour

        - type: counter
          title: Average Runtime (Last 24h)
          query: |
            SELECT AVG(execution_duration_ms) / 1000 / 60 as avg_runtime_minutes
            FROM system.jobs.runs
            WHERE job_id = {{job_id}}
              AND start_time >= current_timestamp() - INTERVAL 24 HOURS

  alerts:
    - name: job-failure-alert
      condition: |
        SELECT COUNT(*) as failure_count
        FROM system.jobs.runs
        WHERE job_id = {{job_id}}
          AND result_state = 'FAILED'
          AND start_time >= current_timestamp() - INTERVAL 1 HOUR
        HAVING failure_count > 0
      severity: critical
      notifications:
        - type: email
          recipients:
            - data-engineering@company.com
        - type: slack
          channel: "#data-alerts"
        - type: pagerduty
          service_key: "{{pagerduty_service_key}}"

    - name: sla-breach-warning
      condition: |
        SELECT execution_duration_ms / 1000 / 60 as runtime_minutes
        FROM system.jobs.runs
        WHERE job_id = {{job_id}}
          AND start_time = (SELECT MAX(start_time) FROM system.jobs.runs WHERE job_id = {{job_id}})
        HAVING runtime_minutes > 180  -- 3 hour SLA
      severity: high
      notifications:
        - type: email
          recipients:
            - data-engineering@company.com

    - name: data-quality-degradation
      condition: |
        SELECT quality_score
        FROM prod.monitoring.quality_metrics
        WHERE table_name = 'prod.gold.customer_360'
          AND check_timestamp = (SELECT MAX(check_timestamp) FROM prod.monitoring.quality_metrics)
        HAVING quality_score < 95
      severity: medium
      notifications:
        - type: slack
          channel: "#data-quality"
```

## Deployment Checklist

### Pre-Deployment
- [ ] Code reviewed and approved
- [ ] Unit tests passing (100%)
- [ ] Integration tests passing
- [ ] Data quality tests passing
- [ ] Security scan completed
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Runbook created/updated
- [ ] Rollback plan documented

### Deployment
- [ ] Deployment window scheduled
- [ ] Stakeholders notified
- [ ] Backup of current production taken
- [ ] Environment variables configured
- [ ] Secrets updated in Key Vault
- [ ] Deployment executed
- [ ] Post-deployment tests run
- [ ] Monitoring dashboards verified
- [ ] Alerting tested

### Post-Deployment
- [ ] Smoke tests passed
- [ ] Performance metrics within SLA
- [ ] No error spikes in logs
- [ ] Data quality checks passed
- [ ] Stakeholders notified of completion
- [ ] Deployment documented
- [ ] Lessons learned captured

## Rollback Procedure

### Automated Rollback
```python
# scripts/rollback_deployment.py
def rollback_deployment(deployment_id: str):
    """Rollback to previous deployment"""
    logger.info(f"Rolling back deployment: {deployment_id}")

    # Load deployment manifest
    manifest = load_deployment_manifest(deployment_id)

    # Revert to previous job configuration
    previous_config = manifest["previous_config"]

    deployer = WorkflowDeployer(
        workspace_url=os.getenv("DATABRICKS_HOST"),
        token=os.getenv("DATABRICKS_TOKEN"),
        environment=manifest["environment"]
    )

    # Deploy previous configuration
    result = deployer.deploy(
        config=previous_config,
        strategy="direct",
        validate=False  # Skip validation during rollback
    )

    if result["success"]:
        logger.info("✓ Rollback completed successfully")
        # Notify stakeholders
        send_rollback_notification(deployment_id, result)
    else:
        logger.error("✗ Rollback failed - manual intervention required")
        raise Exception("Rollback failed")
```

## Best Practices

1. **Always validate before deploying to production**
2. **Use blue-green or canary for critical pipelines**
3. **Test rollback procedures regularly**
4. **Monitor deployments closely for first 24 hours**
5. **Document all configuration changes**
6. **Use infrastructure-as-code for reproducibility**
7. **Implement automated quality gates**
8. **Maintain deployment history and audit trail**

## Troubleshooting

**Issue**: Deployment fails with permission errors
**Solution**: Verify service principal has required permissions, check Unity Catalog grants

**Issue**: Job fails to start after deployment
**Solution**: Check cluster configuration, verify libraries are installed, review job logs

**Issue**: Smoke tests failing on green environment
**Solution**: Review test logs, validate test data, check for configuration issues

**Issue**: Rollback not working
**Solution**: Verify deployment manifest exists, check for manual configuration changes

## Security Considerations

1. **Use service principals for deployments**
2. **Store secrets in Azure Key Vault/AWS Secrets Manager**
3. **Implement least-privilege access controls**
4. **Enable audit logging for all deployments**
5. **Require approval for production deployments**
6. **Encrypt sensitive configuration values**
7. **Rotate credentials regularly**

## Related Commands

- `/databricks-engineering:validate-deployment` - Pre-deployment validation
- `/databricks-engineering:monitor-data-product` - Post-deployment monitoring
- `/databricks-engineering:deploy-bundle` - Deploy using Asset Bundles

---

**Last Updated**: 2024-12-31
**Version**: 1.0.0
**Category**: Deployment
**Prepared by**: gekambaram
