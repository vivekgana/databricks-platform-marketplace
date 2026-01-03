"""
JIRA Integration Plugin Implementation

Implements the DevOpsIntegrationPlugin interface for Atlassian JIRA.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from jira import JIRA
from jira.exceptions import JIRAError

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


class JiraPlugin(DevOpsIntegrationPlugin):
    """JIRA integration plugin"""

    def __init__(self):
        self.client: Optional[JIRA] = None
        self.logger = logging.getLogger(__name__)

    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        return PluginMetadata(
            name="JIRA Integration",
            version="1.0.0",
            description="Atlassian JIRA integration for work item management",
            author="Databricks Platform Team",
            supported_features=[
                "work_items",
                "incidents",
                "commits",
                "pull_requests",
                "team_velocity",
                "webhooks",
            ],
            requires_auth=True,
            documentation_url="https://docs.yourcompany.com/plugins/jira",
        )

    def authenticate(self, config: PluginConfig) -> bool:
        """Authenticate with JIRA"""
        try:
            self.client = JIRA(
                server=config.api_endpoint,
                basic_auth=(config.organization, config.api_key),
                options={"verify": config.verify_ssl},
            )
            # Test authentication
            self.client.myself()
            self.logger.info("Successfully authenticated with JIRA")
            return True
        except JIRAError as e:
            self.logger.error(f"JIRA authentication failed: {e}")
            raise AuthenticationError(f"Failed to authenticate with JIRA: {e}")

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
        """Create JIRA issue"""
        if not self.client:
            self.authenticate(config)

        try:
            issue_dict = {
                "project": {"key": config.project},
                "summary": work_item.title,
                "description": work_item.description,
                "issuetype": {"name": "Task"},
                "priority": {"name": self._map_priority_to_jira(work_item.priority)},
            }

            # Add labels
            if work_item.labels:
                issue_dict["labels"] = work_item.labels

            # Add assignee
            if work_item.assignee:
                issue_dict["assignee"] = {"name": work_item.assignee}

            # Add custom fields
            for field_id, value in work_item.custom_fields.items():
                issue_dict[field_id] = value

            # Add story points if provided
            if work_item.story_points:
                # Default story points field in JIRA
                issue_dict["customfield_10016"] = work_item.story_points

            issue = self.client.create_issue(fields=issue_dict)
            self.logger.info(f"Created JIRA issue: {issue.key}")
            return issue.key

        except JIRAError as e:
            self.logger.error(f"Failed to create JIRA issue: {e}")
            raise IntegrationError(f"Failed to create work item in JIRA: {e}")

    def update_work_item(
        self, item_id: str, updates: Dict[str, Any], config: PluginConfig
    ) -> bool:
        """Update existing JIRA issue"""
        if not self.client:
            self.authenticate(config)

        try:
            issue = self.client.issue(item_id)

            # Map updates to JIRA fields
            jira_updates = {}
            if "title" in updates:
                jira_updates["summary"] = updates["title"]
            if "description" in updates:
                jira_updates["description"] = updates["description"]
            if "status" in updates:
                # Status changes require transitions, not field updates
                self._transition_issue(issue, updates["status"])
            if "priority" in updates:
                jira_updates["priority"] = {
                    "name": self._map_priority_to_jira(updates["priority"])
                }
            if "assignee" in updates:
                jira_updates["assignee"] = {"name": updates["assignee"]}
            if "labels" in updates:
                jira_updates["labels"] = updates["labels"]

            # Update the issue
            if jira_updates:
                issue.update(fields=jira_updates)

            self.logger.info(f"Updated JIRA issue: {item_id}")
            return True

        except JIRAError as e:
            if e.status_code == 404:
                raise WorkItemNotFoundError(f"Work item {item_id} not found")
            self.logger.error(f"Failed to update JIRA issue: {e}")
            raise IntegrationError(f"Failed to update work item: {e}")

    def get_work_item(self, item_id: str, config: PluginConfig) -> WorkItem:
        """Retrieve JIRA issue details"""
        if not self.client:
            self.authenticate(config)

        try:
            issue = self.client.issue(item_id)
            return self._jira_issue_to_work_item(issue)

        except JIRAError as e:
            if e.status_code == 404:
                raise WorkItemNotFoundError(f"Work item {item_id} not found")
            raise IntegrationError(f"Failed to retrieve work item: {e}")

    def search_work_items(
        self, query: str, config: PluginConfig, limit: int = 100
    ) -> List[WorkItem]:
        """Search for JIRA issues"""
        if not self.client:
            self.authenticate(config)

        try:
            # Build JQL query
            jql = f"project = {config.project} AND text ~ '{query}'"
            issues = self.client.search_issues(jql, maxResults=limit)

            return [self._jira_issue_to_work_item(issue) for issue in issues]

        except JIRAError as e:
            self.logger.error(f"Failed to search JIRA issues: {e}")
            raise IntegrationError(f"Failed to search work items: {e}")

    def link_to_commit(
        self,
        item_id: str,
        commit_sha: str,
        repo_url: str,
        config: PluginConfig,
    ) -> bool:
        """Link JIRA issue to git commit"""
        if not self.client:
            self.authenticate(config)

        try:
            issue = self.client.issue(item_id)

            # Add comment with commit link
            commit_url = f"{repo_url}/commit/{commit_sha}"
            comment = f"Linked to commit: [{commit_sha[:7]}]({commit_url})"
            self.client.add_comment(issue, comment)

            self.logger.info(f"Linked JIRA issue {item_id} to commit {commit_sha}")
            return True

        except JIRAError as e:
            self.logger.error(f"Failed to link commit: {e}")
            raise IntegrationError(f"Failed to link commit: {e}")

    def link_to_pull_request(
        self, item_id: str, pr_url: str, config: PluginConfig
    ) -> bool:
        """Link JIRA issue to pull request"""
        if not self.client:
            self.authenticate(config)

        try:
            issue = self.client.issue(item_id)

            # Create remote link to PR
            self.client.add_simple_link(issue, {"url": pr_url, "title": "Pull Request"})

            self.logger.info(f"Linked JIRA issue {item_id} to PR {pr_url}")
            return True

        except JIRAError as e:
            self.logger.error(f"Failed to link pull request: {e}")
            raise IntegrationError(f"Failed to link pull request: {e}")

    def create_from_incident(
        self, incident: Dict[str, Any], config: PluginConfig
    ) -> str:
        """Auto-create JIRA issue from production incident"""

        # AI-powered root cause analysis (placeholder for now)
        root_cause = self._analyze_incident(incident)
        fix_suggestions = self._suggest_fixes(root_cause)

        description = f"""
🚨 *Automated Incident Report*

*Incident:* {incident.get('title', 'Unknown')}
*Severity:* {incident.get('severity', 'Unknown')}
*Time:* {incident.get('timestamp', 'Unknown')}

*Root Cause Analysis:*
{root_cause.get('summary', 'Analysis in progress')}

*Affected Components:*
{', '.join(root_cause.get('components', ['Unknown']))}

*Suggested Fixes:*
{self._format_fixes(fix_suggestions)}

*Logs:*
{{code}}
{incident.get('logs', 'No logs available')[-500:]}
{{code}}

_This issue was automatically created by DevPlatform AI_
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
            custom_fields={
                "customfield_10016": 5  # Default story points for incidents
            },
        )

        return self.create_work_item(work_item, config)

    def get_team_velocity(
        self, team_id: str, timeframe_days: int, config: PluginConfig
    ) -> Dict[str, float]:
        """Calculate team velocity from JIRA"""
        if not self.client:
            self.authenticate(config)

        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=timeframe_days)

            jql = f"""
            project = {config.project}
            AND status = Done
            AND resolved >= '{start_date.strftime('%Y-%m-%d')}'
            AND team = {team_id}
            """

            issues = self.client.search_issues(jql, maxResults=1000)

            # Calculate velocity metrics
            total_story_points = sum(
                float(getattr(issue.fields, "customfield_10016", 0) or 0)
                for issue in issues
            )

            # Get unique sprints
            sprints = set()
            for issue in issues:
                sprint_field = getattr(issue.fields, "customfield_10020", None)
                if sprint_field:
                    for sprint in sprint_field:
                        sprints.add(sprint.name if hasattr(sprint, "name") else str(sprint))

            sprints_completed = len(sprints)

            return {
                "total_story_points": total_story_points,
                "avg_velocity": (
                    total_story_points / max(sprints_completed, 1)
                    if sprints_completed > 0
                    else 0
                ),
                "issues_completed": len(issues),
                "sprints": sprints_completed,
                "timeframe_days": timeframe_days,
            }

        except JIRAError as e:
            self.logger.error(f"Failed to calculate velocity: {e}")
            raise IntegrationError(f"Failed to calculate team velocity: {e}")

    def webhook_handler(
        self, event_type: str, payload: Dict[str, Any], config: PluginConfig
    ) -> Dict[str, Any]:
        """Handle incoming webhooks from JIRA"""
        self.logger.info(f"Received webhook event: {event_type}")

        handlers = {
            "jira:issue_created": self._handle_issue_created,
            "jira:issue_updated": self._handle_issue_updated,
            "jira:issue_deleted": self._handle_issue_deleted,
        }

        handler = handlers.get(event_type)
        if handler:
            return handler(payload, config)

        return {"status": "ignored", "event_type": event_type}

    # Helper methods
    def _map_priority_to_jira(self, priority: WorkItemPriority) -> str:
        """Map standard priority to JIRA priority"""
        mapping = {
            WorkItemPriority.CRITICAL: "Highest",
            WorkItemPriority.HIGH: "High",
            WorkItemPriority.MEDIUM: "Medium",
            WorkItemPriority.LOW: "Low",
        }
        return mapping.get(priority, "Medium")

    def _map_jira_priority_to_standard(self, jira_priority: str) -> WorkItemPriority:
        """Map JIRA priority to standard priority"""
        mapping = {
            "Highest": WorkItemPriority.CRITICAL,
            "High": WorkItemPriority.HIGH,
            "Medium": WorkItemPriority.MEDIUM,
            "Low": WorkItemPriority.LOW,
        }
        return mapping.get(jira_priority, WorkItemPriority.MEDIUM)

    def _map_jira_status_to_standard(self, jira_status: str) -> WorkItemStatus:
        """Map JIRA status to standard status"""
        status_lower = jira_status.lower()
        if status_lower in ["to do", "open", "backlog"]:
            return WorkItemStatus.TODO
        elif status_lower in ["in progress", "in development"]:
            return WorkItemStatus.IN_PROGRESS
        elif status_lower in ["in review", "code review"]:
            return WorkItemStatus.IN_REVIEW
        elif status_lower in ["blocked", "on hold"]:
            return WorkItemStatus.BLOCKED
        elif status_lower in ["done", "closed", "resolved"]:
            return WorkItemStatus.DONE
        elif status_lower == "cancelled":
            return WorkItemStatus.CANCELLED
        return WorkItemStatus.TODO

    def _jira_issue_to_work_item(self, issue) -> WorkItem:
        """Convert JIRA issue to WorkItem"""
        return WorkItem(
            id=issue.key,
            title=issue.fields.summary,
            description=issue.fields.description or "",
            status=self._map_jira_status_to_standard(issue.fields.status.name),
            assignee=(
                issue.fields.assignee.name if issue.fields.assignee else None
            ),
            priority=self._map_jira_priority_to_standard(issue.fields.priority.name),
            labels=issue.fields.labels or [],
            created_at=datetime.fromisoformat(issue.fields.created.replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(issue.fields.updated.replace("Z", "+00:00")),
            url=f"{self.client.server_url}/browse/{issue.key}",
            story_points=float(getattr(issue.fields, "customfield_10016", 0) or 0),
        )

    def _transition_issue(self, issue, target_status: WorkItemStatus):
        """Transition JIRA issue to target status"""
        # Get available transitions
        transitions = self.client.transitions(issue)

        # Find matching transition
        status_mapping = {
            WorkItemStatus.TODO: ["To Do", "Open"],
            WorkItemStatus.IN_PROGRESS: ["In Progress", "Start Progress"],
            WorkItemStatus.IN_REVIEW: ["In Review", "Code Review"],
            WorkItemStatus.BLOCKED: ["Blocked", "On Hold"],
            WorkItemStatus.DONE: ["Done", "Close", "Resolve"],
            WorkItemStatus.CANCELLED: ["Cancelled", "Cancel"],
        }

        target_names = status_mapping.get(target_status, [])
        for transition in transitions:
            if transition["name"] in target_names:
                self.client.transition_issue(issue, transition["id"])
                return

    def _analyze_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze incident to determine root cause (placeholder)"""
        # This would use AI/ML for real root cause analysis
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

    def _format_fixes(self, fixes: List[str]) -> str:
        """Format fix suggestions as markdown list"""
        return "\n".join(f"- {fix}" for fix in fixes)

    def _get_component_owner(self, component: str) -> Optional[str]:
        """Get owner of a component (placeholder)"""
        # This would lookup from configuration
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

    def _handle_issue_created(
        self, payload: Dict[str, Any], config: PluginConfig
    ) -> Dict[str, Any]:
        """Handle issue created webhook"""
        issue_key = payload.get("issue", {}).get("key")
        self.logger.info(f"Issue created: {issue_key}")
        return {"status": "processed", "issue_key": issue_key}

    def _handle_issue_updated(
        self, payload: Dict[str, Any], config: PluginConfig
    ) -> Dict[str, Any]:
        """Handle issue updated webhook"""
        issue_key = payload.get("issue", {}).get("key")
        self.logger.info(f"Issue updated: {issue_key}")
        return {"status": "processed", "issue_key": issue_key}

    def _handle_issue_deleted(
        self, payload: Dict[str, Any], config: PluginConfig
    ) -> Dict[str, Any]:
        """Handle issue deleted webhook"""
        issue_key = payload.get("issue", {}).get("key")
        self.logger.info(f"Issue deleted: {issue_key}")
        return {"status": "processed", "issue_key": issue_key}
