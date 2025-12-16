"""
Agent evaluation module for LLM-as-a-Judge conformity monitoring.

This module provides tools to evaluate agent responses against their
specific rules and constraints defined in their system prompts.
"""

from backend.cto.evaluation.agent_evaluator import (
    AgentEvaluator,
    AgentEvaluatorError,
    EvaluationError,
    LLMProviderError,
    RuleExtractionError,
)
from backend.cto.evaluation.models import (
    AgentPromptInput,
    ConversationMessage,
    EvaluationResult,
    ExtractedRule,
    RuleViolation,
)

__all__ = [
    # Main evaluator
    "AgentEvaluator",
    # Exceptions
    "AgentEvaluatorError",
    "EvaluationError",
    "LLMProviderError",
    "RuleExtractionError",
    # Data models
    "AgentPromptInput",
    "ConversationMessage",
    "EvaluationResult",
    "ExtractedRule",
    "RuleViolation",
]
