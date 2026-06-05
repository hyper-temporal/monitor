"""
Domain: Threat detection logic.

Business rules for identifying malicious or suspicious network behavior.
Works with typed Connection objects, not dicts.
"""

from typing import List, Tuple
from locmon.domain.connection import Connection


class ThreatDetector:
    """Identify potentially malicious network behavior."""

    @staticmethod
    def is_beaconing(connections: List[Connection], min_count: int = 5) -> List[str]:
        """
        Detect potential C2 beaconing (repeated connections to same IP).

        Business rule: If traffic to same IP >= min_count times, it's suspicious.
        C2 beacons often establish periodic callbacks.

        Args:
            connections: List of typed Connection objects
            min_count: Minimum repeated connections to flag as beacon

        Returns list of IPs that look like beacons.
        """
        # Count connections per IP
        ip_counts = {}
        for conn in connections:
            ip = conn.dst_ip
            ip_counts[ip] = ip_counts.get(ip, 0) + 1

        # Find IPs with >= min_count connections
        beacons = [ip for ip, count in ip_counts.items() if count >= min_count]
        return beacons

    @staticmethod
    def has_unusual_ports(connections: List[Connection]) -> List[Tuple[str, List[int]]]:
        """
        Detect connections to unusual ports.

        Business rule: Connections to non-standard high ports are suspicious.
        Standard ports are HTTP/HTTPS/DNS/NTP/etc.

        Args:
            connections: List of typed Connection objects

        Returns list of (IP, [unusual_ports]) tuples.
        """
        common_ports = {80, 443, 53, 22, 25, 465, 587, 993, 143, 123, 5353}

        # Aggregate ports per IP
        ip_ports = {}
        for conn in connections:
            ip = conn.dst_ip
            port = conn.dst_port
            if ip not in ip_ports:
                ip_ports[ip] = set()
            ip_ports[ip].add(port)

        # Find IPs with unusual ports (high port >1024 not in common list)
        unusual = []
        for ip, ports in ip_ports.items():
            unusual_p = [p for p in ports if p not in common_ports and p > 1024]
            if unusual_p:
                unusual.append((ip, sorted(unusual_p)))

        return unusual

    @staticmethod
    def detect_threats(connections: List[Connection]) -> dict:
        """
        Run all threat detection rules on a set of connections.

        Returns dict with all threat indicators.
        """
        return {
            "beacons": ThreatDetector.is_beaconing(connections),
            "unusual_ports": ThreatDetector.has_unusual_ports(connections),
        }
