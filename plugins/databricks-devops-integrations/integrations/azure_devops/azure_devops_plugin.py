"""
Azure DevOps Integration Plugin Implementation

Implements the DevOpsIntegrationPlugin interface for Microsoft Azure DevOps.
"""

import logging
import base64
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from azure.devops.connection import Connection
from azure.devops.v7_0.work_item_tracking import (
    Wiql,
    JsonPatchOperation,
)
from msrest.authentication import BasicAuthentication

from ...sdk.base_plugin import (
    DevOpsIntegrationPlugin,
    WorkItem,
    PluginConfig,
    PluginMetadata,
    WorkItemStatus,
    WorkItemPriority,
)
from ...sdk.exceptions import (
    AuthenticationError,
    ConfigurationError,
    WorkItemNotFoundError,
    IntegrationError,
)


class AzureDevOpsPlugin(DevOpsIntegrationPlugin):
    """Azure DevOps integration plugin"""

    def __init__(self):
        self.connection: Optional[Connection] = None
        self.work_item_client = None
        self.wit_client = None
        self.logger = logging.getLogger(__name__)

    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        return PluginMetadata(
            name="Azure DevOps Integration",
            version="1.0.0",
            description="Microsoft Azure DevOps integration for work item tracking",
            author="Databricks Platform Team",
            supported_features=[
                "work_items",
                "boards",
                "sprints",
                "incidents",
                "commits",
                "pull_requests",
                "team_velocity",
                "webhooks",
            ],
            requires_auth=True,
            documentation_url="https://docs.yourcompany.com/plugins/azure-devops",
        )

    def authenticate(self, config: PluginConfig) -> bool:
        """Authenticate with Azure DevOps"""
        try:
            credentials = BasicAuthentication("", config.api_key)
            self.connection = Connection(
                base_url=config.api_endpoint, creds=credentials
            )
            self.work_item_client = (
                self.connection.clients.get_work_item_tracking_client()
            )
            self.wit_client = self.work_item_client

            # Test authentication by getting a project
            self.connection.clients.get_core_client().get_project(config.project)

            self.logger.info("Successfully authenticated with Azure DevOps")
            return True

        except Exception as e:
            self.logger.error(f"Azure DevOps authentication failed: {e}")
            raise AuthenticationError(f"Failed to authenticate with Azure DevOps: {e}")

    def validate_config(self, config: PluginConfig) -> bool:
        """Validate plugin configuration"""
        required_fields = ["api_endpoint", "api_key", "organization", "project"]
        for field in required_fields:
            if not getattr(config, field, None):
                raise ConfigurationError(f"Missing required field: {field}")

        if not config.api_endpoint.startswith("https://"):
            raise ConfigurationError("API endpoint must use HTTPS")

        return True

    def create_work_item(self, work_item: WorkItem, config: PluginConfig) -> str:
        """Create Azure DevOps work item"""
        if not self.work_item_client:
            self.authenticate(config)

        try:
            # Build JSON Patch document
            document = [
                JsonPatchOperation(
                    op="add", path="/fields/System.Title", value=work_item.title
                ),
                JsonPatchOperation(
                    op="add",
                    path="/fields/System.Description",
                    value=work_item.description,
                ),
                JsonPatchOperation(
                    op="add",
                    path="/fields/Microsoft.VSTS.Common.Priority",
                    value=self._map_priority_to_ado(work_item.priority),
                ),
            ]

            # Add assignee
            if work_item.assignee:
                document.append(
                    JsonPatchOperation(
                        op="add",
                        path="/fields/System.AssignedTo",
                        value=work_item.assignee,
                    )
                )

            # Add tags/labels
            if work_item.labels:
                document.append(
                    JsonPatchOperation(
                        op="add",
                        path="/fields/System.Tags",
                        value="; ".join(work_item.labels),
                    )
                )

            # Add story points
            if work_item.story_points:
                document.append(
                    JsonPatchOperation(
                        op="add",
                        path="/fields/Microsoft.VSTS.Scheduling.StoryPoints",
                        value=work_item.story_points,
                    )
                )

            # Add custom fields
            for field_path, value in work_item.custom_fields.items():
                document.append(
                    JsonPatchOperation(op="add", path=field_path, value=value)
                )

            # Create work item (default type: Task)
            work_item_type = work_item.custom_fields.get("work_item_type", "Task")
            created_item = self.work_item_client.create_work_item(
                document=document, project=config.project, type=work_item_type
            )

            self.logger.info(f"Created Azure DevOps work item: {created_item.id}")
            return str(created_item.id)

        except Exception as e:
            self.logger.error(f"Failed to create Azure DevOps work item: {e}")
            raise IntegrationError(f"Failed to create work item in Azure DevOps: {e}")

    def update_work_item(
        self, item_id: str, updates: Dict[str, Any], config: PluginConfig
    ) -> bool:
        """Update existing Azure DevOps work item"""
        if not self.work_item_client:
            self.authenticate(config)

        try:
            document = []

            # Map updates to Azure DevOps fields
            if "title" in updates:
                document.append(
                    JsonPatchOperation(
                        op="replace",
                        path="/fields/System.Title",
                        value=updates["title"],
                    )
                )
            if "description" in updates:
                document.append(
                    JsonPatchOperation(
                        op="replace",
                        path="/fields/System.Description",
                        value=updates["description"],
                    )
                )
            if "status" in updates:
                document.append(
                    JsonPatchOperation(
                        op="replace",
                        path="/fields/System.State",
                        value=self._map_status_to_ado(updates["status"]),
                    )
                )
            if "priority" in updates:
                document.append(
                    JsonPatchOperation(
                        op="replace",
                        path="/fields/Microsoft.VSTS.Common.Priority",
                        value=self._map_priority_to_ado(updates["priority"]),
                    )
                )
            if "assignee" in updates:
                document.append(
                    JsonPatchOperation(
                        op="replace",
                        path="/fields/System.AssignedTo",
                        value=updates["assignee"],
                    )
                )
            if "labels" in updates:
                document.append(
                    JsonPatchOperation(
                        op="replace",
                        path="/fields/System.Tags",
                        value="; ".join(updates["labels"]),
                    )
                )

            if document:
                self.work_item_client.update_work_item(
                    document=document, id=int(item_id), project=config.project
                )

            self.logger.info(f"Updated Azure DevOps work item: {item_id}")
            return True

        except Exception as e:
            if "404" in str(e):
                raise WorkItemNotFoundError(f"Work item {item_id} not found")
            self.logger.error(f"Failed to update Azure DevOps work item: {e}")
            raise IntegrationError(f"Failed to update work item: {e}")

    def get_work_item(self, item_id: str, config: PluginConfig) -> WorkItem:
        """Retrieve Azure DevOps work item details"""
        if not self.work_item_client:
            self.authenticate(config)

        try:
            work_item = self.work_item_client.get_work_item(int(item_id), expand="All")
            return self._ado_work_item_to_work_item(work_item)

        except Exception as e:
            if "404" in str(e):
                raise WorkItemNotFoundError(f"Work item {item_id} not found")
            raise IntegrationError(f"Failed to retrieve work item: {e}")

    def search_work_items(
        self, query: str, config: PluginConfig, limit: int = 100
    ) -> List[WorkItem]:
        """Search for Azure DevOps work items"""
        if not self.work_item_client:
            self.authenticate(config)

        try:
            # Build WIQL query
            wiql_query = f"""
            SELECT [System.Id], [System.Title], [System.State]
            FROM WorkItems
            WHERE [System.TeamProject] = '{config.project}'
            AND [System.Title] CONTAINS '{query}'
            ORDER BY [System.ChangedDate] DESC
            """

            wiql = Wiql(query=wiql_query)
            result = self.work_item_client.query_by_wiql(wiql, top=limit)

            if not result.work_items:
                return []

            # Get full work item details
            work_item_ids = [item.id for item in result.work_items]
            work_items = self.work_item_client.get_work_items(
                ids=work_item_ids, expand="All"
            )

            return [self._ado_work_item_to_work_item(wi) for wi in work_items]

        except Exception as e:
            self.logger.error(f"Failed to search Azure DevOps work items: {e}")
            raise IntegrationError(f"Failed to search work items: {e}")

    def link_to_commit(
        self,
        item_id: str,
        commit_sha: str,
        repo_url: str,
        config: PluginConfig,
    ) -> bool:
        """Link Azure DevOps work item to git commit"""
        if not self.work_item_client:
            self.authenticate(config)

        try:
            # Add commit link as a comment
            commit_url = f"{repo_url}/commit/{commit_sha}"
            comment_text = (
                f"Linked to commit: <a href='{commit_url}'>{commit_sha[:7]}</a>"
            )

            document = [
                JsonPatchOperation(
                    op="add",
                    path="/fields/System.History",
                    value=comment_text,
                )
            ]

            self.work_item_client.update_work_item(
                document=document, id=int(item_id), project=config.project
            )

            self.logger.info(
                f"Linked Azure DevOps work item {item_id} to commit {commit_sha}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to link commit: {e}")
            raise IntegrationError(f"Failed to link commit: {e}")

    def link_to_pull_request(
        self, item_id: str, pr_url: str, config: PluginConfig
    ) -> bool:
        """Link Azure DevOps work item to pull request"""
        if not self.work_item_client:
            self.authenticate(config)

        try:
            # Create artifact link to PR
            document = [
                JsonPatchOperation(
                    op="add",
                    path="/relations/-",
                    value={
                        "rel": "ArtifactLink",
                        "url": pr_url,
                        "attributes": {"name": "Pull Request"},
                    },
                )
            ]

            self.work_item_client.update_work_item(
                document=document, id=int(item_id), project=config.project
            )

            self.logger.info(f"Linked Azure DevOps work item {item_id} to PR {pr_url}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to link pull request: {e}")
            raise IntegrationError(f"Failed to link pull request: {e}")

    def create_from_incident(
        self, incident: Dict[str, Any], config: PluginConfig
    ) -> str:
        """Auto-create Azure DevOps work item from production incident"""

        # AI-powered root cause analysis
        root_cause = self._analyze_incident(incident)
        fix_suggestions = self._suggest_fixes(root_cause)

        description = f"""
        <h2>🚨 Automated Incident Report</h2>

        <p><strong>Incident:</strong> {incident.get('title', 'Unknown')}</p>
        <p><strong>Severity:</strong> {incident.get('severity', 'Unknown')}</p>
        <p><strong>Time:</strong> {incident.get('timestamp', 'Unknown')}</p>

        <h3>Root Cause Analysis:</h3>
        <p>{root_cause.get('summary', 'Analysis in progress')}</p>

        <h3>Affected Components:</h3>
        <p>{', '.join(root_cause.get('components', ['Unknown']))}</p>

        <h3>Suggested Fixes:</h3>
        {self._format_fixes_html(fix_suggestions)}

        <h3>Logs:</h3>
        <pre>{incident.get('logs', 'No logs available')[-500:]}</pre>

        <p><em>This work item was automatically created by DevPlatform AI</em></p>
        """

        work_item = WorkItem(
            id="",
            title=f"[AUTO] {incident.get('title', 'Production Incident')}",
            description=description,
            status=WorkItemStatus.TODO,
            assignee=self._get_component_owner(
                root_cause.get("components", ["Unknown"])[0]
            ),
            priority=self._map_severity_to_priority(incident.get("severity", "medium")),
            labels=["auto-generated", "incident", "production"],
            story_points=5.0,  # Default for incidents
            custom_fields={
                "work_item_type": "Bug",  # Incidents are bugs
            },
        )

        return self.create_work_item(work_item, config)

    def get_team_velocity(
        self, team_id: str, timeframe_days: int, config: PluginConfig
    ) -> Dict[str, float]:
        """Calculate team velocity from Azure DevOps"""
        if not self.work_item_client:
            self.authenticate(config)

        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=timeframe_days)

            # Build WIQL query for completed work items
            wiql_query = f"""
            SELECT [System.Id], [Microsoft.VSTS.Scheduling.StoryPoints]
            FROM WorkItems
            WHERE [System.TeamProject] = '{config.project}'
            AND [System.State] = 'Done'
            AND [System.ChangedDate] >= '{start_date.strftime('%Y-%m-%d')}'
            AND [System.AreaPath] UNDER '{config.project}\\{team_id}'
            """

            wiql = Wiql(query=wiql_query)
            result = self.work_item_client.query_by_wiql(wiql, top=1000)

            if not result.work_items:
                return {
                    "total_story_points": 0,
                    "avg_velocity": 0,
                    "issues_completed": 0,
                    "sprints": 0,
                    "timeframe_days": timeframe_days,
                }

            # Get work item details
            work_item_ids = [item.id for item in result.work_items]
            work_items = self.work_item_client.get_work_items(
                ids=work_item_ids, expand="All"
            )

            # Calculate metrics
            total_story_points = sum(
                float(wi.fields.get("Microsoft.VSTS.Scheduling.StoryPoints", 0) or 0)
                for wi in work_items
            )

            # Estimate sprints (assuming 2-week sprints)
            sprints_completed = max(1, timeframe_days // 14)

            return {
                "total_story_points": total_story_points,
                "avg_velocity": total_story_points / sprints_completed,
                "issues_completed": len(work_items),
                "sprints": sprints_completed,
                "timeframe_days": timeframe_days,
            }

        except Exception as e:
            self.logger.error(f"Failed to calculate velocity: {e}")
            raise IntegrationError(f"Failed to calculate team velocity: {e}")

    def webhook_handler(
        self, event_type: str, payload: Dict[str, Any], config: PluginConfig
    ) -> Dict[str, Any]:
        """Handle incoming webhooks from Azure DevOps"""
        self.logger.info(f"Received webhook event: {event_type}")

        handlers = {
            "workitem.created": self._handle_workitem_created,
            "workitem.updated": self._handle_workitem_updated,
            "workitem.deleted": self._handle_workitem_deleted,
            "git.push": self._handle_git_push,
            "git.pullrequest.created": self._handle_pr_created,
        }

        handler = handlers.get(event_type)
        if handler:
            return handler(payload, config)

        return {"status": "ignored", "event_type": event_type}

    # Helper methods
    def _map_priority_to_ado(self, priority: WorkItemPriority) -> int:
        """Map standard priority to Azure DevOps priority (1-4)"""
        mapping = {
            WorkItemPriority.CRITICAL: 1,
            WorkItemPriority.HIGH: 2,
            WorkItemPriority.MEDIUM: 3,
            WorkItemPriority.LOW: 4,
        }
        return mapping.get(priority, 3)

    def _map_ado_priority_to_standard(self, ado_priority: int) -> WorkItemPriority:
        """Map Azure DevOps priority to standard priority"""
        mapping = {
            1: WorkItemPriority.CRITICAL,
            2: WorkItemPriority.HIGH,
            3: WorkItemPriority.MEDIUM,
            4: WorkItemPriority.LOW,
        }
        return mapping.get(ado_priority, WorkItemPriority.MEDIUM)

    def _map_status_to_ado(self, status: WorkItemStatus) -> str:
        """Map standard status to Azure DevOps state"""
        mapping = {
            WorkItemStatus.TODO: "New",
            WorkItemStatus.IN_PROGRESS: "Active",
            WorkItemStatus.IN_REVIEW: "Resolved",
            WorkItemStatus.BLOCKED: "New",  # ADO doesn't have blocked state
            WorkItemStatus.DONE: "Closed",
            WorkItemStatus.CANCELLED: "Removed",
        }
        return mapping.get(status, "New")

    def _map_ado_status_to_standard(self, ado_status: str) -> WorkItemStatus:
        """Map Azure DevOps state to standard status"""
        status_lower = ado_status.lower()
        if status_lower in ["new", "approved", "proposed"]:
            return WorkItemStatus.TODO
        elif status_lower in ["active", "committed"]:
            return WorkItemStatus.IN_PROGRESS
        elif status_lower in ["resolved"]:
            return WorkItemStatus.IN_REVIEW
        elif status_lower in ["closed", "done"]:
            return WorkItemStatus.DONE
        elif status_lower in ["removed", "cut"]:
            return WorkItemStatus.CANCELLED
        return WorkItemStatus.TODO

    def _ado_work_item_to_work_item(self, ado_wi) -> WorkItem:
        """Convert Azure DevOps work item to WorkItem"""
        fields = ado_wi.fields

        # Parse dates
        created_at = None
        updated_at = None
        if "System.CreatedDate" in fields:
            created_at = datetime.fromisoformat(
                fields["System.CreatedDate"].replace("Z", "+00:00")
            )
        if "System.ChangedDate" in fields:
            updated_at = datetime.fromisoformat(
                fields["System.ChangedDate"].replace("Z", "+00:00")
            )

        # Parse tags
        tags = []
        if "System.Tags" in fields and fields["System.Tags"]:
            tags = [tag.strip() for tag in fields["System.Tags"].split(";")]

        return WorkItem(
            id=str(ado_wi.id),
            title=fields.get("System.Title", ""),
            description=fields.get("System.Description", ""),
            status=self._map_ado_status_to_standard(fields.get("System.State", "New")),
            assignee=(
                fields["System.AssignedTo"]["displayName"]
                if "System.AssignedTo" in fields
                else None
            ),
            priority=self._map_ado_priority_to_standard(
                fields.get("Microsoft.VSTS.Common.Priority", 3)
            ),
            labels=tags,
            created_at=created_at,
            updated_at=updated_at,
            url=ado_wi.url if hasattr(ado_wi, "url") else None,
            story_points=float(
                fields.get("Microsoft.VSTS.Scheduling.StoryPoints", 0) or 0
            ),
        )

    def _analyze_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze incident to determine root cause (placeholder)"""
        return {
            "summary": "Analysis based on error logs and metrics",
            "components": ["api-gateway", "database"],
            "confidence": 0.85,
        }

    def _suggest_fixes(self, root_cause: Dict[str, Any]) -> List[str]:
        """Suggest fixes based on root cause (placeholder)"""
        return [
            "Increase connection pool size",
            "Add retry logic for transient failures",
            "Review query performance",
        ]

    def _format_fixes_html(self, fixes: List[str]) -> str:
        """Format fix suggestions as HTML list"""
        return "<ul>" + "".join(f"<li>{fix}</li>" for fix in fixes) + "</ul>"

    def _get_component_owner(self, component: str) -> Optional[str]:
        """Get owner of a component (placeholder)"""
        return None

    def _map_severity_to_priority(self, severity: str) -> WorkItemPriority:
        """Map incident severity to work item priority"""
        mapping = {
            "critical": WorkItemPriority.CRITICAL,
            "high": WorkItemPriority.HIGH,
            "medium": WorkItemPriority.MEDIUM,
            "low": WorkItemPriority.LOW,
        }
        return mapping.get(severity.lower(), WorkItemPriority.MEDIUM)

    def _handle_workitem_created(
        self, payload: Dict[str, Any], config: PluginConfig
    ) -> Dict[str, Any]:
        """Handle work item created webhook"""
        work_item_id = payload.get("resource", {}).get("id")
        self.logger.info(f"Work item created: {work_item_id}")
        return {"status": "processed", "work_item_id": work_item_id}

    def _handle_workitem_updated(
        self, payload: Dict[str, Any], config: PluginConfig
    ) -> Dict[str, Any]:
        """Handle work item updated webhook"""
        work_item_id = payload.get("resource", {}).get("id")
        self.logger.info(f"Work item updated: {work_item_id}")
        return {"status": "processed", "work_item_id": work_item_id}

    def _handle_workitem_deleted(
        self, payload: Dict[str, Any], config: PluginConfig
    ) -> Dict[str, Any]:
        """Handle work item deleted webhook"""
        work_item_id = payload.get("resource", {}).get("id")
        self.logger.info(f"Work item deleted: {work_item_id}")
        return {"status": "processed", "work_item_id": work_item_id}

    def _handle_git_push(
        self, payload: Dict[str, Any], config: PluginConfig
    ) -> Dict[str, Any]:
        """Handle git push webhook"""
        return {"status": "processed", "event": "git.push"}

    def _handle_pr_created(
        self, payload: Dict[str, Any], config: PluginConfig
    ) -> Dict[str, Any]:
        """Handle pull request created webhook"""
        pr_id = payload.get("resource", {}).get("pullRequestId")
        self.logger.info(f"Pull request created: {pr_id}")
        return {"status": "processed", "pr_id": pr_id}

    # Evidence Management Methods
    def upload_attachment(
        self,
        work_item_id: str,
        file_path: str,
        comment: Optional[str] = None,
        config: Optional[PluginConfig] = None,
    ) -> str:
        """
        Upload a file as an attachment to a work item.

        Args:
            work_item_id: Work item ID
            file_path: Path to the file to upload
            comment: Optional comment to add with the attachment
            config: Plugin configuration

        Returns:
            URL of the uploaded attachment

        Raises:
            IntegrationError: If upload fails
        """
        if not self.work_item_client:
            if not config:
                raise IntegrationError("Configuration required for authentication")
            self.authenticate(config)

        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise IntegrationError(f"File not found: {file_path}")

            # Read file content
            with open(file_path, "rb") as f:
                file_content = f.read()

            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"

            # Upload attachment
            attachment = self.work_item_client.create_attachment(
                upload_stream=file_content,
                file_name=file_path_obj.name,
                upload_type=mime_type,
            )

            # Link attachment to work item
            document = [
                JsonPatchOperation(
                    op="add",
                    path="/relations/-",
                    value={
                        "rel": "AttachedFile",
                        "url": attachment.url,
                        "attributes": {
                            "comment": comment or f"Attachment: {file_path_obj.name}"
                        },
                    },
                )
            ]

            self.work_item_client.update_work_item(
                document=document, id=int(work_item_id)
            )

            self.logger.info(
                f"Uploaded attachment {file_path_obj.name} to work item {work_item_id}"
            )
            return attachment.url

        except Exception as e:
            self.logger.error(f"Failed to upload attachment: {e}")
            raise IntegrationError(f"Failed to upload attachment: {e}")

    def add_comment(
        self,
        work_item_id: str,
        comment: str,
        config: Optional[PluginConfig] = None,
    ) -> bool:
        """
        Add a plain text comment to a work item.

        Args:
            work_item_id: Work item ID
            comment: Comment text
            config: Plugin configuration

        Returns:
            True if successful

        Raises:
            IntegrationError: If adding comment fails
        """
        if not self.work_item_client:
            if not config:
                raise IntegrationError("Configuration required for authentication")
            self.authenticate(config)

        try:
            document = [
                JsonPatchOperation(
                    op="add", path="/fields/System.History", value=comment
                )
            ]

            self.work_item_client.update_work_item(
                document=document, id=int(work_item_id)
            )

            self.logger.info(f"Added comment to work item {work_item_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add comment: {e}")
            raise IntegrationError(f"Failed to add comment: {e}")

    def add_rich_comment(
        self,
        work_item_id: str,
        html_content: str,
        plain_text: Optional[str] = None,
        config: Optional[PluginConfig] = None,
    ) -> bool:
        """
        Add a rich HTML comment to a work item.

        Azure DevOps supports HTML in the System.History field.

        Args:
            work_item_id: Work item ID
            html_content: HTML formatted comment
            plain_text: Optional plain text fallback (not used in ADO but kept for API compatibility)
            config: Plugin configuration

        Returns:
            True if successful

        Raises:
            IntegrationError: If adding comment fails
        """
        if not self.work_item_client:
            if not config:
                raise IntegrationError("Configuration required for authentication")
            self.authenticate(config)

        try:
            # Azure DevOps System.History field supports HTML directly
            document = [
                JsonPatchOperation(
                    op="add", path="/fields/System.History", value=html_content
                )
            ]

            self.work_item_client.update_work_item(
                document=document, id=int(work_item_id)
            )

            self.logger.info(f"Added rich comment to work item {work_item_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add rich comment: {e}")
            raise IntegrationError(f"Failed to add rich comment: {e}")

    def update_work_item_with_evidence(
        self,
        work_item_id: str,
        evidence_summary: Dict[str, Any],
        stage: str,
        status: str,
        config: Optional[PluginConfig] = None,
    ) -> bool:
        """
        Update work item with evidence from a workflow stage.

        This is a convenience method that combines multiple operations:
        - Adds a rich comment with stage results
        - Updates work item description with evidence summary
        - Updates custom fields for workflow tracking

        Args:
            work_item_id: Work item ID
            evidence_summary: Evidence summary dictionary with:
                - evidence_items: List of evidence items
                - metrics: Dict of metrics
                - duration_seconds: Stage duration
            stage: Workflow stage name
            status: Stage status (passed/failed)
            config: Plugin configuration

        Returns:
            True if successful

        Raises:
            IntegrationError: If update fails
        """
        if not self.work_item_client:
            if not config:
                raise IntegrationError("Configuration required for authentication")
            self.authenticate(config)

        try:
            # Import here to avoid circular dependency
            from ai_sdlc.evidence import EvidenceFormatter, ADOCommentFormat

            # Format stage comment
            formatter = EvidenceFormatter(work_item_id)
            comment_html = formatter.format_stage_comment(
                stage=stage,
                status=status,
                duration_seconds=evidence_summary.get("duration_seconds", 0),
                evidence_items=evidence_summary.get("evidence_items", []),
                metrics=evidence_summary.get("metrics"),
                format_type=ADOCommentFormat.HTML,
            )

            # Add rich comment
            self.add_rich_comment(work_item_id, comment_html, config=config)

            # Update custom fields for workflow tracking
            document = [
                JsonPatchOperation(
                    op="add",
                    path="/fields/Custom.LastWorkflowStage",
                    value=stage,
                ),
                JsonPatchOperation(
                    op="add",
                    path="/fields/Custom.LastWorkflowStatus",
                    value=status,
                ),
                JsonPatchOperation(
                    op="add",
                    path="/fields/Custom.LastWorkflowUpdate",
                    value=datetime.now().isoformat(),
                ),
            ]

            self.work_item_client.update_work_item(
                document=document, id=int(work_item_id)
            )

            self.logger.info(
                f"Updated work item {work_item_id} with evidence from stage {stage}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to update work item with evidence: {e}")
            # Don't raise - evidence update shouldn't fail the workflow
            return False

    def upload_evidence_package(
        self,
        work_item_id: str,
        evidence_items: List[Any],  # List of EvidenceItem
        max_attachments: int = 3,
        config: Optional[PluginConfig] = None,
    ) -> Dict[str, Any]:
        """
        Upload a package of evidence files to a work item.

        This method intelligently selects the most important evidence items
        (e.g., key screenshots, reports) to upload as attachments.

        Args:
            work_item_id: Work item ID
            evidence_items: List of EvidenceItem objects
            max_attachments: Maximum number of attachments to upload (default: 3)
            config: Plugin configuration

        Returns:
            Dictionary with:
                - uploaded_count: Number of files uploaded
                - uploaded_urls: List of attachment URLs
                - skipped_count: Number of files skipped

        Raises:
            IntegrationError: If upload fails
        """
        if not self.work_item_client:
            if not config:
                raise IntegrationError("Configuration required for authentication")
            self.authenticate(config)

        try:
            # Import here to avoid circular dependency
            from ai_sdlc.evidence import ScreenshotManager, EvidenceCategory

            # Prioritize screenshots and reports
            priority_categories = [
                EvidenceCategory.SCREENSHOT,
                EvidenceCategory.REPORT,
            ]

            prioritized_items = []
            other_items = []

            for item in evidence_items:
                if item.category in priority_categories:
                    prioritized_items.append(item)
                else:
                    other_items.append(item)

            # For screenshots, use ScreenshotManager to select top ones
            screenshots = [
                item
                for item in prioritized_items
                if item.category == EvidenceCategory.SCREENSHOT
            ]
            if screenshots:
                screenshot_manager = ScreenshotManager()
                screenshots_dict = [
                    {
                        "filename": s.filename,
                        "path": s.path,
                        "size_bytes": s.size_bytes or 0,
                    }
                    for s in screenshots
                ]
                top_screenshots = screenshot_manager.select_top_screenshots(
                    screenshots_dict, max_count=max_attachments
                )
                selected_items = [
                    item
                    for item in screenshots
                    if item.filename in [s["filename"] for s in top_screenshots]
                ]
            else:
                # No screenshots, select from other priority items
                selected_items = prioritized_items[:max_attachments]

            # Upload selected items
            uploaded_urls = []
            for item in selected_items:
                try:
                    url = self.upload_attachment(
                        work_item_id=work_item_id,
                        file_path=item.path,
                        comment=f"{item.category.value}: {item.description or item.filename}",
                        config=config,
                    )
                    uploaded_urls.append(url)
                except Exception as e:
                    self.logger.warning(f"Failed to upload {item.filename}: {e}")

            result = {
                "uploaded_count": len(uploaded_urls),
                "uploaded_urls": uploaded_urls,
                "skipped_count": len(evidence_items) - len(uploaded_urls),
            }

            self.logger.info(
                f"Uploaded {result['uploaded_count']} evidence files to work item {work_item_id}"
            )
            return result

        except Exception as e:
            self.logger.error(f"Failed to upload evidence package: {e}")
            raise IntegrationError(f"Failed to upload evidence package: {e}")

    def create_artifact_package(
        self,
        work_item_id: str,
        artifact_name: str,
        artifact_version: str,
        evidence_items: List[Any],
        config: Optional[PluginConfig] = None,
    ) -> Dict[str, Any]:
        """
        Create a persistent artifact package in Azure Artifacts (Universal Packages).

        This creates a permanent artifact package that can be versioned and
        referenced across multiple work items, unlike simple attachments.

        Args:
            work_item_id: Work item ID to link artifact to
            artifact_name: Name of the artifact package (e.g., "pbi-6340168-evidence")
            artifact_version: Semantic version (e.g., "1.0.0")
            evidence_items: List of EvidenceItem objects to include
            config: Plugin configuration

        Returns:
            Dictionary with:
                - package_id: Universal Package ID
                - package_url: URL to access the package
                - version: Package version
                - files_count: Number of files in package
                - artifact_link: ADO artifact link URL

        Raises:
            IntegrationError: If artifact creation fails
        """
        if not self.connection:
            if not config:
                raise IntegrationError("Configuration required for authentication")
            self.authenticate(config)

        try:
            import tarfile
            import tempfile
            import json
            import requests
            from io import BytesIO

            # Get feed client for Universal Packages
            # Note: Azure DevOps Universal Packages use REST API, not Python SDK
            org_url = config.api_endpoint.rstrip("/")
            project = config.project
            pat = config.api_key

            # Create a feed if it doesn't exist (or use existing "ai-sdlc-evidence" feed)
            feed_name = "ai-sdlc-evidence"

            # Create temporary directory for artifact package
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                package_dir = temp_path / artifact_name

                package_dir.mkdir(parents=True, exist_ok=True)

                # Copy evidence files to package directory
                files_added = []
                for item in evidence_items:
                    if Path(item.path).exists():
                        try:
                            dest_path = package_dir / item.filename
                            # Create subdirectories if needed
                            dest_path.parent.mkdir(parents=True, exist_ok=True)

                            # Copy file
                            import shutil

                            shutil.copy2(item.path, dest_path)
                            files_added.append(
                                {
                                    "filename": item.filename,
                                    "category": item.category.value,
                                    "stage": item.stage,
                                    "size_bytes": item.size_bytes,
                                }
                            )
                        except Exception as e:
                            self.logger.warning(
                                f"Failed to add {item.filename} to package: {e}"
                            )

                # Create package metadata
                metadata = {
                    "work_item_id": work_item_id,
                    "created_at": datetime.now().isoformat(),
                    "artifact_name": artifact_name,
                    "version": artifact_version,
                    "files": files_added,
                    "total_files": len(files_added),
                }

                metadata_file = package_dir / "manifest.json"
                metadata_file.write_text(json.dumps(metadata, indent=2))

                # Create tar.gz package
                package_file = temp_path / f"{artifact_name}-{artifact_version}.tar.gz"
                with tarfile.open(package_file, "w:gz") as tar:
                    tar.add(package_dir, arcname=artifact_name)

                # Upload to Azure Artifacts Universal Package
                # API: PUT https://pkgs.dev.azure.com/{organization}/_apis/packaging/feeds/{feedId}/upack/packages/{packageName}/versions/{packageVersion}?api-version=7.1-preview.1
                upload_url = f"{org_url}/_apis/packaging/feeds/{feed_name}/upack/packages/{artifact_name}/versions/{artifact_version}?api-version=7.1-preview.1"

                headers = {
                    "Content-Type": "application/octet-stream",
                }

                auth = (
                    "",
                    pat,
                )  # Azure DevOps PAT uses empty username with PAT as password

                with open(package_file, "rb") as f:
                    package_data = f.read()

                response = requests.put(
                    upload_url, headers=headers, auth=auth, data=package_data, timeout=300
                )

                if response.status_code == 201:
                    package_info = response.json()
                    package_id = package_info.get("id")
                    package_url = f"{org_url}/{project}/_packaging?_a=package&feed={feed_name}&package={artifact_name}&version={artifact_version}&protocolType=UPack"

                    # Link artifact to work item using ArtifactLink
                    artifact_link_url = f"{org_url}/_apis/packaging/feeds/{feed_name}/packages/{package_id}"

                    document = [
                        JsonPatchOperation(
                            op="add",
                            path="/relations/-",
                            value={
                                "rel": "ArtifactLink",
                                "url": artifact_link_url,
                                "attributes": {
                                    "name": f"Evidence Package {artifact_version}",
                                    "comment": f"Persistent artifact package with {len(files_added)} evidence files",
                                },
                            },
                        )
                    ]

                    self.work_item_client.update_work_item(
                        document=document, id=int(work_item_id)
                    )

                    result = {
                        "package_id": package_id,
                        "package_url": package_url,
                        "version": artifact_version,
                        "files_count": len(files_added),
                        "artifact_link": artifact_link_url,
                        "files": files_added,
                    }

                    self.logger.info(
                        f"Created persistent artifact package {artifact_name}:{artifact_version} with {len(files_added)} files"
                    )
                    return result

                elif response.status_code == 409:
                    # Package version already exists
                    raise IntegrationError(
                        f"Artifact package {artifact_name}:{artifact_version} already exists. Use a different version."
                    )
                else:
                    raise IntegrationError(
                        f"Failed to upload artifact package: HTTP {response.status_code} - {response.text}"
                    )

        except Exception as e:
            self.logger.error(f"Failed to create artifact package: {e}")
            raise IntegrationError(f"Failed to create artifact package: {e}")

    def link_existing_artifact(
        self,
        work_item_id: str,
        artifact_url: str,
        artifact_name: str,
        comment: Optional[str] = None,
        config: Optional[PluginConfig] = None,
    ) -> bool:
        """
        Link an existing artifact package to a work item.

        Args:
            work_item_id: Work item ID
            artifact_url: URL of the artifact package
            artifact_name: Display name for the artifact
            comment: Optional comment
            config: Plugin configuration

        Returns:
            True if successful

        Raises:
            IntegrationError: If linking fails
        """
        if not self.work_item_client:
            if not config:
                raise IntegrationError("Configuration required for authentication")
            self.authenticate(config)

        try:
            document = [
                JsonPatchOperation(
                    op="add",
                    path="/relations/-",
                    value={
                        "rel": "ArtifactLink",
                        "url": artifact_url,
                        "attributes": {
                            "name": artifact_name,
                            "comment": comment or f"Linked artifact: {artifact_name}",
                        },
                    },
                )
            ]

            self.work_item_client.update_work_item(
                document=document, id=int(work_item_id)
            )

            self.logger.info(
                f"Linked artifact {artifact_name} to work item {work_item_id}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to link artifact: {e}")
            raise IntegrationError(f"Failed to link artifact: {e}")

    def get_work_item_artifacts(
        self, work_item_id: str, config: Optional[PluginConfig] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all artifacts linked to a work item.

        Args:
            work_item_id: Work item ID
            config: Plugin configuration

        Returns:
            List of artifact dictionaries with:
                - url: Artifact URL
                - name: Artifact name
                - comment: Link comment
                - rel: Relation type

        Raises:
            IntegrationError: If retrieval fails
        """
        if not self.work_item_client:
            if not config:
                raise IntegrationError("Configuration required for authentication")
            self.authenticate(config)

        try:
            work_item = self.work_item_client.get_work_item(
                int(work_item_id), expand="Relations"
            )

            artifacts = []
            if work_item.relations:
                for relation in work_item.relations:
                    if relation.rel == "ArtifactLink":
                        artifacts.append(
                            {
                                "url": relation.url,
                                "name": relation.attributes.get("name", "Unnamed"),
                                "comment": relation.attributes.get("comment", ""),
                                "rel": relation.rel,
                            }
                        )

            self.logger.info(
                f"Retrieved {len(artifacts)} artifacts for work item {work_item_id}"
            )
            return artifacts

        except Exception as e:
            self.logger.error(f"Failed to get work item artifacts: {e}")
            raise IntegrationError(f"Failed to get work item artifacts: {e}")
