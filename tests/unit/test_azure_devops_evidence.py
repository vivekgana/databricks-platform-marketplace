"""
Unit tests for Azure DevOps plugin evidence methods.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from pathlib import Path
from plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import (
    AzureDevOpsPlugin,
)
from plugins.databricks_devops_integrations.sdk.exceptions import IntegrationError


@pytest.mark.unit
class TestAzureDevOpsEvidenceMethods:
    """Test suite for ADO evidence management methods."""

    @pytest.fixture
    def plugin(self):
        """Create ADO plugin instance."""
        plugin = AzureDevOpsPlugin()
        plugin.work_item_client = Mock()
        return plugin

    @pytest.fixture
    def mock_config(self):
        """Mock plugin configuration."""
        from plugins.databricks_devops_integrations.sdk.base_plugin import (
            PluginConfig,
        )

        return PluginConfig(
            api_endpoint="https://dev.azure.com/test",
            api_key="test-pat",
            organization="test-org",
            project="test-project",
        )

    def test_add_comment_success(self, plugin, mock_config):
        """Test adding plain text comment."""
        work_item_id = "12345"
        comment = "Test comment"

        result = plugin.add_comment(work_item_id, comment, config=mock_config)

        assert result is True
        plugin.work_item_client.update_work_item.assert_called_once()

    def test_add_comment_no_client(self, mock_config):
        """Test adding comment without authenticated client."""
        plugin = AzureDevOpsPlugin()
        plugin.work_item_client = None

        # Should raise error without config
        with pytest.raises(IntegrationError, match="Configuration required"):
            plugin.add_comment("12345", "comment")

    def test_add_rich_comment_success(self, plugin, mock_config):
        """Test adding rich HTML comment."""
        work_item_id = "12345"
        html_content = "<h1>Test</h1><p>Rich content</p>"

        result = plugin.add_rich_comment(
            work_item_id, html_content, config=mock_config
        )

        assert result is True
        plugin.work_item_client.update_work_item.assert_called_once()

        # Verify HTML was passed to System.History
        call_args = plugin.work_item_client.update_work_item.call_args
        document = call_args[1]["document"]
        assert any(
            op.path == "/fields/System.History" and html_content in str(op.value)
            for op in document
        )

    def test_add_rich_comment_with_plain_text_fallback(
        self, plugin, mock_config
    ):
        """Test rich comment with plain text fallback (not used in ADO)."""
        work_item_id = "12345"
        html_content = "<h1>Test</h1>"
        plain_text = "Test"

        result = plugin.add_rich_comment(
            work_item_id, html_content, plain_text, config=mock_config
        )

        assert result is True

    @patch("builtins.open", new_callable=mock_open, read_data=b"file content")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.stat")
    def test_upload_attachment_success(
        self, mock_stat, mock_exists, mock_file, plugin, mock_config
    ):
        """Test uploading attachment to work item."""
        work_item_id = "12345"
        file_path = "/path/to/file.txt"

        # Mock attachment creation
        mock_attachment = Mock()
        mock_attachment.url = "https://attachment-url"
        plugin.work_item_client.create_attachment = MagicMock(
            return_value=mock_attachment
        )

        result_url = plugin.upload_attachment(
            work_item_id, file_path, comment="Test file", config=mock_config
        )

        assert result_url == "https://attachment-url"
        plugin.work_item_client.create_attachment.assert_called_once()
        plugin.work_item_client.update_work_item.assert_called_once()

    def test_upload_attachment_file_not_found(self, plugin, mock_config):
        """Test uploading non-existent file."""
        work_item_id = "12345"
        file_path = "/nonexistent/file.txt"

        with pytest.raises(IntegrationError, match="File not found"):
            plugin.upload_attachment(work_item_id, file_path, config=mock_config)

    @patch("builtins.open", new_callable=mock_open, read_data=b"png data")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.stat")
    @patch("mimetypes.guess_type", return_value=("image/png", None))
    def test_upload_attachment_mime_type_detection(
        self, mock_mime, mock_stat, mock_exists, mock_file, plugin, mock_config
    ):
        """Test MIME type detection for attachments."""
        work_item_id = "12345"
        file_path = "/path/to/image.png"

        mock_attachment = Mock()
        mock_attachment.url = "https://attachment-url"
        plugin.work_item_client.create_attachment = MagicMock(
            return_value=mock_attachment
        )

        plugin.upload_attachment(work_item_id, file_path, config=mock_config)

        # Verify MIME type was detected
        create_call = plugin.work_item_client.create_attachment.call_args
        assert create_call[1]["upload_type"] == "image/png"

    @patch(
        "ai_sdlc.evidence.EvidenceFormatter.format_stage_comment",
        return_value="<h1>Formatted Comment</h1>",
    )
    def test_update_work_item_with_evidence_success(
        self, mock_format, plugin, mock_config
    ):
        """Test updating work item with evidence summary."""
        work_item_id = "12345"
        evidence_summary = {
            "evidence_items": [],
            "metrics": {"coverage": 85.5},
            "duration_seconds": 12.5,
        }

        # Mock add_rich_comment
        plugin.add_rich_comment = MagicMock(return_value=True)

        result = plugin.update_work_item_with_evidence(
            work_item_id=work_item_id,
            evidence_summary=evidence_summary,
            stage="unit_testing",
            status="passed",
            config=mock_config,
        )

        assert result is True
        plugin.add_rich_comment.assert_called_once()
        plugin.work_item_client.update_work_item.assert_called_once()

        # Verify custom fields were updated
        call_args = plugin.work_item_client.update_work_item.call_args
        document = call_args[1]["document"]

        field_paths = [op.path for op in document]
        assert "/fields/Custom.LastWorkflowStage" in field_paths
        assert "/fields/Custom.LastWorkflowStatus" in field_paths
        assert "/fields/Custom.LastWorkflowUpdate" in field_paths

    def test_update_work_item_with_evidence_handles_errors(
        self, plugin, mock_config
    ):
        """Test that evidence update errors don't fail workflow."""
        work_item_id = "12345"
        evidence_summary = {
            "evidence_items": [],
            "metrics": {},
            "duration_seconds": 0,
        }

        # Mock error in add_rich_comment
        plugin.add_rich_comment = MagicMock(
            side_effect=Exception("Comment failed")
        )

        # Should return False but not raise
        result = plugin.update_work_item_with_evidence(
            work_item_id=work_item_id,
            evidence_summary=evidence_summary,
            stage="unit_testing",
            status="passed",
            config=mock_config,
        )

        assert result is False

    @patch("builtins.open", new_callable=mock_open, read_data=b"file content")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.stat")
    def test_upload_evidence_package_success(
        self, mock_stat, mock_exists, mock_file, plugin, mock_config, temp_dir
    ):
        """Test uploading evidence package."""
        from ai_sdlc.evidence import EvidenceItem, EvidenceCategory
        from datetime import datetime

        work_item_id = "12345"

        # Create evidence items
        evidence_items = [
            EvidenceItem(
                path=f"{temp_dir}/screenshot1.png",
                category=EvidenceCategory.SCREENSHOT,
                stage="qa_testing",
                filename="screenshot1.png",
                size_bytes=1000,
                created_at=datetime.now(),
                metadata={},
            ),
            EvidenceItem(
                path=f"{temp_dir}/screenshot2.png",
                category=EvidenceCategory.SCREENSHOT,
                stage="qa_testing",
                filename="screenshot2.png",
                size_bytes=2000,
                created_at=datetime.now(),
                metadata={},
            ),
        ]

        # Mock upload_attachment
        plugin.upload_attachment = MagicMock(
            return_value="https://attachment-url"
        )

        result = plugin.upload_evidence_package(
            work_item_id=work_item_id,
            evidence_items=evidence_items,
            max_attachments=3,
            config=mock_config,
        )

        assert result["uploaded_count"] == 2
        assert len(result["uploaded_urls"]) == 2
        assert result["skipped_count"] == 0

    def test_upload_evidence_package_prioritizes_screenshots(
        self, plugin, mock_config, temp_dir
    ):
        """Test that screenshots are prioritized in evidence package."""
        from ai_sdlc.evidence import EvidenceItem, EvidenceCategory
        from datetime import datetime

        work_item_id = "12345"

        # Create mixed evidence items
        evidence_items = [
            EvidenceItem(
                path=f"{temp_dir}/code.py",
                category=EvidenceCategory.CODE,
                stage="code_generation",
                filename="code.py",
                size_bytes=1000,
                created_at=datetime.now(),
                metadata={},
            ),
            EvidenceItem(
                path=f"{temp_dir}/screenshot.png",
                category=EvidenceCategory.SCREENSHOT,
                stage="qa_testing",
                filename="screenshot.png",
                size_bytes=2000,
                created_at=datetime.now(),
                metadata={},
            ),
        ]

        # Mock upload_attachment
        uploaded_items = []

        def track_upload(work_item_id, file_path, comment, config):
            uploaded_items.append(file_path)
            return "https://url"

        plugin.upload_attachment = MagicMock(side_effect=track_upload)

        plugin.upload_evidence_package(
            work_item_id=work_item_id,
            evidence_items=evidence_items,
            max_attachments=1,  # Only 1 allowed
            config=mock_config,
        )

        # Screenshot should be uploaded (prioritized)
        assert len(uploaded_items) == 1
        assert "screenshot.png" in uploaded_items[0]

    def test_upload_evidence_package_handles_upload_failures(
        self, plugin, mock_config, temp_dir
    ):
        """Test that evidence package handles individual upload failures."""
        from ai_sdlc.evidence import EvidenceItem, EvidenceCategory
        from datetime import datetime

        work_item_id = "12345"

        evidence_items = [
            EvidenceItem(
                path=f"{temp_dir}/screenshot1.png",
                category=EvidenceCategory.SCREENSHOT,
                stage="qa_testing",
                filename="screenshot1.png",
                size_bytes=1000,
                created_at=datetime.now(),
                metadata={},
            ),
            EvidenceItem(
                path=f"{temp_dir}/screenshot2.png",
                category=EvidenceCategory.SCREENSHOT,
                stage="qa_testing",
                filename="screenshot2.png",
                size_bytes=2000,
                created_at=datetime.now(),
                metadata={},
            ),
        ]

        # Mock upload_attachment to fail on second item
        def upload_with_failure(work_item_id, file_path, comment, config):
            if "screenshot2" in file_path:
                raise Exception("Upload failed")
            return "https://url"

        plugin.upload_attachment = MagicMock(side_effect=upload_with_failure)

        result = plugin.upload_evidence_package(
            work_item_id=work_item_id,
            evidence_items=evidence_items,
            max_attachments=2,
            config=mock_config,
        )

        # Should still succeed with 1 upload
        assert result["uploaded_count"] == 1
        assert len(result["uploaded_urls"]) == 1
