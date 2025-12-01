"""
Agent configuration loader for CyberIDE CTO System.

This module provides preset configurations for the 13 specialized AI agents
and functions to retrieve and list available agent configurations.
"""

from typing import Dict, List

from backend.cto.schemas.task import AgentConfig, LLMConfig


# =============================================================================
# AGENT PRESETS
# =============================================================================
# Dictionary containing configurations for all 13 specialized agents.
# Each agent has unique temperature, max_tokens, tools, and permissions
# tailored to their specific role in the system.
# =============================================================================

AGENT_PRESETS: Dict[str, AgentConfig] = {
    # -------------------------------------------------------------------------
    # CTO - Chief Technology Officer
    # High-level strategic decisions, orchestrates other agents
    # -------------------------------------------------------------------------
    "cto": AgentConfig(
        agent_id="cto",
        role="Chief Technology Officer",
        description="Orchestrates all agents, makes high-level technical decisions, "
        "and ensures alignment with project goals.",
        llm_config=LLMConfig(
            model="claude-3-5-sonnet-20241022",
            temperature=0.4,
            max_tokens=8192,
        ),
        tools=[
            "delegate_task",
            "review_architecture",
            "approve_changes",
            "analyze_codebase",
            "strategic_planning",
        ],
        permissions={
            "can_delegate": True,
            "can_approve": True,
            "can_execute": True,
            "can_modify_config": True,
            "can_access_all_agents": True,
        },
    ),
    # -------------------------------------------------------------------------
    # Architect - System Architecture Expert
    # Designs system structure, patterns, and high-level decisions
    # -------------------------------------------------------------------------
    "architect": AgentConfig(
        agent_id="architect",
        role="Software Architect",
        description="Designs system architecture, defines patterns, and ensures "
        "scalability and maintainability of the codebase.",
        llm_config=LLMConfig(
            model="claude-3-5-sonnet-20241022",
            temperature=0.6,
            max_tokens=8192,
        ),
        tools=[
            "analyze_architecture",
            "generate_diagrams",
            "review_patterns",
            "evaluate_dependencies",
            "propose_refactoring",
        ],
        permissions={
            "can_delegate": True,
            "can_approve": True,
            "can_execute": False,
            "can_modify_architecture": True,
            "can_review_code": True,
        },
    ),
    # -------------------------------------------------------------------------
    # FullStackDev - Full Stack Developer
    # Implements features across frontend and backend
    # -------------------------------------------------------------------------
    "fullstack_dev": AgentConfig(
        agent_id="fullstack_dev",
        role="Full Stack Developer",
        description="Implements features across the entire stack, from React frontend "
        "to FastAPI backend, ensuring seamless integration.",
        llm_config=LLMConfig(
            model="claude-3-5-sonnet-20241022",
            temperature=0.2,
            max_tokens=16384,
        ),
        tools=[
            "write_code",
            "read_file",
            "edit_file",
            "run_tests",
            "debug_code",
            "search_codebase",
        ],
        permissions={
            "can_delegate": False,
            "can_approve": False,
            "can_execute": True,
            "can_write_code": True,
            "can_run_commands": True,
        },
    ),
    # -------------------------------------------------------------------------
    # BackendDev - Backend Developer
    # Specializes in Python/FastAPI backend development
    # -------------------------------------------------------------------------
    "backend_dev": AgentConfig(
        agent_id="backend_dev",
        role="Backend Developer",
        description="Specializes in Python and FastAPI development, API design, "
        "database operations, and backend optimization.",
        llm_config=LLMConfig(
            model="claude-3-5-sonnet-20241022",
            temperature=0.15,
            max_tokens=16384,
        ),
        tools=[
            "write_code",
            "read_file",
            "edit_file",
            "run_tests",
            "analyze_api",
            "database_operations",
        ],
        permissions={
            "can_delegate": False,
            "can_approve": False,
            "can_execute": True,
            "can_write_code": True,
            "can_access_database": True,
        },
    ),
    # -------------------------------------------------------------------------
    # FrontendDev - Frontend Developer
    # Specializes in React/TypeScript frontend development
    # -------------------------------------------------------------------------
    "frontend_dev": AgentConfig(
        agent_id="frontend_dev",
        role="Frontend Developer",
        description="Specializes in React, TypeScript, and Three.js development, "
        "creating beautiful and performant user interfaces.",
        llm_config=LLMConfig(
            model="claude-3-5-sonnet-20241022",
            temperature=0.25,
            max_tokens=16384,
        ),
        tools=[
            "write_code",
            "read_file",
            "edit_file",
            "run_tests",
            "analyze_components",
            "style_optimization",
        ],
        permissions={
            "can_delegate": False,
            "can_approve": False,
            "can_execute": True,
            "can_write_code": True,
            "can_modify_styles": True,
        },
    ),
    # -------------------------------------------------------------------------
    # MLOps - Machine Learning Operations Engineer
    # Manages ML pipelines, model deployment, and optimization
    # -------------------------------------------------------------------------
    "mlops": AgentConfig(
        agent_id="mlops",
        role="MLOps Engineer",
        description="Manages machine learning pipelines, model training, deployment, "
        "and optimization of AI/ML workflows.",
        llm_config=LLMConfig(
            model="claude-3-5-sonnet-20241022",
            temperature=0.25,
            max_tokens=8192,
        ),
        tools=[
            "analyze_models",
            "optimize_pipeline",
            "monitor_metrics",
            "deploy_model",
            "evaluate_performance",
        ],
        permissions={
            "can_delegate": False,
            "can_approve": False,
            "can_execute": True,
            "can_deploy_models": True,
            "can_access_gpu": True,
        },
    ),
    # -------------------------------------------------------------------------
    # DevOps - DevOps Engineer
    # Manages infrastructure, CI/CD, and deployment
    # -------------------------------------------------------------------------
    "devops": AgentConfig(
        agent_id="devops",
        role="DevOps Engineer",
        description="Manages infrastructure, CI/CD pipelines, Docker configurations, "
        "and ensures reliable deployment processes.",
        llm_config=LLMConfig(
            model="claude-3-5-sonnet-20241022",
            temperature=0.1,
            max_tokens=8192,
        ),
        tools=[
            "manage_docker",
            "configure_ci_cd",
            "deploy_services",
            "monitor_infrastructure",
            "manage_secrets",
        ],
        permissions={
            "can_delegate": False,
            "can_approve": False,
            "can_execute": True,
            "can_deploy": True,
            "can_access_infrastructure": True,
        },
    ),
    # -------------------------------------------------------------------------
    # Security - Security Engineer
    # Ensures code security, audits, and compliance
    # -------------------------------------------------------------------------
    "security": AgentConfig(
        agent_id="security",
        role="Security Engineer",
        description="Audits code for vulnerabilities, ensures security best practices, "
        "and manages security compliance.",
        llm_config=LLMConfig(
            model="claude-3-5-sonnet-20241022",
            temperature=0.2,
            max_tokens=8192,
        ),
        tools=[
            "security_audit",
            "vulnerability_scan",
            "review_permissions",
            "analyze_dependencies",
            "compliance_check",
        ],
        permissions={
            "can_delegate": False,
            "can_approve": True,
            "can_execute": False,
            "can_audit": True,
            "can_block_deployment": True,
        },
    ),
    # -------------------------------------------------------------------------
    # QA - Quality Assurance Engineer
    # Manages testing strategies and quality assurance
    # -------------------------------------------------------------------------
    "qa": AgentConfig(
        agent_id="qa",
        role="QA Engineer",
        description="Designs and implements testing strategies, writes tests, "
        "and ensures software quality through comprehensive QA processes.",
        llm_config=LLMConfig(
            model="claude-3-5-sonnet-20241022",
            temperature=0.3,
            max_tokens=8192,
        ),
        tools=[
            "write_tests",
            "run_tests",
            "analyze_coverage",
            "generate_test_report",
            "regression_testing",
        ],
        permissions={
            "can_delegate": False,
            "can_approve": False,
            "can_execute": True,
            "can_write_tests": True,
            "can_run_tests": True,
        },
    ),
    # -------------------------------------------------------------------------
    # UXCoach - UX/UI Coach
    # Guides UI/UX decisions and user experience improvements
    # -------------------------------------------------------------------------
    "ux_coach": AgentConfig(
        agent_id="ux_coach",
        role="UX/UI Coach",
        description="Guides user experience decisions, reviews UI designs, "
        "and ensures intuitive and accessible interfaces.",
        llm_config=LLMConfig(
            model="claude-3-5-sonnet-20241022",
            temperature=0.7,
            max_tokens=4096,
        ),
        tools=[
            "review_ui",
            "analyze_ux_flow",
            "accessibility_check",
            "design_suggestions",
            "user_journey_mapping",
        ],
        permissions={
            "can_delegate": False,
            "can_approve": False,
            "can_execute": False,
            "can_review_design": True,
            "can_suggest_improvements": True,
        },
    ),
    # -------------------------------------------------------------------------
    # ProductOwner - Product Owner
    # Manages product requirements and priorities
    # -------------------------------------------------------------------------
    "product_owner": AgentConfig(
        agent_id="product_owner",
        role="Product Owner",
        description="Manages product requirements, prioritizes features, "
        "and ensures alignment with business objectives.",
        llm_config=LLMConfig(
            model="claude-3-5-sonnet-20241022",
            temperature=0.5,
            max_tokens=4096,
        ),
        tools=[
            "manage_backlog",
            "prioritize_features",
            "write_user_stories",
            "analyze_requirements",
            "stakeholder_communication",
        ],
        permissions={
            "can_delegate": True,
            "can_approve": True,
            "can_execute": False,
            "can_prioritize": True,
            "can_define_requirements": True,
        },
    ),
    # -------------------------------------------------------------------------
    # TechWriter - Technical Writer
    # Creates and maintains documentation
    # -------------------------------------------------------------------------
    "tech_writer": AgentConfig(
        agent_id="tech_writer",
        role="Technical Writer",
        description="Creates and maintains technical documentation, API docs, "
        "user guides, and ensures documentation accuracy.",
        llm_config=LLMConfig(
            model="claude-3-5-sonnet-20241022",
            temperature=0.4,
            max_tokens=8192,
        ),
        tools=[
            "write_documentation",
            "generate_api_docs",
            "review_docs",
            "create_tutorials",
            "maintain_changelog",
        ],
        permissions={
            "can_delegate": False,
            "can_approve": False,
            "can_execute": False,
            "can_write_docs": True,
            "can_publish_docs": True,
        },
    ),
    # -------------------------------------------------------------------------
    # 3DGraphics - 3D Graphics Engineer
    # Specializes in Three.js, WebGL, and 3D visualization
    # -------------------------------------------------------------------------
    "3d_graphics": AgentConfig(
        agent_id="3d_graphics",
        role="3D Graphics Engineer",
        description="Specializes in Three.js, WebGL, shaders, and 3D visualization "
        "with focus on 60 FPS performance optimization.",
        llm_config=LLMConfig(
            model="claude-3-5-sonnet-20241022",
            temperature=0.3,
            max_tokens=16384,
        ),
        tools=[
            "write_shaders",
            "optimize_rendering",
            "analyze_performance",
            "create_3d_models",
            "debug_webgl",
        ],
        permissions={
            "can_delegate": False,
            "can_approve": False,
            "can_execute": True,
            "can_write_shaders": True,
            "can_optimize_gpu": True,
        },
    ),
}


def get_agent_config(agent_id: str) -> AgentConfig:
    """
    Retrieve the configuration for a specific agent.

    Args:
        agent_id: The unique identifier of the agent.

    Returns:
        AgentConfig: The configuration for the requested agent.

    Raises:
        ValueError: If the agent_id is not found in AGENT_PRESETS.

    Example:
        >>> config = get_agent_config("cto")
        >>> print(config.role)
        'Chief Technology Officer'
    """
    if agent_id not in AGENT_PRESETS:
        available_agents = ", ".join(sorted(AGENT_PRESETS.keys()))
        raise ValueError(
            f"Agent '{agent_id}' not found. Available agents: {available_agents}"
        )
    return AGENT_PRESETS[agent_id]


def list_agents() -> List[str]:
    """
    List all available agent identifiers.

    Returns:
        List[str]: A sorted list of all agent IDs in AGENT_PRESETS.

    Example:
        >>> agents = list_agents()
        >>> print(agents)
        ['3d_graphics', 'architect', 'backend_dev', ...]
    """
    return sorted(AGENT_PRESETS.keys())
