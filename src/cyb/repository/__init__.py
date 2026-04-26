"""
Repository layer: Generic data access interfaces.

Defines contracts for data persistence, independent of specific database implementations.
Implementations (SQLite, PostgreSQL, etc.) belong in infrastructure layer.
"""

from cyb.repository.connection_repository import ConnectionRepository

__all__ = [
    "ConnectionRepository",
]
