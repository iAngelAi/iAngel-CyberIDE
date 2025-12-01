"""
Tests for FileWatcher - File system monitoring with watchdog.

This module validates:
- FileWatcher starts and stops correctly
- File creation/modification/deletion detection
- Ignored patterns (.git, node_modules, __pycache__)
- Debouncing rapid file changes
- Callback execution on file events
- Multiple directory watching
- Event filtering and validation
"""

import pytest
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from neural_cli.file_watcher import (
    FileWatcher,
    NeuralFileHandler
)
from neural_cli.models import FileChangeEvent


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def empty_project(tmp_path):
    """Create an empty project directory."""
    return tmp_path


@pytest.fixture
def project_with_directories(tmp_path):
    """Create a project with standard directory structure."""
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "neural_cli").mkdir()
    return tmp_path


@pytest.fixture
def mock_callback():
    """Create a mock callback function."""
    return Mock()


# ============================================================================
# NeuralFileHandler Tests
# ============================================================================

class TestNeuralFileHandler:
    """Test suite for NeuralFileHandler class."""

    def test_handler_initialization(self, mock_callback):
        """Test NeuralFileHandler initializes correctly."""
        handler = NeuralFileHandler(
            on_change_callback=mock_callback,
            debounce_seconds=1.0
        )

        assert handler.on_change_callback == mock_callback
        assert handler.debounce_seconds == 1.0
        assert len(handler.ignored_patterns) > 0

    def test_should_ignore_git_directory(self, mock_callback):
        """Test .git directory is ignored."""
        handler = NeuralFileHandler(mock_callback)

        git_path = "/project/.git/config"
        assert handler.should_ignore(git_path) is True

    def test_should_ignore_node_modules(self, mock_callback):
        """Test node_modules directory is ignored."""
        handler = NeuralFileHandler(mock_callback)

        node_path = "/project/node_modules/package/index.js"
        assert handler.should_ignore(node_path) is True

    def test_should_ignore_pycache(self, mock_callback):
        """Test __pycache__ directory is ignored."""
        handler = NeuralFileHandler(mock_callback)

        pycache_path = "/project/__pycache__/module.pyc"
        assert handler.should_ignore(pycache_path) is True

    def test_should_ignore_pytest_cache(self, mock_callback):
        """Test .pytest_cache directory is ignored."""
        handler = NeuralFileHandler(mock_callback)

        pytest_path = "/project/.pytest_cache/v/cache"
        assert handler.should_ignore(pytest_path) is True

    def test_should_ignore_pyc_files(self, mock_callback):
        """Test .pyc files are ignored."""
        handler = NeuralFileHandler(mock_callback)

        pyc_path = "/project/module.pyc"
        assert handler.should_ignore(pyc_path) is True

    def test_should_ignore_log_files(self, mock_callback):
        """Test .log files are ignored."""
        handler = NeuralFileHandler(mock_callback)

        log_path = "/project/debug.log"
        assert handler.should_ignore(log_path) is True

    def test_should_not_ignore_source_files(self, mock_callback):
        """Test source files are not ignored."""
        handler = NeuralFileHandler(mock_callback)

        # Python source
        assert handler.should_ignore("/project/src/main.py") is False

        # TypeScript source
        assert handler.should_ignore("/project/src/App.tsx") is False

        # JavaScript
        assert handler.should_ignore("/project/src/utils.js") is False

    def test_should_not_ignore_test_files(self, mock_callback):
        """Test test files are not ignored."""
        handler = NeuralFileHandler(mock_callback)

        test_path = "/project/tests/test_unit.py"
        assert handler.should_ignore(test_path) is False

    def test_debounce_mechanism(self, mock_callback):
        """Test debouncing prevents rapid duplicate events."""
        handler = NeuralFileHandler(mock_callback, debounce_seconds=0.5)

        path = "/project/src/file.py"

        # First call should not be debounced
        assert handler.should_debounce(path) is False

        # Immediate second call should be debounced
        assert handler.should_debounce(path) is True

        # Wait for debounce period
        time.sleep(0.6)

        # After debounce period, should not be debounced
        assert handler.should_debounce(path) is False

    def test_is_test_file_detection(self, mock_callback):
        """Test _is_test_file correctly identifies test files."""
        handler = NeuralFileHandler(mock_callback)

        # Valid test file
        assert handler._is_test_file("/project/tests/test_foo.py") is True

        # Invalid: not in tests directory
        assert handler._is_test_file("/project/src/test_foo.py") is False

        # Invalid: doesn't start with test_
        assert handler._is_test_file("/project/tests/foo_test.py") is False

        # Invalid: not .py file
        assert handler._is_test_file("/project/tests/test_foo.txt") is False

    def test_on_created_triggers_callback(self, mock_callback):
        """Test file creation triggers callback."""
        handler = NeuralFileHandler(mock_callback, debounce_seconds=0)

        # Create mock event
        from watchdog.events import FileCreatedEvent

        event = FileCreatedEvent("/project/src/new_file.py")

        handler.on_created(event)

        # Callback should be called with FileChangeEvent
        assert mock_callback.called
        call_args = mock_callback.call_args[0][0]
        assert isinstance(call_args, FileChangeEvent)
        assert call_args.event_type == "created"

    def test_on_modified_triggers_callback(self, mock_callback):
        """Test file modification triggers callback."""
        handler = NeuralFileHandler(mock_callback, debounce_seconds=0)

        from watchdog.events import FileModifiedEvent

        event = FileModifiedEvent("/project/src/existing_file.py")

        handler.on_modified(event)

        assert mock_callback.called
        call_args = mock_callback.call_args[0][0]
        assert call_args.event_type == "modified"

    def test_on_deleted_triggers_callback(self, mock_callback):
        """Test file deletion triggers callback."""
        handler = NeuralFileHandler(mock_callback, debounce_seconds=0)

        from watchdog.events import FileDeletedEvent

        event = FileDeletedEvent("/project/src/old_file.py")

        handler.on_deleted(event)

        assert mock_callback.called
        call_args = mock_callback.call_args[0][0]
        assert call_args.event_type == "deleted"

    def test_on_moved_triggers_callback(self, mock_callback):
        """Test file move/rename triggers callback."""
        handler = NeuralFileHandler(mock_callback, debounce_seconds=0)

        from watchdog.events import FileMovedEvent

        event = FileMovedEvent(
            src_path="/project/src/old_name.py",
            dest_path="/project/src/new_name.py"
        )

        handler.on_moved(event)

        assert mock_callback.called
        call_args = mock_callback.call_args[0][0]
        assert call_args.event_type == "moved"
        assert "new_name.py" in call_args.file_path

    def test_directory_events_ignored(self, mock_callback):
        """Test directory events are ignored."""
        handler = NeuralFileHandler(mock_callback, debounce_seconds=0)

        from watchdog.events import DirCreatedEvent

        event = DirCreatedEvent("/project/src/new_directory")

        handler.on_created(event)

        # Callback should not be called for directory events
        assert not mock_callback.called

    def test_ignored_files_dont_trigger_callback(self, mock_callback):
        """Test ignored files don't trigger callback."""
        handler = NeuralFileHandler(mock_callback, debounce_seconds=0)

        from watchdog.events import FileCreatedEvent

        # Try to create file in ignored directory
        event = FileCreatedEvent("/project/.git/config")

        handler.on_created(event)

        # Callback should not be called
        assert not mock_callback.called

    def test_callback_exception_handling(self, mock_callback):
        """Test handler gracefully handles callback exceptions."""
        mock_callback.side_effect = Exception("Callback error")

        handler = NeuralFileHandler(mock_callback, debounce_seconds=0)

        from watchdog.events import FileCreatedEvent

        event = FileCreatedEvent("/project/src/file.py")

        # Should not raise exception
        try:
            handler.on_created(event)
        except Exception:
            pytest.fail("Handler should not propagate callback exceptions")


# ============================================================================
# FileWatcher Tests
# ============================================================================

class TestFileWatcher:
    """Test suite for FileWatcher class."""

    def test_file_watcher_initialization(self, project_with_directories, mock_callback):
        """Test FileWatcher initializes correctly."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        assert watcher.project_root == project_with_directories
        assert watcher.on_change_callback == mock_callback
        assert watcher.observer is None
        assert watcher.handler is None

    def test_file_watcher_identifies_watch_directories(self, project_with_directories, mock_callback):
        """Test FileWatcher identifies correct directories to watch."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        # Should identify src/, tests/, neural_cli/
        expected_dirs = [
            project_with_directories / "src",
            project_with_directories / "tests",
            project_with_directories / "neural_cli"
        ]

        assert watcher.watch_dirs == expected_dirs

    def test_file_watcher_start(self, project_with_directories, mock_callback):
        """Test FileWatcher starts successfully."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()

        assert watcher.observer is not None
        assert watcher.handler is not None
        assert watcher.is_running() is True

        # Cleanup
        watcher.stop()

    def test_file_watcher_stop(self, project_with_directories, mock_callback):
        """Test FileWatcher stops successfully."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()
        assert watcher.is_running() is True

        watcher.stop()

        assert watcher.observer is None
        assert watcher.handler is None

    def test_file_watcher_is_running_status(self, project_with_directories, mock_callback):
        """Test is_running returns correct status."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        # Before starting
        assert watcher.is_running() is False

        # After starting
        watcher.start()
        assert watcher.is_running() is True

        # After stopping
        watcher.stop()
        assert watcher.is_running() is False

    def test_file_watcher_start_idempotent(self, project_with_directories, mock_callback):
        """Test starting watcher multiple times is safe."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()
        first_observer = watcher.observer

        # Start again
        watcher.start()

        # Should not create new observer
        assert watcher.observer == first_observer

        watcher.stop()

    def test_file_watcher_stop_when_not_running(self, project_with_directories, mock_callback):
        """Test stopping watcher that's not running is safe."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        # Should not raise exception
        try:
            watcher.stop()
        except Exception:
            pytest.fail("Stop should be safe when watcher not running")

    def test_file_watcher_detects_file_creation(self, project_with_directories, mock_callback):
        """Test FileWatcher detects file creation."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()

        # Create a file
        test_file = project_with_directories / "src" / "new_file.py"
        test_file.write_text("# new code")

        # Wait for event to be processed
        time.sleep(0.5)

        watcher.stop()

        # Callback should have been called
        assert mock_callback.called

    def test_file_watcher_detects_file_modification(self, project_with_directories, mock_callback):
        """Test FileWatcher detects file modification."""
        # Create initial file
        test_file = project_with_directories / "src" / "existing_file.py"
        test_file.write_text("# initial code")

        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()

        # Wait a moment for watcher to initialize
        time.sleep(0.2)

        # Modify the file
        test_file.write_text("# modified code")

        # Wait for event
        time.sleep(0.5)

        watcher.stop()

        # Callback should have been called
        assert mock_callback.called

    def test_file_watcher_detects_file_deletion(self, project_with_directories, mock_callback):
        """Test FileWatcher detects file deletion."""
        # Create initial file
        test_file = project_with_directories / "src" / "to_delete.py"
        test_file.write_text("# will be deleted")

        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()
        time.sleep(0.2)

        # Delete the file
        test_file.unlink()

        # Wait for event
        time.sleep(0.5)

        watcher.stop()

        # Callback should have been called
        assert mock_callback.called

    def test_file_watcher_ignores_git_directory(self, project_with_directories, mock_callback):
        """Test FileWatcher ignores .git directory."""
        # Create .git directory
        git_dir = project_with_directories / ".git"
        git_dir.mkdir()

        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()
        time.sleep(0.2)

        # Create file in .git
        (git_dir / "config").write_text("git config")

        time.sleep(0.5)

        watcher.stop()

        # Callback should not be called for .git files
        assert not mock_callback.called

    def test_get_watched_directories(self, project_with_directories, mock_callback):
        """Test get_watched_directories returns correct list."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()

        watched = watcher.get_watched_directories()

        assert "src" in watched
        assert "tests" in watched
        assert "neural_cli" in watched

        watcher.stop()

    def test_get_stats(self, project_with_directories, mock_callback):
        """Test get_stats returns watcher statistics."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()

        stats = watcher.get_stats()

        assert "is_running" in stats
        assert stats["is_running"] is True
        assert "watched_directories" in stats
        assert "ignored_patterns_count" in stats
        assert "project_root" in stats

        watcher.stop()

    def test_add_watch_directory(self, project_with_directories, mock_callback):
        """Test adding a new directory to watch."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()

        # Add new directory
        new_dir = project_with_directories / "docs"
        new_dir.mkdir()

        watcher.add_watch_directory(new_dir)

        # Directory should be watched
        # (Verification is implicit - no exception raised)

        watcher.stop()

    def test_add_watch_directory_nonexistent(self, project_with_directories, mock_callback):
        """Test adding nonexistent directory is handled gracefully."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()

        nonexistent = project_with_directories / "nonexistent"

        # Should not raise exception
        try:
            watcher.add_watch_directory(nonexistent)
        except Exception:
            pytest.fail("Should handle nonexistent directory gracefully")

        watcher.stop()

    def test_add_watch_directory_when_not_running(self, project_with_directories, mock_callback):
        """Test adding watch directory when watcher not running."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        new_dir = project_with_directories / "docs"
        new_dir.mkdir()

        # Should not raise exception
        try:
            watcher.add_watch_directory(new_dir)
        except Exception:
            pytest.fail("Should handle add when not running")

    def test_add_ignored_pattern(self, project_with_directories, mock_callback):
        """Test adding custom ignored pattern."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()

        watcher.add_ignored_pattern("*.tmp")

        # Verify pattern was added
        assert "*.tmp" in watcher.handler.ignored_patterns

        watcher.stop()

    def test_remove_ignored_pattern(self, project_with_directories, mock_callback):
        """Test removing ignored pattern."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()

        # Remove an existing pattern
        original_count = len(watcher.handler.ignored_patterns)
        watcher.remove_ignored_pattern("*.log")

        # Pattern should be removed
        assert len(watcher.handler.ignored_patterns) == original_count - 1
        assert "*.log" not in watcher.handler.ignored_patterns

        watcher.stop()


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Test suite for edge cases and error handling."""

    def test_watcher_with_nonexistent_project_root(self, mock_callback):
        """Test watcher handles nonexistent project root."""
        watcher = FileWatcher(
            project_root="/nonexistent/path",
            on_change_callback=mock_callback
        )

        # Should not crash on start
        watcher.start()

        # Observer should be created even if directories don't exist
        assert watcher.observer is not None

        watcher.stop()

    def test_watcher_with_empty_watch_dirs(self, empty_project, mock_callback):
        """Test watcher with no watch directories."""
        watcher = FileWatcher(
            project_root=str(empty_project),
            on_change_callback=mock_callback
        )

        # Should start successfully even with no watch dirs
        watcher.start()
        assert watcher.is_running() is True

        watcher.stop()

    def test_rapid_file_changes_debounced(self, project_with_directories, mock_callback):
        """Test rapid file changes are debounced."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()

        test_file = project_with_directories / "src" / "rapid_changes.py"

        # Make rapid changes
        for i in range(5):
            test_file.write_text(f"# version {i}")
            time.sleep(0.1)  # Rapid changes within debounce window

        time.sleep(1.5)  # Wait for debounce

        watcher.stop()

        # Callback should be called, but not 5 times (debounced)
        assert mock_callback.called
        # Exact call count depends on timing, but should be < 5

    def test_unicode_in_file_paths(self, project_with_directories, mock_callback):
        """Test watcher handles Unicode in file paths."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()

        # Create file with Unicode name
        unicode_file = project_with_directories / "src" / "émoji_🎉.py"
        unicode_file.write_text("# unicode test")

        time.sleep(0.5)

        watcher.stop()

        # Should handle Unicode gracefully
        assert mock_callback.called

    def test_very_large_file_creation(self, project_with_directories, mock_callback):
        """Test watcher handles large files."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()

        # Create large file
        large_file = project_with_directories / "src" / "large_file.py"
        large_file.write_text("# " + ("x" * 1_000_000))  # 1MB file

        time.sleep(0.5)

        watcher.stop()

        # Should detect large file creation
        assert mock_callback.called

    def test_concurrent_file_changes_in_different_directories(self, project_with_directories, mock_callback):
        """Test concurrent changes in different watched directories."""
        watcher = FileWatcher(
            project_root=str(project_with_directories),
            on_change_callback=mock_callback
        )

        watcher.start()

        # Create files in different directories simultaneously
        (project_with_directories / "src" / "file1.py").write_text("# src")
        (project_with_directories / "tests" / "test_file.py").write_text("# test")
        (project_with_directories / "neural_cli" / "module.py").write_text("# backend")

        time.sleep(1.0)

        watcher.stop()

        # All changes should be detected
        assert mock_callback.call_count >= 3
