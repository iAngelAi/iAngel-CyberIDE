"""
File Watcher for CyberIDE Neural Core.

This module uses watchdog to monitor file system changes in real-time.
When files change, it triggers test runs and sends updates to the WebSocket server.
"""

import time
import asyncio
from pathlib import Path
from typing import Callable, Optional, Set
from datetime import datetime, timezone
from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    FileSystemEvent,
    FileCreatedEvent,
    FileModifiedEvent,
    FileDeletedEvent,
    FileMovedEvent
)

from .models import FileChangeEvent


class NeuralFileHandler(FileSystemEventHandler):
    """
    Custom file system event handler for CyberIDE.

    This handler filters events and triggers appropriate actions
    based on the type of file that changed.
    """

    def __init__(
        self,
        on_change_callback: Callable[[FileChangeEvent], None],
        debounce_seconds: float = 1.0
    ):
        """
        Initialize the file handler.

        Args:
            on_change_callback: Async function to call when files change
            debounce_seconds: Wait time to batch rapid changes
        """
        super().__init__()
        self.on_change_callback = on_change_callback
        self.debounce_seconds = debounce_seconds
        self.last_event_time: dict = {}
        self.ignored_patterns: Set[str] = {
            ".git",
            ".pytest_cache",
            "__pycache__",
            "node_modules",
            ".coverage",
            ".venv",
            "venv",
            ".DS_Store",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".mypy_cache",
            ".ruff_cache",
            "dist",
            "build",
            "*.log"
        }

    def should_ignore(self, path: str) -> bool:
        """Check if a path should be ignored."""
        path_obj = Path(path)

        # Check if any part of path matches ignored patterns
        for pattern in self.ignored_patterns:
            if pattern.startswith("*."):
                # File extension pattern
                if path_obj.suffix == pattern[1:]:
                    return True
            else:
                # Directory or filename pattern
                if pattern in path_obj.parts:
                    return True
                if path_obj.name == pattern:
                    return True

        return False

    def should_debounce(self, path: str) -> bool:
        """
        Check if event should be debounced.

        Returns True if we should ignore this event (too soon after last one).
        """
        now = time.time()
        last_time = self.last_event_time.get(path, 0)

        if now - last_time < self.debounce_seconds:
            return True

        self.last_event_time[path] = now
        return False

    def on_created(self, event: FileCreatedEvent) -> None:
        """Handle file creation events."""
        if event.is_directory:
            return

        if self.should_ignore(event.src_path):
            return

        if self.should_debounce(event.src_path):
            return

        change_event = FileChangeEvent(
            event_type="created",
            file_path=event.src_path,
            is_test_file=self._is_test_file(event.src_path),
            timestamp=datetime.now(timezone.utc)
        )

        self._handle_event(change_event)

    def on_modified(self, event: FileModifiedEvent) -> None:
        """Handle file modification events."""
        if event.is_directory:
            return

        if self.should_ignore(event.src_path):
            return

        if self.should_debounce(event.src_path):
            return

        change_event = FileChangeEvent(
            event_type="modified",
            file_path=event.src_path,
            is_test_file=self._is_test_file(event.src_path),
            timestamp=datetime.now(timezone.utc)
        )

        self._handle_event(change_event)

    def on_deleted(self, event: FileDeletedEvent) -> None:
        """Handle file deletion events."""
        if event.is_directory:
            return

        if self.should_ignore(event.src_path):
            return

        change_event = FileChangeEvent(
            event_type="deleted",
            file_path=event.src_path,
            is_test_file=self._is_test_file(event.src_path),
            timestamp=datetime.now(timezone.utc)
        )

        self._handle_event(change_event)

    def on_moved(self, event: FileMovedEvent) -> None:
        """Handle file move/rename events."""
        if event.is_directory:
            return

        if self.should_ignore(event.dest_path):
            return

        change_event = FileChangeEvent(
            event_type="moved",
            file_path=event.dest_path,
            is_test_file=self._is_test_file(event.dest_path),
            timestamp=datetime.now(timezone.utc)
        )

        self._handle_event(change_event)

    def _handle_event(self, event: FileChangeEvent) -> None:
        """Process a file change event."""
        try:
            # Call the async callback
            self.on_change_callback(event)
        except Exception as e:
            print(f"❌ Error handling file event: {e}")

    def _is_test_file(self, path: str) -> bool:
        """Check if a file is a test file."""
        path_obj = Path(path)
        return (
            path_obj.name.startswith("test_") and
            path_obj.suffix == ".py" and
            "tests" in path_obj.parts
        )


class FileWatcher:
    """
    File system watcher for CyberIDE project.

    Monitors src/, tests/, and neural_cli/ directories for changes
    and triggers appropriate actions (test runs, metric updates).
    """

    def __init__(
        self,
        project_root: str,
        on_change_callback: Callable[[FileChangeEvent], None]
    ):
        """
        Initialize the file watcher.

        Args:
            project_root: Absolute path to project root
            on_change_callback: Async function to call on file changes
        """
        self.project_root = Path(project_root)
        self.on_change_callback = on_change_callback
        self.observer: Optional[Observer] = None
        self.handler: Optional[NeuralFileHandler] = None

        # Directories to watch
        self.watch_dirs = [
            self.project_root / "src",
            self.project_root / "tests",
            self.project_root / "neural_cli"
        ]

    def start(self) -> None:
        """Start watching for file changes."""
        if self.observer is not None:
            print("⚠ File watcher already running")
            return

        print("ℹ Starting Neural File Watcher...")

        # Create handler
        self.handler = NeuralFileHandler(
            on_change_callback=self.on_change_callback,
            debounce_seconds=1.0
        )

        # Create observer
        self.observer = Observer()

        # Schedule watches for each directory
        for watch_dir in self.watch_dirs:
            if watch_dir.exists():
                self.observer.schedule(
                    self.handler,
                    str(watch_dir),
                    recursive=True
                )
                print(f"  ✓ Watching: {watch_dir.relative_to(self.project_root)}/")
            else:
                print(f"  ⚠ Directory not found: {watch_dir.relative_to(self.project_root)}/")

        # Start observer
        self.observer.start()
        print("✓ Neural File Watcher active")
        print("  Monitoring for file changes...")

    def stop(self) -> None:
        """Stop watching for file changes."""
        if self.observer is None:
            return

        print("\nℹ Stopping Neural File Watcher...")
        self.observer.stop()
        self.observer.join(timeout=5.0)
        self.observer = None
        self.handler = None
        print("✓ File watcher stopped")

    def is_running(self) -> bool:
        """Check if watcher is currently running."""
        return self.observer is not None and self.observer.is_alive()

    def add_watch_directory(self, directory: Path) -> None:
        """
        Add a new directory to watch.

        Args:
            directory: Path to directory to watch
        """
        if self.observer is None or self.handler is None:
            print("⚠ Cannot add watch: watcher not running")
            return

        if not directory.exists():
            print(f"⚠ Directory does not exist: {directory}")
            return

        self.observer.schedule(
            self.handler,
            str(directory),
            recursive=True
        )
        print(f"✓ Added watch: {directory}")

    def remove_ignored_pattern(self, pattern: str) -> None:
        """
        Remove a pattern from the ignore list.

        Args:
            pattern: Pattern to stop ignoring (e.g., "*.log")
        """
        if self.handler is None:
            return

        if pattern in self.handler.ignored_patterns:
            self.handler.ignored_patterns.remove(pattern)
            print(f"✓ Removed ignore pattern: {pattern}")

    def add_ignored_pattern(self, pattern: str) -> None:
        """
        Add a pattern to the ignore list.

        Args:
            pattern: Pattern to ignore (e.g., "*.tmp")
        """
        if self.handler is None:
            return

        self.handler.ignored_patterns.add(pattern)
        print(f"✓ Added ignore pattern: {pattern}")

    def get_watched_directories(self) -> list[str]:
        """Get list of currently watched directories."""
        if self.observer is None:
            return []

        # Watchdog doesn't provide easy access to scheduled watches
        # Return our configured watch list
        return [str(d.relative_to(self.project_root)) for d in self.watch_dirs if d.exists()]

    def get_stats(self) -> dict:
        """
        Get watcher statistics.

        Returns:
            Dictionary with watcher stats
        """
        return {
            "is_running": self.is_running(),
            "watched_directories": self.get_watched_directories(),
            "ignored_patterns_count": len(self.handler.ignored_patterns) if self.handler else 0,
            "project_root": str(self.project_root)
        }


async def create_file_watcher(
    project_root: str,
    on_change_callback: Callable[[FileChangeEvent], None]
) -> FileWatcher:
    """
    Create and start a file watcher (async factory).

    Args:
        project_root: Absolute path to project root
        on_change_callback: Async function to call on changes

    Returns:
        Running FileWatcher instance
    """
    watcher = FileWatcher(project_root, on_change_callback)
    watcher.start()
    return watcher
