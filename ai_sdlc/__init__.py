"""
AI-SDLC - AI-Driven Software Development Life Cycle for Databricks

A comprehensive system for automating software development workflows with
AI-powered code generation, multi-repo awareness, and Databricks integration.
"""

__version__ = "0.1.0"
__author__ = "Databricks Platform Team"

from .core.config_loader import ConfigLoader, ProjectConfig
from .core.llm_client import LLMClient, LLMProvider, LLMResponse
from .parsers.repo_router import RepoRouter, RoutingResult
from .parsers.requirement_parser import (
    AcceptanceCriteria,
    Requirement,
    RequirementParser,
    VerificationMethod,
)

__all__ = [
    "__version__",
    "__author__",
    "ConfigLoader",
    "ProjectConfig",
    "LLMClient",
    "LLMProvider",
    "LLMResponse",
    "RequirementParser",
    "Requirement",
    "AcceptanceCriteria",
    "VerificationMethod",
    "RepoRouter",
    "RoutingResult",
]
