"""
Domain model: Process metadata.

Represents what we know about a process (PID, executable, user).
Pure domain concept with no infrastructure dependencies.
"""

from dataclasses import dataclass


@dataclass
class ProcessInfo:
    """
    Information about a process.
    
    Domain model: represents process metadata discovered via OS queries.
    No business logic, just a strongly-typed container for process data.
    """
    pid: int
    exe: str      # executable path or "unknown"
    user: str     # username or "unknown"

    def is_known(self) -> bool:
        """Check if process was successfully identified."""
        return self.exe != "unknown" and self.user != "unknown"
