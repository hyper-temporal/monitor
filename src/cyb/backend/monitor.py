"""
Real-time network monitor.

Orchestrates packet capture, process enrichment, rule evaluation,
and live display of connections.

Follows Single Responsibility: only coordinates other components.
"""

from typing import Optional, List, Dict, Any
import logging

from cyb.infrastructure import Config, PacketCapture, ProcessEnricher, ConnectionStorage

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
                # Process packet
                connection = self._process_packet(packet)
                if not connection:
                    continue
                
                # Default action
                connection["action"] = "allow"
                
                # Store
                self.storage.insert(connection)
                
                # Display
                self._display_connection(connection, filter_expr)
                
        except KeyboardInterrupt:
            logger.info("Monitor stopped by user")
        except Exception as e:
            logger.error(f"Monitor error: {e}", exc_info=True)
            raise
    
    def _process_packet(self, packet: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Enrich packet with process information."""
        # Extract network info
        connection = {
            "src_ip": packet.get("src_ip"),
            "dst_ip": packet.get("dst_ip"),
            "dst_port": packet.get("dst_port"),
            "protocol": packet.get("protocol"),
            "timestamp": packet.get("timestamp"),
        }
        
        # Enrich with process info
        if packet.get("pid"):
            proc_info = self.enricher.get_process_info(packet["pid"])
            connection.update(proc_info)
        
        return connection if connection.get("dst_ip") else None
    
    def _display_connection(self, conn: Dict[str, Any], 
                          filter_expr: Optional[str] = None) -> None:
        """Display connection to user."""
        if filter_expr:
            exe = conn.get("exe", "")
            ip = conn.get("dst_ip", "")
            if filter_expr not in exe and filter_expr not in ip:
                return
        
        action_symbol = "→" if conn.get("action") == "allow" else "✗"
        exe = conn.get("exe", "unknown").split("/")[-1]
        print(f"{action_symbol} {exe:15} {conn.get('dst_ip'):15} "
              f"{conn.get('dst_port'):5} {conn.get('protocol')}")
