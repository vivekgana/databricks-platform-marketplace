"""
Data Product Metadata Management
"""
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class DataProductSchema:
    """Define data product schema."""
    name: str
    type: str
    required: bool
    description: str


@dataclass
class DataProductSLA:
    """Define SLA requirements."""
    freshness_hours: int
    availability_percent: float
    completeness_percent: float


class DataProduct:
    """Data product with metadata and contracts."""

    def __init__(
        self,
        name: str,
        version: str,
        owner: str,
        schema: List[DataProductSchema],
        sla: DataProductSLA
    ):
        self.name = name
        self.version = version
        self.owner = owner
        self.schema = schema
        self.sla = sla
        self.created_at = datetime.now()
