"""
Repository interface for database operations.

Defines the contract for database-level operations.
"""

from typing import Protocol


class Database(Protocol):
    """Abstract interface for database operations."""

    def vacuum(self) -> None:
        """Optimize database (reclaim space)."""
        ...

    def clear_all(self) -> None:
        """Clear all tables and optimize."""
        ...
