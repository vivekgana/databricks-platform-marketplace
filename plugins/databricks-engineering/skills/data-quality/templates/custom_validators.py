"""
Custom Validators Template
Reusable validation functions for business rules.
"""
from typing import Dict, Any, Callable
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, abs as spark_abs


def validate_amount_calculation(
    df: DataFrame,
    total_col: str,
    quantity_col: str,
    price_col: str,
    tolerance: float = 0.01
) -> int:
    """
    Validate total amount matches quantity * price.

    Returns:
        Count of records with mismatched amounts
    """
    return df.filter(
        spark_abs(col(total_col) - (col(quantity_col) * col(price_col))) > tolerance
    ).count()


def validate_date_sequence(
    df: DataFrame,
    start_date_col: str,
    end_date_col: str
) -> int:
    """
    Validate end date is after start date.

    Returns:
        Count of records with invalid date sequences
    """
    return df.filter(col(end_date_col) < col(start_date_col)).count()


def validate_referential_integrity(
    df: DataFrame,
    key_column: str,
    reference_df: DataFrame,
    reference_key: str
) -> int:
    """
    Check referential integrity between tables.

    Returns:
        Count of orphaned records
    """
    orphaned = df.join(
        reference_df,
        df[key_column] == reference_df[reference_key],
        "left_anti"
    )
    return orphaned.count()
