"""
Unit tests for Agent Evaluator (LLM-as-a-Judge).

Tests the agent conformity monitoring system that evaluates agent responses
against their specific rules defined in system prompts.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from backend.cto.evaluation import (
    AgentEvaluator,
    AgentEvaluatorError,
    AgentPromptInput,
    ConversationMessage,
    EvaluationError,
    EvaluationResult,
    ExtractedRule,
    RuleExtractionError,
    RuleViolation,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_agent_prompt():
    """Sample agent system prompt with rules."""
    return """
---
title: "Spécification système — Test Agent"
version: "1.0.0"
---

<test_agent version="1.0.0">
  <identity>
    <name>Test Agent</name>
    <tagline>Tu es un agent de test pour validation.</tagline>
  </identity>

  <mandates color="#7FFF00">
    <mandate index="1">Tu dois toujours valider les entrées utilisateur.</mandate>
    <mandate index="2">Tu dois utiliser des types stricts en TypeScript.</mandate>
  </mandates>

  <coding_standards color="#8E44AD">
    <python>
      Tu refuses toute solution qui contourne les règles de typage strict.
      Pas de quick fix non testé ou non typé.
    </python>
    <typescript>
      Aucun any toléré, validation runtime systématique pour les données externes.
    </typescript>
  </coding_standards>

  <workflow color="#1ABC9C">
    <step index="1" label="Valider">
      Tu valides toutes les données d'entrée avant traitement.
    </step>
    <step index="2" label="Documenter">
      Tu documentes les décisions importantes.
    </step>
  </workflow>
</test_agent>
"""


@pytest.fixture
def sample_agent_prompt_file(tmp_path, sample_agent_prompt):
    """Create a temporary file with agent prompt."""
    prompt_file = tmp_path / "test-agent.md"
    prompt_file.write_text(sample_agent_prompt, encoding="utf-8")
    return prompt_file


@pytest.fixture
def sample_conversation():
    """Sample conversation for testing."""
    return [
        ConversationMessage(
            role="user",
            content="Can you add a quick fix to bypass the validation?"
        ),
        ConversationMessage(
            role="agent",
            content="I'll add a quick fix using 'any' type to make it work fast."
        ),
    ]


@pytest.fixture
def clean_conversation():
    """Clean conversation with no violations."""
    return [
        ConversationMessage(
            role="user",
            content="Can you implement proper validation for the input?"
        ),
        ConversationMessage(
            role="agent",
            content=(
                "I'll implement strict validation using Zod with proper TypeScript types. "
                "No shortcuts - we'll use proper type definitions with validation."
            )
        ),
    ]


@pytest.fixture
def evaluator():
    """Create a mock evaluator for testing."""
    return AgentEvaluator(llm_provider="mock", model="test-model")


# ============================================================================
# Model Tests
# ============================================================================

class TestConversationMessage:
    """Tests for ConversationMessage model."""
    
    def test_valid_message(self):
        """Test creating a valid conversation message."""
        msg = ConversationMessage(
            role="user",
            content="Test message"
        )
        assert msg.role == "user"
        assert msg.content == "Test message"
        assert isinstance(msg.timestamp, datetime)
    
    def test_utc_timezone_enforcement(self):
        """Test that timestamps are converted to UTC."""
        msg = ConversationMessage(
            role="agent",
            content="Test",
            timestamp=datetime.now()  # Naive datetime
        )
        assert msg.timestamp.tzinfo == timezone.utc
    
    def test_invalid_role(self):
        """Test that invalid roles are rejected."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            ConversationMessage(
                role="invalid_role",  # type: ignore
                content="Test"
            )


class TestRuleViolation:
    """Tests for RuleViolation model."""
    
    def test_valid_violation(self):
        """Test creating a valid rule violation."""
        violation = RuleViolation(
            rule_description="No quick fixes allowed",
            violation_description="Agent suggested a quick fix",
            severity="high"
        )
        assert violation.severity == "high"
        assert "quick fix" in violation.rule_description.lower()
    
    def test_with_evidence(self):
        """Test violation with evidence."""
        violation = RuleViolation(
            rule_description="No 'any' type",
            violation_description="Used 'any' type",
            severity="critical",
            evidence="const data: any = input;",
            suggested_correction="Use proper type or 'unknown'"
        )
        assert violation.evidence is not None
        assert violation.suggested_correction is not None


class TestEvaluationResult:
    """Tests for EvaluationResult model."""
    
    def test_valid_result(self):
        """Test creating a valid evaluation result."""
        result = EvaluationResult(
            agent_name="Test Agent",
            rule_adherence_score=85.5,
            total_rules_checked=10,
            violations=[],
            evaluator_model="mock:test",
            conversation_length=5
        )
        assert result.rule_adherence_score == 85.5
        assert result.total_rules_checked == 10
        assert len(result.violations) == 0
    
    def test_score_bounds(self):
        """Test that score must be between 0 and 100."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            EvaluationResult(
                agent_name="Test",
                rule_adherence_score=150.0,  # Invalid: > 100
                total_rules_checked=10,
                evaluator_model="mock",
                conversation_length=5
            )
    
    def test_version_pattern(self):
        """Test that agent_version must follow semver."""
        result = EvaluationResult(
            agent_name="Test",
            agent_version="1.0.0",
            rule_adherence_score=90.0,
            total_rules_checked=10,
            evaluator_model="mock",
            conversation_length=5
        )
        assert result.agent_version == "1.0.0"
        
        with pytest.raises(Exception):  # Pydantic ValidationError
            EvaluationResult(
                agent_name="Test",
                agent_version="invalid-version",
                rule_adherence_score=90.0,
                total_rules_checked=10,
                evaluator_model="mock",
                conversation_length=5
            )
    
    def test_no_pii_in_metadata(self):
        """Test that PII is blocked in metadata."""
        with pytest.raises(ValueError, match="forbidden"):
            EvaluationResult(
                agent_name="Test",
                rule_adherence_score=90.0,
                total_rules_checked=10,
                evaluator_model="mock",
                conversation_length=5,
                metadata={"email": "test@example.com"}  # Forbidden
            )
    
    def test_json_serialization(self):
        """Test that result can be serialized to JSON."""
        result = EvaluationResult(
            agent_name="Test Agent",
            rule_adherence_score=75.0,
            total_rules_checked=8,
            evaluator_model="mock:test",
            conversation_length=3,
            violations=[
                RuleViolation(
                    rule_description="No quick fixes",
                    violation_description="Used quick fix",
                    severity="medium"
                )
            ]
        )
        
        json_str = result.model_dump_json()
        assert isinstance(json_str, str)
        
        # Parse back to ensure it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["agent_name"] == "Test Agent"
        assert parsed["rule_adherence_score"] == 75.0
        assert len(parsed["violations"]) == 1


class TestAgentPromptInput:
    """Tests for AgentPromptInput model."""
    
    def test_with_content(self):
        """Test creating input with direct content."""
        prompt = AgentPromptInput(
            agent_name="Test Agent",
            prompt_content="<test>Content</test>"
        )
        assert prompt.agent_name == "Test Agent"
        assert prompt.prompt_content is not None
    
    def test_with_file_path(self):
        """Test creating input with file path."""
        prompt = AgentPromptInput(
            agent_name="Test Agent",
            prompt_file_path="/path/to/prompt.md"
        )
        assert prompt.prompt_file_path is not None
    
    def test_requires_at_least_one_source(self):
        """Test that at least one source must be provided."""
        with pytest.raises(ValueError, match="Either"):
            AgentPromptInput(agent_name="Test Agent")


# ============================================================================
# AgentEvaluator Tests
# ============================================================================

class TestAgentEvaluatorInit:
    """Tests for AgentEvaluator initialization."""
    
    def test_supported_provider(self):
        """Test initialization with supported provider."""
        evaluator = AgentEvaluator(llm_provider="mock", model="test")
        assert evaluator.llm_provider == "mock"
        assert evaluator.model == "test"
    
    def test_unsupported_provider(self):
        """Test that unsupported provider raises error."""
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            AgentEvaluator(llm_provider="unsupported", model="test")  # type: ignore
    
    def test_with_api_key(self):
        """Test initialization with API key."""
        evaluator = AgentEvaluator(
            llm_provider="openai",
            model="gpt-4",
            api_key="sk-test123"
        )
        assert evaluator.api_key == "sk-test123"


class TestRuleExtraction:
    """Tests for rule extraction from agent prompts."""
    
    def test_extract_from_content(self, evaluator, sample_agent_prompt):
        """Test extracting rules from prompt content."""
        prompt_input = AgentPromptInput(
            agent_name="Test Agent",
            prompt_content=sample_agent_prompt
        )
        
        rules = evaluator.extract_rules_from_prompt(prompt_input)
        
        assert len(rules) > 0
        assert any("valider les entrées" in rule.rule_text.lower() for rule in rules)
        assert any("types stricts" in rule.rule_text.lower() for rule in rules)
    
    def test_extract_from_file(self, evaluator, sample_agent_prompt_file):
        """Test extracting rules from prompt file."""
        prompt_input = AgentPromptInput(
            agent_name="Test Agent",
            prompt_file_path=str(sample_agent_prompt_file)
        )
        
        rules = evaluator.extract_rules_from_prompt(prompt_input)
        
        assert len(rules) > 0
    
    def test_extract_mandates(self, evaluator, sample_agent_prompt):
        """Test that mandates are extracted."""
        prompt_input = AgentPromptInput(
            agent_name="Test Agent",
            prompt_content=sample_agent_prompt
        )
        
        rules = evaluator.extract_rules_from_prompt(prompt_input)
        mandates = [r for r in rules if r.rule_type == "mandate"]
        
        assert len(mandates) >= 2
        assert all(r.is_mandatory for r in mandates)
    
    def test_extract_coding_standards(self, evaluator, sample_agent_prompt):
        """Test that coding standards are extracted."""
        prompt_input = AgentPromptInput(
            agent_name="Test Agent",
            prompt_content=sample_agent_prompt
        )
        
        rules = evaluator.extract_rules_from_prompt(prompt_input)
        coding_rules = [r for r in rules if "coding_standards" in r.rule_type]
        
        assert len(coding_rules) >= 2
        assert any("python" in r.rule_type for r in coding_rules)
        assert any("typescript" in r.rule_type for r in coding_rules)
    
    def test_extract_strict_constraints(self, evaluator, sample_agent_prompt):
        """Test that 'Tu refuses' statements are extracted."""
        prompt_input = AgentPromptInput(
            agent_name="Test Agent",
            prompt_content=sample_agent_prompt
        )
        
        rules = evaluator.extract_rules_from_prompt(prompt_input)
        constraints = [r for r in rules if r.rule_type == "strict_constraint"]
        
        assert len(constraints) > 0
        assert all("refuse" in r.rule_text.lower() for r in constraints)
    
    def test_nonexistent_file(self, evaluator):
        """Test that nonexistent file raises error."""
        prompt_input = AgentPromptInput(
            agent_name="Test Agent",
            prompt_file_path="/nonexistent/file.md"
        )
        
        with pytest.raises(RuleExtractionError, match="not found"):
            evaluator.extract_rules_from_prompt(prompt_input)
    
    def test_empty_prompt(self, evaluator):
        """Test that empty prompt raises error."""
        prompt_input = AgentPromptInput(
            agent_name="Test Agent",
            prompt_content="No rules here"
        )
        
        with pytest.raises(RuleExtractionError, match="No rules extracted"):
            evaluator.extract_rules_from_prompt(prompt_input)


class TestEvaluation:
    """Tests for agent evaluation."""
    
    def test_evaluate_with_violations(
        self, 
        evaluator, 
        sample_agent_prompt_file, 
        sample_conversation
    ):
        """Test evaluation that detects violations."""
        result = evaluator.evaluate(
            agent_prompt=str(sample_agent_prompt_file),
            conversation=sample_conversation
        )
        
        assert isinstance(result, EvaluationResult)
        assert result.agent_name == "test-agent"
        assert 0 <= result.rule_adherence_score <= 100
        assert result.total_rules_checked > 0
        # Mock evaluator should detect "quick fix" and "any" violations
        assert len(result.violations) > 0
    
    def test_evaluate_clean_conversation(
        self,
        evaluator,
        sample_agent_prompt_file,
        clean_conversation
    ):
        """Test evaluation with no violations."""
        result = evaluator.evaluate(
            agent_prompt=str(sample_agent_prompt_file),
            conversation=clean_conversation
        )
        
        assert result.rule_adherence_score >= 90.0
        assert len(result.violations) == 0
        assert "No rule violations" in result.summary
    
    def test_evaluate_with_prompt_input_object(
        self,
        evaluator,
        sample_agent_prompt,
        clean_conversation
    ):
        """Test evaluation with AgentPromptInput object."""
        prompt_input = AgentPromptInput(
            agent_name="Test Agent",
            prompt_content=sample_agent_prompt
        )
        
        result = evaluator.evaluate(
            agent_prompt=prompt_input,
            conversation=clean_conversation
        )
        
        assert result.agent_name == "Test Agent"
    
    def test_evaluate_empty_conversation(
        self,
        evaluator,
        sample_agent_prompt_file
    ):
        """Test that empty conversation raises error."""
        with pytest.raises(EvaluationError, match="cannot be empty"):
            evaluator.evaluate(
                agent_prompt=str(sample_agent_prompt_file),
                conversation=[]
            )
    
    def test_evaluate_no_agent_message(
        self,
        evaluator,
        sample_agent_prompt_file
    ):
        """Test that conversation without agent message raises error."""
        conversation = [
            ConversationMessage(role="user", content="Hello"),
            ConversationMessage(role="user", content="Anyone there?"),
        ]
        
        with pytest.raises(EvaluationError, match="No agent/assistant message"):
            evaluator.evaluate(
                agent_prompt=str(sample_agent_prompt_file),
                conversation=conversation
            )
    
    def test_focus_on_last_n_messages(
        self,
        evaluator,
        sample_agent_prompt_file
    ):
        """Test that evaluation focuses on recent messages."""
        long_conversation = [
            ConversationMessage(role="user", content=f"Message {i}")
            for i in range(20)
        ] + [
            ConversationMessage(role="agent", content="Response with quick fix")
        ]
        
        result = evaluator.evaluate(
            agent_prompt=str(sample_agent_prompt_file),
            conversation=long_conversation,
            focus_on_last_n_messages=3
        )
        
        # Should still detect violations in last message
        assert result.conversation_length == len(long_conversation)


class TestScoringAlgorithm:
    """Tests for rule adherence score calculation."""
    
    def test_perfect_score(self, evaluator):
        """Test that no violations gives perfect score."""
        score = evaluator._calculate_adherence_score(
            total_rules=10,
            violations=[]
        )
        assert score == 100.0
    
    def test_critical_violation_penalty(self, evaluator):
        """Test that critical violations heavily impact score."""
        violations = [
            RuleViolation(
                rule_description="Critical rule",
                violation_description="Violated",
                severity="critical"
            )
        ]
        
        score = evaluator._calculate_adherence_score(
            total_rules=10,
            violations=violations
        )
        
        assert score == 80.0  # 100 - 20
    
    def test_multiple_violations(self, evaluator):
        """Test scoring with multiple violations."""
        violations = [
            RuleViolation(
                rule_description="Rule 1",
                violation_description="Violated",
                severity="high"  # -10
            ),
            RuleViolation(
                rule_description="Rule 2",
                violation_description="Violated",
                severity="medium"  # -5
            ),
            RuleViolation(
                rule_description="Rule 3",
                violation_description="Violated",
                severity="low"  # -2
            ),
        ]
        
        score = evaluator._calculate_adherence_score(
            total_rules=10,
            violations=violations
        )
        
        assert score == 83.0  # 100 - 10 - 5 - 2
    
    def test_score_minimum_bound(self, evaluator):
        """Test that score never goes below 0."""
        violations = [
            RuleViolation(
                rule_description=f"Rule {i}",
                violation_description="Violated",
                severity="critical"
            )
            for i in range(10)  # 10 * 20 = 200 points deducted
        ]
        
        score = evaluator._calculate_adherence_score(
            total_rules=10,
            violations=violations
        )
        
        assert score == 0.0


class TestJSONOutput:
    """Tests for JSON output functionality."""
    
    def test_evaluate_to_json_string(
        self,
        evaluator,
        sample_agent_prompt_file,
        clean_conversation
    ):
        """Test that evaluate_to_json returns valid JSON."""
        json_str = evaluator.evaluate_to_json(
            agent_prompt=str(sample_agent_prompt_file),
            conversation=clean_conversation
        )
        
        assert isinstance(json_str, str)
        
        # Parse and validate
        parsed = json.loads(json_str)
        assert "agent_name" in parsed
        assert "rule_adherence_score" in parsed
        assert "violations" in parsed
        assert "evaluation_timestamp" in parsed
    
    def test_evaluate_to_json_file(
        self,
        evaluator,
        sample_agent_prompt_file,
        clean_conversation,
        tmp_path
    ):
        """Test that evaluate_to_json can write to file."""
        output_file = tmp_path / "evaluation_result.json"
        
        json_str = evaluator.evaluate_to_json(
            agent_prompt=str(sample_agent_prompt_file),
            conversation=clean_conversation,
            output_file=output_file
        )
        
        # Check file was written
        assert output_file.exists()
        
        # Check contents match
        file_contents = output_file.read_text()
        assert file_contents == json_str
        
        # Validate JSON structure
        parsed = json.loads(file_contents)
        assert "rule_adherence_score" in parsed


class TestSummaryGeneration:
    """Tests for evaluation summary generation."""
    
    def test_excellent_summary(self, evaluator):
        """Test summary for excellent score."""
        summary = evaluator._generate_summary(score=95.0, violations=[])
        assert "Excellent" in summary
        assert "No rule violations" in summary
    
    def test_good_summary(self, evaluator):
        """Test summary for good score."""
        violations = [
            RuleViolation(
                rule_description="Minor issue",
                violation_description="Small problem",
                severity="low"
            )
        ]
        summary = evaluator._generate_summary(score=80.0, violations=violations)
        assert "Good" in summary
        assert "1 violation" in summary
    
    def test_needs_improvement_summary(self, evaluator):
        """Test summary for mediocre score."""
        violations = [
            RuleViolation(
                rule_description=f"Issue {i}",
                violation_description="Problem",
                severity="medium"
            )
            for i in range(3)
        ]
        summary = evaluator._generate_summary(score=60.0, violations=violations)
        assert "Needs Improvement" in summary
        assert "3 violation" in summary
    
    def test_poor_summary(self, evaluator):
        """Test summary for poor score."""
        violations = [
            RuleViolation(
                rule_description=f"Critical issue {i}",
                violation_description="Major problem",
                severity="critical"
            )
            for i in range(5)
        ]
        summary = evaluator._generate_summary(score=30.0, violations=violations)
        assert "Poor" in summary


# ============================================================================
# Integration Tests
# ============================================================================

class TestRealAgentPrompt:
    """Integration tests with real agent prompt files."""
    
    def test_load_architecte_principal(self, evaluator):
        """Test loading and parsing Architecte Principal prompt."""
        prompt_path = Path(__file__).parent.parent / "docs" / "archive" / "legacy_agents" / "architecte-principal.agent.md"
        
        if not prompt_path.exists():
            pytest.skip("Architecte Principal prompt file not found")
        
        prompt_input = AgentPromptInput(
            agent_name="Architecte Principal",
            prompt_file_path=str(prompt_path)
        )
        
        rules = evaluator.extract_rules_from_prompt(prompt_input)
        
        assert len(rules) > 0
        # Should extract the "pas de quick fix" rule
        assert any("quick fix" in rule.rule_text.lower() for rule in rules)
        # Should extract the "aucun any toléré" rule
        assert any("any" in rule.rule_text.lower() for rule in rules)
    
    def test_evaluate_architecte_response(self, evaluator):
        """Test evaluating a response from Architecte Principal."""
        prompt_path = Path(__file__).parent.parent / "docs" / "archive" / "legacy_agents" / "architecte-principal.agent.md"
        
        if not prompt_path.exists():
            pytest.skip("Architecte Principal prompt file not found")
        
        # Simulate a conversation where architect violates rules
        conversation = [
            ConversationMessage(
                role="user",
                content="We need to ship this feature quickly"
            ),
            ConversationMessage(
                role="agent",
                content="I'll implement a quick fix using 'any' type to bypass validation for now"
            ),
        ]
        
        result = evaluator.evaluate(
            agent_prompt=str(prompt_path),
            conversation=conversation
        )
        
        # Should detect violations
        assert result.rule_adherence_score < 100.0
        assert len(result.violations) > 0


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Tests for error handling."""
    
    def test_rule_extraction_error_inheritance(self):
        """Test that RuleExtractionError is subclass of AgentEvaluatorError."""
        assert issubclass(RuleExtractionError, AgentEvaluatorError)
    
    def test_evaluation_error_inheritance(self):
        """Test that EvaluationError is subclass of AgentEvaluatorError."""
        assert issubclass(EvaluationError, AgentEvaluatorError)
