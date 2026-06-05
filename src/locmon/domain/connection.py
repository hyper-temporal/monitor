"""
Domain model: Network connection.

Represents an enriched network connection with process information.
Core domain entity - no infrastructure dependencies.

Status lifecycle: pending → allowed | blocked
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Connection:
    """
    A network connection event.

    Domain entity: represents a single observed network connection
    with process enrichment and metadata.

    Status lifecycle: pending → allowed | blocked
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
    size: int = 0

    def to_dict(self, include_none: bool = False) -> dict:
        """
        Convert to dictionary for serialization.

        Args:
            include_none: Include None values in output
        """
        data = {
            "timestamp": self.timestamp,
            "src_ip": self.src_ip,
            "dst_ip": self.dst_ip,
            "dst_port": self.dst_port,
            "protocol": self.protocol,
            "pid": self.pid,
            "exe": self.exe,
            "user": self.user,
            "status": self.status,
            "size": self.size,
        }

        if not include_none:
            data = {k: v for k, v in data.items() if v is not None}

        return data
