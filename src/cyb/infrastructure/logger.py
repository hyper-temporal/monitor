"""
Logging setup.

Responsibility: Configure logging for the application.
Single Responsibility: Only logging setup.
"""

import logging
import sys
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure logging."""
    log_dir = Path.home() / ".cyb" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_fmt = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_fmt)
    
    # File handler
    file_handler = logging.FileHandler(log_dir / "cyb.log")
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_fmt)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
