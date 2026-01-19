"""
Unit tests for persistent artifact functionality in Azure DevOps.
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch, mock_open
from pathlib import Path
from datetime import datetime

# Add plugins directory to path
sys.path.insert(
    0,
    str(
        Path(__file__).parent.parent.parent
        / "plugins"
        / "databricks-devops-integrations"
    ),
)

from integrations.azure_devops.azure_devops_plugin import AzureDevOpsPlugin
from sdk.exceptions import IntegrationError


@pytest.mark.unit
class TestPersistentArtifacts:
    """Test suite for persistent artifact functionality."""

    @pytest.fixture
    def plugin(self):
        """Create ADO plugin instance."""
        plugin = AzureDevOpsPlugin()
        plugin.work_item_client = Mock()
        plugin.connection = Mock()
        return plugin

    @pytest.fixture
    def mock_config(self):
        """Mock plugin configuration."""
        from sdk.base_plugin import PluginConfig

        return PluginConfig(
            api_endpoint="https://dev.azure.com/test-org",
            api_key="test-pat",
            organization="test-org",
            project="test-project",
        )

    @pytest.fixture
    def sample_evidence_items(self, temp_dir):
        """Create sample evidence items."""
        from ai_sdlc.evidence import EvidenceItem, EvidenceCategory

        items = []

        # Create test files
        for i in range(3):
            file_path = Path(temp_dir) / f"evidence_{i}.txt"
            file_path.write_text(f"Evidence content {i}")

            item = EvidenceItem(
                path=str(file_path),
                category=EvidenceCategory.REPORT,
                stage="test_stage",
                filename=f"evidence_{i}.txt",
                size_bytes=file_path.stat().st_size,
                created_at=datetime.now(),
                metadata={},
            )
            items.append(item)

        return items

    @patch("requests.put")
    @patch("tarfile.open")
    @patch("tempfile.TemporaryDirectory")
    def test_create_artifact_package_success(
        self,
        mock_temp_dir,
        mock_tarfile,
        mock_requests_put,
        plugin,
        mock_config,
        sample_evidence_items,
        temp_dir,
    ):
        """Test successful artifact package creation."""
        # Mock temporary directory
        mock_temp_dir.return_value.__enter__.return_value = temp_dir

        # Mock successful upload response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "package-123"}
        mock_requests_put.return_value = mock_response

        # Execute
        result = plugin.create_artifact_package(
            work_item_id="12345",
            artifact_name="test-artifact",
            artifact_version="1.0.0",
            evidence_items=sample_evidence_items,
            config=mock_config,
        )

        # Verify
        assert result["package_id"] == "package-123"
        assert result["version"] == "1.0.0"
        assert result["files_count"] == 3
        assert "package_url" in result
        assert "artifact_link" in result

        # Verify work item was updated with artifact link
        plugin.work_item_client.update_work_item.assert_called_once()
        call_args = plugin.work_item_client.update_work_item.call_args
        document = call_args[1]["document"]

        # Check ArtifactLink was added
        assert any(
            op.path == "/relations/-" and op.value.get("rel") == "ArtifactLink"
            for op in document
        )

    @patch("requests.put")
    def test_create_artifact_package_version_conflict(
        self, mock_requests_put, plugin, mock_config, sample_evidence_items
    ):
        """Test artifact package creation with version conflict."""
        # Mock conflict response (409)
        mock_response = Mock()
        mock_response.status_code = 409
        mock_requests_put.return_value = mock_response

        # Execute and verify error
        with pytest.raises(IntegrationError, match="already exists"):
            plugin.create_artifact_package(
                work_item_id="12345",
                artifact_name="test-artifact",
                artifact_version="1.0.0",
                evidence_items=sample_evidence_items,
                config=mock_config,
            )

    @patch("requests.put")
    def test_create_artifact_package_upload_failure(
        self, mock_requests_put, plugin, mock_config, sample_evidence_items
    ):
        """Test artifact package creation with upload failure."""
        # Mock failed response (500)
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_requests_put.return_value = mock_response

        # Execute and verify error
        with pytest.raises(IntegrationError, match="Failed to upload artifact package"):
            plugin.create_artifact_package(
                work_item_id="12345",
                artifact_name="test-artifact",
                artifact_version="1.0.0",
                evidence_items=sample_evidence_items,
                config=mock_config,
            )

    def test_create_artifact_package_no_config(self, plugin, sample_evidence_items):
        """Test artifact package creation without configuration."""
        plugin.connection = None

        with pytest.raises(IntegrationError, match="Configuration required"):
            plugin.create_artifact_package(
                work_item_id="12345",
                artifact_name="test-artifact",
                artifact_version="1.0.0",
                evidence_items=sample_evidence_items,
            )

    def test_link_existing_artifact_success(self, plugin, mock_config):
        """Test linking existing artifact to work item."""
        result = plugin.link_existing_artifact(
            work_item_id="12345",
            artifact_url="https://dev.azure.com/test/_apis/packaging/feeds/test/packages/123",
            artifact_name="Test Artifact",
            comment="Test comment",
            config=mock_config,
        )

        assert result is True
        plugin.work_item_client.update_work_item.assert_called_once()

        # Verify ArtifactLink was added
        call_args = plugin.work_item_client.update_work_item.call_args
        document = call_args[1]["document"]
        assert len(document) == 1
        assert document[0].path == "/relations/-"
        assert document[0].value["rel"] == "ArtifactLink"
        assert (
            document[0].value["url"]
            == "https://dev.azure.com/test/_apis/packaging/feeds/test/packages/123"
        )
        assert document[0].value["attributes"]["name"] == "Test Artifact"
        assert document[0].value["attributes"]["comment"] == "Test comment"

    def test_link_existing_artifact_failure(self, plugin, mock_config):
        """Test linking existing artifact with failure."""
        plugin.work_item_client.update_work_item.side_effect = Exception(
            "Update failed"
        )

        with pytest.raises(IntegrationError, match="Failed to link artifact"):
            plugin.link_existing_artifact(
                work_item_id="12345",
                artifact_url="https://test-url",
                artifact_name="Test Artifact",
                config=mock_config,
            )

    def test_link_existing_artifact_no_config(self, plugin):
        """Test linking artifact without configuration."""
        plugin.work_item_client = None

        with pytest.raises(IntegrationError, match="Configuration required"):
            plugin.link_existing_artifact(
                work_item_id="12345",
                artifact_url="https://test-url",
                artifact_name="Test Artifact",
            )

    def test_get_work_item_artifacts_success(self, plugin, mock_config):
        """Test retrieving work item artifacts."""
        # Mock work item with artifact relations
        mock_work_item = Mock()
        mock_relation1 = Mock()
        mock_relation1.rel = "ArtifactLink"
        mock_relation1.url = "https://test-artifact-1"
        mock_relation1.attributes = {"name": "Artifact 1", "comment": "Comment 1"}

        mock_relation2 = Mock()
        mock_relation2.rel = "ArtifactLink"
        mock_relation2.url = "https://test-artifact-2"
        mock_relation2.attributes = {"name": "Artifact 2", "comment": "Comment 2"}

        mock_relation3 = Mock()
        mock_relation3.rel = "Hyperlink"  # Not an artifact
        mock_relation3.url = "https://test-link"

        mock_work_item.relations = [mock_relation1, mock_relation2, mock_relation3]
        plugin.work_item_client.get_work_item.return_value = mock_work_item

        # Execute
        artifacts = plugin.get_work_item_artifacts(
            work_item_id="12345", config=mock_config
        )

        # Verify
        assert len(artifacts) == 2  # Only artifact links, not hyperlink
        assert artifacts[0]["url"] == "https://test-artifact-1"
        assert artifacts[0]["name"] == "Artifact 1"
        assert artifacts[0]["comment"] == "Comment 1"
        assert artifacts[1]["url"] == "https://test-artifact-2"

        plugin.work_item_client.get_work_item.assert_called_once_with(
            12345, expand="Relations"
        )

    def test_get_work_item_artifacts_no_relations(self, plugin, mock_config):
        """Test retrieving artifacts for work item with no relations."""
        # Mock work item with no relations
        mock_work_item = Mock()
        mock_work_item.relations = None
        plugin.work_item_client.get_work_item.return_value = mock_work_item

        # Execute
        artifacts = plugin.get_work_item_artifacts(
            work_item_id="12345", config=mock_config
        )

        # Verify
        assert len(artifacts) == 0

    def test_get_work_item_artifacts_failure(self, plugin, mock_config):
        """Test retrieving artifacts with failure."""
        plugin.work_item_client.get_work_item.side_effect = Exception("Get failed")

        with pytest.raises(IntegrationError, match="Failed to get work item artifacts"):
            plugin.get_work_item_artifacts(work_item_id="12345", config=mock_config)

    def test_get_work_item_artifacts_no_config(self, plugin):
        """Test retrieving artifacts without configuration."""
        plugin.work_item_client = None

        with pytest.raises(IntegrationError, match="Configuration required"):
            plugin.get_work_item_artifacts(work_item_id="12345")


@pytest.mark.unit
class TestEvidenceCollectorPersistentArtifacts:
    """Test evidence collector agent with persistent artifacts."""

    @pytest.fixture
    def evidence_collector_agent(self, work_item_id, temp_dir):
        """Create evidence collector agent."""
        from ai_sdlc.agents.evidence_collector_agent import EvidenceCollectorAgent

        return EvidenceCollectorAgent(
            work_item_id=work_item_id, evidence_base_path=temp_dir
        )

    @pytest.fixture
    def sample_stage_results(self, temp_dir):
        """Create sample stage results with evidence."""
        # Create test evidence files
        planning_file = Path(temp_dir) / "plan.md"
        planning_file.write_text("# Implementation Plan")

        code_file = Path(temp_dir) / "service.py"
        code_file.write_text("def process(): pass")

        return {
            "planning": {
                "success": True,
                "evidence_paths": [str(planning_file)],
            },
            "code_generation": {
                "success": True,
                "evidence_paths": [str(code_file)],
            },
        }

    def test_execute_without_persistent_artifact(
        self, evidence_collector_agent, sample_stage_results
    ):
        """Test execute without creating persistent artifact."""
        input_data = {
            "previous_stages": sample_stage_results,
            "create_persistent_artifact": False,
        }

        result = evidence_collector_agent.execute(input_data)

        assert result["success"] is True
        assert "artifact_package" not in result["data"]
        assert result["data"]["total_artifacts"] == 2

    @patch.object(
        EvidenceCollectorAgent,
        "_create_persistent_artifact",
        return_value={"package_id": "123"},
    )
    def test_execute_with_persistent_artifact(
        self,
        mock_create_artifact,
        evidence_collector_agent,
        sample_stage_results,
        mock_ado_plugin,
        mock_config,
    ):
        """Test execute with persistent artifact creation."""
        input_data = {
            "previous_stages": sample_stage_results,
            "create_persistent_artifact": True,
            "artifact_version": "1.0.0",
            "ado_plugin": mock_ado_plugin,
            "ado_config": mock_config,
        }

        result = evidence_collector_agent.execute(input_data)

        assert result["success"] is True
        assert "artifact_package" in result["data"]
        assert result["data"]["artifact_package"]["package_id"] == "123"
        mock_create_artifact.assert_called_once()

    def test_create_persistent_artifact_success(
        self,
        evidence_collector_agent,
        sample_stage_results,
        mock_ado_plugin,
        mock_config,
    ):
        """Test _create_persistent_artifact method."""
        from ai_sdlc.agents.evidence_collector_agent import EvidenceCollectorAgent

        # Prepare evidence
        all_evidence = [
            {
                "stage": "planning",
                "path": "/test/plan.md",
                "filename": "plan.md",
                "type": "plan",
                "exists": True,
            }
        ]

        input_data = {
            "ado_plugin": mock_ado_plugin,
            "ado_config": mock_config,
            "artifact_version": "1.0.0",
        }

        # Mock ADO plugin response
        mock_ado_plugin.create_artifact_package.return_value = {
            "package_id": "test-123",
            "package_url": "https://test-url",
            "version": "1.0.0",
            "files_count": 1,
        }

        # Execute
        result = evidence_collector_agent._create_persistent_artifact(
            all_evidence, sample_stage_results, input_data
        )

        # Verify
        assert result is not None
        assert result["package_id"] == "test-123"
        assert result["version"] == "1.0.0"

    def test_create_persistent_artifact_no_config(
        self, evidence_collector_agent, sample_stage_results
    ):
        """Test _create_persistent_artifact without ADO config."""
        all_evidence = [{"stage": "planning", "path": "/test/plan.md"}]
        input_data = {}  # No ado_plugin or ado_config

        result = evidence_collector_agent._create_persistent_artifact(
            all_evidence, sample_stage_results, input_data
        )

        # Should return None without failing
        assert result is None

    def test_create_persistent_artifact_no_valid_items(
        self,
        evidence_collector_agent,
        sample_stage_results,
        mock_ado_plugin,
        mock_config,
    ):
        """Test _create_persistent_artifact with no valid evidence items."""
        # Evidence that doesn't exist
        all_evidence = [
            {"stage": "planning", "path": "/nonexistent/file.txt", "exists": False}
        ]

        input_data = {
            "ado_plugin": mock_ado_plugin,
            "ado_config": mock_config,
            "artifact_version": "1.0.0",
        }

        result = evidence_collector_agent._create_persistent_artifact(
            all_evidence, sample_stage_results, input_data
        )

        # Should return None when no valid items
        assert result is None

    def test_create_persistent_artifact_handles_exception(
        self,
        evidence_collector_agent,
        sample_stage_results,
        mock_ado_plugin,
        mock_config,
    ):
        """Test _create_persistent_artifact handles exceptions gracefully."""
        all_evidence = [
            {
                "stage": "planning",
                "path": "/test/plan.md",
                "type": "plan",
                "exists": True,
            }
        ]

        input_data = {
            "ado_plugin": mock_ado_plugin,
            "ado_config": mock_config,
            "artifact_version": "1.0.0",
        }

        # Mock exception in ADO plugin
        mock_ado_plugin.create_artifact_package.side_effect = Exception("Upload failed")

        # Should not raise exception, just return None
        result = evidence_collector_agent._create_persistent_artifact(
            all_evidence, sample_stage_results, input_data
        )

        assert result is None  # Should return None on error


# Fix import for the mock reference
from ai_sdlc.agents.evidence_collector_agent import EvidenceCollectorAgent
