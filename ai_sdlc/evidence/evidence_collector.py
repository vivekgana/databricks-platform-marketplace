"""
Evidence Collector

Collects and organizes evidence artifacts from workflow stages.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class EvidenceCategory(Enum):
    """Categories of evidence artifacts."""

    PLAN = "plan"
    CODE = "code"
    TEST = "test"
    SCREENSHOT = "screenshot"
    REPORT = "report"
    LOG = "log"
    DATA = "data"
    DOCUMENTATION = "documentation"


@dataclass
class EvidenceItem:
    """Represents a single evidence artifact."""

    path: str
    category: EvidenceCategory
    stage: str
    filename: str
    description: Optional[str] = None
    size_bytes: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "category": self.category.value,
            "stage": self.stage,
            "filename": self.filename,
            "description": self.description,
            "size_bytes": self.size_bytes,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


class EvidenceCollector:
    """
    Collects and organizes evidence artifacts.

    Manages evidence items from all workflow stages and prepares them
    for storage and presentation.
    """

    def __init__(self, work_item_id: str, base_path: str):
        """
        Initialize evidence collector.

        Args:
            work_item_id: The work item ID
            base_path: Base path for evidence storage
        """
        self.work_item_id = work_item_id
        self.base_path = base_path
        self.evidence_items: List[EvidenceItem] = []
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def add_evidence(
        self,
        path: str,
        category: EvidenceCategory,
        stage: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EvidenceItem:
        """
        Add an evidence item.

        Args:
            path: Path to the evidence file
            category: Evidence category
            stage: Workflow stage
            description: Optional description
            metadata: Optional metadata

        Returns:
            Created EvidenceItem
        """
        # Get file info
        file_path = Path(path)
        filename = file_path.name
        size_bytes = file_path.stat().st_size if file_path.exists() else None

        # Create evidence item
        item = EvidenceItem(
            path=path,
            category=category,
            stage=stage,
            filename=filename,
            description=description,
            size_bytes=size_bytes,
            metadata=metadata or {},
        )

        self.evidence_items.append(item)
        self.logger.info(f"Added evidence: {filename} ({category.value}) from {stage}")

        return item

    def add_screenshot(
        self,
        path: str,
        stage: str,
        description: Optional[str] = None,
    ) -> EvidenceItem:
        """
        Add a screenshot evidence item.

        Args:
            path: Path to screenshot file
            stage: Workflow stage
            description: Optional description

        Returns:
            Created EvidenceItem
        """
        return self.add_evidence(
            path=path,
            category=EvidenceCategory.SCREENSHOT,
            stage=stage,
            description=description,
        )

    def add_report(
        self,
        path: str,
        stage: str,
        description: Optional[str] = None,
    ) -> EvidenceItem:
        """
        Add a report evidence item.

        Args:
            path: Path to report file
            stage: Workflow stage
            description: Optional description

        Returns:
            Created EvidenceItem
        """
        return self.add_evidence(
            path=path,
            category=EvidenceCategory.REPORT,
            stage=stage,
            description=description,
        )

    def get_evidence_by_category(
        self, category: EvidenceCategory
    ) -> List[EvidenceItem]:
        """
        Get evidence items by category.

        Args:
            category: Evidence category

        Returns:
            List of evidence items
        """
        return [item for item in self.evidence_items if item.category == category]

    def get_evidence_by_stage(self, stage: str) -> List[EvidenceItem]:
        """
        Get evidence items by stage.

        Args:
            stage: Workflow stage

        Returns:
            List of evidence items
        """
        return [item for item in self.evidence_items if item.stage == stage]

    def get_screenshots(self) -> List[EvidenceItem]:
        """Get all screenshot evidence items."""
        return self.get_evidence_by_category(EvidenceCategory.SCREENSHOT)

    def get_reports(self) -> List[EvidenceItem]:
        """Get all report evidence items."""
        return self.get_evidence_by_category(EvidenceCategory.REPORT)

    def get_all_evidence(self) -> List[EvidenceItem]:
        """Get all evidence items."""
        return self.evidence_items

    def get_summary(self) -> Dict[str, Any]:
        """
        Get evidence summary.

        Returns:
            Summary dictionary
        """
        return {
            "work_item_id": self.work_item_id,
            "total_items": len(self.evidence_items),
            "by_category": {
                category.value: len(self.get_evidence_by_category(category))
                for category in EvidenceCategory
            },
            "by_stage": self._count_by_stage(),
            "total_size_bytes": sum(
                item.size_bytes for item in self.evidence_items if item.size_bytes
            ),
            "screenshots_count": len(self.get_screenshots()),
            "reports_count": len(self.get_reports()),
        }

    def _count_by_stage(self) -> Dict[str, int]:
        """Count evidence items by stage."""
        stages = set(item.stage for item in self.evidence_items)
        return {stage: len(self.get_evidence_by_stage(stage)) for stage in stages}

    def export_metadata(self) -> Dict[str, Any]:
        """
        Export evidence metadata.

        Returns:
            Metadata dictionary
        """
        return {
            "work_item_id": self.work_item_id,
            "base_path": self.base_path,
            "collected_at": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "items": [item.to_dict() for item in self.evidence_items],
        }

    def clear(self):
        """Clear all evidence items."""
        self.evidence_items.clear()
        self.logger.info("Cleared all evidence items")
