"""
JIRA Plugin Adapter.

Integrates with JIRA Cloud/Server for agile project management.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ai_sdlc.plugins.base import WorkItemPlugin, PluginType, PluginCapability
from ai_sdlc.plugins.models import (
    WorkItem,
    WorkItemUpdate,
    Comment,
    Attachment,
)

logger = logging.getLogger(__name__)


class JiraAdapter(WorkItemPlugin):
    """JIRA plugin adapter."""

    def __init__(self):
        super().__init__()
        self.jira_client = None
        self.project_key = None
        self.url = None

    def get_name(self) -> str:
        return "jira"

    def get_type(self) -> PluginType:
        return PluginType.AGILE

    def get_capabilities(self) -> List[PluginCapability]:
        return [PluginCapability.WORK_ITEM_MANAGEMENT]

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate JIRA configuration."""
        required = ["url", "project_key", "email", "api_token"]
        return all(k in config for k in required)

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize JIRA client."""
        try:
            from jira import JIRA

            self.url = config["url"]
            self.project_key = config["project_key"]

            self.jira_client = JIRA(
                server=self.url,
                basic_auth=(config["email"], config["api_token"]),
            )

            self.config = config
            self.initialized = True
            logger.info(
                f"Initialized JIRA adapter for {self.url} project {self.project_key}"
            )
            return True

        except ImportError:
            logger.error(
                "JIRA Python library not installed. Install with: pip install jira"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to initialize JIRA adapter: {e}")
            return False

    def get_work_item(self, work_item_id: str) -> WorkItem:
        """Get issue from JIRA."""
        issue = self.jira_client.issue(work_item_id)

        return WorkItem(
            id=issue.key,
            title=issue.fields.summary,
            description=issue.fields.description or "",
            state=issue.fields.status.name,
            assigned_to=(
                issue.fields.assignee.displayName if issue.fields.assignee else None
            ),
            created_date=self._parse_date(issue.fields.created),
            updated_date=self._parse_date(issue.fields.updated),
            item_type=issue.fields.issuetype.name,
            parent_id=(
                issue.fields.parent.key if hasattr(issue.fields, "parent") else None
            ),
            tags=[label for label in issue.fields.labels],
            custom_fields=self._extract_custom_fields(issue),
            url=f"{self.url}/browse/{issue.key}",
            tool_name="jira",
        )

    def create_work_item(
        self,
        title: str,
        description: str,
        item_type: str,
        parent_id: Optional[str] = None,
        assigned_to: Optional[str] = None,
        **kwargs,
    ) -> WorkItem:
        """Create issue in JIRA."""
        issue_dict = {
            "project": {"key": self.project_key},
            "summary": title,
            "description": description,
            "issuetype": {"name": self._map_item_type(item_type)},
        }

        if assigned_to:
            issue_dict["assignee"] = {"name": assigned_to}

        if parent_id:
            issue_dict["parent"] = {"key": parent_id}

        # Add custom fields
        for key, value in kwargs.items():
            issue_dict[key] = value

        new_issue = self.jira_client.create_issue(fields=issue_dict)
        return self.get_work_item(new_issue.key)

    def update_work_item(self, work_item_id: str, update: WorkItemUpdate) -> WorkItem:
        """Update issue in JIRA."""
        issue = self.jira_client.issue(work_item_id)
        update_dict = {}

        if update.title:
            update_dict["summary"] = update.title

        if update.description:
            update_dict["description"] = update.description

        if update.state:
            # Transition to new state
            transitions = self.jira_client.transitions(issue)
            transition_id = None
            for t in transitions:
                if t["name"].lower() == update.state.lower():
                    transition_id = t["id"]
                    break

            if transition_id:
                self.jira_client.transition_issue(issue, transition_id)

        if update.assigned_to:
            update_dict["assignee"] = {"name": update.assigned_to}

        if update.tags:
            update_dict["labels"] = update.tags

        if update.custom_fields:
            update_dict.update(update.custom_fields)

        if update_dict:
            issue.update(fields=update_dict)

        if update.comment:
            self.add_comment(work_item_id, update.comment)

        return self.get_work_item(work_item_id)

    def add_comment(self, work_item_id: str, comment: str) -> Comment:
        """Add comment to issue."""
        jira_comment = self.jira_client.add_comment(work_item_id, comment)

        return Comment(
            id=jira_comment.id,
            content=comment,
            author=jira_comment.author.displayName,
            created_date=self._parse_date(jira_comment.created),
        )

    def attach_file(
        self, work_item_id: str, file_path: str, comment: Optional[str] = None
    ) -> Attachment:
        """Attach file to issue."""
        attachment = self.jira_client.add_attachment(
            issue=work_item_id, attachment=file_path
        )

        if comment:
            self.add_comment(work_item_id, comment)

        return Attachment(
            id=attachment.id,
            filename=attachment.filename,
            url=attachment.content,
            size_bytes=attachment.size,
            content_type=attachment.mimeType,
            created_date=self._parse_date(attachment.created),
            created_by=attachment.author.displayName,
        )

    def get_children(self, work_item_id: str) -> List[WorkItem]:
        """Get child issues (subtasks)."""
        issue = self.jira_client.issue(work_item_id)
        children = []

        if hasattr(issue.fields, "subtasks"):
            for subtask in issue.fields.subtasks:
                children.append(self.get_work_item(subtask.key))

        return children

    def link_work_items(self, source_id: str, target_id: str, link_type: str) -> bool:
        """Link issues in JIRA."""
        try:
            # Map generic link types to JIRA link types
            link_type_map = {
                "related": "Relates",
                "blocks": "Blocks",
                "blocked_by": "Blocked",
                "parent": "Parent",
                "child": "Child",
            }

            jira_link_type = link_type_map.get(link_type, "Relates")

            self.jira_client.create_issue_link(
                type=jira_link_type,
                inwardIssue=source_id,
                outwardIssue=target_id,
            )
            return True

        except Exception as e:
            logger.error(f"Failed to link issues: {e}")
            return False

    def search_work_items(self, query: str, max_results: int = 100) -> List[WorkItem]:
        """Search issues using JQL."""
        jql = f'project = {self.project_key} AND text ~ "{query}" ORDER BY updated DESC'

        issues = self.jira_client.search_issues(jql, maxResults=max_results)
        return [self.get_work_item(issue.key) for issue in issues]

    # Helper methods
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse JIRA date string."""
        if not date_str:
            return None

        try:
            # JIRA uses ISO 8601 with timezone
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None

    def _map_item_type(self, generic_type: str) -> str:
        """Map generic item type to JIRA issue type."""
        type_map = {
            "epic": "Epic",
            "feature": "Story",
            "story": "Story",
            "task": "Task",
            "bug": "Bug",
            "enabler": "Task",
        }
        return type_map.get(generic_type.lower(), "Task")

    def _extract_custom_fields(self, issue) -> Dict[str, Any]:
        """Extract custom fields from JIRA issue."""
        custom_fields = {}

        # Get all fields
        for field_name in dir(issue.fields):
            if field_name.startswith("customfield_"):
                value = getattr(issue.fields, field_name)
                if value is not None:
                    custom_fields[field_name] = str(value)

        return custom_fields
