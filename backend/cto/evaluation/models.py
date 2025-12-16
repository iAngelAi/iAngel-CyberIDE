"""
Pydantic models for Agent Evaluation System.

This module defines type-safe data structures for evaluating agent conformity
to their specific rules using LLM-as-a-Judge methodology.

Conformité: 
- Respects protocol 02-AUDIT-FIRST with comprehensive validation
- Respects protocol 04-TYPING-STRICT with Pydantic V2 strict typing
- No PII in evaluation data
"""

from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ConversationMessage(BaseModel):
    """
    Single message in a conversation history.
    
    Represents either a user request or an agent response.
    """
    
    role: Literal["user", "agent", "assistant", "system"] = Field(
        ...,
        description="Role of the message sender"
    )
    
    content: str = Field(
        ...,
        min_length=1,
        max_length=100000,
        description="Content of the message"
    )
    
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the message was sent"
    )
    
    @field_validator('timestamp')
    @classmethod
    def ensure_utc_timezone(cls, v: datetime) -> datetime:
        """Ensure all timestamps are in UTC timezone."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)


class RuleViolation(BaseModel):
    """
    Detected violation of agent-specific rules.
    
    Contains details about what rule was violated and supporting evidence.
    """
    
    rule_description: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Description of the rule that was violated"
    )
    
    violation_description: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Explanation of how the rule was violated"
    )
    
    severity: Literal["low", "medium", "high", "critical"] = Field(
        ...,
        description="Severity level of the violation"
    )
    
    evidence: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Specific text from the agent response showing the violation"
    )
    
    suggested_correction: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Suggested way to correct this violation"
    )


class ExtractedRule(BaseModel):
    """
    Rule extracted from agent system prompt.
    
    Represents a specific constraint or guideline the agent must follow.
    """
    
    rule_type: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Type/category of the rule (e.g., 'coding_standards', 'workflow')"
    )
    
    rule_text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Full text of the rule"
    )
    
    is_mandatory: bool = Field(
        default=True,
        description="Whether this rule is mandatory (vs. recommended)"
    )
    
    context: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Additional context about when/how this rule applies"
    )


class EvaluationResult(BaseModel):
    """
    Complete evaluation result for an agent conversation.
    
    Contains the rule adherence score, detected violations, and metadata.
    Used for integration with monitoring systems.
    """
    
    agent_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the agent being evaluated (e.g., 'Architecte Principal')"
    )
    
    agent_version: str = Field(
        default="1.0.0",
        pattern=r"^\d+\.\d+\.\d+$",
        description="Version of the agent specification"
    )
    
    rule_adherence_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Overall rule adherence score (0-100, higher is better)"
    )
    
    total_rules_checked: int = Field(
        ...,
        ge=0,
        description="Total number of rules evaluated"
    )
    
    violations: List[RuleViolation] = Field(
        default_factory=list,
        description="List of detected rule violations"
    )
    
    evaluation_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when evaluation was performed"
    )
    
    evaluator_model: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="LLM model used for evaluation (e.g., 'gpt-4', 'claude-3-opus')"
    )
    
    conversation_length: int = Field(
        ...,
        ge=1,
        description="Number of messages in the evaluated conversation"
    )
    
    metadata: Optional[Dict[str, str | int | float | bool]] = Field(
        default=None,
        description="Additional metadata about the evaluation (no PII)"
    )
    
    summary: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Human-readable summary of the evaluation"
    )
    
    @field_validator('evaluation_timestamp')
    @classmethod
    def ensure_utc_timezone(cls, v: datetime) -> datetime:
        """Ensure all timestamps are in UTC timezone."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)
    
    @field_validator('metadata')
    @classmethod
    def validate_metadata_no_pii(
        cls, 
        v: Optional[Dict[str, str | int | float | bool]]
    ) -> Optional[Dict[str, str | int | float | bool]]:
        """
        Validate that metadata doesn't contain PII.
        
        Blocked keys: email, name, username, password, token, key, secret
        """
        if v is None:
            return v
        
        forbidden_keys = {
            'email', 'name', 'username', 'password', 
            'token', 'key', 'secret', 'api_key',
            'user_id', 'client_id', 'session_id'
        }
        
        for key in v.keys():
            if key.lower() in forbidden_keys:
                raise ValueError(
                    f"Metadata key '{key}' is forbidden as it may contain PII. "
                    f"Use anonymized identifiers instead."
                )
        
        return v
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class AgentPromptInput(BaseModel):
    """
    Input containing agent system prompt for rule extraction.
    
    Can be provided as file path or direct content.
    """
    
    agent_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the agent"
    )
    
    prompt_content: Optional[str] = Field(
        default=None,
        max_length=100000,
        description="Full content of the agent system prompt (if provided directly)"
    )
    
    prompt_file_path: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Path to the agent system prompt file (if loading from file)"
    )
    
    @field_validator('prompt_content', 'prompt_file_path')
    @classmethod
    def at_least_one_source(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure at least one of prompt_content or prompt_file_path is provided."""
        # This validation happens per field, so we check in the model validator instead
        return v
    
    def __init__(self, **data):
        """Validate that at least one source is provided."""
        super().__init__(**data)
        if not self.prompt_content and not self.prompt_file_path:
            raise ValueError(
                "Either 'prompt_content' or 'prompt_file_path' must be provided"
            )
