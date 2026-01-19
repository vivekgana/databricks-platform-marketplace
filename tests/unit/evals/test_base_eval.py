"""
Unit tests for BaseEval and evaluation framework.
"""

import pytest
from ai_sdlc.evals.base_eval import BaseEval


class ConcreteEval(BaseEval):
    """Concrete implementation of BaseEval for testing."""

    def evaluate(self, agent_result):
        """Simple evaluation implementation."""
        if not agent_result.get("success", False):
            return {
                "passed": False,
                "score": 0.0,
                "issues": [
                    self._create_issue("critical", "execution", "Agent failed", "")
                ],
                "recommendations": ["Fix agent execution"],
                "metrics": {},
                "blocking_issues": ["Agent failed"],
            }

        output_data = agent_result.get("output_data", {})
        score = 0.0

        # Check metric_1 (50%)
        if output_data.get("metric_1", 0) >= 80:
            score += 0.5

        # Check metric_2 (50%)
        if output_data.get("metric_2", 0.0) >= 0.8:
            score += 0.5

        passed = self._is_passing_score(score)

        return {
            "passed": passed,
            "score": score,
            "issues": [],
            "recommendations": [],
            "metrics": output_data,
            "blocking_issues": [],
        }


@pytest.mark.unit
class TestBaseEval:
    """Test suite for BaseEval."""

    @pytest.fixture
    def evaluator(self):
        """Create evaluator instance."""
        return ConcreteEval(min_score=0.7)

    def test_initialization(self, evaluator):
        """Test evaluator initializes correctly."""
        assert evaluator.min_score == 0.7
        assert evaluator.config == {}

    def test_initialization_with_config(self):
        """Test evaluator initialization with config."""
        config = {"custom_setting": "value"}
        evaluator = ConcreteEval(min_score=0.8, config=config)

        assert evaluator.min_score == 0.8
        assert evaluator.config == config

    def test_evaluate_success(
        self, evaluator, sample_agent_result_success
    ):
        """Test evaluation with successful agent result."""
        result = evaluator.evaluate(sample_agent_result_success)

        assert "passed" in result
        assert "score" in result
        assert "issues" in result
        assert "recommendations" in result
        assert "metrics" in result
        assert "blocking_issues" in result
        assert isinstance(result["passed"], bool)
        assert isinstance(result["score"], float)

    def test_evaluate_agent_failure(
        self, evaluator, sample_agent_result_failure
    ):
        """Test evaluation with failed agent result."""
        result = evaluator.evaluate(sample_agent_result_failure)

        assert result["passed"] is False
        assert result["score"] == 0.0
        assert len(result["blocking_issues"]) > 0
        assert "Agent failed" in result["blocking_issues"][0]

    def test_evaluate_passing_score(self, evaluator):
        """Test evaluation that meets minimum score."""
        agent_result = {
            "success": True,
            "output_data": {"metric_1": 90, "metric_2": 0.9},
            "evidence_files": [],
        }

        result = evaluator.evaluate(agent_result)

        assert result["passed"] is True
        assert result["score"] >= evaluator.min_score

    def test_evaluate_failing_score(self, evaluator):
        """Test evaluation that fails to meet minimum score."""
        agent_result = {
            "success": True,
            "output_data": {"metric_1": 50, "metric_2": 0.5},
            "evidence_files": [],
        }

        result = evaluator.evaluate(agent_result)

        assert result["passed"] is False
        assert result["score"] < evaluator.min_score

    def test_create_issue(self, evaluator):
        """Test creating standardized issue."""
        issue = evaluator._create_issue(
            severity="high",
            category="quality",
            message="Quality issue found",
            location="module.function",
        )

        assert issue["severity"] == "high"
        assert issue["category"] == "quality"
        assert issue["message"] == "Quality issue found"
        assert issue["location"] == "module.function"

    def test_is_passing_score_true(self, evaluator):
        """Test passing score check returns True."""
        assert evaluator._is_passing_score(0.7) is True
        assert evaluator._is_passing_score(0.8) is True
        assert evaluator._is_passing_score(1.0) is True

    def test_is_passing_score_false(self, evaluator):
        """Test passing score check returns False."""
        assert evaluator._is_passing_score(0.69) is False
        assert evaluator._is_passing_score(0.5) is False
        assert evaluator._is_passing_score(0.0) is False

    def test_is_passing_score_boundary(self, evaluator):
        """Test passing score at exact boundary."""
        assert evaluator._is_passing_score(0.7) is True

    def test_different_min_scores(self):
        """Test evaluators with different minimum scores."""
        eval_70 = ConcreteEval(min_score=0.7)
        eval_80 = ConcreteEval(min_score=0.8)

        agent_result = {
            "success": True,
            "output_data": {"metric_1": 85, "metric_2": 0.7},
            "evidence_files": [],
        }

        result_70 = eval_70.evaluate(agent_result)
        result_80 = eval_80.evaluate(agent_result)

        # Score of 0.5 should pass for 70% but not 80%
        # (metric_1 >= 80 gives 0.5, metric_2 < 0.8 gives 0)
        assert result_70["score"] == 0.5
        assert result_80["score"] == 0.5

    def test_evaluation_result_structure(self, evaluator):
        """Test that evaluation result has correct structure."""
        agent_result = {
            "success": True,
            "output_data": {"metric_1": 90, "metric_2": 0.9},
            "evidence_files": [],
        }

        result = evaluator.evaluate(agent_result)

        # Verify all required keys are present
        required_keys = [
            "passed",
            "score",
            "issues",
            "recommendations",
            "metrics",
            "blocking_issues",
        ]
        for key in required_keys:
            assert key in result

        # Verify types
        assert isinstance(result["passed"], bool)
        assert isinstance(result["score"], (int, float))
        assert isinstance(result["issues"], list)
        assert isinstance(result["recommendations"], list)
        assert isinstance(result["metrics"], dict)
        assert isinstance(result["blocking_issues"], list)

    def test_score_bounds(self, evaluator):
        """Test that scores are properly bounded between 0 and 1."""
        # Test score at boundaries
        agent_result_max = {
            "success": True,
            "output_data": {"metric_1": 100, "metric_2": 1.0},
            "evidence_files": [],
        }

        agent_result_min = {
            "success": True,
            "output_data": {"metric_1": 0, "metric_2": 0.0},
            "evidence_files": [],
        }

        result_max = evaluator.evaluate(agent_result_max)
        result_min = evaluator.evaluate(agent_result_min)

        assert 0.0 <= result_max["score"] <= 1.0
        assert 0.0 <= result_min["score"] <= 1.0
