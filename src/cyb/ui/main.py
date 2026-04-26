"""
PyQt5 frontend for cyber observability.
Responsibility: Display real-time connections, search/filter, rule creation.
"""

import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Check if PyQt5 is available
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit,
        QComboBox, QHeaderView, QTabWidget, QMessageBox
    )
    from PyQt5.QtCore import Qt, QTimer, QSortFilterProxyModel
    from PyQt5.QtGui import QColor, QFont
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from cyb.backend import BackendAPI
from cyb.domain import Connection
from cyb.domain import identify_ip, identify_port, is_common_traffic
from cyb.core.analytics import ConnectionAnalytics


class ConnectionTable(QTableWidget):
    """Table widget displaying connections with search/filter and sorting."""

    def __init__(self):
        super().__init__()
        self.connections = []  # Keep all connections in memory
        self.sort_column = 0  # Default sort by time
        self.sort_ascending = False  # Newest first
        self.setup_table()

    def setup_table(self):
        """Initialize table structure with sortable headers."""
        self.setColumnCount(9)
        self.setHorizontalHeaderLabels([
            "Time", "Src IP", "Dst IP", "Service", "Port", "Protocol", "Process", "User", "Status"
        ])
        self.setRowCount(0)

        # Make columns resizable
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.sectionClicked.connect(self.on_column_clicked)  # Enable sorting on header click

        # Alternate row colors
        self.setAlternatingRowColors(True)

    def add_connection(self, conn: dict):
        """Add a connection and maintain in-memory list."""
        self.connections.insert(0, conn)  # Newest first

        # Keep only last 1000 connections in memory
        if len(self.connections) > 1000:
            self.connections = self.connections[:1000]

        self.refresh_table()

    def on_column_clicked(self, col: int):
        """Handle column header click for sorting."""
        if self.sort_column == col:
            # Toggle sort direction if same column clicked
            self.sort_ascending = not self.sort_ascending
        else:
            # New column, sort ascending
            self.sort_column = col
            self.sort_ascending = True

        self.refresh_table()

    def _get_sort_key(self, conn: dict, col: int):
        """Extract sort key from connection based on column."""
        col_map = {
            0: lambda c: c["timestamp"],          # Time
            1: lambda c: c["src_ip"],             # Src IP
            2: lambda c: c["dst_ip"],             # Dst IP
            3: lambda c: identify_ip(c["dst_ip"]), # Service
            4: lambda c: c["dst_port"],           # Port (numeric)
            5: lambda c: c["protocol"],           # Protocol
            6: lambda c: c["exe"] or "",          # Process
            7: lambda c: c["user"] or "",         # User
            8: lambda c: c["status"],             # Status
        }
        return col_map.get(col, lambda c: c["timestamp"])(conn)

    def is_suspicious(self, conn: dict) -> tuple:
        """
        Detect suspicious activity.
        Returns: (is_suspicious, reason_short, service_name)
        """
        service = identify_ip(conn["dst_ip"])
        port_info = identify_port(conn["dst_port"])

        # Check if this is normal traffic
        if is_common_traffic(conn["dst_ip"], conn["dst_port"]):
            # Known service on known port = normal
            return (False, "", service)

        # High/unusual ports (not common services)
        common_ports = {80, 443, 53, 22, 25, 465, 587, 993, 143, 123, 53, 5353}
        if conn["dst_port"] not in common_ports and conn["dst_port"] > 1024:
            # High port not in common list
            return (True, "high-port", service)

        # Count how many times we've seen this destination
        dest_count = sum(1 for c in self.connections if c["dst_ip"] == conn["dst_ip"])
        if dest_count == 1 and service == "Unknown":
            # New, never-seen-before destination AND unknown service
            return (True, "new-dest", service)

        return (False, "", service)

    def refresh_table(self):
        """Refresh table display from connections list (with sorting)."""
        self.setRowCount(0)

        # Sort connections
        sorted_conns = sorted(
            self.connections,
            key=lambda c: self._get_sort_key(c, self.sort_column),
            reverse=not self.sort_ascending
        )

        for conn in sorted_conns[:100]:  # Show only latest 100
            row = self.rowCount()
            self.insertRow(row)

            # Get service identification and suspicious status
            is_sus, sus_reason, service = self.is_suspicious(conn)
            port_info = identify_port(conn["dst_port"])

            items = [
                conn["timestamp"].split("T")[1][:8],  # HH:MM:SS
                conn["src_ip"],
                conn["dst_ip"],
                service,  # Service name (Google, Anthropic, Unknown, etc.)
                str(conn["dst_port"]),
                conn["protocol"],
                conn["exe"] or "—",
                conn["user"] or "—",
                conn["status"],
            ]

            for col, text in enumerate(items):
                item = QTableWidgetItem(text)

                # Build tooltip
                tooltip_parts = []
                if col == 3:  # Service column
                    tooltip_parts.append(f"📍 {service}")
                    tooltip_parts.append(f"🔌 {port_info}")
                    if is_sus:
                        reasons = {
                            "high-port": "Unusual port (not common service)",
                            "new-dest": "First connection to this destination"
                        }
                        tooltip_parts.append(f"⚠️ Suspicious: {reasons.get(sus_reason, sus_reason)}")

                if tooltip_parts:
                    item.setToolTip(" | ".join(tooltip_parts))

                # Highlight suspicious activity with orange background (only on Service column)
                if is_sus and col == 3:
                    item.setBackground(QColor(255, 165, 0))

                # Status color takes precedence
                if conn["status"] == "blocked":
                    item.setBackground(QColor(255, 100, 100))  # Dark red
                elif conn["status"] == "allowed":
                    item.setBackground(QColor(100, 255, 100))  # Dark green

                self.setItem(row, col, item)

    def filter_connections(self, search_text: str):
        """Filter connections by search text (IP, port, protocol, etc)."""
        if not search_text:
            self.refresh_table()
            return

        search_lower = search_text.lower()
        filtered = [
            conn for conn in self.connections
            if search_lower in conn["src_ip"].lower()
            or search_lower in conn["dst_ip"].lower()
            or search_lower in str(conn["dst_port"])
            or search_lower in conn["protocol"].lower()
            or (conn["exe"] and search_lower in conn["exe"].lower())
        ]

        self.setRowCount(0)
        for conn in filtered[:100]:  # Show max 100 results
            row = self.rowCount()
            self.insertRow(row)

            # Get IP intelligence
            is_sus, sus_reason, service = self.is_suspicious(conn)
            port_info = identify_port(conn["dst_port"])

            items = [
                conn["timestamp"].split("T")[1][:8],
                conn["src_ip"],
                conn["dst_ip"],
                service,  # Service name
                str(conn["dst_port"]),
                conn["protocol"],
                conn["exe"] or "—",
                conn["user"] or "—",
                conn["status"],
            ]

            for col, text in enumerate(items):
                item = QTableWidgetItem(text)

                # Highlight matching text
                if search_lower in text.lower():
                    item.setBackground(QColor(255, 255, 100))  # Yellow highlight

                # Show tooltip on Service column
                if col == 3:  # Service column
                    tooltip_parts = [f"📍 {service}", f"🔌 {port_info}"]
                    if is_sus:
                        reasons = {
                            "high-port": "Unusual port (not common service)",
                            "new-dest": "First connection to this destination"
                        }
                        tooltip_parts.append(f"⚠️ Suspicious: {reasons.get(sus_reason, sus_reason)}")
                    item.setToolTip(" | ".join(tooltip_parts))

                if conn["status"] == "blocked":
                    item.setBackground(QColor(255, 200, 200))
                elif conn["status"] == "allowed":
                    item.setBackground(QColor(200, 255, 200))

                self.setItem(row, col, item)


class AnalyticsTable(QTableWidget):
    """Table showing aggregated analytics (grouped by IP)."""

    def __init__(self):
        super().__init__()
        self.analytics_data = {}
        self.sort_column = 1  # Default sort by Count
        self.sort_ascending = False  # Descending (most active first)
        self.setup_table()

    def setup_table(self):
        """Initialize table structure."""
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels([
            "Destination IP", "Source IPs", "Processes", "Ports", "Activity", "Last Seen"
        ])
        self.setRowCount(0)

        # Make columns resizable
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.sectionClicked.connect(self.on_column_clicked)  # Enable sorting on header click

        # Alternate row colors
        self.setAlternatingRowColors(True)

        # Enable item selection and clipboard copy
        self.setSelectionMode(self.SelectionMode.SingleSelection)
        self.setSelectionBehavior(self.SelectionBehavior.SelectItems)
        self.itemClicked.connect(self.on_item_clicked)

        # Enable row selection via vertical header click
        self.verticalHeader().sectionClicked.connect(self.on_row_clicked)

    def on_item_clicked(self, item):
        """Handle cell click—copy cell content to clipboard."""
        from PyQt5.QtWidgets import QApplication
        text = item.text()
        if text:
            try:
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
                logger.info(f"✓ Copied: {text}")
            except Exception as e:
                logger.error(f"Copy failed: {e}")

    def on_row_clicked(self, row: int):
        """Handle row number click—copy entire row to clipboard."""
        from PyQt5.QtWidgets import QApplication
        # Collect all cells in the row
        row_data = []
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                row_data.append(item.text())

        text = " | ".join(row_data)
        if text:
            try:
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
                logger.info(f"✓ Copied row: {text[:60]}...")
            except Exception as e:
                logger.error(f"Copy failed: {e}")

    def on_column_clicked(self, col: int):
        """Handle column header click for sorting."""
        if self.sort_column == col:
            # Toggle sort direction if same column clicked
            self.sort_ascending = not self.sort_ascending
        else:
            # New column, sort descending (most active first)
            self.sort_column = col
            self.sort_ascending = False

        # Re-render with new sort order
        if self.analytics_data:
            self.update_analytics_with_sort()

    def _get_sort_key(self, ip: str, data: dict, col: int):
        """Extract sort key from analytics data based on column."""
        col_map = {
            0: lambda: ip,                          # Destination IP
            1: lambda: len(data.get("src_ips", [])),# Source IPs count
            2: lambda: len(data["processes"]),      # Processes count
            3: lambda: len(data["ports"]),          # Ports count
            4: lambda: data["count"],               # Activity (by count)
            5: lambda: data["last_seen"],           # Last Seen (timestamp)
        }
        return col_map.get(col, lambda: ip)()

    def update_analytics_with_sort(self):
        """Re-render analytics with current sort order."""
        # Sort by current column
        sorted_ips = sorted(
            self.analytics_data.items(),
            key=lambda x: self._get_sort_key(x[0], x[1], self.sort_column),
            reverse=not self.sort_ascending
        )

        self.setRowCount(0)
        # Display all IPs (no limit) - user can scroll to see all
        for ip, data in sorted_ips:
            self._add_row(ip, data)

    def update_analytics(self, connections: list):
        """Update analytics from connections list."""
        if not connections:
            self.setRowCount(0)
            return

        # Group by IP
        grouped = ConnectionAnalytics.group_by_ip(connections)
        self.analytics_data = grouped

        # Re-render with current sort order
        self.update_analytics_with_sort()

    def _add_row(self, ip: str, data: dict):
        """Add a single row to the analytics table."""
        row = self.rowCount()
        self.insertRow(row)

        # Build display strings
        service = identify_ip(ip)
        processes = ", ".join(data["processes"][:3])  # Show first 3
        if len(data["processes"]) > 3:
            processes += f" +{len(data['processes']) - 3}"
        processes = processes or "—"

        ports = ", ".join(str(p) for p in data["ports"][:3])
        if len(data["ports"]) > 3:
            ports += f" +{len(data['ports']) - 3}"
        ports = ports or "—"

        # Determine activity level
        count = data["count"]
        if count > 50:
            activity = f"🔥 {count}"
        elif count > 20:
            activity = f"⚡ {count}"
        elif count > 5:
            activity = f"📊 {count}"
        else:
            activity = f"📌 {count}"

        # Extract time from last_seen timestamp (HH:MM:SS)
        last_seen_time = data["last_seen"].split("T")[1][:8] if data["last_seen"] else "—"

        # Format source IPs
        src_ips = ", ".join(data.get("src_ips", [])[:3])  # Show first 3
        if len(data.get("src_ips", [])) > 3:
            src_ips += f" +{len(data['src_ips']) - 3}"
        src_ips = src_ips or "—"
        
        items = [
            f"{ip} ({service})",
            src_ips,
            processes,
            ports,
            activity,
            last_seen_time,
        ]

        for col, text in enumerate(items):
            item = QTableWidgetItem(text)

            # Highlight unusual services
            if "Unknown" in text and col == 0:
                item.setBackground(QColor(255, 165, 0))  # Orange for unknown

            # Highlight high activity
            if col == 3 and count > 50:
                item.setBackground(QColor(255, 200, 100))

            # Add tooltip with full details
            src_ips_str = ', '.join(data.get('src_ips', []) or []) or 'None'
            tooltip = f"""
Destination IP: {ip}
Source IPs: {src_ips_str}
Service: {service}
Connections: {count}
Processes: {', '.join(data['processes']) or 'None'}
Ports: {', '.join(str(p) for p in data['ports']) or 'None'}
Protocols: {', '.join(data['protocols'])}
First seen: {data['first_seen'][:19] if data['first_seen'] else 'N/A'}
Last seen: {data['last_seen'][:19] if data['last_seen'] else 'N/A'}
Status: Blocked={data['status_counts']['blocked']} Allowed={data['status_counts']['allowed']} Pending={data['status_counts']['pending']}
            """.strip()
            item.setToolTip(tooltip)

            self.setItem(row, col, item)


class CyberObservabilityApp(QMainWindow):
    """Main application window."""

    def __init__(self, backend: BackendAPI):
        super().__init__()
        self.backend = backend
        self.setWindowTitle("Cyber Observability — Live Monitor")
        self.setGeometry(100, 100, 1400, 700)

        logger.info("Initializing UI...")

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout
        layout = QVBoxLayout()
        central.setLayout(layout)

        # Title
        title = QLabel("🔍 Network Connections (Real-time)")
        layout.addWidget(title)

        # Live status bar (shows last packet)
        self.live_status = QLabel("⏳ Waiting for connections...")
        self.live_status.setStyleSheet("background-color: #f0f0f0; padding: 8px; font-family: monospace; font-weight: bold;")
        layout.addWidget(self.live_status)

        # Search/Filter row
        search_layout = QHBoxLayout()
        layout.addLayout(search_layout)

        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("IP, port, protocol, process name...")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)

        # Tabs: Raw connections (limited) vs Analytics (all data, grouped by IP)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Connection details (latest 1000 packets only)
        self.table = ConnectionTable()
        self.tabs.addTab(self.table, "📋 Connections (Latest 1000)")

        # Tab 2: Analytics (all packets, grouped by IP)
        self.analytics_table = AnalyticsTable()
        self.tabs.addTab(self.analytics_table, "📊 Analytics (All Data)")

        # Suspicious activity summary
        self.suspicious_label = QLabel("⚠️ Suspicious: 0 | 🆕 New Destinations: 0 | 🔴 High Ports: 0")
        self.suspicious_label.setStyleSheet("color: #ff8800; font-weight: bold;")
        layout.addWidget(self.suspicious_label)

        # Export/Data row
        export_layout = QHBoxLayout()
        layout.addLayout(export_layout)

        export_layout.addStretch()
        export_json_btn = QPushButton("💾 Export JSON")
        export_json_btn.clicked.connect(self.on_export_json)
        export_layout.addWidget(export_json_btn)

        export_csv_btn = QPushButton("📊 Export CSV")
        export_csv_btn.clicked.connect(self.on_export_csv)
        export_layout.addWidget(export_csv_btn)

        clear_btn = QPushButton("🗑️ Delete Database")
        clear_btn.clicked.connect(self.on_clear_connections)
        export_layout.addWidget(clear_btn)

        # Stats label
        self.stats_label = QLabel("Connections: 0 | Rules: 0")
        layout.addWidget(self.stats_label)

        # Track last known connection count for polling
        self.last_connection_count = 0

        # Register event handler with backend
        self.backend.set_event_handler("connection_ingested", self.on_connection_ingested)

        # Timer to refresh stats and poll for new connections (for separate process mode)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats_and_connections)
        self.timer.start(500)  # Update every 500ms to catch new connections

        logger.info("UI initialized")

    def on_connection_ingested(self, data: dict):
        """Handle new connection from backend."""
        conn = data["connection"]
        self.table.add_connection(conn)
        logger.debug(f"Added connection: {conn['src_ip']} → {conn['dst_ip']}:{conn['dst_port']}")

    def on_search(self, text: str):
        """Handle search/filter input."""
        self.table.filter_connections(text)

        rule_id = self.backend.add_rule(
            action=action,
            dst_ip=dst_ip,
            dst_port=dst_port,
            exe=None,
            created=datetime.now().isoformat(),
        )
        logger.info(f"Rule created: {action} {dst_ip}:{dst_port} (id={rule_id})")

        # Clear inputs
        self.ip_input.clear()
        self.port_input.clear()

    def update_stats_and_connections(self):
        """Update statistics and poll for new connections (for separate process mode)."""
        # Raw connections table: show latest 1000 packets only (for display performance)
        raw_conns = self.backend.get_recent_connections(limit=1000)

        # Analytics table: query all data from backend for aggregation
        all_conns = self.backend.get_all_connections()

        rules = self.backend.get_rules()

        # Count unique IPs in analytics
        unique_ips = len(self.analytics_table.analytics_data) if self.analytics_table.analytics_data else 0

        self.stats_label.setText(
            f"Connections: {len(all_conns)} (Total) | {len(raw_conns)} (Displayed) | "
            f"Unique IPs: {unique_ips} | Rules: {len(rules)}"
        )

        # Update live status (most recent packet)
        if raw_conns:
            latest = raw_conns[0]  # Most recent connection
            service = identify_ip(latest["dst_ip"])
            time = latest["timestamp"].split("T")[1][:8]  # HH:MM:SS
            process = latest["exe"] or "System"
            status_color = "🟩" if latest["status"] == "allowed" else ("🔴" if latest["status"] == "blocked" else "⚫")

            self.live_status.setText(
                f"{status_color} [{time}] {process} → {latest['dst_ip']} ({service}):{latest['dst_port']} "
                f"({latest['protocol']})"
            )
        else:
            self.live_status.setText("⏳ Waiting for connections...")

        # Calculate suspicious activity metrics (from raw table only for display)
        suspicious_count = 0
        new_dest_count = 0
        high_port_count = 0
        unknown_ips = 0

        if self.table.connections:
            for conn in self.table.connections:
                is_sus, reason, service = self.table.is_suspicious(conn)
                if is_sus:
                    suspicious_count += 1
                    if reason == "new-dest":
                        new_dest_count += 1
                    elif reason == "high-port":
                        high_port_count += 1
                if service == "Unknown":
                    unknown_ips += 1

        self.suspicious_label.setText(
            f"⚠️ Suspicious: {suspicious_count} | "
            f"🆕 New Dests: {new_dest_count} | "
            f"🔴 High Ports: {high_port_count} | "
            f"❓ Unknown IPs: {unknown_ips}"
        )

        # Refresh raw connections table (latest 1000 only)
        current_count = len(raw_conns)
        if current_count > self.last_connection_count:
            # New connections arrived, refresh table with latest
            new_connections = raw_conns[:current_count - self.last_connection_count]
            for conn in reversed(new_connections):  # Add in reverse order (newest first)
                self.table.add_connection(conn)
            self.last_connection_count = current_count

        # Refresh analytics with ALL data from backend (for accurate aggregation)
        self.analytics_table.update_analytics(all_conns)

    def on_export_json(self):
        """Export connections and rules to JSON with timestamp."""
        import json

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cyb_export_{timestamp}.json"
        # Save to home directory
        filepath = Path.home() / filename

        try:
            conns = self.backend.get_recent_connections(limit=10000)
            rules = self.backend.get_rules()

            data = {
                "export_date": datetime.now().isoformat(),
                "summary": {
                    "total_connections": len(conns),
                    "total_rules": len(rules),
                },
                "connections": [c for c in conns],
                "rules": rules,
            }

            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"✓ Exported to {filepath}")
            self.stats_label.setText(self.stats_label.text() + f" | 💾 Saved: {filename}")
        except Exception as e:
            logger.error(f"Export failed: {e}")

    def on_export_csv(self):
        """Export connections to CSV with timestamp."""
        import csv

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cyb_connections_{timestamp}.csv"
        filepath = Path.home() / filename

        try:
            conns = self.backend.get_recent_connections(limit=10000)

            if not conns:
                logger.warning("No connections to export")
                return

            # Get first connection to determine columns
            first = conns[0]
            fieldnames = first.keys()

            with open(filepath, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for conn in conns:
                    row = conn
                    writer.writerow(row)

            logger.info(f"✓ Exported to {filepath}")
            self.stats_label.setText(self.stats_label.text() + f" | 📊 Saved: {filename}")
        except Exception as e:
            logger.error(f"Export failed: {e}")

    def on_clear_connections(self):
        """Clear all connections from database."""
        response = self.show_confirmation_dialog(
            "⚠️ Clear Database",
            "This will delete all captured packets.\n\n"
            "Continue?"
        )

        if not response:
            return

        try:
            self.backend.clear_database()
            logger.info("✓ Database cleared and vacuumed")
            
            # Reset UI
            self.table.connections = []
            self.table.refresh_table()
            self.analytics_table.setRowCount(0)
            self.analytics_table.analytics_data = {}
            self.last_connection_count = 0
            self.stats_label.setText("Connections: 0 | Unique IPs: 0 | Rules: 0")

        except Exception as e:
            logger.error(f"Database error: {e}")
        except Exception as e:
            logger.error(f"Clear failed: {e}")


    def show_confirmation_dialog(self, title: str, message: str) -> bool:
        """Show a simple yes/no confirmation dialog."""
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes


def main():
    """Entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Cyber Observability — Real-time Network Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python -m cyb.ui.main -d /path/to/cyb.db
  uv run python -m cyb.ui.main --database ./cyb.db
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
        print("PyQt5 not installed. Install with: pip install PyQt5")
        sys.exit(1)

    # Resolve database path
    db_path = args.database if args.database else "cyb.db"
    
    # Convert to absolute path if relative
    if not Path(db_path).is_absolute():
        db_path = str(Path.cwd() / db_path)

    logger.info(f"Using database: {db_path}")

    # Initialize backend with database path
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
    app = QApplication(sys.argv)
    window = CyberObservabilityApp(backend)
    window.show()

    logger.info("App started. Waiting for connections...")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
