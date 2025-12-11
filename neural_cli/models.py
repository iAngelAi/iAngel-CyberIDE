"""
Models for CyberIDE Neural Core.

This module defines Pydantic models for data structures used throughout
the neural backend system. These models ensure type safety and data validation.

Validation Strategy:
    Numeric fields with bounds (coverage, illumination, percentages) use
    "clamping with warning" - values outside valid range are corrected to
    the nearest bound and a warning is logged to alert developers of
    potential upstream calculation errors.

    See: docs/adr/ADR-001-logging-strategy.md
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from .logging_config import get_logger

logger = get_logger(__name__)


class RegionStatus(str, Enum):
    """Status levels for brain regions - maps to visual illumination states."""
    HEALTHY = "healthy"      # Green illumination
    WARNING = "warning"      # Yellow illumination
    ERROR = "error"          # Red illumination (pulsing)
    OFFLINE = "offline"      # Dim/no illumination


class DiagnosticLevel(str, Enum):
    """Diagnostic severity levels for error reporting."""
    CAUTION = "CAUTION"      # Medium risk or regression
    ALERT = "ALERT"          # Immediate attention required


class BrainRegion(BaseModel):
    """
    Represents a specific region of the neural brain visualization.

    Each region corresponds to a module or component of the project
    (frontend, backend, tests, docs, integrations).
    """
    status: RegionStatus = Field(default=RegionStatus.OFFLINE)
    coverage: float = Field(default=0.0)  # Bounds enforced by validator with logging
    test_count: int = Field(default=0, ge=0)
    passing_tests: int = Field(default=0, ge=0)
    failing_tests: int = Field(default=0, ge=0)
    file_count: int = Field(default=0, ge=0)
    last_modified: Optional[datetime] = None

    @field_validator('coverage')
    @classmethod
    def validate_coverage(cls, v: float) -> float:
        """
        Ensure coverage is between 0 and 100.

        Values outside this range are clamped and a warning is logged
        to alert developers of potential upstream calculation errors.
        """
        if v < 0.0:
            logger.warning(
                "BrainRegion.coverage=%.2f is below 0.0, clamping to 0.0. "
                "Check upstream calculation in MetricCalculator.",
                v
            )
            return 0.0
        if v > 100.0:
            logger.warning(
                "BrainRegion.coverage=%.2f exceeds 100.0, clamping to 100.0. "
                "Check upstream calculation in MetricCalculator.",
                v
            )
            return 100.0
        return v


class Diagnostic(BaseModel):
    """
    Diagnostic message for issues detected in the project.

    These appear as warnings/alerts in the UI and terminal.
    """
    level: DiagnosticLevel
    region: str
    message: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    file_path: Optional[str] = None
    line_number: Optional[int] = None


class NeuralStatus(BaseModel):
    """
    Complete state of the Neural Brain.

    This is the main data structure sent to the frontend via WebSocket
    and persisted in neural_status.json.
    """
    illumination: float = Field(default=0.0)  # Bounds enforced by validator with logging
    regions: Dict[str, BrainRegion] = Field(default_factory=dict)
    diagnostics: List[Diagnostic] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    project_name: str = "CyberIDE"
    version: str = "1.0.0"

    # Project metadata
    has_license: bool = False
    has_readme: bool = False
    documentation_complete: bool = False
    api_configured: bool = False
    mcp_providers_count: int = 0

    @field_validator('illumination')
    @classmethod
    def validate_illumination(cls, v: float) -> float:
        """
        Ensure illumination is between 0.0 and 1.0.

        Values outside this range are clamped and a warning is logged
        to alert developers of potential upstream calculation errors.
        """
        if v < 0.0:
            logger.warning(
                "NeuralStatus.illumination=%.3f is below 0.0, clamping to 0.0. "
                "Check upstream calculation in MetricCalculator.",
                v
            )
            return 0.0
        if v > 1.0:
            logger.warning(
                "NeuralStatus.illumination=%.3f exceeds 1.0, clamping to 1.0. "
                "Check upstream calculation in MetricCalculator.",
                v
            )
            return 1.0
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FileChangeEvent(BaseModel):
    """Event emitted when a file changes in the watched directories."""
    event_type: str  # created, modified, deleted, moved
    file_path: str
    is_test_file: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PytestRunResult(BaseModel):
    """Result of running pytest on the project."""
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    coverage_percentage: float = 0.0
    duration: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    failed_tests: List[Dict[str, str]] = Field(default_factory=list)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WebSocketMessage(BaseModel):
    """
    Generic WebSocket message format.

    All messages sent through WebSocket follow this structure.
    """
    type: str  # neural_status, file_change, test_result, diagnostic
    data: dict
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProjectMetrics(BaseModel):
    """
    Calculated metrics for the entire project.

    Used to determine overall illumination percentage.
    """
    total_files: int = 0
    total_lines: int = 0
    test_coverage: float = 0.0
    documentation_score: float = 0.0
    module_completion: float = 0.0
    integration_score: float = 0.0
    overall_health: float = 0.0

    @field_validator('test_coverage', 'documentation_score', 'module_completion',
                     'integration_score', 'overall_health')
    @classmethod
    def validate_percentage(cls, v: float, info) -> float:
        """
        Ensure all percentage fields are between 0 and 100.

        Values outside this range are clamped and a warning is logged
        to alert developers of potential upstream calculation errors.
        """
        field_name = info.field_name if info else "unknown"

        if v < 0.0:
            logger.warning(
                "ProjectMetrics.%s=%.2f is below 0.0, clamping to 0.0. "
                "Check upstream calculation.",
                field_name, v
            )
            return 0.0
        if v > 100.0:
            logger.warning(
                "ProjectMetrics.%s=%.2f exceeds 100.0, clamping to 100.0. "
                "Check upstream calculation.",
                field_name, v
            )
            return 100.0
        return v
