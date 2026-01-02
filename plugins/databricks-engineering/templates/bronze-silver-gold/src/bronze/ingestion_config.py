"""
Ingestion Configuration

Centralized configuration for bronze layer data ingestion.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class SourceFormat(Enum):
    """Supported source data formats."""

    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    AVRO = "avro"
    ORC = "orc"
    DELTA = "delta"
    JDBC = "jdbc"


class IngestionMode(Enum):
    """Data ingestion modes."""

    BATCH = "batch"
    STREAMING = "streaming"
    INCREMENTAL = "incremental"


@dataclass
class IngestionConfig:
    """
    Configuration for data ingestion operations.

    Attributes:
        source_path: Path to source data
        table_name: Target bronze table name
        source_format: Format of source data
        ingestion_mode: Batch, streaming, or incremental
        merge_schema: Whether to merge schema changes
        partition_by: Columns to partition by
        options: Additional format-specific options
        quality_checks: Enable quality checks during ingestion
        checkpoint_location: Checkpoint location for streaming
    """

    source_path: str
    table_name: str
    source_format: SourceFormat = SourceFormat.JSON
    ingestion_mode: IngestionMode = IngestionMode.BATCH
    merge_schema: bool = True
    partition_by: Optional[List[str]] = None
    options: Dict[str, Any] = field(default_factory=dict)
    quality_checks: bool = True
    checkpoint_location: Optional[str] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.ingestion_mode == IngestionMode.STREAMING and not self.checkpoint_location:
            self.checkpoint_location = f"/tmp/checkpoints/{self.table_name}"


@dataclass
class CSVConfig:
    """CSV-specific configuration."""

    header: bool = True
    delimiter: str = ","
    quote: str = '"'
    escape: str = "\\"
    multiline: bool = False
    infer_schema: bool = True
    encoding: str = "UTF-8"


@dataclass
class JSONConfig:
    """JSON-specific configuration."""

    multiline: bool = False
    allow_comments: bool = False
    allow_unquoted_field_names: bool = False
    allow_single_quotes: bool = True
    allow_numeric_leading_zeros: bool = False
    date_format: Optional[str] = None
    timestamp_format: Optional[str] = None


@dataclass
class JDBCConfig:
    """JDBC-specific configuration."""

    url: str
    source_table: str
    properties: Dict[str, str] = field(default_factory=dict)
    partition_column: Optional[str] = None
    num_partitions: int = 10
    lower_bound: Optional[int] = None
    upper_bound: Optional[int] = None
    fetch_size: int = 100000
    session_init_statement: Optional[str] = None

    def to_properties_dict(self) -> Dict[str, str]:
        """Convert to properties dictionary for JDBC reader."""
        props = self.properties.copy()

        if self.fetch_size:
            props["fetchSize"] = str(self.fetch_size)

        if self.session_init_statement:
            props["sessionInitStatement"] = self.session_init_statement

        return props


@dataclass
class StreamingConfig:
    """Streaming ingestion configuration."""

    trigger_interval: str = "1 minute"
    max_files_per_trigger: Optional[int] = None
    max_bytes_per_trigger: Optional[str] = None
    trigger_once: bool = False
    await_termination: bool = False
    timeout: Optional[int] = None


# Predefined source configurations
COMMON_SOURCES = {
    "s3_json": IngestionConfig(
        source_path="s3://bucket/path/",
        table_name="bronze_source",
        source_format=SourceFormat.JSON,
        options={
            "multiline": "true",
            "inferSchema": "true",
        },
    ),
    "s3_parquet": IngestionConfig(
        source_path="s3://bucket/path/",
        table_name="bronze_source",
        source_format=SourceFormat.PARQUET,
        partition_by=["year", "month", "day"],
    ),
    "abfs_csv": IngestionConfig(
        source_path="abfss://container@storage.dfs.core.windows.net/path/",
        table_name="bronze_source",
        source_format=SourceFormat.CSV,
        options={
            "header": "true",
            "inferSchema": "true",
            "delimiter": ",",
        },
    ),
    "streaming_json": IngestionConfig(
        source_path="s3://bucket/streaming/",
        table_name="bronze_streaming",
        source_format=SourceFormat.JSON,
        ingestion_mode=IngestionMode.STREAMING,
        options={
            "maxFilesPerTrigger": "100",
        },
    ),
}


def get_config_for_source(source_name: str) -> IngestionConfig:
    """
    Get predefined configuration for a source.

    Args:
        source_name: Name of the predefined source

    Returns:
        IngestionConfig for the source

    Raises:
        ValueError: If source name not found
    """
    if source_name not in COMMON_SOURCES:
        raise ValueError(
            f"Source '{source_name}' not found. Available sources: {list(COMMON_SOURCES.keys())}"
        )

    return COMMON_SOURCES[source_name]


def create_jdbc_config(
    url: str,
    source_table: str,
    user: str,
    password: str,
    driver: str = "org.postgresql.Driver",
    **kwargs,
) -> JDBCConfig:
    """
    Create JDBC configuration with common settings.

    Args:
        url: JDBC connection URL
        source_table: Source table name
        user: Database user
        password: Database password
        driver: JDBC driver class
        **kwargs: Additional configuration options

    Returns:
        JDBCConfig instance
    """
    properties = {
        "user": user,
        "password": password,
        "driver": driver,
    }

    return JDBCConfig(url=url, source_table=source_table, properties=properties, **kwargs)
