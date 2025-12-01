"""
Task and Agent configuration schemas for CyberIDE CTO System.

This module defines Pydantic models for agent configurations used
throughout the CTO agent orchestration system.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """
    Configuration for the LLM (Large Language Model) used by an agent.

    Attributes:
        model: The model identifier (e.g., "claude-3-5-sonnet-20241022")
        temperature: Creativity/randomness level (0.0-1.0)
        max_tokens: Maximum tokens in the response
        top_p: Nucleus sampling parameter (optional)
        stop_sequences: Sequences that stop generation (optional)
    """

    model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="The LLM model identifier",
    )
    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Creativity level (0.0 = deterministic, 1.0 = creative)",
    )
    max_tokens: int = Field(
        default=4096,
        ge=1,
        le=200000,
        description="Maximum tokens in the response",
    )
    top_p: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling parameter",
    )
    stop_sequences: Optional[List[str]] = Field(
        default=None,
        description="Sequences that stop generation",
    )


class AgentConfig(BaseModel):
    """
    Configuration for a specialized AI agent in the CTO system.

    Each agent has a unique role, specific LLM settings, tools, and permissions
    that define its capabilities and constraints within the system.

    Attributes:
        agent_id: Unique identifier for the agent
        role: Human-readable role description
        llm_config: LLM configuration for this agent
        tools: List of tools this agent can use
        permissions: Dictionary of permission flags
        description: Optional detailed description of the agent's purpose
        system_prompt: Optional custom system prompt for the agent
    """

    agent_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for the agent",
    )
    role: str = Field(
        ...,
        min_length=1,
        description="Human-readable role description",
    )
    llm_config: LLMConfig = Field(
        default_factory=LLMConfig,
        description="LLM configuration for this agent",
    )
    tools: List[str] = Field(
        default_factory=list,
        description="List of tools this agent can use",
    )
    permissions: Dict[str, bool] = Field(
        default_factory=dict,
        description="Dictionary of permission flags",
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the agent's purpose",
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="Custom system prompt for the agent",
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "agent_id": "cto",
                "role": "Chief Technology Officer",
                "llm_config": {
                    "model": "claude-3-5-sonnet-20241022",
                    "temperature": 0.4,
                    "max_tokens": 8192,
                },
                "tools": ["code_review", "architecture_analysis", "delegation"],
                "permissions": {
                    "can_delegate": True,
                    "can_approve": True,
                    "can_execute": True,
                },
            }
        }
