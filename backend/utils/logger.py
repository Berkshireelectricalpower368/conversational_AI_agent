"""
Structured logging setup for the Google Drive File Discovery Assistant.

Provides a configured logger with colored console output and structured
formatting. Use `get_logger(__name__)` in any module to get a logger.
"""

import logging
import sys
from typing import Optional


# ── Color codes for terminal output ──────────────────────────
COLORS = {
    "DEBUG":    "\033[36m",   # Cyan
    "INFO":     "\033[32m",   # Green
    "WARNING":  "\033[33m",   # Yellow
    "ERROR":    "\033[31m",   # Red
    "CRITICAL": "\033[1;31m", # Bold Red
    "RESET":    "\033[0m",    # Reset
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log level names in terminal output."""

    def format(self, record: logging.LogRecord) -> str:
        # Add color to the level name
        color = COLORS.get(record.levelname, COLORS["RESET"])
        record.levelname = f"{color}{record.levelname:<8}{COLORS['RESET']}"
        return super().format(record)


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name, typically __name__ of the calling module.
        level: Optional override for log level. If None, uses LOG_LEVEL env var or INFO.
    
    Returns:
        Configured logging.Logger instance.
    
    Usage:
        from backend.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Server started", extra={"port": 8000})
    """
    logger = logging.getLogger(name)

    # Only configure if the logger doesn't already have handlers
    # (prevents duplicate log lines on repeated imports)
    if not logger.handlers:
        # Determine log level
        if level is None:
            import os
            level = os.getenv("LOG_LEVEL", "INFO").upper()

        logger.setLevel(getattr(logging, level, logging.INFO))

        # Console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level, logging.INFO))

        # Format: timestamp | level | module | message
        formatter = ColoredFormatter(
            fmt="%(asctime)s | %(levelname)s | %(name)-30s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Prevent log propagation to root logger (avoids duplicates)
        logger.propagate = False

    return logger
