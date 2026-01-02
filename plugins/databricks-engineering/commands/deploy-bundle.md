# Deploy Bundle Command

## Description
Deploy Databricks projects using Asset Bundles with multi-environment support, CI/CD integration, and infrastructure-as-code patterns. Provides consistent deployments across dev, staging, and production.

## Usage
```bash
/databricks-engineering:deploy-bundle [--environment env] [--validate] [--dry-run]
```

## Parameters

- `--environment` (optional): Target environment - "dev", "staging", "prod" (default: "dev")
- `--validate` (optional): Validate bundle before deployment (default: true)
- `--dry-run` (optional): Preview changes without deploying (default: false)
- `--target` (optional): Specific bundle target to deploy
- `--force` (optional): Force deploy even with validation errors (default: false)

## Examples

### Example 1: Deploy to development
```bash
/databricks-engineering:deploy-bundle --environment dev
```

### Example 2: Production deployment with validation
```bash
/databricks-engineering:deploy-bundle --environment prod --validate
```

### Example 3: Dry-run for preview
```bash
/databricks-engineering:deploy-bundle --environment prod --dry-run
```

## What This Command Does

### Phase 1: Bundle Validation (5 minutes)
- Validates databricks.yml configuration
- Checks resource definitions
- Verifies environment variables
- Validates permissions and access
- Checks for conflicts

### Phase 2: Deployment (10-20 minutes)
- Generates deployment manifest
- Provisions resources
- Deploys jobs and pipelines
- Applies configurations
- Updates permissions

### Phase 3: Post-Deployment (5 minutes)
- Runs validation tests
- Verifies resource creation
- Tests job execution
- Validates monitoring setup
- Generates deployment report

## Bundle Configuration

### databricks.yml
```yaml
bundle:
  name: customer-360-pipeline

workspace:
  host: https://your-workspace.cloud.databricks.com

targets:
  dev:
    mode: development
    workspace:
      root_path: /Workspace/dev/${bundle.name}
    resources:
      jobs:
        customer_360_job:
          name: "[DEV] Customer 360 Pipeline"
          job_clusters:
            - job_cluster_key: main
              new_cluster:
                spark_version: 13.3.x-scala2.12
                node_type_id: i3.xlarge
                num_workers: 2
                autoscale:
                  min_workers: 1
                  max_workers: 4
          tasks:
            - task_key: bronze
              job_cluster_key: main
              notebook_task:
                notebook_path: ./notebooks/bronze
                base_parameters:
                  env: dev
                  catalog: dev_catalog
            - task_key: silver
              depends_on:
                - task_key: bronze
              job_cluster_key: main
              notebook_task:
                notebook_path: ./notebooks/silver
                base_parameters:
                  env: dev
                  catalog: dev_catalog
          schedule:
            quartz_cron_expression: "0 0 * * * ?"
            timezone_id: "UTC"
            pause_status: "UNPAUSED"

  staging:
    mode: staging
    workspace:
      root_path: /Workspace/staging/${bundle.name}
    resources:
      jobs:
        customer_360_job:
          name: "[STAGING] Customer 360 Pipeline"
          job_clusters:
            - job_cluster_key: main
              new_cluster:
                spark_version: 13.3.x-scala2.12
                node_type_id: i3.2xlarge
                num_workers: 4
                autoscale:
                  min_workers: 2
                  max_workers: 8
                aws_attributes:
                  availability: SPOT_WITH_FALLBACK

  prod:
    mode: production
    workspace:
      root_path: /Workspace/prod/${bundle.name}
    resources:
      jobs:
        customer_360_job:
          name: "[PROD] Customer 360 Pipeline"
          job_clusters:
            - job_cluster_key: main
              new_cluster:
                spark_version: 13.3.x-scala2.12
                node_type_id: i3.4xlarge
                num_workers: 8
                autoscale:
                  min_workers: 4
                  max_workers: 16
                aws_attributes:
                  availability: SPOT_WITH_FALLBACK
          max_concurrent_runs: 1
          timeout_seconds: 14400
          email_notifications:
            on_failure:
              - data-platform@company.com
          webhook_notifications:
            on_failure:
              - id: pagerduty-webhook

include:
  - resources/*.yml
  - ./environments/${bundle.target}.yml

variables:
  catalog:
    description: "Unity Catalog name"
    default: ${bundle.target}_catalog
  schema:
    description: "Schema name"
    default: customer_360
```

### Deployment Script
```bash
#!/bin/bash
# scripts/deploy_bundle.sh

set -e

ENVIRONMENT=${1:-dev}
DRY_RUN=${2:-false}

echo "Deploying bundle to ${ENVIRONMENT}"

# Validate bundle
echo "Validating bundle configuration..."
databricks bundle validate --target ${ENVIRONMENT}

if [ $? -ne 0 ]; then
    echo "❌ Bundle validation failed"
    exit 1
fi

echo "✅ Bundle validation passed"

# Dry run if requested
if [ "$DRY_RUN" = "true" ]; then
    echo "Running dry-run deployment..."
    databricks bundle deploy --target ${ENVIRONMENT} --dry-run
    exit 0
fi

# Deploy bundle
echo "Deploying bundle..."
databricks bundle deploy --target ${ENVIRONMENT}

if [ $? -ne 0 ]; then
    echo "❌ Bundle deployment failed"
    exit 1
fi

echo "✅ Bundle deployed successfully"

# Run post-deployment tests
echo "Running post-deployment validation..."
databricks bundle run --target ${ENVIRONMENT} validation_job

echo "✅ Deployment complete"
```

### CI/CD Integration (GitHub Actions)
```yaml
# .github/workflows/deploy-bundle.yml
name: Deploy Databricks Bundle

on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches:
      - main

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Databricks CLI
        run: |
          curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

      - name: Configure Databricks CLI
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: |
          databricks configure --token

      - name: Validate Bundle
        run: |
          databricks bundle validate --target dev

  deploy-dev:
    needs: validate
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Dev
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: |
          databricks bundle deploy --target dev

  deploy-prod:
    needs: validate
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Prod
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: |
          databricks bundle deploy --target prod

      - name: Run Smoke Tests
        run: |
          databricks bundle run --target prod smoke_tests
```

## Multi-Environment Configuration

### Environment-Specific Files
```yaml
# environments/dev.yml
variables:
  catalog: dev_catalog
  schema: customer_360_dev
  checkpoint_path: /mnt/checkpoints/dev

resources:
  jobs:
    customer_360_job:
      schedule:
        pause_status: "PAUSED"
      max_retries: 0
```

```yaml
# environments/prod.yml
variables:
  catalog: prod_catalog
  schema: customer_360
  checkpoint_path: /mnt/checkpoints/prod

resources:
  jobs:
    customer_360_job:
      schedule:
        pause_status: "UNPAUSED"
      max_retries: 2
      retry_on_timeout: true
      email_notifications:
        on_start:
          - data-platform@company.com
        on_success:
          - data-platform@company.com
        on_failure:
          - data-platform@company.com
          - oncall@company.com
```

## Best Practices

1. **Environment Parity**: Keep environments as similar as possible
2. **Secrets Management**: Use Databricks secrets for credentials
3. **Version Control**: Track all bundle configuration in git
4. **Automated Testing**: Test bundles in dev before promoting
5. **Incremental Deployments**: Deploy incrementally to reduce risk
6. **Rollback Plan**: Maintain ability to rollback quickly
7. **Documentation**: Document bundle structure and dependencies
8. **Monitoring**: Set up monitoring for all deployed resources

## Troubleshooting

**Issue**: Bundle validation fails
**Solution**: Check databricks.yml syntax, verify resource names unique, validate environment variables

**Issue**: Deployment fails with permission errors
**Solution**: Verify service principal permissions, check workspace access, validate Unity Catalog grants

**Issue**: Resources not updating
**Solution**: Check for resource name conflicts, verify target specification, use --force flag cautiously

## Related Commands

- `/databricks-engineering:validate-deployment` - Pre-deployment validation
- `/databricks-engineering:deploy-workflow` - Traditional job deployment
- `/databricks-engineering:monitor-data-product` - Post-deployment monitoring

---

**Last Updated**: 2024-12-31
**Version**: 1.0.0
**Category**: Deployment
**Prepared by**: gekambaram
