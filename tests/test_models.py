"""
Test Suite: Pydantic Models

PURPOSE: Validate Pydantic model constraints and serialization
COVERAGE: Models defined in neural_cli/models.py

Tests cover:
- BrainRegion field constraints (coverage 0-100)
- NeuralStatus illumination constraint (0.0-1.0)
- Invalid datetime strings rejected
- RegionStatus enum validation
- Serialization to JSON (datetime → ISO 8601)
- Field validators work correctly
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from neural_cli.models import (
    BrainRegion,
    NeuralStatus,
    Diagnostic,
    DiagnosticLevel,
    RegionStatus,
    FileChangeEvent,
    TestResult,
    WebSocketMessage,
    ProjectMetrics,
)


class TestBrainRegion:
    """Test BrainRegion model validation and constraints."""

    def test_valid_brain_region(self):
        """Valid brain region should be accepted."""
        region = BrainRegion(
            status=RegionStatus.HEALTHY,
            coverage=85.0,
            test_count=10,
            passing_tests=10,
            failing_tests=0,
            file_count=15,
            last_modified=datetime.now(),
        )

        assert region.status == RegionStatus.HEALTHY
        assert region.coverage == 85.0
        assert region.test_count == 10

    def test_default_values(self):
        """Brain region should have correct defaults."""
        region = BrainRegion()

        assert region.status == RegionStatus.OFFLINE
        assert region.coverage == 0.0
        assert region.test_count == 0
        assert region.passing_tests == 0
        assert region.failing_tests == 0
        assert region.file_count == 0
        assert region.last_modified is None

    def test_coverage_validation_clamping(self):
        """Coverage should be clamped to 0-100 range."""
        # Test upper bound clamping
        region = BrainRegion(coverage=150.0)
        assert region.coverage == 100.0

        # Test lower bound clamping
        region = BrainRegion(coverage=-50.0)
        assert region.coverage == 0.0

    def test_negative_test_count_rejected(self):
        """Negative test counts should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BrainRegion(test_count=-5)

        assert "test_count" in str(exc_info.value)

    def test_negative_passing_tests_rejected(self):
        """Negative passing test counts should be rejected."""
        with pytest.raises(ValidationError):
            BrainRegion(passing_tests=-1)

    def test_negative_failing_tests_rejected(self):
        """Negative failing test counts should be rejected."""
        with pytest.raises(ValidationError):
            BrainRegion(failing_tests=-1)

    def test_negative_file_count_rejected(self):
        """Negative file counts should be rejected."""
        with pytest.raises(ValidationError):
            BrainRegion(file_count=-1)

    def test_status_enum_values(self):
        """All RegionStatus enum values should be accepted."""
        for status in RegionStatus:
            region = BrainRegion(status=status)
            assert region.status == status

    def test_invalid_status_rejected(self):
        """Invalid status string should be rejected."""
        with pytest.raises(ValidationError):
            BrainRegion(status="invalid_status")

    def test_last_modified_nullable(self):
        """last_modified should accept None."""
        region = BrainRegion(last_modified=None)
        assert region.last_modified is None

    def test_json_serialization(self):
        """Model should serialize to JSON correctly."""
        now = datetime.now()
        region = BrainRegion(
            status=RegionStatus.HEALTHY,
            coverage=85.0,
            last_modified=now,
        )

        data = region.model_dump(mode='json')

        assert data['status'] == 'healthy'
        assert data['coverage'] == 85.0
        assert isinstance(data['last_modified'], str)  # ISO 8601 string


class TestDiagnostic:
    """Test Diagnostic model validation."""

    def test_valid_diagnostic(self):
        """Valid diagnostic should be accepted."""
        diag = Diagnostic(
            level=DiagnosticLevel.CAUTION,
            region="core-logic",
            message="Test coverage below threshold",
            details="Current coverage: 75%. Target: 80%.",
            file_path="/src/utils/helpers.py",
            line_number=42,
        )

        assert diag.level == DiagnosticLevel.CAUTION
        assert diag.region == "core-logic"
        assert diag.message == "Test coverage below threshold"

    def test_diagnostic_levels(self):
        """All DiagnosticLevel enum values should be accepted."""
        for level in DiagnosticLevel:
            diag = Diagnostic(level=level, region="test", message="Test")
            assert diag.level == level

    def test_invalid_diagnostic_level_rejected(self):
        """Invalid diagnostic level should be rejected."""
        with pytest.raises(ValidationError):
            Diagnostic(level="INVALID", region="test", message="Test")

    def test_default_timestamp(self):
        """Diagnostic should have auto-generated timestamp."""
        diag = Diagnostic(level=DiagnosticLevel.ALERT, region="test", message="Test")
        assert diag.timestamp is not None
        assert isinstance(diag.timestamp, datetime)

    def test_optional_fields_nullable(self):
        """Optional fields should accept None."""
        diag = Diagnostic(
            level=DiagnosticLevel.CAUTION,
            region="test",
            message="Test",
            details=None,
            file_path=None,
            line_number=None,
        )

        assert diag.details is None
        assert diag.file_path is None
        assert diag.line_number is None


class TestNeuralStatus:
    """Test NeuralStatus model validation and constraints."""

    def test_valid_neural_status(self):
        """Valid neural status should be accepted."""
        status = NeuralStatus(
            illumination=0.75,
            regions={
                "core-logic": BrainRegion(status=RegionStatus.HEALTHY, coverage=85.0),
            },
            diagnostics=[],
            project_name="CyberIDE",
            version="1.0.0",
        )

        assert status.illumination == 0.75
        assert "core-logic" in status.regions

    def test_illumination_validation_clamping(self):
        """Illumination should be clamped to 0.0-1.0 range."""
        # Test upper bound clamping
        status = NeuralStatus(illumination=1.5)
        assert status.illumination == 1.0

        # Test lower bound clamping
        status = NeuralStatus(illumination=-0.5)
        assert status.illumination == 0.0

    def test_illumination_boundary_values(self):
        """Illumination should accept boundary values."""
        status1 = NeuralStatus(illumination=0.0)
        assert status1.illumination == 0.0

        status2 = NeuralStatus(illumination=1.0)
        assert status2.illumination == 1.0

    def test_default_values(self):
        """Neural status should have correct defaults."""
        status = NeuralStatus()

        assert status.illumination == 0.0
        assert status.regions == {}
        assert status.diagnostics == []
        assert status.project_name == "CyberIDE"
        assert status.version == "1.0.0"
        assert status.has_license is False
        assert status.has_readme is False
        assert status.documentation_complete is False
        assert status.api_configured is False
        assert status.mcp_providers_count == 0

    def test_auto_timestamp(self):
        """Neural status should have auto-generated timestamp."""
        status = NeuralStatus()
        assert status.timestamp is not None
        assert isinstance(status.timestamp, datetime)

    def test_empty_regions(self):
        """Neural status should accept empty regions dict."""
        status = NeuralStatus(regions={})
        assert status.regions == {}

    def test_multiple_regions(self):
        """Neural status should accept multiple regions."""
        status = NeuralStatus(
            regions={
                "core-logic": BrainRegion(status=RegionStatus.HEALTHY),
                "api-integration": BrainRegion(status=RegionStatus.WARNING),
                "tests": BrainRegion(status=RegionStatus.ERROR),
            }
        )

        assert len(status.regions) == 3
        assert status.regions["core-logic"].status == RegionStatus.HEALTHY

    def test_diagnostics_list(self):
        """Neural status should accept diagnostics list."""
        diag = Diagnostic(level=DiagnosticLevel.ALERT, region="test", message="Error")
        status = NeuralStatus(diagnostics=[diag])

        assert len(status.diagnostics) == 1
        assert status.diagnostics[0].level == DiagnosticLevel.ALERT

    def test_json_serialization_with_datetime(self):
        """Model should serialize datetime to ISO 8601."""
        status = NeuralStatus(illumination=0.5)
        data = status.model_dump(mode='json')

        assert isinstance(data['timestamp'], str)
        # Verify it's ISO 8601 format
        datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))


class TestFileChangeEvent:
    """Test FileChangeEvent model validation."""

    def test_valid_file_change_event(self):
        """Valid file change event should be accepted."""
        event = FileChangeEvent(
            event_type="modified",
            file_path="/src/utils/helpers.py",
            is_test_file=False,
        )

        assert event.event_type == "modified"
        assert event.file_path == "/src/utils/helpers.py"
        assert event.is_test_file is False

    def test_default_is_test_file(self):
        """is_test_file should default to False."""
        event = FileChangeEvent(event_type="created", file_path="/src/main.py")
        assert event.is_test_file is False

    def test_auto_timestamp(self):
        """File change event should have auto-generated timestamp."""
        event = FileChangeEvent(event_type="created", file_path="/test.py")
        assert event.timestamp is not None
        assert isinstance(event.timestamp, datetime)

    def test_event_types(self):
        """Different event types should be accepted."""
        event_types = ["created", "modified", "deleted", "moved"]

        for event_type in event_types:
            event = FileChangeEvent(event_type=event_type, file_path="/test.py")
            assert event.event_type == event_type


class TestTestResult:
    """Test TestResult model validation."""

    def test_valid_test_result(self):
        """Valid test result should be accepted."""
        result = TestResult(
            total_tests=100,
            passed=85,
            failed=15,
            skipped=0,
            errors=0,
            coverage_percentage=75.5,
            duration=2.345,
        )

        assert result.total_tests == 100
        assert result.passed == 85
        assert result.coverage_percentage == 75.5

    def test_default_values(self):
        """Test result should have correct defaults."""
        result = TestResult()

        assert result.total_tests == 0
        assert result.passed == 0
        assert result.failed == 0
        assert result.skipped == 0
        assert result.errors == 0
        assert result.coverage_percentage == 0.0
        assert result.duration == 0.0
        assert result.failed_tests == []

    def test_failed_tests_list(self):
        """Failed tests list should be accepted."""
        result = TestResult(
            total_tests=10,
            passed=8,
            failed=2,
            failed_tests=[
                {"test_name": "test_edge_case", "error_message": "AssertionError"},
            ],
        )

        assert len(result.failed_tests) == 1
        assert result.failed_tests[0]["test_name"] == "test_edge_case"

    def test_auto_timestamp(self):
        """Test result should have auto-generated timestamp."""
        result = TestResult()
        assert result.timestamp is not None
        assert isinstance(result.timestamp, datetime)


class TestWebSocketMessage:
    """Test WebSocketMessage model validation."""

    def test_valid_websocket_message(self):
        """Valid WebSocket message should be accepted."""
        message = WebSocketMessage(
            type="neural_status",
            data={"illumination": 0.75, "regions": {}},
        )

        assert message.type == "neural_status"
        assert message.data["illumination"] == 0.75

    def test_auto_timestamp(self):
        """WebSocket message should have auto-generated timestamp."""
        message = WebSocketMessage(type="test", data={})
        assert message.timestamp is not None
        assert isinstance(message.timestamp, datetime)

    def test_different_message_types(self):
        """Different message types should be accepted."""
        types = ["neural_status", "file_change", "test_result", "diagnostic"]

        for msg_type in types:
            message = WebSocketMessage(type=msg_type, data={})
            assert message.type == msg_type


class TestProjectMetrics:
    """Test ProjectMetrics model validation."""

    def test_valid_project_metrics(self):
        """Valid project metrics should be accepted."""
        metrics = ProjectMetrics(
            total_files=500,
            total_lines=25000,
            test_coverage=85.5,
            documentation_score=75.0,
            module_completion=90.0,
            integration_score=80.0,
            overall_health=82.5,
        )

        assert metrics.total_files == 500
        assert metrics.test_coverage == 85.5

    def test_default_values(self):
        """Project metrics should have correct defaults."""
        metrics = ProjectMetrics()

        assert metrics.total_files == 0
        assert metrics.total_lines == 0
        assert metrics.test_coverage == 0.0
        assert metrics.documentation_score == 0.0
        assert metrics.module_completion == 0.0
        assert metrics.integration_score == 0.0
        assert metrics.overall_health == 0.0

    def test_percentage_field_clamping(self):
        """Percentage fields should be clamped to 0-100."""
        # Test upper bound
        metrics = ProjectMetrics(test_coverage=150.0)
        assert metrics.test_coverage == 100.0

        # Test lower bound
        metrics = ProjectMetrics(test_coverage=-50.0)
        assert metrics.test_coverage == 0.0

    def test_all_percentage_fields_clamped(self):
        """All percentage fields should be clamped."""
        metrics = ProjectMetrics(
            test_coverage=150.0,
            documentation_score=200.0,
            module_completion=-10.0,
            integration_score=120.0,
            overall_health=-5.0,
        )

        assert metrics.test_coverage == 100.0
        assert metrics.documentation_score == 100.0
        assert metrics.module_completion == 0.0
        assert metrics.integration_score == 100.0
        assert metrics.overall_health == 0.0


class TestEnums:
    """Test enum definitions."""

    def test_region_status_values(self):
        """RegionStatus should have correct values."""
        assert RegionStatus.HEALTHY.value == "healthy"
        assert RegionStatus.WARNING.value == "warning"
        assert RegionStatus.ERROR.value == "error"
        assert RegionStatus.OFFLINE.value == "offline"

    def test_diagnostic_level_values(self):
        """DiagnosticLevel should have correct values."""
        assert DiagnosticLevel.CAUTION.value == "CAUTION"
        assert DiagnosticLevel.ALERT.value == "ALERT"

    def test_enum_membership(self):
        """Enum membership checks should work."""
        assert "healthy" in [s.value for s in RegionStatus]
        assert "ALERT" in [l.value for l in DiagnosticLevel]
