"""
Data models for AI-SDLC plugin system.

Provides universal data structures that work across all agile/DevOps tools.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class WorkItemState(Enum):
    """Universal work item states."""

    NEW = "new"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    DONE = "done"
    CLOSED = "closed"


class WorkItemType(Enum):
    """Universal work item types."""

    EPIC = "epic"
    FEATURE = "feature"
    STORY = "story"
    TASK = "task"
    BUG = "bug"
    ENABLER = "enabler"


class PullRequestState(Enum):
    """Universal pull request states."""

    OPEN = "open"
    MERGED = "merged"
    CLOSED = "closed"
    DRAFT = "draft"


class PipelineStatus(Enum):
    """Universal pipeline run statuses."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


@dataclass
class WorkItem:
    """Universal work item representation."""

    id: str
    title: str
    description: str
    state: str
    assigned_to: Optional[str] = None
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    item_type: str = "task"
    parent_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    url: str = ""
    tool_name: str = ""  # Which tool this came from (ado, jira, github)


@dataclass
class WorkItemUpdate:
    """Work item update request."""

    state: Optional[str] = None
    assigned_to: Optional[str] = None
    comment: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class PullRequest:
    """Universal pull request representation."""

    id: str
    title: str
    description: str
    source_branch: str
    target_branch: str
    state: str
    author: str
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    url: str = ""
    work_item_ids: List[str] = field(default_factory=list)
    reviewers: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    tool_name: str = ""


@dataclass
class Artifact:
    """Universal artifact representation."""

    name: str
    version: str
    url: str
    size_bytes: int = 0
    created_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_name: str = ""


@dataclass
class PipelineRun:
    """Universal pipeline run representation."""

    id: str
    pipeline_name: str
    status: str
    started_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    url: str = ""
    duration_seconds: Optional[int] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    tool_name: str = ""


@dataclass
class Comment:
    """Universal comment representation."""

    id: str
    content: str
    author: str
    created_date: datetime
    updated_date: Optional[datetime] = None
    parent_id: Optional[str] = None  # For threaded comments


@dataclass
class Attachment:
    """Universal attachment representation."""

    id: str
    filename: str
    url: str
    size_bytes: int
    content_type: str
    created_date: datetime
    created_by: str
