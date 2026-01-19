# AI-SDLC Code Generation Guide

**Document Version:** 1.0
**Last Updated:** 2026-01-17
**Prepared by:** AI-SDLC Platform Team

---

## Table of Contents

1. [Overview](#overview)
2. [Code Generation Architecture](#code-generation-architecture)
3. [Python Code Generation](#python-code-generation)
4. [PySpark Code Generation](#pyspark-code-generation)
5. [SQL Code Generation](#sql-code-generation)
6. [Test Generation](#test-generation)
7. [Code Quality](#code-quality)
8. [Templates and Patterns](#templates-and-patterns)
9. [Best Practices](#best-practices)
10. [Reference](#reference)

---

## Overview

### What is Code Generation?

The AI-SDLC Code Generation system uses AI (LLMs) to automatically generate production-quality code from work item requirements. The system supports:

- **Python** - Classes, functions, modules
- **PySpark** - Data transformations, DLT pipelines
- **SQL** - Queries, stored procedures, views
- **Tests** - Unit tests, integration tests

### Why AI-Powered Code Generation?

**Benefits:**
- **Speed:** Generate code in seconds vs hours
- **Consistency:** Follow project patterns automatically
- **Quality:** Built-in standards compliance
- **Coverage:** Comprehensive tests generated automatically

**Approach:**
1. Parse work item requirements
2. Build context from existing codebase
3. Generate code using LLM with templates
4. Validate against quality standards
5. Generate corresponding tests

---

## Code Generation Architecture

### Component Overview

```
CodeGeneratorAgent
├── Python Generator
│   ├── Module structure
│   ├── Class definitions
│   └── Function implementations
├── PySpark Generator
│   ├── DataFrame transformations
│   ├── Delta Lake operations
│   └── DLT pipeline code
├── SQL Generator
│   ├── SELECT queries
│   ├── Stored procedures
│   └── Views and tables
└── Test Template Generator
    ├── pytest fixtures
    ├── Test cases
    └── Mock data
```

### Generation Flow

```
Requirements (from work item)
    ↓
Extract key information
    ├─ Entity names
    ├─ Operations
    ├─ Data schemas
    └─ Business logic
    ↓
Analyze existing codebase
    ├─ Coding patterns
    ├─ Naming conventions
    ├─ Import styles
    └─ Architecture patterns
    ↓
Build LLM prompt
    ├─ Requirements context
    ├─ Code templates
    ├─ Examples from codebase
    └─ Quality requirements
    ↓
Generate code with LLM
    ├─ Temperature: 0.2 (deterministic)
    ├─ Max tokens: 8000
    └─ Model: databricks-claude-sonnet-4-5
    ↓
Post-process and validate
    ├─ Format with black
    ├─ Add missing imports
    ├─ Validate syntax
    └─ Run quality checks
    ↓
Generate tests
    ├─ Happy path tests
    ├─ Edge case tests
    ├─ Error handling tests
    └─ Integration tests
    ↓
Save as evidence
```

---

## Python Code Generation

### Module Structure

Generated Python modules follow this structure:

```python
"""
[Module Title]

[Module Description]
"""

# Standard library imports
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

# Third-party imports
import pandas as pd
from pydantic import BaseModel

# Local imports
from myproject.utils import helper_function

logger = logging.getLogger(__name__)


# Data models (if needed)
class DataModel(BaseModel):
    """Data model for [entity]."""
    id: str
    name: str
    created_at: datetime


# Main classes
class ServiceClass:
    """
    [Service Description]

    This class handles [detailed explanation].
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize service.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data.

        Args:
            input_data: Input data dictionary

        Returns:
            Processed results

        Raises:
            ValueError: If input is invalid
        """
        try:
            # Validate input
            self._validate_input(input_data)

            # Process
            result = self._do_processing(input_data)

            return result

        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            raise

    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate input data."""
        if not input_data:
            raise ValueError("Input data cannot be empty")

    def _do_processing(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal processing logic."""
        # Implementation
        return {"status": "success"}


# Module-level functions (if needed)
def utility_function(param: str) -> str:
    """
    Utility function description.

    Args:
        param: Parameter description

    Returns:
        Result description
    """
    return param.upper()
```

### Class Generation

**Input Requirements:**
```json
{
  "entity": "AuditLog",
  "operations": ["create", "read", "update", "delete"],
  "fields": [
    {"name": "id", "type": "str"},
    {"name": "timestamp", "type": "datetime"},
    {"name": "user_id", "type": "str"},
    {"name": "action", "type": "str"},
    {"name": "details", "type": "Dict[str, Any]"}
  ]
}
```

**Generated Code:**
```python
"""
Audit Log Management

Provides CRUD operations for audit logs.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class AuditLog:
    """Audit log entry."""
    id: str
    timestamp: datetime
    user_id: str
    action: str
    details: Dict[str, Any]


class AuditLogService:
    """
    Audit Log Service

    Manages audit log entries with full CRUD operations.
    """

    def __init__(self, storage_backend: Any):
        """
        Initialize audit log service.

        Args:
            storage_backend: Storage backend for persistence
        """
        self.storage = storage_backend
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def create(self, user_id: str, action: str, details: Dict[str, Any]) -> AuditLog:
        """
        Create a new audit log entry.

        Args:
            user_id: User who performed the action
            action: Action that was performed
            details: Additional details about the action

        Returns:
            Created audit log entry

        Raises:
            ValueError: If required fields are missing
        """
        if not user_id or not action:
            raise ValueError("user_id and action are required")

        log_entry = AuditLog(
            id=self._generate_id(),
            timestamp=datetime.now(),
            user_id=user_id,
            action=action,
            details=details,
        )

        self.storage.save(log_entry)
        self.logger.info(f"Created audit log: {log_entry.id}")

        return log_entry

    def read(self, log_id: str) -> Optional[AuditLog]:
        """
        Retrieve an audit log entry by ID.

        Args:
            log_id: Audit log ID

        Returns:
            Audit log entry or None if not found
        """
        return self.storage.get(log_id)

    def update(self, log_id: str, updates: Dict[str, Any]) -> AuditLog:
        """
        Update an audit log entry.

        Args:
            log_id: Audit log ID
            updates: Fields to update

        Returns:
            Updated audit log entry

        Raises:
            ValueError: If log not found
        """
        log_entry = self.read(log_id)
        if not log_entry:
            raise ValueError(f"Audit log {log_id} not found")

        # Update fields
        for key, value in updates.items():
            if hasattr(log_entry, key):
                setattr(log_entry, key, value)

        self.storage.save(log_entry)
        self.logger.info(f"Updated audit log: {log_id}")

        return log_entry

    def delete(self, log_id: str) -> bool:
        """
        Delete an audit log entry.

        Args:
            log_id: Audit log ID

        Returns:
            True if deleted, False otherwise
        """
        success = self.storage.delete(log_id)
        if success:
            self.logger.info(f"Deleted audit log: {log_id}")
        return success

    def _generate_id(self) -> str:
        """Generate unique audit log ID."""
        import uuid
        return str(uuid.uuid4())
```

### Function Generation

**Simpler operations generate standalone functions:**

```python
def calculate_risk_score(
    transaction_amount: float,
    transaction_frequency: int,
    account_age_days: int,
    previous_fraud_count: int = 0
) -> float:
    """
    Calculate risk score for a transaction.

    Risk score formula:
    - Base score from amount (0-40 points)
    - Frequency penalty (0-30 points)
    - Account age discount (0-20 points)
    - Previous fraud penalty (0-10 points)

    Args:
        transaction_amount: Transaction amount in USD
        transaction_frequency: Number of transactions in last 24h
        account_age_days: Age of account in days
        previous_fraud_count: Count of previous fraud incidents

    Returns:
        Risk score from 0 (low risk) to 100 (high risk)
    """
    # Base score from amount
    if transaction_amount > 10000:
        amount_score = 40
    elif transaction_amount > 5000:
        amount_score = 30
    elif transaction_amount > 1000:
        amount_score = 20
    else:
        amount_score = 10

    # Frequency penalty
    frequency_score = min(transaction_frequency * 5, 30)

    # Account age discount
    if account_age_days > 365:
        age_discount = 20
    elif account_age_days > 90:
        age_discount = 10
    else:
        age_discount = 0

    # Previous fraud penalty
    fraud_penalty = min(previous_fraud_count * 5, 10)

    # Calculate final score
    risk_score = amount_score + frequency_score - age_discount + fraud_penalty
    risk_score = max(0, min(100, risk_score))  # Clamp to 0-100

    return risk_score
```

---

## PySpark Code Generation

### DataFrame Transformations

**Input Requirements:**
```json
{
  "operation": "transform_audit_logs",
  "input_table": "raw_audit_logs",
  "output_table": "processed_audit_logs",
  "transformations": [
    "Parse JSON details field",
    "Extract user email domain",
    "Categorize actions",
    "Add timestamp partitions"
  ]
}
```

**Generated PySpark Code:**
```python
"""
Audit Log Transformation

Transforms raw audit logs into processed format for analytics.
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
import logging

logger = logging.getLogger(__name__)


def transform_audit_logs(spark: SparkSession, input_path: str, output_path: str) -> DataFrame:
    """
    Transform raw audit logs into processed format.

    Transformations:
    1. Parse JSON details field
    2. Extract user email domain
    3. Categorize actions
    4. Add timestamp partitions

    Args:
        spark: SparkSession
        input_path: Path to raw audit logs
        output_path: Path for processed logs

    Returns:
        Transformed DataFrame
    """
    logger.info(f"Reading raw audit logs from {input_path}")

    # Read raw data
    df = spark.read.format("delta").load(input_path)

    # Parse JSON details
    df = df.withColumn(
        "details_parsed",
        F.from_json(F.col("details"), StructType([
            StructField("resource_id", StringType()),
            StructField("resource_type", StringType()),
            StructField("ip_address", StringType()),
        ]))
    )

    # Extract nested fields
    df = df.select(
        "*",
        F.col("details_parsed.resource_id").alias("resource_id"),
        F.col("details_parsed.resource_type").alias("resource_type"),
        F.col("details_parsed.ip_address").alias("ip_address"),
    ).drop("details_parsed")

    # Extract user email domain
    df = df.withColumn(
        "user_domain",
        F.when(
            F.col("user_id").contains("@"),
            F.split(F.col("user_id"), "@")[1]
        ).otherwise(F.lit("internal"))
    )

    # Categorize actions
    df = df.withColumn(
        "action_category",
        F.when(F.col("action").isin("create", "insert", "add"), "CREATE")
        .when(F.col("action").isin("read", "select", "view", "get"), "READ")
        .when(F.col("action").isin("update", "modify", "edit"), "UPDATE")
        .when(F.col("action").isin("delete", "remove", "drop"), "DELETE")
        .otherwise("OTHER")
    )

    # Add timestamp partitions
    df = df.withColumn("year", F.year(F.col("timestamp"))) \
           .withColumn("month", F.month(F.col("timestamp"))) \
           .withColumn("day", F.dayofmonth(F.col("timestamp")))

    # Write to Delta Lake with partitioning
    logger.info(f"Writing processed audit logs to {output_path}")
    df.write.format("delta") \
        .mode("overwrite") \
        .partitionBy("year", "month", "day") \
        .save(output_path)

    return df


def aggregate_audit_metrics(df: DataFrame) -> DataFrame:
    """
    Aggregate audit log metrics by user and action category.

    Args:
        df: Processed audit logs DataFrame

    Returns:
        Aggregated metrics DataFrame
    """
    metrics = df.groupBy("user_id", "user_domain", "action_category") \
        .agg(
            F.count("*").alias("action_count"),
            F.countDistinct("resource_id").alias("unique_resources"),
            F.min("timestamp").alias("first_action"),
            F.max("timestamp").alias("last_action"),
        ) \
        .orderBy(F.desc("action_count"))

    return metrics
```

### Delta Lake Operations

```python
"""
Delta Lake Utilities

Provides utility functions for Delta Lake operations.
"""

from pyspark.sql import SparkSession, DataFrame
from delta.tables import DeltaTable
import logging

logger = logging.getLogger(__name__)


def upsert_to_delta(
    spark: SparkSession,
    source_df: DataFrame,
    target_path: str,
    merge_keys: list,
    update_condition: str = None
) -> None:
    """
    Upsert data to Delta Lake table.

    Args:
        spark: SparkSession
        source_df: Source DataFrame with updates
        target_path: Path to target Delta table
        merge_keys: List of columns to merge on
        update_condition: Optional condition for updates
    """
    logger.info(f"Upserting to {target_path}")

    # Check if table exists
    if DeltaTable.isDeltaTable(spark, target_path):
        delta_table = DeltaTable.forPath(spark, target_path)

        # Build merge condition
        merge_condition = " AND ".join([
            f"target.{key} = source.{key}" for key in merge_keys
        ])

        # Perform merge
        merge_builder = delta_table.alias("target") \
            .merge(source_df.alias("source"), merge_condition)

        # Update when matched
        if update_condition:
            merge_builder = merge_builder.whenMatchedUpdate(
                condition=update_condition,
                set={col: f"source.{col}" for col in source_df.columns}
            )
        else:
            merge_builder = merge_builder.whenMatchedUpdateAll()

        # Insert when not matched
        merge_builder = merge_builder.whenNotMatchedInsertAll()

        merge_builder.execute()

        logger.info("Upsert completed successfully")
    else:
        # Table doesn't exist, create it
        source_df.write.format("delta").save(target_path)
        logger.info(f"Created new Delta table at {target_path}")


def compact_delta_table(spark: SparkSession, table_path: str) -> None:
    """
    Compact Delta Lake table by optimizing files.

    Args:
        spark: SparkSession
        table_path: Path to Delta table
    """
    logger.info(f"Compacting Delta table: {table_path}")

    delta_table = DeltaTable.forPath(spark, table_path)

    # Optimize (compact small files)
    delta_table.optimize().executeCompaction()

    # Vacuum old files (retain 7 days)
    delta_table.vacuum(retentionHours=168)

    logger.info("Compaction completed")
```

### DLT Pipeline Code

```python
"""
DLT Pipeline for Audit Logs

Databricks Delta Live Tables pipeline for real-time audit log processing.
"""

import dlt
from pyspark.sql import functions as F


@dlt.table(
    name="bronze_audit_logs",
    comment="Raw audit logs from source systems",
    table_properties={"quality": "bronze"},
)
def bronze_audit_logs():
    """Ingest raw audit logs."""
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", "/mnt/schemas/audit_logs")
        .load("/mnt/raw/audit_logs")
    )


@dlt.table(
    name="silver_audit_logs",
    comment="Cleaned and enriched audit logs",
    table_properties={"quality": "silver"},
)
@dlt.expect_or_drop("valid_timestamp", "timestamp IS NOT NULL")
@dlt.expect_or_drop("valid_user", "user_id IS NOT NULL")
def silver_audit_logs():
    """Transform and clean audit logs."""
    return (
        dlt.read_stream("bronze_audit_logs")
        .select(
            F.col("id"),
            F.col("timestamp").cast("timestamp"),
            F.col("user_id"),
            F.col("action"),
            F.from_json(F.col("details"), "resource_id STRING, resource_type STRING").alias("details_parsed"),
        )
        .select(
            "*",
            F.col("details_parsed.resource_id").alias("resource_id"),
            F.col("details_parsed.resource_type").alias("resource_type"),
        )
        .drop("details_parsed")
    )


@dlt.table(
    name="gold_audit_metrics",
    comment="Aggregated audit metrics for analytics",
    table_properties={"quality": "gold"},
)
def gold_audit_metrics():
    """Aggregate audit metrics."""
    return (
        dlt.read("silver_audit_logs")
        .groupBy(
            F.window("timestamp", "1 hour"),
            "user_id",
            "action",
        )
        .agg(
            F.count("*").alias("action_count"),
            F.countDistinct("resource_id").alias("unique_resources"),
        )
    )
```

---

## SQL Code Generation

### Query Generation

**Input Requirements:**
```json
{
  "operation": "get_high_risk_transactions",
  "tables": ["transactions", "users", "risk_scores"],
  "conditions": ["risk_score > 75", "transaction_date >= today - 7 days"],
  "order_by": "risk_score DESC"
}
```

**Generated SQL:**
```sql
-- High Risk Transactions Report
-- Retrieves transactions with high risk scores from the last 7 days

SELECT
    t.transaction_id,
    t.transaction_date,
    t.amount,
    u.user_id,
    u.email,
    u.account_created_date,
    r.risk_score,
    r.risk_factors
FROM
    transactions t
    INNER JOIN users u ON t.user_id = u.user_id
    INNER JOIN risk_scores r ON t.transaction_id = r.transaction_id
WHERE
    r.risk_score > 75
    AND t.transaction_date >= CURRENT_DATE - INTERVAL '7' DAY
ORDER BY
    r.risk_score DESC,
    t.transaction_date DESC
LIMIT 1000;
```

### Stored Procedure Generation

```sql
-- Calculate User Risk Profile
-- Stored procedure to calculate comprehensive risk profile for a user

CREATE OR REPLACE PROCEDURE calculate_user_risk_profile(
    IN p_user_id VARCHAR(50),
    OUT p_risk_score DECIMAL(5,2),
    OUT p_risk_category VARCHAR(20)
)
LANGUAGE SQL
AS $$
DECLARE
    v_transaction_count INT;
    v_avg_transaction_amount DECIMAL(10,2);
    v_account_age_days INT;
    v_fraud_count INT;
    v_base_score DECIMAL(5,2) := 0;
BEGIN
    -- Get user metrics
    SELECT
        COUNT(*) as transaction_count,
        AVG(amount) as avg_amount,
        DATEDIFF(day, u.account_created_date, CURRENT_DATE) as account_age,
        COALESCE(SUM(CASE WHEN f.is_fraud THEN 1 ELSE 0 END), 0) as fraud_count
    INTO
        v_transaction_count,
        v_avg_transaction_amount,
        v_account_age_days,
        v_fraud_count
    FROM
        users u
        LEFT JOIN transactions t ON u.user_id = t.user_id
        LEFT JOIN fraud_incidents f ON t.transaction_id = f.transaction_id
    WHERE
        u.user_id = p_user_id
    GROUP BY
        u.user_id, u.account_created_date;

    -- Calculate risk score
    v_base_score := 50;  -- Start at neutral

    -- Adjust for transaction patterns
    IF v_avg_transaction_amount > 5000 THEN
        v_base_score := v_base_score + 20;
    END IF;

    IF v_transaction_count > 100 THEN
        v_base_score := v_base_score - 10;  -- High volume is normal
    END IF;

    -- Adjust for account age
    IF v_account_age_days < 30 THEN
        v_base_score := v_base_score + 15;  -- New accounts are risky
    ELSIF v_account_age_days > 365 THEN
        v_base_score := v_base_score - 15;  -- Old accounts are trusted
    END IF;

    -- Adjust for fraud history
    v_base_score := v_base_score + (v_fraud_count * 10);

    -- Clamp score to 0-100
    p_risk_score := GREATEST(0, LEAST(100, v_base_score));

    -- Categorize risk
    IF p_risk_score >= 75 THEN
        p_risk_category := 'HIGH';
    ELSIF p_risk_score >= 50 THEN
        p_risk_category := 'MEDIUM';
    ELSE
        p_risk_category := 'LOW';
    END IF;

END;
$$;
```

---

## Test Generation

### Unit Test Generation

**For every generated module, tests are automatically created:**

```python
"""
Tests for Audit Log Service

Generated unit tests for audit_log_service.py
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from audit_log_service import AuditLogService, AuditLog


class TestAuditLogService:
    """Test suite for AuditLogService."""

    @pytest.fixture
    def mock_storage(self):
        """Mock storage backend."""
        storage = Mock()
        storage.save = MagicMock()
        storage.get = MagicMock()
        storage.delete = MagicMock(return_value=True)
        return storage

    @pytest.fixture
    def service(self, mock_storage):
        """Create AuditLogService instance with mock storage."""
        return AuditLogService(storage_backend=mock_storage)

    def test_create_audit_log_success(self, service, mock_storage):
        """Test successful audit log creation."""
        # Arrange
        user_id = "user@example.com"
        action = "LOGIN"
        details = {"ip": "192.168.1.1"}

        # Act
        log_entry = service.create(user_id, action, details)

        # Assert
        assert log_entry.user_id == user_id
        assert log_entry.action == action
        assert log_entry.details == details
        assert isinstance(log_entry.timestamp, datetime)
        assert isinstance(log_entry.id, str)
        mock_storage.save.assert_called_once_with(log_entry)

    def test_create_audit_log_missing_user_id(self, service):
        """Test audit log creation with missing user_id."""
        with pytest.raises(ValueError, match="user_id and action are required"):
            service.create("", "ACTION", {})

    def test_create_audit_log_missing_action(self, service):
        """Test audit log creation with missing action."""
        with pytest.raises(ValueError, match="user_id and action are required"):
            service.create("user@example.com", "", {})

    def test_read_audit_log_found(self, service, mock_storage):
        """Test reading an existing audit log."""
        # Arrange
        log_id = "log-123"
        expected_log = AuditLog(
            id=log_id,
            timestamp=datetime.now(),
            user_id="user@example.com",
            action="LOGIN",
            details={},
        )
        mock_storage.get.return_value = expected_log

        # Act
        result = service.read(log_id)

        # Assert
        assert result == expected_log
        mock_storage.get.assert_called_once_with(log_id)

    def test_read_audit_log_not_found(self, service, mock_storage):
        """Test reading a non-existent audit log."""
        # Arrange
        mock_storage.get.return_value = None

        # Act
        result = service.read("nonexistent")

        # Assert
        assert result is None

    def test_update_audit_log_success(self, service, mock_storage):
        """Test successful audit log update."""
        # Arrange
        log_id = "log-123"
        existing_log = AuditLog(
            id=log_id,
            timestamp=datetime.now(),
            user_id="user@example.com",
            action="LOGIN",
            details={"ip": "192.168.1.1"},
        )
        mock_storage.get.return_value = existing_log

        updates = {"action": "LOGOUT"}

        # Act
        updated_log = service.update(log_id, updates)

        # Assert
        assert updated_log.action == "LOGOUT"
        mock_storage.save.assert_called_once()

    def test_update_audit_log_not_found(self, service, mock_storage):
        """Test updating a non-existent audit log."""
        # Arrange
        mock_storage.get.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Audit log .* not found"):
            service.update("nonexistent", {"action": "NEW_ACTION"})

    def test_delete_audit_log_success(self, service, mock_storage):
        """Test successful audit log deletion."""
        # Arrange
        log_id = "log-123"

        # Act
        result = service.delete(log_id)

        # Assert
        assert result is True
        mock_storage.delete.assert_called_once_with(log_id)

    def test_delete_audit_log_failure(self, service, mock_storage):
        """Test failed audit log deletion."""
        # Arrange
        mock_storage.delete.return_value = False

        # Act
        result = service.delete("log-123")

        # Assert
        assert result is False


# Integration tests (optional)
@pytest.mark.integration
class TestAuditLogServiceIntegration:
    """Integration tests with real storage backend."""

    @pytest.fixture
    def real_storage(self):
        """Set up real storage backend for integration tests."""
        # Implementation depends on your storage
        pass

    def test_full_crud_cycle(self, real_storage):
        """Test complete CRUD cycle with real storage."""
        service = AuditLogService(storage_backend=real_storage)

        # Create
        log = service.create("user@example.com", "TEST_ACTION", {})
        assert log.id is not None

        # Read
        retrieved = service.read(log.id)
        assert retrieved.id == log.id

        # Update
        updated = service.update(log.id, {"action": "UPDATED_ACTION"})
        assert updated.action == "UPDATED_ACTION"

        # Delete
        assert service.delete(log.id) is True
        assert service.read(log.id) is None
```

---

## Code Quality

### Quality Checks

All generated code is validated against:

1. **Linting (black)**
   ```bash
   black --check generated_code.py
   ```

2. **Style (ruff)**
   ```bash
   ruff check generated_code.py
   ```

3. **Security (bandit)**
   ```bash
   bandit -r generated_code.py
   ```

4. **Complexity (radon)**
   ```bash
   radon cc generated_code.py -a -nb
   ```

5. **Type checking (mypy)**
   ```bash
   mypy generated_code.py --strict
   ```

### Code Quality Report

Generated as `code-quality-report.json`:

```json
{
  "file": "audit_log_service.py",
  "timestamp": "2026-01-17T10:30:00Z",
  "checks": {
    "linting": {
      "passed": true,
      "tool": "black",
      "issues": []
    },
    "style": {
      "passed": true,
      "tool": "ruff",
      "issues": []
    },
    "security": {
      "passed": true,
      "tool": "bandit",
      "vulnerabilities": [],
      "confidence_level": "HIGH"
    },
    "complexity": {
      "passed": true,
      "tool": "radon",
      "average_complexity": 3.2,
      "max_complexity": 8,
      "functions_above_threshold": []
    },
    "documentation": {
      "passed": true,
      "docstring_coverage": 100,
      "missing_docstrings": []
    },
    "type_hints": {
      "passed": true,
      "coverage": 95,
      "missing_hints": ["_internal_helper"]
    }
  },
  "overall_quality_score": 0.95,
  "recommendations": [
    "Consider adding type hints to _internal_helper function"
  ]
}
```

---

## Templates and Patterns

### Template Structure

Templates guide code generation:

```python
# Template: Service Class
SERVICE_CLASS_TEMPLATE = """
class {class_name}:
    \"\"\"
    {class_description}
    \"\"\"

    def __init__(self, {init_params}):
        \"\"\"
        Initialize {class_name}.

        Args:
            {init_params_docs}
        \"\"\"
        {init_body}

    def {main_method}(self, {method_params}) -> {return_type}:
        \"\"\"
        {method_description}

        Args:
            {method_params_docs}

        Returns:
            {return_description}
        \"\"\"
        {method_body}
"""
```

### Pattern Library

Common patterns automatically applied:

1. **Singleton Pattern**
2. **Factory Pattern**
3. **Repository Pattern**
4. **Service Layer Pattern**
5. **Dependency Injection**

---

## Best Practices

1. **Always generate tests** alongside code
2. **Use type hints** for all functions
3. **Include docstrings** for all public methods
4. **Handle errors explicitly** with try/except
5. **Log important operations** for debugging
6. **Follow project conventions** from existing code
7. **Validate inputs** before processing
8. **Keep complexity low** (max cyclomatic complexity: 10)
9. **Make code testable** with dependency injection
10. **Document assumptions** in comments

---

## Document History

| Version | Date       | Author                | Changes                   |
|---------|------------|-----------------------|---------------------------|
| 1.0     | 2026-01-17 | AI-SDLC Platform Team | Initial code gen guide    |

---

**Need Help?**
- Report issues: [GitHub Issues](https://github.com/your-org/ai-sdlc/issues)
- Slack: #ai-sdlc-support
- Email: ai-sdlc-support@yourcompany.com
