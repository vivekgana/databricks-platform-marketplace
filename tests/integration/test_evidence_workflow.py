"""
Integration tests for evidence collection workflow.

These tests verify the complete evidence management flow from
collection through storage to ADO integration.
"""

import pytest
from pathlib import Path
from ai_sdlc.evidence import (
    EvidenceCollector,
    EvidenceCategory,
    LocalFileEvidenceStorage,
    EvidenceFormatter,
    ADOCommentFormat,
)


@pytest.mark.integration
class TestEvidenceWorkflow:
    """Integration tests for complete evidence workflow."""

    @pytest.fixture
    def evidence_workflow(self, work_item_id, temp_dir):
        """Set up complete evidence workflow."""
        # Create collector
        collector = EvidenceCollector(work_item_id, temp_dir)

        # Create storage (using local for testing)
        storage_path = Path(temp_dir) / "storage"
        storage = LocalFileEvidenceStorage(str(storage_path))

        # Create formatter
        formatter = EvidenceFormatter(work_item_id)

        return {
            "collector": collector,
            "storage": storage,
            "formatter": formatter,
            "work_item_id": work_item_id,
            "temp_dir": temp_dir,
        }

    def test_complete_evidence_collection_flow(self, evidence_workflow):
        """Test complete evidence collection, storage, and formatting."""
        collector = evidence_workflow["collector"]
        storage = evidence_workflow["storage"]
        formatter = evidence_workflow["formatter"]
        temp_dir = evidence_workflow["temp_dir"]

        # Step 1: Create evidence files
        planning_file = Path(temp_dir) / "plan.md"
        planning_file.write_text("# Implementation Plan\n\nDetails here...")

        code_file = Path(temp_dir) / "service.py"
        code_file.write_text("def process(): pass")

        test_file = Path(temp_dir) / "test_service.py"
        test_file.write_text("def test_process(): assert True")

        report_file = Path(temp_dir) / "coverage.json"
        report_file.write_text('{"coverage": 85.5}')

        # Step 2: Collect evidence
        collector.add_evidence(
            str(planning_file),
            EvidenceCategory.PLAN,
            "planning",
            "Implementation plan",
        )

        collector.add_evidence(
            str(code_file),
            EvidenceCategory.CODE,
            "code_generation",
            "Generated service code",
        )

        collector.add_evidence(
            str(test_file),
            EvidenceCategory.TEST,
            "unit_testing",
            "Unit tests",
        )

        collector.add_report(
            str(report_file), "unit_testing", "Coverage report"
        )

        # Verify collection
        assert len(collector.get_all_evidence()) == 4
        assert len(collector.get_evidence_by_stage("unit_testing")) == 2

        # Step 3: Upload to storage
        uploaded_paths = []
        for item in collector.get_all_evidence():
            remote_path = f"{item.stage}/{item.filename}"
            url = storage.upload_file(
                local_path=item.path,
                remote_path=remote_path,
                metadata={
                    "work_item_id": evidence_workflow["work_item_id"],
                    "stage": item.stage,
                    "category": item.category.value,
                },
            )
            uploaded_paths.append(url)

        # Verify uploads
        assert len(uploaded_paths) == 4

        # Verify files in storage
        planning_files = storage.list_files(prefix="planning/")
        assert len(planning_files) > 0

        # Step 4: Format for ADO
        stage_comment = formatter.format_stage_comment(
            stage="unit_testing",
            status="passed",
            duration_seconds=12.5,
            evidence_items=collector.get_evidence_by_stage("unit_testing"),
            metrics={"coverage": 85.5, "tests_passed": 10},
            format_type=ADOCommentFormat.MARKDOWN,
        )

        # Verify formatting
        assert "## ✅ Stage: Unit Testing" in stage_comment
        assert "**Status:** PASSED" in stage_comment
        assert "coverage" in stage_comment.lower()
        assert "85.5" in stage_comment

        # Step 5: Generate workflow summary
        stage_results = {
            "planning": {"status": "passed", "duration_seconds": 10.0},
            "code_generation": {"status": "passed", "duration_seconds": 30.0},
            "unit_testing": {"status": "passed", "duration_seconds": 12.5},
        }

        workflow_summary = formatter.format_workflow_summary(
            collector=collector,
            stage_results=stage_results,
            format_type=ADOCommentFormat.MARKDOWN,
        )

        # Verify summary
        assert "AI-SDLC Workflow Complete" in workflow_summary
        assert evidence_workflow["work_item_id"] in workflow_summary
        assert "planning" in workflow_summary.lower()
        assert "code_generation" in workflow_summary.lower()

    def test_evidence_retrieval_after_upload(self, evidence_workflow):
        """Test retrieving evidence after upload to storage."""
        collector = evidence_workflow["collector"]
        storage = evidence_workflow["storage"]
        temp_dir = evidence_workflow["temp_dir"]

        # Create and collect evidence
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Test content")

        collector.add_evidence(
            str(test_file), EvidenceCategory.REPORT, "test_stage"
        )

        # Upload to storage
        item = collector.get_all_evidence()[0]
        remote_path = f"{item.stage}/{item.filename}"
        storage.upload_file(item.path, remote_path)

        # Download from storage
        download_path = Path(temp_dir) / "downloaded_test.txt"
        success = storage.download_file(remote_path, str(download_path))

        assert success is True
        assert download_path.exists()

        # Verify content matches
        with open(download_path, "r") as f:
            downloaded_content = f.read()
        assert downloaded_content == "Test content"

    def test_evidence_export_and_summary(self, evidence_workflow):
        """Test evidence export and summary generation."""
        collector = evidence_workflow["collector"]
        temp_dir = evidence_workflow["temp_dir"]

        # Add various evidence items
        for i in range(5):
            file_path = Path(temp_dir) / f"file_{i}.txt"
            file_path.write_text(f"Content {i}")

            category = (
                EvidenceCategory.CODE
                if i % 2 == 0
                else EvidenceCategory.TEST
            )
            stage = (
                "code_generation" if i < 3 else "unit_testing"
            )

            collector.add_evidence(str(file_path), category, stage)

        # Export metadata
        metadata = collector.export_metadata()

        # Verify export structure
        assert metadata["work_item_id"] == evidence_workflow["work_item_id"]
        assert "collected_at" in metadata
        assert "summary" in metadata
        assert "items" in metadata
        assert len(metadata["items"]) == 5

        # Verify summary
        summary = metadata["summary"]
        assert summary["total_items"] == 5
        assert "by_category" in summary
        assert "by_stage" in summary
        assert summary["by_stage"]["code_generation"] == 3
        assert summary["by_stage"]["unit_testing"] == 2

    def test_multi_stage_evidence_formatting(self, evidence_workflow):
        """Test formatting evidence across multiple stages."""
        collector = evidence_workflow["collector"]
        formatter = evidence_workflow["formatter"]
        temp_dir = evidence_workflow["temp_dir"]

        # Add evidence for multiple stages
        stages = ["planning", "code_generation", "unit_testing", "qa_testing"]

        for stage in stages:
            file_path = Path(temp_dir) / f"{stage}_output.txt"
            file_path.write_text(f"{stage} output")
            collector.add_evidence(
                str(file_path),
                EvidenceCategory.REPORT,
                stage,
                f"{stage} report",
            )

        # Format each stage
        for stage in stages:
            stage_items = collector.get_evidence_by_stage(stage)
            comment = formatter.format_stage_comment(
                stage=stage,
                status="passed",
                duration_seconds=10.0,
                evidence_items=stage_items,
                format_type=ADOCommentFormat.MARKDOWN,
            )

            # Verify stage-specific content
            assert stage.replace("_", " ").title() in comment
            assert "PASSED" in comment
            assert f"{stage}_output.txt" in comment

    @pytest.mark.slow
    def test_large_evidence_collection(self, evidence_workflow):
        """Test handling large number of evidence files."""
        collector = evidence_workflow["collector"]
        temp_dir = evidence_workflow["temp_dir"]

        # Create many evidence files
        num_files = 50
        for i in range(num_files):
            file_path = Path(temp_dir) / f"evidence_{i}.txt"
            file_path.write_text(f"Evidence content {i}")

            category = (
                EvidenceCategory.CODE
                if i < 20
                else EvidenceCategory.TEST if i < 40 else EvidenceCategory.REPORT
            )
            stage = (
                "code_generation"
                if i < 25
                else "unit_testing" if i < 45 else "qa_testing"
            )

            collector.add_evidence(str(file_path), category, stage)

        # Verify collection
        assert len(collector.get_all_evidence()) == num_files

        # Verify summary can handle large counts
        summary = collector.get_summary()
        assert summary["total_items"] == num_files
        assert summary["by_category"]["code"] == 20
        assert summary["by_category"]["test"] == 20
        assert summary["by_category"]["report"] == 10


@pytest.mark.integration
@pytest.mark.requires_azure
class TestAzureBlobStorageIntegration:
    """Integration tests for Azure Blob Storage (requires credentials)."""

    def test_azure_blob_upload_download(self, work_item_id, temp_dir):
        """
        Test uploading and downloading from Azure Blob Storage.

        NOTE: This test requires Azure credentials to be configured.
        Set AZURE_STORAGE_CONNECTION_STRING environment variable.
        """
        pytest.skip("Requires Azure credentials")

        # Uncomment when running with Azure credentials
        # from ai_sdlc.evidence import AzureBlobEvidenceStorage
        #
        # storage = AzureBlobEvidenceStorage(container_name="test-evidence")
        #
        # # Create test file
        # test_file = Path(temp_dir) / "test.txt"
        # test_file.write_text("Test content")
        #
        # # Upload
        # remote_path = f"{work_item_id}/test/test.txt"
        # url = storage.upload_file(str(test_file), remote_path)
        # assert url is not None
        #
        # # Download
        # download_file = Path(temp_dir) / "downloaded.txt"
        # success = storage.download_file(remote_path, str(download_file))
        # assert success is True
        # assert download_file.read_text() == "Test content"
        #
        # # Cleanup
        # storage.delete_file(remote_path)
