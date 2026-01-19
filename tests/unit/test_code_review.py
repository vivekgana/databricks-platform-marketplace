"""
Unit tests for PySpark Code Review functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from ai_sdlc.agents.code_review_agent import CodeReviewAgent
from ai_sdlc.evals.code_review_eval import CodeReviewEval


@pytest.mark.unit
class TestCodeReviewAgent:
    """Test suite for CodeReviewAgent."""

    @pytest.fixture
    def agent(self, temp_dir):
        """Create code review agent."""
        return CodeReviewAgent(work_item_id="12345", evidence_base_path=temp_dir)

    @pytest.fixture
    def sample_code_with_issues(self, temp_dir):
        """Create sample code file with security issues."""
        code_file = Path(temp_dir) / "sample.py"
        code_file.write_text(
            """
import os

def process_user_input(user_input):
    # SQL injection vulnerability
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"

    # Command injection vulnerability
    os.system("ls " + user_input)

    # Eval usage
    result = eval(user_input)

    return result

def inefficient_code(df):
    # Performance issue: collect()
    data = df.collect()

    # Performance issue: cartesian join
    df2 = df.crossJoin(df)

    return data
"""
        )
        return str(code_file)

    @pytest.fixture
    def sample_clean_code(self, temp_dir):
        """Create sample clean code file."""
        code_file = Path(temp_dir) / "clean.py"
        code_file.write_text(
            """
def add_numbers(a: int, b: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return a + b

class Calculator:
    \"\"\"Simple calculator class.\"\"\"

    def multiply(self, x: int, y: int) -> int:
        \"\"\"Multiply two numbers.\"\"\"
        return x * y
"""
        )
        return str(code_file)

    def test_execute_success(self, agent, sample_code_with_issues):
        """Test successful code review execution."""
        result = agent.execute(
            {
                "code_files": [sample_code_with_issues],
                "severity_threshold": "low",
                "review_type": "all",
            }
        )

        assert result["success"] is True
        assert result["data"]["files_reviewed"] == 1
        assert result["data"]["total_findings"] > 0
        assert "severity_score" in result["data"]
        assert "categorized" in result["data"]

    def test_execute_with_no_files(self, agent):
        """Test execution with no files provided."""
        result = agent.execute({"code_files": []})

        assert result["success"] is False
        assert "No code files provided" in result["error_message"]

    def test_security_pattern_detection(self, agent, sample_code_with_issues):
        """Test that security vulnerabilities are detected."""
        result = agent.execute(
            {
                "code_files": [sample_code_with_issues],
                "severity_threshold": "low",
                "review_type": "security",
            }
        )

        assert result["success"] is True
        summary = result["data"]["summary"]

        # Should detect SQL injection, command injection, and eval usage
        assert summary["critical_count"] >= 3

    def test_performance_pattern_detection(self, agent, sample_code_with_issues):
        """Test that performance issues are detected."""
        result = agent.execute(
            {
                "code_files": [sample_code_with_issues],
                "severity_threshold": "low",
                "review_type": "performance",
            }
        )

        assert result["success"] is True
        summary = result["data"]["summary"]

        # Should detect collect() and crossJoin()
        assert summary["total_findings"] >= 2

    def test_clean_code_review(self, agent, sample_clean_code):
        """Test review of clean code with no issues."""
        result = agent.execute(
            {
                "code_files": [sample_clean_code],
                "severity_threshold": "medium",
                "review_type": "all",
            }
        )

        assert result["success"] is True
        assert result["data"]["severity_score"] < 10  # Very low score

    def test_severity_threshold_filtering(self, agent, sample_code_with_issues):
        """Test that severity threshold filters results correctly."""
        # Get all findings
        result_all = agent.execute(
            {
                "code_files": [sample_code_with_issues],
                "severity_threshold": "low",
                "review_type": "all",
            }
        )

        # Get only high severity findings
        result_high = agent.execute(
            {
                "code_files": [sample_code_with_issues],
                "severity_threshold": "high",
                "review_type": "all",
            }
        )

        # High severity should have fewer findings
        assert (
            result_high["data"]["total_findings"]
            <= result_all["data"]["total_findings"]
        )

    def test_categorize_findings(self, agent):
        """Test findings categorization."""
        findings = [
            {"severity": "critical"},
            {"severity": "critical"},
            {"severity": "high"},
            {"severity": "medium"},
            {"severity": "low"},
        ]

        categorized = agent._categorize_findings(findings)

        assert categorized["critical"] == 2
        assert categorized["high"] == 1
        assert categorized["medium"] == 1
        assert categorized["low"] == 1

    def test_severity_score_calculation(self, agent):
        """Test severity score calculation."""
        findings = [
            {"severity": "critical"},  # 10 points
            {"severity": "high"},  # 5 points
            {"severity": "medium"},  # 2 points
            {"severity": "low"},  # 1 point
        ]

        score = agent._calculate_severity_score(findings)

        assert score == 18  # 10 + 5 + 2 + 1

    def test_code_snippet_extraction(self, agent):
        """Test code snippet extraction."""
        code = "line 1\nline 2\nline 3\nline 4\nline 5"
        snippet = agent._get_code_snippet(code, 3, context=1)

        assert "line 2" in snippet
        assert "line 3" in snippet
        assert "line 4" in snippet
        assert ">>>" in snippet  # Marker for target line

    def test_nonexistent_file(self, agent):
        """Test handling of nonexistent files."""
        result = agent.execute({"code_files": ["/nonexistent/file.py"]})

        assert result["success"] is True  # Doesn't fail on missing files
        assert result["data"]["files_reviewed"] == 0


@pytest.mark.unit
class TestCodeReviewEval:
    """Test suite for CodeReviewEval."""

    @pytest.fixture
    def evaluator(self):
        """Create code review evaluator."""
        return CodeReviewEval(min_score=0.7)

    def test_evaluate_success(self, evaluator):
        """Test evaluation of successful review."""
        agent_result = {
            "success": True,
            "data": {
                "files_reviewed": 5,
                "severity_score": 10,
                "total_findings": 5,
                "summary": {
                    "critical_count": 0,
                    "high_count": 1,
                    "medium_count": 2,
                    "low_count": 2,
                    "severity_score": 10,
                    "total_findings": 5,
                },
            },
        }

        result = evaluator.evaluate(agent_result)

        assert result["passed"] is True
        assert result["score"] >= 0.7
        assert result["metrics"]["files_reviewed"] == 5

    def test_evaluate_critical_issues(self, evaluator):
        """Test evaluation with critical issues."""
        agent_result = {
            "success": True,
            "data": {
                "files_reviewed": 5,
                "severity_score": 30,
                "total_findings": 3,
                "summary": {
                    "critical_count": 3,
                    "high_count": 0,
                    "medium_count": 0,
                    "low_count": 0,
                    "severity_score": 30,
                    "total_findings": 3,
                },
            },
        }

        result = evaluator.evaluate(agent_result)

        assert result["passed"] is False
        assert len([i for i in result["issues"] if i.blocking]) > 0
        assert any("critical" in i.description.lower() for i in result["issues"])

    def test_evaluate_high_severity_score(self, evaluator):
        """Test evaluation with high severity score."""
        agent_result = {
            "success": True,
            "data": {
                "files_reviewed": 5,
                "severity_score": 60,
                "total_findings": 12,
                "summary": {
                    "critical_count": 0,
                    "high_count": 12,
                    "medium_count": 0,
                    "low_count": 0,
                    "severity_score": 60,
                    "total_findings": 12,
                },
            },
        }

        result = evaluator.evaluate(agent_result)

        assert result["passed"] is False
        assert any("score" in i.description.lower() for i in result["issues"])

    def test_evaluate_agent_failure(self, evaluator):
        """Test evaluation when agent fails."""
        agent_result = {
            "success": False,
            "error_message": "Agent execution failed",
        }

        result = evaluator.evaluate(agent_result)

        assert result["passed"] is False
        assert result["score"] == 0.0
        assert len(result["issues"]) > 0
        assert result["issues"][0].blocking is True

    def test_evaluate_no_files_reviewed(self, evaluator):
        """Test evaluation when no files were reviewed."""
        agent_result = {
            "success": True,
            "data": {
                "files_reviewed": 0,
                "severity_score": 0,
                "total_findings": 0,
                "summary": {
                    "critical_count": 0,
                    "high_count": 0,
                    "medium_count": 0,
                    "low_count": 0,
                    "severity_score": 0,
                    "total_findings": 0,
                },
            },
        }

        result = evaluator.evaluate(agent_result)

        assert result["passed"] is False
        assert any("no files" in i.description.lower() for i in result["issues"])

    def test_recommendations_generation(self, evaluator):
        """Test that recommendations are generated based on findings."""
        agent_result = {
            "success": True,
            "data": {
                "files_reviewed": 5,
                "severity_score": 40,
                "total_findings": 8,
                "summary": {
                    "critical_count": 2,
                    "high_count": 2,
                    "medium_count": 2,
                    "low_count": 2,
                    "severity_score": 40,
                    "total_findings": 8,
                },
            },
        }

        result = evaluator.evaluate(agent_result)

        assert len(result["recommendations"]) > 0
        assert any("critical" in rec.lower() for rec in result["recommendations"])


@pytest.mark.integration
class TestCodeReviewIntegration:
    """Integration tests for code review workflow."""

    def test_full_review_workflow(self, temp_dir):
        """Test complete code review workflow."""
        # Create code files
        code_file = Path(temp_dir) / "app.py"
        code_file.write_text(
            """
def process(data):
    # SQL injection
    query = "SELECT * FROM table WHERE id = " + data
    return query
"""
        )

        # Run agent
        agent = CodeReviewAgent(work_item_id="test", evidence_base_path=temp_dir)
        agent_result = agent.execute(
            {"code_files": [str(code_file)], "review_type": "all"}
        )

        # Evaluate
        evaluator = CodeReviewEval(min_score=0.7)
        eval_result = evaluator.evaluate(agent_result)

        # Verify
        assert agent_result["success"] is True
        assert eval_result["score"] >= 0.0
        assert "issues" in eval_result
