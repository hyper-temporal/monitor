"""
Domain model: Raw network packet.

Represents a single packet captured from the network interface.
Strongly-typed equivalent of tcpdump/libpcap output.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Packet:
    """
    A raw network packet from tcpdump/libpcap.
    
    Domain concept: represents the raw facts observed on the network,
    before enrichment with process information.
    """
    timestamp: str
    src_ip: str
    dst_ip: str
    dst_port: int
    protocol: str
    src_port: Optional[int] = None
    pid: Optional[int] = None

    def is_valid(self) -> bool:
        """Check if packet has required fields."""
        return bool(self.dst_ip and self.dst_port and self.protocol)
