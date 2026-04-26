"""
Domain Service: Network traffic analysis.

Pure domain logic for analyzing connections to find patterns and anomalies.
Works exclusively with typed Connection objects (no dict handling).
Focused on aggregation and pattern detection (business intelligence).

No I/O, no infrastructure dependencies - pure computation.
"""

from typing import List, Dict, Tuple
from cyb.domain.connection import Connection


class ConnectionAnalytics:
    """Analyze network connections to find patterns and trends.
    
    Domain Service: implements domain-level business logic for understanding
    traffic patterns. No infrastructure concerns (no I/O, config, etc).
    
    Requires typed Connection objects - callers are responsible for conversion.
    """

    @staticmethod
    def group_by_ip(connections: List[Connection]) -> Dict[str, dict]:
        """
        Group connections by destination IP.
        
        Returns dict of IP → aggregated stats (count, processes, ports, bytes, etc).
        
        Args:
            connections: List of Connection objects (must be typed)
        """
        grouped = {}
        
        for conn in connections:
            ip = conn.dst_ip
            
            if ip not in grouped:
                grouped[ip] = {
                    "ip": ip,
                    "count": 0,
                    "total_bytes": 0,
                    "src_ips": set(),
                    "processes": set(),
                    "ports": set(),
                    "protocols": set(),
                    "first_seen": conn.timestamp,
                    "last_seen": conn.timestamp,
                    "status_counts": {"blocked": 0, "allowed": 0, "pending": 0},
                }
            
            g = grouped[ip]
            g["count"] += 1
            g["total_bytes"] += conn.size
            if conn.src_ip:
                g["src_ips"].add(conn.src_ip)
            if conn.exe:
                g["processes"].add(conn.exe)
            g["ports"].add(conn.dst_port)
            g["protocols"].add(conn.protocol)
            g["status_counts"][conn.status] += 1
            
            # Track first and last seen
            if conn.timestamp < g["first_seen"]:
                g["first_seen"] = conn.timestamp
            if conn.timestamp > g["last_seen"]:
                g["last_seen"] = conn.timestamp
        
        # Convert sets to lists for serialization
        for ip, data in grouped.items():
            data["src_ips"] = sorted(list(data["src_ips"]))
            data["processes"] = sorted(list(data["processes"]))
            data["ports"] = sorted(list(data["ports"]))
            data["protocols"] = sorted(list(data["protocols"]))
        
        return grouped

    @staticmethod
    def group_by_process(connections: List[Connection]) -> Dict[str, dict]:
        """Group connections by process (executable).
        
        Returns dict of process → aggregated stats.
        
        Args:
            connections: List of Connection objects (must be typed)
        """
        grouped = {}
        
        for conn in connections:
            process = conn.exe or "Unknown"
            
            if process not in grouped:
                grouped[process] = {
                    "process": process,
                    "count": 0,
                    "total_bytes": 0,
                    "destinations": set(),
                    "ports": set(),
                    "protocols": set(),
                    "first_seen": conn.timestamp,
                    "last_seen": conn.timestamp,
                    "status_counts": {"blocked": 0, "allowed": 0, "pending": 0},
                }
            
            g = grouped[process]
            g["count"] += 1
            g["total_bytes"] += conn.size
            g["destinations"].add(conn.dst_ip)
            g["ports"].add(conn.dst_port)
            g["protocols"].add(conn.protocol)
            g["status_counts"][conn.status] += 1
            
            if conn.timestamp < g["first_seen"]:
                g["first_seen"] = conn.timestamp
            if conn.timestamp > g["last_seen"]:
                g["last_seen"] = conn.timestamp
        
        # Convert sets to lists for serialization
        for process, data in grouped.items():
            data["destinations"] = sorted(list(data["destinations"]))
            data["ports"] = sorted(list(data["ports"]))
            data["protocols"] = sorted(list(data["protocols"]))
        
        return grouped

    @staticmethod
    def get_top_ips(grouped: Dict[str, dict], limit: int = 20) -> List[Tuple[str, int]]:
        """Get most active destination IPs."""
        return sorted(
            [(ip, data["count"]) for ip, data in grouped.items()],
            key=lambda x: x[1],
            reverse=True
        )[:limit]

    @staticmethod
    def get_top_processes(grouped: Dict[str, dict], limit: int = 20) -> List[Tuple[str, int]]:
        """Get most active processes."""
        return sorted(
            [(proc, data["count"]) for proc, data in grouped.items()],
            key=lambda x: x[1],
            reverse=True
        )[:limit]

    @staticmethod
    def get_activity_summary(connections: List[Connection]) -> dict:
        """Get overall activity summary (metadata about traffic).
        
        Args:
            connections: List of Connection objects (must be typed)
        """
        if not connections:
            return {
                "total_connections": 0,
                "total_bytes": 0,
                "unique_ips": 0,
                "unique_processes": 0,
                "unique_ports": 0,
                "protocols": [],
                "status": {"blocked": 0, "allowed": 0, "pending": 0},
            }

        ips = set()
        processes = set()
        ports = set()
        protocols = set()
        status_counts = {"blocked": 0, "allowed": 0, "pending": 0}
        total_bytes = 0

        for conn in connections:
            ips.add(conn.dst_ip)
            if conn.exe:
                processes.add(conn.exe)
            ports.add(conn.dst_port)
            protocols.add(conn.protocol)
            status_counts[conn.status] += 1
            total_bytes += conn.size

        return {
            "total_connections": len(connections),
            "total_bytes": total_bytes,
            "unique_ips": len(ips),
            "unique_processes": len(processes),
            "unique_ports": len(ports),
            "protocols": sorted(list(protocols)),
            "status": status_counts,
        }
