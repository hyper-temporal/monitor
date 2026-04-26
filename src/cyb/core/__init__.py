"""
Core/Application Layer: Use Cases and Service Ports.

Use Cases:
  - ThreatAnalysisUseCase: Detect threats, analyze patterns, send alerts
  - TrafficAnalysisUseCase: Analyze traffic patterns for dashboards

Service Ports (Application-level abstractions):
  - AlertService: Abstract port for sending notifications
    (Implementations in Infrastructure: EmailAlertService, SlackAlertService, etc.)

Responsibility:
  - Orchestrate domain services to implement business workflows
  - Depend on repository interfaces (data access)
  - Depend on service ports (external concerns)
  - Does NOT know about: SQL, email, config, HTTP, logging, etc.

Dependencies:
  - Domain Services (ThreatDetector, ConnectionAnalytics)
  - Repository Interfaces (ConnectionRepository, ThreatIntelligenceRepository)
  - Service Ports (AlertService)
"""

from cyb.core.threat_analysis_use_case import (
    ThreatAnalysisUseCase,
    TrafficAnalysisUseCase,
)
from cyb.core.alert_service import AlertService

__all__ = [
    # Use Cases
    "ThreatAnalysisUseCase",
    "TrafficAnalysisUseCase",
    # Service Ports
    "AlertService",
]
