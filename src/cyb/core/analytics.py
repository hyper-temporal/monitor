"""
Analytics: Aggregate and analyze network traffic patterns.
Responsibility: Group connections by IP, identify patterns, detect anomalies.
"""

from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Tuple


class ConnectionAnalytics:
    """Analyze network connections to find patterns."""

    def __init__(self):
        pass

    @staticmethod
    def group_by_ip(connections: List[dict]) -> Dict[str, dict]:
        """
        Group connections by destination IP.
        Returns dict of IP → aggregated stats.
        """
        grouped = defaultdict(lambda: {
            "ip": None,
            "count": 0,
            "src_ips": set(),
            "processes": set(),
            "ports": set(),
            "protocols": set(),
            "first_seen": None,
            "last_seen": None,
            "status_counts": {"blocked": 0, "allowed": 0, "pending": 0},
            "timestamps": [],
        })

        for conn in connections:
            ip = conn["dst_ip"]
            g = grouped[ip]

            g["ip"] = ip
            g["count"] += 1
            if conn["src_ip"]:
                g["src_ips"].add(conn["src_ip"])
            if conn["exe"]:
                g["processes"].add(conn["exe"])
            g["ports"].add(conn["dst_port"])
            g["protocols"].add(conn["protocol"])
            g["status_counts"][conn["status"]] += 1
            g["timestamps"].append(conn["timestamp"])

            # Track first and last seen
            if g["first_seen"] is None or conn["timestamp"] < g["first_seen"]:
                g["first_seen"] = conn["timestamp"]
            if g["last_seen"] is None or conn["timestamp"] > g["last_seen"]:
                g["last_seen"] = conn["timestamp"]

        # Convert sets to lists for serialization
        for ip, data in grouped.items():
            data["src_ips"] = sorted(list(data["src_ips"]))
            data["processes"] = sorted(list(data["processes"]))
            data["ports"] = sorted(list(data["ports"]))
            data["protocols"] = sorted(list(data["protocols"]))

        return dict(grouped)

    @staticmethod
    def group_by_process(connections: List[dict]) -> Dict[str, dict]:
        """Group connections by process (executable)."""
        grouped = defaultdict(lambda: {
            "process": None,
            "count": 0,
            "destinations": set(),
            "ports": set(),
            "protocols": set(),
            "first_seen": None,
            "last_seen": None,
            "status_counts": {"blocked": 0, "allowed": 0, "pending": 0},
        })

        for conn in connections:
            process = conn["exe"] or "Unknown"
            g = grouped[process]

            g["process"] = process
            g["count"] += 1
            g["destinations"].add(conn["dst_ip"])
            g["ports"].add(conn["dst_port"])
            g["protocols"].add(conn["protocol"])
            g["status_counts"][conn["status"]] += 1

            if g["first_seen"] is None or conn["timestamp"] < g["first_seen"]:
                g["first_seen"] = conn["timestamp"]
            if g["last_seen"] is None or conn["timestamp"] > g["last_seen"]:
                g["last_seen"] = conn["timestamp"]

        for process, data in grouped.items():
            data["destinations"] = sorted(list(data["destinations"]))
            data["ports"] = sorted(list(data["ports"]))
            data["protocols"] = sorted(list(data["protocols"]))

        return dict(grouped)

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
    def get_activity_summary(connections: List[dict]) -> dict:
        """Get overall activity summary."""
        if not connections:
            return {
                "total_connections": 0,
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

        for conn in connections:
            ips.add(conn["dst_ip"])
            if conn["exe"]:
                processes.add(conn["exe"])
            ports.add(conn["dst_port"])
            protocols.add(conn["protocol"])
            status_counts[conn["status"]] += 1

        return {
            "total_connections": len(connections),
            "unique_ips": len(ips),
            "unique_processes": len(processes),
            "unique_ports": len(ports),
            "protocols": sorted(list(protocols)),
            "status": status_counts,
        }

    @staticmethod
    def detect_beaconing(grouped: Dict[str, dict], min_count: int = 5) -> List[str]:
        """
        Detect potential C2 beaconing (repeated connections to same IP).
        Returns list of IPs that look like beacons.
        """
        beacons = []
        for ip, data in grouped.items():
            if data["count"] >= min_count:
                # High frequency connections to same IP = potential beacon
                beacons.append(ip)
        return beacons

    @staticmethod
    def detect_unusual_ports(grouped: Dict[str, dict]) -> List[Tuple[str, List[int]]]:
        """
        Detect connections to unusual ports.
        Returns list of (IP, [unusual_ports])
        """
        common_ports = {80, 443, 53, 22, 25, 465, 587, 993, 143, 123, 5353}
        unusual = []

        for ip, data in grouped.items():
            unusual_p = [p for p in data["ports"] if p not in common_ports and p > 1024]
            if unusual_p:
                unusual.append((ip, unusual_p))

        return unusual
