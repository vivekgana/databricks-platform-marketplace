"""
Unit tests for ADO Adapter.

Tests the Azure DevOps plugin adapter functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from ai_sdlc.plugins.adapters.ado_adapter import ADOAdapter
from ai_sdlc.plugins.models import WorkItem, WorkItemUpdate, Comment


class TestADOAdapter:
    """Test ADO adapter functionality."""

    @pytest.fixture
    def mock_ado_plugin(self):
        """Create a mock Azure DevOps plugin."""
        mock = Mock()
        mock.get_work_item = Mock()
        mock.create_work_item = Mock()
        mock.update_work_item = Mock()
        mock.add_comment = Mock()
        return mock

    @pytest.fixture
    def ado_adapter(self, mock_ado_plugin):
        """Create ADO adapter with mocked dependencies."""
        adapter = ADOAdapter()
        adapter.ado_plugin = mock_ado_plugin
        adapter.organization = "test-org"
        adapter.project = "TestProject"
        adapter.initialized = True
        return adapter

    def test_get_name(self):
        """Test plugin name."""
        adapter = ADOAdapter()
        assert adapter.get_name() == "ado"

    def test_validate_config_valid(self):
        """Test config validation with valid config."""
        adapter = ADOAdapter()
        config = {
            "organization": "test-org",
            "project": "TestProject",
            "pat": "test-token",
        }
        assert adapter.validate_config(config) is True

    def test_validate_config_missing_fields(self):
        """Test config validation with missing fields."""
        adapter = ADOAdapter()
        config = {"organization": "test-org"}  # Missing project and pat
        assert adapter.validate_config(config) is False

    @patch("ai_sdlc.plugins.adapters.ado_adapter.AzureDevOpsPlugin")  # Mock the import
    def test_initialize_success(self, mock_plugin_class):
        """Test successful initialization."""
        mock_plugin_instance = Mock()
        mock_plugin_class.return_value = mock_plugin_instance

        adapter = ADOAdapter()
        config = {
            "organization": "test-org",
            "project": "TestProject",
            "pat": "test-token",
        }

        result = adapter.initialize(config)

        assert result is True
        assert adapter.initialized is True
        assert adapter.organization == "test-org"
        assert adapter.project == "TestProject"
        mock_plugin_class.assert_called_once_with(
            organization="test-org",
            project="TestProject",
            personal_access_token="test-token",
        )

    def test_get_work_item(self, ado_adapter, mock_ado_plugin):
        """Test getting work item."""
        # Mock ADO response
        mock_ado_plugin.get_work_item.return_value = {
            "id": 12345,
            "fields": {
                "System.Title": "Test Work Item",
                "System.Description": "Test Description",
                "System.State": "Active",
                "System.AssignedTo": {"displayName": "John Doe"},
                "System.CreatedDate": "2026-01-18T00:00:00Z",
                "System.ChangedDate": "2026-01-18T12:00:00Z",
                "System.WorkItemType": "Task",
                "System.Tags": "tag1; tag2",
            },
            "_links": {
                "html": {
                    "href": "https://dev.azure.com/test-org/TestProject/_workitems/edit/12345"
                }
            },
        }

        work_item = ado_adapter.get_work_item("12345")

        assert isinstance(work_item, WorkItem)
        assert work_item.id == "12345"
        assert work_item.title == "Test Work Item"
        assert work_item.description == "Test Description"
        assert work_item.state == "Active"
        assert work_item.assigned_to == "John Doe"
        assert work_item.item_type == "Task"
        assert work_item.tags == ["tag1", "tag2"]
        assert work_item.tool_name == "ado"

    def test_create_work_item(self, ado_adapter, mock_ado_plugin):
        """Test creating work item."""
        # Mock ADO response for create and get
        mock_ado_plugin.create_work_item.return_value = {"id": 12346}
        mock_ado_plugin.get_work_item.return_value = {
            "id": 12346,
            "fields": {
                "System.Title": "New Work Item",
                "System.Description": "New Description",
                "System.State": "New",
                "System.WorkItemType": "Task",
            },
            "_links": {
                "html": {
                    "href": "https://dev.azure.com/test-org/TestProject/_workitems/edit/12346"
                }
            },
        }

        work_item = ado_adapter.create_work_item(
            title="New Work Item",
            description="New Description",
            item_type="Task",
            assigned_to="Jane Doe",
        )

        assert isinstance(work_item, WorkItem)
        assert work_item.title == "New Work Item"
        assert work_item.description == "New Description"
        mock_ado_plugin.create_work_item.assert_called_once()

    def test_update_work_item(self, ado_adapter, mock_ado_plugin):
        """Test updating work item."""
        # Mock ADO response
        mock_ado_plugin.get_work_item.return_value = {
            "id": 12345,
            "fields": {
                "System.Title": "Updated Title",
                "System.Description": "Test Description",
                "System.State": "Active",
                "System.WorkItemType": "Task",
            },
            "_links": {
                "html": {
                    "href": "https://dev.azure.com/test-org/TestProject/_workitems/edit/12345"
                }
            },
        }

        update = WorkItemUpdate(title="Updated Title", state="Active")
        work_item = ado_adapter.update_work_item("12345", update)

        assert work_item.title == "Updated Title"
        mock_ado_plugin.update_work_item.assert_called_once()

    def test_add_comment(self, ado_adapter, mock_ado_plugin):
        """Test adding comment."""
        # Mock ADO response
        mock_ado_plugin.add_comment.return_value = {
            "id": "comment-123",
            "createdBy": {"displayName": "Test User"},
            "createdDate": "2026-01-18T12:00:00Z",
        }

        comment = ado_adapter.add_comment("12345", "Test comment")

        assert isinstance(comment, Comment)
        assert comment.content == "Test comment"
        assert comment.author == "Test User"
        mock_ado_plugin.add_comment.assert_called_once_with("12345", "Test comment")

    def test_search_work_items(self, ado_adapter, mock_ado_plugin):
        """Test searching work items."""
        # Mock ADO response
        mock_ado_plugin.query_work_items.return_value = [
            {"id": 12345},
            {"id": 12346},
        ]
        mock_ado_plugin.get_work_item.side_effect = [
            {
                "id": 12345,
                "fields": {
                    "System.Title": "Item 1",
                    "System.State": "Active",
                    "System.WorkItemType": "Task",
                },
                "_links": {
                    "html": {
                        "href": "https://dev.azure.com/test-org/TestProject/_workitems/edit/12345"
                    }
                },
            },
            {
                "id": 12346,
                "fields": {
                    "System.Title": "Item 2",
                    "System.State": "Active",
                    "System.WorkItemType": "Task",
                },
                "_links": {
                    "html": {
                        "href": "https://dev.azure.com/test-org/TestProject/_workitems/edit/12346"
                    }
                },
            },
        ]

        results = ado_adapter.search_work_items("test query")

        assert len(results) == 2
        assert all(isinstance(item, WorkItem) for item in results)
        assert results[0].title == "Item 1"
        assert results[1].title == "Item 2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
