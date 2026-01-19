# Scaffold Project Command

## Description
Scaffold a new Databricks data engineering project with best practices, standard structure, CI/CD configurations, testing frameworks, and documentation templates. Provides production-ready project foundation.

## Usage
```bash
/databricks-engineering:scaffold-project [project-name] [--template template] [--framework framework]
```

## Parameters

- `project-name` (required): Name of the new project
- `--template` (optional): Project template - "medallion", "dlt", "mlops", "data-product" (default: "medallion")
- `--framework` (optional): Testing framework - "pytest", "unittest" (default: "pytest")
- `--include-ci-cd` (optional): Include CI/CD configuration (default: true)
- `--include-docs` (optional): Include documentation templates (default: true)
- `--python-version` (optional): Python version - "3.9", "3.10", "3.11" (default: "3.10")

## Examples

### Example 1: Basic medallion architecture project
```bash
/databricks-engineering:scaffold-project customer-analytics --template medallion
```

### Example 2: DLT pipeline project
```bash
/databricks-engineering:scaffold-project real-time-events \
  --template dlt \
  --include-ci-cd
```

### Example 3: Data product project
```bash
/databricks-engineering:scaffold-project customer-360-product \
  --template data-product \
  --framework pytest
```

## What This Command Does

### Project Structure Generation (5 minutes)
- Creates directory structure
- Generates configuration files
- Sets up package structure
- Creates README and documentation
- Initializes git repository

### Code Template Generation (10 minutes)
- Generates pipeline templates
- Creates utility functions
- Sets up logging configuration
- Generates test templates
- Creates example notebooks

### CI/CD Setup (5 minutes)
- Generates GitHub Actions workflows
- Creates Azure DevOps pipelines
- Sets up pre-commit hooks
- Configures linting and formatting
- Sets up deployment scripts

## Generated Project Structure

### Medallion Architecture Template
```
customer-analytics/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── deploy-dev.yml
│       ├── deploy-staging.yml
│       └── deploy-prod.yml
├── .databricks/
│   └── project.json
├── databricks.yml              # Databricks Asset Bundle config
├── src/
│   ├── __init__.py
│   ├── bronze/
│   │   ├── __init__.py
│   │   ├── ingest_customers.py
│   │   ├── ingest_orders.py
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── customer_schema.py
│   │       └── order_schema.py
│   ├── silver/
│   │   ├── __init__.py
│   │   ├── clean_customers.py
│   │   ├── enrich_orders.py
│   │   └── transformations/
│   │       ├── __init__.py
│   │       ├── data_cleansing.py
│   │       └── business_logic.py
│   ├── gold/
│   │   ├── __init__.py
│   │   ├── customer_metrics.py
│   │   ├── sales_aggregates.py
│   │   └── metrics/
│   │       ├── __init__.py
│   │       ├── customer_ltv.py
│   │       └── sales_kpis.py
│   ├── common/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logging_config.py
│   │   ├── spark_utils.py
│   │   └── delta_utils.py
│   └── quality/
│       ├── __init__.py
│       ├── expectations.py
│       └── validations.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_bronze.py
│   │   ├── test_silver.py
│   │   └── test_gold.py
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_end_to_end.py
│   └── fixtures/
│       ├── __init__.py
│       ├── sample_customers.py
│       └── sample_orders.py
├── notebooks/
│   ├── exploratory/
│   │   └── data_exploration.py
│   ├── bronze/
│   │   └── bronze_ingestion.py
│   ├── silver/
│   │   └── silver_transformation.py
│   └── gold/
│       └── gold_aggregation.py
├── config/
│   ├── dev.yaml
│   ├── staging.yaml
│   └── prod.yaml
├── docs/
│   ├── README.md
│   ├── architecture.md
│   ├── setup.md
│   ├── development.md
│   ├── deployment.md
│   └── api-reference.md
├── deployments/
│   ├── dev-job.yml
│   ├── staging-job.yml
│   └── prod-job.yml
├── scripts/
│   ├── setup.sh
│   ├── deploy.sh
│   ├── run_tests.sh
│   └── generate_docs.sh
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── setup.py
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── CHANGELOG.md
```

## Generated Files

### pyproject.toml
```toml
[tool.poetry]
name = "customer-analytics"
version = "1.0.0"
description = "Customer analytics data pipeline"
authors = ["Data Engineering Team <data-eng@company.com>"]

[tool.poetry.dependencies]
python = "^3.10"
pyspark = "^3.5.0"
delta-spark = "^3.0.0"
databricks-sdk = "^0.18.0"
great-expectations = "^0.18.0"
pyyaml = "^6.0"
python-dotenv = "^1.0.0"

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
pytest-spark = "^0.6.0"
black = "^23.0.0"
flake8 = "^6.0.0"
mypy = "^1.0.0"
pre-commit = "^3.0.0"

[tool.black]
line-length = 100
target-version = ['py310']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --cov=src --cov-report=html --cov-report=term"

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

### src/common/config.py
```python
"""
Configuration management for the data pipeline
"""

import os
import yaml
from typing import Dict, Any
from pathlib import Path


class Config:
    """Pipeline configuration manager"""

    def __init__(self, environment: str = "dev"):
        self.environment = environment
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        config_path = Path(__file__).parent.parent.parent / "config" / f"{self.environment}.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Override with environment variables
        config = self._apply_env_overrides(config)

        return config

    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides"""
        # Example: PIPELINE_CATALOG overrides config['catalog']
        if catalog := os.getenv('PIPELINE_CATALOG'):
            config['catalog'] = catalog

        if schema := os.getenv('PIPELINE_SCHEMA'):
            config['schema'] = schema

        return config

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default

        return value

    @property
    def catalog(self) -> str:
        """Get catalog name"""
        return self.get('catalog', f"{self.environment}_catalog")

    @property
    def schema(self) -> str:
        """Get schema name"""
        return self.get('schema', 'customer_analytics')

    @property
    def checkpoint_path(self) -> str:
        """Get checkpoint path"""
        return self.get('paths.checkpoint', f"/mnt/checkpoints/{self.environment}")

    @property
    def bronze_path(self) -> str:
        """Get bronze layer path"""
        return f"{self.catalog}.bronze"

    @property
    def silver_path(self) -> str:
        """Get silver layer path"""
        return f"{self.catalog}.silver"

    @property
    def gold_path(self) -> str:
        """Get gold layer path"""
        return f"{self.catalog}.gold"
```

### src/common/logging_config.py
```python
"""
Logging configuration for the pipeline
"""

import logging
import sys
from typing import Optional


def setup_logging(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging for the application

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
```

### src/bronze/ingest_customers.py
```python
"""
Bronze layer: Ingest customer data
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from typing import Optional
import logging

from src.common.config import Config
from src.common.logging_config import setup_logging

logger = setup_logging(__name__)


class CustomerIngestion:
    """Ingest customer data into bronze layer"""

    def __init__(self, spark: SparkSession, config: Config):
        self.spark = spark
        self.config = config

    def ingest(
        self,
        source_path: str,
        source_format: str = "json",
        checkpoint_path: Optional[str] = None
    ) -> DataFrame:
        """
        Ingest customer data from source

        Args:
            source_path: Path to source data
            source_format: Format of source data (json, csv, parquet)
            checkpoint_path: Checkpoint location for streaming

        Returns:
            DataFrame with ingested data
        """
        logger.info(f"Ingesting customer data from {source_path}")

        if checkpoint_path:
            # Streaming ingestion
            df = self._ingest_streaming(source_path, source_format, checkpoint_path)
        else:
            # Batch ingestion
            df = self._ingest_batch(source_path, source_format)

        # Add metadata columns
        df = self._add_metadata(df)

        # Write to bronze
        target_table = f"{self.config.bronze_path}.customers"
        self._write_to_bronze(df, target_table)

        logger.info(f"Successfully ingested customer data to {target_table}")

        return df

    def _ingest_streaming(
        self,
        source_path: str,
        source_format: str,
        checkpoint_path: str
    ) -> DataFrame:
        """Ingest data using Auto Loader"""
        return (
            self.spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", source_format)
            .option("cloudFiles.schemaLocation", f"{checkpoint_path}/schema")
            .option("cloudFiles.inferColumnTypes", "true")
            .load(source_path)
        )

    def _ingest_batch(self, source_path: str, source_format: str) -> DataFrame:
        """Ingest data in batch mode"""
        return self.spark.read.format(source_format).load(source_path)

    def _add_metadata(self, df: DataFrame) -> DataFrame:
        """Add ingestion metadata"""
        return (
            df
            .withColumn("_ingestion_timestamp", F.current_timestamp())
            .withColumn("_source_file", F.input_file_name())
            .withColumn("_data_source", F.lit("source_system"))
        )

    def _write_to_bronze(self, df: DataFrame, target_table: str):
        """Write data to bronze table"""
        (
            df.write
            .format("delta")
            .mode("append")
            .option("mergeSchema", "true")
            .saveAsTable(target_table)
        )


# Notebook entry point
if __name__ == "__main__":
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()
    config = Config(environment="dev")

    ingestion = CustomerIngestion(spark, config)
    ingestion.ingest(
        source_path="/mnt/raw/customers",
        source_format="json"
    )
```

### tests/conftest.py
```python
"""
Pytest configuration and fixtures
"""

import pytest
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from typing import Generator


@pytest.fixture(scope="session")
def spark() -> Generator[SparkSession, None, None]:
    """Create Spark session for tests"""
    spark = (
        SparkSession.builder
        .master("local[2]")
        .appName("pytest")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()
    )

    yield spark

    spark.stop()


@pytest.fixture
def sample_customers(spark: SparkSession) -> DataFrame:
    """Create sample customer data"""
    data = [
        ("C001", "john.doe@email.com", "John", "Doe", 30, "US"),
        ("C002", "jane.smith@email.com", "Jane", "Smith", 25, "UK"),
        ("C003", "bob.jones@email.com", "Bob", "Jones", 35, "CA"),
    ]

    schema = "customer_id STRING, email STRING, first_name STRING, last_name STRING, age INT, country STRING"

    return spark.createDataFrame(data, schema)
```

### README.md
```markdown
# Customer Analytics Pipeline

Databricks data engineering project for customer analytics.

## Overview

This project implements a medallion architecture data pipeline for processing customer and order data.

## Architecture

```
Raw Data → Bronze (Raw) → Silver (Cleaned) → Gold (Aggregated)
```

### Layers

- **Bronze**: Raw data ingestion with minimal transformation
- **Silver**: Cleaned, validated, and enriched data
- **Gold**: Business-level aggregations and metrics

## Setup

### Prerequisites

- Python 3.10+
- Databricks workspace
- Unity Catalog enabled

### Installation

```bash
# Clone repository
git clone <repository-url>
cd customer-analytics

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_bronze.py
```

### Code Formatting

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

## Deployment

### Deploy to Dev

```bash
databricks bundle deploy --target dev
```

### Deploy to Production

```bash
databricks bundle deploy --target prod
```

## Documentation

- [Architecture](docs/architecture.md)
- [Development Guide](docs/development.md)
- [Deployment Guide](docs/deployment.md)
- [API Reference](docs/api-reference.md)

## License

Copyright (c) 2024 Company Name
```

## Generated CI/CD Configuration

### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run tests
        run: pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install black flake8 mypy

      - name: Run black
        run: black --check src/ tests/

      - name: Run flake8
        run: flake8 src/ tests/

      - name: Run mypy
        run: mypy src/
```

## Best Practices

1. **Project Structure**: Follow standard Python package structure
2. **Testing**: Write tests before implementation (TDD)
3. **Documentation**: Keep documentation up to date
4. **CI/CD**: Automate testing and deployment
5. **Code Quality**: Use linting and formatting tools
6. **Version Control**: Use semantic versioning
7. **Configuration**: Environment-specific configurations
8. **Logging**: Comprehensive logging for debugging

## Troubleshooting

**Issue**: Import errors in tests
**Solution**: Ensure src/ is in PYTHONPATH, use `pip install -e .`

**Issue**: Spark session errors
**Solution**: Install pyspark and delta-spark, configure properly

**Issue**: CI/CD pipeline failures
**Solution**: Check secrets configured, verify permissions

## Related Commands

- `/databricks-engineering:plan-pipeline` - Plan new pipeline
- `/databricks-engineering:work-pipeline` - Implement pipeline
- `/databricks-engineering:deploy-bundle` - Deploy project

---

**Last Updated**: 2024-12-31
**Version**: 1.0.0
**Category**: Project Setup
**Prepared by**: Data Platform Team
