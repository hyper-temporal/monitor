"""
Frontend application: Runs as normal user (no privileges required).
Responsibility: Display real-time connections from database, create rules, search/filter.
Reads from shared SQLite database populated by the backend daemon.
"""

import sys

# Handle both direct execution and module execution
try:
    from backend.api import BackendAPI
    from backend.logger import get_logger
    from frontend.main import CyberObservabilityApp
except ImportError:
    # Direct execution: add parent directory to path
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from backend.api import BackendAPI
    from backend.logger import get_logger
    from frontend.main import CyberObservabilityApp

logger = get_logger(__name__)

# Try to import PyQt5
try:
    from PyQt5.QtWidgets import QApplication
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


def main():
    """Frontend application: Display network connections from database."""
    if not PYQT_AVAILABLE:
        logger.error("PyQt5 not installed")
        logger.error("Install with: pip install PyQt5")
        sys.exit(1)

    # Initialize backend (reads from shared database)
    backend = BackendAPI()
    logger.info("Frontend initialized - connecting to shared database")
    logger.info("")

    # Create and show PyQt5 GUI
    logger.info("🎨 Launching frontend GUI (runs as normal user)...")
    logger.info("")

    app = QApplication(sys.argv)
    window = CyberObservabilityApp(backend)
    window.show()

    logger.info("GUI started. Waiting for connections from backend daemon...")
    logger.info("")
    logger.info("To capture packets:")
    logger.info("  1. Open another terminal")
    logger.info("  2. Run: sudo python backend_daemon.py --interface en0")
    logger.info("  3. Watch connections appear here in real-time")
    logger.info("")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
