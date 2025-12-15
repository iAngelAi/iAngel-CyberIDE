import json
from pathlib import Path
from typing import List
from datetime import datetime

from .models import PytestRunResult

class TestHistoryManager:
    """
    Manages the history of test runs.

    Persists test results to a JSON file and retrieves them.
    """

    def __init__(self, project_root: str, max_history: int = 50):
        """
        Initialize the history manager.

        Args:
            project_root: Absolute path to the project root directory
            max_history: Maximum number of historical records to keep
        """
        self.project_root = Path(project_root)
        self.history_file = self.project_root / "test_history.json"
        self.max_history = max_history

    def add_result(self, result: PytestRunResult) -> None:
        """
        Add a new test result to history.

        Args:
            result: The PytestRunResult to add
        """
        history = self._load_history()

        # Add new result to the beginning of the list
        history.insert(0, result.model_dump(mode='json'))

        # Trim history if it exceeds the limit
        if len(history) > self.max_history:
            history = history[:self.max_history]

        self._save_history(history)

    def get_history(self, limit: int = 10) -> List[dict]:
        """
        Get recent test history.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of test result dictionaries
        """
        history = self._load_history()
        return history[:limit]

    def _load_history(self) -> List[dict]:
        """Load history from file."""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠ Failed to load test history: {e}")
            return []

    def _save_history(self, history: List[dict]) -> None:
        """Save history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save test history: {e}")
