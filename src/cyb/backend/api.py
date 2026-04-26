"""
IPC API for backend-frontend communication.
Responsibility: Expose backend operations through queue-based interface.
"""

from typing import Any, Callable, Optional

from cyb.domain import Connection
from cyb.infrastructure import SQLiteRepository


class BackendAPI:
    """
    Simple IPC interface for frontend.
    Uses queues for command/response, callbacks for events.
    """

    def __init__(self, db_path: str = None, read_only: bool = False):
        """Initialize backend with repository.
        
        Args:
            db_path: Path to SQLite database
            read_only: If True, open in read-only mode (for frontend use)
        """
        if db_path is None:
            db_path = "cyb.db"
        
        self.storage = SQLiteRepository(db_path=db_path, read_only=read_only)
        self._event_callbacks = {}
        self.read_only = read_only

    def set_event_handler(self, event_type: str, callback: Callable) -> None:
        """Register a callback for an event type."""
        self._event_callbacks[event_type] = callback

    def _emit_event(self, event_type: str, data: Any) -> None:
        """Emit an event if a handler is registered."""
        if event_type in self._event_callbacks:
            self._event_callbacks[event_type](data)

    def ingest_connection(self, conn: Connection) -> None:
        """
        Ingest a new connection.
        - Store it
        - Emit event
        """
        if self.read_only:
            raise RuntimeError("Cannot ingest connections in read-only mode")
        
        # Store (status already set by backend daemon)
        conn_id = self.storage.insert_connection(conn)

        # Emit event for UI (compact serialization: exclude None values)
        self._emit_event("connection_ingested", {
            "id": conn_id,
            "connection": conn.to_dict(include_none=False),
        })

    def get_recent_connections(self, limit: int = 100) -> list:
        """Fetch recent connections (limited, compact serialization)."""
        conns = self.storage.get_connections(limit=limit)
        return [c.to_dict(include_none=False) for c in conns]

    def get_all_connections(self) -> list:
        """Fetch all connections from database (no limit, compact)."""
        conns = self.storage.get_all_connections()
        return [c.to_dict(include_none=False) for c in conns]

    def get_connections_by_ip(self, dst_ip: str, limit: int = 50) -> list:
        """Query connections by destination IP (compact)."""
        conns = self.storage.get_connection_by_ip(dst_ip, limit=limit)
        return [c.to_dict(include_none=False) for c in conns]

    def get_connections_by_exe(self, exe: str, limit: int = 50) -> list:
        """Query connections by executable (compact)."""
        conns = self.storage.get_connection_by_exe(exe, limit=limit)
        return [c.to_dict(include_none=False) for c in conns]

    def get_rules(self) -> list:
        """Get all rules (returns empty list - rules not implemented)."""
        return []

    def clear_database(self) -> None:
        """Clear all connections and vacuum database.
        
        Opens a separate writable connection, ignoring read_only mode.
        """
        from cyb.infrastructure import SQLiteRepository
        
        # Create temporary writable repository to clear data
        temp_storage = SQLiteRepository(db_path=self.storage.db_path, read_only=False)
        temp_storage.clear_and_vacuum()
