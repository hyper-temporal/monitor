"""
Frontend application: Runs as normal user (no privileges required).
Responsibility: Display real-time connections from database, search/filter.
Reads from shared SQLite database populated by the backend daemon.
"""

import sys
import argparse
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Check if PyQt5 is available
try:
    from PyQt5.QtWidgets import QApplication
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from locmon.backend import BackendAPI
from locmon.ui.main import CyberObservabilityApp


def main():
    """Frontend application: Display network connections from database."""
    parser = argparse.ArgumentParser(
        description="Cyber Observability — Real-time Network Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m cyb.ui.frontend_app -d /path/to/cyb.db
  python -m cyb.ui.frontend_app --database ./cyb.db
        """,
    )
    parser.add_argument(
        "-d", "--database",
        type=str,
        required=False,
        help="Path to SQLite database (default: cyb.db in current directory)",
    )

    args = parser.parse_args()

    if not PYQT_AVAILABLE:
        logger.error("PyQt5 not installed")
        logger.error("Install with: pip install PyQt5")
        sys.exit(1)

    # Resolve database path
    db_path = args.database if args.database else "cyb.db"

    # Convert to absolute path if relative
    if not Path(db_path).is_absolute():
        db_path = str(Path.cwd() / db_path)

    logger.info(f"Using database: {db_path}")

    # Initialize backend (reads from shared database)
    try:
        backend = BackendAPI(db_path=db_path, read_only=True)
        logger.info("Backend initialized")
    except FileNotFoundError as e:
        logger.error(f"Database not found: {db_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to initialize backend: {e}")
        sys.exit(1)

    # Create and show PyQt5 GUI
    logger.info("🎨 Launching frontend GUI (runs as normal user)...")

    app = QApplication(sys.argv)
    window = CyberObservabilityApp(backend)
    window.show()

    logger.info("GUI started. Waiting for connections...")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
