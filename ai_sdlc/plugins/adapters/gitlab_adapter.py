"""
GitLab Plugin Adapter.

Integrates with GitLab for source control, issues, and CI/CD.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from ai_sdlc.plugins.base import (
    WorkItemPlugin,
    PullRequestPlugin,
    ArtifactPlugin,
    PipelinePlugin,
    PluginType,
    PluginCapability,
)
from ai_sdlc.plugins.models import (
    WorkItem,
    WorkItemUpdate,
    PullRequest,
    Artifact,
    PipelineRun,
    Comment,
    Attachment,
)

logger = logging.getLogger(__name__)


class GitLabAdapter(WorkItemPlugin, PullRequestPlugin, ArtifactPlugin, PipelinePlugin):
    """GitLab plugin adapter."""

    def __init__(self):
        super().__init__()
        self.gitlab_client = None
        self.project = None
        self.project_id = None
        self.url = None

    def get_name(self) -> str:
        return "gitlab"

    def get_type(self) -> PluginType:
        return PluginType.SOURCE_CONTROL

    def get_capabilities(self) -> List[PluginCapability]:
        return [
            PluginCapability.WORK_ITEM_MANAGEMENT,
            PluginCapability.PULL_REQUEST,
            PluginCapability.ARTIFACT_STORAGE,
            PluginCapability.PIPELINE_EXECUTION,
        ]

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate GitLab configuration."""
        required = ["url", "project_id", "token"]
        return all(k in config for k in required)

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize GitLab client."""
        try:
            import gitlab

            self.url = config["url"]
            self.project_id = config["project_id"]
            token = config["token"]

            self.gitlab_client = gitlab.Gitlab(self.url, private_token=token)
            self.project = self.gitlab_client.projects.get(self.project_id)

            self.config = config
            self.initialized = True
            logger.info(f"Initialized GitLab adapter for project {self.project_id}")
            return True

        except ImportError:
            logger.error(
                "python-gitlab library not installed. Install with: pip install python-gitlab"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to initialize GitLab adapter: {e}")
            return False

    # Work Item (Issues) methods
    def get_work_item(self, work_item_id: str) -> WorkItem:
        """Get issue from GitLab."""
        issue = self.project.issues.get(int(work_item_id))

        return WorkItem(
            id=str(issue.iid),
            title=issue.title,
            description=issue.description or "",
            state=issue.state,
            assigned_to=issue.assignee["name"] if issue.assignee else None,
            created_date=self._parse_date(issue.created_at),
            updated_date=self._parse_date(issue.updated_at),
            item_type="issue",
            parent_id=None,  # Can be extracted from epic relationship if needed
            tags=issue.labels,
            custom_fields={},
            url=issue.web_url,
            tool_name="gitlab",
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
        """Create issue in GitLab."""
        issue_data = {
            "title": title,
            "description": description,
        }

        if assigned_to:
            # Get user ID by username
            users = self.gitlab_client.users.list(username=assigned_to)
            if users:
                issue_data["assignee_ids"] = [users[0].id]

        if kwargs.get("labels"):
            issue_data["labels"] = kwargs["labels"]

        issue = self.project.issues.create(issue_data)
        return self.get_work_item(str(issue.iid))

    def update_work_item(self, work_item_id: str, update: WorkItemUpdate) -> WorkItem:
        """Update issue in GitLab."""
        issue = self.project.issues.get(int(work_item_id))

        if update.title:
            issue.title = update.title

        if update.description:
            issue.description = update.description

        if update.state:
            state_map = {
                "done": "closed",
                "closed": "closed",
                "active": "opened",
                "open": "opened",
            }
            issue.state_event = state_map.get(update.state.lower(), "opened")

        if update.assigned_to:
            users = self.gitlab_client.users.list(username=update.assigned_to)
            if users:
                issue.assignee_ids = [users[0].id]

        if update.tags:
            issue.labels = update.tags

        issue.save()

        if update.comment:
            self.add_comment(work_item_id, update.comment)

        return self.get_work_item(work_item_id)

    def add_comment(self, work_item_id: str, comment: str) -> Comment:
        """Add comment to issue."""
        issue = self.project.issues.get(int(work_item_id))
        note = issue.notes.create({"body": comment})

        return Comment(
            id=str(note.id),
            content=comment,
            author=note.author["name"],
            created_date=self._parse_date(note.created_at),
        )

    def attach_file(
        self, work_item_id: str, file_path: str, comment: Optional[str] = None
    ) -> Attachment:
        """Attach file to issue."""
        # Upload file to project
        with open(file_path, "rb") as f:
            upload = self.project.upload(Path(file_path).name, filedata=f)

        # Add comment with file link
        filename = Path(file_path).name
        file_url = upload["url"]

        attachment_comment = f"📎 [{filename}]({file_url})"
        if comment:
            attachment_comment = f"{comment}\n\n{attachment_comment}"

        self.add_comment(work_item_id, attachment_comment)

        return Attachment(
            id=str(upload.get("id", "")),
            filename=filename,
            url=file_url,
            size_bytes=(
                Path(file_path).stat().st_size if Path(file_path).exists() else 0
            ),
            content_type="application/octet-stream",
            created_date=datetime.now(),
            created_by="",
        )

    def get_children(self, work_item_id: str) -> List[WorkItem]:
        """Get child issues (not directly supported, would need epic relationship)."""
        return []

    def link_work_items(self, source_id: str, target_id: str, link_type: str) -> bool:
        """Link issues (via cross-reference)."""
        try:
            issue = self.project.issues.get(int(source_id))
            issue.notes.create({"body": f"Related to #{target_id}"})
            return True
        except Exception as e:
            logger.error(f"Failed to link issues: {e}")
            return False

    def search_work_items(self, query: str, max_results: int = 100) -> List[WorkItem]:
        """Search issues."""
        issues = self.project.issues.list(search=query, per_page=max_results)
        return [self.get_work_item(str(issue.iid)) for issue in issues]

    # Pull Request (Merge Request) methods
    def create_pull_request(
        self,
        title: str,
        description: str,
        source_branch: str,
        target_branch: str,
        work_item_ids: Optional[List[str]] = None,
        reviewers: Optional[List[str]] = None,
    ) -> PullRequest:
        """Create merge request."""
        mr_data = {
            "source_branch": source_branch,
            "target_branch": target_branch,
            "title": title,
            "description": description,
        }

        # Link to issues
        if work_item_ids:
            mr_data["description"] += "\n\nCloses:\n"
            for work_item_id in work_item_ids:
                mr_data["description"] += f"- #{work_item_id}\n"

        mr = self.project.mergerequests.create(mr_data)

        # Add reviewers
        if reviewers:
            reviewer_ids = []
            for username in reviewers:
                users = self.gitlab_client.users.list(username=username)
                if users:
                    reviewer_ids.append(users[0].id)

            if reviewer_ids:
                mr.reviewer_ids = reviewer_ids
                mr.save()

        return self._convert_mr(mr)

    def get_pull_request(self, pr_id: str) -> PullRequest:
        """Get merge request by ID."""
        mr = self.project.mergerequests.get(int(pr_id))
        return self._convert_mr(mr)

    def add_comment(self, pr_id: str, comment: str) -> Comment:
        """Add comment to merge request."""
        mr = self.project.mergerequests.get(int(pr_id))
        note = mr.notes.create({"body": comment})

        return Comment(
            id=str(note.id),
            content=comment,
            author=note.author["name"],
            created_date=self._parse_date(note.created_at),
        )

    def link_work_items(self, pr_id: str, work_item_ids: List[str]) -> bool:
        """Link work items to merge request."""
        try:
            mr = self.project.mergerequests.get(int(pr_id))

            description = mr.description or ""
            if "Closes:" not in description:
                description += "\n\nCloses:\n"

            for work_item_id in work_item_ids:
                if f"#{work_item_id}" not in description:
                    description += f"- #{work_item_id}\n"

            mr.description = description
            mr.save()
            return True

        except Exception as e:
            logger.error(f"Failed to link work items to MR: {e}")
            return False

    def get_changed_files(self, pr_id: str) -> List[str]:
        """Get changed files in merge request."""
        mr = self.project.mergerequests.get(int(pr_id))
        changes = mr.changes()
        return [change["new_path"] for change in changes.get("changes", [])]

    # Artifact methods (GitLab Package Registry)
    def upload_artifact(
        self,
        name: str,
        version: str,
        files: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        """Upload artifact to GitLab Package Registry."""
        # GitLab Package Registry requires specific package types
        logger.warning(
            "GitLab Package Registry upload requires package-type-specific implementation"
        )

        return Artifact(
            name=name,
            version=version,
            url=f"{self.url}/{self.project.path_with_namespace}/-/packages",
            size_bytes=sum(Path(f).stat().st_size for f in files if Path(f).exists()),
            created_date=datetime.now(),
            metadata=metadata or {},
            tool_name="gitlab",
        )

    def download_artifact(self, name: str, version: str, destination: str) -> str:
        """Download artifact from GitLab Package Registry."""
        logger.warning(
            "GitLab Package Registry download requires package-type-specific implementation"
        )
        return destination

    def list_versions(self, artifact_name: str) -> List[str]:
        """List artifact versions."""
        packages = self.project.packages.list(package_name=artifact_name)
        return [pkg.version for pkg in packages]

    # Pipeline methods (GitLab CI)
    def trigger_pipeline(
        self,
        pipeline_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        branch: Optional[str] = None,
    ) -> PipelineRun:
        """Trigger GitLab CI pipeline."""
        ref = branch or self.project.default_branch

        pipeline = self.project.pipelines.create(
            {"ref": ref, "variables": parameters or []}
        )

        return self._convert_pipeline(pipeline)

    def get_pipeline_run(self, run_id: str) -> PipelineRun:
        """Get pipeline status."""
        pipeline = self.project.pipelines.get(int(run_id))
        return self._convert_pipeline(pipeline)

    def get_logs(self, run_id: str) -> str:
        """Get pipeline execution logs."""
        pipeline = self.project.pipelines.get(int(run_id))
        jobs = pipeline.jobs.list()

        logs = ""
        for job in jobs:
            logs += f"\n=== Job: {job.name} ===\n"
            logs += job.trace().decode("utf-8")

        return logs

    def cancel_run(self, run_id: str) -> bool:
        """Cancel pipeline run."""
        try:
            pipeline = self.project.pipelines.get(int(run_id))
            pipeline.cancel()
            return True
        except Exception as e:
            logger.error(f"Failed to cancel pipeline: {e}")
            return False

    # Helper methods
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse GitLab date string."""
        if not date_str:
            return None

        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None

    def _convert_mr(self, mr) -> PullRequest:
        """Convert GitLab MR to universal format."""
        # Extract issue numbers from description
        work_item_ids = []
        if mr.description:
            import re

            work_item_ids = re.findall(r"#(\d+)", mr.description)

        reviewers = []
        if hasattr(mr, "reviewers") and mr.reviewers:
            reviewers = [r["name"] for r in mr.reviewers]

        return PullRequest(
            id=str(mr.iid),
            title=mr.title,
            description=mr.description or "",
            source_branch=mr.source_branch,
            target_branch=mr.target_branch,
            state=mr.state,
            author=mr.author["name"],
            created_date=self._parse_date(mr.created_at),
            updated_date=self._parse_date(mr.updated_at),
            url=mr.web_url,
            work_item_ids=work_item_ids,
            reviewers=reviewers,
            labels=mr.labels,
            tool_name="gitlab",
        )

    def _convert_pipeline(self, pipeline) -> PipelineRun:
        """Convert GitLab pipeline to universal format."""
        status_map = {
            "success": "succeeded",
            "failed": "failed",
            "running": "running",
            "pending": "pending",
            "canceled": "canceled",
        }

        duration = getattr(pipeline, "duration", None)

        return PipelineRun(
            id=str(pipeline.id),
            pipeline_name=f"Pipeline {pipeline.id}",
            status=status_map.get(pipeline.status, pipeline.status),
            started_date=self._parse_date(getattr(pipeline, "created_at", None)),
            completed_date=self._parse_date(getattr(pipeline, "finished_at", None)),
            url=pipeline.web_url,
            duration_seconds=duration,
            tool_name="gitlab",
        )
