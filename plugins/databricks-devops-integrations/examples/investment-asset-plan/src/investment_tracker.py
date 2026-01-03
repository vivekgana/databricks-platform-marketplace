"""
Investment Asset Plan Tracker

Demonstrates DevOps integration plugins for investment management workflows.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from ...sdk import (
    PluginRegistry,
    PluginConfig,
    WorkItem,
    WorkItemStatus,
    WorkItemPriority,
)
from ...integrations.jira import JiraPlugin
from ...integrations.azure_devops import AzureDevOpsPlugin


class InvestmentTracker:
    """
    Investment asset tracker using DevOps integrations

    Manages investment opportunities, due diligence, portfolio monitoring,
    and compliance tracking using JIRA or Azure DevOps.
    """

    def __init__(self, platform: str = "jira", config: Optional[PluginConfig] = None):
        """
        Initialize investment tracker

        Args:
            platform: "jira" or "azure_devops"
            config: Optional plugin configuration (otherwise loads from env)
        """
        self.platform = platform
        self.logger = logging.getLogger(__name__)
        self.registry = PluginRegistry()

        # Initialize plugin
        if config is None:
            config = self._load_config_from_env(platform)

        if platform == "jira":
            plugin = JiraPlugin()
        elif platform == "azure_devops":
            plugin = AzureDevOpsPlugin()
        else:
            raise ValueError(f"Unsupported platform: {platform}")

        # Register plugin
        self.registry.register(f"{platform}-tracker", plugin, config)
        self.plugin = plugin
        self.config = config

        # Authenticate
        self.plugin.authenticate(config)
        self.logger.info(f"Initialized investment tracker with {platform}")

    def create_from_opportunity(self, opportunity: Dict[str, Any]) -> str:
        """
        Create work items from investment opportunity

        Args:
            opportunity: Investment opportunity details

        Returns:
            Main work item ID
        """
        # Create main epic/feature for opportunity
        main_item = WorkItem(
            id="",
            title=f"Investment: {opportunity['title']}",
            description=self._format_opportunity_description(opportunity),
            status=WorkItemStatus.TODO,
            priority=self._map_risk_to_priority(opportunity.get("risk_level", "medium")),
            labels=["investment", "opportunity", opportunity.get("sector", "general")],
            story_points=self._estimate_story_points(opportunity),
            custom_fields=self._map_opportunity_to_custom_fields(opportunity),
        )

        # Create the main work item
        main_id = self.plugin.create_work_item(main_item, self.config)
        self.logger.info(f"Created investment opportunity: {main_id}")

        # Create due diligence sub-tasks
        self._create_due_diligence_tasks(main_id, opportunity)

        return main_id

    def create_incident(self, alert: Dict[str, Any]) -> str:
        """
        Create incident from portfolio alert

        Args:
            alert: Portfolio alert details

        Returns:
            Incident work item ID
        """
        incident = {
            "title": f"Portfolio Alert: {alert.get('portfolio_company', 'Unknown')} - {alert.get('alert_type', 'Alert')}",
            "severity": alert.get("severity", "medium"),
            "timestamp": datetime.utcnow().isoformat(),
            "logs": alert.get("details", "No details available"),
            "components": [alert.get("portfolio_company", "Unknown")],
        }

        incident_id = self.plugin.create_from_incident(incident, self.config)
        self.logger.info(f"Created incident from alert: {incident_id}")
        return incident_id

    def update_task(
        self, task_id: str, status: str = None, findings: str = None
    ) -> bool:
        """
        Update due diligence task

        Args:
            task_id: Task work item ID
            status: New status
            findings: Findings to add to description

        Returns:
            True if successful
        """
        updates = {}

        if status:
            status_map = {
                "pending": WorkItemStatus.TODO,
                "in_progress": WorkItemStatus.IN_PROGRESS,
                "completed": WorkItemStatus.DONE,
                "blocked": WorkItemStatus.BLOCKED,
            }
            updates["status"] = status_map.get(status, WorkItemStatus.TODO)

        if findings:
            # Get current work item
            current = self.plugin.get_work_item(task_id, self.config)
            updates["description"] = f"{current.description}\n\n**Findings:**\n{findings}"

        return self.plugin.update_work_item(task_id, updates, self.config)

    def get_due_diligence_tasks(
        self, opportunity_name: str
    ) -> List[WorkItem]:
        """
        Get all due diligence tasks for an opportunity

        Args:
            opportunity_name: Name of the investment opportunity

        Returns:
            List of work items
        """
        query = f"due diligence {opportunity_name}"
        return self.plugin.search_work_items(query, self.config)

    def get_team_velocity(
        self, team_id: str = "Investment Team", days: int = 30
    ) -> Dict[str, float]:
        """
        Get investment team velocity metrics

        Args:
            team_id: Team identifier
            days: Number of days to analyze

        Returns:
            Velocity metrics
        """
        return self.plugin.get_team_velocity(team_id, days, self.config)

    def link_to_document(
        self, work_item_id: str, document_url: str
    ) -> bool:
        """
        Link work item to due diligence document

        Args:
            work_item_id: Work item ID
            document_url: URL to document (SharePoint, Google Drive, etc)

        Returns:
            True if successful
        """
        # Use PR link functionality for document links
        return self.plugin.link_to_pull_request(work_item_id, document_url, self.config)

    def health_check(self) -> Dict[str, Any]:
        """Check plugin health"""
        return self.plugin.health_check(self.config)

    # Private helper methods
    def _load_config_from_env(self, platform: str) -> PluginConfig:
        """Load configuration from environment variables"""
        import os

        if platform == "jira":
            return PluginConfig(
                plugin_id="jira-investment-tracker",
                api_endpoint=os.getenv("JIRA_URL", ""),
                api_key=os.getenv("JIRA_API_TOKEN", ""),
                organization=os.getenv("JIRA_EMAIL", ""),
                project=os.getenv("JIRA_PROJECT", "INVEST"),
            )
        elif platform == "azure_devops":
            return PluginConfig(
                plugin_id="ado-investment-tracker",
                api_endpoint=os.getenv("AZURE_DEVOPS_ORG_URL", ""),
                api_key=os.getenv("AZURE_DEVOPS_PAT", ""),
                organization=os.getenv("AZURE_DEVOPS_ORG", ""),
                project=os.getenv("AZURE_DEVOPS_PROJECT", ""),
            )

    def _format_opportunity_description(self, opportunity: Dict[str, Any]) -> str:
        """Format opportunity as work item description"""
        return f"""
# Investment Opportunity

**Company:** {opportunity.get('title', 'Unknown')}
**Stage:** {opportunity.get('stage', 'Unknown')}
**Amount:** ${opportunity.get('amount', 0):,}
**Sector:** {opportunity.get('sector', 'Unknown')}
**Risk Level:** {opportunity.get('risk_level', 'Unknown')}

## Description
{opportunity.get('description', 'No description provided')}

## Next Steps
- Complete due diligence checklist
- Review financial statements
- Conduct management interviews
- Present to investment committee
        """

    def _map_risk_to_priority(self, risk_level: str) -> WorkItemPriority:
        """Map risk level to work item priority"""
        mapping = {
            "critical": WorkItemPriority.CRITICAL,
            "high": WorkItemPriority.HIGH,
            "medium": WorkItemPriority.MEDIUM,
            "low": WorkItemPriority.LOW,
        }
        return mapping.get(risk_level.lower(), WorkItemPriority.MEDIUM)

    def _estimate_story_points(self, opportunity: Dict[str, Any]) -> float:
        """Estimate story points based on opportunity complexity"""
        # Simple heuristic based on amount and stage
        amount = opportunity.get("amount", 0)
        stage = opportunity.get("stage", "")

        base_points = 5.0

        # Adjust for amount
        if amount > 50000000:  # >$50M
            base_points += 8.0
        elif amount > 10000000:  # >$10M
            base_points += 5.0
        elif amount > 1000000:  # >$1M
            base_points += 3.0

        # Adjust for stage
        if stage == "due_diligence":
            base_points += 5.0
        elif stage == "term_sheet":
            base_points += 3.0

        return base_points

    def _map_opportunity_to_custom_fields(
        self, opportunity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Map opportunity fields to platform custom fields"""
        if self.platform == "jira":
            return {
                "customfield_10030": opportunity.get("amount", 0),  # Investment amount
                "customfield_10031": opportunity.get("sector", ""),  # Sector
                "customfield_10032": opportunity.get("risk_level", ""),  # Risk level
            }
        elif self.platform == "azure_devops":
            return {
                "/fields/Custom.InvestmentAmount": opportunity.get("amount", 0),
                "/fields/Custom.Sector": opportunity.get("sector", ""),
                "/fields/Custom.RiskLevel": opportunity.get("risk_level", ""),
            }
        return {}

    def _create_due_diligence_tasks(
        self, parent_id: str, opportunity: Dict[str, Any]
    ) -> List[str]:
        """Create standard due diligence sub-tasks"""
        standard_tasks = [
            {
                "title": "Financial Due Diligence",
                "description": "Review financial statements, projections, and cap table",
                "priority": WorkItemPriority.HIGH,
            },
            {
                "title": "Technical Due Diligence",
                "description": "Review technology stack, architecture, and scalability",
                "priority": WorkItemPriority.HIGH,
            },
            {
                "title": "Legal Due Diligence",
                "description": "Review contracts, IP, and compliance",
                "priority": WorkItemPriority.MEDIUM,
            },
            {
                "title": "Market Due Diligence",
                "description": "Analyze market size, competition, and positioning",
                "priority": WorkItemPriority.MEDIUM,
            },
            {
                "title": "Management Interviews",
                "description": "Conduct interviews with key management team",
                "priority": WorkItemPriority.HIGH,
            },
            {
                "title": "Reference Checks",
                "description": "Contact customer and employee references",
                "priority": WorkItemPriority.MEDIUM,
            },
        ]

        task_ids = []
        for task in standard_tasks:
            work_item = WorkItem(
                id="",
                title=f"[{opportunity['title']}] {task['title']}",
                description=task["description"],
                status=WorkItemStatus.TODO,
                priority=task["priority"],
                labels=["due_diligence", opportunity.get("sector", "general")],
                parent_id=parent_id,
                story_points=3.0,
            )

            task_id = self.plugin.create_work_item(work_item, self.config)
            task_ids.append(task_id)
            self.logger.info(f"Created due diligence task: {task_id}")

        return task_ids
