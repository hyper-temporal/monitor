"""
Repository interface for connections.

Defines the contract for accessing connection data.
"""

from typing import List, Protocol
from cyb.infrastructure.models import Connection


class ConnectionRepository(Protocol):
    """Abstract interface for connection storage."""

    def insert_connection(self, conn: Connection) -> int:
        """Insert a connection. Returns row id."""
        ...

    def get_all_connections(self) -> List[Connection]:
        """Fetch all connections."""
        ...

    def get_recent_connections(self, limit: int = 100) -> List[Connection]:
        """Fetch recent connections (limited)."""
        ...

    def get_connection_by_ip(self, dst_ip: str, limit: int = 50) -> List[Connection]:
        """Fetch connections to a specific IP."""
        ...

    def get_connection_by_exe(self, exe: str, limit: int = 50) -> List[Connection]:
        """Fetch connections from a specific executable."""
        ...

    def clear_connections(self) -> None:
        """Delete all connections."""
        ...

    def update_connection_status(self, conn_id: int, status: str) -> bool:
        """Update connection status."""
        ...
