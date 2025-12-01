from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class TaskType(str, Enum):
    CODE = "code"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    REFACTOR = "refactor"
    DEBUG = "debug"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    OPTIMIZATION = "optimization"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LLMConfig(BaseModel):
    model: str = Field(..., description="Nom du modèle LLM")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    max_tokens: int = Field(default=8192, gt=0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)


class AgentConfig(BaseModel):
    agent_id: str
    role: str
    llm_config: LLMConfig
    tools: List[str] = Field(default_factory=list)
    permissions: Dict[str, bool] = Field(default_factory=dict)


class TaskRequest(BaseModel):
    task_type: TaskType
    description: str
    context: Optional[Dict[str, Any]] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    user_id: Optional[str] = None
    project_id: Optional[str] = None


class TaskResult(BaseModel):
    task_id: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    agent_used: Optional[str] = None
    cost: Optional[float] = None
    latency: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
