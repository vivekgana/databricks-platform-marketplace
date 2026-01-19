"""
State Reader for Work Items

Reads work item states from agile tools and maps them to workflow stages.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any

from ai_sdlc.plugins.base import WorkItemPlugin
from ai_sdlc.plugins.models import WorkItem as PluginWorkItem

from .state_machine import ADOState, WorkflowStage, STAGE_TO_ADO_STATE

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStateInfo:
    """
    Information about the current workflow state for a work item.
    """

    work_item_id: str
    work_item_type: str
    title: str
    current_ado_state: ADOState
    suggested_workflow_stage: Optional[WorkflowStage]
    last_updated: datetime
    assigned_to: Optional[str] = None
    description: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class StateReader:
    """
    Reads work item states from agile tools and maps to workflow stages.
    """

    def __init__(self, agile_plugin: WorkItemPlugin, config: Dict[str, Any]):
        """
        Initialize the state reader.

        Args:
            agile_plugin: Work item management plugin (ADO, JIRA, GitHub, etc.)
            config: Configuration dictionary
        """
        self.agile_plugin = agile_plugin
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def read_work_item_state(self, work_item_id: str) -> WorkflowStateInfo:
        """
        Read the current state of a work item from the agile tool.

        Args:
            work_item_id: The work item ID

        Returns:
            WorkflowStateInfo with current state information

        Raises:
            ValueError: If work item not found or invalid
        """
        try:
            # Get work item from plugin
            work_item = self.agile_plugin.get_work_item(work_item_id)

            if not work_item:
                raise ValueError(f"Work item {work_item_id} not found")

            # Parse state
            ado_state = self._parse_ado_state(work_item.state)

            # Map to workflow stage
            workflow_stage = self._map_ado_state_to_workflow_stage(ado_state, work_item)

            # Extract tags
            tags = work_item.tags if work_item.tags else []

            return WorkflowStateInfo(
                work_item_id=work_item_id,
                work_item_type=work_item.item_type,
                title=work_item.title,
                current_ado_state=ado_state,
                suggested_workflow_stage=workflow_stage,
                last_updated=work_item.updated_date or datetime.now(),
                assigned_to=work_item.assigned_to,
                description=work_item.description or "",
                tags=tags,
            )

        except Exception as e:
            self.logger.error(f"Error reading work item {work_item_id}: {e}")
            raise

    def _parse_ado_state(self, state_string: str) -> ADOState:
        """
        Parse ADO state string to ADOState enum.

        Args:
            state_string: The state string from ADO

        Returns:
            ADOState enum value

        Raises:
            ValueError: If state string is invalid
        """
        # Normalize state string
        state_normalized = state_string.strip()

        # Try to match to ADOState
        for ado_state in ADOState:
            if ado_state.value.lower() == state_normalized.lower():
                return ado_state

        # If no exact match, try partial matching
        state_lower = state_normalized.lower()
        if "new" in state_lower:
            return ADOState.NEW
        elif "plan" in state_lower:
            return ADOState.PLANNING
        elif "dev" in state_lower or "progress" in state_lower:
            return ADOState.IN_DEVELOPMENT
        elif "test" in state_lower:
            return ADOState.TESTING
        elif "done" in state_lower or "complete" in state_lower:
            return ADOState.DONE

        raise ValueError(f"Unknown ADO state: {state_string}")

    def _map_ado_state_to_workflow_stage(
        self, ado_state: ADOState, work_item: WorkItem
    ) -> Optional[WorkflowStage]:
        """
        Map ADO state to suggested workflow stage.

        This uses the ADO state and work item metadata to suggest the next
        appropriate workflow stage.

        Args:
            ado_state: The current ADO state
            work_item: The work item

        Returns:
            Suggested WorkflowStage or None if cannot determine
        """
        # Check for workflow stage marker in tags or custom fields
        # (In production, you might store current workflow stage in a custom field)

        # Default mapping based on ADO state
        stage_mapping = {
            ADOState.NEW: WorkflowStage.PLANNING,
            ADOState.PLANNING: WorkflowStage.PLANNING,
            ADOState.IN_DEVELOPMENT: WorkflowStage.CODE_GENERATION,
            ADOState.TESTING: WorkflowStage.QA_TESTING,
            ADOState.DONE: WorkflowStage.COMPLETE,
        }

        return stage_mapping.get(ado_state)

    def should_start_workflow(self, work_item_id: str) -> tuple[bool, str]:
        """
        Determine if workflow should be started for a work item.

        Args:
            work_item_id: The work item ID

        Returns:
            Tuple of (should_start, reason)
        """
        try:
            state_info = self.read_work_item_state(work_item_id)

            # Check if in appropriate state
            if state_info.current_ado_state == ADOState.NEW:
                return True, "Work item is new and ready for workflow"

            if state_info.current_ado_state == ADOState.PLANNING:
                return True, "Work item is in planning state"

            # Check if already in progress or done
            if state_info.current_ado_state == ADOState.DONE:
                return False, "Work item is already completed"

            # If in development or testing, workflow might be in progress
            return (
                True,
                f"Work item is in {state_info.current_ado_state.value} - can resume workflow",
            )

        except Exception as e:
            return False, f"Error checking work item state: {e}"

    def find_work_items_ready_for_workflow(
        self, work_item_type: Optional[str] = None
    ) -> List[WorkflowStateInfo]:
        """
        Find work items that are ready to start workflow.

        Args:
            work_item_type: Optional filter by work item type (Epic, Feature, PBI, etc.)

        Returns:
            List of WorkflowStateInfo for work items ready for workflow
        """
        try:
            # Build WIQL query
            type_filter = (
                f"AND [System.WorkItemType] = '{work_item_type}'"
                if work_item_type
                else ""
            )

            wiql_query = f"""
            SELECT [System.Id], [System.Title], [System.State]
            FROM WorkItems
            WHERE [System.TeamProject] = '{self.config.project}'
            AND [System.State] IN ('New', 'Planning', 'In Development')
            {type_filter}
            ORDER BY [System.ChangedDate] DESC
            """

            # Execute query
            work_item_ids = self.ado_plugin.query_work_items(wiql_query, self.config)

            # Get full state info for each
            state_infos = []
            for work_item_id in work_item_ids:
                try:
                    state_info = self.read_work_item_state(str(work_item_id))
                    state_infos.append(state_info)
                except Exception as e:
                    self.logger.warning(
                        f"Could not read state for work item {work_item_id}: {e}"
                    )

            return state_infos

        except Exception as e:
            self.logger.error(f"Error finding work items ready for workflow: {e}")
            return []

    def get_workflow_stage_from_work_item(
        self, work_item_id: str
    ) -> Optional[WorkflowStage]:
        """
        Get the current workflow stage for a work item.

        This attempts to read a custom field or tag that tracks the exact workflow stage.

        Args:
            work_item_id: The work item ID

        Returns:
            Current WorkflowStage or None if not tracked
        """
        try:
            work_item = self.ado_plugin.get_work_item(work_item_id, self.config)

            # Check for custom field (would need to be configured in ADO)
            # For now, use tags
            if hasattr(work_item, "tags") and work_item.tags:
                tags = [tag.strip().lower() for tag in work_item.tags.split(";")]

                # Look for workflow stage tags
                for tag in tags:
                    if tag.startswith("workflow:"):
                        stage_name = tag.replace("workflow:", "")
                        try:
                            return WorkflowStage(stage_name)
                        except ValueError:
                            pass

            # Fall back to ADO state mapping
            state_info = self.read_work_item_state(work_item_id)
            return state_info.suggested_workflow_stage

        except Exception as e:
            self.logger.error(
                f"Error getting workflow stage for work item {work_item_id}: {e}"
            )
            return None

    def update_workflow_stage_tag(
        self, work_item_id: str, stage: WorkflowStage
    ) -> bool:
        """
        Update the work item with a workflow stage tag.

        Args:
            work_item_id: The work item ID
            stage: The current workflow stage

        Returns:
            True if successful, False otherwise
        """
        try:
            work_item = self.ado_plugin.get_work_item(work_item_id, self.config)

            # Get existing tags
            existing_tags = []
            if hasattr(work_item, "tags") and work_item.tags:
                existing_tags = [
                    tag.strip()
                    for tag in work_item.tags.split(";")
                    if not tag.strip().lower().startswith("workflow:")
                ]

            # Add new workflow stage tag
            new_tags = existing_tags + [f"workflow:{stage.value}"]
            tags_string = "; ".join(new_tags)

            # Update work item
            updates = {"tags": tags_string}
            self.ado_plugin.update_work_item(work_item_id, self.config, **updates)

            self.logger.info(
                f"Updated work item {work_item_id} with workflow stage: {stage.value}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error updating workflow stage tag for work item {work_item_id}: {e}"
            )
            return False
