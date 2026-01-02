# Review Pipeline

## Description
Multi-agent code review with 12+ specialized reviewers analyzing your Databricks pipeline for performance, security, quality, cost optimization, and best practices.

## Usage
```bash
/databricks-engineering:review-pipeline [pipeline-name] [--agents agent1,agent2]
```

## What This Command Does

Orchestrates multiple specialized agents to perform comprehensive code review:

1. **PySpark Optimizer** - Performance and optimization
2. **Delta Lake Expert** - Delta operations and maintenance
3. **Data Quality Sentinel** - Validation and monitoring
4. **Pipeline Architect** - Design patterns and structure
5. **Unity Catalog Expert** - Governance and permissions
6. **Security Guardian** - Security and compliance
7. **Cost Analyzer** - Resource optimization
8. **Streaming Specialist** - Real-time processing patterns
9. **Notebook Reviewer** - Code quality and standards
10. **Workflow Orchestrator** - Job dependencies
11. **pytest-Databricks** - Testing coverage
12. **MLflow Reviewer** - Experiment tracking

## Parameters

- `pipeline-name` (required): Name of pipeline to review
- `--agents` (optional): Comma-separated list of specific agents
- `--layer` (optional): Review specific layer only (bronze|silver|gold)
- `--output` (optional): Output format (markdown|json|html)

## Examples

### Example 1: Full pipeline review
```bash
/databricks-engineering:review-pipeline customer-360
```

### Example 2: Performance-focused review
```bash
/databricks-engineering:review-pipeline customer-360 --agents pyspark-optimizer,cost-analyzer
```

### Example 3: Security and governance review
```bash
/databricks-engineering:review-pipeline customer-360 --agents security-guardian,unity-catalog-expert
```

## Review Process

### Phase 1: Static Analysis
- Code structure and organization
- Import dependencies
- Configuration validation
- Documentation completeness

### Phase 2: Agent Reviews
Each agent provides specialized review:

#### PySpark Optimizer Reviews:
- Shuffle optimization
- Partition strategies
- Broadcasting opportunities
- Caching effectiveness
- UDF performance

#### Delta Lake Expert Reviews:
- Table optimization (OPTIMIZE, VACUUM)
- Z-ORDER configuration
- Time travel usage
- Merge operations
- Change data feed

#### Data Quality Sentinel Reviews:
- Validation coverage
- Data quality rules
- Monitoring setup
- Alert configuration
- SLA compliance

#### Security Guardian Reviews:
- PII handling
- Access controls
- Secrets management
- Encryption at rest/transit
- Audit logging

### Phase 3: Report Generation
Consolidated report with:
- Executive summary
- Critical issues
- Warnings
- Recommendations
- Code examples

## Output Format

### Markdown Report
```markdown
# Pipeline Review: customer-360
**Date**: 2024-01-15
**Reviewers**: 12 agents
**Status**: PASS (with recommendations)

## Executive Summary
Pipeline follows medallion architecture best practices with 3 critical issues and 8 recommendations.

## Critical Issues (3)
1. **PySpark Performance** - Multiple unnecessary shuffles in Silver layer
2. **Security** - PII fields not masked in Bronze layer
3. **Cost** - Over-provisioned cluster configuration

## Warnings (8)
...

## Recommendations (15)
...
```

## Related Commands

- `/databricks-engineering:work-pipeline` - Implement pipeline
- `/databricks-engineering:optimize-costs` - Cost optimization
- `/databricks-engineering:test-data-quality` - Quality testing

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0
**Category**: Quality
