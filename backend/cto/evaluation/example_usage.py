"""
Example usage of the Agent Evaluator system.

This script demonstrates how to use the LLM-as-a-Judge evaluation system
to monitor agent conformity to their specific rules.

Usage:
    python -m backend.cto.evaluation.example_usage
"""

import json
from pathlib import Path

from backend.cto.evaluation import (
    AgentEvaluator,
    AgentPromptInput,
    ConversationMessage,
)


def example_basic_evaluation():
    """
    Basic example: Evaluate a single conversation.
    
    This example shows how to evaluate an agent response against
    the rules defined in its system prompt.
    """
    print("=" * 80)
    print("Example 1: Basic Evaluation")
    print("=" * 80)
    
    # Initialize evaluator with mock provider (for testing)
    # In production, use: evaluator = AgentEvaluator(llm_provider="openai", model="gpt-4", api_key="...")
    evaluator = AgentEvaluator(llm_provider="mock", model="test-model")
    
    # Define agent prompt (in practice, load from file)
    agent_prompt = AgentPromptInput(
        agent_name="Architecte Principal",
        prompt_content="""
        <architect_principal>
          <coding_standards>
            <python>
              Tu refuses toute solution qui contourne ces règles (pas de « quick fix » non testé ou non typé).
            </python>
            <typescript>
              Tu assumes que tout code TypeScript est compilé en mode strict complet (aucun any toléré).
            </typescript>
          </coding_standards>
        </architect_principal>
        """
    )
    
    # Define conversation to evaluate
    conversation = [
        ConversationMessage(
            role="user",
            content="We need to ship this feature quickly. Can you help?"
        ),
        ConversationMessage(
            role="agent",
            content=(
                "I understand the urgency. However, I'll implement a proper solution "
                "with strict typing and comprehensive tests. Using quick fixes would "
                "create technical debt. Let me design a clean architecture instead."
            )
        ),
    ]
    
    # Evaluate the conversation
    result = evaluator.evaluate(
        agent_prompt=agent_prompt,
        conversation=conversation
    )
    
    # Display results
    print(f"\nAgent: {result.agent_name}")
    print(f"Rule Adherence Score: {result.rule_adherence_score:.1f}/100")
    print(f"Total Rules Checked: {result.total_rules_checked}")
    print(f"Violations Detected: {len(result.violations)}")
    print(f"Summary: {result.summary}")
    
    if result.violations:
        print("\nViolations:")
        for i, violation in enumerate(result.violations, 1):
            print(f"\n  {i}. {violation.rule_description}")
            print(f"     Severity: {violation.severity}")
            print(f"     Issue: {violation.violation_description}")


def example_with_violations():
    """
    Example with violations: Evaluate a conversation that violates rules.
    
    This demonstrates how the evaluator detects rule violations.
    """
    print("\n" + "=" * 80)
    print("Example 2: Detecting Violations")
    print("=" * 80)
    
    evaluator = AgentEvaluator(llm_provider="mock")
    
    agent_prompt = AgentPromptInput(
        agent_name="Backend Engineer",
        prompt_content="""
        <backend_engineer>
          <coding_standards>
            <common_rules>
              Tu refuses toute solution qui utilise des quick fixes.
            </common_rules>
            <typescript>
              Aucun any toléré - utilise unknown avec type guards.
            </typescript>
          </coding_standards>
        </backend_engineer>
        """
    )
    
    # Conversation with rule violations
    conversation = [
        ConversationMessage(
            role="user",
            content="Fix this TypeScript error quickly"
        ),
        ConversationMessage(
            role="agent",
            content=(
                "I'll add a quick fix by casting to 'any' type: "
                "const data: any = input; "
                "This will make the error go away fast."
            )
        ),
    ]
    
    result = evaluator.evaluate(
        agent_prompt=agent_prompt,
        conversation=conversation
    )
    
    print(f"\nAgent: {result.agent_name}")
    print(f"Rule Adherence Score: {result.rule_adherence_score:.1f}/100")
    print(f"Violations: {len(result.violations)}")
    
    for i, violation in enumerate(result.violations, 1):
        print(f"\n  Violation {i}:")
        print(f"    Rule: {violation.rule_description[:60]}...")
        print(f"    Severity: {violation.severity}")
        print(f"    Evidence: {violation.evidence[:100] if violation.evidence else 'N/A'}...")


def example_load_from_file():
    """
    Example: Load agent prompt from file.
    
    This shows how to evaluate using actual agent specification files.
    """
    print("\n" + "=" * 80)
    print("Example 3: Loading from File")
    print("=" * 80)
    
    # Path to agent specification file
    project_root = Path(__file__).parent.parent.parent.parent
    agent_file = project_root / "docs" / "archive" / "legacy_agents" / "architecte-principal.agent.md"
    
    if not agent_file.exists():
        print(f"\nSkipping: Agent file not found at {agent_file}")
        return
    
    evaluator = AgentEvaluator(llm_provider="mock")
    
    # Simple way: pass file path directly
    conversation = [
        ConversationMessage(
            role="user",
            content="Can you review this architecture?"
        ),
        ConversationMessage(
            role="agent",
            content=(
                "I'll review the architecture carefully. "
                "Let me analyze the design patterns, scalability considerations, "
                "and ensure we follow strict coding standards. "
                "No shortcuts or quick fixes - we need a robust solution."
            )
        ),
    ]
    
    result = evaluator.evaluate(
        agent_prompt=str(agent_file),
        conversation=conversation
    )
    
    print(f"\nAgent: {result.agent_name}")
    print(f"Score: {result.rule_adherence_score:.1f}/100")
    print(f"Rules Checked: {result.total_rules_checked}")
    print(f"Summary: {result.summary}")


def example_json_output():
    """
    Example: Generate JSON output for monitoring integration.
    
    This shows how to export evaluation results as JSON for
    integration with monitoring systems.
    """
    print("\n" + "=" * 80)
    print("Example 4: JSON Output for Monitoring")
    print("=" * 80)
    
    evaluator = AgentEvaluator(llm_provider="mock")
    
    agent_prompt = AgentPromptInput(
        agent_name="MLOps Engineer",
        prompt_content="""
        <mlops_engineer>
          <mlops_principles>
            <principle index="1" label="Industrialisation robuste">
              Tu refuses de déployer un modèle sans observabilité, plan de rollback et stratégie de réentraînement.
            </principle>
          </mlops_principles>
        </mlops_engineer>
        """
    )
    
    conversation = [
        ConversationMessage(
            role="user",
            content="Deploy this model to production"
        ),
        ConversationMessage(
            role="agent",
            content=(
                "I'll deploy the model with comprehensive monitoring, "
                "automated rollback capabilities, and a retraining pipeline. "
                "We need observability in place before going live."
            )
        ),
    ]
    
    # Generate JSON output
    json_output = evaluator.evaluate_to_json(
        agent_prompt=agent_prompt,
        conversation=conversation
    )
    
    print("\nJSON Output (formatted):")
    print("-" * 80)
    
    # Pretty print the JSON
    parsed = json.loads(json_output)
    print(json.dumps(parsed, indent=2))
    
    print("\nThis JSON can be ingested by monitoring systems like:")
    print("  - Prometheus (via custom exporter)")
    print("  - Grafana (as data source)")
    print("  - ELK Stack (for log analysis)")
    print("  - DataDog, New Relic, etc.")


def example_batch_evaluation():
    """
    Example: Batch evaluation of multiple conversations.
    
    This shows how to evaluate multiple agent interactions
    and aggregate the results.
    """
    print("\n" + "=" * 80)
    print("Example 5: Batch Evaluation")
    print("=" * 80)
    
    evaluator = AgentEvaluator(llm_provider="mock")
    
    agent_prompt = AgentPromptInput(
        agent_name="Test Agent",
        prompt_content="""
        <test_agent>
          <mandates>
            <mandate index="1">Tu dois toujours valider les entrées.</mandate>
            <mandate index="2">Tu refuses les quick fixes.</mandate>
          </mandates>
        </test_agent>
        """
    )
    
    # Multiple conversations to evaluate
    conversations = [
        [
            ConversationMessage(role="user", content="Fix this bug"),
            ConversationMessage(role="agent", content="I'll implement a proper fix with tests"),
        ],
        [
            ConversationMessage(role="user", content="Make this faster"),
            ConversationMessage(role="agent", content="Let me add a quick fix to bypass validation"),
        ],
        [
            ConversationMessage(role="user", content="Add this feature"),
            ConversationMessage(role="agent", content="I'll design it properly with validation"),
        ],
    ]
    
    results = []
    for i, conversation in enumerate(conversations, 1):
        result = evaluator.evaluate(
            agent_prompt=agent_prompt,
            conversation=conversation
        )
        results.append(result)
        print(f"\nConversation {i}:")
        print(f"  Score: {result.rule_adherence_score:.1f}/100")
        print(f"  Violations: {len(result.violations)}")
    
    # Calculate aggregate metrics
    avg_score = sum(r.rule_adherence_score for r in results) / len(results)
    total_violations = sum(len(r.violations) for r in results)
    
    print("\n" + "-" * 80)
    print("Aggregate Metrics:")
    print(f"  Total Conversations: {len(results)}")
    print(f"  Average Score: {avg_score:.1f}/100")
    print(f"  Total Violations: {total_violations}")
    print(f"  Pass Rate (>75): {sum(1 for r in results if r.rule_adherence_score > 75)}/{len(results)}")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  Agent Evaluator - LLM-as-a-Judge Examples".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    try:
        example_basic_evaluation()
        example_with_violations()
        example_load_from_file()
        example_json_output()
        example_batch_evaluation()
        
        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Configure LLM provider (OpenAI, Anthropic, or Google)")
        print("  2. Integrate with your monitoring system")
        print("  3. Set up automated evaluation in CI/CD pipeline")
        print("  4. Define thresholds for acceptable scores")
        print()
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
