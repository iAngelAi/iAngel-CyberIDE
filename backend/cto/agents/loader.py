"""
Agent loader and configuration presets for CyberIDE CTO.

This module provides predefined agent configurations optimized for
different roles in the AI-powered development workflow.
"""

from typing import Dict, Optional

from backend.cto.schemas.task import AgentConfig, LLMConfig


# Base model used across all agents
_DEFAULT_MODEL = "claude-3-5-sonnet-20241022"


AGENT_PRESETS: Dict[str, AgentConfig] = {
    # ═══════════════════════════════════════════════════════════════════════════
    # CTO - Chief Technology Officer Agent
    # Orchestrates other agents, delegates tasks, and approves critical changes
    # ═══════════════════════════════════════════════════════════════════════════
    "agent-cto-001": AgentConfig(
        agent_id="agent-cto-001",
        role="cto",
        llm_config=LLMConfig(
            model=_DEFAULT_MODEL,
            temperature=0.4,
            max_tokens=8192,
            top_p=0.95,
        ),
        tools=["sub_agent", "memory_query"],
        permissions={
            "can_delegate": True,
            "can_approve": True,
        },
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Architect - System Architecture Agent
    # Designs system structure, evaluates architectural decisions, read-only access
    # ═══════════════════════════════════════════════════════════════════════════
    "agent-architect-001": AgentConfig(
        agent_id="agent-architect-001",
        role="architecte-principal",
        llm_config=LLMConfig(
            model=_DEFAULT_MODEL,
            temperature=0.6,
            max_tokens=16384,
            top_p=0.95,
        ),
        tools=["read_file", "memory_query"],
        permissions={
            "can_write_files": False,
        },
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FullStack Developer - Frontend & Backend Implementation
    # Implements features across the stack, can write files but no shell access
    # ═══════════════════════════════════════════════════════════════════════════
    "agent-fullstack-001": AgentConfig(
        agent_id="agent-fullstack-001",
        role="developpeur-fullstack",
        llm_config=LLMConfig(
            model=_DEFAULT_MODEL,
            temperature=0.2,
            max_tokens=16384,
            top_p=0.95,
        ),
        tools=["read_file", "write_file", "git"],
        permissions={
            "can_write_files": True,
            "can_execute_shell": False,
        },
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Backend Developer - API & Server-side Logic
    # Specialized in backend development, Python/FastAPI focused
    # ═══════════════════════════════════════════════════════════════════════════
    "agent-backend-001": AgentConfig(
        agent_id="agent-backend-001",
        role="developpeur-backend",
        llm_config=LLMConfig(
            model=_DEFAULT_MODEL,
            temperature=0.15,
            max_tokens=16384,
            top_p=0.95,
        ),
        tools=["read_file", "write_file"],
        permissions={
            "can_write_files": True,
        },
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MLOps Engineer - Machine Learning Operations
    # Manages ML pipelines, model deployment, requires shell access for training
    # ═══════════════════════════════════════════════════════════════════════════
    "agent-mlops-001": AgentConfig(
        agent_id="agent-mlops-001",
        role="ingenieur-mlops",
        llm_config=LLMConfig(
            model=_DEFAULT_MODEL,
            temperature=0.25,
            max_tokens=12288,
            top_p=0.95,
        ),
        tools=["read_file", "write_file", "shell_execute"],
        permissions={
            "can_write_files": True,
            "can_execute_shell": True,
        },
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DevOps Engineer - Infrastructure & CI/CD
    # Manages infrastructure, deployments, Docker, requires full shell access
    # ═══════════════════════════════════════════════════════════════════════════
    "agent-devops-001": AgentConfig(
        agent_id="agent-devops-001",
        role="ingenieur-devops",
        llm_config=LLMConfig(
            model=_DEFAULT_MODEL,
            temperature=0.1,
            max_tokens=12288,
            top_p=0.95,
        ),
        tools=["read_file", "write_file", "shell_execute"],
        permissions={
            "can_write_files": True,
            "can_execute_shell": True,
        },
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Security Engineer - Security Auditing & Vulnerability Assessment
    # Performs security audits, read-only to prevent accidental exposure
    # ═══════════════════════════════════════════════════════════════════════════
    "agent-security-001": AgentConfig(
        agent_id="agent-security-001",
        role="ingenieur-securite",
        llm_config=LLMConfig(
            model=_DEFAULT_MODEL,
            temperature=0.2,
            max_tokens=12288,
            top_p=0.95,
        ),
        tools=["read_file", "memory_query"],
        permissions={
            "can_write_files": False,
        },
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UX Coach - User Experience & Design Guidance
    # Provides UX feedback and recommendations, creative temperature for ideas
    # ═══════════════════════════════════════════════════════════════════════════
    "agent-ux-001": AgentConfig(
        agent_id="agent-ux-001",
        role="coach-ux",
        llm_config=LLMConfig(
            model=_DEFAULT_MODEL,
            temperature=0.7,
            max_tokens=8192,
            top_p=0.95,
        ),
        tools=["read_file", "memory_query"],
        permissions={
            "can_write_files": False,
        },
    ),
}


def get_agent_config(agent_id: str) -> AgentConfig:
    """
    Retrieve the configuration for an agent by its ID.
    
    Args:
        agent_id: Unique identifier of the agent (e.g., 'agent-cto-001').
    
    Returns:
        AgentConfig with the agent's LLM settings, tools, and permissions.
    
    Raises:
        KeyError: If no agent with the given ID exists in AGENT_PRESETS.
    
    Example:
        >>> config = get_agent_config("agent-fullstack-001")
        >>> config.role
        'developpeur-fullstack'
        >>> config.llm_config.temperature
        0.2
    """
    if agent_id not in AGENT_PRESETS:
        available_agents = ", ".join(sorted(AGENT_PRESETS.keys()))
        raise KeyError(
            f"Agent '{agent_id}' not found. "
            f"Available agents: {available_agents}"
        )
    
    return AGENT_PRESETS[agent_id]


def get_agent_by_role(role: str) -> Optional[AgentConfig]:
    """
    Find an agent configuration by its role name.
    
    Args:
        role: Role identifier (e.g., 'developpeur-fullstack', 'cto').
    
    Returns:
        AgentConfig if found, None otherwise.
    
    Example:
        >>> config = get_agent_by_role("cto")
        >>> config.agent_id
        'agent-cto-001'
    """
    for agent_config in AGENT_PRESETS.values():
        if agent_config.role == role:
            return agent_config
    return None


def list_agents_with_permission(permission: str, value: bool = True) -> list[AgentConfig]:
    """
    List all agents that have a specific permission.
    
    Args:
        permission: Permission key to check (e.g., 'can_write_files').
        value: Expected value of the permission (default: True).
    
    Returns:
        List of AgentConfig objects matching the permission criteria.
    
    Example:
        >>> writers = list_agents_with_permission("can_write_files")
        >>> len(writers)
        4
    """
    return [
        config for config in AGENT_PRESETS.values()
        if config.permissions.get(permission) == value
    ]
