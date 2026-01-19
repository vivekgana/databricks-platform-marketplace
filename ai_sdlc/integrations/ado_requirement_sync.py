"""
Azure DevOps Work Item <-> Requirement Synchronization

Enables bidirectional sync between REQ-*.md files and Azure DevOps work items.
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..parsers.requirement_parser import Requirement, RequirementParser, RequirementStatus
from ...plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import (
    AzureDevOpsPlugin,
)
from ...plugins.databricks_devops_integrations.sdk.base_plugin import (
    PluginConfig,
    WorkItem,
    WorkItemStatus,
    WorkItemPriority,
)


@dataclass
class ADOWorkItemReference:
    """Parsed Azure DevOps work item reference."""

    organization: str
    project: str
    work_item_id: str
    url: str

    @classmethod
    def parse_url(cls, ado_url: str) -> Optional["ADOWorkItemReference"]:
        """
        Parse Azure DevOps work item URL.

        Example: https://dev.azure.com/symphonyvsts/Audit%20Cortex%202/_workitems/edit/6340168

        Returns:
            Parsed reference or None if invalid URL
        """
        # Pattern: https://dev.azure.com/{org}/{project}/_workitems/edit/{id}
        pattern = r"https://dev\.azure\.com/([^/]+)/([^/]+)/_workitems/edit/(\d+)"
        match = re.match(pattern, ado_url)

        if not match:
            return None

        org, project, work_item_id = match.groups()

        # URL decode project name (spaces encoded as %20)
        project = project.replace("%20", " ")

        return cls(
            organization=org,
            project=project,
            work_item_id=work_item_id,
            url=ado_url,
        )


class ADORequirementSync:
    """Synchronize requirements with Azure DevOps work items."""

    def __init__(
        self,
        ado_plugin: AzureDevOpsPlugin,
        config: PluginConfig,
        req_parser: Optional[RequirementParser] = None,
    ):
        """
        Initialize ADO requirement synchronizer.

        Args:
            ado_plugin: Configured Azure DevOps plugin
            config: Plugin configuration
            req_parser: Requirement parser (creates new if not provided)
        """
        self.ado_plugin = ado_plugin
        self.config = config
        self.req_parser = req_parser or RequirementParser()
        self.logger = logging.getLogger(__name__)

    def link_requirement_to_ado(
        self, requirement: Requirement, create_if_missing: bool = False
    ) -> Optional[str]:
        """
        Link requirement to Azure DevOps work item.

        Args:
            requirement: Requirement to link
            create_if_missing: If True, create ADO work item if ado_link is missing

        Returns:
            Work item URL or None if failed
        """
        # If requirement already has ADO link, validate it
        if requirement.ado_link:
            ado_ref = ADOWorkItemReference.parse_url(requirement.ado_link)
            if ado_ref:
                # Verify work item exists
                try:
                    self.ado_plugin.get_work_item(ado_ref.work_item_id, self.config)
                    self.logger.info(
                        f"Requirement {requirement.req_id} already linked to ADO {ado_ref.work_item_id}"
                    )
                    return requirement.ado_link
                except Exception as e:
                    self.logger.warning(
                        f"ADO work item {ado_ref.work_item_id} not found: {e}"
                    )

        # Create new ADO work item if requested
        if create_if_missing:
            return self._create_ado_work_item_from_requirement(requirement)

        return None

    def _create_ado_work_item_from_requirement(
        self, requirement: Requirement
    ) -> Optional[str]:
        """
        Create Azure DevOps work item from requirement.

        Args:
            requirement: Requirement to create work item from

        Returns:
            Work item URL or None if failed
        """
        try:
            # Build description with requirement details
            description = self._build_ado_description(requirement)

            # Map requirement priority to ADO priority
            priority = self._map_requirement_priority_to_ado(requirement.priority.value)

            # Map requirement status to ADO status
            status = self._map_requirement_status_to_ado(requirement.status)

            # Create work item
            work_item = WorkItem(
                id="",
                title=f"[{requirement.req_id}] {requirement.title}",
                description=description,
                status=status,
                assignee=requirement.owner,
                priority=priority,
                labels=[
                    "requirement",
                    requirement.req_id,
                    requirement.product,
                    requirement.team,
                ],
                story_points=self._estimate_story_points(requirement),
                custom_fields={
                    "work_item_type": "User Story",  # Requirements are user stories
                    "/fields/Custom.RequirementID": requirement.req_id,
                    "/fields/Custom.TargetRelease": requirement.target_release,
                },
            )

            # Create work item in ADO
            work_item_id = self.ado_plugin.create_work_item(work_item, self.config)

            # Build work item URL
            ado_url = f"https://dev.azure.com/{self.config.organization}/{self.config.project}/_workitems/edit/{work_item_id}"

            self.logger.info(
                f"Created ADO work item {work_item_id} for requirement {requirement.req_id}"
            )

            return ado_url

        except Exception as e:
            self.logger.error(
                f"Failed to create ADO work item for requirement {requirement.req_id}: {e}"
            )
            return None

    def sync_requirement_to_ado(
        self, requirement: Requirement, ado_url: str
    ) -> bool:
        """
        Sync requirement changes to existing ADO work item.

        Args:
            requirement: Requirement with updated data
            ado_url: Azure DevOps work item URL

        Returns:
            True if sync succeeded
        """
        ado_ref = ADOWorkItemReference.parse_url(ado_url)
        if not ado_ref:
            self.logger.error(f"Invalid ADO URL: {ado_url}")
            return False

        try:
            # Build updates
            updates = {
                "title": f"[{requirement.req_id}] {requirement.title}",
                "description": self._build_ado_description(requirement),
                "status": self._map_requirement_status_to_ado(requirement.status),
                "priority": self._map_requirement_priority_to_ado(
                    requirement.priority.value
                ),
                "assignee": requirement.owner,
                "labels": [
                    "requirement",
                    requirement.req_id,
                    requirement.product,
                    requirement.team,
                ],
            }

            # Update work item
            self.ado_plugin.update_work_item(
                ado_ref.work_item_id, updates, self.config
            )

            self.logger.info(
                f"Synced requirement {requirement.req_id} to ADO {ado_ref.work_item_id}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to sync requirement {requirement.req_id} to ADO: {e}"
            )
            return False

    def sync_ado_to_requirement(
        self, ado_url: str, requirement_file: Path
    ) -> Optional[Dict]:
        """
        Sync ADO work item changes back to requirement file.

        Args:
            ado_url: Azure DevOps work item URL
            requirement_file: Path to REQ-*.md file

        Returns:
            Dictionary of changes made, or None if failed
        """
        ado_ref = ADOWorkItemReference.parse_url(ado_url)
        if not ado_ref:
            self.logger.error(f"Invalid ADO URL: {ado_url}")
            return None

        try:
            # Get current work item from ADO
            work_item = self.ado_plugin.get_work_item(
                ado_ref.work_item_id, self.config
            )

            # Parse existing requirement file
            requirement = self.req_parser.parse_file(str(requirement_file))

            # Detect changes
            changes = {}

            # Check status
            req_status = self._map_ado_status_to_requirement(work_item.status)
            if req_status != requirement.status.value:
                changes["status"] = {
                    "old": requirement.status.value,
                    "new": req_status,
                }

            # Check assignee
            if work_item.assignee != requirement.owner:
                changes["owner"] = {
                    "old": requirement.owner,
                    "new": work_item.assignee,
                }

            # Log changes
            if changes:
                self.logger.info(
                    f"Detected changes from ADO {ado_ref.work_item_id} to requirement {requirement.req_id}: {changes}"
                )
            else:
                self.logger.info(
                    f"No changes detected for requirement {requirement.req_id}"
                )

            return changes if changes else None

        except Exception as e:
            self.logger.error(f"Failed to sync ADO to requirement: {e}")
            return None

    def search_ado_by_requirement_id(self, req_id: str) -> Optional[WorkItem]:
        """
        Search for ADO work item by requirement ID.

        Args:
            req_id: Requirement ID (e.g., "REQ-101")

        Returns:
            Work item if found, None otherwise
        """
        try:
            # Search by title containing req_id
            work_items = self.ado_plugin.search_work_items(
                query=req_id, config=self.config, limit=10
            )

            # Filter to exact matches
            for work_item in work_items:
                if req_id in work_item.title:
                    return work_item

            return None

        except Exception as e:
            self.logger.error(f"Failed to search ADO for requirement {req_id}: {e}")
            return None

    def validate_ado_link(self, ado_url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that ADO link is accessible and correct.

        Args:
            ado_url: Azure DevOps work item URL

        Returns:
            Tuple of (is_valid, error_message)
        """
        ado_ref = ADOWorkItemReference.parse_url(ado_url)
        if not ado_ref:
            return False, f"Invalid ADO URL format: {ado_url}"

        # Check organization matches config
        if ado_ref.organization != self.config.organization:
            return (
                False,
                f"Organization mismatch: URL has '{ado_ref.organization}' but config has '{self.config.organization}'",
            )

        # Check project matches config
        if ado_ref.project != self.config.project:
            return (
                False,
                f"Project mismatch: URL has '{ado_ref.project}' but config has '{self.config.project}'",
            )

        # Check work item exists
        try:
            self.ado_plugin.get_work_item(ado_ref.work_item_id, self.config)
            return True, None
        except Exception as e:
            return False, f"Work item {ado_ref.work_item_id} not found: {e}"

    # Helper methods
    def _build_ado_description(self, requirement: Requirement) -> str:
        """Build ADO work item description from requirement."""
        desc = f"<h2>{requirement.title}</h2>\n\n"

        # Problem statement
        if requirement.problem_statement:
            desc += f"<h3>Problem Statement</h3>\n<p>{requirement.problem_statement}</p>\n\n"

        # Acceptance criteria
        if requirement.acceptance_criteria:
            desc += "<h3>Acceptance Criteria</h3>\n<ul>\n"
            for ac in requirement.acceptance_criteria:
                desc += f"<li><strong>{ac.id}:</strong> {ac.given} / {ac.when} / {ac.then}</li>\n"
            desc += "</ul>\n\n"

        # Links
        desc += f"<p><em>Requirement ID:</em> <strong>{requirement.req_id}</strong></p>\n"
        desc += f"<p><em>Target Release:</em> {requirement.target_release}</p>\n"

        if requirement.docs_link:
            desc += f'<p><a href="{requirement.docs_link}">View full requirement documentation</a></p>\n'

        return desc

    def _map_requirement_priority_to_ado(self, priority: str) -> WorkItemPriority:
        """Map requirement priority to ADO priority."""
        mapping = {
            "P1": WorkItemPriority.CRITICAL,
            "P2": WorkItemPriority.HIGH,
            "P3": WorkItemPriority.MEDIUM,
        }
        return mapping.get(priority, WorkItemPriority.MEDIUM)

    def _map_requirement_status_to_ado(self, status: RequirementStatus) -> WorkItemStatus:
        """Map requirement status to ADO status."""
        mapping = {
            RequirementStatus.DRAFT: WorkItemStatus.TODO,
            RequirementStatus.IN_REVIEW: WorkItemStatus.IN_REVIEW,
            RequirementStatus.APPROVED: WorkItemStatus.TODO,
            RequirementStatus.IN_DEV: WorkItemStatus.IN_PROGRESS,
            RequirementStatus.IN_QA: WorkItemStatus.IN_REVIEW,
            RequirementStatus.READY_FOR_DEMO: WorkItemStatus.IN_REVIEW,
            RequirementStatus.DONE: WorkItemStatus.DONE,
        }
        return mapping.get(status, WorkItemStatus.TODO)

    def _map_ado_status_to_requirement(self, status: WorkItemStatus) -> str:
        """Map ADO status back to requirement status."""
        mapping = {
            WorkItemStatus.TODO: "Approved",
            WorkItemStatus.IN_PROGRESS: "In Dev",
            WorkItemStatus.IN_REVIEW: "In QA",
            WorkItemStatus.DONE: "Done",
            WorkItemStatus.CANCELLED: "Draft",  # Fallback
            WorkItemStatus.BLOCKED: "In Review",  # Fallback
        }
        return mapping.get(status, "Draft")

    def _estimate_story_points(self, requirement: Requirement) -> float:
        """
        Estimate story points based on requirement complexity.

        Simple heuristic:
        - Base points: 3
        - +1 for each AC
        - +2 if > 5 functional requirements
        - +1 if demo evidence required
        """
        points = 3.0  # Base

        # Add for acceptance criteria
        points += len(requirement.acceptance_criteria)

        # Add for functional requirements
        if len(requirement.functional_requirements) > 5:
            points += 2.0

        # Add for demo evidence
        if requirement.demo:
            points += 1.0

        # Cap at 13 (Fibonacci)
        return min(points, 13.0)
