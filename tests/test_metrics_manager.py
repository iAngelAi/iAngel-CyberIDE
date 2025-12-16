"""
Unit tests for MetricsManager with async Producer-Consumer pattern.

These tests validate:
1. Non-blocking metric recording (O(1) operation)
2. Batch persistence to disk
3. Graceful shutdown with final flush
4. Data validation with Pydantic
5. Error handling and resilience

Test Coverage:
- Basic operations (start, stop, record)
- Concurrent metric recording
- Batch writes and file persistence
- Statistics tracking
- Edge cases (empty queue, queue full, shutdown)
- Error scenarios (invalid inputs, disk errors)
"""

import asyncio
import json
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from backend.cto.metrics import MetricsManager, MetricRecord, MetricsStats


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def metrics_storage(tmp_path):
    """Create a temporary directory for metrics storage."""
    storage = tmp_path / "metrics"
    storage.mkdir()
    return storage


@pytest_asyncio.fixture
async def metrics_manager(metrics_storage):
    """Create and start a MetricsManager instance."""
    manager = MetricsManager(
        storage_path=metrics_storage,
        flush_interval_seconds=0.5,  # Fast flush for testing
        max_batch_size=10,
        max_queue_size=100
    )
    await manager.start()
    yield manager
    await manager.stop()


# ============================================================================
# Test: Initialization and Configuration
# ============================================================================

def test_init_creates_storage_directory(tmp_path):
    """Test that initialization creates the storage directory."""
    storage = tmp_path / "test_metrics"
    assert not storage.exists()
    
    manager = MetricsManager(storage_path=storage)
    
    assert storage.exists()
    assert storage.is_dir()


def test_init_with_invalid_parameters():
    """Test that invalid parameters raise ValueError."""
    with pytest.raises(ValueError, match="flush_interval_seconds must be positive"):
        MetricsManager(storage_path="/tmp", flush_interval_seconds=0)
    
    with pytest.raises(ValueError, match="max_batch_size must be positive"):
        MetricsManager(storage_path="/tmp", max_batch_size=0)
    
    with pytest.raises(ValueError, match="max_queue_size must be positive"):
        MetricsManager(storage_path="/tmp", max_queue_size=-1)


# ============================================================================
# Test: Lifecycle Management (Start/Stop)
# ============================================================================

@pytest.mark.asyncio
async def test_start_sets_running_state(metrics_storage):
    """Test that start() sets the running state correctly."""
    manager = MetricsManager(storage_path=metrics_storage)
    
    assert not manager._is_running
    
    await manager.start()
    
    assert manager._is_running
    assert manager._worker_task is not None
    assert not manager._worker_task.done()
    
    await manager.stop()


@pytest.mark.asyncio
async def test_start_twice_raises_error(metrics_storage):
    """Test that starting an already running manager raises RuntimeError."""
    manager = MetricsManager(storage_path=metrics_storage)
    await manager.start()
    
    with pytest.raises(RuntimeError, match="already running"):
        await manager.start()
    
    await manager.stop()


@pytest.mark.asyncio
async def test_stop_gracefully_flushes_metrics(metrics_storage):
    """Test that stop() flushes remaining metrics before shutdown."""
    manager = MetricsManager(
        storage_path=metrics_storage,
        flush_interval_seconds=10.0  # Long interval
    )
    await manager.start()
    
    # Record some metrics
    await manager.record_operation(
        operation_type="test",
        operation_name="test_op",
        duration_ms=10.0
    )
    
    # Stop immediately (before flush interval)
    await manager.stop()
    
    # Verify metrics were flushed
    stats = await manager.get_stats()
    assert stats.total_recorded == 1
    assert stats.total_persisted == 1
    assert stats.queue_size == 0


@pytest.mark.asyncio
async def test_stop_when_not_running_is_safe(metrics_storage):
    """Test that calling stop() when not running doesn't raise errors."""
    manager = MetricsManager(storage_path=metrics_storage)
    
    # Should not raise any errors
    await manager.stop()


# ============================================================================
# Test: Metric Recording (Core Functionality)
# ============================================================================

@pytest.mark.asyncio
async def test_record_operation_basic(metrics_manager):
    """Test basic metric recording."""
    await metrics_manager.record_operation(
        operation_type="api_request",
        operation_name="GET /api/status",
        duration_ms=42.5
    )
    
    stats = await metrics_manager.get_stats()
    assert stats.total_recorded == 1
    assert stats.queue_size == 1


@pytest.mark.asyncio
async def test_record_operation_with_metadata(metrics_manager):
    """Test metric recording with metadata."""
    metadata = {
        "status_code": 200,
        "region": "us-east",
        "cache_hit": True,
        "response_size_bytes": 1024
    }
    
    await metrics_manager.record_operation(
        operation_type="api_request",
        operation_name="GET /api/users",
        duration_ms=35.7,
        success=True,
        metadata=metadata
    )
    
    stats = await metrics_manager.get_stats()
    assert stats.total_recorded == 1


@pytest.mark.asyncio
async def test_record_operation_with_error(metrics_manager):
    """Test metric recording for failed operations."""
    await metrics_manager.record_operation(
        operation_type="database_query",
        operation_name="SELECT users",
        duration_ms=150.0,
        success=False,
        error_message="Connection timeout"
    )
    
    stats = await metrics_manager.get_stats()
    assert stats.total_recorded == 1


@pytest.mark.asyncio
async def test_record_operation_when_not_running_raises_error(metrics_storage):
    """Test that recording when manager is not running raises RuntimeError."""
    manager = MetricsManager(storage_path=metrics_storage)
    
    with pytest.raises(RuntimeError, match="not running"):
        await manager.record_operation(
            operation_type="test",
            operation_name="test_op",
            duration_ms=10.0
        )


@pytest.mark.asyncio
async def test_record_operation_validates_inputs(metrics_manager):
    """Test that invalid inputs are rejected by Pydantic validation."""
    # Negative duration
    with pytest.raises(Exception):  # Pydantic ValidationError
        await metrics_manager.record_operation(
            operation_type="test",
            operation_name="test_op",
            duration_ms=-10.0
        )
    
    # Empty operation_type
    with pytest.raises(Exception):
        await metrics_manager.record_operation(
            operation_type="",
            operation_name="test_op",
            duration_ms=10.0
        )


@pytest.mark.asyncio
async def test_record_operation_rejects_pii_in_metadata(metrics_manager):
    """Test that PII in metadata is rejected."""
    forbidden_metadata = {
        "email": "user@example.com",  # PII
        "status": 200
    }
    
    with pytest.raises(ValueError, match="forbidden as it may contain PII"):
        await metrics_manager.record_operation(
            operation_type="api_request",
            operation_name="GET /api/users",
            duration_ms=50.0,
            metadata=forbidden_metadata
        )


# ============================================================================
# Test: Batch Persistence
# ============================================================================

@pytest.mark.asyncio
async def test_metrics_are_persisted_to_disk(metrics_storage):
    """Test that metrics are written to disk as JSON files."""
    manager = MetricsManager(
        storage_path=metrics_storage,
        flush_interval_seconds=0.1,  # Fast flush
        max_batch_size=5
    )
    await manager.start()
    
    # Record multiple metrics
    for i in range(5):
        await manager.record_operation(
            operation_type="test",
            operation_name=f"test_op_{i}",
            duration_ms=float(i * 10)
        )
    
    # Wait for flush
    await asyncio.sleep(0.2)
    
    # Verify files were created
    json_files = list(metrics_storage.glob("metrics_*.json"))
    assert len(json_files) > 0
    
    # Verify file content
    with open(json_files[0], 'r') as f:
        batch_data = json.load(f)
    
    assert "records" in batch_data
    assert "batch_id" in batch_data
    assert "total_records" in batch_data
    assert batch_data["total_records"] == len(batch_data["records"])
    
    await manager.stop()


@pytest.mark.asyncio
async def test_batch_size_limits_records_per_file(metrics_storage):
    """Test that max_batch_size limits records per file."""
    manager = MetricsManager(
        storage_path=metrics_storage,
        flush_interval_seconds=0.1,
        max_batch_size=3  # Small batch size
    )
    await manager.start()
    
    # Record 10 metrics (should create multiple batches)
    for i in range(10):
        await manager.record_operation(
            operation_type="test",
            operation_name=f"test_op_{i}",
            duration_ms=10.0
        )
    
    # Wait for flushes
    await asyncio.sleep(0.5)
    
    # Verify multiple batch files were created
    json_files = list(metrics_storage.glob("metrics_*.json"))
    assert len(json_files) >= 3
    
    # Verify each batch respects max_batch_size
    for json_file in json_files:
        with open(json_file, 'r') as f:
            batch_data = json.load(f)
        assert len(batch_data["records"]) <= 3
    
    await manager.stop()


@pytest.mark.asyncio
async def test_atomic_write_prevents_partial_files(metrics_storage):
    """Test that writes are atomic (no partial files on crash)."""
    manager = MetricsManager(
        storage_path=metrics_storage,
        flush_interval_seconds=0.1
    )
    await manager.start()
    
    await manager.record_operation(
        operation_type="test",
        operation_name="test_op",
        duration_ms=10.0
    )
    
    # Wait for flush
    await asyncio.sleep(0.2)
    
    # Verify no .tmp files remain
    tmp_files = list(metrics_storage.glob("*.tmp"))
    assert len(tmp_files) == 0
    
    # Verify JSON file is valid
    json_files = list(metrics_storage.glob("metrics_*.json"))
    assert len(json_files) > 0
    
    with open(json_files[0], 'r') as f:
        batch_data = json.load(f)  # Should not raise JSONDecodeError
    
    assert "records" in batch_data
    
    await manager.stop()


# ============================================================================
# Test: Statistics and Observability
# ============================================================================

@pytest.mark.asyncio
async def test_get_stats_returns_accurate_counts(metrics_manager):
    """Test that get_stats() returns accurate statistics."""
    # Record some metrics
    for i in range(5):
        await metrics_manager.record_operation(
            operation_type="test",
            operation_name=f"test_op_{i}",
            duration_ms=10.0
        )
    
    stats = await metrics_manager.get_stats()
    
    assert stats.total_recorded == 5
    assert stats.queue_size <= 5
    assert stats.is_running is True


@pytest.mark.asyncio
async def test_stats_track_persistence(metrics_storage):
    """Test that statistics track persisted metrics."""
    manager = MetricsManager(
        storage_path=metrics_storage,
        flush_interval_seconds=0.1
    )
    await manager.start()
    
    # Record metrics
    for i in range(3):
        await manager.record_operation(
            operation_type="test",
            operation_name=f"test_op_{i}",
            duration_ms=10.0
        )
    
    # Wait for flush
    await asyncio.sleep(0.2)
    
    stats = await manager.get_stats()
    
    assert stats.total_recorded == 3
    assert stats.total_persisted == 3
    assert stats.batches_written >= 1
    assert stats.avg_batch_size > 0
    assert stats.last_flush_timestamp is not None
    
    await manager.stop()


# ============================================================================
# Test: Concurrency and Performance
# ============================================================================

@pytest.mark.asyncio
async def test_concurrent_recording(metrics_manager):
    """Test that concurrent metric recording works correctly."""
    async def record_metrics(count: int):
        for i in range(count):
            await metrics_manager.record_operation(
                operation_type="concurrent_test",
                operation_name=f"test_op_{i}",
                duration_ms=float(i)
            )
    
    # Record metrics concurrently from multiple tasks
    await asyncio.gather(
        record_metrics(10),
        record_metrics(10),
        record_metrics(10)
    )
    
    stats = await metrics_manager.get_stats()
    assert stats.total_recorded == 30


@pytest.mark.asyncio
async def test_record_operation_is_fast(metrics_manager):
    """Test that record_operation() is non-blocking (< 1ms)."""
    start = asyncio.get_event_loop().time()
    
    await metrics_manager.record_operation(
        operation_type="performance_test",
        operation_name="test_op",
        duration_ms=10.0
    )
    
    elapsed_ms = (asyncio.get_event_loop().time() - start) * 1000
    
    # Should be nearly instant (< 1ms for O(1) queue operation)
    assert elapsed_ms < 1.0


# ============================================================================
# Test: Edge Cases
# ============================================================================

@pytest.mark.asyncio
async def test_empty_queue_flush_is_safe(metrics_storage):
    """Test that flushing an empty queue doesn't cause errors."""
    manager = MetricsManager(
        storage_path=metrics_storage,
        flush_interval_seconds=0.1
    )
    await manager.start()
    
    # Wait for flush interval (queue is empty)
    await asyncio.sleep(0.2)
    
    stats = await manager.get_stats()
    assert stats.total_persisted == 0
    assert stats.batches_written == 0
    
    await manager.stop()


@pytest.mark.asyncio
async def test_timezone_handling(metrics_manager):
    """Test that timestamps are correctly normalized to UTC."""
    await metrics_manager.record_operation(
        operation_type="timezone_test",
        operation_name="test_op",
        duration_ms=10.0
    )
    
    # Wait for flush
    await asyncio.sleep(0.6)
    
    # Read the persisted file
    json_files = list(metrics_manager.storage_path.glob("metrics_*.json"))
    assert len(json_files) > 0
    
    with open(json_files[0], 'r') as f:
        batch_data = json.load(f)
    
    # Verify timestamp is in ISO format with UTC timezone
    timestamp_str = batch_data["records"][0]["timestamp"]
    timestamp = datetime.fromisoformat(timestamp_str)
    
    # Should be timezone-aware and in UTC
    assert timestamp.tzinfo is not None
    assert timestamp.tzinfo == timezone.utc


# ============================================================================
# Test: Error Handling
# ============================================================================

@pytest.mark.asyncio
async def test_disk_write_error_doesnt_crash_worker(metrics_storage, monkeypatch):
    """Test that disk write errors don't crash the background worker."""
    manager = MetricsManager(
        storage_path=metrics_storage,
        flush_interval_seconds=0.1
    )
    await manager.start()
    
    # Mock the write to raise an error
    original_write = manager._sync_write_json
    write_call_count = 0
    
    def failing_write(*args, **kwargs):
        nonlocal write_call_count
        write_call_count += 1
        if write_call_count == 1:
            raise IOError("Simulated disk error")
        return original_write(*args, **kwargs)
    
    monkeypatch.setattr(manager, '_sync_write_json', failing_write)
    
    # Record metrics
    await manager.record_operation(
        operation_type="error_test",
        operation_name="test_op_1",
        duration_ms=10.0
    )
    
    # Wait for first flush (will fail)
    await asyncio.sleep(0.2)
    
    # Record another metric (worker should still be running)
    await manager.record_operation(
        operation_type="error_test",
        operation_name="test_op_2",
        duration_ms=20.0
    )
    
    # Wait for second flush (should succeed)
    await asyncio.sleep(0.2)
    
    # Worker should still be running
    stats = await manager.get_stats()
    assert stats.is_running is True
    
    await manager.stop()


@pytest.mark.asyncio
async def test_shutdown_timeout_forces_cancellation(metrics_storage):
    """Test that shutdown timeout forces worker cancellation."""
    manager = MetricsManager(
        storage_path=metrics_storage,
        flush_interval_seconds=10.0  # Long interval
    )
    await manager.start()
    
    # Record a metric
    await manager.record_operation(
        operation_type="timeout_test",
        operation_name="test_op",
        duration_ms=10.0
    )
    
    # Stop with very short timeout
    await manager.stop(timeout=0.1)
    
    # Should complete without hanging
    assert not manager._is_running
    
    # Worker task should be cancelled
    assert manager._worker_task.done()
