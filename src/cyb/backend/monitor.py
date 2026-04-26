"""
Real-time network monitor.

Orchestrates packet capture, process enrichment, and storage.

Follows Single Responsibility: only coordinates other components.
"""

from typing import Optional
import logging

from cyb.infrastructure import Config, PacketCapture, ProcessEnricher, ConnectionStorage, Connection, Packet

logger = logging.getLogger(__name__)


class Monitor:
    """
    Coordinates real-time network monitoring.
    
    Depends on abstractions (interfaces), not concrete implementations.
    Can be extended for different UIs (CLI, GUI) without changes.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize monitor with config."""
        self.config = Config(config_path=config_path)
        self.capture = PacketCapture(self.config)
        self.enricher = ProcessEnricher(self.config)
        self.storage = ConnectionStorage(self.config)
        
    def run(self, limit: int = 100, filter_expr: Optional[str] = None) -> None:
        """Start monitoring loop."""
        logger.info("Starting network monitor")
        
        try:
            for packet in self.capture.stream():
                # Packet is already typed (PacketCapture yields Packet objects)
                if not packet.is_valid():
                    continue
                
                # Enrich packet with process info → Connection
                connection = self._process_packet(packet)
                if not connection:
                    continue
                
                # Store
                self.storage.insert(connection)
                
                # Display
                self._display_connection(connection, filter_expr)
                
        except KeyboardInterrupt:
            logger.info("Monitor stopped by user")
        except Exception as e:
            logger.error(f"Monitor error: {e}", exc_info=True)
            raise
    
    def _process_packet(self, packet: Packet) -> Optional[Connection]:
        """
        Enrich typed Packet with process information.
        
        Returns Connection object with network and process metadata.
        """
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
    
    def _display_connection(self, conn: Connection, 
                          filter_expr: Optional[str] = None) -> None:
        """Display connection to user."""
        if filter_expr:
            exe = conn.exe or ""
            ip = conn.dst_ip or ""
            if filter_expr not in exe and filter_expr not in ip:
                return
        
        action_symbol = "→"  # No blocking rules yet
        exe = conn.exe.split("/")[-1] if conn.exe else "unknown"
        print(f"{action_symbol} {exe:15} {conn.dst_ip:15} "
              f"{conn.dst_port:5} {conn.protocol}")
