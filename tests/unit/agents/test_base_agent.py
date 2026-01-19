"""
Unit tests for BaseAgent.
"""

import pytest
from pathlib import Path
from ai_sdlc.agents.base_agent import BaseAgent


class ConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""

    def execute(self, input_data, timeout_seconds=None):
        """Simple execution implementation."""
        try:
            # Validate input
            if not input_data.get("work_item_title"):
                raise ValueError("work_item_title is required")

            # Process
            result_data = {
                "processed_title": input_data["work_item_title"].upper(),
                "metric": 100,
            }

            # Save evidence
            evidence_path = self._save_evidence_file(
                "test-report.txt", "Test Report Content"
            )

            return {
                "success": True,
                "output_data": result_data,
                "evidence_files": [evidence_path],
            }

        except Exception as e:
            return {
                "success": False,
                "output_data": {},
                "evidence_files": [],
                "error_message": str(e),
            }


@pytest.mark.unit
class TestBaseAgent:
    """Test suite for BaseAgent."""

    @pytest.fixture
    def agent(self, work_item_id, mock_config, temp_dir):
        """Create agent instance."""
        return ConcreteAgent(
            work_item_id=work_item_id,
            config=mock_config,
            evidence_path=temp_dir,
        )

    def test_initialization(self, agent, work_item_id, mock_config, temp_dir):
        """Test agent initializes correctly."""
        assert agent.work_item_id == work_item_id
        assert agent.config == mock_config
        assert agent.evidence_path == temp_dir

        # Evidence directory should be created
        assert Path(temp_dir).exists()

    def test_execute_success(self, agent):
        """Test successful agent execution."""
        input_data = {
            "work_item_title": "test title",
            "work_item_description": "test description",
        }

        result = agent.execute(input_data)

        assert result["success"] is True
        assert "output_data" in result
        assert "evidence_files" in result
        assert len(result["evidence_files"]) > 0
        assert result["output_data"]["processed_title"] == "TEST TITLE"

    def test_execute_missing_input(self, agent):
        """Test execution with missing required input."""
        input_data = {}  # Missing work_item_title

        result = agent.execute(input_data)

        assert result["success"] is False
        assert "error_message" in result
        assert "work_item_title is required" in result["error_message"]

    def test_get_evidence_file_path(self, agent, temp_dir):
        """Test getting evidence file path."""
        filename = "test-file.txt"
        file_path = agent._get_evidence_file_path(filename)

        expected_path = str(Path(temp_dir) / filename)
        assert file_path == expected_path

    def test_save_evidence_file(self, agent, temp_dir):
        """Test saving text evidence file."""
        filename = "test-report.txt"
        content = "Test Report Content"

        file_path = agent._save_evidence_file(filename, content)

        # Verify file was created
        assert Path(file_path).exists()

        # Verify content
        with open(file_path, "r", encoding="utf-8") as f:
            saved_content = f.read()
        assert saved_content == content

    def test_save_json_evidence(self, agent, temp_dir):
        """Test saving JSON evidence file."""
        filename = "test-data.json"
        data = {"key": "value", "number": 42}

        file_path = agent._save_json_evidence(filename, data)

        # Verify file was created
        assert Path(file_path).exists()

        # Verify content is valid JSON
        import json

        with open(file_path, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        assert loaded_data == data

    def test_save_json_evidence_formatting(self, agent, temp_dir):
        """Test JSON evidence is properly formatted."""
        filename = "test-data.json"
        data = {"key1": "value1", "key2": "value2"}

        file_path = agent._save_json_evidence(filename, data)

        # Verify file is indented
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "  " in content  # Should have indentation

    def test_evidence_path_creation(self, work_item_id, mock_config, temp_dir):
        """Test evidence directory is created if it doesn't exist."""
        # Use non-existent subdirectory
        evidence_path = str(Path(temp_dir) / "new_evidence_dir")

        agent = ConcreteAgent(
            work_item_id=work_item_id,
            config=mock_config,
            evidence_path=evidence_path,
        )

        # Directory should be created
        assert Path(evidence_path).exists()
        assert Path(evidence_path).is_dir()

    def test_multiple_evidence_files(self, agent):
        """Test saving multiple evidence files."""
        # Save multiple files
        file1 = agent._save_evidence_file("file1.txt", "Content 1")
        file2 = agent._save_evidence_file("file2.txt", "Content 2")
        file3 = agent._save_json_evidence("file3.json", {"data": 3})

        # All files should exist
        assert Path(file1).exists()
        assert Path(file2).exists()
        assert Path(file3).exists()

        # Files should be in evidence directory
        assert Path(file1).parent == Path(agent.evidence_path)
        assert Path(file2).parent == Path(agent.evidence_path)
        assert Path(file3).parent == Path(agent.evidence_path)

    def test_execute_with_timeout(self, agent):
        """Test execution with timeout parameter."""
        input_data = {"work_item_title": "test"}

        # Execute with timeout (should still succeed quickly)
        result = agent.execute(input_data, timeout_seconds=30)

        assert result["success"] is True

    def test_result_structure(self, agent):
        """Test that execute returns correct result structure."""
        input_data = {"work_item_title": "test"}

        result = agent.execute(input_data)

        # Verify required keys
        assert "success" in result
        assert "output_data" in result
        assert "evidence_files" in result

        # Verify types
        assert isinstance(result["success"], bool)
        assert isinstance(result["output_data"], dict)
        assert isinstance(result["evidence_files"], list)

    def test_logger_initialization(self, agent):
        """Test that agent has logger initialized."""
        assert hasattr(agent, "logger")
        assert agent.logger is not None

    def test_config_access(self, agent, mock_config):
        """Test accessing configuration."""
        assert agent.config == mock_config
        assert agent.config.get("llm_model") == "test-model"
        assert agent.config.get("temperature") == 0.2

    def test_evidence_file_with_subdirectory(self, agent, temp_dir):
        """Test saving evidence file in subdirectory."""
        filename = "subdir/nested/file.txt"
        content = "Nested file content"

        # This should work even with nested paths
        file_path = agent._save_evidence_file(filename, content)

        # Verify file was created in correct location
        assert Path(file_path).exists()

        # Verify the full path includes subdirectories
        assert "subdir" in file_path
        assert "nested" in file_path
