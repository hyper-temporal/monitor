"""
Domain: Traffic classification logic.

Business rules for classifying network traffic as normal or suspicious.
"""

from typing import Literal


class TrafficClassifier:
    """Classify network traffic as normal or suspicious."""

    # Known services and their IP prefixes (from infrastructure lookup)
    KNOWN_SERVICES = {
        "138.199": "Anthropic",
        "142.250": "Google", "172.217": "Google", "172.218": "Google",
        "8.8.8": "Google DNS",
        "1.1.1": "Cloudflare", "104.16": "Cloudflare",
        "3.": "AWS", "13.": "AWS", "16.": "AWS", "18.": "AWS",
        "40.": "Azure", "41.": "Azure",
        "17.": "Apple",
        "31.13": "Meta", "66.220": "Meta",
    }

    # Known ports and their services
    KNOWN_PORTS = {
        20, 21,    # FTP
        22,        # SSH
        25, 465, 587,  # SMTP
        53,        # DNS
        80, 443,   # HTTP/HTTPS
        110, 143, 993, 995,  # Email
        123,       # NTP
        3306, 5432, 27017,   # Databases
        5353,      # mDNS
    }

    @staticmethod
    def is_common_traffic(dst_ip: str, dst_port: int) -> bool:
        """
        Classify if traffic is normal or unusual.
        
        Business rule:
          - Known services are normal
          - Well-known ports are normal
          - Everything else is potentially suspicious
        
        Returns True if normal, False if suspicious.
        """
        # Check if IP belongs to known service
        for prefix in TrafficClassifier.KNOWN_SERVICES.keys():
            if dst_ip.startswith(prefix):
                return True  # Known service = normal

        # Check if port is well-known
        if dst_port in TrafficClassifier.KNOWN_PORTS:
            return True  # Well-known port = normal

        # Unknown = suspicious
        return False

    @staticmethod
    def classify(dst_ip: str, dst_port: int) -> Literal["normal", "suspicious"]:
        """
        Classify a single connection.
        
        Returns "normal" or "suspicious" based on business rules.
        """
        return "normal" if TrafficClassifier.is_common_traffic(dst_ip, dst_port) else "suspicious"
