"""
Task schemas for CyberIDE CTO module.

This module defines Pydantic models for AI-powered task orchestration,
including task types, priorities, statuses, LLM configurations, and agent configs.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class TaskType(str, Enum):
    """Types of tasks that can be delegated to AI agents."""
    
    CODE = "code"
    """Code generation, implementation, and modifications."""
    
    ARCHITECTURE = "architecture"
    """System design, module structure, and architectural decisions."""
    
    SECURITY = "security"
    """Security audits, vulnerability assessments, and fixes."""
    
    REFACTOR = "refactor"
    """Code refactoring for improved maintainability and performance."""
    
    DEBUG = "debug"
    """Bug investigation, diagnosis, and resolution."""
    
    DOCUMENTATION = "documentation"
    """Documentation generation, updates, and maintenance."""
    
    TESTING = "testing"
    """Test creation, test coverage improvements, and test fixes."""
    
    OPTIMIZATION = "optimization"
    """Performance optimization and resource efficiency improvements."""


class TaskPriority(str, Enum):
    """Priority levels for task execution ordering."""
    
    LOW = "low"
    """Non-urgent tasks, can be deferred."""
    
    MEDIUM = "medium"
    """Standard priority, normal execution order."""
    
    HIGH = "high"
    """Important tasks requiring prompt attention."""
    
    CRITICAL = "critical"
    """Urgent tasks requiring immediate execution."""


class TaskStatus(str, Enum):
    """Execution status of a task."""
    
    PENDING = "pending"
    """Task is queued and waiting for execution."""
    
    IN_PROGRESS = "in_progress"
    """Task is currently being processed by an agent."""
    
    COMPLETED = "completed"
    """Task has been successfully completed."""
    
    FAILED = "failed"
    """Task execution failed with an error."""
    
    CANCELLED = "cancelled"
    """Task was cancelled before completion."""


class LLMConfig(BaseModel):
    """
    Configuration for Language Model settings.
    
    Controls the behavior of the AI model used by agents.
    """
    
    model: str = Field(
        ...,
        description="Identifier of the LLM model to use (e.g., 'claude-3-opus', 'gpt-4')",
        examples=["claude-3-opus", "claude-3-sonnet", "gpt-4-turbo"]
    )
    
    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0.0-2.0). Lower values are more deterministic."
    )
    
    max_tokens: int = Field(
        default=8192,
        gt=0,
        description="Maximum number of tokens in the response."
    )
    
    top_p: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling parameter (0.0-1.0). Controls diversity of outputs."
    )
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Ensure temperature is within valid range."""
        return max(0.0, min(2.0, v))
    
    @field_validator('top_p')
    @classmethod
    def validate_top_p(cls, v: float) -> float:
        """Ensure top_p is within valid range."""
        return max(0.0, min(1.0, v))


class AgentConfig(BaseModel):
    """
    Configuration for an AI agent.
    
    Defines the agent's identity, capabilities, and permissions.
    """
    
    agent_id: str = Field(
        ...,
        description="Unique identifier for the agent.",
        examples=["agent-fullstack-001", "agent-security-002"]
    )
    
    role: str = Field(
        ...,
        description="Role or specialization of the agent.",
        examples=["developpeur-fullstack", "ingenieur-qa-automation", "architecte-principal"]
    )
    
    llm_config: LLMConfig = Field(
        ...,
        description="LLM configuration for this agent."
    )
    
    tools: List[str] = Field(
        default_factory=list,
        description="List of tool identifiers the agent can use.",
        examples=[["read_file", "write_file", "shell_execute", "search_code"]]
    )
    
    permissions: Dict[str, bool] = Field(
        default_factory=dict,
        description="Permission flags for agent capabilities.",
        examples=[{"can_write_files": True, "can_execute_shell": False, "can_access_network": True}]
    )


class TaskRequest(BaseModel):
    """
    Request to create and execute a new task.
    
    Submitted by users or other systems to initiate task execution.
    """
    
    task_type: TaskType = Field(
        ...,
        description="Type of task to execute."
    )
    
    description: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Detailed description of the task to accomplish."
    )
    
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context for task execution (file paths, code snippets, etc.)."
    )
    
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Priority level for task scheduling."
    )
    
    user_id: str = Field(
        ...,
        description="Identifier of the user requesting the task."
    )
    
    project_id: str = Field(
        ...,
        description="Identifier of the project this task belongs to."
    )


class TaskResult(BaseModel):
    """
    Result of a completed or failed task.
    
    Contains execution metrics, output, and status information.
    """
    
    task_id: str = Field(
        ...,
        description="Unique identifier of the executed task."
    )
    
    status: TaskStatus = Field(
        ...,
        description="Final status of the task execution."
    )
    
    result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Output data from successful task execution."
    )
    
    error: Optional[str] = Field(
        default=None,
        description="Error message if the task failed."
    )
    
    agent_used: str = Field(
        ...,
        description="Identifier of the agent that processed the task."
    )
    
    cost: float = Field(
        ...,
        ge=0.0,
        description="Estimated cost of task execution (in API credits or currency)."
    )
    
    latency: float = Field(
        ...,
        ge=0.0,
        description="Total execution time in seconds."
    )
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the task was created."
    )
    
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the task was completed (None if still pending)."
    )
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
