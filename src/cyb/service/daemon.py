"""
Backend daemon entry point: packet capture service with elevated privileges.

Responsibility: CLI argument parsing, config loading, setup, and daemon lifecycle.
Delegates actual monitoring work to NetworkMonitorService.

Single Responsibility: Only handles setup and entry point, not monitoring logic.
"""

import sys
import argparse
import signal
import logging
from pathlib import Path

from cyb.infrastructure import get_logger, Config
from cyb.infrastructure.logger import setup_logging
from cyb.service import NetworkMonitorService

# Global reference for signal handler
service = None
logger = None


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    if logger:
        logger.info("")
        logger.info("Capture interrupted by user.")
    sys.exit(0)


def _setup_logging(log_level: str) -> logging.Logger:
    """Configure logging for backend daemon."""
    # Convert string level to logging constant
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Setup root logger with handlers
    setup_logging(level=level)
    
    # Get logger for this module
    return get_logger(__name__)


def _print_welcome() -> None:
    """Print welcome banner."""
    print("")
    print("╔════════════════════════════════════════════════════╗")
    print("║    Cyber Observability Backend Daemon — Capture   ║")
    print("╚════════════════════════════════════════════════════╝")
    print("")


def _print_config(interface: str, packet_limit: int, db_path: str, log_level: str) -> None:
    """Print configuration summary."""
    print("Configuration (from .env and CLI args):")
    print(f"  • Capture Interface: {interface}")
    print(f"  • Packet Limit: {packet_limit if packet_limit > 0 else 'unlimited'}")
    print(f"  • Database: {db_path}")
    print(f"  • Log Level: {log_level}")
    print("")


def _print_instructions() -> None:
    """Print usage instructions."""
    print("What to do:")
    print("  1. Open another terminal and run: python frontend_app.py")
    print("  2. In the frontend window, watch connections appear in real-time")
    print("  3. Generate network traffic (ping, curl, browse, etc.)")
    print("  4. Press Ctrl+C here to stop capture (frontend keeps running)")
    print("")
    print("ℹ️  The database is shared between backend and frontend via SQLite")
    print("")


def _setup_database_permissions(db_path: str) -> None:
    """Ensure database file is writable by all users."""
    try:
        import os
        if os.path.exists(db_path):
            os.chmod(db_path, 0o666)
            logger.info(f"✓ Database permissions set: {db_path}")
    except Exception as e:
        logger.warning(f"Could not set database permissions: {e}")


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Cyber Observability Backend Daemon - Packet Capture Service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Capture from default interface (requires sudo)
  sudo python -m cyb.service.daemon

  # Capture from specific interface
  sudo python -m cyb.service.daemon --interface en0

  # Capture with custom packet limit
  sudo python -m cyb.service.daemon --interface en0 --packets 100

  # Debug mode (verbose logging)
  LOG_LEVEL=DEBUG sudo python -m cyb.service.daemon
        """
    )

    parser.add_argument(
        "--interface",
        type=str,
        help="Network interface to capture from (e.g., en0, en1, any)"
    )
    parser.add_argument(
        "--packets",
        type=int,
        help="Maximum number of packets to capture (0 = unlimited)"
    )

    return parser.parse_args()


def main():
    """Main entry point for backend daemon."""
    global service, logger

    # Parse arguments
    args = _parse_args()

    # Load configuration
    config = Config()
    log_level = config.get("logging", {}).get("level", "INFO")
    
    # Setup logging FIRST so all subsequent logs appear
    logger = _setup_logging(log_level)

    # Extract config values (CLI args override config file)
    interface = args.interface or config.get("capture", {}).get("interface", "any")
    packet_limit = args.packets if args.packets is not None else config.get("capture", {}).get("packet_count", 0)
    db_path = config.get("storage", {}).get("db_path", "~/.cyb/cyb.db")

    # Setup
    _print_welcome()
    _print_config(interface, packet_limit, db_path, log_level)
    _print_instructions()

    # Expand db_path and ensure permissions
    db_path_expanded = str(Path(db_path).expanduser())
    _setup_database_permissions(db_path_expanded)

    # Initialize service with config
    try:
        logger.info("Initializing network monitor service...")
        service = NetworkMonitorService(config)
    except Exception as e:
        logger.error(f"Failed to initialize service: {e}")
        sys.exit(1)

    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Start packet capture
    try:
        logger.info(f"🔴 Starting real packet capture on interface '{interface}'...")
        logger.info(f"Press Ctrl+C to stop")
        logger.info("")
        service.run(limit=packet_limit if packet_limit > 0 else 0)
        logger.info("")
        logger.info("✓ Capture complete.")
    except PermissionError:
        logger.error("Permission denied. tcpdump requires sudo/root privileges.")
        logger.error("Try: sudo python -m cyb.service.daemon")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
