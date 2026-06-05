"""
Data export application service.

Responsibility: Export connections in various formats using repository abstraction.
Depends on repository interface (ConnectionRepository), not specific database implementation.

Dependencies are injected from outside - no default instantiation.
"""

import json
import csv
from io import StringIO
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from locmon.repository import ConnectionRepository

logger = logging.getLogger(__name__)


class Exporter:
    """Exports connection data in multiple formats.
    
    Pure infrastructure service: depends on repository interface, not implementation.
    Dependencies injected from outside (factory or DI container).
    """
    
    def __init__(self, repository: "ConnectionRepository") -> None:
        """Initialize exporter with injected repository.
        
        Args:
            repository: ConnectionRepository implementation (interface).
                       Must be provided - no default instantiation.
                       
        Raises:
            TypeError: If repository is None
        """
        if repository is None:
            raise TypeError(
                "Exporter requires explicit repository injection. "
                "Use create_exporter() factory or inject directly."
            )
        self.repository = repository
    
    def export(self, format: str = "json") -> str:
        """Export all connections in requested format.
        
        Args:
            format: Output format - "json", "csv", or "sql"
            
        Returns:
            Exported data as string
            
        Raises:
            ValueError: If format is unknown
        """
        connections = self.repository.get_all_connections()
        
        if format == "json":
            return self._to_json(connections)
        elif format == "csv":
            return self._to_csv(connections)
        elif format == "sql":
            return self._to_sql(connections)
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def _to_json(self, connections) -> str:
        """Export as JSON."""
        data = [conn.to_dict() for conn in connections]
        return json.dumps(data, indent=2)
    
    def _to_csv(self, connections) -> str:
        """Export as CSV."""
        if not connections:
            return ""
        
        output = StringIO()
        conn_dicts = [conn.to_dict() for conn in connections]
        writer = csv.DictWriter(output, fieldnames=conn_dicts[0].keys())
        writer.writeheader()
        writer.writerows(conn_dicts)
        return output.getvalue()
    
    def _to_sql(self, connections) -> str:
        """Export as SQL INSERT statements."""
        lines = []
        for conn in connections:
            conn_dict = conn.to_dict()
            cols = ", ".join(conn_dict.keys())
            vals = ", ".join(f"'{v}'" if v else "NULL" for v in conn_dict.values())
            lines.append(f"INSERT INTO connections ({cols}) VALUES ({vals});")
        return "\n".join(lines)


def create_exporter(repository: "ConnectionRepository" = None) -> Exporter:
    """Factory function to create an Exporter with dependency injection.
    
    Args:
        repository: Injected ConnectionRepository implementation.
                   If None, creates SQLiteRepository with default config.
    
    Returns:
        Configured Exporter instance
        
    Note:
        This factory handles the infrastructure concern of instantiating
        SQLiteRepository. Exporter itself depends only on the interface.
    """
    if repository is None:
        # Infrastructure concern: create concrete implementation with config
        from locmon.infrastructure.sqlite_repository import SQLiteRepository
        from locmon.infrastructure.config import Config
        
        config = Config()
        db_path = config.get("storage", {}).get("db_path", "~/.cyb/cyb.db")
        repository = SQLiteRepository(db_path=db_path, read_only=True)
    
    return Exporter(repository=repository)
