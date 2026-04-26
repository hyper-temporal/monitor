"""
Domain model: Network connection.

Represents a network connection event with full enrichment.
Core domain entity - no infrastructure dependencies.
"""

from dataclasses import dataclass, asdict
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

    def to_dict(self, include_none: bool = False) -> dict:
        """
        Convert to dictionary for serialization.

        Args:
            include_none: If False (default), exclude None values to reduce payload

        Uses dataclasses.asdict() for efficient conversion.
        """
        data = asdict(self)

        # Remove None values to reduce JSON payload size
        if not include_none:
            data = {k: v for k, v in data.items() if v is not None}

        return data
