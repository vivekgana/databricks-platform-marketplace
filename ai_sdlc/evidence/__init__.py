"""
Evidence Management System

Provides evidence collection, storage, and formatting for workflow artifacts.
"""

from .evidence_collector import EvidenceCollector, EvidenceItem, EvidenceCategory
from .evidence_storage import (
    EvidenceStorage,
    AzureBlobEvidenceStorage,
    LocalFileEvidenceStorage,
)
from .evidence_formatter import EvidenceFormatter, ADOCommentFormat
from .screenshot_manager import ScreenshotManager

__all__ = [
    "EvidenceCollector",
    "EvidenceItem",
    "EvidenceCategory",
    "EvidenceStorage",
    "AzureBlobEvidenceStorage",
    "LocalFileEvidenceStorage",
    "EvidenceFormatter",
    "ADOCommentFormat",
    "ScreenshotManager",
]
