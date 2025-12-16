"""
Example usage of the high-performance MetricsManager.

This example demonstrates:
1. Basic setup and lifecycle management
2. Recording various types of operations
3. Using context managers for automatic timing
4. Integration with FastAPI
5. Monitoring and observability

Run this example:
    python3 -m backend.cto.metrics.example
"""

import asyncio
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from .manager import MetricsManager
from .models import MetricsStats


# ============================================================================
# Example 1: Basic Usage
# ============================================================================

async def example_basic():
    """Basic metrics recording example."""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)
    
    # Create metrics manager
    manager = MetricsManager(
        storage_path="./example_metrics",
        flush_interval_seconds=2.0,  # Fast flush for demo
        max_batch_size=10
    )
    
    # Start the background worker
    await manager.start()
    print("✓ MetricsManager started")
    
    # Record some operations
    print("\nRecording metrics...")
    
    await manager.record_operation(
        operation_type="api_request",
        operation_name="GET /api/users",
        duration_ms=42.5,
        success=True,
        metadata={"status_code": 200, "region": "us-east"}
    )
    print("  ✓ Recorded API request")
    
    await manager.record_operation(
        operation_type="database_query",
        operation_name="SELECT * FROM users WHERE active = true",
        duration_ms=15.3,
        success=True,
        metadata={"rows_returned": 42, "cache_hit": False}
    )
    print("  ✓ Recorded database query")
    
    await manager.record_operation(
        operation_type="computation",
        operation_name="calculate_user_score",
        duration_ms=125.7,
        success=True
    )
    print("  ✓ Recorded computation")
    
    # Check statistics
    stats = await manager.get_stats()
    print(f"\n📊 Statistics:")
    print(f"  Total recorded: {stats.total_recorded}")
    print(f"  Queue size: {stats.queue_size}")
    print(f"  Running: {stats.is_running}")
    
    # Wait for flush
    print("\n⏳ Waiting for flush (2 seconds)...")
    await asyncio.sleep(2.5)
    
    # Check statistics after flush
    stats = await manager.get_stats()
    print(f"\n📊 Statistics after flush:")
    print(f"  Total persisted: {stats.total_persisted}")
    print(f"  Batches written: {stats.batches_written}")
    print(f"  Average batch size: {stats.avg_batch_size:.1f}")
    print(f"  Queue size: {stats.queue_size}")
    
    # Graceful shutdown
    print("\n🛑 Stopping MetricsManager...")
    await manager.stop()
    print("✓ MetricsManager stopped (all metrics flushed)")
    
    # Show created files
    metrics_dir = Path("./example_metrics")
    if metrics_dir.exists():
        files = list(metrics_dir.glob("metrics_*.json"))
        print(f"\n📁 Created {len(files)} metric file(s):")
        for file in files:
            print(f"  - {file.name}")


# ============================================================================
# Example 2: Context Manager for Timing
# ============================================================================

@asynccontextmanager
async def track_operation(
    manager: MetricsManager,
    operation_type: str,
    operation_name: str
):
    """Context manager to automatically track operation duration."""
    start = time.time()
    error_msg: Optional[str] = None
    
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


async def example_context_manager():
    """Example using context manager for automatic timing."""
    print("\n" + "=" * 60)
    print("Example 2: Context Manager for Timing")
    print("=" * 60)
    
    manager = MetricsManager(storage_path="./example_metrics")
    await manager.start()
    print("✓ MetricsManager started")
    
    # Successful operation
    print("\n⚙️  Running successful operation...")
    async with track_operation(
        manager,
        operation_type="computation",
        operation_name="process_user_data"
    ):
        await asyncio.sleep(0.1)  # Simulate work
    print("✓ Operation completed and metrics recorded")
    
    # Failed operation
    print("\n⚙️  Running failed operation...")
    try:
        async with track_operation(
            manager,
            operation_type="api_request",
            operation_name="POST /api/invalid"
        ):
            await asyncio.sleep(0.05)
            raise ValueError("Invalid request data")
    except ValueError:
        print("✓ Operation failed and error metrics recorded")
    
    # Check statistics
    stats = await manager.get_stats()
    print(f"\n📊 Statistics:")
    print(f"  Total recorded: {stats.total_recorded}")
    
    await manager.stop()
    print("\n✓ MetricsManager stopped")


# ============================================================================
# Example 3: Concurrent Operations
# ============================================================================

async def simulate_concurrent_requests(
    manager: MetricsManager,
    request_id: int,
    count: int
):
    """Simulate concurrent API requests."""
    for i in range(count):
        await manager.record_operation(
            operation_type="api_request",
            operation_name=f"GET /api/endpoint_{i % 5}",
            duration_ms=float(10 + (i * request_id) % 50),
            success=True,
            metadata={"request_id": request_id, "endpoint_id": i % 5}
        )
        # Small delay to simulate real requests
        await asyncio.sleep(0.001)


async def example_concurrent():
    """Example with concurrent metric recording."""
    print("\n" + "=" * 60)
    print("Example 3: Concurrent Operations")
    print("=" * 60)
    
    manager = MetricsManager(
        storage_path="./example_metrics",
        flush_interval_seconds=1.0
    )
    await manager.start()
    print("✓ MetricsManager started")
    
    # Simulate concurrent requests
    print("\n⚙️  Simulating 10 concurrent workers...")
    print("   Each worker records 50 metrics")
    
    start = time.time()
    await asyncio.gather(*[
        simulate_concurrent_requests(manager, i, 50)
        for i in range(10)
    ])
    elapsed = time.time() - start
    
    print(f"✓ Completed in {elapsed:.2f}s")
    
    # Check statistics
    stats = await manager.get_stats()
    print(f"\n📊 Statistics:")
    print(f"  Total recorded: {stats.total_recorded}")
    print(f"  Throughput: {stats.total_recorded / elapsed:.0f} metrics/sec")
    print(f"  Queue size: {stats.queue_size}")
    
    # Wait for flush
    print("\n⏳ Waiting for flush...")
    await asyncio.sleep(1.5)
    
    stats = await manager.get_stats()
    print(f"\n📊 After flush:")
    print(f"  Total persisted: {stats.total_persisted}")
    print(f"  Batches written: {stats.batches_written}")
    print(f"  Queue size: {stats.queue_size}")
    
    await manager.stop()
    print("\n✓ MetricsManager stopped")


# ============================================================================
# Example 4: Monitoring and Observability
# ============================================================================

async def monitor_metrics_health(manager: MetricsManager, duration: float):
    """Monitor metrics system health for a period of time."""
    print(f"\n📊 Monitoring for {duration} seconds...")
    print("    Queue   | Recorded | Persisted | Batches | Status")
    print("    " + "-" * 55)
    
    start = time.time()
    while time.time() - start < duration:
        stats = await manager.get_stats()
        status = "🟢" if stats.is_running else "🔴"
        print(
            f"    {stats.queue_size:6d} | "
            f"{stats.total_recorded:8d} | "
            f"{stats.total_persisted:9d} | "
            f"{stats.batches_written:7d} | {status}"
        )
        await asyncio.sleep(0.5)


async def example_monitoring():
    """Example with monitoring and observability."""
    print("\n" + "=" * 60)
    print("Example 4: Monitoring and Observability")
    print("=" * 60)
    
    manager = MetricsManager(
        storage_path="./example_metrics",
        flush_interval_seconds=2.0
    )
    await manager.start()
    print("✓ MetricsManager started")
    
    # Start monitoring task
    monitor_task = asyncio.create_task(
        monitor_metrics_health(manager, duration=5.0)
    )
    
    # Generate metrics continuously
    for i in range(100):
        await manager.record_operation(
            operation_type="api_request",
            operation_name=f"GET /api/resource/{i % 10}",
            duration_ms=float(20 + i % 80),
            success=True
        )
        await asyncio.sleep(0.05)  # 20 metrics/sec
    
    # Wait for monitoring to complete
    await monitor_task
    
    await manager.stop()
    print("\n✓ MetricsManager stopped")


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("MetricsManager Examples")
    print("=" * 60)
    
    # Run examples sequentially
    await example_basic()
    await example_context_manager()
    await example_concurrent()
    await example_monitoring()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\n💡 Check ./example_metrics/ directory for persisted metrics")
    
    # Cleanup example files (optional)
    cleanup = input("\n🗑️  Delete example metrics files? (y/n): ")
    if cleanup.lower() == 'y':
        import shutil
        metrics_dir = Path("./example_metrics")
        if metrics_dir.exists():
            shutil.rmtree(metrics_dir)
            print("✓ Example metrics deleted")


if __name__ == "__main__":
    asyncio.run(main())
