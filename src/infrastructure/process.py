"""
Process enrichment via lsof/ps.

Responsibility: Map PIDs to executable names, user info.
Single Responsibility: Only enriches process metadata.
"""

import subprocess
import logging

from cyb.domain import ProcessInfo

logger = logging.getLogger(__name__)


class ProcessEnricher:
    """Enriches connections with process information."""
    
    def __init__(self, config):
        """Initialize with config."""
        self.config = config
        self._cache: dict[int, ProcessInfo] = {}
    
    def get_process_info(self, pid: int) -> ProcessInfo:
        """
        Get process info for a given PID.
        
        Returns ProcessInfo with exe and user (or "unknown" if not found).
        Results are cached for performance.
        """
        if pid in self._cache:
            return self._cache[pid]
        
        info = self._fetch_process_info(pid)
        self._cache[pid] = info
        return info
    
    def _fetch_process_info(self, pid: int) -> ProcessInfo:
        """Fetch process info from /proc or ps."""
        try:
            # Try /proc/[pid]/comm (Linux)
            try:
                with open(f"/proc/{pid}/comm") as f:
                    exe = f.read().strip()
                    user = self._get_user(pid)
                    return ProcessInfo(pid=pid, exe=exe, user=user)
            except FileNotFoundError:
                pass
            
            # Fallback: ps command (macOS/BSD)
            result = subprocess.run(
                ["ps", "-o", "comm=", "-p", str(pid)],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                exe = result.stdout.strip()
                user = self._get_user(pid)
                return ProcessInfo(pid=pid, exe=exe, user=user)
            
        except Exception as e:
            logger.debug(f"Process fetch error (PID {pid}): {e}")
        
        # Return unknown process info
        return ProcessInfo(pid=pid, exe="unknown", user="unknown")
    
    def _get_user(self, pid: int) -> str:
        """Get user for PID."""
        try:
            with open(f"/proc/{pid}/status") as f:
                for line in f:
                    if line.startswith("Uid:"):
                        uid = line.split()[1]
                        return uid
        except Exception:
            pass
        return "unknown"
