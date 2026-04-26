"""Tests for packet capture parsing."""

import pytest
from cyb.core.capture import PacketCapture


@pytest.fixture
def mock_config():
    return {
        "capture": {"interface": None}
    }


@pytest.fixture
def capture(mock_config):
    return PacketCapture(mock_config)


class TestPacketParsing:
    """Test tcpdump line parsing."""
    
    def test_parse_udp_packet(self, capture):
        """Parse UDP packet."""
        line = "13:45:22.123456 IP 192.168.1.100.54321 > 8.8.8.8.53: UDP, length 53"
        result = capture._parse_line(line)
        
        assert result is not None
        assert result["src_ip"] == "192.168.1.100"
        assert result["src_port"] == 54321
        assert result["dst_ip"] == "8.8.8.8"
        assert result["dst_port"] == 53
        assert result["protocol"] == "UDP"
        assert result["timestamp"] is not None
    
    def test_parse_tcp_packet(self, capture):
        """Parse TCP packet."""
        line = "13:45:22.234567 IP 192.168.1.100.54322 > 1.1.1.1.443: TCP Flags [S]"
        result = capture._parse_line(line)
        
        assert result is not None
        assert result["src_ip"] == "192.168.1.100"
        assert result["dst_port"] == 443
        assert result["protocol"] == "TCP"
    
    def test_parse_invalid_line(self, capture):
        """Skip invalid lines."""
        assert capture._parse_line("") is None
        assert capture._parse_line("tcpdump: listening on any") is None
        assert capture._parse_line("garbage data") is None
    
    def test_parse_ipv6_ignored(self, capture):
        """IPv6 packets not parsed yet."""
        line = "2001:db8::1.54321 > 2001:db8::2.443: TCP"
        result = capture._parse_line(line)
        assert result is None
    
    def test_parse_multiple_ips_in_line(self, capture):
        """Handle lines with multiple IP patterns."""
        # Real tcpdump output can be messy
        line = "13:45:22 IP 10.0.0.1.1234 > 10.0.0.2.5678: TCP"
        result = capture._parse_line(line)
        
        assert result is not None
        assert result["dst_ip"] == "10.0.0.2"
        assert result["dst_port"] == 5678


class TestSampleData:
    """Test with realistic tcpdump output."""
    
    SAMPLE_OUTPUT = [
        "13:45:22.123456 IP 192.168.1.100.54321 > 8.8.8.8.53: UDP, length 53",
        "13:45:22.234567 IP 192.168.1.100.54322 > 1.1.1.1.443: TCP Flags [S]",
        "13:45:22.345678 IP 192.168.1.100.12345 > 142.250.80.46.443: TCP Flags [.]",
        "13:45:23.456789 IP 192.168.1.101.51234 > 8.8.8.8.53: UDP, length 33",
    ]
    
    def test_parse_sample_output(self, capture):
        """Parse realistic tcpdump output."""
        results = [capture._parse_line(line) for line in self.SAMPLE_OUTPUT]
        results = [r for r in results if r]  # Filter None
        
        assert len(results) == 4
        
        # Check first packet
        assert results[0]["src_ip"] == "192.168.1.100"
        assert results[0]["dst_ip"] == "8.8.8.8"
        assert results[0]["dst_port"] == 53
        assert results[0]["protocol"] == "UDP"
        
        # Check second packet
        assert results[1]["protocol"] == "TCP"
        assert results[1]["dst_port"] == 443
        
        # Check third packet
        assert results[2]["dst_ip"] == "142.250.80.46"
        
        # Check fourth packet
        assert results[3]["src_ip"] == "192.168.1.101"
