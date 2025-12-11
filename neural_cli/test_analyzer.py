"""
Test Analyzer for CyberIDE Neural Core.

This module integrates with pytest to run tests, collect results,
and calculate coverage. It triggers test runs when files change
and reports results to the WebSocket server.
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime, timezone
import re

from .models import PytestRunResult


class PytestAnalyzer:
    """
    Analyzes test results and coverage for the project.

    Integrates with pytest and pytest-cov to get comprehensive
    test metrics that drive the neural illumination.
    """

    def __init__(self, project_root: str):
        """
        Initialize the test analyzer.

        Args:
            project_root: Absolute path to the project root directory
        """
        self.project_root = Path(project_root)
        self.tests_dir = self.project_root / "tests"
        self.coverage_file = self.project_root / ".coverage"
        self.pytest_cache = self.project_root / ".pytest_cache"

    def run_tests(
        self,
        path: Optional[str] = None,
        verbose: bool = True
    ) -> PytestRunResult:
        """
        Run pytest tests and collect results.

        Args:
            path: Specific test file or directory to run (None = all tests)
            verbose: Whether to show verbose output

        Returns:
            PytestRunResult object with test metrics and coverage
        """
        # Build pytest command using current python interpreter
        cmd = [sys.executable, "-m", "pytest"]

        # Add target path
        if path:
            cmd.append(str(path))
        elif self.tests_dir.exists():
            cmd.append(str(self.tests_dir))
        else:
            # No tests directory - return empty result
            return PytestRunResult(
                total_tests=0,
                passed=0,
                failed=0,
                coverage_percentage=0.0
            )

        # Add coverage arguments
        cmd.extend([
            "--cov=src",
            "--cov=neural_cli",
            "--cov-report=json",
            "--cov-report=term-missing",
            "--json-report",
            "--json-report-file=test_results.json"
        ])

        # Add verbosity
        if verbose:
            cmd.append("-v")

        # Add color output
        cmd.append("--color=yes")

        # Run pytest
        start_time = datetime.now(timezone.utc)
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()

            # Parse results
            test_result = self._parse_pytest_output(result, duration)

            return test_result

        except subprocess.TimeoutExpired:
            print("⚠ Test execution timeout after 5 minutes")
            return PytestRunResult(
                total_tests=0,
                passed=0,
                failed=1,
                errors=1,
                duration=300.0
            )
        except FileNotFoundError:
            print("❌ pytest not found. Install with: pip install pytest pytest-cov")
            return PytestRunResult(
                total_tests=0,
                passed=0,
                failed=0,
                errors=1
            )
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return PytestRunResult(
                total_tests=0,
                passed=0,
                failed=0,
                errors=1
            )

    def _parse_pytest_output(
        self,
        result: subprocess.CompletedProcess,
        duration: float
    ) -> PytestRunResult:
        """Parse pytest output and extract test metrics."""
        # Try to read JSON report first (most reliable)
        json_report = self.project_root / "test_results.json"
        if json_report.exists():
            try:
                with open(json_report, 'r') as f:
                    data = json.load(f)
                    return self._parse_json_report(data, duration)
            except Exception as e:
                print(f"⚠ Failed to parse JSON report: {e}")

        # Fallback: parse text output
        return self._parse_text_output(result.stdout, duration)

    def _parse_json_report(self, data: dict, duration: float) -> PytestRunResult:
        """Parse pytest JSON report."""
        summary = data.get("summary", {})

        # Get test counts
        total = summary.get("total", 0)
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        skipped = summary.get("skipped", 0)
        errors = summary.get("error", 0)

        # Get coverage
        coverage = self._read_coverage_report()

        # Get failed test details
        failed_tests = []
        for test in data.get("tests", []):
            if test.get("outcome") == "failed":
                failed_tests.append({
                    "name": test.get("nodeid", "unknown"),
                    "error": test.get("call", {}).get("longrepr", "")[:200]
                })

        return PytestRunResult(
            total_tests=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            coverage_percentage=coverage,
            duration=duration,
            failed_tests=failed_tests
        )

    def _parse_text_output(self, output: str, duration: float) -> PytestRunResult:
        """Parse pytest text output (fallback method)."""
        # Look for summary line like: "5 passed, 2 failed in 1.23s"
        summary_pattern = r'(\d+)\s+passed'
        failed_pattern = r'(\d+)\s+failed'
        skipped_pattern = r'(\d+)\s+skipped'
        error_pattern = r'(\d+)\s+error'

        passed = 0
        failed = 0
        skipped = 0
        errors = 0

        # Extract counts
        passed_match = re.search(summary_pattern, output)
        if passed_match:
            passed = int(passed_match.group(1))

        failed_match = re.search(failed_pattern, output)
        if failed_match:
            failed = int(failed_match.group(1))

        skipped_match = re.search(skipped_pattern, output)
        if skipped_match:
            skipped = int(skipped_match.group(1))

        error_match = re.search(error_pattern, output)
        if error_match:
            errors = int(error_match.group(1))

        total = passed + failed + skipped + errors

        # Get coverage
        coverage = self._read_coverage_report()

        return PytestRunResult(
            total_tests=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            coverage_percentage=coverage,
            duration=duration
        )

    def _read_coverage_report(self) -> float:
        """Read coverage percentage from coverage.json."""
        coverage_json = self.project_root / "coverage.json"
        if not coverage_json.exists():
            return 0.0

        try:
            with open(coverage_json, 'r') as f:
                data = json.load(f)
                total = data.get("totals", {})
                percent = total.get("percent_covered", 0.0)
                return round(percent, 2)
        except Exception as e:
            print(f"⚠ Failed to read coverage report: {e}")
            return 0.0

    def should_run_tests(self, file_path: str) -> bool:
        """
        Determine if tests should be run based on file change.

        Args:
            file_path: Path to the changed file

        Returns:
            True if tests should be run
        """
        path = Path(file_path)

        # Always run if test file changed
        if self._is_test_file(file_path):
            return True

        # Run if source file changed (in src/ or neural_cli/)
        if path.is_relative_to(self.project_root / "src"):
            return True
        if path.is_relative_to(self.project_root / "neural_cli"):
            return True

        # Don't run for other files (docs, config, etc.)
        return False

    def _is_test_file(self, file_path: str) -> bool:
        """Check if a file is a test file."""
        path = Path(file_path)
        return (
            path.name.startswith("test_") and
            path.suffix == ".py" and
            "tests" in path.parts
        )

    def get_test_files(self) -> List[Path]:
        """Get list of all test files in the project."""
        if not self.tests_dir.exists():
            return []

        return list(self.tests_dir.rglob("test_*.py"))

    def get_coverage_by_file(self) -> Dict[str, float]:
        """
        Get coverage percentage for each file.

        Returns:
            Dictionary mapping file paths to coverage percentages
        """
        coverage_json = self.project_root / "coverage.json"
        if not coverage_json.exists():
            return {}

        try:
            with open(coverage_json, 'r') as f:
                data = json.load(f)
                files = data.get("files", {})

                # Convert to percentages
                result = {}
                for file_path, stats in files.items():
                    summary = stats.get("summary", {})
                    percent = summary.get("percent_covered", 0.0)
                    result[file_path] = round(percent, 2)

                return result
        except Exception as e:
            print(f"⚠ Failed to read file coverage: {e}")
            return {}

    def format_test_summary(self, result: PytestRunResult) -> str:
        """
        Format test result as a colored terminal summary.

        Args:
            result: PytestRunResult object

        Returns:
            Formatted string for terminal output
        """
        # Status emoji
        if result.failed > 0 or result.errors > 0:
            status = "❌ TESTS FAILED"
            color = "\033[91m"  # Red
        elif result.total_tests == 0:
            status = "⚠ NO TESTS"
            color = "\033[93m"  # Yellow
        else:
            status = "✓ TESTS PASSED"
            color = "\033[92m"  # Green

        reset = "\033[0m"

        # Build summary
        lines = [
            f"\n{color}{'=' * 50}{reset}",
            f"{color}{status}{reset}",
            f"{color}{'=' * 50}{reset}",
            f"Total:   {result.total_tests}",
            f"Passed:  {result.passed}",
            f"Failed:  {result.failed}",
            f"Skipped: {result.skipped}",
            f"Errors:  {result.errors}",
            f"Coverage: {result.coverage_percentage:.1f}%",
            f"Duration: {result.duration:.2f}s",
        ]

        # Add failed test details
        if result.failed_tests:
            lines.append(f"\n{color}Failed Tests:{reset}")
            for test in result.failed_tests:
                lines.append(f"  - {test['name']}")
                if test.get('error'):
                    lines.append(f"    {test['error'][:100]}...")

        lines.append(f"{color}{'=' * 50}{reset}\n")

        return "\n".join(lines)

    def create_placeholder_tests(self) -> None:
        """
        Create placeholder test directory structure.

        This is useful for initializing a new project.
        """
        # Create tests directory
        self.tests_dir.mkdir(exist_ok=True)

        # Create __init__.py
        init_file = self.tests_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Test suite for CyberIDE."""\n')

        # Create conftest.py with fixtures
        conftest = self.tests_dir / "conftest.py"
        if not conftest.exists():
            conftest.write_text('''"""
Pytest configuration and fixtures.
"""

import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_data():
    """Return sample test data."""
    return {
        "test_value": 42,
        "test_string": "Hello, Neural Core!"
    }
''')

        # Create sample test file
        sample_test = self.tests_dir / "test_sample.py"
        if not sample_test.exists():
            sample_test.write_text('''"""
Sample test file to validate test infrastructure.
"""


def test_sample_pass():
    """A passing test to light up the neural circuits."""
    assert True, "This test always passes"


def test_basic_math():
    """Test basic arithmetic."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6


def test_with_fixture(sample_data):
    """Test using a fixture."""
    assert sample_data["test_value"] == 42
    assert "Neural" in sample_data["test_string"]
''')

        print("✓ Created placeholder test structure")
        print(f"  - {self.tests_dir}/")
        print(f"  - {init_file.name}")
        print(f"  - {conftest.name}")
        print(f"  - {sample_test.name}")
