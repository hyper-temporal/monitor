"""
Network packet capture via tcpdump.

Responsibility: Parse tcpdump output into Packet objects.
Works with standard macOS/Linux tcpdump.

Single Responsibility: Only handles packet parsing.
Dependency Inversion: Accepts configurable field_map, not hardcoded structure.
"""

import re
import subprocess
import shlex
from datetime import datetime
from typing import Generator, Optional
import logging

from cyb.domain.packet import Packet

logger = logging.getLogger(__name__)


class PacketCapture:
    """Captures and parses network packets using tcpdump."""

    def __init__(self, config):
        """Initialize packet capture with config."""
        self.config = config
        self.interface = config.get("capture", {}).get("interface")

    def stream(self) -> Generator[Packet, None, None]:
        """Stream packets from tcpdump as typed Packet objects."""
        cmd = self._build_command()
        logger.info(f"Starting tcpdump: {cmd}")

        try:
            # Run with sudo if needed
            full_cmd = f"sudo {cmd}"

            proc = subprocess.Popen(
                shlex.split(full_cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            for line in proc.stdout:
                packet = self._parse_line(line)
                if packet:
                    yield packet

        except KeyboardInterrupt:
            logger.info("Capture stopped by user")
        except PermissionError as e:
            logger.error("Need root access for packet capture")
            raise
        except Exception as e:
            logger.error(f"Capture error: {e}")
            raise

    def _build_command(self) -> str:
        """Build tcpdump command."""
        # Capture TCP and UDP packets
        # -i any: all interfaces
        # -n: no DNS resolution (faster)
        # -l: line buffered output
        # -q: quiet (less info per packet)

        if self.interface:
            cmd = f"tcpdump -i {self.interface} -n -l -q tcp or udp"
        else:
            cmd = "tcpdump -i any -n -l -q tcp or udp"

        return cmd

    def _parse_line(self, line: str) -> Optional[Packet]:
        """Parse a single tcpdump line into typed Packet.

        Example tcpdump output:
        13:45:22.123456 IP 192.168.1.100.54321 > 8.8.8.8.53: UDP, length 53
        13:45:22.234567 IP 192.168.1.100.54322 > 1.1.1.1.443: TCP Flags [S]
        """
        try:
            if not line.strip() or line.startswith("tcpdump"):
                return None

            # Parse IP addresses and ports
            # Pattern: src_ip.src_port > dst_ip.dst_port
            match = re.search(
                r'(\d+\.\d+\.\d+\.\d+)\.(\d+)\s*>\s*(\d+\.\d+\.\d+\.\d+)\.(\d+)',
                line
            )
            if not match:
                return None

            src_ip, src_port, dst_ip, dst_port = match.groups()

            # Determine protocol
            protocol = "UDP" if "UDP" in line else "TCP"

            # Return typed Packet (NamedTuple - more efficient than dataclass)
            return Packet(
                timestamp=datetime.utcnow().isoformat(),
                src_ip=src_ip,
                src_port=int(src_port),
                dst_ip=dst_ip,
                dst_port=int(dst_port),
                protocol=protocol,
                pid=None,  # Will be enriched later
            )
        except (ValueError, AttributeError) as e:
            logger.debug(f"Parse error on line '{line}': {e}")
            return None
