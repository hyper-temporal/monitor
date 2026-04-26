"""
Network monitoring service: coordinates packet capture, enrichment, and storage.

Service layer: orchestrates infrastructure components to implement the
"capture packets, enrich with process info, store connections" workflow.

Responsibility: Orchestrate the flow from raw packets → enriched connections → storage.
Pure coordination logic - no display, no CLI, no infrastructure initialization.

Single Responsibility Principle: Only orchestrates the capture-enrich-store pipeline.
Dependency Inversion: Depends on Config/PacketCapture/ProcessEnricher/ConnectionStorage abstractions.
"""

from typing import Optional
import logging

from cyb.infrastructure import Config, PacketCapture, ProcessEnricher, ConnectionStorage
from cyb.domain import Connection, Packet

logger = logging.getLogger(__name__)


class NetworkMonitorService:
    """
    Service for real-time network monitoring.

    Coordinates:
    - Packet capture from network interface
    - Process metadata enrichment
    - Connection storage/persistence

    Responsibilities:
    - Initialize capture, enrichment, and storage components
    - Run monitoring loop: packet → enrich → store
    - Handle errors and logging

    Does NOT handle:
    - Display/UI presentation
    - CLI argument parsing
    - Daemon lifecycle
    """

    def __init__(self, config=None, config_path=None):
        """Initialize service with configuration.

        Args:
            config: Config object with all settings loaded (preferred)
            config_path: Path to config file (alternative)
        """
        # Accept either Config object or path string for flexibility
        if config is None:
            if config_path:
                self.config = Config(config_path=config_path)
            else:
                self.config = Config()
        else:
            self.config = config

        self.capture = PacketCapture(self.config)
        self.enricher = ProcessEnricher(self.config)
        self.storage = ConnectionStorage(self.config)

    def run(self, limit: int = 100, filter_expr: Optional[str] = None) -> None:
        """Start monitoring loop.

        Args:
            limit: Maximum number of packets to capture (0 = unlimited)
            filter_expr: Optional filter expression (for CLI display)
        """
        logger.info("Starting network monitoring service")

        packet_count = 0

        try:
            for packet in self.capture.stream():
                # Validate packet structure
                if not packet.is_valid():
                    logger.debug(f"Skipping invalid packet: {packet}")
                    continue

                logger.debug(f"Raw packet: {packet.src_ip}:{packet.src_port} → {packet.dst_ip}:{packet.dst_port} ({packet.protocol})")

                # Enrich packet with process info → Connection
                connection = self._enrich_packet(packet)
                if not connection:
                    continue

                # Log enriched connection
                logger.debug(f"Enriched: {connection.exe} ({connection.user}) → {connection.dst_ip}:{connection.dst_port}")

                # Store connection
                self.storage.insert(connection)

                packet_count += 1

                # Display to CLI if not a daemon
                if filter_expr:
                    self._display_connection(connection, filter_expr)

                # Stop if limit reached
                if limit > 0 and packet_count >= limit:
                    logger.info(f"Packet limit ({limit}) reached")
                    break

        except KeyboardInterrupt:
            logger.info("Service stopped by user")
        except PermissionError:
            logger.error("Permission denied - tcpdump requires root/sudo")
            raise
        except Exception as e:
            logger.error(f"Service error: {e}", exc_info=True)
            raise

        logger.info(f"Captured {packet_count} packets")

    def _enrich_packet(self, packet: Packet) -> Optional[Connection]:
        """
        Enrich typed Packet with process information.

        Args:
            packet: Raw packet from tcpdump

        Returns:
            Connection object with network and process metadata, or None if enrichment fails
        """
        try:
            # Enrich with process info (type-safe ProcessInfo)
            proc_info = self.enricher.get_process_info(packet.pid) if packet.pid else None

            # Build Connection object (type-safe, validated)
            return Connection(
                timestamp=packet.timestamp,
                src_ip=packet.src_ip,
                dst_ip=packet.dst_ip,
                dst_port=packet.dst_port,
                protocol=packet.protocol,
                pid=packet.pid,
                exe=proc_info.exe if proc_info else "unknown",
                user=proc_info.user if proc_info else "unknown",
                status="pending"
            )
        except Exception as e:
            logger.warning(f"Failed to enrich packet {packet}: {e}")
            return None

    def _display_connection(self, conn: Connection, 
                          filter_expr: Optional[str] = None) -> None:
        """Display connection to CLI."""
        if filter_expr:
            exe = conn.exe or ""
            ip = conn.dst_ip or ""
            if filter_expr not in exe and filter_expr not in ip:
                return

        action_symbol = "→"  # No blocking rules yet
        exe = conn.exe.split("/")[-1] if conn.exe else "unknown"
        print(f"{action_symbol} {exe:15} {conn.dst_ip:15} "
              f"{conn.dst_port:5} {conn.protocol}")
