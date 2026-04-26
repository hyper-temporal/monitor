"""
Domain model: Network packet.

Represents a raw network packet captured from the network interface.
Core domain entity - no infrastructure dependencies.
"""

from typing import NamedTuple, Optional


class Packet(NamedTuple):
    """
    A raw network packet from tcpdump/libpcap.

    Domain entity: represents the raw facts observed on the network,
    before enrichment with process information.
    """
    timestamp: str
    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    protocol: str
    pid: Optional[int] = None

    def is_valid(self) -> bool:
        """Check required fields are present."""
        return all([
            self.timestamp, self.src_ip, self.dst_ip,
            self.dst_port, self.protocol
        ])
