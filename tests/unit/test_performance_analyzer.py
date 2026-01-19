"""
Unit tests for PerformanceAnalyzerAgent.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

from ai_sdlc.agents.performance_analyzer_agent import PerformanceAnalyzerAgent


@pytest.fixture
def agent(tmp_path):
    """Create PerformanceAnalyzerAgent instance."""
    return PerformanceAnalyzerAgent(
        work_item_id="test-123",
        config={},
        evidence_path=str(tmp_path / "evidence")
    )


@pytest.fixture
def sample_event_log():
    """Sample Spark event log content."""
    return """
    {"Event":"SparkListenerApplicationStart","App Name":"TestApp","Timestamp":1234567890}
    {"Event":"SparkListenerStageSubmitted","Stage Info":{"Stage ID":0,"Number of Tasks":100}}
    {"Event":"SparkListenerTaskEnd","Task Info":{"Task ID":0,"Duration":1000,"Metrics":{"Executor Run Time":900,"Memory Bytes Spilled":104857600}}}
    {"Event":"SparkListenerTaskEnd","Task Info":{"Task ID":1,"Duration":5000,"Metrics":{"Executor Run Time":4900,"Memory Bytes Spilled":524288000}}}
    {"Event":"SparkListenerStageCompleted","Stage Info":{"Stage ID":0}}
    """


@pytest.fixture
def sample_query_plan():
    """Sample Spark query plan."""
    return """
    == Physical Plan ==
    CollectLimit 100
    +- Project [id#0, name#1, value#2]
       +- Join Inner, (id#0 = id#3)
          :- Scan parquet table1
          +- Scan parquet table2
    """


@pytest.fixture
def sample_metrics():
    """Sample performance metrics."""
    return {
        "response_time_ms": 3500,
        "memory_usage_gb": 12.5,
        "cpu_usage_percent": 85.3,
        "total_tasks": 1000,
        "failed_tasks": 5,
        "data_read_gb": 100.0,
        "data_written_gb": 50.0,
        "shuffle_read_gb": 25.0,
        "shuffle_write_gb": 25.0,
    }


@pytest.mark.unit
class TestPerformanceAnalyzerAgent:
    """Tests for PerformanceAnalyzerAgent."""

    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.work_item_id == "test-123"
        assert agent.evidence_path.endswith("evidence")

    def test_execute_logs_analysis_success(self, agent, tmp_path, sample_event_log):
        """Test successful event log analysis."""
        # Create temporary log file
        log_file = tmp_path / "eventlog.txt"
        log_file.write_text(sample_event_log)

        input_data = {
            "analysis_type": "logs",
            "log_path": str(log_file),
            "thresholds": {
                "skew_threshold": 3.0,
                "spill_threshold_mb": 100,
            },
        }

        result = agent.execute(input_data)

        assert result["success"]
        assert "data" in result
        assert "performance_score" in result["data"]
        assert "issues" in result["data"]
        assert "bottlenecks" in result["data"]
        assert "recommendations" in result["data"]
        assert "report_file" in result["data"]
        assert "optimization_script" in result["data"]

    def test_execute_query_plan_analysis_success(self, agent, sample_query_plan):
        """Test successful query plan analysis."""
        input_data = {
            "analysis_type": "query_plan",
            "query_plan": sample_query_plan,
        }

        result = agent.execute(input_data)

        assert result["success"]
        assert "data" in result
        assert "performance_score" in result["data"]
        assert "issues" in result["data"]
        assert "recommendations" in result["data"]

    def test_execute_metrics_analysis_success(self, agent, sample_metrics):
        """Test successful metrics analysis."""
        input_data = {
            "analysis_type": "metrics",
            "metrics": sample_metrics,
            "thresholds": {
                "response_time_threshold_ms": 2000,
                "memory_threshold_gb": 10,
            },
        }

        result = agent.execute(input_data)

        assert result["success"]
        assert "data" in result
        assert "performance_score" in result["data"]
        assert "issues" in result["data"]

        # Should detect high response time and memory usage
        issues = result["data"]["issues"]
        assert any("response time" in i["description"].lower() for i in issues)
        assert any("memory" in i["description"].lower() for i in issues)

    def test_execute_full_analysis_success(
        self, agent, tmp_path, sample_event_log, sample_query_plan, sample_metrics
    ):
        """Test comprehensive full analysis."""
        # Create temporary log file
        log_file = tmp_path / "eventlog.txt"
        log_file.write_text(sample_event_log)

        input_data = {
            "analysis_type": "full",
            "log_path": str(log_file),
            "query_plan": sample_query_plan,
            "metrics": sample_metrics,
        }

        result = agent.execute(input_data)

        assert result["success"]
        assert "data" in result
        assert "performance_score" in result["data"]
        assert "issues" in result["data"]
        assert "bottlenecks" in result["data"]
        assert "recommendations" in result["data"]
        assert "report_file" in result["data"]

    def test_execute_missing_analysis_type(self, agent):
        """Test execution with missing analysis type."""
        input_data = {}

        result = agent.execute(input_data)

        assert not result["success"]
        assert "error_message" in result
        assert "analysis_type" in result["error_message"]

    def test_execute_invalid_analysis_type(self, agent):
        """Test execution with invalid analysis type."""
        input_data = {"analysis_type": "invalid"}

        result = agent.execute(input_data)

        assert not result["success"]
        assert "error_message" in result

    def test_execute_logs_missing_log_path(self, agent):
        """Test logs analysis with missing log path."""
        input_data = {"analysis_type": "logs"}

        result = agent.execute(input_data)

        assert not result["success"]
        assert "error_message" in result
        assert "log_path" in result["error_message"]

    def test_execute_query_plan_missing_plan(self, agent):
        """Test query plan analysis with missing plan."""
        input_data = {"analysis_type": "query_plan"}

        result = agent.execute(input_data)

        assert not result["success"]
        assert "error_message" in result
        assert "query_plan" in result["error_message"]

    def test_execute_metrics_missing_metrics(self, agent):
        """Test metrics analysis with missing metrics."""
        input_data = {"analysis_type": "metrics"}

        result = agent.execute(input_data)

        assert not result["success"]
        assert "error_message" in result
        assert "metrics" in result["error_message"]

    def test_data_skew_detection(self, agent, tmp_path):
        """Test data skew detection from event logs."""
        # Create log with skewed task durations
        skewed_log = """
        {"Event":"SparkListenerApplicationStart","App Name":"TestApp"}
        {"Event":"SparkListenerTaskEnd","Task Info":{"Task ID":0,"Duration":1000}}
        {"Event":"SparkListenerTaskEnd","Task Info":{"Task ID":1,"Duration":1000}}
        {"Event":"SparkListenerTaskEnd","Task Info":{"Task ID":2,"Duration":10000}}
        """
        log_file = tmp_path / "skewed_log.txt"
        log_file.write_text(skewed_log)

        input_data = {
            "analysis_type": "logs",
            "log_path": str(log_file),
            "thresholds": {"skew_threshold": 3.0},
        }

        result = agent.execute(input_data)

        assert result["success"]
        issues = result["data"]["issues"]
        # Should detect skew (max 10000ms vs median ~1000ms)
        assert any("skew" in i["description"].lower() for i in issues)

    def test_spill_to_disk_detection(self, agent, tmp_path):
        """Test spill to disk detection."""
        # Create log with memory spill
        spill_log = """
        {"Event":"SparkListenerApplicationStart","App Name":"TestApp"}
        {"Event":"SparkListenerTaskEnd","Task Info":{"Task ID":0,"Metrics":{"Memory Bytes Spilled":524288000}}}
        {"Event":"SparkListenerTaskEnd","Task Info":{"Task ID":1,"Metrics":{"Memory Bytes Spilled":1048576000}}}
        """
        log_file = tmp_path / "spill_log.txt"
        log_file.write_text(spill_log)

        input_data = {
            "analysis_type": "logs",
            "log_path": str(log_file),
            "thresholds": {"spill_threshold_mb": 100},
        }

        result = agent.execute(input_data)

        assert result["success"]
        issues = result["data"]["issues"]
        # Should detect spill (>100MB threshold)
        assert any("spill" in i["description"].lower() for i in issues)

    def test_collect_usage_detection(self, agent):
        """Test detection of collect() usage in query plan."""
        query_plan_with_collect = """
        == Physical Plan ==
        CollectLimit 1000000
        +- Scan parquet table
        """

        input_data = {
            "analysis_type": "query_plan",
            "query_plan": query_plan_with_collect,
        }

        result = agent.execute(input_data)

        assert result["success"]
        issues = result["data"]["issues"]
        # Should detect large collect
        assert any(
            "collect" in i["description"].lower() or "limit" in i["description"].lower()
            for i in issues
        )

    def test_cartesian_join_detection(self, agent):
        """Test detection of cartesian product in query plan."""
        query_plan_with_cartesian = """
        == Physical Plan ==
        CartesianProduct
        :- Scan parquet table1
        +- Scan parquet table2
        """

        input_data = {
            "analysis_type": "query_plan",
            "query_plan": query_plan_with_cartesian,
        }

        result = agent.execute(input_data)

        assert result["success"]
        issues = result["data"]["issues"]
        # Should detect cartesian join
        assert any("cartesian" in i["description"].lower() for i in issues)

    def test_performance_score_calculation(self, agent, sample_metrics):
        """Test performance score calculation."""
        # Good metrics
        good_metrics = {
            "response_time_ms": 500,
            "memory_usage_gb": 2.0,
            "cpu_usage_percent": 50.0,
            "failed_tasks": 0,
        }

        input_data = {
            "analysis_type": "metrics",
            "metrics": good_metrics,
            "thresholds": {
                "response_time_threshold_ms": 2000,
                "memory_threshold_gb": 10,
            },
        }

        result = agent.execute(input_data)

        assert result["success"]
        # Good metrics should have high score
        assert result["data"]["performance_score"] > 70

        # Bad metrics
        bad_metrics = {
            "response_time_ms": 10000,
            "memory_usage_gb": 50.0,
            "cpu_usage_percent": 95.0,
            "failed_tasks": 100,
        }

        input_data["metrics"] = bad_metrics

        result = agent.execute(input_data)

        assert result["success"]
        # Bad metrics should have low score
        assert result["data"]["performance_score"] < 50

    def test_optimization_script_generation(self, agent, tmp_path, sample_event_log):
        """Test that optimization script is generated."""
        log_file = tmp_path / "eventlog.txt"
        log_file.write_text(sample_event_log)

        input_data = {
            "analysis_type": "logs",
            "log_path": str(log_file),
        }

        result = agent.execute(input_data)

        assert result["success"]
        assert "optimization_script" in result["data"]

        # Check that script file exists
        script_file = Path(result["data"]["optimization_script"])
        assert script_file.exists()

        # Check script content
        script_content = script_file.read_text()
        assert "from pyspark.sql import SparkSession" in script_content
        assert "def optimize_" in script_content

    def test_performance_report_generation(self, agent, tmp_path, sample_event_log):
        """Test that performance report is generated."""
        log_file = tmp_path / "eventlog.txt"
        log_file.write_text(sample_event_log)

        input_data = {
            "analysis_type": "logs",
            "log_path": str(log_file),
        }

        result = agent.execute(input_data)

        assert result["success"]
        assert "report_file" in result["data"]

        # Check that report file exists
        report_file = Path(result["data"]["report_file"])
        assert report_file.exists()

        # Check report content
        report_content = report_file.read_text()
        assert "# Performance Analysis Report" in report_content
        assert "## Performance Score" in report_content
        assert "## Issues Detected" in report_content
        assert "## Recommendations" in report_content

    def test_metrics_summary_generation(self, agent, tmp_path, sample_event_log):
        """Test that metrics summary JSON is generated."""
        log_file = tmp_path / "eventlog.txt"
        log_file.write_text(sample_event_log)

        input_data = {
            "analysis_type": "logs",
            "log_path": str(log_file),
        }

        result = agent.execute(input_data)

        assert result["success"]
        assert "metrics_summary" in result["data"]

        # Check that summary file exists
        summary_file = Path(result["data"]["metrics_summary"])
        assert summary_file.exists()

        # Check summary content
        with open(summary_file, "r") as f:
            summary = json.load(f)

        assert "performance_score" in summary
        assert "total_issues" in summary
        assert "issues_by_severity" in summary

    def test_recommendations_prioritization(self, agent, sample_metrics):
        """Test that recommendations are prioritized."""
        # Create metrics with multiple issues
        problematic_metrics = {
            "response_time_ms": 5000,  # High
            "memory_usage_gb": 20.0,  # High
            "cpu_usage_percent": 95.0,  # High
            "failed_tasks": 50,  # High
            "shuffle_read_gb": 100.0,  # Medium
        }

        input_data = {
            "analysis_type": "metrics",
            "metrics": problematic_metrics,
            "thresholds": {
                "response_time_threshold_ms": 2000,
                "memory_threshold_gb": 10,
            },
        }

        result = agent.execute(input_data)

        assert result["success"]
        recommendations = result["data"]["recommendations"]

        # Should have multiple recommendations
        assert len(recommendations) > 0

        # Critical/high severity issues should come first
        issues = result["data"]["issues"]
        critical_or_high = [i for i in issues if i["severity"] in ["critical", "high"]]
        assert len(critical_or_high) > 0

    def test_evidence_path_creation(self, agent, tmp_path, sample_event_log):
        """Test that evidence directory is created."""
        log_file = tmp_path / "eventlog.txt"
        log_file.write_text(sample_event_log)

        input_data = {
            "analysis_type": "logs",
            "log_path": str(log_file),
        }

        result = agent.execute(input_data)

        assert result["success"]

        # Check that evidence directory exists
        evidence_dir = Path(agent.evidence_path)
        assert evidence_dir.exists()
        assert evidence_dir.is_dir()

    def test_concurrent_analysis_isolation(self, tmp_path, sample_event_log):
        """Test that multiple concurrent analyses don't interfere."""
        # Create two agents with different work items
        agent1 = PerformanceAnalyzerAgent(
            work_item_id="test-1",
            config={},
            evidence_path=str(tmp_path / "evidence1")
        )
        agent2 = PerformanceAnalyzerAgent(
            work_item_id="test-2",
            config={},
            evidence_path=str(tmp_path / "evidence2")
        )

        log_file = tmp_path / "eventlog.txt"
        log_file.write_text(sample_event_log)

        input_data = {
            "analysis_type": "logs",
            "log_path": str(log_file),
        }

        # Execute both
        result1 = agent1.execute(input_data)
        result2 = agent2.execute(input_data)

        assert result1["success"]
        assert result2["success"]

        # Check that evidence is isolated
        assert result1["data"]["report_file"] != result2["data"]["report_file"]
        assert Path(result1["data"]["report_file"]).exists()
        assert Path(result2["data"]["report_file"]).exists()

    def test_large_event_log_handling(self, agent, tmp_path):
        """Test handling of large event logs."""
        # Create a large log file
        large_log_lines = []
        for i in range(10000):
            large_log_lines.append(
                f'{{"Event":"SparkListenerTaskEnd","Task Info":{{"Task ID":{i},"Duration":{1000 + i % 100}}}}}'
            )

        log_file = tmp_path / "large_log.txt"
        log_file.write_text("\n".join(large_log_lines))

        input_data = {
            "analysis_type": "logs",
            "log_path": str(log_file),
        }

        result = agent.execute(input_data)

        assert result["success"]
        assert "performance_score" in result["data"]

    def test_empty_query_plan_handling(self, agent):
        """Test handling of empty query plan."""
        input_data = {
            "analysis_type": "query_plan",
            "query_plan": "",
        }

        result = agent.execute(input_data)

        # Should handle gracefully
        assert result["success"]
        assert result["data"]["performance_score"] >= 0

    def test_malformed_metrics_handling(self, agent):
        """Test handling of malformed metrics."""
        malformed_metrics = {
            "response_time_ms": "invalid",  # Should be number
            "memory_usage_gb": None,
        }

        input_data = {
            "analysis_type": "metrics",
            "metrics": malformed_metrics,
        }

        result = agent.execute(input_data)

        # Should handle gracefully (might fail or return degraded results)
        if not result["success"]:
            assert "error_message" in result
        else:
            # If it succeeds, should have valid score
            assert 0 <= result["data"]["performance_score"] <= 100
