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

from locmon.domain.connection import Connection
from locmon.domain.packet import Packet
from locmon.domain.process_info import ProcessInfo
from locmon.domain.connection_analytics import ConnectionAnalytics
from locmon.domain.threat_detector import ThreatDetector
from locmon.domain.traffic_classifier import TrafficClassifier
from locmon.domain.ip_intel import identify_ip, identify_port, is_common_traffic

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
