"""
Repository layer: Data access abstraction and interfaces.

Responsibility: Define data access contracts and implement them.
All database operations belong here.
"""

# Import interfaces from dedicated modules
from cyb.repository.connection_repository import ConnectionRepository
from cyb.repository.database import Database

# Import concrete implementations
from cyb.repository.sqlite import SQLiteRepository

__all__ = [
    # Interfaces
    "ConnectionRepository",
    "Database",
    # Implementations
    "SQLiteRepository",
]
