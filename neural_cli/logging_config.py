"""
Logging configuration for CyberIDE Neural Core.

This module provides centralized logging setup with:
- Console output with Neural Core visual identity (emojis preserved)
- Configurable log levels via NEURAL_LOG_LEVEL environment variable
- pytest-compatible log capture via standard logging

Usage:
    # At application startup (main.py lifespan)
    from neural_cli.logging_config import setup_logging
    setup_logging()

    # In any module
    from neural_cli.logging_config import get_logger
    logger = get_logger(__name__)
    logger.info("Message here")

Environment Variables:
    NEURAL_LOG_LEVEL: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)

See Also:
    ADR-001: docs/adr/ADR-001-logging-strategy.md
"""

import logging
import os
import sys
from typing import Final

# -----------------------------------------------------------------------------
# Configuration Constants
# -----------------------------------------------------------------------------

LOG_FORMAT: Final[str] = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_LEVEL: Final[str] = "INFO"
ENV_LOG_LEVEL_KEY: Final[str] = "NEURAL_LOG_LEVEL"

# Track if logging has been configured to prevent duplicate handlers
_logging_configured: bool = False


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------

def setup_logging() -> None:
    """
    Configure logging for the Neural Core application.

    This function should be called once at application startup, typically
    in the FastAPI lifespan context manager in main.py.

    The log level can be controlled via the NEURAL_LOG_LEVEL environment
    variable. Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL.

    This function is idempotent - calling it multiple times is safe and
    will not create duplicate handlers.

    Example:
        # In main.py lifespan
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            setup_logging()
            # ... rest of startup
            yield
            # ... shutdown
    """
    global _logging_configured

    if _logging_configured:
        # Already configured, skip to prevent duplicate handlers
        return

    log_level = _get_log_level_from_env()

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[_create_console_handler(log_level)],
        force=True  # Python 3.8+: reconfigure even if already configured
    )

    # Reduce noise from third-party libraries
    _configure_third_party_loggers()

    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    This is the standard way to obtain a logger in any neural_cli module.
    The logger will inherit the configuration set by setup_logging().

    Args:
        name: The module name, typically __name__

    Returns:
        A configured Logger instance

    Example:
        from neural_cli.logging_config import get_logger

        logger = get_logger(__name__)

        def some_function():
            logger.info("Processing started")
            logger.warning("Something unusual: %s", detail)
            logger.error("Failed to process: %s", error)
    """
    return logging.getLogger(name)


# -----------------------------------------------------------------------------
# Internal Helpers
# -----------------------------------------------------------------------------

def _get_log_level_from_env() -> int:
    """
    Read log level from environment variable.

    Returns:
        Logging level constant (e.g., logging.INFO)
    """
    level_name = os.getenv(ENV_LOG_LEVEL_KEY, DEFAULT_LOG_LEVEL).upper()

    # Validate and convert to logging constant
    level = getattr(logging, level_name, None)

    if level is None or not isinstance(level, int):
        # Invalid level specified, fall back to default
        # We can't log this warning yet since logging isn't configured
        level = logging.INFO

    return level


def _create_console_handler(level: int) -> logging.StreamHandler:
    """
    Create a console handler with the specified level.

    Args:
        level: Logging level for the handler

    Returns:
        Configured StreamHandler
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    return handler


def _configure_third_party_loggers() -> None:
    """
    Reduce verbosity of third-party library loggers.

    These libraries can be noisy at INFO level, so we set them to WARNING
    unless the user explicitly requests DEBUG level globally.
    """
    noisy_loggers = [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "watchdog",
        "watchdog.observers",
        "httpx",
        "httpcore",
    ]

    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
