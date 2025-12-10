"""
Regression Detector for CyberIDE Neural Core.

This module detects subtle regressions in project health by comparing
current metrics against historical baselines. Unlike binary test failures,
this catches progressive degradation in coverage, performance, and quality.
"""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from .models import NeuralStatus, Diagnostic, DiagnosticLevel


@dataclass
class RegressionAlert:
    """
    Alert for detected regression in project metrics.
    
    Attributes:
        metric: Name of the metric that regressed
        old_value: Previous value
        new_value: Current value
        severity: "minor", "moderate", or "critical"
        message: Human-readable alert message
        region: Affected brain region (if applicable)
    """
    metric: str
    old_value: float
    new_value: float
    severity: str
    message: str
    region: Optional[str] = None


class RegressionDetector:
    """
    Detects regressions by comparing current status against historical data.
    
    This enables proactive detection of quality degradation before it
    becomes critical (e.g., coverage slowly dropping from 85% to 70%).
    """
    
    def __init__(self, project_root: str, max_history: int = 10):
        """
        Initialize regression detector.
        
        Args:
            project_root: Absolute path to project root
            max_history: Maximum number of historical snapshots to keep
        """
        self.project_root = Path(project_root)
        self.history_file = self.project_root / "neural_history.json"
        self.max_history = max_history
        
        # Configurable thresholds for alerts
        self.thresholds = {
            "coverage_drop": 5.0,         # Alert if coverage drops >5%
            "illumination_drop": 0.1,     # Alert if illumination drops >10%
            "failed_tests_increase": 1,   # Alert if any test starts failing
            "minor_coverage_drop": 2.0,   # Minor alert for >2% drop
            "region_coverage_drop": 10.0  # Alert if region coverage drops >10%
        }
    
    def detect_regressions(
        self, current_status: NeuralStatus
    ) -> List[RegressionAlert]:
        """
        Compare current status with historical baseline to detect regressions.
        
        Args:
            current_status: Current neural status
            
        Returns:
            List of regression alerts (empty if no regressions)
        """
        alerts: List[RegressionAlert] = []
        
        # Load historical data
        history = self._load_history()
        if not history:
            # No baseline yet, can't detect regressions
            return alerts
        
        # Get most recent historical status for comparison
        last_status_data = history[-1]
        
        # Check global illumination regression
        illumination_alerts = self._check_illumination_regression(
            current_status, last_status_data
        )
        alerts.extend(illumination_alerts)
        
        # Check per-region regressions
        region_alerts = self._check_region_regressions(
            current_status, last_status_data
        )
        alerts.extend(region_alerts)
        
        # Check test failure increases
        test_alerts = self._check_test_regressions(
            current_status, last_status_data
        )
        alerts.extend(test_alerts)
        
        return alerts
    
    def _check_illumination_regression(
        self, current: NeuralStatus, last_data: dict
    ) -> List[RegressionAlert]:
        """Check for global illumination drop."""
        alerts = []
        
        last_illumination = last_data.get("illumination", 0.0)
        illumination_drop = last_illumination - current.illumination
        
        if illumination_drop > self.thresholds["illumination_drop"]:
            severity = "critical" if illumination_drop > 0.2 else "moderate"
            alerts.append(RegressionAlert(
                metric="illumination",
                old_value=last_illumination,
                new_value=current.illumination,
                severity=severity,
                message=f"Overall health dropped {illumination_drop:.1%} "
                        f"({last_illumination:.1%} → {current.illumination:.1%})",
                region="overall"
            ))
        
        return alerts
    
    def _check_region_regressions(
        self, current: NeuralStatus, last_data: dict
    ) -> List[RegressionAlert]:
        """Check for per-region coverage/health regressions."""
        alerts = []
        
        last_regions = last_data.get("regions", {})
        
        for region_name, region in current.regions.items():
            last_region = last_regions.get(region_name)
            if not last_region:
                continue
            
            # Check coverage drop in this region
            last_coverage = last_region.get("coverage", 0.0)
            coverage_drop = last_coverage - region.coverage
            
            if coverage_drop > self.thresholds["region_coverage_drop"]:
                alerts.append(RegressionAlert(
                    metric="coverage",
                    old_value=last_coverage,
                    new_value=region.coverage,
                    severity="moderate",
                    message=f"Coverage dropped {coverage_drop:.1f}% in {region_name} "
                            f"({last_coverage:.1f}% → {region.coverage:.1f}%)",
                    region=region_name
                ))
            elif coverage_drop > self.thresholds["minor_coverage_drop"]:
                alerts.append(RegressionAlert(
                    metric="coverage",
                    old_value=last_coverage,
                    new_value=region.coverage,
                    severity="minor",
                    message=f"Slight coverage drop in {region_name}: "
                            f"{coverage_drop:.1f}%",
                    region=region_name
                ))
            
            # Check status degradation
            last_status = last_region.get("status", "offline")
            if self._is_status_worse(region.status.value, last_status):
                alerts.append(RegressionAlert(
                    metric="status",
                    old_value=0,  # Placeholder for enum
                    new_value=1,
                    severity="moderate",
                    message=f"Status degraded in {region_name}: "
                            f"{last_status} → {region.status.value}",
                    region=region_name
                ))
        
        return alerts
    
    def _check_test_regressions(
        self, current: NeuralStatus, last_data: dict
    ) -> List[RegressionAlert]:
        """Check for new test failures."""
        alerts = []
        
        last_regions = last_data.get("regions", {})
        
        for region_name, region in current.regions.items():
            last_region = last_regions.get(region_name)
            if not last_region:
                continue
            
            last_failing = last_region.get("failing_tests", 0)
            current_failing = region.failing_tests
            
            if current_failing > last_failing:
                new_failures = current_failing - last_failing
                alerts.append(RegressionAlert(
                    metric="failing_tests",
                    old_value=float(last_failing),
                    new_value=float(current_failing),
                    severity="critical",
                    message=f"NEW TEST FAILURES in {region_name}: "
                            f"{new_failures} test(s) now failing "
                            f"({last_failing} → {current_failing})",
                    region=region_name
                ))
        
        return alerts
    
    def _is_status_worse(self, current_status: str, last_status: str) -> bool:
        """Determine if current status is worse than last status."""
        status_hierarchy = {
            "healthy": 3,
            "warning": 2,
            "error": 1,
            "offline": 0
        }
        
        current_level = status_hierarchy.get(current_status, 0)
        last_level = status_hierarchy.get(last_status, 0)
        
        return current_level < last_level
    
    def save_snapshot(self, status: NeuralStatus):
        """
        Save current status to history for future regression detection.
        
        Args:
            status: Neural status to snapshot
        """
        history = self._load_history()
        
        # Add current status
        status_dict = status.model_dump(mode='json')
        history.append(status_dict)
        
        # Keep only max_history items (rolling window)
        if len(history) > self.max_history:
            history = history[-self.max_history:]
        
        # Save to file
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠ Failed to save history snapshot: {e}")
    
    def _load_history(self) -> List[dict]:
        """Load historical snapshots from file."""
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
                # Ensure it's a list
                if not isinstance(history, list):
                    return []
                return history
        except Exception as e:
            print(f"⚠ Failed to load history: {e}")
            return []
    
    def convert_alerts_to_diagnostics(
        self, alerts: List[RegressionAlert]
    ) -> List[Diagnostic]:
        """
        Convert regression alerts to diagnostic messages.
        
        Args:
            alerts: List of regression alerts
            
        Returns:
            List of Diagnostic objects for display
        """
        diagnostics = []
        
        for alert in alerts:
            # Map severity to diagnostic level
            level = DiagnosticLevel.ALERT if alert.severity == "critical" else DiagnosticLevel.CAUTION
            
            # Create diagnostic
            diagnostic = Diagnostic(
                level=level,
                region=alert.region or "overall",
                message=f"REGRESSION: {alert.message}",
                details=f"{alert.metric}: {alert.old_value:.2f} → {alert.new_value:.2f}",
                timestamp=datetime.now(timezone.utc)
            )
            diagnostics.append(diagnostic)
        
        return diagnostics
    
    def get_trend(self, metric: str, region: Optional[str] = None) -> str:
        """
        Analyze trend for a specific metric.
        
        Args:
            metric: Metric name (e.g., "coverage", "illumination")
            region: Optional region name for region-specific metrics
            
        Returns:
            "improving", "stable", or "degrading"
        """
        history = self._load_history()
        if len(history) < 3:
            return "stable"  # Not enough data
        
        # Extract values for this metric
        values = []
        for snapshot in history:
            if region:
                region_data = snapshot.get("regions", {}).get(region)
                if region_data and metric in region_data:
                    values.append(float(region_data[metric]))
            else:
                if metric in snapshot:
                    values.append(float(snapshot[metric]))
        
        if len(values) < 3:
            return "stable"
        
        # Simple trend calculation: compare first value vs last value
        # (More reliable than averaging thirds for small datasets)
        first_value = values[0]
        last_value = values[-1]
        
        delta = last_value - first_value
        
        # Thresholds (relative to first value for percentage-based metrics)
        threshold = 0.05
        if metric in ["illumination"]:
            # For 0-1 scale, 0.05 = 5%
            pass
        elif metric in ["coverage"]:
            # For 0-100 scale, 5 points = 5%
            threshold = 5.0
        
        if delta > threshold:
            return "improving"
        elif delta < -threshold:
            return "degrading"
        else:
            return "stable"
    
    def clear_history(self):
        """Clear all historical data (useful for testing)."""
        if self.history_file.exists():
            self.history_file.unlink()
