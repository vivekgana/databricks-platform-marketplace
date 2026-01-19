"""
Evaluation Framework for AI-SDLC

Provides evaluation (evals) for workflow stages to ensure quality gates are met.
"""

from .eval_framework import (
    BaseEval,
    EvalResult,
    EvalIssue,
    IssueSeverity,
    EvalRunner,
)
from .code_eval import CodeEval
from .test_eval import TestEval
from .plan_eval import PlanEval

__all__ = [
    "BaseEval",
    "EvalResult",
    "EvalIssue",
    "IssueSeverity",
    "EvalRunner",
    "CodeEval",
    "TestEval",
    "PlanEval",
]
