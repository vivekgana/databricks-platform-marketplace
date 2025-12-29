# Plan Pipeline Command

## Description
Create detailed data pipeline implementation plans with medallion architecture, cost estimation, and quality requirements.

## Usage
```bash
claude /databricks:plan-pipeline "<pipeline description>"
```

## Examples

### Basic Usage
```bash
claude /databricks:plan-pipeline "Build customer 360 pipeline ingesting from Salesforce, processing with PySpark, outputting to Unity Catalog"
```

### With Options
```bash
claude /databricks:plan-pipeline "Real-time fraud detection from Kafka" \
  --architecture streaming \
  --quality-level high \
  --cost-target 1000
```

## What It Does

1. **Research Phase**
   - Analyzes existing codebase patterns
   - Reviews similar pipelines in the repository
   - Checks Unity Catalog for relevant tables
   - Researches framework best practices

2. **Architecture Design**
   - Proposes medallion architecture (Bronze/Silver/Gold)
   - Defines data flow and transformations
   - Identifies required resources
   - Plans incremental processing strategy

3. **Quality Planning**
   - Defines data quality checks
   - Sets up validation rules
   - Plans Great Expectations suites
   - Identifies monitoring requirements

4. **Cost Estimation**
   - Estimates compute costs
   - Projects storage requirements
   - Suggests optimization opportunities
   - Calculates monthly run rate

5. **Implementation Plan**
   - Creates detailed task breakdown
   - Generates acceptance criteria
   - Provides code examples
   - Defines testing strategy

## Output

Creates a comprehensive plan document with:
- Executive summary
- Architecture diagrams (Mermaid)
- Detailed implementation steps
- Code templates
- Test strategy
- Deployment checklist
- Cost breakdown

## Related Commands
- `/databricks:work-pipeline` - Execute the plan
- `/databricks:review-pipeline` - Review implementation
- `/databricks:optimize-costs` - Cost optimization

## Agent Collaboration

This command uses these specialized agents:
- `pipeline-architect` - Architecture design
- `cost-analyzer` - Cost estimation
- `data-quality-sentinel` - Quality planning
- `unity-catalog-expert` - Governance planning
