"""
Metrics System - High-Performance Async Metrics Collection.

This package provides a non-blocking metrics collection system optimized for
high-concurrency environments.

Public API:
    MetricsManager: Main class for metrics collection
    MetricRecord: Single metric record model
    MetricsBatch: Batch of metrics for persistence
    MetricsStats: Statistics about the metrics system

Usage:
    from backend.cto.metrics import MetricsManager
    
    manager = MetricsManager(storage_path="./metrics")
    await manager.start()
    
    await manager.record_operation(
        operation_type="api_request",
        operation_name="GET /api/status",
        duration_ms=42.5
    )
    
    await manager.stop()
"""

from .manager import MetricsManager
from .models import MetricRecord, MetricsBatch, MetricsStats

__all__ = [
    "MetricsManager",
    "MetricRecord",
    "MetricsBatch",
    "MetricsStats",
]
