"""
Configuration management.

Responsibility: Load and provide access to config.
Single Responsibility: Only config loading.
"""

import yaml
from pathlib import Path
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class Config:
    """Manages configuration from files and environment."""

    DEFAULT_CONFIG = {
        "capture": {
            "interface": None,
            "packet_count": 0,  # 0 = unlimited
        },
        "storage": {
            "db_path": "~/.cyb/cyb.db",
        },
        "logging": {
            "level": "INFO",
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """Load configuration."""
        self.config = self.DEFAULT_CONFIG.copy()

        if config_path:
            self._load_file(config_path)
        else:
            self._load_default()

    def _load_default(self) -> None:
        """Load from default locations."""
        default_paths = [
            Path.home() / ".cyb" / "config.yaml",
            Path.home() / ".config" / "cyb" / "config.yaml",
            Path("/etc/cyb/config.yaml"),
        ]

        for path in default_paths:
            if path.exists():
                self._load_file(str(path))
                break

    def _load_file(self, path: str) -> None:
        """Load config from file."""
        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
                self.config.update(data)
                logger.info(f"Config loaded from {path}")
        except Exception as e:
            logger.warning(f"Could not load config from {path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value."""
        return self.config.get(key, default)
