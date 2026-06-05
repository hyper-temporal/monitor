"""
Domain: IP intelligence - identify known services and classify traffic.

Business logic for mapping IPs to services and determining if traffic is normal.
"""

# Common cloud/SaaS providers and their IP ranges
KNOWN_SERVICES = {
    "138.199": "Anthropic",
    "142.250": "Google",
    "172.217": "Google",
    "172.218": "Google",
    "8.8.8": "Google DNS",
    "1.1.1": "Cloudflare",
    "104.16": "Cloudflare",
    "3.": "AWS",
    "13.": "AWS",
    "16.": "AWS",
    "18.": "AWS",
    "40.": "Azure",
    "41.": "Azure",
    "17.": "Apple",
    "31.13": "Meta",
    "66.220": "Meta",
    "140.82": "GitHub",
}

# Common ports and their services
KNOWN_PORTS = {
    20: "FTP (data)",
    21: "FTP (control)",
    22: "SSH",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    123: "NTP",
    143: "IMAP",
    443: "HTTPS",
    465: "SMTPS",
    587: "SMTP (submission)",
    993: "IMAPS",
    995: "POP3S",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5353: "mDNS",
    8080: "HTTP (alt)",
    8443: "HTTPS (alt)",
    27017: "MongoDB",
}


def identify_ip(dst_ip: str) -> str:
    """
    Identify what service/company an IP belongs to.
    
    Args:
        dst_ip: Destination IP address
        
    Returns:
        Friendly service name or "Unknown"
    """
    for prefix, service in KNOWN_SERVICES.items():
        if dst_ip.startswith(prefix):
            return service
    return "Unknown"


def identify_port(dst_port: int) -> str:
    """
    Identify what service a port typically runs.
    
    Args:
        dst_port: Destination port
        
    Returns:
        Service name or "Unknown (port X)"
    """
    return KNOWN_PORTS.get(dst_port, f"Unknown (port {dst_port})")


def is_common_traffic(dst_ip: str, dst_port: int) -> bool:
    """
    Check if traffic is normal/expected.
    
    Business rule:
    - If IP is from known service → normal
    - If port is well-known → normal
    - Otherwise → suspicious
    
    Args:
        dst_ip: Destination IP address
        dst_port: Destination port
        
    Returns:
        True if normal, False if suspicious
    """
    service = identify_ip(dst_ip)
    if service != "Unknown":
        return True
    
    if dst_port in KNOWN_PORTS:
        return True
    
    return False
