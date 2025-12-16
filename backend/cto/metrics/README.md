# Metrics System - High-Performance Async Metrics Collection

## Overview

The Metrics System provides a **non-blocking, high-performance** metrics collection solution optimized for massively concurrent environments. It implements an **async Producer-Consumer pattern** with `asyncio.Queue` for instant metric buffering and batched disk writes.

## Architecture

### Producer-Consumer Pattern

```
┌─────────────────┐
│  Application    │  ← Producers (O(1) non-blocking)
│  Threads/Tasks  │
└────────┬────────┘
         │ record_operation()
         ↓
┌────────────────────┐
│   asyncio.Queue    │  ← In-memory buffer (thread-safe)
│   (max 10,000)     │
└────────┬───────────┘
         │ Background Worker
         ↓
┌────────────────────┐
│   Batch Writer     │  ← Consumer (periodic flush)
│   (every 5s)       │
└────────┬───────────┘
         │ Atomic writes
         ↓
┌────────────────────┐
│   Disk Storage     │  ← JSON files (metrics_YYYYMMDD_HHMMSS.json)
└────────────────────┘
```

### Key Features

- **Non-blocking Operations**: `record_operation()` is O(1) and returns instantly
- **Batched Writes**: Metrics are written in batches every 5 seconds or when batch size is reached
- **Graceful Shutdown**: Ensures all buffered metrics are flushed before shutdown
- **Atomic Writes**: Uses write-to-temp + rename pattern to prevent partial files
- **Type Safety**: Full static typing with Pydantic V2 validation
- **Security**: PII detection in metadata, no sensitive data logging
- **Observability**: Built-in statistics tracking (queue size, flush count, etc.)

## Installation

The metrics system is included in the `backend.cto.metrics` package:

```python
from backend.cto.metrics import MetricsManager
```

## Quick Start

### Basic Usage

```python
import asyncio
from backend.cto.metrics import MetricsManager

async def main():
    # Create and start metrics manager
    manager = MetricsManager(
        storage_path="./metrics",
        flush_interval_seconds=5.0,
        max_batch_size=1000
    )
    await manager.start()
    
    # Record operations (non-blocking, O(1))
    await manager.record_operation(
        operation_type="api_request",
        operation_name="GET /api/users",
        duration_ms=42.5,
        success=True,
        metadata={"status_code": 200, "region": "us-east"}
    )
    
    # Graceful shutdown (flushes remaining metrics)
    await manager.stop()

asyncio.run(main())
```

### FastAPI Integration

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.cto.metrics import MetricsManager

# Global metrics manager
metrics_manager: MetricsManager | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage metrics manager lifecycle."""
    global metrics_manager
    
    # Startup
    metrics_manager = MetricsManager(storage_path="./metrics")
    await metrics_manager.start()
    
    yield
    
    # Shutdown
    if metrics_manager:
        await metrics_manager.stop()

app = FastAPI(lifespan=lifespan)

@app.get("/api/users")
async def get_users():
    """Example endpoint with metrics."""
    import time
    start = time.time()
    
    # Your business logic here
    users = ["Alice", "Bob", "Charlie"]
    
    # Record metrics
    duration_ms = (time.time() - start) * 1000
    if metrics_manager:
        await metrics_manager.record_operation(
            operation_type="api_request",
            operation_name="GET /api/users",
            duration_ms=duration_ms,
            success=True,
            metadata={"count": len(users)}
        )
    
    return {"users": users}
```

### Context Manager for Timing

```python
from contextlib import asynccontextmanager
from backend.cto.metrics import MetricsManager
import time

@asynccontextmanager
async def track_operation(
    manager: MetricsManager,
    operation_type: str,
    operation_name: str
):
    """Context manager to automatically track operation duration."""
    start = time.time()
    error_msg = None
    
    try:
        yield
    except Exception as e:
        error_msg = str(e)
        raise
    finally:
        duration_ms = (time.time() - start) * 1000
        await manager.record_operation(
            operation_type=operation_type,
            operation_name=operation_name,
            duration_ms=duration_ms,
            success=(error_msg is None),
            error_message=error_msg
        )

# Usage
async def process_data():
    async with track_operation(
        manager,
        operation_type="computation",
        operation_name="process_user_data"
    ):
        # Your processing logic here
        await expensive_computation()
```

## API Reference

### MetricsManager

#### Constructor

```python
MetricsManager(
    storage_path: str | Path,
    flush_interval_seconds: float = 5.0,
    max_batch_size: int = 1000,
    max_queue_size: int = 10000
)
```

**Parameters:**
- `storage_path`: Directory where metrics JSON files will be stored
- `flush_interval_seconds`: How often to flush metrics to disk (default: 5s)
- `max_batch_size`: Maximum records per batch file (default: 1000)
- `max_queue_size`: Maximum metrics in queue before backpressure (default: 10000)

#### Methods

##### `async start() -> None`

Start the background metrics worker. Must be called before recording metrics.

**Raises:**
- `RuntimeError`: If manager is already running

##### `async stop(timeout: float = 10.0) -> None`

Stop the metrics manager and flush remaining metrics.

**Parameters:**
- `timeout`: Maximum seconds to wait for graceful shutdown (default: 10s)

**Raises:**
- `asyncio.TimeoutError`: If shutdown exceeds timeout

##### `async record_operation(...) -> None`

Record a single operation metric (non-blocking, O(1)).

**Parameters:**
- `operation_type` (str): Type of operation (e.g., "api_request", "db_query")
- `operation_name` (str): Specific operation identifier
- `duration_ms` (float): Operation duration in milliseconds (must be >= 0)
- `success` (bool): Whether the operation succeeded (default: True)
- `error_message` (str, optional): Error message if operation failed
- `metadata` (dict, optional): Additional context (no PII allowed)

**Raises:**
- `ValueError`: If validation fails
- `RuntimeError`: If manager is not running

**Example:**
```python
await manager.record_operation(
    operation_type="database_query",
    operation_name="SELECT users WHERE active = true",
    duration_ms=15.3,
    success=True,
    metadata={"rows_returned": 42, "cache_hit": False}
)
```

##### `async get_stats() -> MetricsStats`

Get current statistics about the metrics system.

**Returns:** `MetricsStats` object with:
- `total_recorded`: Total metrics recorded since start
- `total_persisted`: Total metrics written to disk
- `queue_size`: Current queue size
- `batches_written`: Number of batch files written
- `last_flush_timestamp`: UTC timestamp of last flush
- `avg_batch_size`: Average records per batch
- `is_running`: Whether the worker is running

## Performance Characteristics

### Latency

- **record_operation()**: < 1ms (O(1) queue operation)
- **Disk flush**: Batched every 5 seconds (configurable)
- **Shutdown**: Graceful with final flush (< 10 seconds default)

### Throughput

- **Queue capacity**: 10,000 metrics (configurable)
- **Batch size**: 1,000 records per file (configurable)
- **Expected throughput**: 10,000+ metrics/second

### Memory Usage

- **Per metric**: ~1KB (varies with metadata)
- **Queue memory**: ~10MB at max capacity (10,000 metrics)
- **No memory leaks**: Background worker clears queue regularly

## Data Format

Metrics are persisted as JSON files with the following structure:

```json
{
  "records": [
    {
      "operation_type": "api_request",
      "operation_name": "GET /api/users",
      "duration_ms": 42.5,
      "timestamp": "2025-12-16T08:00:00.000000+00:00",
      "success": true,
      "error_message": null,
      "metadata": {
        "status_code": 200,
        "region": "us-east"
      }
    }
  ],
  "batch_timestamp": "2025-12-16T08:00:05.123456+00:00",
  "batch_id": "20251216_080005_123456",
  "total_records": 1
}
```

**File naming**: `metrics_YYYYMMDD_HHMMSS_microseconds.json`

## Security & Compliance

### PII Protection

The system automatically rejects metadata containing PII-sensitive keys:

```python
# ❌ This will raise ValueError
await manager.record_operation(
    operation_type="api_request",
    operation_name="GET /api/profile",
    duration_ms=50.0,
    metadata={"email": "user@example.com"}  # Forbidden!
)

# ✅ This is allowed
await manager.record_operation(
    operation_type="api_request",
    operation_name="GET /api/profile",
    duration_ms=50.0,
    metadata={"user_hash": "abc123", "region": "us-east"}
)
```

**Forbidden metadata keys:**
- email, name, username, password
- token, key, secret, api_key
- user_id, client_id, session_id

### Compliance

This metrics system is designed to comply with:

- **Loi 25** (Québec): No PII in metrics, anonymized data only
- **PIPEDA** (Canada): Privacy by design, data minimization
- **RGPD/GDPR** (EU): Right to erasure (delete metric files as needed)

### Data Retention

**Recommendation**: Implement automatic deletion of metrics older than 30 days:

```python
from pathlib import Path
from datetime import datetime, timedelta

def cleanup_old_metrics(storage_path: Path, days: int = 30):
    """Delete metrics older than specified days."""
    cutoff = datetime.now() - timedelta(days=days)
    
    for file in storage_path.glob("metrics_*.json"):
        # Parse timestamp from filename
        timestamp_str = file.stem.replace("metrics_", "")
        file_date = datetime.strptime(timestamp_str[:8], "%Y%m%d")
        
        if file_date < cutoff:
            file.unlink()  # Delete file
```

## Best Practices

### 1. Use Descriptive Operation Names

```python
# ❌ Bad: Generic names
await manager.record_operation("api", "request", 50.0)

# ✅ Good: Specific, searchable names
await manager.record_operation(
    "api_request",
    "POST /api/v1/users/create",
    50.0
)
```

### 2. Include Useful Metadata

```python
# ✅ Good: Helps with debugging and analysis
await manager.record_operation(
    operation_type="database_query",
    operation_name="SELECT products",
    duration_ms=125.0,
    metadata={
        "query_hash": "abc123",  # Anonymized query identifier
        "rows_returned": 50,
        "cache_hit": False,
        "database": "products_read_replica"
    }
)
```

### 3. Handle Errors Properly

```python
try:
    result = await expensive_operation()
    await manager.record_operation(
        operation_type="computation",
        operation_name="data_processing",
        duration_ms=duration,
        success=True
    )
except Exception as e:
    await manager.record_operation(
        operation_type="computation",
        operation_name="data_processing",
        duration_ms=duration,
        success=False,
        error_message=str(e)[:1000]  # Truncate to 1000 chars
    )
    raise
```

### 4. Monitor Queue Size

```python
# Periodically check queue health
stats = await manager.get_stats()
if stats.queue_size > 5000:
    logger.warning(
        "Metrics queue is getting full",
        queue_size=stats.queue_size,
        max_queue_size=10000
    )
```

## Troubleshooting

### Queue Full Error

If you see `asyncio.QueueFull` or high queue sizes:

1. **Reduce flush interval**: Lower `flush_interval_seconds` to write more frequently
2. **Increase batch size**: Raise `max_batch_size` to write more per flush
3. **Increase queue size**: Raise `max_queue_size` (consumes more memory)
4. **Check disk I/O**: Ensure disk writes aren't bottlenecked

### Metrics Not Persisting

1. **Check manager is started**: Ensure `await manager.start()` was called
2. **Check storage path**: Verify directory exists and is writable
3. **Check logs**: Look for errors during flush operations
4. **Wait for flush**: Metrics are written every 5 seconds, not immediately

### High Memory Usage

1. **Check queue size**: Use `get_stats()` to monitor queue growth
2. **Reduce queue size**: Lower `max_queue_size` setting
3. **Increase flush frequency**: Lower `flush_interval_seconds`
4. **Check metadata size**: Large metadata dicts increase memory

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_metrics_manager.py -v
```

**Test coverage:**
- Basic operations (start, stop, record)
- Concurrent metric recording
- Batch writes and file persistence
- Statistics tracking
- Edge cases (empty queue, full queue, shutdown)
- Error scenarios (invalid inputs, disk errors)

## License

This code is part of the iAngel CyberIDE project.
See LICENSE file for details.
