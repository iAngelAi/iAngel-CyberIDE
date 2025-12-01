"""
Metric Calculator for Neural Illumination.

This module calculates the overall brain illumination percentage (0-100%)
based on various project health metrics: test coverage, documentation,
module completion, and integration status.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timezone

from .models import (
    NeuralStatus,
    BrainRegion,
    RegionStatus,
    ProjectMetrics,
    Diagnostic,
    DiagnosticLevel
)


class MetricCalculator:
    """
    Calculates project health metrics and brain illumination.

    The illumination is progressive: as critical milestones are achieved,
    more neural circuits light up in the 3D brain visualization.
    """

    def __init__(self, project_root: str):
        """
        Initialize the metric calculator.

        Args:
            project_root: Absolute path to the project root directory
        """
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        self.tests_dir = self.project_root / "tests"
        self.neural_cli_dir = self.project_root / "neural_cli"

        # Weight factors for overall illumination (must sum to 1.0)
        self.weights = {
            "test_coverage": 0.35,      # 35% - Most critical
            "documentation": 0.15,       # 15% - Important for production
            "module_completion": 0.25,   # 25% - Code completeness
            "integration": 0.15,         # 15% - API/MCP configured
            "production_ready": 0.10     # 10% - All tests passing
        }

    def calculate_neural_status(
        self,
        test_coverage: float = 0.0,
        test_results: Dict = None,
        file_counts: Dict[str, int] = None
    ) -> NeuralStatus:
        """
        Calculate the complete neural status of the project.

        Args:
            test_coverage: Test coverage percentage (0-100)
            test_results: Dictionary with test results (passed, failed, total)
            file_counts: Dictionary with file counts per region

        Returns:
            NeuralStatus object with calculated illumination and regions
        """
        test_results = test_results or {"passed": 0, "failed": 0, "total": 0}
        file_counts = file_counts or {}

        # Calculate individual metrics
        metrics = self._calculate_metrics(test_coverage, test_results, file_counts)

        # Create brain regions
        regions = self._create_regions(test_results, file_counts, test_coverage)

        # Calculate overall illumination (0.0 to 1.0)
        illumination = self._calculate_illumination(metrics)

        # Generate diagnostics
        diagnostics = self._generate_diagnostics(regions, metrics, test_results)

        # Build neural status
        status = NeuralStatus(
            illumination=illumination,
            regions=regions,
            diagnostics=diagnostics,
            timestamp=datetime.now(timezone.utc),
            has_license=self._check_file_exists("LICENSE"),
            has_readme=self._check_file_exists("README.md"),
            documentation_complete=(metrics.documentation_score >= 80.0),
            api_configured=self._check_api_configured(),
            mcp_providers_count=self._count_mcp_providers()
        )

        return status

    def _calculate_metrics(
        self,
        test_coverage: float,
        test_results: Dict,
        file_counts: Dict[str, int]
    ) -> ProjectMetrics:
        """Calculate detailed project metrics."""
        # Test coverage metric (0-100)
        coverage_metric = test_coverage

        # Documentation metric (0-100)
        doc_score = self._calculate_documentation_score()

        # Module completion metric (0-100)
        # Based on presence of key files and directories
        module_score = self._calculate_module_completion(file_counts)

        # Integration metric (0-100)
        # Based on API configuration and MCP providers
        integration_score = self._calculate_integration_score()

        # Overall health (weighted average)
        overall_health = (
            coverage_metric * self.weights["test_coverage"] +
            doc_score * self.weights["documentation"] +
            module_score * self.weights["module_completion"] +
            integration_score * self.weights["integration"]
        )

        return ProjectMetrics(
            total_files=sum(file_counts.values()),
            test_coverage=coverage_metric,
            documentation_score=doc_score,
            module_completion=module_score,
            integration_score=integration_score,
            overall_health=overall_health
        )

    def _calculate_illumination(self, metrics: ProjectMetrics) -> float:
        """
        Calculate overall brain illumination (0.0 to 1.0).

        This is the key metric that determines how much of the 3D brain
        is illuminated in the visualization.
        """
        # Start with overall health (0-100)
        base_illumination = metrics.overall_health

        # Bonus for production readiness (all tests passing)
        # This adds up to 10% extra illumination
        if self._check_production_ready():
            base_illumination += 10.0

        # Normalize to 0.0-1.0 range
        illumination = min(base_illumination / 100.0, 1.0)

        return illumination

    def _create_regions(
        self,
        test_results: Dict,
        file_counts: Dict[str, int],
        test_coverage: float
    ) -> Dict[str, BrainRegion]:
        """Create brain region objects for each major component."""
        regions = {}

        # UI Components region (src/components, src/hooks, etc.)
        # Maps to frontend files
        ui_files = file_counts.get("frontend", 0)
        regions["ui-components"] = BrainRegion(
            status=self._determine_region_status(test_coverage, test_results, "ui-components"),
            coverage=test_coverage if ui_files > 0 else 0.0,
            test_count=test_results.get("total", 0),
            passing_tests=test_results.get("passed", 0),
            failing_tests=test_results.get("failed", 0),
            file_count=ui_files,
            last_modified=datetime.now(timezone.utc)
        )

        # Core Logic region (neural_cli/)
        # Maps to backend files
        core_files = file_counts.get("backend", 0)
        regions["core-logic"] = BrainRegion(
            status=self._determine_region_status(test_coverage, test_results, "core-logic"),
            coverage=test_coverage if core_files > 0 else 0.0,
            test_count=test_results.get("total", 0),
            passing_tests=test_results.get("passed", 0),
            failing_tests=test_results.get("failed", 0),
            file_count=core_files,
            last_modified=datetime.now(timezone.utc)
        )

        # Data Layer region (currently empty, reserved for future database/storage layer)
        # Will be used when data persistence is added
        regions["data-layer"] = BrainRegion(
            status=RegionStatus.OFFLINE,
            coverage=0.0,
            test_count=0,
            passing_tests=0,
            failing_tests=0,
            file_count=0,
            last_modified=datetime.now(timezone.utc)
        )

        # Tests region
        test_files = file_counts.get("tests", 0)
        regions["tests"] = BrainRegion(
            status=self._determine_region_status(test_coverage, test_results, "tests"),
            coverage=test_coverage,
            test_count=test_results.get("total", 0),
            passing_tests=test_results.get("passed", 0),
            failing_tests=test_results.get("failed", 0),
            file_count=test_files,
            last_modified=datetime.now(timezone.utc)
        )

        # Documentation region
        doc_score = self._calculate_documentation_score()
        regions["documentation"] = BrainRegion(
            status=RegionStatus.HEALTHY if doc_score >= 80 else RegionStatus.WARNING,
            coverage=doc_score,
            test_count=0,
            passing_tests=0,
            failing_tests=0,
            file_count=len(list(self.project_root.glob("*.md"))),
            last_modified=datetime.now(timezone.utc)
        )

        # API Integration region (APIs, MCP)
        # Maps to integration score
        integration_score = self._calculate_integration_score()
        regions["api-integration"] = BrainRegion(
            status=RegionStatus.HEALTHY if integration_score >= 50 else RegionStatus.OFFLINE,
            coverage=integration_score,
            test_count=0,
            passing_tests=0,
            failing_tests=0,
            file_count=self._count_mcp_providers(),
            last_modified=datetime.now(timezone.utc)
        )

        return regions

    def _determine_region_status(
        self,
        coverage: float,
        test_results: Dict,
        region_name: str
    ) -> RegionStatus:
        """Determine the status (color) of a brain region."""
        has_failures = test_results.get("failed", 0) > 0

        if has_failures:
            return RegionStatus.ERROR  # Red pulsing
        elif coverage < 50:
            return RegionStatus.WARNING  # Yellow
        elif coverage < 80:
            return RegionStatus.HEALTHY  # Green
        else:
            return RegionStatus.HEALTHY  # Bright green

    def _generate_diagnostics(
        self,
        regions: Dict[str, BrainRegion],
        metrics: ProjectMetrics,
        test_results: Dict
    ) -> List[Diagnostic]:
        """Generate diagnostic messages for issues detected."""
        diagnostics = []

        # Check for failing tests
        if test_results.get("failed", 0) > 0:
            diagnostics.append(Diagnostic(
                level=DiagnosticLevel.ALERT,
                region="tests",
                message=f"ALERT: {test_results['failed']} test(s) failing",
                details="Immediate attention required. Tests must pass for production readiness."
            ))

        # Check for low coverage
        if metrics.test_coverage < 50:
            diagnostics.append(Diagnostic(
                level=DiagnosticLevel.CAUTION,
                region="tests",
                message=f"CAUTION: Low test coverage ({metrics.test_coverage:.1f}%)",
                details="Medium risk. Aim for at least 80% coverage."
            ))

        # Check for missing documentation
        if metrics.documentation_score < 60:
            diagnostics.append(Diagnostic(
                level=DiagnosticLevel.CAUTION,
                region="documentation",
                message="CAUTION: Incomplete documentation",
                details="Missing critical documentation files (README, LICENSE, or API docs)."
            ))

        # Check for API configuration
        if metrics.integration_score < 30:
            diagnostics.append(Diagnostic(
                level=DiagnosticLevel.CAUTION,
                region="integration",
                message="CAUTION: API/MCP not configured",
                details="No external integrations detected. Configure API keys or MCP providers."
            ))

        return diagnostics

    def _calculate_documentation_score(self) -> float:
        """Calculate documentation completeness score (0-100)."""
        score = 0.0

        # README exists and has content (30 points)
        readme_path = self.project_root / "README.md"
        if readme_path.exists() and readme_path.stat().st_size > 500:
            score += 30.0

        # LICENSE exists (20 points)
        if self._check_file_exists("LICENSE") or self._check_file_exists("LICENSE.md"):
            score += 20.0

        # CLAUDE.md or project instructions (20 points)
        if (self.project_root / "CLAUDE.md").exists():
            score += 20.0

        # API documentation or OpenAPI spec (15 points)
        api_docs = list(self.project_root.glob("**/openapi*.{json,yaml,yml}"))
        if api_docs:
            score += 15.0

        # Setup/installation guide (15 points)
        if (self.project_root / "SETUP.md").exists() or \
           (self.project_root / "QUICKSTART.md").exists():
            score += 15.0

        return min(score, 100.0)

    def _calculate_module_completion(self, file_counts: Dict[str, int]) -> float:
        """Calculate module completion score (0-100)."""
        score = 0.0

        # Frontend files exist (25 points)
        if file_counts.get("frontend", 0) > 0:
            score += 25.0

        # Backend files exist (25 points)
        if file_counts.get("backend", 0) > 0:
            score += 25.0

        # Test files exist (30 points)
        if file_counts.get("tests", 0) > 0:
            score += 30.0

        # Config files exist (20 points)
        config_files = ["package.json", "requirements.txt", "vite.config.ts"]
        existing_configs = sum(1 for f in config_files if self._check_file_exists(f))
        score += (existing_configs / len(config_files)) * 20.0

        return min(score, 100.0)

    def _calculate_integration_score(self) -> float:
        """Calculate integration/API configuration score (0-100)."""
        score = 0.0

        # API configuration exists (50 points)
        if self._check_api_configured():
            score += 50.0

        # MCP providers configured (50 points)
        mcp_count = self._count_mcp_providers()
        if mcp_count > 0:
            score += min(mcp_count * 15, 50.0)

        return min(score, 100.0)

    def _check_file_exists(self, filename: str) -> bool:
        """Check if a file exists in the project root."""
        return (self.project_root / filename).exists()

    def _check_api_configured(self) -> bool:
        """Check if API is configured (placeholder for now)."""
        # Check for .env file or config with API keys
        env_file = self.project_root / ".env"
        if env_file.exists():
            # Very basic check - just see if it has content
            return env_file.stat().st_size > 10

        # Check for neural_status.json with api_configured flag
        status_file = self.project_root / "neural_status.json"
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    data = json.load(f)
                    return data.get("api_configured", False)
            except:
                pass

        return False

    def _count_mcp_providers(self) -> int:
        """Count configured MCP providers (placeholder for now)."""
        # This will be implemented when MCP integration is added
        # For now, check for a hypothetical mcp_config.json
        mcp_config = self.project_root / "mcp_config.json"
        if mcp_config.exists():
            try:
                with open(mcp_config, 'r') as f:
                    data = json.load(f)
                    return len(data.get("providers", []))
            except:
                pass
        return 0

    def _check_production_ready(self) -> bool:
        """Check if project is production ready (all critical tests passing)."""
        # This will be set by the test analyzer
        status_file = self.project_root / "neural_status.json"
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    data = json.load(f)
                    # Check if there are tests and all are passing
                    for region_name, region_data in data.get("regions", {}).items():
                        if region_data.get("failing_tests", 0) > 0:
                            return False
                    # If we have tests and none are failing, production ready
                    total_tests = sum(
                        r.get("test_count", 0)
                        for r in data.get("regions", {}).values()
                    )
                    return total_tests > 0
            except:
                pass
        return False

    def count_files_by_region(self) -> Dict[str, int]:
        """
        Count files in each major region of the project.

        Returns:
            Dictionary mapping region names to file counts
        """
        counts = {
            "frontend": 0,
            "backend": 0,
            "tests": 0
        }

        # Count frontend files (src/)
        if self.src_dir.exists():
            counts["frontend"] = len([
                f for f in self.src_dir.rglob("*")
                if f.is_file() and f.suffix in [".ts", ".tsx", ".js", ".jsx"]
            ])

        # Count backend files (neural_cli/)
        if self.neural_cli_dir.exists():
            counts["backend"] = len([
                f for f in self.neural_cli_dir.rglob("*.py")
                if f.is_file() and not f.name.startswith("__")
            ])

        # Count test files
        if self.tests_dir.exists():
            counts["tests"] = len([
                f for f in self.tests_dir.rglob("test_*.py")
                if f.is_file()
            ])

        return counts
