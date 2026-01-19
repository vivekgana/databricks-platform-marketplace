"""
Pytest configuration and shared fixtures for AI-SDLC tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import Any, Dict


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test evidence."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def work_item_id():
    """Standard test work item ID."""
    return "TEST-12345"


@pytest.fixture
def mock_config():
    """Mock configuration for agents and evaluators."""
    return {
        "llm_model": "test-model",
        "temperature": 0.2,
        "max_tokens": 1000,
        "timeout_seconds": 30,
    }


@pytest.fixture
def mock_ado_plugin():
    """Mock Azure DevOps plugin."""
    plugin = Mock()
    plugin.authenticate = MagicMock(return_value=True)
    plugin.get_work_item = MagicMock()
    plugin.update_work_item = MagicMock(return_value=True)
    plugin.add_comment = MagicMock(return_value=True)
    plugin.add_rich_comment = MagicMock(return_value=True)
    plugin.upload_attachment = MagicMock(return_value="https://attachment-url")
    plugin.upload_evidence_package = MagicMock(
        return_value={
            "uploaded_count": 3,
            "uploaded_urls": ["url1", "url2", "url3"],
            "skipped_count": 0,
        }
    )
    return plugin


@pytest.fixture
def sample_agent_result_success():
    """Sample successful agent result."""
    return {
        "success": True,
        "output_data": {
            "result": "Test output",
            "metric_1": 100,
            "metric_2": 0.95,
        },
        "evidence_files": [
            "/tmp/evidence/report.txt",
            "/tmp/evidence/data.json",
        ],
    }


@pytest.fixture
def sample_agent_result_failure():
    """Sample failed agent result."""
    return {
        "success": False,
        "output_data": {},
        "evidence_files": [],
        "error_message": "Agent execution failed",
    }


@pytest.fixture
def sample_work_item_data():
    """Sample work item data."""
    return {
        "work_item_id": "TEST-12345",
        "work_item_title": "Test Work Item",
        "work_item_description": "Test Description",
        "work_item_type": "Feature",
        "requirements": ["Requirement 1", "Requirement 2"],
    }


@pytest.fixture
def sample_evidence_items(temp_dir):
    """Create sample evidence files."""
    from ai_sdlc.evidence import EvidenceItem, EvidenceCategory
    from datetime import datetime

    # Create sample files
    report_path = Path(temp_dir) / "report.txt"
    report_path.write_text("Sample report content")

    data_path = Path(temp_dir) / "data.json"
    data_path.write_text('{"key": "value"}')

    screenshot_path = Path(temp_dir) / "screenshot.png"
    screenshot_path.write_bytes(b"fake-png-data")

    return [
        EvidenceItem(
            path=str(report_path),
            category=EvidenceCategory.REPORT,
            stage="test_stage",
            filename="report.txt",
            description="Test report",
            size_bytes=report_path.stat().st_size,
            created_at=datetime.now(),
            metadata={},
        ),
        EvidenceItem(
            path=str(data_path),
            category=EvidenceCategory.DATA,
            stage="test_stage",
            filename="data.json",
            description="Test data",
            size_bytes=data_path.stat().st_size,
            created_at=datetime.now(),
            metadata={},
        ),
        EvidenceItem(
            path=str(screenshot_path),
            category=EvidenceCategory.SCREENSHOT,
            stage="test_stage",
            filename="screenshot.png",
            description="Test screenshot",
            size_bytes=screenshot_path.stat().st_size,
            created_at=datetime.now(),
            metadata={"resolution": "1920x1080"},
        ),
    ]


@pytest.fixture
def mock_storage():
    """Mock evidence storage."""
    storage = Mock()
    storage.upload_file = MagicMock(return_value="https://storage-url/file")
    storage.download_file = MagicMock(return_value=True)
    storage.list_files = MagicMock(return_value=["file1.txt", "file2.json"])
    storage.get_file_url = MagicMock(return_value="https://storage-url/file")
    storage.delete_file = MagicMock(return_value=True)
    return storage


@pytest.fixture
def sample_stage_results():
    """Sample workflow stage results."""
    return {
        "planning": {
            "status": "passed",
            "duration_seconds": 12.3,
            "eval_score": 0.85,
        },
        "code_generation": {
            "status": "passed",
            "duration_seconds": 45.7,
            "eval_score": 0.92,
        },
        "unit_testing": {
            "status": "passed",
            "duration_seconds": 12.5,
            "eval_score": 0.88,
        },
    }


# Test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow-running tests")
    config.addinivalue_line("markers", "requires_azure: Tests requiring Azure credentials")
