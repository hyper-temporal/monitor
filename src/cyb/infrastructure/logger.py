"""
Logging setup.

Responsibility: Configure logging for the application.
Single Responsibility: Only logging setup.
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure logging for the entire application.
    
    Args:
        level: Log level (logging.INFO, logging.DEBUG, etc.)
    """
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(level)  # Root logger accepts this level and above
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Single console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    
    root_logger.addHandler(handler)
