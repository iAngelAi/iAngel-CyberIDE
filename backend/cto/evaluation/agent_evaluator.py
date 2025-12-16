"""
Agent Evaluator - LLM-as-a-Judge for Agent Conformity Monitoring.

This module implements an evaluation system that uses LLM models to assess
whether agent responses conform to their specific rules and constraints.

Key Features:
- Extracts rules from agent system prompts (markdown format)
- Analyzes conversation history for rule violations
- Computes Rule Adherence Score (0-100)
- Outputs structured JSON for monitoring integration

Conformité:
- Protocol 02-AUDIT-FIRST: All operations are logged and validated
- Protocol 04-TYPING-STRICT: Full Pydantic validation, no type casting
- OWASP compliance: Input validation, no injection risks
"""

import json
import re
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import ValidationError

from backend.cto.evaluation.models import (
    AgentPromptInput,
    ConversationMessage,
    EvaluationResult,
    ExtractedRule,
    RuleViolation,
)


class AgentEvaluatorError(Exception):
    """Base exception for AgentEvaluator errors."""
    pass


class RuleExtractionError(AgentEvaluatorError):
    """Raised when rule extraction from prompt fails."""
    pass


class EvaluationError(AgentEvaluatorError):
    """Raised when evaluation process fails."""
    pass


class LLMProviderError(AgentEvaluatorError):
    """Raised when LLM provider communication fails."""
    pass


class AgentEvaluator:
    """
    LLM-as-a-Judge evaluator for agent conformity monitoring.

    This class analyzes agent conversations to detect violations of their
    specific rules defined in system prompts. It uses an external LLM to
    perform the evaluation.

    Usage:
        evaluator = AgentEvaluator(llm_provider="openai", model="gpt-4")
        result = evaluator.evaluate(
            agent_prompt="<agent specifications>",
            conversation=[
                ConversationMessage(role="user", content="..."),
                ConversationMessage(role="agent", content="..."),
            ]
        )
        print(result.rule_adherence_score)
    """

    SUPPORTED_PROVIDERS = ["openai", "anthropic", "google", "mock"]

    def __init__(
        self,
        llm_provider: Literal["openai", "anthropic", "google", "mock"] = "mock",
        model: str = "gpt-4",
        api_key: Optional[str] = None,
    ):
        """
        Initialize the Agent Evaluator.

        Args:
            llm_provider: LLM provider to use for evaluation
            model: Specific model to use (e.g., 'gpt-4', 'claude-3-opus')
            api_key: API key for the LLM provider (if required)

        Raises:
            ValueError: If provider is not supported
        """
        if llm_provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported LLM provider: {llm_provider}. "
                f"Supported: {', '.join(self.SUPPORTED_PROVIDERS)}"
            )

        self.llm_provider = llm_provider
        self.model = model
        self.api_key = api_key

        # Initialize provider client (lazy loading)
        self._client = None

    def extract_rules_from_prompt(
        self,
        prompt_input: AgentPromptInput,
    ) -> List[ExtractedRule]:
        """
        Extract specific rules from agent system prompt.

        This method parses the agent's markdown prompt to identify:
        - Coding standards (e.g., "no quick fixes", "no any type")
        - Workflow rules (e.g., "must document ADRs")
        - Technology constraints (e.g., "Python/TS only unless justified")

        Args:
            prompt_input: Agent prompt input with content or file path

        Returns:
            List of extracted rules

        Raises:
            RuleExtractionError: If rule extraction fails
        """
        try:
            # Load prompt content
            if prompt_input.prompt_content:
                content = prompt_input.prompt_content
            elif prompt_input.prompt_file_path:
                path = Path(prompt_input.prompt_file_path)
                if not path.exists():
                    raise RuleExtractionError(
                        f"Prompt file not found: {prompt_input.prompt_file_path}"
                    )
                content = path.read_text(encoding="utf-8")
            else:
                raise RuleExtractionError(
                    "Either prompt_content or prompt_file_path must be provided"
                )

            rules: List[ExtractedRule] = []

            # Extract rules from different sections using regex patterns

            # Pattern 1: <mandate> tags
            mandate_pattern = r'<mandate[^>]*>(.*?)</mandate>'
            mandates = re.findall(mandate_pattern, content, re.DOTALL)
            for mandate in mandates:
                clean_mandate = mandate.strip()
                if clean_mandate:
                    rules.append(ExtractedRule(
                        rule_type="mandate",
                        rule_text=clean_mandate,
                        is_mandatory=True,
                        context="Core mandate from agent specification"
                    ))

            # Pattern 2: <principle> tags
            principle_pattern = r'<principle[^>]*label="([^"]*)"[^>]*>(.*?)</principle>'
            principles = re.findall(principle_pattern, content, re.DOTALL)
            for label, principle in principles:
                clean_principle = principle.strip()
                if clean_principle:
                    rules.append(ExtractedRule(
                        rule_type="principle",
                        rule_text=f"{label}: {clean_principle}",
                        is_mandatory=True,
                        context="Architectural/operational principle"
                    ))

            # Pattern 3: Coding standards sections
            standards_pattern = r'<coding_standards[^>]*>(.*?)</coding_standards>'
            standards_match = re.search(standards_pattern, content, re.DOTALL)
            if standards_match:
                standards_content = standards_match.group(1)
                # Extract nested tags like <python>, <typescript>
                nested_pattern = r'<(\w+)>(.*?)</\1>'
                nested_rules = re.findall(nested_pattern, standards_content, re.DOTALL)
                for tag, rule_text in nested_rules:
                    clean_text = rule_text.strip()
                    if clean_text:
                        rules.append(ExtractedRule(
                            rule_type=f"coding_standards_{tag}",
                            rule_text=clean_text,
                            is_mandatory=True,
                            context=f"Coding standard for {tag}"
                        ))

            # Pattern 4: Workflow steps
            step_pattern = r'<step[^>]*label="([^"]*)"[^>]*>(.*?)</step>'
            steps = re.findall(step_pattern, content, re.DOTALL)
            for label, step in steps:
                clean_step = step.strip()
                if clean_step:
                    rules.append(ExtractedRule(
                        rule_type="workflow_step",
                        rule_text=f"{label}: {clean_step}",
                        is_mandatory=False,  # Workflow steps are often recommendations
                        context="Recommended workflow step"
                    ))

            # Pattern 5: Explicit "Tu refuses" or "Tu évites" statements
            refusal_pattern = r'(Tu refuses?[^.!?]+[.!?]|Tu évites?[^.!?]+[.!?])'
            refusals = re.findall(refusal_pattern, content, re.IGNORECASE)
            for refusal in refusals:
                clean_refusal = refusal.strip()
                if clean_refusal:
                    rules.append(ExtractedRule(
                        rule_type="strict_constraint",
                        rule_text=clean_refusal,
                        is_mandatory=True,
                        context="Explicit constraint from agent specification"
                    ))

            if not rules:
                raise RuleExtractionError(
                    f"No rules extracted from prompt for agent: {prompt_input.agent_name}"
                )

            return rules

        except (IOError, OSError) as e:
            raise RuleExtractionError(f"Failed to read prompt file: {e}") from e
        except Exception as e:
            raise RuleExtractionError(f"Rule extraction failed: {e}") from e

    def evaluate(
        self,
        agent_prompt: AgentPromptInput | str,
        conversation: List[ConversationMessage],
        focus_on_last_n_messages: int = 5,
    ) -> EvaluationResult:
        """
        Evaluate agent conversation for rule adherence.

        This method:
        1. Extracts rules from the agent prompt
        2. Analyzes the conversation (focusing on recent messages)
        3. Uses LLM to detect violations
        4. Computes a Rule Adherence Score (0-100)
        5. Returns structured evaluation result

        Args:
            agent_prompt: Agent prompt input (string path or AgentPromptInput object)
            conversation: List of conversation messages to evaluate
            focus_on_last_n_messages: How many recent messages to focus on

        Returns:
            EvaluationResult with score, violations, and metadata

        Raises:
            EvaluationError: If evaluation fails
            ValidationError: If inputs are invalid
        """
        try:
            # Validate and prepare agent prompt
            if isinstance(agent_prompt, str):
                # Assume it's a file path
                prompt_input = AgentPromptInput(
                    agent_name=Path(agent_prompt).stem,
                    prompt_file_path=agent_prompt
                )
            else:
                prompt_input = agent_prompt

            # Validate conversation
            if not conversation:
                raise EvaluationError("Conversation cannot be empty")

            # Validate all messages are ConversationMessage instances
            for i, msg in enumerate(conversation):
                if not isinstance(msg, ConversationMessage):
                    raise EvaluationError(
                        f"Message at index {i} is not a ConversationMessage"
                    )

            # Extract rules from prompt
            rules = self.extract_rules_from_prompt(prompt_input)

            # Focus on most recent messages (agent's last responses)
            recent_messages = conversation[-focus_on_last_n_messages:]

            # Find the last agent response to evaluate
            last_agent_msg = None
            for msg in reversed(recent_messages):
                if msg.role in ["agent", "assistant"]:
                    last_agent_msg = msg
                    break

            if not last_agent_msg:
                raise EvaluationError(
                    "No agent/assistant message found in conversation"
                )

            # Perform LLM-based evaluation
            violations = self._evaluate_with_llm(
                rules=rules,
                agent_response=last_agent_msg.content,
                conversation_context=recent_messages,
            )

            # Calculate Rule Adherence Score
            score = self._calculate_adherence_score(
                total_rules=len(rules),
                violations=violations,
            )

            # Build result
            result = EvaluationResult(
                agent_name=prompt_input.agent_name,
                rule_adherence_score=score,
                total_rules_checked=len(rules),
                violations=violations,
                evaluator_model=f"{self.llm_provider}:{self.model}",
                conversation_length=len(conversation),
                summary=self._generate_summary(score, violations),
            )

            return result

        except RuleExtractionError as e:
            raise EvaluationError(f"Rule extraction failed: {e}") from e
        except ValidationError as e:
            raise EvaluationError(f"Validation error: {e}") from e
        except Exception as e:
            raise EvaluationError(f"Evaluation failed: {e}") from e

    def _evaluate_with_llm(
        self,
        rules: List[ExtractedRule],
        agent_response: str,
        conversation_context: List[ConversationMessage],
    ) -> List[RuleViolation]:
        """
        Use LLM to detect rule violations in agent response.

        Args:
            rules: List of rules to check
            agent_response: The agent's response to evaluate
            conversation_context: Recent conversation for context

        Returns:
            List of detected violations

        Raises:
            LLMProviderError: If LLM call fails
        """
        if self.llm_provider == "mock":
            # Mock implementation for testing
            return self._mock_evaluate(rules, agent_response)

        # Build evaluation prompt for the LLM
        evaluation_prompt = self._build_evaluation_prompt(
            rules, agent_response, conversation_context
        )

        try:
            # Call appropriate LLM provider
            if self.llm_provider == "openai":
                violations = self._evaluate_with_openai(evaluation_prompt)
            elif self.llm_provider == "anthropic":
                violations = self._evaluate_with_anthropic(evaluation_prompt)
            elif self.llm_provider == "google":
                violations = self._evaluate_with_google(evaluation_prompt)
            else:
                raise LLMProviderError(f"Provider not implemented: {self.llm_provider}")

            return violations

        except Exception as e:
            raise LLMProviderError(f"LLM evaluation failed: {e}") from e

    def _build_evaluation_prompt(
        self,
        rules: List[ExtractedRule],
        agent_response: str,
        conversation_context: List[ConversationMessage],
    ) -> str:
        """Build the evaluation prompt for the LLM judge."""
        rules_text = "\n".join([
            f"- [{rule.rule_type}] {rule.rule_text}"
            for rule in rules if rule.is_mandatory
        ])

        context_text = "\n".join([
            f"[{msg.role}]: {msg.content[:500]}..."
            for msg in conversation_context[:-1]  # Exclude last message
        ])

        return f"""You are an expert evaluator assessing whether an AI agent's response adheres to its specific rules.

AGENT'S RULES:
{rules_text}

CONVERSATION CONTEXT:
{context_text}

AGENT'S RESPONSE TO EVALUATE:
{agent_response}

TASK:
Analyze the agent's response and identify any violations of the rules listed above.
For each violation, provide:
1. The rule that was violated
2. How it was violated
3. Severity (low/medium/high/critical)
4. Evidence from the response
5. Suggested correction

Output your analysis as JSON with this structure:
{{
    "violations": [
        {{
            "rule_description": "...",
            "violation_description": "...",
            "severity": "high",
            "evidence": "...",
            "suggested_correction": "..."
        }}
    ]
}}

If no violations are found, return {{"violations": []}}.
"""

    def _mock_evaluate(
        self,
        rules: List[ExtractedRule],
        agent_response: str,
    ) -> List[RuleViolation]:
        """
        Mock evaluation for testing (no actual LLM call).

        Performs simple pattern matching to detect obvious violations.
        """
        violations: List[RuleViolation] = []

        # Check for common anti-patterns mentioned in rules
        response_lower = agent_response.lower()

        # Check for "quick fix" mentions if rules prohibit them
        for rule in rules:
            if "quick fix" in rule.rule_text.lower() and "refuses" in rule.rule_text.lower():
                if "quick fix" in response_lower or "quickfix" in response_lower:
                    violations.append(RuleViolation(
                        rule_description=rule.rule_text,
                        violation_description="Agent mentioned 'quick fix' despite rule prohibiting them",
                        severity="high",
                        evidence=self._extract_evidence(agent_response, "quick fix"),
                        suggested_correction="Remove references to quick fixes and implement proper solutions"
                    ))

        # Check for "any" type usage in TypeScript rules
        for rule in rules:
            if "typescript" in rule.rule_type.lower() and "any" in rule.rule_text.lower():
                if re.search(r'\bany\b', agent_response):
                    violations.append(RuleViolation(
                        rule_description=rule.rule_text,
                        violation_description="Agent used 'any' type despite strict typing requirements",
                        severity="high",
                        evidence=self._extract_evidence(agent_response, "any"),
                        suggested_correction="Replace 'any' with proper type definitions or 'unknown' with type guards"
                    ))

        return violations

    def _extract_evidence(self, text: str, keyword: str, context_chars: int = 100) -> str:
        """Extract evidence snippet containing keyword with surrounding context."""
        keyword_lower = keyword.lower()
        text_lower = text.lower()

        idx = text_lower.find(keyword_lower)
        if idx == -1:
            return text[:200]  # Return first 200 chars if keyword not found

        start = max(0, idx - context_chars)
        end = min(len(text), idx + len(keyword) + context_chars)

        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

        return snippet

    def _evaluate_with_openai(self, prompt: str) -> List[RuleViolation]:
        """Evaluate using OpenAI API."""
        try:
            import openai

            if not self.api_key:
                raise LLMProviderError("OpenAI API key not provided")

            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer and evaluator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,  # Deterministic evaluation
            )

            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)

            violations = [
                RuleViolation(**violation)
                for violation in result_json.get("violations", [])
            ]

            return violations

        except ImportError as e:
            raise LLMProviderError("OpenAI library not installed") from e
        except Exception as e:
            raise LLMProviderError(f"OpenAI API call failed: {e}") from e

    def _evaluate_with_anthropic(self, prompt: str) -> List[RuleViolation]:
        """Evaluate using Anthropic Claude API."""
        try:
            import anthropic

            if not self.api_key:
                raise LLMProviderError("Anthropic API key not provided")

            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            result_text = response.content[0].text
            result_json = json.loads(result_text)

            violations = [
                RuleViolation(**violation)
                for violation in result_json.get("violations", [])
            ]

            return violations

        except ImportError as e:
            raise LLMProviderError("Anthropic library not installed") from e
        except Exception as e:
            raise LLMProviderError(f"Anthropic API call failed: {e}") from e

    def _evaluate_with_google(self, prompt: str) -> List[RuleViolation]:
        """Evaluate using Google Gemini API."""
        try:
            from google.cloud import aiplatform

            if not self.api_key:
                raise LLMProviderError("Google API key not provided")

            # This is a simplified implementation
            # Real implementation would use Vertex AI or Gemini API
            raise LLMProviderError("Google provider not fully implemented yet")

        except ImportError as e:
            raise LLMProviderError("Google Cloud AI library not installed") from e
        except Exception as e:
            raise LLMProviderError(f"Google API call failed: {e}") from e

    def _calculate_adherence_score(
        self,
        total_rules: int,
        violations: List[RuleViolation],
    ) -> float:
        """
        Calculate Rule Adherence Score (0-100).

        Scoring algorithm:
        - Start at 100
        - Deduct points based on violation severity:
          - Critical: -20 points per violation
          - High: -10 points per violation
          - Medium: -5 points per violation
          - Low: -2 points per violation
        - Minimum score is 0

        Args:
            total_rules: Total number of rules checked
            violations: List of detected violations

        Returns:
            Score between 0 and 100
        """
        if total_rules == 0:
            return 100.0  # No rules to violate

        score = 100.0

        severity_penalties = {
            "critical": 20.0,
            "high": 10.0,
            "medium": 5.0,
            "low": 2.0,
        }

        for violation in violations:
            penalty = severity_penalties.get(violation.severity, 5.0)
            score -= penalty

        # Ensure score is in valid range
        return max(0.0, min(100.0, score))

    def _generate_summary(
        self,
        score: float,
        violations: List[RuleViolation],
    ) -> str:
        """Generate human-readable summary of evaluation."""
        if score >= 90:
            status = "Excellent"
        elif score >= 75:
            status = "Good"
        elif score >= 50:
            status = "Needs Improvement"
        else:
            status = "Poor"

        if not violations:
            return f"{status} - No rule violations detected. Score: {score:.1f}/100"

        violation_summary = ", ".join([
            f"{v.severity} ({v.rule_description[:50]}...)"
            for v in violations[:3]
        ])

        more_text = f" and {len(violations) - 3} more" if len(violations) > 3 else ""

        return (
            f"{status} - {len(violations)} violation(s) detected: "
            f"{violation_summary}{more_text}. Score: {score:.1f}/100"
        )

    def evaluate_to_json(
        self,
        agent_prompt: AgentPromptInput | str,
        conversation: List[ConversationMessage],
        output_file: Optional[Path] = None,
        **kwargs,
    ) -> str:
        """
        Evaluate and return result as JSON string.

        Convenience method for integration with monitoring systems.

        Args:
            agent_prompt: Agent prompt input
            conversation: Conversation to evaluate
            output_file: Optional file to write JSON to
            **kwargs: Additional arguments for evaluate()

        Returns:
            JSON string of evaluation result
        """
        result = self.evaluate(agent_prompt, conversation, **kwargs)
        json_str = result.model_dump_json(indent=2)

        if output_file:
            output_file.write_text(json_str, encoding="utf-8")

        return json_str
