"""
Domain layer: Business logic and core concepts.

Entities:
  - Connection, Packet, ProcessInfo

Domain Services:
  - ConnectionAnalytics: traffic pattern analysis
  - ThreatDetector: threat identification rules
  - TrafficClassifier: normal vs suspicious classification

Utilities:
  - identify_ip, identify_port, is_common_traffic: IP/port intelligence

Pure business logic with zero infrastructure dependencies.
"""

from cyb.domain.connection import Connection
from cyb.domain.packet import Packet
from cyb.domain.process_info import ProcessInfo
from cyb.domain.connection_analytics import ConnectionAnalytics
from cyb.domain.threat_detector import ThreatDetector
from cyb.domain.traffic_classifier import TrafficClassifier
from cyb.domain.ip_intel import identify_ip, identify_port, is_common_traffic

__all__ = [
    # Entities
    "Connection",
    "Packet",
    "ProcessInfo",
    # Domain Services
    "ConnectionAnalytics",
    "ThreatDetector",
    "TrafficClassifier",
    # Utilities
    "identify_ip",
    "identify_port",
    "is_common_traffic",
]
