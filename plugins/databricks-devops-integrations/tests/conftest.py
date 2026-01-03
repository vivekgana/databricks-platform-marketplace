"""
Pytest configuration and fixtures for DevOps integration plugin tests
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from sdk import (
    PluginConfig,
    WorkItem,
    WorkItemStatus,
    WorkItemPriority,
)


@pytest.fixture
def mock_jira_config():
    """Mock JIRA configuration"""
    return PluginConfig(
        plugin_id="test-jira",
        api_endpoint="https://test.atlassian.net",
        api_key="test-api-key",
        organization="test@example.com",
        project="TEST",
        custom_settings={},
    )


@pytest.fixture
def mock_ado_config():
    """Mock Azure DevOps configuration"""
    return PluginConfig(
        plugin_id="test-ado",
        api_endpoint="https://dev.azure.com/testorg",
        api_key="test-pat-token",
        organization="testorg",
        project="TestProject",
        custom_settings={},
    )


@pytest.fixture
def sample_work_item():
    """Sample work item for testing"""
    return WorkItem(
        id="",
        title="Test Work Item",
        description="This is a test work item",
        status=WorkItemStatus.TODO,
        assignee="test.user@example.com",
        priority=WorkItemPriority.MEDIUM,
        labels=["test", "sample"],
        story_points=5.0,
    )


@pytest.fixture
def sample_incident():
    """Sample incident for testing"""
    return {
        "title": "Production API Gateway Timeout",
        "severity": "high",
        "timestamp": datetime.utcnow().isoformat(),
        "logs": "Error: Connection timeout after 30s\nStack trace: ...",
        "components": ["api-gateway", "database"],
    }


@pytest.fixture
def sample_opportunity():
    """Sample investment opportunity for testing"""
    return {
        "title": "Series A Investment - TechCo Inc",
        "description": "Cloud-based SaaS platform for enterprise",
        "amount": 10000000,
        "stage": "due_diligence",
        "sector": "Enterprise Software",
        "risk_level": "medium",
    }


@pytest.fixture
def mock_jira_client():
    """Mock JIRA client"""
    client = MagicMock()

    # Mock issue
    mock_issue = Mock()
    mock_issue.key = "TEST-123"
    mock_issue.id = "12345"
    mock_issue.fields.summary = "Test Issue"
    mock_issue.fields.description = "Test Description"
    mock_issue.fields.status.name = "To Do"
    mock_issue.fields.priority.name = "Medium"
    mock_issue.fields.assignee = None
    mock_issue.fields.labels = ["test"]
    mock_issue.fields.created = "2026-01-02T00:00:00.000Z"
    mock_issue.fields.updated = "2026-01-02T00:00:00.000Z"
    mock_issue.fields.customfield_10016 = 5.0  # Story points

    client.create_issue.return_value = mock_issue
    client.issue.return_value = mock_issue
    client.search_issues.return_value = [mock_issue]
    client.myself.return_value = {"emailAddress": "test@example.com"}
    client.server_url = "https://test.atlassian.net"

    return client


@pytest.fixture
def mock_ado_client():
    """Mock Azure DevOps work item tracking client"""
    client = MagicMock()

    # Mock work item
    mock_work_item = Mock()
    mock_work_item.id = 123
    mock_work_item.fields = {
        "System.Id": 123,
        "System.Title": "Test Work Item",
        "System.Description": "Test Description",
        "System.State": "New",
        "Microsoft.VSTS.Common.Priority": 3,
        "System.Tags": "test; sample",
        "System.CreatedDate": "2026-01-02T00:00:00.000Z",
        "System.ChangedDate": "2026-01-02T00:00:00.000Z",
        "Microsoft.VSTS.Scheduling.StoryPoints": 5.0,
    }
    mock_work_item.url = "https://dev.azure.com/testorg/TestProject/_workitems/edit/123"

    # Mock query result
    mock_query_result = Mock()
    mock_query_result.work_items = [Mock(id=123)]

    client.create_work_item.return_value = mock_work_item
    client.get_work_item.return_value = mock_work_item
    client.get_work_items.return_value = [mock_work_item]
    client.query_by_wiql.return_value = mock_query_result

    return client


@pytest.fixture
def mock_connection(mock_ado_client):
    """Mock Azure DevOps connection"""
    connection = MagicMock()
    connection.clients.get_work_item_tracking_client.return_value = mock_ado_client
    connection.clients.get_core_client.return_value.get_project.return_value = Mock(
        name="TestProject"
    )
    return connection


@pytest.fixture
def enable_integration_tests(request):
    """Fixture to conditionally enable integration tests"""
    return request.config.getoption("--run-integration", default=False)


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests (requires real credentials)",
    )


def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "unit: mark test as unit test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(
            reason="need --run-integration option to run"
        )
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
