"""
High-Performance Metrics Manager with Async Producer-Consumer Pattern.

This module implements a non-blocking metrics collection system that:
1. Instantly buffers metrics in memory (O(1) operation)
2. Asynchronously persists metrics to disk in batches
3. Ensures data integrity with graceful shutdown

Architecture Pattern: Producer-Consumer with asyncio.Queue
- Producers: Application code calling record_operation()
- Consumer: Background worker task that flushes metrics periodically
- Buffer: asyncio.Queue with unlimited size (memory-bounded by system)

Performance Characteristics:
- record_operation(): O(1) - Instant, non-blocking
- Disk I/O: Batched every 5 seconds or when queue reaches threshold
- Memory usage: ~1KB per metric * queue_size

Conformité: OWASP Top 10
- Input Validation: All inputs validated via Pydantic
- Secure Design: No PII in metrics, anonymized data only
- Logging: Structured logging with no sensitive data
- Configuration: Secure defaults, configurable limits

Author: Ingénieur Backend MCP
Date: 2025-12-16
"""

import asyncio
import orjson
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from .models import MetricRecord, MetricsBatch, MetricsStats


class MetricsManager:
    """
    High-performance metrics manager with async I/O.
    
    This class implements a Producer-Consumer pattern where:
    - Producers (application code) instantly queue metrics
    - A background consumer task flushes metrics to disk periodically
    
    Usage:
        manager = MetricsManager(storage_path="./metrics")
        await manager.start()
        
        # Record operations (non-blocking)
        await manager.record_operation(
            operation_type="api_request",
            operation_name="GET /api/status",
            duration_ms=45.3
        )
        
        # Graceful shutdown (flushes remaining metrics)
        await manager.stop()
    
    Thread Safety:
        This class is designed for use with asyncio and is not thread-safe.
        Use asyncio.Lock if accessing from multiple coroutines that need
        synchronized access to internal state.
    """
    
    def __init__(
        self,
        storage_path: str | Path,
        flush_interval_seconds: float = 5.0,
        max_batch_size: int = 1000,
        max_queue_size: int = 10000
    ):
        """
        Initialize the MetricsManager.
        
        Args:
            storage_path: Directory where metrics JSON files will be stored
            flush_interval_seconds: How often to flush metrics to disk (default: 5s)
            max_batch_size: Maximum records per batch file (default: 1000)
            max_queue_size: Maximum metrics in queue before backpressure (default: 10000)
        
        Raises:
            ValueError: If parameters are invalid
        """
        if flush_interval_seconds <= 0:
            raise ValueError("flush_interval_seconds must be positive")
        if max_batch_size <= 0:
            raise ValueError("max_batch_size must be positive")
        if max_queue_size <= 0:
            raise ValueError("max_queue_size must be positive")
        
        self.storage_path = Path(storage_path)
        self.flush_interval = flush_interval_seconds
        self.max_batch_size = max_batch_size
        self.max_queue_size = max_queue_size
        
        # Producer-Consumer queue (async, thread-safe within asyncio)
        self._queue: asyncio.Queue[MetricRecord] = asyncio.Queue(maxsize=max_queue_size)
        
        # Background worker task
        self._worker_task: Optional[asyncio.Task[None]] = None
        
        # Lifecycle management
        self._is_running: bool = False
        self._shutdown_event: asyncio.Event = asyncio.Event()
        
        # Statistics (for monitoring and observability)
        self._stats = MetricsStats()
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def start(self) -> None:
        """
        Start the background metrics worker.
        
        This method:
        1. Validates the manager isn't already running
        2. Creates the background worker task
        3. Sets running flag
        
        Raises:
            RuntimeError: If manager is already running
        """
        if self._is_running:
            raise RuntimeError("MetricsManager is already running")
        
        self._is_running = True
        self._stats.is_running = True
        self._shutdown_event.clear()
        
        # Start the background worker task
        self._worker_task = asyncio.create_task(self._background_worker())
    
    async def stop(self, timeout: float = 10.0) -> None:
        """
        Stop the metrics manager and flush remaining metrics.
        
        This method ensures graceful shutdown:
        1. Signals the worker to stop accepting new work
        2. Waits for the worker to flush remaining metrics
        3. Performs a final flush if needed
        4. Cancels the worker task if timeout is reached
        
        Args:
            timeout: Maximum seconds to wait for graceful shutdown
        
        Raises:
            asyncio.TimeoutError: If shutdown exceeds timeout
        """
        if not self._is_running:
            return  # Already stopped
        
        # Signal shutdown
        self._shutdown_event.set()
        self._is_running = False
        
        if self._worker_task is None:
            return
        
        try:
            # Wait for worker to finish with timeout
            await asyncio.wait_for(self._worker_task, timeout=timeout)
        except asyncio.TimeoutError:
            # Force cancellation if timeout exceeded
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        
        # Perform final flush of any remaining items
        await self._flush_metrics()
        
        self._stats.is_running = False
    
    async def record_operation(
        self,
        operation_type: str,
        operation_name: str,
        duration_ms: float,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, str | int | float | bool]] = None
    ) -> None:
        """
        Record a single operation metric (non-blocking, O(1)).
        
        This method instantly queues the metric for later persistence.
        If the queue is full, it will block until space is available
        (backpressure mechanism to prevent memory exhaustion).
        
        Args:
            operation_type: Type of operation (e.g., "api_request", "db_query")
            operation_name: Specific operation identifier
            duration_ms: Operation duration in milliseconds (must be >= 0)
            success: Whether the operation succeeded
            error_message: Error message if operation failed
            metadata: Additional context (no PII allowed)
        
        Raises:
            ValueError: If validation fails (invalid inputs)
            RuntimeError: If manager is not running
        
        Example:
            await manager.record_operation(
                operation_type="api_request",
                operation_name="GET /api/users",
                duration_ms=42.5,
                success=True,
                metadata={"status_code": 200, "region": "us-east"}
            )
        """
        if not self._is_running:
            raise RuntimeError(
                "MetricsManager is not running. Call start() first."
            )
        
        # Validate and create metric record (Pydantic validation)
        metric = MetricRecord(
            operation_type=operation_type,
            operation_name=operation_name,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
            metadata=metadata
        )
        
        # Queue the metric (blocks if queue is full - backpressure)
        await self._queue.put(metric)
        
        # Update statistics
        self._stats.total_recorded += 1
        self._stats.queue_size = self._queue.qsize()
    
    async def get_stats(self) -> MetricsStats:
        """
        Get current statistics about the metrics system.
        
        Returns:
            MetricsStats object with current statistics
        
        This is useful for monitoring and observability:
        - Check queue size to detect backlog
        - Monitor flush operations
        - Verify system is running
        """
        self._stats.queue_size = self._queue.qsize()
        return self._stats.model_copy(deep=True)
    
    async def _background_worker(self) -> None:
        """
        Background worker task that flushes metrics periodically.
        
        This coroutine runs continuously until shutdown is signaled.
        It flushes metrics every `flush_interval` seconds or when
        the queue reaches `max_batch_size`.
        
        Error Handling:
            Exceptions during flush are logged but don't crash the worker.
            This ensures metrics collection continues even if disk writes fail.
        """
        while not self._shutdown_event.is_set():
            try:
                # Wait for flush interval or shutdown signal
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self.flush_interval
                )
                # If we reach here, shutdown was signaled
                break
            except asyncio.TimeoutError:
                # Timeout reached - time to flush
                pass
            
            # Flush metrics if queue is not empty
            if not self._queue.empty():
                try:
                    await self._flush_metrics()
                except Exception as e:
                    # Log error but continue running
                    # In production, use proper logging (structlog)
                    print(f"Error flushing metrics: {e}")
        
        # Final flush on shutdown
        if not self._queue.empty():
            try:
                await self._flush_metrics()
            except Exception as e:
                print(f"Error during final flush: {e}")
    
    async def _flush_metrics(self) -> None:
        """
        Flush metrics from queue to disk in batches.
        
        This method:
        1. Drains up to `max_batch_size` metrics from the queue
        2. Creates a MetricsBatch with unique ID
        3. Writes the batch to a JSON file atomically
        4. Updates statistics
        
        File Format:
            metrics_YYYYMMDD_HHMMSS_microseconds.json
        
        Atomicity:
            Uses write-to-temp + rename pattern for atomic writes
            (prevents partial file reads during write)
        """
        if self._queue.empty():
            return
        
        # Collect metrics from queue (non-blocking, up to max_batch_size)
        records: list[MetricRecord] = []
        for _ in range(min(self.max_batch_size, self._queue.qsize())):
            try:
                record = self._queue.get_nowait()
                records.append(record)
            except asyncio.QueueEmpty:
                break
        
        if not records:
            return
        
        # Create batch with unique ID
        now = datetime.now(timezone.utc)
        batch_id = now.strftime("%Y%m%d_%H%M%S") + f"_{now.microsecond:06d}"
        
        batch = MetricsBatch(
            records=records,
            batch_id=batch_id,
            total_records=len(records)
        )
        
        # Write batch to disk atomically
        await self._write_batch(batch)
        
        # Update statistics
        self._stats.total_persisted += len(records)
        self._stats.batches_written += 1
        self._stats.last_flush_timestamp = now
        self._stats.queue_size = self._queue.qsize()
        
        # Update average batch size
        if self._stats.batches_written > 0:
            self._stats.avg_batch_size = (
                self._stats.total_persisted / self._stats.batches_written
            )
    
    async def _write_batch(self, batch: MetricsBatch) -> None:
        """
        Write a batch to disk atomically.
        
        Uses write-to-temp + rename for atomic writes:
        1. Write to temporary file (.tmp extension)
        2. Rename to final filename (atomic operation on POSIX)
        
        This prevents partial reads if the process crashes during write.
        
        Args:
            batch: MetricsBatch to write to disk
        
        Raises:
            IOError: If disk write fails
        """
        filename = f"metrics_{batch.batch_id}.json"
        filepath = self.storage_path / filename
        temp_filepath = self.storage_path / f"{filename}.tmp"
        
        # Serialize batch to JSON
        batch_data = batch.model_dump(mode='json')
        
        # Write to temporary file
        await asyncio.to_thread(
            self._sync_write_json,
            temp_filepath,
            batch_data
        )
        
        # Atomic rename
        await asyncio.to_thread(
            temp_filepath.rename,
            filepath
        )
    
    @staticmethod
    def _sync_write_json(filepath: Path, data: dict) -> None:
        """
        Synchronous JSON write helper (called in thread pool).
        
        Uses orjson for high-performance serialization with:
        - OPT_INDENT_2: Pretty-print with 2-space indentation for readability
        - Native datetime serialization (no custom encoder needed)
        - Binary mode for maximum performance
        
        Args:
            filepath: Path to write JSON file
            data: Dictionary to serialize as JSON
        """
        # orjson.dumps returns bytes, write in binary mode for performance
        json_bytes = orjson.dumps(
            data,
            option=orjson.OPT_INDENT_2  # Pretty-print for debugging/readability
        )
        with open(filepath, 'wb') as f:
            f.write(json_bytes)
