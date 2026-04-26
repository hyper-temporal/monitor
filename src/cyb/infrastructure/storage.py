"""
Connection storage via repository abstraction.

Responsibility: Persist and query connections (delegates to repository).
Single Responsibility: Only CRUD operations via repository layer.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ConnectionStorage:
    """SQLite-based connection storage (delegates to repository)."""
    
    def __init__(self, config):
        """Initialize storage with repository."""
        from cyb.repository import SQLiteRepository
        
        self.config = config
        self.db_path = Path(config.get("storage", {}).get("db_path", "~/.cyb/cyb.db")).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use repository for all database operations
        self.repository = SQLiteRepository(db_path=str(self.db_path), read_only=False)
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema via repository."""
        import sqlite3
        import os
        
        # Create tables if needed
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("""
                CREATE TABLE IF NOT EXISTS connections (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    src_ip TEXT,
                    src_port INTEGER,
                    dst_ip TEXT,
                    dst_port INTEGER,
                    protocol TEXT,
                    pid INTEGER,
                    exe TEXT,
                    user TEXT,
                    action TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON connections(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_exe ON connections(exe)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dst_ip ON connections(dst_ip)")
            conn.commit()
            conn.close()
        except sqlite3.OperationalError:
            pass  # Table already exists
        
        # Make database world-writable so frontend can access it
        try:
            os.chmod(str(self.db_path), 0o666)
        except Exception:
            pass
    
    def insert(self, connection: Dict[str, Any]) -> None:
        """Insert a connection via repository."""
        from uuid import uuid4
        from cyb.infrastructure.models import Connection
        
        # Map dict to Connection object
        conn_obj = Connection(
            timestamp=connection.get("timestamp", datetime.utcnow().isoformat()),
            src_ip=connection.get("src_ip"),
            dst_ip=connection.get("dst_ip"),
            dst_port=connection.get("dst_port"),
            protocol=connection.get("protocol"),
            pid=connection.get("pid"),
            exe=connection.get("exe"),
            user=connection.get("user"),
            status=connection.get("action", "allow"),  # Maps action → status
        )
        
        # Direct insert using raw SQL (repository doesn't expose insert yet)
        # This is acceptable as storage.py is the backend persistence layer
        import sqlite3
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute("""
                INSERT INTO connections (
                    id, timestamp, src_ip, src_port, dst_ip, dst_port,
                    protocol, pid, exe, user, action
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid4()),
                conn_obj.timestamp,
                conn_obj.src_ip,
                None,  # src_port
                conn_obj.dst_ip,
                conn_obj.dst_port,
                conn_obj.protocol,
                conn_obj.pid,
                conn_obj.exe,
                conn_obj.user,
                conn_obj.status,
            ))
            conn.commit()
        finally:
            conn.close()
    
    def query(self, since: Optional[str] = None, exe: Optional[str] = None,
             limit: int = 100) -> List[Dict[str, Any]]:
        """Query connections via repository."""
        import sqlite3
        
        # Use direct SQL for complex queries (backend persistence layer)
        query = "SELECT * FROM connections WHERE 1=1"
        params = []
        
        if since:
            query += " AND timestamp >= ?"
            params.append(since)
        
        if exe:
            query += " AND exe LIKE ?"
            params.append(f"%{exe}%")
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
