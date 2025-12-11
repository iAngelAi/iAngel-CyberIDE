"""
Pytest configuration and fixtures.

This module provides shared fixtures for all test files:
- Project structure fixtures (empty, minimal, full projects)
- Mock objects for testing
- Temporary directory management
- Sample data for validation
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock


# ============================================================================
# Project Structure Fixtures
# ============================================================================

@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def empty_project(tmp_path):
    """Create an empty project directory for testing."""
    return tmp_path


@pytest.fixture
def minimal_project(tmp_path):
    """
    Create a minimal project with basic structure.

    Structure:
    - src/main.ts
    - tests/test_sample.py
    - neural_cli/core.py
    - README.md (>500 bytes)
    - LICENSE
    """
    # Create directories
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "neural_cli").mkdir()

    # Create documentation
    (tmp_path / "README.md").write_text("# Test Project\n" + ("x" * 600))
    (tmp_path / "LICENSE").write_text("MIT License")

    # Create source files
    (tmp_path / "src" / "main.ts").write_text("console.log('hello');")
    (tmp_path / "neural_cli" / "core.py").write_text("# Python backend")
    (tmp_path / "tests" / "test_sample.py").write_text("def test_pass(): assert True")

    return tmp_path


@pytest.fixture
def full_project(tmp_path):
    """
    Create a full-featured project for comprehensive testing.

    Structure:
    - src/ with multiple TypeScript files
    - tests/ with multiple test files
    - neural_cli/ with multiple Python modules
    - Complete documentation (README, LICENSE, CLAUDE.md, SETUP.md)
    - Configuration files (package.json, requirements.txt, vite.config.ts)
    - .env file for API configuration
    """
    # Create directory structure
    (tmp_path / "src" / "components").mkdir(parents=True)
    (tmp_path / "src" / "hooks").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "neural_cli").mkdir()

    # Create documentation
    (tmp_path / "README.md").write_text("# Full Project\n" + ("x" * 1000))
    (tmp_path / "LICENSE").write_text("MIT License")
    (tmp_path / "CLAUDE.md").write_text("# Project Instructions")
    (tmp_path / "SETUP.md").write_text("# Setup Guide")

    # Create frontend files
    for i in range(5):
        (tmp_path / "src" / "components" / f"Component{i}.tsx").write_text(
            f"export const Component{i} = () => null;"
        )

    # Create backend files
    for i in range(3):
        (tmp_path / "neural_cli" / f"module{i}.py").write_text(f"# Module {i}")

    # Create test files
    for i in range(5):
        (tmp_path / "tests" / f"test_module{i}.py").write_text(
            f"def test_{i}(): assert True"
        )

    # Create configuration files
    (tmp_path / "package.json").write_text("{}")
    (tmp_path / "requirements.txt").write_text("pytest\nfastapi")
    (tmp_path / "vite.config.ts").write_text("export default {}")

    # Create .env for API configuration
    (tmp_path / ".env").write_text("API_KEY=test_key_123")

    return tmp_path


# ============================================================================
# Data Fixtures
# ============================================================================

@pytest.fixture
def sample_data():
    """Return sample test data."""
    return {
        "test_value": 42,
        "test_string": "Hello, Neural Core!"
    }


@pytest.fixture
def sample_test_result():
    """Return a sample PytestRunResult object."""
    from neural_cli.models import PytestRunResult

    return PytestRunResult(
        total_tests=10,
        passed=9,
        failed=1,
        skipped=0,
        errors=0,
        coverage_percentage=85.5,
        duration=2.5,
        failed_tests=[
            {"name": "test_edge_case", "error": "AssertionError: Expected 5, got 3"}
        ]
    )


@pytest.fixture
def sample_neural_status():
    """Return a sample NeuralStatus object."""
    from neural_cli.models import NeuralStatus, BrainRegion, RegionStatus

    return NeuralStatus(
        illumination=0.75,
        regions={
            "ui-components": BrainRegion(
                status=RegionStatus.HEALTHY,
                coverage=95.0,
                test_count=10,
                passing_tests=10,
                failing_tests=0,
                file_count=15
            ),
            "core-logic": BrainRegion(
                status=RegionStatus.HEALTHY,
                coverage=87.0,
                test_count=8,
                passing_tests=8,
                failing_tests=0,
                file_count=10
            )
        },
        has_license=True,
        has_readme=True,
        documentation_complete=True,
        api_configured=False,
        mcp_providers_count=0
    )


@pytest.fixture
def mock_coverage_json(tmp_path):
    """Create a mock coverage.json file."""
    coverage_data = {
        "totals": {
            "percent_covered": 87.5,
            "num_statements": 100,
            "missing_lines": 12
        },
        "files": {
            "/src/main.py": {
                "summary": {"percent_covered": 90.0}
            },
            "/src/utils.py": {
                "summary": {"percent_covered": 85.0}
            }
        }
    }

    coverage_file = tmp_path / "coverage.json"
    coverage_file.write_text(json.dumps(coverage_data))
    return coverage_file


@pytest.fixture
def mock_test_results_json(tmp_path):
    """Create a mock test_results.json file."""
    test_data = {
        "summary": {
            "total": 15,
            "passed": 13,
            "failed": 2,
            "skipped": 0,
            "error": 0
        },
        "tests": [
            {
                "nodeid": "tests/test_foo.py::test_bar",
                "outcome": "failed",
                "call": {
                    "longrepr": "AssertionError: Expected 5, got 3"
                }
            }
        ]
    }

    results_file = tmp_path / "test_results.json"
    results_file.write_text(json.dumps(test_data))
    return results_file


# ============================================================================
# Mock Object Fixtures
# ============================================================================

@pytest.fixture
def mock_callback():
    """Create a mock callback function for event handlers."""
    return Mock()


@pytest.fixture
def mock_async_callback():
    """Create a mock async callback function."""
    return AsyncMock()


# ============================================================================
# Configuration
# ============================================================================

@pytest.fixture(autouse=True)
def reset_neural_core():
    """
    Reset neural_core state before each test.

    This prevents test pollution where one test's changes
    affect another test.
    """
    from neural_cli.main import neural_core

    # Store original values
    original_test_running = neural_core.test_running
    original_connected_clients = neural_core.connected_clients.copy()

    # Reset to clean state
    neural_core.test_running = False
    neural_core.connected_clients.clear()

    yield

    # Restore after test
    neural_core.test_running = original_test_running
    neural_core.connected_clients = original_connected_clients


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
