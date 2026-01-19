"""
Epic/Feature/Enabler Generator from ADO and Wiki

Parse ADO work items (Epic, Feature, Enabler) and auto-generate child PBIs.
Supports importing from wiki design documents.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

from ..parsers.requirement_parser import RequirementParser
from ...plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import (
    AzureDevOpsPlugin,
)
from ...plugins.databricks_devops_integrations.sdk.base_plugin import (
    PluginConfig,
    WorkItem,
    WorkItemStatus,
    WorkItemPriority,
)
from .pbi_generator import PBIGenerator, PBIType, EnablerPBI, FeaturePBI


class WorkItemType(Enum):
    """ADO work item types."""

    EPIC = "Epic"
    FEATURE = "Feature"
    ENABLER = "Enabler"
    PBI = "Product Backlog Item"
    TASK = "Task"


@dataclass
class ADOWorkItemReference:
    """Parsed Azure DevOps work item reference."""

    organization: str
    project: str
    work_item_id: str
    work_item_type: WorkItemType
    url: str
    title: str = ""
    description: str = ""

    @classmethod
    def parse_url(cls, ado_url: str) -> Optional["ADOWorkItemReference"]:
        """
        Parse Azure DevOps work item URL.

        Supports:
        - https://dev.azure.com/{org}/{project}/_workitems/edit/{id}
        - https://dev.azure.com/{org}/{project}/_backlogs/backlog/{team}/Epics/?workitem={id}
        """
        # Standard work item URL
        pattern = r"https://dev\.azure\.com/([^/]+)/([^/]+)/_workitems/edit/(\d+)"
        match = re.match(pattern, ado_url)

        if match:
            org, project, work_item_id = match.groups()
            project = project.replace("%20", " ")
            return cls(
                organization=org,
                project=project,
                work_item_id=work_item_id,
                work_item_type=WorkItemType.PBI,  # Will be updated after fetch
                url=ado_url,
            )

        # Backlog URL with workitem parameter
        pattern = r"https://dev\.azure\.com/([^/]+)/([^/]+)/_backlogs.*workitem=(\d+)"
        match = re.search(pattern, ado_url)

        if match:
            org, project, work_item_id = match.groups()
            project = project.replace("%20", " ")
            return cls(
                organization=org,
                project=project,
                work_item_id=work_item_id,
                work_item_type=WorkItemType.EPIC,  # Will be updated after fetch
                url=ado_url,
            )

        return None


@dataclass
class WikiReference:
    """Parsed wiki page reference."""

    organization: str
    project: str
    wiki_name: str
    page_id: str
    url: str
    page_title: str = ""

    @classmethod
    def parse_url(cls, wiki_url: str) -> Optional["WikiReference"]:
        """
        Parse Azure DevOps wiki URL.

        Example: https://dev.azure.com/symphonyvsts/Audit%20Cortex%202/_wiki/wikis/Audit-Cortex-2.wiki/220464/DM-ADP-automated-Unit-and-Integration-test-design
        """
        pattern = r"https://dev\.azure\.com/([^/]+)/([^/]+)/_wiki/wikis/([^/]+)/(\d+)/(.+)"
        match = re.match(pattern, wiki_url)

        if not match:
            return None

        org, project, wiki_name, page_id, page_title = match.groups()

        # Decode URL-encoded values
        project = project.replace("%20", " ")
        page_title = page_title.replace("-", " ")

        return cls(
            organization=org,
            project=project,
            wiki_name=wiki_name,
            page_id=page_id,
            page_title=page_title,
            url=wiki_url,
        )


@dataclass
class ChildPBIGenerationResult:
    """Result of child PBI generation."""

    parent_id: str
    parent_title: str
    parent_type: WorkItemType
    existing_children: List[str]
    generated_children: List[str]
    total_children: int
    success: bool
    error_message: Optional[str] = None


class EpicFeatureGenerator:
    """Generate child PBIs from Epic/Feature/Enabler work items."""

    def __init__(
        self,
        ado_plugin: AzureDevOpsPlugin,
        config: PluginConfig,
        pbi_generator: Optional[PBIGenerator] = None,
    ):
        """
        Initialize Epic/Feature generator.

        Args:
            ado_plugin: Configured Azure DevOps plugin
            config: Plugin configuration
            pbi_generator: PBI generator (creates new if not provided)
        """
        self.ado_plugin = ado_plugin
        self.config = config
        self.pbi_generator = pbi_generator or PBIGenerator(ado_plugin, config)
        self.logger = logging.getLogger(__name__)

    def process_work_item_url(
        self, ado_url: str, auto_generate: bool = True
    ) -> ChildPBIGenerationResult:
        """
        Process ADO work item URL and generate/find child PBIs.

        Args:
            ado_url: Azure DevOps work item URL (Epic, Feature, or Enabler)
            auto_generate: If True, auto-generate missing child PBIs

        Returns:
            Result with existing and generated child PBIs
        """
        # Parse URL
        ado_ref = ADOWorkItemReference.parse_url(ado_url)
        if not ado_ref:
            return ChildPBIGenerationResult(
                parent_id="",
                parent_title="",
                parent_type=WorkItemType.PBI,
                existing_children=[],
                generated_children=[],
                total_children=0,
                success=False,
                error_message=f"Invalid ADO URL: {ado_url}",
            )

        try:
            # Fetch work item
            work_item = self.ado_plugin.get_work_item(ado_ref.work_item_id, self.config)

            # Update work item type
            ado_ref.title = work_item.title
            ado_ref.description = work_item.description
            ado_ref.work_item_type = self._get_work_item_type(work_item)

            # Find existing child PBIs
            existing_children = self._find_child_work_items(ado_ref.work_item_id)

            self.logger.info(
                f"Found {len(existing_children)} existing child PBIs for {ado_ref.work_item_type.value} {ado_ref.work_item_id}"
            )

            # Generate missing child PBIs if requested
            generated_children = []
            if auto_generate:
                generated_children = self._generate_child_pbis(work_item, ado_ref)

            return ChildPBIGenerationResult(
                parent_id=ado_ref.work_item_id,
                parent_title=ado_ref.title,
                parent_type=ado_ref.work_item_type,
                existing_children=existing_children,
                generated_children=generated_children,
                total_children=len(existing_children) + len(generated_children),
                success=True,
            )

        except Exception as e:
            self.logger.error(f"Failed to process work item {ado_ref.work_item_id}: {e}")
            return ChildPBIGenerationResult(
                parent_id=ado_ref.work_item_id,
                parent_title=ado_ref.title,
                parent_type=ado_ref.work_item_type,
                existing_children=[],
                generated_children=[],
                total_children=0,
                success=False,
                error_message=str(e),
            )

    def process_wiki_url(
        self, wiki_url: str, auto_generate: bool = True
    ) -> List[ChildPBIGenerationResult]:
        """
        Process wiki URL, extract ADO work item references, and generate child PBIs.

        Args:
            wiki_url: Azure DevOps wiki page URL
            auto_generate: If True, auto-generate missing child PBIs

        Returns:
            List of results for each work item found in wiki
        """
        # Parse wiki URL
        wiki_ref = WikiReference.parse_url(wiki_url)
        if not wiki_ref:
            self.logger.error(f"Invalid wiki URL: {wiki_url}")
            return []

        try:
            # Fetch wiki page content
            wiki_content = self._fetch_wiki_content(wiki_ref)

            # Extract ADO work item references from wiki
            work_item_urls = self._extract_work_item_urls(wiki_content)

            self.logger.info(
                f"Found {len(work_item_urls)} ADO work item references in wiki page"
            )

            # Process each work item
            results = []
            for work_item_url in work_item_urls:
                result = self.process_work_item_url(work_item_url, auto_generate)
                results.append(result)

            return results

        except Exception as e:
            self.logger.error(f"Failed to process wiki page: {e}")
            return []

    def generate_pbis_from_epic(self, epic_id: str) -> List[str]:
        """
        Generate child PBIs from Epic work item.

        Args:
            epic_id: Epic work item ID

        Returns:
            List of created PBI IDs
        """
        try:
            # Fetch Epic
            epic = self.ado_plugin.get_work_item(epic_id, self.config)

            # Parse Epic description for requirements
            child_pbis = self._parse_epic_requirements(epic)

            pbi_ids = []
            for pbi_spec in child_pbis:
                # Create PBI
                if pbi_spec["type"] == PBIType.ENABLER:
                    enabler = EnablerPBI(
                        title=pbi_spec["title"],
                        description=pbi_spec["description"],
                        technical_details=pbi_spec.get("technical_details", ""),
                        acceptance_criteria=pbi_spec.get("acceptance_criteria", []),
                        story_points=pbi_spec.get("story_points", 5.0),
                        priority=pbi_spec.get("priority", WorkItemPriority.MEDIUM),
                        tags=pbi_spec.get("tags", []) + ["epic", epic_id],
                    )
                    result = self.pbi_generator.generate_enabler_pbi(enabler)
                else:
                    feature = FeaturePBI(
                        title=pbi_spec["title"],
                        description=pbi_spec["description"],
                        user_story=pbi_spec.get("user_story", ""),
                        acceptance_criteria=pbi_spec.get("acceptance_criteria", []),
                        business_value=pbi_spec.get("business_value", ""),
                        story_points=pbi_spec.get("story_points", 5.0),
                        priority=pbi_spec.get("priority", WorkItemPriority.MEDIUM),
                        tags=pbi_spec.get("tags", []) + ["epic", epic_id],
                    )
                    result = self.pbi_generator.generate_feature_pbi(feature)

                if result.success:
                    # Link to Epic
                    self._link_parent_child(epic_id, result.work_item_id)
                    pbi_ids.append(result.work_item_id)

            self.logger.info(f"Generated {len(pbi_ids)} PBIs from Epic {epic_id}")
            return pbi_ids

        except Exception as e:
            self.logger.error(f"Failed to generate PBIs from Epic {epic_id}: {e}")
            return []

    # Helper methods
    def _get_work_item_type(self, work_item: WorkItem) -> WorkItemType:
        """Determine work item type from ADO work item."""
        # Check custom fields or title for work item type
        title_lower = work_item.title.lower()

        if "epic" in title_lower or "[epic]" in title_lower:
            return WorkItemType.EPIC
        elif "feature" in title_lower or "[feature]" in title_lower:
            return WorkItemType.FEATURE
        elif "enabler" in title_lower or "[enabler]" in title_lower:
            return WorkItemType.ENABLER
        elif "task" in title_lower:
            return WorkItemType.TASK
        else:
            return WorkItemType.PBI

    def _find_child_work_items(self, parent_id: str) -> List[str]:
        """
        Find all child work items of a parent.

        Args:
            parent_id: Parent work item ID

        Returns:
            List of child work item IDs
        """
        try:
            # Query for child work items using WIQL
            wiql_query = f"""
            SELECT [System.Id]
            FROM WorkItemLinks
            WHERE [Source].[System.Id] = {parent_id}
            AND [System.Links.LinkType] = 'System.LinkTypes.Hierarchy-Forward'
            MODE (MustContain)
            """

            # Execute query
            from azure.devops.v7_0.work_item_tracking import Wiql

            wiql = Wiql(query=wiql_query)
            result = self.ado_plugin.wit_client.query_by_wiql(wiql)

            # Extract child IDs
            child_ids = []
            if result.work_item_relations:
                for relation in result.work_item_relations:
                    if relation.target and relation.target.id != int(parent_id):
                        child_ids.append(str(relation.target.id))

            return child_ids

        except Exception as e:
            self.logger.error(f"Failed to find child work items: {e}")
            return []

    def _generate_child_pbis(
        self, parent_work_item: WorkItem, ado_ref: ADOWorkItemReference
    ) -> List[str]:
        """
        Generate missing child PBIs from parent work item.

        Analyzes parent description and generates appropriate child PBIs.
        """
        generated_ids = []

        try:
            # Parse parent description for child requirements
            child_specs = self._parse_work_item_for_children(parent_work_item, ado_ref)

            for spec in child_specs:
                # Create child PBI
                if spec["type"] == PBIType.ENABLER:
                    enabler = EnablerPBI(
                        title=spec["title"],
                        description=spec["description"],
                        technical_details=spec.get("technical_details", ""),
                        acceptance_criteria=spec.get("acceptance_criteria", []),
                        story_points=spec.get("story_points", 5.0),
                        priority=parent_work_item.priority,
                        tags=[ado_ref.work_item_type.value.lower(), ado_ref.work_item_id],
                    )
                    result = self.pbi_generator.generate_enabler_pbi(enabler)
                else:
                    feature = FeaturePBI(
                        title=spec["title"],
                        description=spec["description"],
                        user_story=spec.get("user_story", ""),
                        acceptance_criteria=spec.get("acceptance_criteria", []),
                        business_value=spec.get("business_value", ""),
                        story_points=spec.get("story_points", 5.0),
                        priority=parent_work_item.priority,
                        tags=[ado_ref.work_item_type.value.lower(), ado_ref.work_item_id],
                    )
                    result = self.pbi_generator.generate_feature_pbi(feature)

                if result.success:
                    # Link to parent
                    self._link_parent_child(ado_ref.work_item_id, result.work_item_id)
                    generated_ids.append(result.work_item_id)

            self.logger.info(
                f"Generated {len(generated_ids)} child PBIs for {ado_ref.work_item_type.value} {ado_ref.work_item_id}"
            )

        except Exception as e:
            self.logger.error(f"Failed to generate child PBIs: {e}")

        return generated_ids

    def _parse_work_item_for_children(
        self, work_item: WorkItem, ado_ref: ADOWorkItemReference
    ) -> List[Dict]:
        """
        Parse work item description to extract child PBI specifications.

        Looks for:
        - Bullet points with child requirements
        - Numbered lists
        - Sections marked with headers
        """
        child_specs = []

        description = work_item.description.lower()

        # Check if description contains structured child items
        # Pattern 1: Bullet points with "- [Enabler] ..." or "- [Feature] ..."
        pattern = r"-\s*\[(Enabler|Feature)\]\s*(.+?)(?=\n-|\n\n|$)"
        matches = re.finditer(pattern, work_item.description, re.MULTILINE)

        for match in matches:
            pbi_type_str, title = match.groups()
            pbi_type = (
                PBIType.ENABLER if pbi_type_str == "Enabler" else PBIType.FEATURE
            )

            child_specs.append(
                {
                    "type": pbi_type,
                    "title": title.strip(),
                    "description": f"Child of {ado_ref.work_item_type.value} {ado_ref.work_item_id}: {ado_ref.title}",
                    "story_points": 5.0,
                }
            )

        # Pattern 2: Numbered list with items
        if not child_specs:
            pattern = r"\d+\.\s+(.+?)(?=\n\d+\.|\n\n|$)"
            matches = re.finditer(pattern, work_item.description, re.MULTILINE)

            for match in matches:
                title = match.group(1).strip()

                # Detect type from title
                pbi_type = (
                    PBIType.ENABLER
                    if any(
                        keyword in title.lower()
                        for keyword in ["api", "framework", "pipeline", "setup"]
                    )
                    else PBIType.FEATURE
                )

                child_specs.append(
                    {
                        "type": pbi_type,
                        "title": title,
                        "description": f"Child of {ado_ref.work_item_type.value} {ado_ref.work_item_id}: {ado_ref.title}",
                        "story_points": 5.0,
                    }
                )

        # If no structured format found, create single child PBI
        if not child_specs:
            # Default: Create one child PBI with same type as parent
            pbi_type = (
                PBIType.ENABLER
                if ado_ref.work_item_type == WorkItemType.ENABLER
                else PBIType.FEATURE
            )

            child_specs.append(
                {
                    "type": pbi_type,
                    "title": f"Implement {ado_ref.title}",
                    "description": work_item.description,
                    "story_points": 8.0,
                }
            )

        return child_specs

    def _parse_epic_requirements(self, epic: WorkItem) -> List[Dict]:
        """Parse Epic description to extract child PBI requirements."""
        return self._parse_work_item_for_children(
            epic,
            ADOWorkItemReference(
                organization=self.config.organization,
                project=self.config.project,
                work_item_id=epic.id,
                work_item_type=WorkItemType.EPIC,
                url="",
                title=epic.title,
                description=epic.description,
            ),
        )

    def _fetch_wiki_content(self, wiki_ref: WikiReference) -> str:
        """
        Fetch wiki page content from Azure DevOps.

        Args:
            wiki_ref: Wiki page reference

        Returns:
            Wiki page markdown content
        """
        try:
            # Use Azure DevOps REST API to fetch wiki content
            import requests

            url = f"https://dev.azure.com/{wiki_ref.organization}/{wiki_ref.project}/_apis/wiki/wikis/{wiki_ref.wiki_name}/pages/{wiki_ref.page_id}?includeContent=true&api-version=7.0"

            headers = {"Authorization": f"Basic {self.config.api_key}"}

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            wiki_data = response.json()
            return wiki_data.get("content", "")

        except Exception as e:
            self.logger.error(f"Failed to fetch wiki content: {e}")
            # Return empty string to continue processing
            return ""

    def _extract_work_item_urls(self, wiki_content: str) -> List[str]:
        """
        Extract ADO work item URLs from wiki markdown content.

        Looks for:
        - [[123456]] - ADO work item reference
        - https://dev.azure.com/.../workitems/edit/123456
        - [[Epic: Title|123456]]
        """
        urls = []

        # Pattern 1: [[123456]] format
        pattern = r"\[\[(\d+)\]\]"
        matches = re.finditer(pattern, wiki_content)
        for match in matches:
            work_item_id = match.group(1)
            url = f"https://dev.azure.com/{self.config.organization}/{self.config.project}/_workitems/edit/{work_item_id}"
            urls.append(url)

        # Pattern 2: Full URLs
        pattern = r"https://dev\.azure\.com/[^/]+/[^/]+/_workitems/edit/\d+"
        matches = re.finditer(pattern, wiki_content)
        for match in matches:
            urls.append(match.group(0))

        # Pattern 3: [[Epic: Title|123456]] format
        pattern = r"\[\[[^\]]+\|(\d+)\]\]"
        matches = re.finditer(pattern, wiki_content)
        for match in matches:
            work_item_id = match.group(1)
            url = f"https://dev.azure.com/{self.config.organization}/{self.config.project}/_workitems/edit/{work_item_id}"
            if url not in urls:
                urls.append(url)

        return list(set(urls))  # Remove duplicates

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
                        "attributes": {"comment": "Child PBI"},
                    }
                ]
            }

            self.ado_plugin.update_work_item(child_id, updates, self.config)
            self.logger.info(f"Linked child {child_id} to parent {parent_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to link parent-child: {e}")
            return False
