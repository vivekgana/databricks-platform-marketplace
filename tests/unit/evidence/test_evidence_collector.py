"""
Unit tests for EvidenceCollector.
"""

import pytest
from pathlib import Path
from ai_sdlc.evidence import EvidenceCollector, EvidenceCategory, EvidenceItem


@pytest.mark.unit
class TestEvidenceCollector:
    """Test suite for EvidenceCollector."""

    @pytest.fixture
    def collector(self, work_item_id, temp_dir):
        """Create EvidenceCollector instance."""
        return EvidenceCollector(
            work_item_id=work_item_id, base_path=temp_dir
        )

    def test_initialization(self, collector, work_item_id, temp_dir):
        """Test collector initializes correctly."""
        assert collector.work_item_id == work_item_id
        assert collector.base_path == temp_dir
        assert len(collector.evidence_items) == 0

    def test_add_evidence(self, collector, temp_dir):
        """Test adding evidence item."""
        # Create test file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("test content")

        # Add evidence
        item = collector.add_evidence(
            path=str(test_file),
            category=EvidenceCategory.REPORT,
            stage="test_stage",
            description="Test report",
        )

        assert isinstance(item, EvidenceItem)
        assert item.path == str(test_file)
        assert item.category == EvidenceCategory.REPORT
        assert item.stage == "test_stage"
        assert item.description == "Test report"
        assert item.filename == "test.txt"
        assert item.size_bytes > 0
        assert len(collector.evidence_items) == 1

    def test_add_screenshot(self, collector, temp_dir):
        """Test adding screenshot evidence."""
        screenshot_file = Path(temp_dir) / "screenshot.png"
        screenshot_file.write_bytes(b"fake-png-data")

        item = collector.add_screenshot(
            path=str(screenshot_file),
            stage="qa_testing",
            description="Test screenshot",
        )

        assert item.category == EvidenceCategory.SCREENSHOT
        assert item.stage == "qa_testing"
        assert len(collector.evidence_items) == 1

    def test_add_report(self, collector, temp_dir):
        """Test adding report evidence."""
        report_file = Path(temp_dir) / "report.html"
        report_file.write_text("<html>Report</html>")

        item = collector.add_report(
            path=str(report_file),
            stage="unit_testing",
            description="Test report",
        )

        assert item.category == EvidenceCategory.REPORT
        assert item.stage == "unit_testing"

    def test_get_evidence_by_category(self, collector, temp_dir):
        """Test retrieving evidence by category."""
        # Add multiple items
        for i in range(3):
            file_path = Path(temp_dir) / f"report_{i}.txt"
            file_path.write_text(f"Report {i}")
            collector.add_report(str(file_path), "test_stage")

        for i in range(2):
            file_path = Path(temp_dir) / f"screenshot_{i}.png"
            file_path.write_bytes(b"fake-png")
            collector.add_screenshot(str(file_path), "test_stage")

        # Get by category
        reports = collector.get_evidence_by_category(EvidenceCategory.REPORT)
        screenshots = collector.get_evidence_by_category(
            EvidenceCategory.SCREENSHOT
        )

        assert len(reports) == 3
        assert len(screenshots) == 2

    def test_get_evidence_by_stage(self, collector, temp_dir):
        """Test retrieving evidence by stage."""
        # Add items to different stages
        file1 = Path(temp_dir) / "file1.txt"
        file1.write_text("content1")
        collector.add_evidence(
            str(file1), EvidenceCategory.CODE, "code_generation"
        )

        file2 = Path(temp_dir) / "file2.txt"
        file2.write_text("content2")
        collector.add_evidence(str(file2), EvidenceCategory.TEST, "unit_testing")

        file3 = Path(temp_dir) / "file3.txt"
        file3.write_text("content3")
        collector.add_evidence(
            str(file3), EvidenceCategory.CODE, "code_generation"
        )

        # Get by stage
        code_gen_items = collector.get_evidence_by_stage("code_generation")
        unit_test_items = collector.get_evidence_by_stage("unit_testing")

        assert len(code_gen_items) == 2
        assert len(unit_test_items) == 1

    def test_get_screenshots(self, collector, temp_dir):
        """Test getting all screenshots."""
        # Add screenshots
        for i in range(3):
            file_path = Path(temp_dir) / f"screenshot_{i}.png"
            file_path.write_bytes(b"fake-png")
            collector.add_screenshot(str(file_path), "qa_testing")

        # Add non-screenshot
        report_file = Path(temp_dir) / "report.txt"
        report_file.write_text("report")
        collector.add_report(str(report_file), "qa_testing")

        screenshots = collector.get_screenshots()
        assert len(screenshots) == 3
        assert all(
            item.category == EvidenceCategory.SCREENSHOT for item in screenshots
        )

    def test_get_reports(self, collector, temp_dir):
        """Test getting all reports."""
        # Add reports
        for i in range(2):
            file_path = Path(temp_dir) / f"report_{i}.html"
            file_path.write_text(f"<html>Report {i}</html>")
            collector.add_report(str(file_path), "unit_testing")

        reports = collector.get_reports()
        assert len(reports) == 2
        assert all(item.category == EvidenceCategory.REPORT for item in reports)

    def test_get_all_evidence(self, collector, temp_dir):
        """Test getting all evidence items."""
        # Add various items
        file1 = Path(temp_dir) / "file1.txt"
        file1.write_text("content")
        collector.add_evidence(str(file1), EvidenceCategory.CODE, "code_generation")

        file2 = Path(temp_dir) / "screenshot.png"
        file2.write_bytes(b"png")
        collector.add_screenshot(str(file2), "qa_testing")

        all_items = collector.get_all_evidence()
        assert len(all_items) == 2

    def test_get_summary(self, collector, temp_dir):
        """Test getting evidence summary."""
        # Add various items
        for i in range(2):
            file_path = Path(temp_dir) / f"code_{i}.py"
            file_path.write_text(f"code {i}")
            collector.add_evidence(
                str(file_path), EvidenceCategory.CODE, "code_generation"
            )

        for i in range(3):
            file_path = Path(temp_dir) / f"screenshot_{i}.png"
            file_path.write_bytes(b"png" * 100)
            collector.add_screenshot(str(file_path), "qa_testing")

        summary = collector.get_summary()

        assert summary["work_item_id"] == collector.work_item_id
        assert summary["total_items"] == 5
        assert summary["screenshots_count"] == 3
        assert summary["total_size_bytes"] > 0
        assert "by_category" in summary
        assert "by_stage" in summary

    def test_export_metadata(self, collector, temp_dir):
        """Test exporting evidence metadata."""
        # Add item
        file_path = Path(temp_dir) / "test.txt"
        file_path.write_text("content")
        collector.add_evidence(
            str(file_path), EvidenceCategory.CODE, "code_generation"
        )

        metadata = collector.export_metadata()

        assert metadata["work_item_id"] == collector.work_item_id
        assert metadata["base_path"] == collector.base_path
        assert "collected_at" in metadata
        assert "summary" in metadata
        assert "items" in metadata
        assert len(metadata["items"]) == 1

    def test_clear(self, collector, temp_dir):
        """Test clearing evidence items."""
        # Add items
        file_path = Path(temp_dir) / "test.txt"
        file_path.write_text("content")
        collector.add_evidence(
            str(file_path), EvidenceCategory.CODE, "code_generation"
        )

        assert len(collector.evidence_items) == 1

        # Clear
        collector.clear()

        assert len(collector.evidence_items) == 0

    def test_add_evidence_with_metadata(self, collector, temp_dir):
        """Test adding evidence with custom metadata."""
        file_path = Path(temp_dir) / "test.txt"
        file_path.write_text("content")

        custom_metadata = {"version": "1.0", "author": "test"}

        item = collector.add_evidence(
            path=str(file_path),
            category=EvidenceCategory.CODE,
            stage="code_generation",
            metadata=custom_metadata,
        )

        assert item.metadata == custom_metadata

    def test_evidence_item_to_dict(self, collector, temp_dir):
        """Test EvidenceItem serialization."""
        file_path = Path(temp_dir) / "test.txt"
        file_path.write_text("content")

        item = collector.add_evidence(
            str(file_path), EvidenceCategory.CODE, "code_generation"
        )

        item_dict = item.to_dict()

        assert item_dict["path"] == str(file_path)
        assert item_dict["category"] == "code"
        assert item_dict["stage"] == "code_generation"
        assert item_dict["filename"] == "test.txt"
        assert "created_at" in item_dict
