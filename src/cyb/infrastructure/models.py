"""
Data models: Shared data structures (not domain entities).

These are DTOs (data transfer objects) - no business logic, just data shapes.
Used across layers for passing data around.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Connection:
    """
    A network connection event.
    
    Data structure: represents a single observed connection.
    No business logic, just a container for connection data.
    """
    timestamp: str
    src_ip: str
    dst_ip: str
    dst_port: int
    protocol: str
    pid: Optional[int] = None
    exe: Optional[str] = None
    user: Optional[str] = None
    status: str = "pending"  # pending, allowed, blocked

    def to_dict(self) -> dict:
        """Convert to dictionary (for serialization)."""
        return {
            "timestamp": self.timestamp,
            "src_ip": self.src_ip,
            "dst_ip": self.dst_ip,
            "dst_port": self.dst_port,
            "protocol": self.protocol,
            "pid": self.pid,
            "exe": self.exe,
            "user": self.user,
            "status": self.status,
        }
