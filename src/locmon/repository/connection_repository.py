"""
Repository interface: Generic contract for connection data access.

Abstraction layer - independent of any specific database implementation.
Allows swapping SQLite for PostgreSQL, MongoDB, etc. without changing domain or infrastructure code.
"""

from typing import List, Protocol

from locmon.domain import Connection


class ConnectionRepository(Protocol):
    """
    Abstract interface for connection data access.
    
    Implementations (e.g., SQLiteRepository) handle specific database backends.
    Domain code depends only on this interface, not concrete implementations.
    """

    def insert_connection(self, conn: Connection) -> int:
        """Insert a connection record. Returns row id."""
        ...

    def get_connections(self, limit: int = 100) -> List[Connection]:
        """Get recent connections (limited)."""
        ...

    def get_all_connections(self) -> List[Connection]:
        """Get all connections from database (no limit)."""
        ...

    def get_connection_by_ip(self, dst_ip: str, limit: int = 50) -> List[Connection]:
        """Get connections by destination IP."""
        ...

    def get_connection_by_exe(self, exe: str, limit: int = 50) -> List[Connection]:
        """Get connections by executable."""
        ...

    def clear_and_vacuum(self) -> None:
        """Delete all connections and reclaim space."""
        ...
