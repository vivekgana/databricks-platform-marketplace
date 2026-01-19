"""
Unit tests for GitHub Adapter.

Tests the GitHub plugin adapter functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from ai_sdlc.plugins.adapters.github_adapter import GitHubAdapter
from ai_sdlc.plugins.models import WorkItem, PullRequest, WorkItemUpdate


class TestGitHubAdapter:
    """Test GitHub adapter functionality."""

    @pytest.fixture
    def mock_repo(self):
        """Create a mock GitHub repository."""
        mock = Mock()
        mock.get_issue = Mock()
        mock.create_issue = Mock()
        mock.get_pull = Mock()
        mock.create_pull = Mock()
        return mock

    @pytest.fixture
    def github_adapter(self, mock_repo):
        """Create GitHub adapter with mocked dependencies."""
        adapter = GitHubAdapter()
        adapter.github_client = Mock()
        adapter.repo = mock_repo
        adapter.owner = "test-owner"
        adapter.repository = "test-repo"
        adapter.initialized = True
        return adapter

    def test_get_name(self):
        """Test plugin name."""
        adapter = GitHubAdapter()
        assert adapter.get_name() == "github"

    def test_validate_config_valid(self):
        """Test config validation with valid config."""
        adapter = GitHubAdapter()
        config = {
            "owner": "test-owner",
            "repository": "test-repo",
            "token": "ghp_test_token",
        }
        assert adapter.validate_config(config) is True

    def test_validate_config_missing_fields(self):
        """Test config validation with missing fields."""
        adapter = GitHubAdapter()
        config = {"owner": "test-owner"}  # Missing repository and token
        assert adapter.validate_config(config) is False

    @patch("ai_sdlc.plugins.adapters.github_adapter.Github")
    def test_initialize_success(self, mock_github_class):
        """Test successful initialization."""
        mock_client = Mock()
        mock_repo = Mock()
        mock_client.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_client

        adapter = GitHubAdapter()
        config = {
            "owner": "test-owner",
            "repository": "test-repo",
            "token": "ghp_test_token",
        }

        result = adapter.initialize(config)

        assert result is True
        assert adapter.initialized is True
        assert adapter.owner == "test-owner"
        assert adapter.repository == "test-repo"
        mock_github_class.assert_called_once_with("ghp_test_token")

    def test_get_work_item(self, github_adapter, mock_repo):
        """Test getting issue (work item)."""
        # Mock GitHub issue
        mock_issue = Mock()
        mock_issue.number = 123
        mock_issue.title = "Test Issue"
        mock_issue.body = "Test Description"
        mock_issue.state = "open"
        mock_issue.assignee = Mock(login="john_doe")
        mock_issue.created_at = datetime(2026, 1, 18, 0, 0)
        mock_issue.updated_at = datetime(2026, 1, 18, 12, 0)
        mock_issue.html_url = "https://github.com/test-owner/test-repo/issues/123"
        mock_issue.labels = [Mock(name="bug"), Mock(name="high-priority")]

        mock_repo.get_issue.return_value = mock_issue

        work_item = github_adapter.get_work_item("123")

        assert isinstance(work_item, WorkItem)
        assert work_item.id == "123"
        assert work_item.title == "Test Issue"
        assert work_item.description == "Test Description"
        assert work_item.state == "open"
        assert work_item.assigned_to == "john_doe"
        assert work_item.tags == ["bug", "high-priority"]
        assert work_item.tool_name == "github"

    def test_create_work_item(self, github_adapter, mock_repo):
        """Test creating issue."""
        # Mock GitHub issue creation
        mock_issue = Mock()
        mock_issue.number = 124
        mock_issue.title = "New Issue"
        mock_issue.body = "New Description"
        mock_issue.state = "open"
        mock_issue.assignee = None
        mock_issue.created_at = datetime.now()
        mock_issue.updated_at = datetime.now()
        mock_issue.html_url = "https://github.com/test-owner/test-repo/issues/124"
        mock_issue.labels = []

        mock_repo.create_issue.return_value = mock_issue
        mock_repo.get_issue.return_value = mock_issue

        work_item = github_adapter.create_work_item(
            title="New Issue",
            description="New Description",
            item_type="issue",
        )

        assert isinstance(work_item, WorkItem)
        assert work_item.title == "New Issue"
        mock_repo.create_issue.assert_called_once()

    def test_create_pull_request(self, github_adapter, mock_repo):
        """Test creating pull request."""
        # Mock GitHub PR
        mock_pr = Mock()
        mock_pr.number = 456
        mock_pr.title = "Test PR"
        mock_pr.body = "PR Description"
        mock_pr.state = "open"
        mock_pr.user = Mock(login="jane_doe")
        mock_pr.head = Mock(ref="feature-branch")
        mock_pr.base = Mock(ref="main")
        mock_pr.created_at = datetime.now()
        mock_pr.updated_at = datetime.now()
        mock_pr.html_url = "https://github.com/test-owner/test-repo/pull/456"
        mock_pr.labels = []
        mock_pr.get_review_requests.return_value = ([], [])
        mock_pr.create_review_request = Mock()

        mock_repo.create_pull.return_value = mock_pr

        pr = github_adapter.create_pull_request(
            title="Test PR",
            description="PR Description",
            source_branch="feature-branch",
            target_branch="main",
            reviewers=["reviewer1"],
        )

        assert isinstance(pr, PullRequest)
        assert pr.title == "Test PR"
        assert pr.source_branch == "feature-branch"
        assert pr.target_branch == "main"
        mock_repo.create_pull.assert_called_once()

    def test_get_changed_files(self, github_adapter, mock_repo):
        """Test getting changed files in PR."""
        # Mock PR files
        mock_file1 = Mock(filename="file1.py")
        mock_file2 = Mock(filename="file2.py")

        mock_pr = Mock()
        mock_pr.get_files.return_value = [mock_file1, mock_file2]

        mock_repo.get_pull.return_value = mock_pr

        files = github_adapter.get_changed_files("456")

        assert files == ["file1.py", "file2.py"]

    def test_search_work_items(self, github_adapter):
        """Test searching issues."""
        # Mock search results
        mock_issue1 = Mock()
        mock_issue1.number = 123
        mock_issue1.title = "Issue 1"
        mock_issue1.body = "Description 1"
        mock_issue1.state = "open"
        mock_issue1.assignee = None
        mock_issue1.created_at = datetime.now()
        mock_issue1.updated_at = datetime.now()
        mock_issue1.html_url = "https://github.com/test-owner/test-repo/issues/123"
        mock_issue1.labels = []

        mock_issue2 = Mock()
        mock_issue2.number = 124
        mock_issue2.title = "Issue 2"
        mock_issue2.body = "Description 2"
        mock_issue2.state = "open"
        mock_issue2.assignee = None
        mock_issue2.created_at = datetime.now()
        mock_issue2.updated_at = datetime.now()
        mock_issue2.html_url = "https://github.com/test-owner/test-repo/issues/124"
        mock_issue2.labels = []

        github_adapter.github_client.search_issues.return_value = [
            mock_issue1,
            mock_issue2,
        ]
        github_adapter.repo.get_issue.side_effect = [mock_issue1, mock_issue2]

        results = github_adapter.search_work_items("test query", max_results=10)

        assert len(results) == 2
        assert all(isinstance(item, WorkItem) for item in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
