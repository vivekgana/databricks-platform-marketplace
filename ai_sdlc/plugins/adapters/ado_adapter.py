"""
Azure DevOps (ADO) Plugin Adapter.

Wraps the existing Azure DevOps integration into the unified plugin interface.
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from ai_sdlc.plugins.base import (
    WorkItemPlugin,
    PullRequestPlugin,
    ArtifactPlugin,
    PluginType,
    PluginCapability,
)
from ai_sdlc.plugins.models import (
    WorkItem,
    WorkItemUpdate,
    PullRequest,
    Artifact,
    Comment,
    Attachment,
)

# Add plugins directory to path for existing integration
sys.path.insert(
    0,
    str(
        Path(__file__).parent.parent.parent.parent
        / "plugins"
        / "databricks-devops-integrations"
    ),
)

from integrations.azure_devops.azure_devops_plugin import AzureDevOpsPlugin

logger = logging.getLogger(__name__)


class ADOAdapter(WorkItemPlugin, PullRequestPlugin, ArtifactPlugin):
    """Azure DevOps plugin adapter."""

    def __init__(self):
        super().__init__()
        self.ado_plugin = None
        self.organization = None
        self.project = None

    def get_name(self) -> str:
        return "ado"

    def get_type(self) -> PluginType:
        return PluginType.AGILE

    def get_capabilities(self) -> List[PluginCapability]:
        return [
            PluginCapability.WORK_ITEM_MANAGEMENT,
            PluginCapability.PULL_REQUEST,
            PluginCapability.ARTIFACT_STORAGE,
        ]

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate ADO configuration."""
        required = ["organization", "project", "pat"]
        return all(k in config for k in required)

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize ADO plugin."""
        try:
            self.organization = config["organization"]
            self.project = config["project"]
            pat = config["pat"]

            self.ado_plugin = AzureDevOpsPlugin(
                organization=self.organization,
                project=self.project,
                personal_access_token=pat,
            )

            self.config = config
            self.initialized = True
            logger.info(
                f"Initialized ADO adapter for {self.organization}/{self.project}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize ADO adapter: {e}")
            return False

    def get_work_item(self, work_item_id: str) -> WorkItem:
        """Get work item from ADO."""
        ado_item = self.ado_plugin.get_work_item(work_item_id)

        fields = ado_item["fields"]

        return WorkItem(
            id=str(ado_item["id"]),
            title=fields.get("System.Title", ""),
            description=fields.get("System.Description", ""),
            state=fields.get("System.State", "New"),
            assigned_to=(
                fields.get("System.AssignedTo", {}).get("displayName")
                if isinstance(fields.get("System.AssignedTo"), dict)
                else fields.get("System.AssignedTo")
            ),
            created_date=self._parse_date(fields.get("System.CreatedDate")),
            updated_date=self._parse_date(fields.get("System.ChangedDate")),
            item_type=fields.get("System.WorkItemType", "Task"),
            parent_id=(
                str(fields.get("System.Parent")) if "System.Parent" in fields else None
            ),
            tags=(
                fields.get("System.Tags", "").split("; ")
                if fields.get("System.Tags")
                else []
            ),
            custom_fields={k: v for k, v in fields.items() if k.startswith("Custom.")},
            url=ado_item["_links"]["html"]["href"],
            tool_name="ado",
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
        """Create work item in ADO."""
        result = self.ado_plugin.create_work_item(
            work_item_type=item_type,
            title=title,
            description=description,
            assigned_to=assigned_to,
            parent_id=int(parent_id) if parent_id else None,
            **kwargs,
        )

        return self.get_work_item(str(result["id"]))

    def update_work_item(self, work_item_id: str, update: WorkItemUpdate) -> WorkItem:
        """Update work item in ADO."""
        update_dict = {}

        if update.state:
            update_dict["state"] = update.state
        if update.assigned_to:
            update_dict["assigned_to"] = update.assigned_to
        if update.title:
            update_dict["title"] = update.title
        if update.description:
            update_dict["description"] = update.description
        if update.tags:
            update_dict["tags"] = "; ".join(update.tags)

        if update.custom_fields:
            update_dict.update(update.custom_fields)

        self.ado_plugin.update_work_item(work_item_id, **update_dict)

        if update.comment:
            self.add_comment(work_item_id, update.comment)

        return self.get_work_item(work_item_id)

    def add_comment(self, work_item_id: str, comment: str) -> Comment:
        """Add comment to work item."""
        result = self.ado_plugin.add_comment(work_item_id, comment)

        return Comment(
            id=str(result.get("id", "")),
            content=comment,
            author=result.get("createdBy", {}).get("displayName", "Unknown"),
            created_date=self._parse_date(result.get("createdDate")),
        )

    def attach_file(
        self, work_item_id: str, file_path: str, comment: Optional[str] = None
    ) -> Attachment:
        """Attach file to work item."""
        result = self.ado_plugin.attach_file(work_item_id, file_path, comment)

        return Attachment(
            id=str(result.get("id", "")),
            filename=Path(file_path).name,
            url=result.get("url", ""),
            size_bytes=(
                Path(file_path).stat().st_size if Path(file_path).exists() else 0
            ),
            content_type="application/octet-stream",
            created_date=datetime.now(),
            created_by=result.get("createdBy", {}).get("displayName", "Unknown"),
        )

    def get_children(self, work_item_id: str) -> List[WorkItem]:
        """Get child work items."""
        # Query for children using ADO relations
        work_item = self.ado_plugin.get_work_item(work_item_id)
        relations = work_item.get("relations", [])

        children = []
        for relation in relations:
            if relation.get("rel") == "System.LinkTypes.Hierarchy-Forward":
                child_url = relation["url"]
                child_id = child_url.split("/")[-1]
                children.append(self.get_work_item(child_id))

        return children

    def link_work_items(self, source_id: str, target_id: str, link_type: str) -> bool:
        """Link work items in ADO."""
        try:
            # Map generic link types to ADO-specific types
            link_type_map = {
                "related": "System.LinkTypes.Related",
                "parent": "System.LinkTypes.Hierarchy-Reverse",
                "child": "System.LinkTypes.Hierarchy-Forward",
                "blocks": "System.LinkTypes.Dependency-Forward",
                "blocked_by": "System.LinkTypes.Dependency-Reverse",
            }

            ado_link_type = link_type_map.get(link_type, link_type)

            self.ado_plugin.link_work_items(source_id, target_id, ado_link_type)
            return True

        except Exception as e:
            logger.error(f"Failed to link work items: {e}")
            return False

    def search_work_items(self, query: str, max_results: int = 100) -> List[WorkItem]:
        """Search work items using WIQL."""
        wiql = f"""
        SELECT [System.Id], [System.Title], [System.State]
        FROM WorkItems
        WHERE [System.TeamProject] = '{self.project}'
        AND [System.Title] CONTAINS '{query}'
        ORDER BY [System.ChangedDate] DESC
        """

        results = self.ado_plugin.query_work_items(wiql, top=max_results)
        return [self.get_work_item(str(item["id"])) for item in results]

    # Pull Request methods
    def create_pull_request(
        self,
        title: str,
        description: str,
        source_branch: str,
        target_branch: str,
        work_item_ids: Optional[List[str]] = None,
        reviewers: Optional[List[str]] = None,
    ) -> PullRequest:
        """Create pull request in Azure Repos."""
        repository = self.config.get("repository", "")

        result = self.ado_plugin.create_pull_request(
            repository=repository,
            source_branch=source_branch,
            target_branch=target_branch,
            title=title,
            description=description,
            work_item_refs=work_item_ids or [],
            reviewers=reviewers or [],
        )

        return self._convert_pr(result)

    def get_pull_request(self, pr_id: str) -> PullRequest:
        """Get pull request by ID."""
        repository = self.config.get("repository", "")
        result = self.ado_plugin.get_pull_request(repository, pr_id)
        return self._convert_pr(result)

    def add_comment(self, pr_id: str, comment: str) -> Comment:
        """Add comment to pull request."""
        repository = self.config.get("repository", "")
        result = self.ado_plugin.add_pr_comment(repository, pr_id, comment)

        return Comment(
            id=str(result.get("id", "")),
            content=comment,
            author=result.get("author", {}).get("displayName", "Unknown"),
            created_date=self._parse_date(result.get("publishedDate")),
        )

    def link_work_items(self, pr_id: str, work_item_ids: List[str]) -> bool:
        """Link work items to pull request."""
        repository = self.config.get("repository", "")
        try:
            self.ado_plugin.link_pr_to_work_items(repository, pr_id, work_item_ids)
            return True
        except Exception as e:
            logger.error(f"Failed to link work items to PR: {e}")
            return False

    def get_changed_files(self, pr_id: str) -> List[str]:
        """Get changed files in pull request."""
        repository = self.config.get("repository", "")
        files = self.ado_plugin.get_pr_files(repository, pr_id)
        return [f["path"] for f in files]

    # Artifact methods
    def upload_artifact(
        self,
        name: str,
        version: str,
        files: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        """Upload artifact to Azure Artifacts."""
        feed = self.config.get("feed", "")

        result = self.ado_plugin.create_artifact_package(
            work_item_id=metadata.get("work_item_id", "") if metadata else "",
            artifact_name=name,
            artifact_version=version,
            evidence_items=files,
            config={"feed": feed},
        )

        return Artifact(
            name=name,
            version=version,
            url=result.get("url", ""),
            size_bytes=sum(Path(f).stat().st_size for f in files if Path(f).exists()),
            created_date=datetime.now(),
            metadata=metadata or {},
            tool_name="ado",
        )

    def download_artifact(self, name: str, version: str, destination: str) -> str:
        """Download artifact from Azure Artifacts."""
        feed = self.config.get("feed", "")

        result = self.ado_plugin.download_artifact(
            feed=feed, artifact_name=name, version=version, destination=destination
        )

        return result

    def list_versions(self, artifact_name: str) -> List[str]:
        """List artifact versions."""
        feed = self.config.get("feed", "")
        versions = self.ado_plugin.list_artifact_versions(feed, artifact_name)
        return [v["version"] for v in versions]

    def link_to_work_item(self, artifact: Artifact, work_item_id: str) -> bool:
        """Link artifact to work item."""
        try:
            self.ado_plugin.link_artifact_to_work_item(
                work_item_id=work_item_id,
                artifact_name=artifact.name,
                artifact_version=artifact.version,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to link artifact to work item: {e}")
            return False

    # Helper methods
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse ADO date string to datetime."""
        if not date_str:
            return None

        try:
            # ADO uses ISO 8601 format
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None

    def _convert_pr(self, ado_pr: Dict[str, Any]) -> PullRequest:
        """Convert ADO PR to universal format."""
        return PullRequest(
            id=str(ado_pr["pullRequestId"]),
            title=ado_pr["title"],
            description=ado_pr.get("description", ""),
            source_branch=ado_pr["sourceRefName"].replace("refs/heads/", ""),
            target_branch=ado_pr["targetRefName"].replace("refs/heads/", ""),
            state=ado_pr["status"].lower(),
            author=ado_pr["createdBy"]["displayName"],
            created_date=self._parse_date(ado_pr.get("creationDate")),
            updated_date=self._parse_date(ado_pr.get("closedDate")),
            url=ado_pr["url"],
            work_item_ids=[str(ref["id"]) for ref in ado_pr.get("workItemRefs", [])],
            reviewers=[r["displayName"] for r in ado_pr.get("reviewers", [])],
            tool_name="ado",
        )
