"""
Data export module.

Responsibility: Export connections in various formats.
Single Responsibility: Only export logic (uses repository for data access).
"""

import json
import csv
from io import StringIO
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Exporter:
    """Exports connection data."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize exporter with repository."""
        from cyb.infrastructure import SQLiteRepository
        from cyb.infrastructure import Config
        
        if db_path is None:
            config = Config()
            db_path = config.get("storage", {}).get("db_path", "~/.cyb/cyb.db")
        
        self.repository = SQLiteRepository(db_path=db_path, read_only=True)
    
    def export(self, format: str = "json") -> str:
        """Export all connections."""
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
