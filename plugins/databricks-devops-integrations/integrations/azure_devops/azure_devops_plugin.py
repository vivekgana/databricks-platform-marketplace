"""
Azure DevOps Integration Plugin Implementation

Implements the DevOpsIntegrationPlugin interface for Microsoft Azure DevOps.
"""

import logging
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
            comment_text = f"Linked to commit: <a href='{commit_url}'>{commit_sha[:7]}</a>"

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

            self.logger.info(
                f"Linked Azure DevOps work item {item_id} to PR {pr_url}"
            )
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
                float(
                    wi.fields.get("Microsoft.VSTS.Scheduling.StoryPoints", 0) or 0
                )
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
