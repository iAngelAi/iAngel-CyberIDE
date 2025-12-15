"""
Tests for MetricCalculator - Business logic for neural illumination calculation.

This module validates:
- File counting by region (frontend, backend, tests)
- Neural status calculation with weighted scoring
- Documentation score calculation
- Module completion metrics
- Integration score calculation
- Illumination percentage (0.0-1.0)
- Diagnostic generation for issues
- Edge cases (empty project, no tests, missing files)
"""

import pytest
import json
from pathlib import Path
from datetime import datetime

from neural_cli.metric_calculator import MetricCalculator
from neural_cli.models import (
    NeuralStatus,
    BrainRegion,
    RegionStatus,
    DiagnosticLevel
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def empty_project(tmp_path):
    """Create an empty project directory."""
    return tmp_path


@pytest.fixture
def minimal_project(tmp_path):
    """Create a minimal project with basic structure."""
    # Create directories
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "neural_cli").mkdir()

    # Create minimal files
    (tmp_path / "README.md").write_text("# Test Project\n" + ("x" * 600))  # >500 bytes
    (tmp_path / "LICENSE").write_text("MIT License")

    # Create some source files
    (tmp_path / "src" / "main.ts").write_text("console.log('hello');")
    (tmp_path / "neural_cli" / "core.py").write_text("# Python backend")
    (tmp_path / "tests" / "test_sample.py").write_text("def test_pass(): assert True")

    return tmp_path


@pytest.fixture
def full_project(tmp_path):
    """Create a full project with all components."""
    # Create directories
    (tmp_path / "src" / "components").mkdir(parents=True)
    (tmp_path / "src" / "hooks").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "neural_cli").mkdir()

    # Create documentation
    (tmp_path / "README.md").write_text("# Full Project\n" + ("x" * 1000))
    (tmp_path / "LICENSE").write_text("MIT License")
    (tmp_path / "CLAUDE.md").write_text("# Project Instructions")
    (tmp_path / "SETUP.md").write_text("# Setup Guide")

    # Create frontend files (15 files)
    for i in range(15):
        (tmp_path / "src" / "components" / f"Component{i}.tsx").write_text(f"export const Component{i} = () => null;")

    # Create backend files (8 files)
    for i in range(8):
        (tmp_path / "neural_cli" / f"module{i}.py").write_text(f"# Module {i}")

    # Create test files (10 files)
    for i in range(10):
        (tmp_path / "tests" / f"test_module{i}.py").write_text(f"def test_{i}(): assert True")

    # Create config files
    (tmp_path / "package.json").write_text("{}")
    (tmp_path / "requirements.txt").write_text("pytest\nfastapi")
    (tmp_path / "vite.config.ts").write_text("export default {}")

    # Create .env for API configuration
    (tmp_path / ".env").write_text("API_KEY=test_key_123")

    return tmp_path


# ============================================================================
# File Counting Tests
# ============================================================================

class TestCountFilesByRegion:
    """Test suite for count_files_by_region method."""

    def test_count_files_empty_project(self, empty_project):
        """Test counting files in empty project returns zeros."""
        calculator = MetricCalculator(str(empty_project))
        counts = calculator.count_files_by_region()

        assert counts["frontend"] == 0
        assert counts["backend"] == 0
        assert counts["tests"] == 0

    def test_count_files_minimal_project(self, minimal_project):
        """Test counting files in minimal project."""
        calculator = MetricCalculator(str(minimal_project))
        counts = calculator.count_files_by_region()

        assert counts["frontend"] == 1  # main.ts
        assert counts["backend"] == 1  # core.py
        assert counts["tests"] == 1  # test_sample.py

    def test_count_files_full_project(self, full_project):
        """Test counting files in full project."""
        calculator = MetricCalculator(str(full_project))
        counts = calculator.count_files_by_region()

        assert counts["frontend"] == 15
        assert counts["backend"] == 8
        assert counts["tests"] == 10

    def test_count_files_ignores_pycache(self, tmp_path):
        """Test that __pycache__ files are not counted."""
        (tmp_path / "neural_cli").mkdir()
        (tmp_path / "neural_cli" / "module.py").write_text("# code")
        (tmp_path / "neural_cli" / "__pycache__").mkdir()
        (tmp_path / "neural_cli" / "__pycache__" / "module.pyc").write_text("")
        (tmp_path / "neural_cli" / "__init__.py").write_text("")

        calculator = MetricCalculator(str(tmp_path))
        counts = calculator.count_files_by_region()

        # Should count module.py but not __init__.py or .pyc files
        assert counts["backend"] == 1

    def test_count_files_only_python_in_backend(self, tmp_path):
        """Test backend only counts .py files."""
        (tmp_path / "neural_cli").mkdir()
        (tmp_path / "neural_cli" / "module.py").write_text("# code")
        (tmp_path / "neural_cli" / "notes.txt").write_text("notes")
        (tmp_path / "neural_cli" / "README.md").write_text("docs")

        calculator = MetricCalculator(str(tmp_path))
        counts = calculator.count_files_by_region()

        # Should only count .py files
        assert counts["backend"] == 1

    def test_count_files_only_test_prefix(self, tmp_path):
        """Test tests directory only counts test_*.py files."""
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_foo.py").write_text("# test")
        (tmp_path / "tests" / "test_bar.py").write_text("# test")
        (tmp_path / "tests" / "helper.py").write_text("# helper")
        (tmp_path / "tests" / "conftest.py").write_text("# config")

        calculator = MetricCalculator(str(tmp_path))
        counts = calculator.count_files_by_region()

        # Should only count test_*.py files
        assert counts["tests"] == 2

    def test_count_files_recursive_counting(self, tmp_path):
        """Test file counting is recursive in subdirectories."""
        (tmp_path / "src" / "components" / "ui").mkdir(parents=True)
        (tmp_path / "src" / "components" / "Button.tsx").write_text("// button")
        (tmp_path / "src" / "components" / "ui" / "Input.tsx").write_text("// input")
        # Créer un répertoire src/hooks pour le test
        (tmp_path / "src" / "hooks").mkdir(parents=True)
        (tmp_path / "src" / "hooks" / "useAuth.ts").write_text("// hook")

        calculator = MetricCalculator(str(tmp_path))
        counts = calculator.count_files_by_region()

        # Should count all TypeScript/JavaScript files recursively
        assert counts["frontend"] == 3


# ============================================================================
# Neural Status Calculation Tests
# ============================================================================

class TestCalculateNeuralStatus:
    """Test suite for calculate_neural_status method."""

    def test_calculate_status_empty_project(self, empty_project):
        """Test status calculation for empty project."""
        calculator = MetricCalculator(str(empty_project))

        status = calculator.calculate_neural_status(
            test_coverage=0.0,
            test_results={"passed": 0, "failed": 0, "total": 0},
            file_counts={"frontend": 0, "backend": 0, "tests": 0}
        )

        assert status.illumination == 0.0
        assert status.has_license is False
        assert status.has_readme is False

    def test_calculate_status_with_tests(self, minimal_project):
        """Test status calculation with passing tests."""
        calculator = MetricCalculator(str(minimal_project))

        status = calculator.calculate_neural_status(
            test_coverage=85.0,
            test_results={"passed": 10, "failed": 0, "total": 10},
            file_counts={"frontend": 5, "backend": 5, "tests": 5}
        )

        assert status.illumination > 0.0
        assert status.has_license is True
        assert status.has_readme is True
        assert "ui-components" in status.regions
        assert "core-logic" in status.regions
        assert "tests" in status.regions

    def test_calculate_status_failing_tests(self, minimal_project):
        """Test status with failing tests generates diagnostics."""
        calculator = MetricCalculator(str(minimal_project))

        status = calculator.calculate_neural_status(
            test_coverage=75.0,
            test_results={"passed": 8, "failed": 2, "total": 10},
            file_counts={"frontend": 5, "backend": 5, "tests": 5}
        )

        # Should have diagnostic for failing tests
        assert len(status.diagnostics) > 0
        alert_diagnostics = [d for d in status.diagnostics if d.level == DiagnosticLevel.ALERT]
        assert len(alert_diagnostics) > 0
        assert "failing" in alert_diagnostics[0].message.lower()

    def test_calculate_status_low_coverage(self, minimal_project):
        """Test status with low coverage generates caution diagnostic."""
        calculator = MetricCalculator(str(minimal_project))

        status = calculator.calculate_neural_status(
            test_coverage=30.0,  # Low coverage
            test_results={"passed": 5, "failed": 0, "total": 5},
            file_counts={"frontend": 10, "backend": 10, "tests": 3}
        )

        # Should have caution diagnostic for low coverage
        caution_diagnostics = [d for d in status.diagnostics if d.level == DiagnosticLevel.CAUTION]
        assert len(caution_diagnostics) > 0
        coverage_warnings = [d for d in caution_diagnostics if "coverage" in d.message.lower()]
        assert len(coverage_warnings) > 0

    def test_calculate_status_illumination_bounds(self, full_project):
        """Test illumination is clamped to 0.0-1.0."""
        calculator = MetricCalculator(str(full_project))

        # Perfect project should have high illumination
        status = calculator.calculate_neural_status(
            test_coverage=100.0,
            test_results={"passed": 50, "failed": 0, "total": 50},
            file_counts={"frontend": 15, "backend": 8, "tests": 10}
        )

        assert 0.0 <= status.illumination <= 1.0

    def test_calculate_status_regions_created(self, minimal_project):
        """Test all brain regions are created."""
        calculator = MetricCalculator(str(minimal_project))

        status = calculator.calculate_neural_status(
            test_coverage=80.0,
            test_results={"passed": 10, "failed": 0, "total": 10},
            file_counts={"frontend": 5, "backend": 5, "tests": 5}
        )

        # Should have all 6 regions (domain-driven names)
        assert "ui-components" in status.regions
        assert "core-logic" in status.regions
        assert "data-layer" in status.regions
        assert "tests" in status.regions
        assert "documentation" in status.regions
        assert "api-integration" in status.regions

    def test_calculate_status_region_status_healthy(self, minimal_project):
        """Test regions are HEALTHY with good metrics."""
        calculator = MetricCalculator(str(minimal_project))

        status = calculator.calculate_neural_status(
            test_coverage=90.0,
            test_results={"passed": 10, "failed": 0, "total": 10},
            file_counts={"frontend": 5, "backend": 5, "tests": 5}
        )

        # With high coverage and no failures, regions should be healthy
        assert status.regions["tests"].status == RegionStatus.HEALTHY

    def test_calculate_status_region_status_error(self, minimal_project):
        """Test regions are ERROR with failing tests."""
        calculator = MetricCalculator(str(minimal_project))

        status = calculator.calculate_neural_status(
            test_coverage=80.0,
            test_results={"passed": 8, "failed": 2, "total": 10},
            file_counts={"frontend": 5, "backend": 5, "tests": 5}
        )

        # With failures, test regions should be in error
        assert status.regions["tests"].status == RegionStatus.ERROR


# ============================================================================
# Documentation Score Tests
# ============================================================================

class TestDocumentationScore:
    """Test suite for _calculate_documentation_score method."""

    def test_documentation_score_empty(self, empty_project):
        """Test documentation score for project with no docs."""
        calculator = MetricCalculator(str(empty_project))
        score = calculator._calculate_documentation_score()

        assert score == 0.0

    def test_documentation_score_readme_only(self, tmp_path):
        """Test documentation score with only README."""
        (tmp_path / "README.md").write_text("# Project\n" + ("x" * 600))  # >500 bytes

        calculator = MetricCalculator(str(tmp_path))
        score = calculator._calculate_documentation_score()

        # README is worth 30 points
        assert score == 30.0

    def test_documentation_score_readme_too_small(self, tmp_path):
        """Test README under 500 bytes doesn't count."""
        (tmp_path / "README.md").write_text("# Short")  # <500 bytes

        calculator = MetricCalculator(str(tmp_path))
        score = calculator._calculate_documentation_score()

        assert score == 0.0

    def test_documentation_score_with_license(self, tmp_path):
        """Test documentation score includes LICENSE."""
        (tmp_path / "README.md").write_text("# Project\n" + ("x" * 600))
        (tmp_path / "LICENSE").write_text("MIT License")

        calculator = MetricCalculator(str(tmp_path))
        score = calculator._calculate_documentation_score()

        # README (30) + LICENSE (20) = 50
        assert score == 50.0

    def test_documentation_score_with_claude_md(self, tmp_path):
        """Test documentation score includes CLAUDE.md."""
        (tmp_path / "README.md").write_text("# Project\n" + ("x" * 600))
        (tmp_path / "LICENSE").write_text("MIT License")
        (tmp_path / "CLAUDE.md").write_text("# Instructions")

        calculator = MetricCalculator(str(tmp_path))
        score = calculator._calculate_documentation_score()

        # README (30) + LICENSE (20) + CLAUDE.md (20) = 70
        assert score == 70.0

    def test_documentation_score_with_setup_guide(self, tmp_path):
        """Test documentation score includes setup guide."""
        (tmp_path / "README.md").write_text("# Project\n" + ("x" * 600))
        (tmp_path / "LICENSE").write_text("MIT License")
        (tmp_path / "CLAUDE.md").write_text("# Instructions")
        (tmp_path / "SETUP.md").write_text("# Setup")

        calculator = MetricCalculator(str(tmp_path))
        score = calculator._calculate_documentation_score()

        # README (30) + LICENSE (20) + CLAUDE.md (20) + SETUP (15) = 85
        assert score == 85.0

    def test_documentation_score_maximum(self, tmp_path):
        """Test documentation score is capped at 100."""
        (tmp_path / "README.md").write_text("# Project\n" + ("x" * 600))
        (tmp_path / "LICENSE").write_text("MIT License")
        (tmp_path / "CLAUDE.md").write_text("# Instructions")
        (tmp_path / "SETUP.md").write_text("# Setup")
        (tmp_path / "openapi.json").write_text("{}")

        calculator = MetricCalculator(str(tmp_path))
        score = calculator._calculate_documentation_score()

        # Total would be 115, but should be capped at 100
        assert score == 100.0


# ============================================================================
# Module Completion Tests
# ============================================================================

class TestModuleCompletion:
    """Test suite for _calculate_module_completion method."""

    def test_module_completion_empty(self, empty_project):
        """Test module completion for empty project."""
        calculator = MetricCalculator(str(empty_project))

        counts = {"frontend": 0, "backend": 0, "tests": 0}
        score = calculator._calculate_module_completion(counts)

        assert score == 0.0

    def test_module_completion_with_frontend(self, tmp_path):
        """Test module completion with frontend files."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.ts").write_text("// code")

        calculator = MetricCalculator(str(tmp_path))
        counts = {"frontend": 1, "backend": 0, "tests": 0}
        score = calculator._calculate_module_completion(counts)

        # Frontend files = 25 points
        assert score == 25.0

    def test_module_completion_with_backend(self, tmp_path):
        """Test module completion with backend files."""
        (tmp_path / "neural_cli").mkdir()
        (tmp_path / "neural_cli" / "core.py").write_text("# code")

        calculator = MetricCalculator(str(tmp_path))
        counts = {"frontend": 0, "backend": 1, "tests": 0}
        score = calculator._calculate_module_completion(counts)

        # Backend files = 25 points
        assert score == 25.0

    def test_module_completion_with_tests(self, tmp_path):
        """Test module completion with test files."""
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_foo.py").write_text("# test")

        calculator = MetricCalculator(str(tmp_path))
        counts = {"frontend": 0, "backend": 0, "tests": 1}
        score = calculator._calculate_module_completion(counts)

        # Test files = 30 points
        assert score == 30.0

    def test_module_completion_with_config_files(self, tmp_path):
        """Test module completion includes config files."""
        (tmp_path / "package.json").write_text("{}")
        (tmp_path / "requirements.txt").write_text("pytest")
        (tmp_path / "vite.config.ts").write_text("export default {}")

        calculator = MetricCalculator(str(tmp_path))
        counts = {"frontend": 0, "backend": 0, "tests": 0}
        score = calculator._calculate_module_completion(counts)

        # All 3 config files = 20 points
        assert score == 20.0

    def test_module_completion_full_project(self, full_project):
        """Test module completion for full project."""
        calculator = MetricCalculator(str(full_project))
        counts = {"frontend": 15, "backend": 8, "tests": 10}
        score = calculator._calculate_module_completion(counts)

        # Frontend (25) + Backend (25) + Tests (30) + Configs (20) = 100
        assert score == 100.0


# ============================================================================
# Integration Score Tests
# ============================================================================

class TestIntegrationScore:
    """Test suite for _calculate_integration_score method."""

    def test_integration_score_empty(self, empty_project):
        """Test integration score for project with no integrations."""
        calculator = MetricCalculator(str(empty_project))
        score = calculator._calculate_integration_score()

        assert score == 0.0

    def test_integration_score_with_env_file(self, tmp_path):
        """Test integration score with .env file."""
        (tmp_path / ".env").write_text("API_KEY=test123")

        calculator = MetricCalculator(str(tmp_path))
        score = calculator._calculate_integration_score()

        # .env file = 50 points
        assert score == 50.0

    def test_integration_score_empty_env_file(self, tmp_path):
        """Test integration score with empty .env file."""
        (tmp_path / ".env").write_text("")  # Too small

        calculator = MetricCalculator(str(tmp_path))
        score = calculator._calculate_integration_score()

        # Empty .env doesn't count
        assert score == 0.0

    def test_integration_score_with_mcp_providers(self, tmp_path):
        """Test integration score with MCP providers."""
        # Create .gemini/settings.json
        (tmp_path / ".gemini").mkdir()
        gemini_settings = {
            "mcpServers": {
                "provider1": {},
                "provider2": {}
            }
        }
        (tmp_path / ".gemini" / "settings.json").write_text(json.dumps(gemini_settings))

        calculator = MetricCalculator(str(tmp_path))
        score = calculator._calculate_integration_score()

        # 2 providers = 30 points (2 * 15)
        assert score == 30.0

    def test_integration_score_with_multiple_config_files(self, tmp_path):
        """Test integration score with MCP providers from multiple files."""
        # Create .gemini/settings.json
        (tmp_path / ".gemini").mkdir()
        gemini_settings = {
            "mcpServers": {
                "provider1": {},
                "provider2": {}
            }
        }
        (tmp_path / ".gemini" / "settings.json").write_text(json.dumps(gemini_settings))

        # Create .github/mcp-configuration.json
        (tmp_path / ".github").mkdir()
        github_config = {
            "mcpServers": {
                "provider2": {}, # Duplicate
                "provider3": {}
            }
        }
        (tmp_path / ".github" / "mcp-configuration.json").write_text(json.dumps(github_config))

        calculator = MetricCalculator(str(tmp_path))
        score = calculator._calculate_integration_score()

        # 3 unique providers (provider1, provider2, provider3) = 45 points (3 * 15)
        assert score == 45.0

    def test_integration_score_maximum(self, tmp_path):
        """Test integration score is capped at 100."""
        (tmp_path / ".env").write_text("API_KEY=test123")

        # Create .gemini/settings.json with many providers
        (tmp_path / ".gemini").mkdir()
        gemini_settings = {
            "mcpServers": {f"provider{i}": {} for i in range(10)}
        }
        (tmp_path / ".gemini" / "settings.json").write_text(json.dumps(gemini_settings))

        calculator = MetricCalculator(str(tmp_path))
        score = calculator._calculate_integration_score()

        # Should be capped at 100
        assert score == 100.0


# ============================================================================
# Illumination Calculation Tests
# ============================================================================

class TestIlluminationCalculation:
    """Test suite for _calculate_illumination method."""

    def test_illumination_weighted_calculation(self, minimal_project):
        """Test illumination uses weighted scoring."""
        calculator = MetricCalculator(str(minimal_project))

        from neural_cli.models import ProjectMetrics

        # Create metrics with known values
        metrics = ProjectMetrics(
            test_coverage=100.0,  # 35% weight
            documentation_score=100.0,  # 15% weight
            module_completion=100.0,  # 25% weight
            integration_score=100.0,  # 15% weight
            overall_health=100.0
        )

        illumination = calculator._calculate_illumination(metrics)

        # With all 100%, illumination should be high
        assert illumination >= 0.9

    def test_illumination_bounds(self, minimal_project):
        """Test illumination is always 0.0-1.0."""
        calculator = MetricCalculator(str(minimal_project))

        from neural_cli.models import ProjectMetrics

        metrics = ProjectMetrics(overall_health=0.0)
        illumination = calculator._calculate_illumination(metrics)
        assert 0.0 <= illumination <= 1.0

        metrics = ProjectMetrics(overall_health=100.0)
        illumination = calculator._calculate_illumination(metrics)
        assert 0.0 <= illumination <= 1.0


# ============================================================================
# Diagnostic Generation Tests
# ============================================================================

class TestDiagnosticGeneration:
    """Test suite for _generate_diagnostics method."""

    def test_diagnostic_for_failing_tests(self, minimal_project):
        """Test diagnostic generated for failing tests."""
        calculator = MetricCalculator(str(minimal_project))

        status = calculator.calculate_neural_status(
            test_coverage=80.0,
            test_results={"passed": 8, "failed": 2, "total": 10},
            file_counts={}
        )

        # Should have ALERT diagnostic
        alerts = [d for d in status.diagnostics if d.level == DiagnosticLevel.ALERT]
        assert len(alerts) > 0
        assert "failing" in alerts[0].message.lower()

    def test_diagnostic_for_low_coverage(self, minimal_project):
        """Test diagnostic generated for low coverage."""
        calculator = MetricCalculator(str(minimal_project))

        status = calculator.calculate_neural_status(
            test_coverage=30.0,  # Below 50%
            test_results={"passed": 5, "failed": 0, "total": 5},
            file_counts={}
        )

        # Should have CAUTION diagnostic
        cautions = [d for d in status.diagnostics if d.level == DiagnosticLevel.CAUTION]
        coverage_cautions = [d for d in cautions if "coverage" in d.message.lower()]
        assert len(coverage_cautions) > 0

    def test_diagnostic_for_missing_documentation(self, empty_project):
        """Test diagnostic generated for missing documentation."""
        calculator = MetricCalculator(str(empty_project))

        status = calculator.calculate_neural_status(
            test_coverage=80.0,
            test_results={"passed": 10, "failed": 0, "total": 10},
            file_counts={}
        )

        # Should have diagnostic about documentation
        doc_diagnostics = [d for d in status.diagnostics if "documentation" in d.message.lower()]
        assert len(doc_diagnostics) > 0

    def test_no_diagnostics_for_healthy_project(self, full_project):
        """Test no diagnostics for healthy project."""
        calculator = MetricCalculator(str(full_project))

        status = calculator.calculate_neural_status(
            test_coverage=85.0,
            test_results={"passed": 50, "failed": 0, "total": 50},
            file_counts={"frontend": 15, "backend": 8, "tests": 10}
        )

        # Should have few or no diagnostics
        # (Might have CAUTION for API, depending on setup)
        alerts = [d for d in status.diagnostics if d.level == DiagnosticLevel.ALERT]
        assert len(alerts) == 0


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    def test_nonexistent_directory(self):
        """Test calculator handles nonexistent directory."""
        calculator = MetricCalculator("/nonexistent/path")

        # Should not crash
        counts = calculator.count_files_by_region()
        assert counts["frontend"] == 0
        assert counts["backend"] == 0
        assert counts["tests"] == 0

    def test_division_by_zero_protection(self, empty_project):
        """Test calculator handles zero division gracefully."""
        calculator = MetricCalculator(str(empty_project))

        # Calculate with no tests
        status = calculator.calculate_neural_status(
            test_coverage=0.0,
            test_results={"passed": 0, "failed": 0, "total": 0},
            file_counts={"frontend": 0, "backend": 0, "tests": 0}
        )

        # Should not crash, illumination should be 0
        assert status.illumination == 0.0

    def test_very_large_file_counts(self, tmp_path):
        """Test calculator handles large numbers of files."""
        calculator = MetricCalculator(str(tmp_path))

        # Simulate large project
        large_counts = {"frontend": 1000, "backend": 500, "tests": 300}

        status = calculator.calculate_neural_status(
            test_coverage=85.0,
            test_results={"passed": 300, "failed": 0, "total": 300},
            file_counts=large_counts
        )

        assert status is not None
        assert 0.0 <= status.illumination <= 1.0

    def test_unicode_in_file_paths(self, tmp_path):
        """Test calculator handles Unicode in file paths."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "émoji_🎉.ts").write_text("// unicode test")

        calculator = MetricCalculator(str(tmp_path))
        counts = calculator.count_files_by_region()

        # Should count the file
        assert counts["frontend"] == 1

    def test_symlinks_handling(self, tmp_path):
        """Test calculator handles symbolic links."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "real_file.ts").write_text("// real")

        # Create symlink
        try:
            (tmp_path / "src" / "link.ts").symlink_to(tmp_path / "src" / "real_file.ts")
        except OSError:
            pytest.skip("Symlinks not supported on this system")

        calculator = MetricCalculator(str(tmp_path))
        counts = calculator.count_files_by_region()

        # Behavior depends on how pathlib handles symlinks
        assert counts["frontend"] >= 1
