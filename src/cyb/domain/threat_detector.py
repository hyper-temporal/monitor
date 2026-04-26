"""
Domain: Threat detection logic.

Business rules for identifying malicious or suspicious network behavior.
"""

from typing import List, Tuple, Dict


class ThreatDetector:
    """Identify potentially malicious network behavior."""

    @staticmethod
    def is_beaconing(grouped: Dict[str, dict], min_count: int = 5) -> List[str]:
        """
        Detect potential C2 beaconing (repeated connections to same IP).
        
        Business rule: If traffic to same IP >= min_count, it's suspicious.
        C2 beacons often establish periodic callbacks.
        
        Returns list of IPs that look like beacons.
        """
        beacons = []
        for ip, data in grouped.items():
            if data["count"] >= min_count:
                beacons.append(ip)
        return beacons

    @staticmethod
    def has_unusual_ports(grouped: Dict[str, dict]) -> List[Tuple[str, List[int]]]:
        """
        Detect connections to unusual ports.
        
        Business rule: Connections to non-standard high ports are suspicious.
        Standard ports are HTTP/HTTPS/DNS/NTP/etc.
        
        Returns list of (IP, [unusual_ports])
        """
        common_ports = {80, 443, 53, 22, 25, 465, 587, 993, 143, 123, 5353}
        unusual = []

        for ip, data in grouped.items():
            # Unusual = high port (>1024) not in common list
            unusual_p = [p for p in data["ports"] if p not in common_ports and p > 1024]
            if unusual_p:
                unusual.append((ip, unusual_p))

        return unusual
