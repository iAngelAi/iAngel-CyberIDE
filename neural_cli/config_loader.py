"""
Config Loader for Neural Core.

Handles loading and validation of 'neural.config.json'.
Provides auto-detection of project type if configuration is missing.
"""

import json
import os
from pathlib import Path
from typing import Optional

from .models import NeuralConfig
from .logging_config import get_logger

logger = get_logger(__name__)

class ConfigLoader:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.config_path = self.project_root / "neural.config.json"

    def load_config(self) -> NeuralConfig:
        """
        Load configuration from file or auto-detect settings.
        Includes robust error handling and validation.
        """
        if self.config_path.exists():
            logger.info(f"📂 Loading configuration from: {self.config_path}")
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                
                # Validation Pydantic explicite
                config = NeuralConfig(**data)
                logger.info("✓ Configuration validated successfully")
                return config
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON in neural.config.json at line {e.lineno}, column {e.colno}: {e.msg}")
                logger.warning("⚠ Falling back to auto-detection due to config error.")
            except Exception as e:
                logger.error(f"❌ Failed to load config file: {e}")
                logger.warning("⚠ Falling back to auto-detection.")
        
        return self._detect_project_settings()

    def _detect_project_settings(self) -> NeuralConfig:
        """
        Auto-detect project type and sensible defaults.
        """
        config = NeuralConfig()
        
        # Node.js detection
        if (self.project_root / "package.json").exists():
            logger.info("ℹ Detected Node.js project")
            config.project_type = "node"
            config.test_command = "npm test"
            config.file_extensions = [".ts", ".tsx", ".js", ".jsx"]
            # Default regions for JS/TS
            config.region_mapping["core-logic"] = ["src/utils", "src/lib", "lib", "utils"]
            config.region_mapping["ui-components"] = ["src/components", "components", "src/views"]
        
        # Python detection
        elif (self.project_root / "pyproject.toml").exists() or (self.project_root / "requirements.txt").exists():
            logger.info("ℹ Detected Python project")
            config.project_type = "python"
            config.test_command = "pytest"
            config.file_extensions = [".py"]
            # Default regions for Python
            config.region_mapping["core-logic"] = ["src", "lib", "core", "app"]
            config.region_mapping["tests"] = ["tests"]

        # Rust detection
        elif (self.project_root / "Cargo.toml").exists():
            logger.info("ℹ Detected Rust project")
            config.project_type = "rust"
            config.test_command = "cargo test"
            config.file_extensions = [".rs"]
            config.source_dirs = ["src"]
            config.test_dirs = ["tests"]

        else:
            logger.info("ℹ Unknown project type, using generic defaults")

        return config
