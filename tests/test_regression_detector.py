"""
Tests for Regression Detector.

This module tests the RegressionDetector's ability to identify
quality degradation by comparing current status with historical baselines.
"""

import json
import pytest
from datetime import datetime, timezone
from pathlib import Path

from neural_cli.regression_detector import RegressionDetector, RegressionAlert
from neural_cli.models import NeuralStatus, BrainRegion, RegionStatus


@pytest.fixture
def temp_project_root(tmp_path):
    """Create a temporary project root for testing."""
    return str(tmp_path)


@pytest.fixture
def detector(temp_project_root):
    """Create a RegressionDetector instance."""
    return RegressionDetector(temp_project_root)


@pytest.fixture
def baseline_status():
    """Create a baseline neural status with good metrics."""
    return NeuralStatus(
        illumination=0.85,
        regions={
            "ui-components": BrainRegion(
                status=RegionStatus.HEALTHY,
                coverage=85.0,
                test_count=42,
                passing_tests=42,
                failing_tests=0
            ),
            "core-logic": BrainRegion(
                status=RegionStatus.HEALTHY,
                coverage=80.0,
                test_count=28,
                passing_tests=28,
                failing_tests=0
            )
        }
    )


@pytest.fixture
def regressed_status():
    """Create a regressed status with degraded metrics."""
    return NeuralStatus(
        illumination=0.70,  # Dropped from 0.85
        regions={
            "ui-components": BrainRegion(
                status=RegionStatus.WARNING,  # Degraded from HEALTHY
                coverage=70.0,  # Dropped from 85.0
                test_count=42,
                passing_tests=40,
                failing_tests=2  # New failures!
            ),
            "core-logic": BrainRegion(
                status=RegionStatus.HEALTHY,
                coverage=75.0,  # Slight drop from 80.0
                test_count=28,
                passing_tests=28,
                failing_tests=0
            )
        }
    )


def test_detector_initialization(detector, temp_project_root):
    """Test that detector initializes correctly."""
    assert detector.project_root == Path(temp_project_root)
    assert detector.history_file == Path(temp_project_root) / "neural_history.json"
    assert detector.max_history == 10
    assert "coverage_drop" in detector.thresholds


def test_save_snapshot(detector, baseline_status):
    """Test saving a status snapshot to history."""
    detector.save_snapshot(baseline_status)
    
    # Verify file was created
    assert detector.history_file.exists()
    
    # Load and verify content
    history = detector._load_history()
    assert len(history) == 1
    assert history[0]["illumination"] == 0.85


def test_save_multiple_snapshots(detector, baseline_status):
    """Test saving multiple snapshots and max_history limit."""
    # Save 15 snapshots (max is 10)
    for i in range(15):
        status = NeuralStatus(illumination=0.5 + i * 0.01)
        detector.save_snapshot(status)
    
    # Should only keep last 10
    history = detector._load_history()
    assert len(history) == 10
    
    # First snapshot should be from iteration 5 (0-indexed)
    assert history[0]["illumination"] == pytest.approx(0.55, rel=0.01)


def test_no_regression_on_first_snapshot(detector, baseline_status):
    """Test that no regressions are detected without baseline."""
    alerts = detector.detect_regressions(baseline_status)
    assert len(alerts) == 0


def test_detect_illumination_regression(detector, baseline_status, regressed_status):
    """Test detection of global illumination drop."""
    # Save baseline
    detector.save_snapshot(baseline_status)
    
    # Check regressed status
    alerts = detector.detect_regressions(regressed_status)
    
    # Should detect illumination drop (0.85 → 0.70 = 15% drop)
    illumination_alerts = [a for a in alerts if a.metric == "illumination"]
    assert len(illumination_alerts) > 0
    
    alert = illumination_alerts[0]
    assert alert.old_value == 0.85
    assert alert.new_value == 0.70
    assert alert.severity in ["moderate", "critical"]
    assert "health dropped" in alert.message.lower()


def test_detect_coverage_regression(detector, baseline_status, regressed_status):
    """Test detection of per-region coverage drop."""
    detector.save_snapshot(baseline_status)
    
    alerts = detector.detect_regressions(regressed_status)
    
    # Should detect coverage drop in ui-components (85 → 70 = 15% drop)
    coverage_alerts = [
        a for a in alerts 
        if a.metric == "coverage" and a.region == "ui-components"
    ]
    assert len(coverage_alerts) > 0
    
    alert = coverage_alerts[0]
    assert alert.old_value == 85.0
    assert alert.new_value == 70.0
    assert alert.severity == "moderate"


def test_detect_test_failure_regression(detector, baseline_status, regressed_status):
    """Test detection of new test failures."""
    detector.save_snapshot(baseline_status)
    
    alerts = detector.detect_regressions(regressed_status)
    
    # Should detect new failures in ui-components (0 → 2 failures)
    test_alerts = [
        a for a in alerts 
        if a.metric == "failing_tests" and a.region == "ui-components"
    ]
    assert len(test_alerts) > 0
    
    alert = test_alerts[0]
    assert alert.old_value == 0.0
    assert alert.new_value == 2.0
    assert alert.severity == "critical"
    assert "NEW TEST FAILURES" in alert.message


def test_detect_status_degradation(detector, baseline_status, regressed_status):
    """Test detection of status degradation (HEALTHY → WARNING)."""
    detector.save_snapshot(baseline_status)
    
    alerts = detector.detect_regressions(regressed_status)
    
    # Should detect status change in ui-components
    status_alerts = [
        a for a in alerts 
        if a.metric == "status" and a.region == "ui-components"
    ]
    assert len(status_alerts) > 0
    
    alert = status_alerts[0]
    assert "degraded" in alert.message.lower()


def test_minor_regression_detection(detector):
    """Test detection of minor regressions (below critical threshold)."""
    # Baseline
    baseline = NeuralStatus(
        illumination=0.85,
        regions={
            "ui-components": BrainRegion(
                status=RegionStatus.HEALTHY,
                coverage=85.0,
                test_count=42,
                passing_tests=42,
                failing_tests=0
            )
        }
    )
    detector.save_snapshot(baseline)
    
    # Slightly regressed (only 3% coverage drop - minor)
    slightly_regressed = NeuralStatus(
        illumination=0.83,
        regions={
            "ui-components": BrainRegion(
                status=RegionStatus.HEALTHY,
                coverage=82.0,  # 3% drop
                test_count=42,
                passing_tests=42,
                failing_tests=0
            )
        }
    )
    
    alerts = detector.detect_regressions(slightly_regressed)
    
    # Should detect minor alert
    coverage_alerts = [a for a in alerts if a.metric == "coverage"]
    if len(coverage_alerts) > 0:
        assert coverage_alerts[0].severity == "minor"


def test_convert_alerts_to_diagnostics(detector):
    """Test conversion of alerts to diagnostic messages."""
    alerts = [
        RegressionAlert(
            metric="coverage",
            old_value=85.0,
            new_value=70.0,
            severity="moderate",
            message="Coverage dropped 15% in ui-components",
            region="ui-components"
        ),
        RegressionAlert(
            metric="failing_tests",
            old_value=0.0,
            new_value=3.0,
            severity="critical",
            message="NEW TEST FAILURES",
            region="core-logic"
        )
    ]
    
    diagnostics = detector.convert_alerts_to_diagnostics(alerts)
    
    assert len(diagnostics) == 2
    assert diagnostics[0].level.value == "CAUTION"  # moderate → CAUTION
    assert diagnostics[1].level.value == "ALERT"    # critical → ALERT
    assert "REGRESSION" in diagnostics[0].message


def test_get_trend_improving(detector):
    """Test trend detection for improving metrics."""
    # Create history with improving coverage
    for i in range(5):
        status = NeuralStatus(
            illumination=0.5 + i * 0.1,  # 0.5, 0.6, 0.7, 0.8, 0.9
            regions={
                "ui-components": BrainRegion(
                    status=RegionStatus.HEALTHY,
                    coverage=50.0 + i * 10.0  # 50, 60, 70, 80, 90
                )
            }
        )
        detector.save_snapshot(status)
    
    # Check trend
    trend = detector.get_trend("illumination")
    assert trend == "improving"


def test_get_trend_degrading(detector):
    """Test trend detection for degrading metrics."""
    # Create history with degrading coverage
    for i in range(5):
        status = NeuralStatus(
            illumination=0.9 - i * 0.1,  # 0.9, 0.8, 0.7, 0.6, 0.5
            regions={
                "ui-components": BrainRegion(
                    status=RegionStatus.HEALTHY,
                    coverage=90.0 - i * 10.0  # 90, 80, 70, 60, 50
                )
            }
        )
        detector.save_snapshot(status)
    
    # Check trend
    trend = detector.get_trend("illumination")
    assert trend == "degrading"


def test_get_trend_stable(detector):
    """Test trend detection for stable metrics."""
    # Create history with stable coverage
    for i in range(5):
        status = NeuralStatus(
            illumination=0.8,  # Constant
            regions={
                "ui-components": BrainRegion(
                    status=RegionStatus.HEALTHY,
                    coverage=80.0  # Constant
                )
            }
        )
        detector.save_snapshot(status)
    
    # Check trend
    trend = detector.get_trend("illumination")
    assert trend == "stable"


def test_get_trend_insufficient_data(detector):
    """Test trend with insufficient historical data."""
    # Only one snapshot
    status = NeuralStatus(illumination=0.8)
    detector.save_snapshot(status)
    
    trend = detector.get_trend("illumination")
    assert trend == "stable"  # Default when insufficient data


def test_clear_history(detector, baseline_status):
    """Test clearing historical data."""
    # Save some data
    detector.save_snapshot(baseline_status)
    assert detector.history_file.exists()
    
    # Clear
    detector.clear_history()
    assert not detector.history_file.exists()


def test_configurable_thresholds(temp_project_root):
    """Test that thresholds are configurable."""
    detector = RegressionDetector(temp_project_root)
    
    # Modify thresholds to be more lenient
    detector.thresholds["region_coverage_drop"] = 15.0  # Moderate alert only if >15%
    detector.thresholds["minor_coverage_drop"] = 5.0    # Minor alert only if >5%
    
    # Test with 8% drop (should NOT trigger moderate, but MAY trigger minor)
    baseline = NeuralStatus(
        regions={
            "ui-components": BrainRegion(coverage=85.0)
        }
    )
    detector.save_snapshot(baseline)
    
    regressed = NeuralStatus(
        regions={
            "ui-components": BrainRegion(coverage=77.0)  # 8% drop
        }
    )
    
    alerts = detector.detect_regressions(regressed)
    
    # Should trigger minor alert (8% > 5% minor threshold)
    # But NOT moderate alert (8% < 15% moderate threshold)
    coverage_alerts = [a for a in alerts if a.metric == "coverage"]
    assert len(coverage_alerts) > 0
    assert coverage_alerts[0].severity == "minor"


def test_no_alerts_for_improvement(detector):
    """Test that improvements don't trigger alerts."""
    # Baseline
    baseline = NeuralStatus(
        illumination=0.70,
        regions={
            "ui-components": BrainRegion(
                status=RegionStatus.WARNING,
                coverage=70.0,
                test_count=42,
                passing_tests=40,
                failing_tests=2
            )
        }
    )
    detector.save_snapshot(baseline)
    
    # Improved status
    improved = NeuralStatus(
        illumination=0.85,  # Improved!
        regions={
            "ui-components": BrainRegion(
                status=RegionStatus.HEALTHY,  # Improved!
                coverage=85.0,  # Improved!
                test_count=42,
                passing_tests=42,
                failing_tests=0  # Fixed!
            )
        }
    )
    
    alerts = detector.detect_regressions(improved)
    
    # Should have NO alerts (improvement is good!)
    assert len(alerts) == 0
