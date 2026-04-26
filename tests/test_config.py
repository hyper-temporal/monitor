"""
Tests for configuration management.
Uses inline mock data only — no external fixtures or data.
"""

import unittest
import os
from pathlib import Path
from backend.config import Config, get_config, set_config


class TestConfig(unittest.TestCase):
    """Test Config dataclass and loading."""

    def test_config_defaults(self):
        """Config has sensible defaults."""
        config = Config()
        self.assertEqual(config.CAPTURE_INTERFACE, "any")
        self.assertEqual(config.CAPTURE_PACKET_COUNT, 10)
        self.assertEqual(config.DB_PATH, "cyb.db")
        self.assertEqual(config.LOG_LEVEL, "INFO")

    def test_config_from_env_with_overrides(self):
        """Config.from_env() loads from environment variables."""
        # Set some env vars
        os.environ["CAPTURE_INTERFACE"] = "eth0"
        os.environ["CAPTURE_PACKET_COUNT"] = "20"
        os.environ["LOG_LEVEL"] = "DEBUG"

        config = Config.from_env()

        self.assertEqual(config.CAPTURE_INTERFACE, "eth0")
        self.assertEqual(config.CAPTURE_PACKET_COUNT, 20)
        self.assertEqual(config.LOG_LEVEL, "DEBUG")

        # Clean up
        del os.environ["CAPTURE_INTERFACE"]
        del os.environ["CAPTURE_PACKET_COUNT"]
        del os.environ["LOG_LEVEL"]

    def test_get_config_returns_singleton(self):
        """get_config() returns the same instance."""
        # Reset global state
        import backend.config as cfg_module
        cfg_module._config = None

        config1 = get_config()
        config2 = get_config()

        self.assertIs(config1, config2)

    def test_set_config_updates_global(self):
        """set_config() updates the global instance."""
        custom_config = Config(CAPTURE_INTERFACE="wlan0")
        set_config(custom_config)

        retrieved = get_config()
        self.assertEqual(retrieved.CAPTURE_INTERFACE, "wlan0")


if __name__ == "__main__":
    unittest.main()
