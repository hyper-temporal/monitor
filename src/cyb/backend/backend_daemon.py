"""
Backend daemon: Runs with elevated privileges (sudo) to capture network packets.
Responsibility: Capture packets via tcpdump, enrich with process info, store in SQLite.
This process runs continuously and doesn't require any frontend.
"""

import sys
import argparse
import signal

from cyb.backend.api import BackendAPI
from cyb.infrastructure import get_logger, Config, PacketCapture

logger = get_logger(__name__)

# Global reference for signal handler
backend = None


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    logger.info("")
    logger.info("Capture interrupted by user.")
    sys.exit(0)


def capture_packets(backend: BackendAPI):
    """
    Capture real network packets continuously and store in database.
    Uses configuration from .env:
    - CAPTURE_INTERFACE: which interface to capture from (default: "any")
    - CAPTURE_PACKET_COUNT: max packets to capture (default: 0 = unlimited)
    """
    config = Config()
    interface = config.get("capture", {}).get("interface", "any")

    logger.info(f"🔴 Starting real packet capture on interface '{interface}'...")
    logger.info(f"Press Ctrl+C to stop")
    logger.info("")

    try:
        # Parser works with plain tcpdump output (no field_map needed)
        parser = PacketCapture()

        packet_limit = config.get("capture", {}).get("packet_count", 0)
        count = 0

        logger.info(f"Listening on {interface}... (waiting for packets)")
        logger.info("")

        for conn in parser.capture_live(
            interface=interface,
            packet_count=packet_limit
        ):
            backend.ingest_connection(conn)
            count += 1

            # Log the captured connection
            status = conn.status or "pending"
            logger.info(f"[{count}] [{status.upper()}] {conn.src_ip} → {conn.dst_ip}:{conn.dst_port} ({conn.protocol})")
            if conn.exe:
                logger.info(f"      ↳ {conn.exe} (user: {conn.user})")

        logger.info("")
        logger.info(f"✓ Capture complete. {count} packets ingested.")

    except KeyboardInterrupt:
        logger.info("")
        logger.info("Capture interrupted by user.")
    except PermissionError:
        logger.error("Permission denied. tcpdump requires sudo/root privileges.")
        logger.error("Try: sudo python backend_daemon.py")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Capture error: {e}")
        sys.exit(1)


def main():
    """Backend daemon: Capture packets and store in database."""
    global backend

    parser = argparse.ArgumentParser(
        description="Cyber Observability Backend Daemon - Packet Capture Service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Capture from default interface (requires sudo)
  sudo python backend_daemon.py

  # Capture from specific interface
  sudo python backend_daemon.py --interface en0

  # Capture with custom packet limit
  sudo python backend_daemon.py --interface en0 --packets 100

  # Debug mode (verbose logging)
  LOG_LEVEL=DEBUG sudo python backend_daemon.py
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

    args = parser.parse_args()

    # Normal operation: start capture
    config = Config()

    logger.info("╔════════════════════════════════════════════════════╗")
    logger.info("║    Cyber Observability Backend Daemon — Capture   ║")
    logger.info("╚════════════════════════════════════════════════════╝")
    logger.info("")
    logger.info("Configuration (from .env and CLI args):")

    # Override config from CLI args if provided
    interface = args.interface or config.get("capture", {}).get("interface", "any")
    packet_limit = args.packets if args.packets is not None else config.get("capture", {}).get("packet_count", 0)
    db_path = config.get("storage", {}).get("db_path", "~/.cyb/cyb.db")
    log_level = config.get("logging", {}).get("level", "INFO")

    logger.info(f"  • Capture Interface: {interface}")
    logger.info(f"  • Packet Limit: {packet_limit if packet_limit > 0 else 'unlimited'}")
    logger.info(f"  • Database: {db_path}")
    logger.info(f"  • Log Level: {log_level}")
    logger.info("")
    logger.info("What to do:")
    logger.info("  1. Open another terminal and run: python frontend_app.py")
    logger.info("  2. In the frontend window, watch connections appear in real-time")
    logger.info("  3. Generate network traffic (ping, curl, browse, etc.)")
    logger.info("  4. Press Ctrl+C here to stop capture (frontend keeps running)")
    logger.info("")
    logger.info("ℹ️  The database is shared between backend and frontend via SQLite")
    logger.info("")

    # Initialize backend with config
    backend = BackendAPI()
    logger.info("Backend initialized with SQLite storage (shared with frontend)")
    logger.info("")

    # Ensure database file is writable by everyone (both root and normal user)
    try:
        import os
        if os.path.exists(db_path):
            os.chmod(db_path, 0o666)
            logger.info(f"✓ Database permissions set: {db_path}")
    except Exception as e:
        logger.warning(f"Could not set database permissions: {e}")

    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Start packet capture
    try:
        capture_packets(backend)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
