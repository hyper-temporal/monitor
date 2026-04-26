"""
IP intelligence: Identify known services and companies.
Responsibility: Map IP addresses to known services, geolocation hints, etc.
"""

# Common cloud/SaaS providers and their IP ranges (simplified - just popular ones)
KNOWN_SERVICES = {
    # Anthropic / Claude
    "138.199": "Anthropic (Claude)",

    # Google
    "142.250": "Google",
    "172.217": "Google",
    "172.218": "Google",
    "172.219": "Google",
    "172.220": "Google",
    "172.221": "Google",
    "172.222": "Google",
    "172.223": "Google",
    "8.8.8": "Google (DNS)",

    # Cloudflare
    "1.1.1": "Cloudflare (DNS)",
    "1.0.0": "Cloudflare",
    "104.16": "Cloudflare",
    "104.17": "Cloudflare",
    "104.18": "Cloudflare",
    "104.19": "Cloudflare",
    "104.20": "Cloudflare",
    "104.21": "Cloudflare",
    "104.22": "Cloudflare",
    "104.23": "Cloudflare",
    "104.24": "Cloudflare",
    "104.25": "Cloudflare",
    "104.26": "Cloudflare",
    "104.27": "Cloudflare",
    "104.28": "Cloudflare",
    "104.29": "Cloudflare",
    "104.30": "Cloudflare",
    "104.31": "Cloudflare",

    # Amazon AWS
    "3.": "Amazon AWS",
    "13.": "Amazon AWS",
    "16.": "Amazon AWS",
    "18.": "Amazon AWS",
    "34.": "Amazon AWS",
    "35.": "Amazon AWS",
    "43.": "Amazon AWS",
    "44.": "Amazon AWS",
    "50.": "Amazon AWS",
    "52.": "Amazon AWS",
    "54.": "Amazon AWS",
    "55.": "Amazon AWS",
    "64.": "Amazon AWS",
    "176.": "Amazon AWS",
    "177.": "Amazon AWS",
    "198.19": "Amazon AWS",

    # Microsoft Azure
    "40.": "Microsoft Azure",
    "41.": "Microsoft Azure",
    "13.64": "Microsoft Azure",
    "13.65": "Microsoft Azure",
    "13.66": "Microsoft Azure",
    "13.67": "Microsoft Azure",
    "13.68": "Microsoft Azure",
    "13.69": "Microsoft Azure",
    "13.70": "Microsoft Azure",
    "13.71": "Microsoft Azure",
    "13.72": "Microsoft Azure",
    "13.73": "Microsoft Azure",
    "13.74": "Microsoft Azure",
    "13.75": "Microsoft Azure",
    "13.76": "Microsoft Azure",
    "13.77": "Microsoft Azure",
    "13.78": "Microsoft Azure",
    "13.79": "Microsoft Azure",
    "13.80": "Microsoft Azure",
    "13.81": "Microsoft Azure",
    "13.82": "Microsoft Azure",
    "13.84": "Microsoft Azure",
    "13.85": "Microsoft Azure",
    "13.86": "Microsoft Azure",
    "13.87": "Microsoft Azure",
    "13.88": "Microsoft Azure",
    "13.89": "Microsoft Azure",
    "13.90": "Microsoft Azure",

    # Apple
    "17.": "Apple",

    # Facebook/Meta
    "31.13": "Facebook/Meta",
    "66.220": "Facebook/Meta",
    "69.171": "Facebook/Meta",
    "74.119": "Facebook/Meta",

    # Twitter/X
    "192.133": "Twitter/X",

    # Spotify
    "35.186": "Spotify",
    "35.187": "Spotify",
    "35.188": "Spotify",

    # Netflix
    "45.57": "Netflix",
    "52.84": "Netflix",
    "52.85": "Netflix",
    "52.86": "Netflix",
    "52.87": "Netflix",

    # GitHub
    "140.82": "GitHub",
    "143.55": "GitHub",

    # Slack
    "52.89": "Slack",
    "52.90": "Slack",

    # Discord
    "162.125": "Discord",
    "35.186": "Discord",
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
    5900: "VNC",
    8080: "HTTP (alt)",
    8443: "HTTPS (alt)",
    27017: "MongoDB",
}


def identify_ip(dst_ip: str) -> str:
    """
    Identify what service/company an IP belongs to.
    Returns a friendly name or "Unknown".
    """
    # Check against known services
    for prefix, service in KNOWN_SERVICES.items():
        if dst_ip.startswith(prefix):
            return service

    return "Unknown"


def identify_port(dst_port: int) -> str:
    """Identify what service a port typically runs."""
    return KNOWN_PORTS.get(dst_port, f"Unknown (port {dst_port})")


def is_common_traffic(dst_ip: str, dst_port: int) -> bool:
    """Check if this is normal/expected traffic."""
    service = identify_ip(dst_ip)
    port_name = identify_port(dst_port)

    # If we recognize the service, it's probably normal
    if service != "Unknown":
        return True

    # If it's a well-known port, it's probably normal
    if dst_port in KNOWN_PORTS:
        return True

    # Everything else is potentially suspicious
    return False
