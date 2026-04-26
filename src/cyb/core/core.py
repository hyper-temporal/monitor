"""
Core domain models and repository interfaces.
Responsibility: Define data types and abstract repository contract.
No database dependencies—pure Python types.
"""

from dataclasses import dataclass
from typing import List, Optional, Protocol
from datetime import datetime


@dataclass
class Connection:
    """A network connection (domain model)."""
    timestamp: str
    src_ip: str
    dst_ip: str
    dst_port: int
    protocol: str
    pid: Optional[int] = None
    exe: Optional[str] = None
    user: Optional[str] = None
    status: str = "pending"  # pending, allowed, blocked

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "src_ip": self.src_ip,
            "dst_ip": self.dst_ip,
            "dst_port": self.dst_port,
            "protocol": self.protocol,
            "pid": self.pid,
            "exe": self.exe,
            "user": self.user,
            "status": self.status,
        }


@dataclass
class Rule:
    """A traffic rule (domain model)."""
    action: str  # allow, block
    dst_ip: Optional[str] = None
    dst_port: Optional[int] = None
    exe: Optional[str] = None
    created: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "action": self.action,
            "dst_ip": self.dst_ip,
            "dst_port": self.dst_port,
            "exe": self.exe,
            "created": self.created,
        }


class ConnectionRepository(Protocol):
    """Abstract interface for connection storage (protocol/ABC)."""

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


class RuleRepository(Protocol):
    """Abstract interface for rule storage."""

    def insert_rule(self, action: str, dst_ip: Optional[str], dst_port: Optional[int], exe: Optional[str], created: str) -> int:
        """Insert a rule. Returns row id."""
        ...

    def get_rules(self) -> List[dict]:
        """Fetch all rules."""
        ...

    def delete_rule(self, rule_id: int) -> bool:
        """Delete a rule."""
        ...

    def clear_rules(self) -> None:
        """Delete all rules."""
        ...


class Database(Protocol):
    """Abstract interface for database operations."""

    def vacuum(self) -> None:
        """Optimize database (reclaim space)."""
        ...

    def clear_all(self) -> None:
        """Clear all tables and optimize."""
        ...
