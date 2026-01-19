"""
GitHub Plugin Adapter.

Integrates with GitHub for source control, issues, and packages.
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


class GitHubAdapter(WorkItemPlugin, PullRequestPlugin, ArtifactPlugin, PipelinePlugin):
    """GitHub plugin adapter."""

    def __init__(self):
        super().__init__()
        self.github_client = None
        self.repo = None
        self.owner = None
        self.repository = None

    def get_name(self) -> str:
        return "github"

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
        """Validate GitHub configuration."""
        required = ["owner", "repository", "token"]
        return all(k in config for k in required)

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize GitHub client."""
        try:
            from github import Github

            self.owner = config["owner"]
            self.repository = config["repository"]
            token = config["token"]

            self.github_client = Github(token)
            self.repo = self.github_client.get_repo(f"{self.owner}/{self.repository}")

            self.config = config
            self.initialized = True
            logger.info(
                f"Initialized GitHub adapter for {self.owner}/{self.repository}"
            )
            return True

        except ImportError:
            logger.error(
                "PyGithub library not installed. Install with: pip install PyGithub"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to initialize GitHub adapter: {e}")
            return False

    # Work Item (Issues) methods
    def get_work_item(self, work_item_id: str) -> WorkItem:
        """Get issue from GitHub."""
        issue = self.repo.get_issue(int(work_item_id))

        return WorkItem(
            id=str(issue.number),
            title=issue.title,
            description=issue.body or "",
            state=issue.state,
            assigned_to=issue.assignee.login if issue.assignee else None,
            created_date=issue.created_at,
            updated_date=issue.updated_at,
            item_type="issue",
            parent_id=None,  # GitHub doesn't have parent-child relationships
            tags=[label.name for label in issue.labels],
            custom_fields={},
            url=issue.html_url,
            tool_name="github",
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
        """Create issue in GitHub."""
        labels = kwargs.get("labels", [])
        issue = self.repo.create_issue(
            title=title, body=description, assignee=assigned_to, labels=labels
        )

        return self.get_work_item(str(issue.number))

    def update_work_item(self, work_item_id: str, update: WorkItemUpdate) -> WorkItem:
        """Update issue in GitHub."""
        issue = self.repo.get_issue(int(work_item_id))

        if update.title:
            issue.edit(title=update.title)

        if update.description:
            issue.edit(body=update.description)

        if update.state:
            state_map = {"done": "closed", "closed": "closed", "active": "open"}
            github_state = state_map.get(update.state.lower(), "open")
            issue.edit(state=github_state)

        if update.assigned_to:
            issue.edit(assignee=update.assigned_to)

        if update.tags:
            issue.edit(labels=update.tags)

        if update.comment:
            self.add_comment(work_item_id, update.comment)

        return self.get_work_item(work_item_id)

    def add_comment(self, work_item_id: str, comment: str) -> Comment:
        """Add comment to issue."""
        issue = self.repo.get_issue(int(work_item_id))
        gh_comment = issue.create_comment(comment)

        return Comment(
            id=str(gh_comment.id),
            content=comment,
            author=gh_comment.user.login,
            created_date=gh_comment.created_at,
            updated_date=gh_comment.updated_at,
        )

    def attach_file(
        self, work_item_id: str, file_path: str, comment: Optional[str] = None
    ) -> Attachment:
        """Attach file to issue (via comment with uploaded asset)."""
        # GitHub doesn't support direct file attachments
        # We'll add a comment with file information
        filename = Path(file_path).name
        file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0

        attachment_comment = f"📎 Attachment: {filename} ({file_size} bytes)"
        if comment:
            attachment_comment = f"{comment}\n\n{attachment_comment}"

        gh_comment = self.add_comment(work_item_id, attachment_comment)

        return Attachment(
            id=gh_comment.id,
            filename=filename,
            url="",  # GitHub issues don't support file uploads
            size_bytes=file_size,
            content_type="application/octet-stream",
            created_date=gh_comment.created_date,
            created_by=gh_comment.author,
        )

    def get_children(self, work_item_id: str) -> List[WorkItem]:
        """Get child issues (not supported by GitHub)."""
        return []

    def link_work_items(self, source_id: str, target_id: str, link_type: str) -> bool:
        """Link issues (via cross-reference in comment)."""
        try:
            issue = self.repo.get_issue(int(source_id))
            issue.create_comment(f"Related to #{target_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to link issues: {e}")
            return False

    def search_work_items(self, query: str, max_results: int = 100) -> List[WorkItem]:
        """Search issues."""
        search_query = f"repo:{self.owner}/{self.repository} {query} is:issue"
        issues = self.github_client.search_issues(query=search_query)

        results = []
        for i, issue in enumerate(issues):
            if i >= max_results:
                break
            results.append(self.get_work_item(str(issue.number)))

        return results

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
        """Create pull request."""
        pr = self.repo.create_pull(
            title=title, body=description, head=source_branch, base=target_branch
        )

        # Add reviewers
        if reviewers:
            pr.create_review_request(reviewers=reviewers)

        # Link to issues
        if work_item_ids:
            pr_body = pr.body or ""
            pr_body += "\n\nRelated issues:\n"
            for work_item_id in work_item_ids:
                pr_body += f"- Closes #{work_item_id}\n"
            pr.edit(body=pr_body)

        return self._convert_pr(pr)

    def get_pull_request(self, pr_id: str) -> PullRequest:
        """Get pull request by ID."""
        pr = self.repo.get_pull(int(pr_id))
        return self._convert_pr(pr)

    def add_comment(self, pr_id: str, comment: str) -> Comment:
        """Add comment to pull request."""
        pr = self.repo.get_pull(int(pr_id))
        gh_comment = pr.create_issue_comment(comment)

        return Comment(
            id=str(gh_comment.id),
            content=comment,
            author=gh_comment.user.login,
            created_date=gh_comment.created_at,
        )

    def link_work_items(self, pr_id: str, work_item_ids: List[str]) -> bool:
        """Link work items to pull request."""
        try:
            pr = self.repo.get_pull(int(pr_id))
            pr_body = pr.body or ""

            if "Related issues:" not in pr_body:
                pr_body += "\n\nRelated issues:\n"

            for work_item_id in work_item_ids:
                if f"#{work_item_id}" not in pr_body:
                    pr_body += f"- Closes #{work_item_id}\n"

            pr.edit(body=pr_body)
            return True

        except Exception as e:
            logger.error(f"Failed to link work items to PR: {e}")
            return False

    def get_changed_files(self, pr_id: str) -> List[str]:
        """Get changed files in pull request."""
        pr = self.repo.get_pull(int(pr_id))
        return [f.filename for f in pr.get_files()]

    # Artifact methods (GitHub Packages)
    def upload_artifact(
        self,
        name: str,
        version: str,
        files: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        """Upload artifact to GitHub Packages."""
        # GitHub Packages requires specific package types (npm, docker, etc.)
        # This is a placeholder - actual implementation depends on package type
        logger.warning(
            "GitHub Packages upload requires package-type-specific implementation"
        )

        return Artifact(
            name=name,
            version=version,
            url=f"https://github.com/{self.owner}/{self.repository}/packages",
            size_bytes=sum(Path(f).stat().st_size for f in files if Path(f).exists()),
            created_date=datetime.now(),
            metadata=metadata or {},
            tool_name="github",
        )

    def download_artifact(self, name: str, version: str, destination: str) -> str:
        """Download artifact from GitHub Packages."""
        logger.warning(
            "GitHub Packages download requires package-type-specific implementation"
        )
        return destination

    def list_versions(self, artifact_name: str) -> List[str]:
        """List artifact versions."""
        logger.warning(
            "GitHub Packages list requires package-type-specific implementation"
        )
        return []

    # Pipeline methods (GitHub Actions)
    def trigger_pipeline(
        self,
        pipeline_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        branch: Optional[str] = None,
    ) -> PipelineRun:
        """Trigger GitHub Actions workflow."""
        workflows = self.repo.get_workflows()

        workflow = None
        for wf in workflows:
            if wf.name == pipeline_name or wf.path.endswith(f"/{pipeline_name}"):
                workflow = wf
                break

        if not workflow:
            raise ValueError(f"Workflow {pipeline_name} not found")

        ref = branch or self.repo.default_branch
        workflow.create_dispatch(ref=ref, inputs=parameters or {})

        # Get the latest run (just created)
        runs = workflow.get_runs()
        latest_run = runs[0] if runs.totalCount > 0 else None

        if latest_run:
            return self._convert_pipeline_run(latest_run)
        else:
            # Return pending run
            return PipelineRun(
                id="pending",
                pipeline_name=pipeline_name,
                status="pending",
                url=workflow.html_url,
                tool_name="github",
            )

    def get_pipeline_run(self, run_id: str) -> PipelineRun:
        """Get pipeline run status."""
        run = self.repo.get_workflow_run(int(run_id))
        return self._convert_pipeline_run(run)

    def get_logs(self, run_id: str) -> str:
        """Get pipeline execution logs."""
        run = self.repo.get_workflow_run(int(run_id))
        # GitHub API requires downloading logs as zip
        logger.warning("GitHub Actions logs require download and extraction")
        return f"Logs URL: {run.logs_url}"

    def cancel_run(self, run_id: str) -> bool:
        """Cancel pipeline run."""
        try:
            run = self.repo.get_workflow_run(int(run_id))
            run.cancel()
            return True
        except Exception as e:
            logger.error(f"Failed to cancel workflow run: {e}")
            return False

    # Helper methods
    def _convert_pr(self, gh_pr) -> PullRequest:
        """Convert GitHub PR to universal format."""
        # Extract issue numbers from PR body
        work_item_ids = []
        if gh_pr.body:
            import re

            work_item_ids = re.findall(r"#(\d+)", gh_pr.body)

        return PullRequest(
            id=str(gh_pr.number),
            title=gh_pr.title,
            description=gh_pr.body or "",
            source_branch=gh_pr.head.ref,
            target_branch=gh_pr.base.ref,
            state=gh_pr.state,
            author=gh_pr.user.login,
            created_date=gh_pr.created_at,
            updated_date=gh_pr.updated_at,
            url=gh_pr.html_url,
            work_item_ids=work_item_ids,
            reviewers=[r.login for r in gh_pr.get_review_requests()[0]],
            labels=[label.name for label in gh_pr.labels],
            tool_name="github",
        )

    def _convert_pipeline_run(self, run) -> PipelineRun:
        """Convert GitHub Actions run to universal format."""
        status_map = {
            "completed": "succeeded" if run.conclusion == "success" else "failed",
            "in_progress": "running",
            "queued": "pending",
        }

        duration = None
        if run.updated_at and run.created_at:
            duration = int((run.updated_at - run.created_at).total_seconds())

        return PipelineRun(
            id=str(run.id),
            pipeline_name=run.name,
            status=status_map.get(run.status, run.status),
            started_date=run.created_at,
            completed_date=run.updated_at,
            url=run.html_url,
            duration_seconds=duration,
            tool_name="github",
        )
