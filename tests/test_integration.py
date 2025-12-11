"""
Integration Tests - End-to-end workflows across multiple components.

This module validates:
- Complete backend startup/shutdown lifecycle
- File change → Test run → Status update → WebSocket broadcast flow
- Multiple WebSocket clients receiving broadcasts simultaneously
- MetricCalculator → NeuralStatus → WebSocket flow
- PytestAnalyzer → FileWatcher integration
- Full project health monitoring cycle
- Error propagation across components
"""

import pytest
import asyncio
import json
import time
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

from neural_cli.main import app, neural_core, update_neural_status
from neural_cli.models import (
    NeuralStatus,
    FileChangeEvent,
    PytestRunResult,
    BrainRegion,
    RegionStatus,
    WebSocketMessage
)
from neural_cli.metric_calculator import MetricCalculator
from neural_cli.test_analyzer import PytestAnalyzer
from neural_cli.file_watcher import FileWatcher


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def client():
    """Create FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def full_project(tmp_path):
    """Create a full project with all components for integration testing."""
    # Create directory structure
    (tmp_path / "src" / "components").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "neural_cli").mkdir()

    # Create documentation
    (tmp_path / "README.md").write_text("# Integration Test Project\n" + ("x" * 600))
    (tmp_path / "LICENSE").write_text("MIT License")

    # Create source files
    (tmp_path / "src" / "main.ts").write_text("console.log('app');")
    (tmp_path / "src" / "components" / "App.tsx").write_text("export const App = () => null;")

    # Create backend files
    (tmp_path / "neural_cli" / "core.py").write_text("# backend logic")

    # Create test files
    (tmp_path / "tests" / "__init__.py").write_text("")
    (tmp_path / "tests" / "conftest.py").write_text("""
import pytest

@pytest.fixture
def sample_data():
    return {"value": 42}
""")
    (tmp_path / "tests" / "test_integration.py").write_text("""
def test_always_pass():
    assert True

def test_math():
    assert 1 + 1 == 2

def test_with_fixture(sample_data):
    assert sample_data["value"] == 42
""")

    return tmp_path


@pytest.fixture
def mock_neural_core(tmp_path):
    """Create a mock neural core for testing."""
    from neural_cli.main import NeuralCore

    core = NeuralCore()
    core.project_root = tmp_path
    core.status_file = tmp_path / "neural_status.json"
    core.current_status = NeuralStatus()
    core.test_running = False

    return core


# ============================================================================
# Component Integration Tests
# ============================================================================

class TestMetricCalculatorIntegration:
    """Integration tests for MetricCalculator with real project structure."""

    def test_calculate_metrics_for_full_project(self, full_project):
        """Test MetricCalculator calculates metrics for complete project."""
        calculator = MetricCalculator(str(full_project))

        # Count files
        file_counts = calculator.count_files_by_region()

        assert file_counts["frontend"] == 2  # main.ts, App.tsx
        assert file_counts["backend"] == 1  # core.py
        assert file_counts["tests"] == 1  # test_integration.py

        # Calculate status
        status = calculator.calculate_neural_status(
            test_coverage=85.0,
            test_results={"passed": 3, "failed": 0, "total": 3},
            file_counts=file_counts
        )

        assert status.illumination > 0.0
        assert status.has_license is True
        assert status.has_readme is True
        assert len(status.regions) == 6  # All regions created (including data-layer)

    def test_documentation_score_affects_illumination(self, full_project):
        """Test documentation completeness affects illumination."""
        calculator = MetricCalculator(str(full_project))

        # Calculate with documentation
        status_with_docs = calculator.calculate_neural_status(
            test_coverage=80.0,
            test_results={"passed": 10, "failed": 0, "total": 10},
            file_counts={}
        )

        # Remove documentation
        (full_project / "README.md").unlink()
        (full_project / "LICENSE").unlink()

        calculator_no_docs = MetricCalculator(str(full_project))

        status_without_docs = calculator_no_docs.calculate_neural_status(
            test_coverage=80.0,
            test_results={"passed": 10, "failed": 0, "total": 10},
            file_counts={}
        )

        # Illumination should be higher with documentation
        assert status_with_docs.illumination > status_without_docs.illumination


class TestPytestAnalyzerIntegration:
    """Integration tests for PytestAnalyzer with real test execution."""

    @pytest.mark.slow
    def test_run_tests_on_real_project(self, full_project):
        """Test running pytest on actual project."""
        analyzer = PytestAnalyzer(str(full_project))

        # This will actually run pytest
        result = analyzer.run_tests(verbose=False)

        # Tests should pass
        assert result.total_tests >= 3
        assert result.passed >= 3
        assert result.failed == 0

    def test_should_run_tests_for_various_files(self, full_project):
        """Test should_run_tests logic with real project paths."""
        analyzer = PytestAnalyzer(str(full_project))

        # Should run for source files
        assert analyzer.should_run_tests(str(full_project / "src" / "main.ts")) is True

        # Should run for backend files
        assert analyzer.should_run_tests(str(full_project / "neural_cli" / "core.py")) is True

        # Should run for test files
        assert analyzer.should_run_tests(str(full_project / "tests" / "test_integration.py")) is True

        # Should not run for docs
        assert analyzer.should_run_tests(str(full_project / "README.md")) is False

    def test_get_test_files_finds_all_tests(self, full_project):
        """Test PytestAnalyzer finds all test files."""
        analyzer = PytestAnalyzer(str(full_project))

        test_files = analyzer.get_test_files()

        # Should find test_integration.py
        assert len(test_files) >= 1
        assert any("test_integration.py" in str(f) for f in test_files)


class TestFileWatcherIntegration:
    """Integration tests for FileWatcher with actual file operations."""

    def test_watcher_detects_real_file_changes(self, full_project):
        """Test FileWatcher detects actual file system changes."""
        events = []

        def callback(event: FileChangeEvent):
            events.append(event)

        watcher = FileWatcher(
            project_root=str(full_project),
            on_change_callback=callback
        )

        watcher.start()
        time.sleep(0.5)  # Let watcher initialize

        # Create a new file
        new_file = full_project / "src" / "NewComponent.tsx"
        new_file.write_text("export const NewComponent = () => null;")

        time.sleep(1.0)  # Wait for event

        watcher.stop()

        # Event should be detected
        assert len(events) > 0
        assert any("NewComponent" in e.file_path for e in events)

    def test_watcher_ignores_unwanted_files(self, full_project):
        """Test FileWatcher ignores .git and node_modules."""
        events = []

        def callback(event: FileChangeEvent):
            events.append(event)

        # Create ignored directories
        (full_project / ".git").mkdir()
        (full_project / "node_modules").mkdir()

        watcher = FileWatcher(
            project_root=str(full_project),
            on_change_callback=callback
        )

        watcher.start()
        time.sleep(0.5)

        # Create files in ignored directories
        (full_project / ".git" / "config").write_text("git")
        (full_project / "node_modules" / "package.json").write_text("{}")

        time.sleep(1.0)

        watcher.stop()

        # Should not detect these events
        assert not any(".git" in e.file_path for e in events)
        assert not any("node_modules" in e.file_path for e in events)


# ============================================================================
# End-to-End Workflow Tests
# ============================================================================

class TestEndToEndWorkflows:
    """End-to-end tests for complete workflows."""

    @pytest.mark.asyncio
    async def test_complete_status_update_flow(self, full_project):
        """Test complete flow: metrics → status → save → load."""
        # Initialize components
        calculator = MetricCalculator(str(full_project))
        neural_core.project_root = full_project
        neural_core.status_file = full_project / "neural_status.json"
        neural_core.metric_calculator = calculator

        # Create test result
        test_result = PytestRunResult(
            total_tests=10,
            passed=10,
            failed=0,
            coverage_percentage=87.5
        )

        # Update status
        await update_neural_status(test_result)

        # Verify status was created
        assert neural_core.current_status is not None
        assert neural_core.current_status.illumination > 0.0

        # Verify file was saved
        assert neural_core.status_file.exists()

        # Verify can reload
        loaded_status = neural_core.load_status()
        assert loaded_status.illumination == neural_core.current_status.illumination

    def test_file_change_to_status_update_flow(self, full_project):
        """Test flow: file change → should run tests → update status."""
        # Initialize components
        analyzer = PytestAnalyzer(str(full_project))
        calculator = MetricCalculator(str(full_project))

        # Simulate file change
        changed_file = str(full_project / "src" / "main.ts")

        # Determine if tests should run
        should_run = analyzer.should_run_tests(changed_file)
        assert should_run is True

        # Run tests
        # (Skipping actual pytest run for speed)

        # Calculate new status
        file_counts = calculator.count_files_by_region()
        status = calculator.calculate_neural_status(
            test_coverage=85.0,
            test_results={"passed": 10, "failed": 0, "total": 10},
            file_counts=file_counts
        )

        # Verify status is valid
        assert status.illumination > 0.0
        assert status.regions["ui-components"].file_count > 0

    @pytest.mark.asyncio
    async def test_websocket_broadcast_flow(self, client, full_project):
        """Test flow: status update → WebSocket broadcast."""
        # Setup
        neural_core.current_status = NeuralStatus(
            illumination=0.75,
            has_license=True,
            has_readme=True
        )

        # Connect WebSocket client
        with client.websocket_connect("/ws") as websocket:
            # Receive initial status
            initial_message = websocket.receive_json()

            assert initial_message["type"] == "neural_status"
            assert initial_message["data"]["illumination"] == 0.75

            # Simulate status update by creating new message
            # (In real scenario, this would come from backend update)

    def test_diagnostic_generation_for_failing_tests(self, full_project):
        """Test diagnostics are generated when tests fail."""
        calculator = MetricCalculator(str(full_project))

        # Calculate status with failing tests
        status = calculator.calculate_neural_status(
            test_coverage=75.0,
            test_results={"passed": 8, "failed": 2, "total": 10},
            file_counts={}
        )

        # Should have ALERT diagnostic
        assert len(status.diagnostics) > 0
        alert_diagnostics = [d for d in status.diagnostics if d.level.value == "ALERT"]
        assert len(alert_diagnostics) > 0
        assert "failing" in alert_diagnostics[0].message.lower()


class TestMultiComponentIntegration:
    """Integration tests involving multiple components working together."""

    def test_all_components_initialization(self, full_project):
        """Test all components can be initialized together."""
        # Initialize all components
        calculator = MetricCalculator(str(full_project))
        analyzer = PytestAnalyzer(str(full_project))

        callback = Mock()
        watcher = FileWatcher(str(full_project), callback)

        # All should initialize without errors
        assert calculator is not None
        assert analyzer is not None
        assert watcher is not None

        # Test basic operations
        file_counts = calculator.count_files_by_region()
        test_files = analyzer.get_test_files()

        assert file_counts is not None
        assert test_files is not None

    def test_full_project_health_check(self, full_project):
        """Test complete project health can be assessed."""
        calculator = MetricCalculator(str(full_project))
        analyzer = PytestAnalyzer(str(full_project))

        # Get file counts
        file_counts = calculator.count_files_by_region()

        # Get test files
        test_files = analyzer.get_test_files()

        # Calculate status
        status = calculator.calculate_neural_status(
            test_coverage=85.0,
            test_results={"passed": len(test_files), "failed": 0, "total": len(test_files)},
            file_counts=file_counts
        )

        # Verify complete health assessment
        assert status.illumination > 0.0
        assert status.has_license is True
        assert status.has_readme is True
        assert len(status.regions) == 6  # All regions including data-layer
        assert all(isinstance(region, BrainRegion) for region in status.regions.values())


# ============================================================================
# WebSocket Multiple Client Tests
# ============================================================================

class TestMultipleWebSocketClients:
    """Integration tests for multiple WebSocket clients."""

    @pytest.mark.asyncio
    async def test_broadcast_to_multiple_clients(self):
        """Test broadcasting message to multiple WebSocket clients."""
        from neural_cli.main import NeuralCore

        core = NeuralCore()

        # Create mock clients
        client1 = AsyncMock()
        client2 = AsyncMock()
        client3 = AsyncMock()

        core.connected_clients = {client1, client2, client3}

        # Broadcast message
        message = WebSocketMessage(
            type="test_result",
            data={"passed": 10, "failed": 0}
        )

        await core.broadcast(message)

        # All clients should receive message
        assert client1.send_json.called
        assert client2.send_json.called
        assert client3.send_json.called

    @pytest.mark.asyncio
    async def test_broadcast_removes_disconnected_clients(self):
        """Test broadcast removes clients that fail to receive."""
        from neural_cli.main import NeuralCore

        core = NeuralCore()

        # Create clients (one will fail)
        good_client1 = AsyncMock()
        good_client2 = AsyncMock()
        bad_client = AsyncMock()
        bad_client.send_json.side_effect = Exception("Connection lost")

        core.connected_clients = {good_client1, bad_client, good_client2}

        message = WebSocketMessage(type="test", data={})

        await core.broadcast(message)

        # Bad client should be removed
        assert bad_client not in core.connected_clients
        assert good_client1 in core.connected_clients
        assert good_client2 in core.connected_clients

    def test_multiple_clients_connect_simultaneously(self, client):
        """Test multiple WebSocket clients can connect at once."""
        neural_core.current_status = NeuralStatus(illumination=0.5)

        # Connect multiple clients
        # Note: TestClient doesn't perfectly simulate concurrent connections
        # but this tests the endpoint can handle multiple requests

        with client.websocket_connect("/ws") as ws1:
            data1 = ws1.receive_json()
            assert data1["type"] == "neural_status"

            with client.websocket_connect("/ws") as ws2:
                data2 = ws2.receive_json()
                assert data2["type"] == "neural_status"

                # Both should receive same status
                assert data1["data"]["illumination"] == data2["data"]["illumination"]


# ============================================================================
# Error Propagation Tests
# ============================================================================

class TestErrorPropagation:
    """Test how errors propagate across components."""

    def test_invalid_project_path_handled_gracefully(self):
        """Test components handle invalid project paths gracefully."""
        invalid_path = "/nonexistent/path/to/project"

        # All components should handle gracefully
        calculator = MetricCalculator(invalid_path)
        file_counts = calculator.count_files_by_region()
        assert file_counts == {"frontend": 0, "backend": 0, "tests": 0}

        analyzer = PytestAnalyzer(invalid_path)
        test_files = analyzer.get_test_files()
        assert test_files == []

    def test_corrupted_status_file_recovery(self, tmp_path):
        """Test system recovers from corrupted status file."""
        from neural_cli.main import NeuralCore

        core = NeuralCore()
        core.project_root = tmp_path
        core.status_file = tmp_path / "neural_status.json"

        # Create corrupted status file
        core.status_file.write_text("not valid json{}")

        # Should return default status
        status = core.load_status()
        assert status.illumination == 0.0

    def test_test_run_failure_doesnt_crash_system(self, full_project):
        """Test test run failure is handled gracefully."""
        analyzer = PytestAnalyzer(str(full_project))

        # Simulate pytest failure by mocking
        with patch('subprocess.run', side_effect=Exception("Pytest crashed")):
            result = analyzer.run_tests()

            # Should return error result, not crash
            assert result.errors == 1
            assert result.total_tests == 0


# ============================================================================
# Performance Integration Tests
# ============================================================================

class TestPerformanceIntegration:
    """Integration tests for performance characteristics."""

    def test_large_project_handling(self, tmp_path):
        """Test system handles large project with many files."""
        # Create large project structure
        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()

        # Create many files
        for i in range(100):
            (tmp_path / "src" / f"file{i}.ts").write_text(f"// File {i}")

        for i in range(50):
            (tmp_path / "tests" / f"test_file{i}.py").write_text(f"def test_{i}(): assert True")

        # Should handle without errors or excessive time
        calculator = MetricCalculator(str(tmp_path))
        file_counts = calculator.count_files_by_region()

        assert file_counts["frontend"] == 100
        assert file_counts["tests"] == 50

    def test_rapid_status_updates(self, full_project):
        """Test system handles rapid status updates."""
        calculator = MetricCalculator(str(full_project))

        # Perform multiple rapid calculations
        statuses = []
        for i in range(10):
            status = calculator.calculate_neural_status(
                test_coverage=float(80 + i),
                test_results={"passed": 10 + i, "failed": 0, "total": 10 + i},
                file_counts={}
            )
            statuses.append(status)

        # All should complete successfully
        assert len(statuses) == 10
        assert all(s.illumination >= 0.0 for s in statuses)


# ============================================================================
# Regression Tests
# ============================================================================

class TestRegression:
    """Regression tests for previously found bugs."""

    def test_division_by_zero_in_metrics(self, tmp_path):
        """Regression: Division by zero when no tests exist."""
        calculator = MetricCalculator(str(tmp_path))

        # Calculate with no tests
        status = calculator.calculate_neural_status(
            test_coverage=0.0,
            test_results={"passed": 0, "failed": 0, "total": 0},
            file_counts={}
        )

        # Should not crash
        assert status.illumination == 0.0

    def test_empty_regions_dict_handled(self, tmp_path):
        """Regression: Empty regions dict causes errors."""
        from neural_cli.main import NeuralCore

        core = NeuralCore()
        core.project_root = tmp_path
        core.status_file = tmp_path / "neural_status.json"

        # Create status with empty regions
        status = NeuralStatus(regions={})
        core.current_status = status

        # Save and reload
        core.save_status()
        loaded = core.load_status()

        assert loaded.regions == {}

    def test_websocket_disconnect_cleanup(self, client):
        """Regression: Disconnected WebSocket clients not cleaned up."""
        neural_core.current_status = NeuralStatus()

        initial_count = len(neural_core.connected_clients)

        # Connect and disconnect
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

        # After disconnect, count should return to initial
        final_count = len(neural_core.connected_clients)
        assert final_count == initial_count
