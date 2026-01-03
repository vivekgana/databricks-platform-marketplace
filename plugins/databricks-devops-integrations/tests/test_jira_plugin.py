"""
Unit tests for JIRA Plugin
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime

from integrations.jira import JiraPlugin
from sdk import WorkItemStatus, WorkItemPriority
from sdk.exceptions import AuthenticationError, WorkItemNotFoundError, IntegrationError


@pytest.mark.unit
class TestJiraPlugin:
    """Test suite for JIRA Plugin"""

    def test_get_metadata(self):
        """Test plugin metadata"""
        plugin = JiraPlugin()
        metadata = plugin.get_metadata()

        assert metadata.name == "JIRA Integration"
        assert metadata.version == "1.0.0"
        assert "work_items" in metadata.supported_features
        assert metadata.requires_auth is True

    def test_validate_config_success(self, mock_jira_config):
        """Test successful configuration validation"""
        plugin = JiraPlugin()
        assert plugin.validate_config(mock_jira_config) is True

    def test_validate_config_missing_field(self, mock_jira_config):
        """Test configuration validation with missing field"""
        plugin = JiraPlugin()
        mock_jira_config.api_endpoint = ""

        with pytest.raises(Exception):  # ConfigurationError
            plugin.validate_config(mock_jira_config)

    @patch("integrations.jira.jira_plugin.JIRA")
    def test_authenticate_success(self, mock_jira_class, mock_jira_config):
        """Test successful authentication"""
        mock_jira_instance = Mock()
        mock_jira_instance.myself.return_value = {"emailAddress": "test@example.com"}
        mock_jira_class.return_value = mock_jira_instance

        plugin = JiraPlugin()
        assert plugin.authenticate(mock_jira_config) is True
        assert plugin.client is not None

    @patch("integrations.jira.jira_plugin.JIRA")
    def test_authenticate_failure(self, mock_jira_class, mock_jira_config):
        """Test authentication failure"""
        mock_jira_class.side_effect = Exception("Authentication failed")

        plugin = JiraPlugin()
        with pytest.raises(AuthenticationError):
            plugin.authenticate(mock_jira_config)

    @patch("integrations.jira.jira_plugin.JIRA")
    def test_create_work_item(
        self, mock_jira_class, mock_jira_config, mock_jira_client, sample_work_item
    ):
        """Test work item creation"""
        mock_jira_class.return_value = mock_jira_client

        plugin = JiraPlugin()
        plugin.authenticate(mock_jira_config)

        item_id = plugin.create_work_item(sample_work_item, mock_jira_config)

        assert item_id == "TEST-123"
        mock_jira_client.create_issue.assert_called_once()

    @patch("integrations.jira.jira_plugin.JIRA")
    def test_update_work_item(
        self, mock_jira_class, mock_jira_config, mock_jira_client
    ):
        """Test work item update"""
        mock_jira_class.return_value = mock_jira_client

        plugin = JiraPlugin()
        plugin.authenticate(mock_jira_config)

        updates = {"title": "Updated Title", "priority": WorkItemPriority.HIGH}

        result = plugin.update_work_item("TEST-123", updates, mock_jira_config)

        assert result is True
        mock_jira_client.issue.assert_called_once_with("TEST-123")

    @patch("integrations.jira.jira_plugin.JIRA")
    def test_get_work_item(self, mock_jira_class, mock_jira_config, mock_jira_client):
        """Test retrieving work item"""
        mock_jira_class.return_value = mock_jira_client

        plugin = JiraPlugin()
        plugin.authenticate(mock_jira_config)

        work_item = plugin.get_work_item("TEST-123", mock_jira_config)

        assert work_item.id == "TEST-123"
        assert work_item.title == "Test Issue"
        mock_jira_client.issue.assert_called_once_with("TEST-123")

    @patch("integrations.jira.jira_plugin.JIRA")
    def test_search_work_items(
        self, mock_jira_class, mock_jira_config, mock_jira_client
    ):
        """Test searching work items"""
        mock_jira_class.return_value = mock_jira_client

        plugin = JiraPlugin()
        plugin.authenticate(mock_jira_config)

        results = plugin.search_work_items("test query", mock_jira_config)

        assert len(results) > 0
        assert results[0].id == "TEST-123"
        mock_jira_client.search_issues.assert_called_once()

    @patch("integrations.jira.jira_plugin.JIRA")
    def test_link_to_commit(self, mock_jira_class, mock_jira_config, mock_jira_client):
        """Test linking work item to commit"""
        mock_jira_class.return_value = mock_jira_client

        plugin = JiraPlugin()
        plugin.authenticate(mock_jira_config)

        result = plugin.link_to_commit(
            "TEST-123",
            "abc123def456",
            "https://github.com/org/repo",
            mock_jira_config,
        )

        assert result is True
        mock_jira_client.add_comment.assert_called_once()

    @patch("integrations.jira.jira_plugin.JIRA")
    def test_link_to_pull_request(
        self, mock_jira_class, mock_jira_config, mock_jira_client
    ):
        """Test linking work item to pull request"""
        mock_jira_class.return_value = mock_jira_client

        plugin = JiraPlugin()
        plugin.authenticate(mock_jira_config)

        result = plugin.link_to_pull_request(
            "TEST-123", "https://github.com/org/repo/pull/42", mock_jira_config
        )

        assert result is True
        mock_jira_client.add_simple_link.assert_called_once()

    @patch("integrations.jira.jira_plugin.JIRA")
    def test_create_from_incident(
        self, mock_jira_class, mock_jira_config, mock_jira_client, sample_incident
    ):
        """Test creating work item from incident"""
        mock_jira_class.return_value = mock_jira_client

        plugin = JiraPlugin()
        plugin.authenticate(mock_jira_config)

        incident_id = plugin.create_from_incident(sample_incident, mock_jira_config)

        assert incident_id == "TEST-123"
        mock_jira_client.create_issue.assert_called()

        # Verify incident details in call
        call_args = mock_jira_client.create_issue.call_args
        assert "[AUTO]" in call_args[1]["fields"]["summary"]

    @patch("integrations.jira.jira_plugin.JIRA")
    def test_get_team_velocity(
        self, mock_jira_class, mock_jira_config, mock_jira_client
    ):
        """Test getting team velocity metrics"""
        mock_jira_class.return_value = mock_jira_client

        plugin = JiraPlugin()
        plugin.authenticate(mock_jira_config)

        velocity = plugin.get_team_velocity("Team Alpha", 30, mock_jira_config)

        assert "total_story_points" in velocity
        assert "avg_velocity" in velocity
        assert "issues_completed" in velocity
        mock_jira_client.search_issues.assert_called_once()

    @patch("integrations.jira.jira_plugin.JIRA")
    def test_health_check_healthy(
        self, mock_jira_class, mock_jira_config, mock_jira_client
    ):
        """Test health check when system is healthy"""
        mock_jira_class.return_value = mock_jira_client

        plugin = JiraPlugin()

        health = plugin.health_check(mock_jira_config)

        assert health["status"] == "healthy"
        assert health["plugin"] == "JIRA Integration"

    @patch("integrations.jira.jira_plugin.JIRA")
    def test_health_check_unhealthy(self, mock_jira_class, mock_jira_config):
        """Test health check when system is unhealthy"""
        mock_jira_class.side_effect = Exception("Connection failed")

        plugin = JiraPlugin()

        health = plugin.health_check(mock_jira_config)

        assert health["status"] == "unhealthy"
        assert "error" in health

    def test_priority_mapping(self):
        """Test priority mapping between standard and JIRA"""
        plugin = JiraPlugin()

        assert plugin._map_priority_to_jira(WorkItemPriority.CRITICAL) == "Highest"
        assert plugin._map_priority_to_jira(WorkItemPriority.HIGH) == "High"
        assert plugin._map_priority_to_jira(WorkItemPriority.MEDIUM) == "Medium"
        assert plugin._map_priority_to_jira(WorkItemPriority.LOW) == "Low"

        assert (
            plugin._map_jira_priority_to_standard("Highest")
            == WorkItemPriority.CRITICAL
        )
        assert plugin._map_jira_priority_to_standard("High") == WorkItemPriority.HIGH
        assert (
            plugin._map_jira_priority_to_standard("Medium") == WorkItemPriority.MEDIUM
        )
        assert plugin._map_jira_priority_to_standard("Low") == WorkItemPriority.LOW

    def test_status_mapping(self):
        """Test status mapping between standard and JIRA"""
        plugin = JiraPlugin()

        assert plugin._map_jira_status_to_standard("To Do") == WorkItemStatus.TODO
        assert (
            plugin._map_jira_status_to_standard("In Progress")
            == WorkItemStatus.IN_PROGRESS
        )
        assert (
            plugin._map_jira_status_to_standard("In Review") == WorkItemStatus.IN_REVIEW
        )
        assert plugin._map_jira_status_to_standard("Done") == WorkItemStatus.DONE
        assert (
            plugin._map_jira_status_to_standard("Cancelled")
            == WorkItemStatus.CANCELLED
        )
