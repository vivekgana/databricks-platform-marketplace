"""
PBI Generator for Azure DevOps

Generate Product Backlog Items (PBIs) for Enablers and Features from requirements.

PBI Types:
- Enabler: Technical infrastructure work (APIs, frameworks, tooling)
- Feature: User-facing functionality (business capabilities)
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any

from ..parsers.requirement_parser import (
    Requirement,
    AcceptanceCriteria,
    RequirementPriority,
    RequirementStatus,
)
from ...plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import (
    AzureDevOpsPlugin,
)
from ...plugins.databricks_devops_integrations.sdk.base_plugin import (
    PluginConfig,
    WorkItem,
    WorkItemStatus,
    WorkItemPriority,
)


class PBIType(Enum):
    """Product Backlog Item types."""

    ENABLER = "Enabler"  # Technical infrastructure
    FEATURE = "Feature"  # User-facing functionality


@dataclass
class EnablerPBI:
    """
    Enabler PBI - Technical infrastructure work.

    Examples:
    - Build REST API framework
    - Set up CI/CD pipeline
    - Create data pipeline infrastructure
    - Implement logging and monitoring
    """

    title: str
    description: str
    technical_details: str
    acceptance_criteria: List[str]
    dependencies: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    story_points: float = 5.0
    priority: WorkItemPriority = WorkItemPriority.MEDIUM
    tags: List[str] = field(default_factory=list)


@dataclass
class FeaturePBI:
    """
    Feature PBI - User-facing functionality.

    Examples:
    - User authentication
    - Dashboard with metrics
    - Data export capability
    - Report generation
    """

    title: str
    description: str
    user_story: str  # As a [user], I want [goal] so that [benefit]
    acceptance_criteria: List[str]
    business_value: str
    user_personas: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    story_points: float = 5.0
    priority: WorkItemPriority = WorkItemPriority.MEDIUM
    tags: List[str] = field(default_factory=list)


@dataclass
class PBIGenerationResult:
    """Result of PBI generation."""

    pbi_type: PBIType
    work_item_id: str
    work_item_url: str
    title: str
    description: str
    success: bool
    error_message: Optional[str] = None


class PBIGenerator:
    """Generate Azure DevOps PBIs from requirements."""

    def __init__(self, ado_plugin: AzureDevOpsPlugin, config: PluginConfig):
        """
        Initialize PBI generator.

        Args:
            ado_plugin: Configured Azure DevOps plugin
            config: Plugin configuration
        """
        self.ado_plugin = ado_plugin
        self.config = config
        self.logger = logging.getLogger(__name__)

    def generate_from_requirement(
        self,
        requirement: Requirement,
        pbi_type: PBIType = PBIType.FEATURE,
        auto_detect: bool = True,
    ) -> List[PBIGenerationResult]:
        """
        Generate PBIs from requirement.

        Args:
            requirement: Requirement to generate PBIs from
            pbi_type: Type of PBI to generate (if not auto-detecting)
            auto_detect: If True, automatically detect PBI type from requirement

        Returns:
            List of generated PBI results
        """
        results = []

        # Auto-detect PBI type if requested
        if auto_detect:
            detected_types = self._detect_pbi_types(requirement)
        else:
            detected_types = [pbi_type]

        # Generate PBIs for each detected type
        for pbi_type in detected_types:
            if pbi_type == PBIType.ENABLER:
                result = self._generate_enabler_pbi(requirement)
            else:
                result = self._generate_feature_pbi(requirement)

            results.append(result)

        return results

    def generate_enabler_pbi(self, enabler: EnablerPBI) -> PBIGenerationResult:
        """
        Generate Enabler PBI in Azure DevOps.

        Args:
            enabler: Enabler PBI specification

        Returns:
            Generation result with work item ID and URL
        """
        try:
            # Build description
            description = self._build_enabler_description(enabler)

            # Create work item
            work_item = WorkItem(
                id="",
                title=f"[Enabler] {enabler.title}",
                description=description,
                status=WorkItemStatus.TODO,
                assignee=None,
                priority=enabler.priority,
                labels=["enabler", "technical"] + enabler.tags,
                story_points=enabler.story_points,
                custom_fields={
                    "work_item_type": "Product Backlog Item",
                    "/fields/Custom.PBIType": "Enabler",
                    "/fields/Custom.TechnicalDetails": enabler.technical_details,
                },
            )

            # Create in ADO
            work_item_id = self.ado_plugin.create_work_item(work_item, self.config)

            # Build URL
            work_item_url = f"https://dev.azure.com/{self.config.organization}/{self.config.project}/_workitems/edit/{work_item_id}"

            self.logger.info(f"Created Enabler PBI {work_item_id}: {enabler.title}")

            return PBIGenerationResult(
                pbi_type=PBIType.ENABLER,
                work_item_id=work_item_id,
                work_item_url=work_item_url,
                title=enabler.title,
                description=description,
                success=True,
            )

        except Exception as e:
            self.logger.error(f"Failed to create Enabler PBI: {e}")
            return PBIGenerationResult(
                pbi_type=PBIType.ENABLER,
                work_item_id="",
                work_item_url="",
                title=enabler.title,
                description="",
                success=False,
                error_message=str(e),
            )

    def generate_feature_pbi(self, feature: FeaturePBI) -> PBIGenerationResult:
        """
        Generate Feature PBI in Azure DevOps.

        Args:
            feature: Feature PBI specification

        Returns:
            Generation result with work item ID and URL
        """
        try:
            # Build description
            description = self._build_feature_description(feature)

            # Create work item
            work_item = WorkItem(
                id="",
                title=f"[Feature] {feature.title}",
                description=description,
                status=WorkItemStatus.TODO,
                assignee=None,
                priority=feature.priority,
                labels=["feature", "user-facing"] + feature.tags,
                story_points=feature.story_points,
                custom_fields={
                    "work_item_type": "Product Backlog Item",
                    "/fields/Custom.PBIType": "Feature",
                    "/fields/Custom.BusinessValue": feature.business_value,
                    "/fields/Custom.UserPersonas": ", ".join(feature.user_personas),
                },
            )

            # Create in ADO
            work_item_id = self.ado_plugin.create_work_item(work_item, self.config)

            # Build URL
            work_item_url = f"https://dev.azure.com/{self.config.organization}/{self.config.project}/_workitems/edit/{work_item_id}"

            self.logger.info(f"Created Feature PBI {work_item_id}: {feature.title}")

            return PBIGenerationResult(
                pbi_type=PBIType.FEATURE,
                work_item_id=work_item_id,
                work_item_url=work_item_url,
                title=feature.title,
                description=description,
                success=True,
            )

        except Exception as e:
            self.logger.error(f"Failed to create Feature PBI: {e}")
            return PBIGenerationResult(
                pbi_type=PBIType.FEATURE,
                work_item_id="",
                work_item_url="",
                title=feature.title,
                description="",
                success=False,
                error_message=str(e),
            )

    def generate_child_tasks(
        self, parent_pbi_id: str, requirement: Requirement
    ) -> List[str]:
        """
        Generate child tasks for a PBI based on acceptance criteria.

        Args:
            parent_pbi_id: Parent PBI work item ID
            requirement: Requirement containing acceptance criteria

        Returns:
            List of created task IDs
        """
        task_ids = []

        try:
            for ac in requirement.acceptance_criteria:
                # Create task for each acceptance criterion
                task_title = f"Implement {ac.id}: {ac.given[:50]}..."

                task_description = f"""
                <h3>{ac.id}</h3>
                <p><strong>Given:</strong> {ac.given}</p>
                <p><strong>When:</strong> {ac.when}</p>
                <p><strong>Then:</strong> {ac.then}</p>
                """

                if ac.verification:
                    task_description += f"""
                    <h4>Verification:</h4>
                    <p><strong>Method:</strong> {ac.verification.method.value}</p>
                    <p><strong>Details:</strong> {ac.verification.details}</p>
                    """

                # Estimate story points for task (AC-based estimation)
                task_points = self._estimate_ac_points(ac)

                work_item = WorkItem(
                    id="",
                    title=task_title,
                    description=task_description,
                    status=WorkItemStatus.TODO,
                    assignee=None,
                    priority=WorkItemPriority.MEDIUM,
                    labels=["acceptance-criteria", ac.id],
                    story_points=task_points,
                    custom_fields={
                        "work_item_type": "Task",
                        "/fields/Custom.AcceptanceCriterionID": ac.id,
                    },
                )

                # Create task
                task_id = self.ado_plugin.create_work_item(work_item, self.config)

                # Link to parent PBI
                self._link_parent_child(parent_pbi_id, task_id)

                task_ids.append(task_id)
                self.logger.info(
                    f"Created task {task_id} for {ac.id} under PBI {parent_pbi_id}"
                )

        except Exception as e:
            self.logger.error(f"Failed to generate child tasks: {e}")

        return task_ids

    # Helper methods
    def _detect_pbi_types(self, requirement: Requirement) -> List[PBIType]:
        """
        Auto-detect PBI types from requirement.

        Heuristics:
        - Enabler if: title contains "API", "framework", "infrastructure", "pipeline", "CI/CD"
        - Feature if: has user personas or user story format
        - Default: Feature
        """
        title_lower = requirement.title.lower()
        description_lower = requirement.problem_statement.lower()

        enabler_keywords = [
            "api",
            "framework",
            "infrastructure",
            "pipeline",
            "ci/cd",
            "cicd",
            "setup",
            "tooling",
            "library",
            "sdk",
            "integration",
            "platform",
        ]

        # Check if it's an enabler
        is_enabler = any(keyword in title_lower for keyword in enabler_keywords) or any(
            keyword in description_lower for keyword in enabler_keywords
        )

        # Check if it's a feature
        has_personas = len(requirement.personas) > 0
        has_user_story = "as a" in description_lower and "i want" in description_lower

        if is_enabler:
            return [PBIType.ENABLER]
        elif has_personas or has_user_story:
            return [PBIType.FEATURE]
        else:
            # Default to feature
            return [PBIType.FEATURE]

    def _generate_enabler_pbi(self, requirement: Requirement) -> PBIGenerationResult:
        """Generate Enabler PBI from requirement."""
        # Extract technical details
        technical_details = requirement.problem_statement

        # Build acceptance criteria from requirement
        ac_list = [str(ac) for ac in requirement.acceptance_criteria]

        # Extract dependencies
        dependencies = []
        for fr in requirement.functional_requirements:
            if "depends on" in fr.lower() or "requires" in fr.lower():
                dependencies.append(fr)

        # Create EnablerPBI
        enabler = EnablerPBI(
            title=requirement.title,
            description=requirement.problem_statement,
            technical_details=technical_details,
            acceptance_criteria=ac_list,
            dependencies=dependencies,
            affected_components=list(requirement.databricks_objects.keys()),
            story_points=self._estimate_requirement_points(requirement),
            priority=self._map_requirement_priority(requirement.priority),
            tags=[requirement.product, requirement.team, requirement.req_id],
        )

        return self.generate_enabler_pbi(enabler)

    def _generate_feature_pbi(self, requirement: Requirement) -> PBIGenerationResult:
        """Generate Feature PBI from requirement."""
        # Build user story
        user_story = self._extract_user_story(requirement)

        # Build acceptance criteria
        ac_list = [str(ac) for ac in requirement.acceptance_criteria]

        # Extract business value
        business_value = requirement.problem_statement[:200]

        # Extract dependencies
        dependencies = []
        for fr in requirement.functional_requirements:
            if "depends on" in fr.lower() or "requires" in fr.lower():
                dependencies.append(fr)

        # Create FeaturePBI
        feature = FeaturePBI(
            title=requirement.title,
            description=requirement.problem_statement,
            user_story=user_story,
            acceptance_criteria=ac_list,
            business_value=business_value,
            user_personas=requirement.personas,
            dependencies=dependencies,
            story_points=self._estimate_requirement_points(requirement),
            priority=self._map_requirement_priority(requirement.priority),
            tags=[requirement.product, requirement.team, requirement.req_id],
        )

        return self.generate_feature_pbi(feature)

    def _build_enabler_description(self, enabler: EnablerPBI) -> str:
        """Build HTML description for Enabler PBI."""
        desc = f"<h2>[Enabler] {enabler.title}</h2>\n\n"

        # Description
        desc += f"<h3>Description</h3>\n<p>{enabler.description}</p>\n\n"

        # Technical Details
        desc += f"<h3>Technical Details</h3>\n<p>{enabler.technical_details}</p>\n\n"

        # Acceptance Criteria
        if enabler.acceptance_criteria:
            desc += "<h3>Acceptance Criteria</h3>\n<ul>\n"
            for i, ac in enumerate(enabler.acceptance_criteria, 1):
                desc += f"<li><strong>AC-{i}:</strong> {ac}</li>\n"
            desc += "</ul>\n\n"

        # Dependencies
        if enabler.dependencies:
            desc += "<h3>Dependencies</h3>\n<ul>\n"
            for dep in enabler.dependencies:
                desc += f"<li>{dep}</li>\n"
            desc += "</ul>\n\n"

        # Affected Components
        if enabler.affected_components:
            desc += "<h3>Affected Components</h3>\n<ul>\n"
            for component in enabler.affected_components:
                desc += f"<li>{component}</li>\n"
            desc += "</ul>\n\n"

        # Story Points
        desc += f"<p><em>Estimated Story Points:</em> <strong>{enabler.story_points}</strong></p>\n"

        return desc

    def _build_feature_description(self, feature: FeaturePBI) -> str:
        """Build HTML description for Feature PBI."""
        desc = f"<h2>[Feature] {feature.title}</h2>\n\n"

        # User Story
        desc += f"<h3>User Story</h3>\n<p><em>{feature.user_story}</em></p>\n\n"

        # Description
        desc += f"<h3>Description</h3>\n<p>{feature.description}</p>\n\n"

        # Business Value
        desc += f"<h3>Business Value</h3>\n<p>{feature.business_value}</p>\n\n"

        # User Personas
        if feature.user_personas:
            desc += "<h3>User Personas</h3>\n<ul>\n"
            for persona in feature.user_personas:
                desc += f"<li>{persona}</li>\n"
            desc += "</ul>\n\n"

        # Acceptance Criteria
        if feature.acceptance_criteria:
            desc += "<h3>Acceptance Criteria</h3>\n<ul>\n"
            for i, ac in enumerate(feature.acceptance_criteria, 1):
                desc += f"<li><strong>AC-{i}:</strong> {ac}</li>\n"
            desc += "</ul>\n\n"

        # Dependencies
        if feature.dependencies:
            desc += "<h3>Dependencies</h3>\n<ul>\n"
            for dep in feature.dependencies:
                desc += f"<li>{dep}</li>\n"
            desc += "</ul>\n\n"

        # Story Points
        desc += f"<p><em>Estimated Story Points:</em> <strong>{feature.story_points}</strong></p>\n"

        return desc

    def _extract_user_story(self, requirement: Requirement) -> str:
        """
        Extract or generate user story from requirement.

        Format: As a [user], I want [goal] so that [benefit]
        """
        description = requirement.problem_statement.lower()

        # Check if already in user story format
        if "as a" in description and "i want" in description:
            # Extract existing user story
            start = description.find("as a")
            end = description.find(".", start) if "." in description[start:] else len(description)
            return requirement.problem_statement[start:end].strip()

        # Generate user story
        persona = requirement.personas[0] if requirement.personas else "user"
        goal = requirement.title
        benefit = requirement.problem_statement[:100]

        return f"As a {persona}, I want {goal} so that {benefit}"

    def _estimate_requirement_points(self, requirement: Requirement) -> float:
        """
        Estimate story points from requirement complexity.

        Factors:
        - Base: 3 points
        - +1 per acceptance criterion
        - +2 if > 5 functional requirements
        - +1 if demo required
        - +1 per databricks object
        """
        points = 3.0

        # Acceptance criteria
        points += len(requirement.acceptance_criteria)

        # Functional requirements
        if len(requirement.functional_requirements) > 5:
            points += 2.0

        # Demo evidence
        if requirement.demo:
            points += 1.0

        # Databricks objects (complexity)
        points += min(len(requirement.databricks_objects), 3)

        # Cap at 13 (Fibonacci)
        return min(points, 13.0)

    def _estimate_ac_points(self, ac: AcceptanceCriteria) -> float:
        """Estimate story points for a single acceptance criterion (task)."""
        # Base task: 1 point
        points = 1.0

        # Add for verification complexity
        if ac.verification:
            if ac.verification.method.value == "test":
                points += 0.5  # Automated test
            elif ac.verification.method.value == "job":
                points += 1.0  # Databricks job
            elif ac.verification.method.value == "query":
                points += 0.5  # SQL query
            elif ac.verification.method.value == "manual":
                points += 1.0  # Manual verification

        # Add for demo evidence
        if ac.demo_evidence:
            points += 0.5

        # Cap at 3 for a task
        return min(points, 3.0)

    def _map_requirement_priority(
        self, priority: RequirementPriority
    ) -> WorkItemPriority:
        """Map requirement priority to work item priority."""
        mapping = {
            RequirementPriority.P1: WorkItemPriority.CRITICAL,
            RequirementPriority.P2: WorkItemPriority.HIGH,
            RequirementPriority.P3: WorkItemPriority.MEDIUM,
        }
        return mapping.get(priority, WorkItemPriority.MEDIUM)

    def _link_parent_child(self, parent_id: str, child_id: str) -> bool:
        """
        Link child work item to parent.

        Args:
            parent_id: Parent work item ID
            child_id: Child work item ID

        Returns:
            True if link succeeded
        """
        try:
            # Create parent-child link
            updates = {
                "relations": [
                    {
                        "rel": "System.LinkTypes.Hierarchy-Reverse",
                        "url": f"https://dev.azure.com/{self.config.organization}/{self.config.project}/_apis/wit/workItems/{parent_id}",
                        "attributes": {"comment": "Child task"},
                    }
                ]
            }

            self.ado_plugin.update_work_item(child_id, updates, self.config)
            self.logger.info(f"Linked task {child_id} to PBI {parent_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to link parent-child: {e}")
            return False
