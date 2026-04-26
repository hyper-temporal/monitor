"""
Test fixtures and constants.
Responsibility: Single source of truth for test data.
"""

# Network test data
TEST_IPS = {
    "local": "192.168.1.100",
    "google_dns": "8.8.8.8",
    "cloudflare_dns": "1.1.1.1",
}

TEST_PORTS = {
    "http": 80,
    "https": 443,
    "dns": 53,
}

TEST_EXES = {
    "chrome": "/usr/bin/chrome",
    "firefox": "/usr/bin/firefox",
}

# Sample tcpdump JSON packets (structure TBD after validation)
SAMPLE_PACKETS = {
    "tcp_https": {
        # TODO: Replace with actual tcpdump -j output
        "sample": "placeholder",
        "expected_fields": {
            "src_ip": TEST_IPS["local"],
            "dst_ip": TEST_IPS["google_dns"],
            "dst_port": TEST_PORTS["https"],
            "protocol": "TCP",
        }
    },
    "udp_dns": {
        # TODO: Replace with actual tcpdump -j output
        "sample": "placeholder",
        "expected_fields": {
            "src_ip": TEST_IPS["local"],
            "dst_ip": TEST_IPS["cloudflare_dns"],
            "dst_port": TEST_PORTS["dns"],
            "protocol": "UDP",
        }
    },
}

# Rules for testing
TEST_RULES = [
    {
        "action": "block",
        "dst_ip": TEST_IPS["google_dns"],
        "dst_port": None,
        "exe": None,
    },
    {
        "action": "allow",
        "dst_ip": None,
        "dst_port": TEST_PORTS["https"],
        "exe": TEST_EXES["chrome"],
    },
]
