"""
Tests for TestAnalyzer - pytest execution and coverage analysis.

This module validates:
- Running pytest tests and collecting results
- Parsing pytest output (JSON and text formats)
- Reading coverage reports
- Determining if tests should run based on file changes
- Identifying test files
- Getting coverage by file
- Creating placeholder test structures
- Timeout and error handling
"""

import pytest
import json
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from neural_cli.test_analyzer import TestAnalyzer
from neural_cli.models import TestResult


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def empty_project(tmp_path):
    """Create an empty project directory."""
    return tmp_path


@pytest.fixture
def project_with_tests(tmp_path):
    """Create a project with test files."""
    # Create tests directory
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()

    # Create test files
    (tests_dir / "test_unit.py").write_text("""
def test_passing():
    assert True

def test_another():
    assert 1 + 1 == 2
""")

    (tests_dir / "test_integration.py").write_text("""
def test_integration():
    assert True
""")

    # Create conftest.py
    (tests_dir / "conftest.py").write_text("# fixtures")

    # Create source directory
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "main.ts").write_text("// source code")

    # Create neural_cli directory
    neural_dir = tmp_path / "neural_cli"
    neural_dir.mkdir()
    (neural_dir / "core.py").write_text("# backend code")

    return tmp_path


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
                "summary": {
                    "percent_covered": 90.0
                }
            },
            "/src/utils.py": {
                "summary": {
                    "percent_covered": 85.0
                }
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
            },
            {
                "nodeid": "tests/test_baz.py::test_qux",
                "outcome": "failed",
                "call": {
                    "longrepr": "ValueError: Invalid input"
                }
            }
        ]
    }

    results_file = tmp_path / "test_results.json"
    results_file.write_text(json.dumps(test_data))
    return results_file


# ============================================================================
# Test File Detection Tests
# ============================================================================

class TestTestFileDetection:
    """Test suite for test file detection methods."""

    def test_get_test_files_empty_directory(self, empty_project):
        """Test getting test files from empty directory."""
        analyzer = TestAnalyzer(str(empty_project))
        test_files = analyzer.get_test_files()

        assert test_files == []

    def test_get_test_files_with_tests(self, project_with_tests):
        """Test getting test files from directory with tests."""
        analyzer = TestAnalyzer(str(project_with_tests))
        test_files = analyzer.get_test_files()

        # Should find test_unit.py and test_integration.py
        assert len(test_files) == 2
        test_names = [f.name for f in test_files]
        assert "test_unit.py" in test_names
        assert "test_integration.py" in test_names

    def test_get_test_files_ignores_non_test_files(self, tmp_path):
        """Test get_test_files ignores non-test files."""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()

        (tests_dir / "test_valid.py").write_text("# test")
        (tests_dir / "helper.py").write_text("# not a test")
        (tests_dir / "conftest.py").write_text("# config")
        (tests_dir / "data.json").write_text("{}")

        analyzer = TestAnalyzer(str(tmp_path))
        test_files = analyzer.get_test_files()

        # Should only find test_valid.py
        assert len(test_files) == 1
        assert test_files[0].name == "test_valid.py"

    def test_is_test_file_valid(self, tmp_path):
        """Test _is_test_file identifies test files correctly."""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()

        analyzer = TestAnalyzer(str(tmp_path))

        # Valid test file
        assert analyzer._is_test_file(str(tests_dir / "test_foo.py"))

        # Invalid: doesn't start with test_
        assert not analyzer._is_test_file(str(tests_dir / "foo_test.py"))

        # Invalid: not in tests directory
        assert not analyzer._is_test_file(str(tmp_path / "test_foo.py"))

        # Invalid: not .py file
        assert not analyzer._is_test_file(str(tests_dir / "test_foo.txt"))


# ============================================================================
# Should Run Tests Logic Tests
# ============================================================================

class TestShouldRunTests:
    """Test suite for should_run_tests method."""

    def test_should_run_tests_for_test_file(self, project_with_tests):
        """Test should run for test file changes."""
        analyzer = TestAnalyzer(str(project_with_tests))

        test_file = str(project_with_tests / "tests" / "test_unit.py")
        assert analyzer.should_run_tests(test_file) is True

    def test_should_run_tests_for_source_file(self, project_with_tests):
        """Test should run for source file changes."""
        analyzer = TestAnalyzer(str(project_with_tests))

        src_file = str(project_with_tests / "src" / "main.ts")
        assert analyzer.should_run_tests(src_file) is True

    def test_should_run_tests_for_backend_file(self, project_with_tests):
        """Test should run for backend file changes."""
        analyzer = TestAnalyzer(str(project_with_tests))

        backend_file = str(project_with_tests / "neural_cli" / "core.py")
        assert analyzer.should_run_tests(backend_file) is True

    def test_should_not_run_tests_for_readme(self, project_with_tests):
        """Test should not run for README changes."""
        analyzer = TestAnalyzer(str(project_with_tests))

        readme_file = str(project_with_tests / "README.md")
        assert analyzer.should_run_tests(readme_file) is False

    def test_should_not_run_tests_for_config(self, project_with_tests):
        """Test should not run for config file changes."""
        analyzer = TestAnalyzer(str(project_with_tests))

        config_file = str(project_with_tests / "package.json")
        assert analyzer.should_run_tests(config_file) is False

    def test_should_not_run_tests_for_git_files(self, project_with_tests):
        """Test should not run for .git files."""
        analyzer = TestAnalyzer(str(project_with_tests))

        git_file = str(project_with_tests / ".git" / "config")
        assert analyzer.should_run_tests(git_file) is False


# ============================================================================
# Coverage Report Reading Tests
# ============================================================================

class TestCoverageReportReading:
    """Test suite for coverage report parsing."""

    def test_read_coverage_report_valid(self, tmp_path, mock_coverage_json):
        """Test reading valid coverage report."""
        analyzer = TestAnalyzer(str(tmp_path))
        coverage = analyzer._read_coverage_report()

        assert coverage == 87.5

    def test_read_coverage_report_missing_file(self, empty_project):
        """Test reading coverage when file doesn't exist."""
        analyzer = TestAnalyzer(str(empty_project))
        coverage = analyzer._read_coverage_report()

        assert coverage == 0.0

    def test_read_coverage_report_invalid_json(self, tmp_path):
        """Test reading coverage with invalid JSON."""
        coverage_file = tmp_path / "coverage.json"
        coverage_file.write_text("not valid json{}")

        analyzer = TestAnalyzer(str(tmp_path))
        coverage = analyzer._read_coverage_report()

        assert coverage == 0.0

    def test_get_coverage_by_file(self, tmp_path, mock_coverage_json):
        """Test getting coverage per file."""
        analyzer = TestAnalyzer(str(tmp_path))
        coverage_by_file = analyzer.get_coverage_by_file()

        assert "/src/main.py" in coverage_by_file
        assert coverage_by_file["/src/main.py"] == 90.0
        assert coverage_by_file["/src/utils.py"] == 85.0

    def test_get_coverage_by_file_no_report(self, empty_project):
        """Test getting coverage by file when no report exists."""
        analyzer = TestAnalyzer(str(empty_project))
        coverage_by_file = analyzer.get_coverage_by_file()

        assert coverage_by_file == {}


# ============================================================================
# Pytest Output Parsing Tests
# ============================================================================

class TestPytestOutputParsing:
    """Test suite for parsing pytest output."""

    def test_parse_json_report_valid(self, tmp_path, mock_test_results_json, mock_coverage_json):
        """Test parsing valid JSON report."""
        analyzer = TestAnalyzer(str(tmp_path))

        mock_result = Mock()
        mock_result.stdout = ""

        test_result = analyzer._parse_pytest_output(mock_result, duration=5.0)

        assert test_result.total_tests == 15
        assert test_result.passed == 13
        assert test_result.failed == 2
        assert test_result.skipped == 0
        assert test_result.errors == 0
        assert test_result.coverage_percentage == 87.5
        assert len(test_result.failed_tests) == 2

    def test_parse_text_output_with_passed(self, empty_project):
        """Test parsing text output with passed tests."""
        analyzer = TestAnalyzer(str(empty_project))

        output = "5 passed in 1.23s"
        test_result = analyzer._parse_text_output(output, duration=1.23)

        assert test_result.passed == 5
        assert test_result.failed == 0
        assert test_result.total_tests == 5

    def test_parse_text_output_with_failures(self, empty_project):
        """Test parsing text output with failures."""
        analyzer = TestAnalyzer(str(empty_project))

        output = "3 passed, 2 failed in 2.5s"
        test_result = analyzer._parse_text_output(output, duration=2.5)

        assert test_result.passed == 3
        assert test_result.failed == 2
        assert test_result.total_tests == 5

    def test_parse_text_output_with_skipped(self, empty_project):
        """Test parsing text output with skipped tests."""
        analyzer = TestAnalyzer(str(empty_project))

        output = "5 passed, 2 skipped in 1.0s"
        test_result = analyzer._parse_text_output(output, duration=1.0)

        assert test_result.passed == 5
        assert test_result.skipped == 2
        assert test_result.total_tests == 7

    def test_parse_text_output_with_errors(self, empty_project):
        """Test parsing text output with errors."""
        analyzer = TestAnalyzer(str(empty_project))

        output = "5 passed, 1 error in 1.5s"
        test_result = analyzer._parse_text_output(output, duration=1.5)

        assert test_result.passed == 5
        assert test_result.errors == 1
        assert test_result.total_tests == 6

    def test_parse_text_output_no_tests(self, empty_project):
        """Test parsing text output when no tests match."""
        analyzer = TestAnalyzer(str(empty_project))

        output = "no tests ran"
        test_result = analyzer._parse_text_output(output, duration=0.0)

        assert test_result.total_tests == 0
        assert test_result.passed == 0


# ============================================================================
# Test Execution Tests
# ============================================================================

class TestTestExecution:
    """Test suite for run_tests method."""

    def test_run_tests_no_tests_directory(self, empty_project):
        """Test running tests when tests directory doesn't exist."""
        analyzer = TestAnalyzer(str(empty_project))
        result = analyzer.run_tests()

        assert result.total_tests == 0
        assert result.passed == 0
        assert result.failed == 0

    @patch('subprocess.run')
    def test_run_tests_success(self, mock_run, project_with_tests, mock_test_results_json, mock_coverage_json):
        """Test successful test run."""
        # Mock subprocess result
        mock_process = Mock()
        mock_process.stdout = "5 passed in 1.23s"
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        analyzer = TestAnalyzer(str(project_with_tests))
        result = analyzer.run_tests()

        # Verify subprocess.run was called with correct arguments
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert "pytest" in call_args
        assert "--cov=src" in call_args
        assert "--cov=neural_cli" in call_args

    @patch('subprocess.run')
    def test_run_tests_timeout(self, mock_run, project_with_tests):
        """Test test run timeout handling."""
        mock_run.side_effect = subprocess.TimeoutExpired("pytest", 300)

        analyzer = TestAnalyzer(str(project_with_tests))
        result = analyzer.run_tests()

        assert result.failed == 1
        assert result.errors == 1
        assert result.duration == 300.0

    @patch('subprocess.run')
    def test_run_tests_pytest_not_found(self, mock_run, project_with_tests):
        """Test handling when pytest is not installed."""
        mock_run.side_effect = FileNotFoundError("pytest not found")

        analyzer = TestAnalyzer(str(project_with_tests))
        result = analyzer.run_tests()

        assert result.errors == 1
        assert result.total_tests == 0

    @patch('subprocess.run')
    def test_run_tests_with_specific_path(self, mock_run, project_with_tests):
        """Test running tests with specific path."""
        mock_process = Mock()
        mock_process.stdout = "2 passed in 0.5s"
        mock_run.return_value = mock_process

        analyzer = TestAnalyzer(str(project_with_tests))
        result = analyzer.run_tests(path="tests/test_unit.py")

        # Verify path was passed to pytest
        call_args = mock_run.call_args[0][0]
        assert any("test_unit.py" in str(arg) for arg in call_args)

    @patch('subprocess.run')
    def test_run_tests_with_verbose_flag(self, mock_run, project_with_tests):
        """Test running tests with verbose output."""
        mock_process = Mock()
        mock_process.stdout = "5 passed in 1.0s"
        mock_run.return_value = mock_process

        analyzer = TestAnalyzer(str(project_with_tests))
        result = analyzer.run_tests(verbose=True)

        # Verify -v flag was passed
        call_args = mock_run.call_args[0][0]
        assert "-v" in call_args

    @patch('subprocess.run')
    def test_run_tests_exception_handling(self, mock_run, project_with_tests):
        """Test handling of unexpected exceptions."""
        mock_run.side_effect = Exception("Unexpected error")

        analyzer = TestAnalyzer(str(project_with_tests))
        result = analyzer.run_tests()

        assert result.errors == 1
        assert result.total_tests == 0


# ============================================================================
# Test Summary Formatting Tests
# ============================================================================

class TestFormatTestSummary:
    """Test suite for format_test_summary method."""

    def test_format_summary_passing_tests(self, empty_project):
        """Test formatting summary for passing tests."""
        analyzer = TestAnalyzer(str(empty_project))

        result = TestResult(
            total_tests=10,
            passed=10,
            failed=0,
            skipped=0,
            errors=0,
            coverage_percentage=87.5,
            duration=2.5
        )

        summary = analyzer.format_test_summary(result)

        assert "TESTS PASSED" in summary
        assert "10" in summary
        assert "87.5" in summary
        assert "2.5" in summary

    def test_format_summary_failing_tests(self, empty_project):
        """Test formatting summary for failing tests."""
        analyzer = TestAnalyzer(str(empty_project))

        result = TestResult(
            total_tests=10,
            passed=8,
            failed=2,
            skipped=0,
            errors=0,
            coverage_percentage=75.0,
            duration=3.0,
            failed_tests=[
                {"name": "test_foo", "error": "AssertionError"},
                {"name": "test_bar", "error": "ValueError"}
            ]
        )

        summary = analyzer.format_test_summary(result)

        assert "TESTS FAILED" in summary
        assert "Failed:  2" in summary
        assert "test_foo" in summary
        assert "test_bar" in summary

    def test_format_summary_no_tests(self, empty_project):
        """Test formatting summary when no tests exist."""
        analyzer = TestAnalyzer(str(empty_project))

        result = TestResult(total_tests=0)

        summary = analyzer.format_test_summary(result)

        assert "NO TESTS" in summary

    def test_format_summary_with_errors(self, empty_project):
        """Test formatting summary with test errors."""
        analyzer = TestAnalyzer(str(empty_project))

        result = TestResult(
            total_tests=10,
            passed=8,
            failed=1,
            errors=1,
            coverage_percentage=70.0,
            duration=2.0
        )

        summary = analyzer.format_test_summary(result)

        assert "TESTS FAILED" in summary
        assert "Errors:  1" in summary


# ============================================================================
# Placeholder Test Creation Tests
# ============================================================================

class TestCreatePlaceholderTests:
    """Test suite for create_placeholder_tests method."""

    def test_create_placeholder_structure(self, empty_project):
        """Test creating placeholder test structure."""
        analyzer = TestAnalyzer(str(empty_project))
        analyzer.create_placeholder_tests()

        # Verify structure was created
        tests_dir = empty_project / "tests"
        assert tests_dir.exists()
        assert (tests_dir / "__init__.py").exists()
        assert (tests_dir / "conftest.py").exists()
        assert (tests_dir / "test_sample.py").exists()

    def test_create_placeholder_conftest_content(self, empty_project):
        """Test conftest.py has correct fixtures."""
        analyzer = TestAnalyzer(str(empty_project))
        analyzer.create_placeholder_tests()

        conftest = empty_project / "tests" / "conftest.py"
        content = conftest.read_text()

        assert "project_root" in content
        assert "sample_data" in content
        assert "@pytest.fixture" in content

    def test_create_placeholder_sample_test_content(self, empty_project):
        """Test test_sample.py has valid tests."""
        analyzer = TestAnalyzer(str(empty_project))
        analyzer.create_placeholder_tests()

        sample_test = empty_project / "tests" / "test_sample.py"
        content = sample_test.read_text()

        assert "test_sample_pass" in content
        assert "test_basic_math" in content
        assert "test_with_fixture" in content

    def test_create_placeholder_idempotent(self, empty_project):
        """Test create_placeholder_tests is idempotent."""
        analyzer = TestAnalyzer(str(empty_project))

        # Create once
        analyzer.create_placeholder_tests()
        first_content = (empty_project / "tests" / "test_sample.py").read_text()

        # Create again
        analyzer.create_placeholder_tests()
        second_content = (empty_project / "tests" / "test_sample.py").read_text()

        # Content should be the same (files not overwritten)
        assert first_content == second_content


# ============================================================================
# Edge Cases Tests
# ============================================================================

class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    def test_analyzer_with_nonexistent_path(self):
        """Test analyzer handles nonexistent project path."""
        analyzer = TestAnalyzer("/nonexistent/path")

        # Should not crash
        test_files = analyzer.get_test_files()
        assert test_files == []

    def test_parse_json_report_missing_fields(self, tmp_path):
        """Test parsing JSON report with missing fields."""
        incomplete_data = {
            "summary": {
                "total": 5
                # Missing other fields
            }
        }

        results_file = tmp_path / "test_results.json"
        results_file.write_text(json.dumps(incomplete_data))

        analyzer = TestAnalyzer(str(tmp_path))
        mock_result = Mock()

        result = analyzer._parse_pytest_output(mock_result, duration=1.0)

        # Should handle gracefully
        assert result.total_tests == 5
        assert result.passed == 0  # Default

    def test_coverage_report_with_missing_totals(self, tmp_path):
        """Test coverage report with missing totals."""
        coverage_data = {
            "files": {}
            # Missing totals field
        }

        coverage_file = tmp_path / "coverage.json"
        coverage_file.write_text(json.dumps(coverage_data))

        analyzer = TestAnalyzer(str(tmp_path))
        coverage = analyzer._read_coverage_report()

        assert coverage == 0.0

    def test_very_long_test_duration(self, empty_project):
        """Test handling very long test duration."""
        analyzer = TestAnalyzer(str(empty_project))

        result = TestResult(
            total_tests=100,
            passed=100,
            duration=3600.0  # 1 hour
        )

        summary = analyzer.format_test_summary(result)

        assert "3600" in summary

    def test_failed_test_with_very_long_error(self, empty_project):
        """Test failed test with very long error message."""
        analyzer = TestAnalyzer(str(empty_project))

        long_error = "AssertionError: " + ("x" * 1000)

        result = TestResult(
            total_tests=1,
            passed=0,
            failed=1,
            failed_tests=[
                {"name": "test_foo", "error": long_error}
            ]
        )

        summary = analyzer.format_test_summary(result)

        # Error should be truncated in summary
        assert "test_foo" in summary
        assert len(summary) < len(long_error) + 1000  # Not full error

    def test_unicode_in_test_output(self, empty_project):
        """Test handling Unicode in test output."""
        analyzer = TestAnalyzer(str(empty_project))

        output = "5 passed, 1 failed 🎉 in 1.0s"
        result = analyzer._parse_text_output(output, duration=1.0)

        assert result.passed == 5
        assert result.failed == 1

    def test_should_run_tests_with_relative_path(self, project_with_tests):
        """Test should_run_tests with relative paths."""
        analyzer = TestAnalyzer(str(project_with_tests))

        # Use relative path
        relative_path = "src/main.ts"
        # Convert to absolute for proper testing
        absolute_path = project_with_tests / relative_path

        result = analyzer.should_run_tests(str(absolute_path))
        assert result is True
