"""
CyberIDE Neural CLI - Neural Core Backend

The Neural Core is the brain of CyberIDE, providing real-time project
health monitoring, test execution, and WebSocket communication for the
3D brain visualization.

Components:
    - FastAPI WebSocket server for real-time communication
    - File watcher for detecting code changes
    - Test analyzer for running pytest and collecting coverage
    - Metric calculator for brain illumination percentage

Usage:
    python -m neural_cli.main

Or:
    python start_neural_core.py
"""

__version__ = "1.0.0"
__author__ = "CyberIDE Neural Architect"

from .main import app, neural_core, main
from .models import (
    NeuralStatus,
    BrainRegion,
    RegionStatus,
    Diagnostic,
    DiagnosticLevel,
    FileChangeEvent,
    PytestRunResult,
    WebSocketMessage,
    ProjectMetrics
)
from .file_watcher import FileWatcher, NeuralFileHandler
from .test_analyzer import PytestAnalyzer
from .metric_calculator import MetricCalculator

__all__ = [
    # Main app
    "app",
    "neural_core",
    "main",
    # Models
    "NeuralStatus",
    "BrainRegion",
    "RegionStatus",
    "Diagnostic",
    "DiagnosticLevel",
    "FileChangeEvent",
    "PytestRunResult",
    "WebSocketMessage",
    "ProjectMetrics",
    # Components
    "FileWatcher",
    "NeuralFileHandler",
    "PytestAnalyzer",
    "MetricCalculator",
]
