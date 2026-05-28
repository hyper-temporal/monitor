"""
Application Layer: Use Cases for Threat Analysis Workflow.

Orchestrates domain services and infrastructure to implement complete
business workflows: analyze traffic for threats and generate alerts.

Responsibility:
  - Coordinate ThreatDetector (domain service) to find threats
  - Coordinate ConnectionAnalytics (domain service) to find patterns
  - Use AlertService (application port) to notify users
  - Use ThreatIntelligenceRepository (repository interface) to persist findings

Flow:
  1. Get connections from repository
  2. Run threat detection (domain logic)
  3. Analyze traffic patterns (domain logic)
  4. Persist results (via repository interface)
  5. Send alerts (via alert service port)

Dependencies:
  - Domain Services: Pure business logic (ThreatDetector, ConnectionAnalytics)
  - Repository Interfaces: Data access contracts (ConnectionRepository, ThreatIntelligenceRepository)
  - Service Ports: External concerns (AlertService)
"""

from typing import List, Dict
from typing import TYPE_CHECKING

from cyb.domain import (
    Connection,
    ThreatDetector,
    ConnectionAnalytics,
    TrafficClassifier,
)

if TYPE_CHECKING:
    from cyb.repository import (
        ConnectionRepository,
        ThreatIntelligenceRepository,
    )
    from cyb.core import AlertService


class ThreatAnalysisUseCase:
    """
    Application Service: Implement threat analysis workflow.
    
    Coordinates:
    - Domain services (ThreatDetector, ConnectionAnalytics)
    - Repository interfaces (where to get/store data)
    - Alert service port (where to send notifications)
    
    Does NOT know about:
    - SQL, databases, config files
    - Email, webhooks, specific alert implementations
    - Any infrastructure details
    """

    def __init__(
        self,
        connection_repo: "ConnectionRepository",
        threat_repo: "ThreatIntelligenceRepository",
        alert_service: "AlertService",
    ):
        """
        Initialize use case with injected dependencies.
        
        Args:
            connection_repo: Repository to fetch connections
            threat_repo: Repository to store threat findings
            alert_service: Service port to send alerts to users
        """
        self.connection_repo = connection_repo
        self.threat_repo = threat_repo
        self.alert_service = alert_service

    def analyze_threats(self, limit: int = 100) -> Dict:
        """
        Run complete threat analysis workflow.
        
        Steps:
        1. Fetch connections from repository
        2. Detect threats (domain logic)
        3. Analyze patterns (domain logic)
        4. Classify traffic (domain logic)
        5. Store results (via repository interface)
        6. Send alerts (via alert service port)
        
        Args:
            limit: Number of recent connections to analyze
            
        Returns:
            Dict with threat analysis results
        """
        # 1. Get connections from repository
        connections: List[Connection] = self.connection_repo.get_connections(limit=limit)

        if not connections:
            return {
                "status": "no_data",
                "message": "No connections to analyze",
                "threats": [],
                "patterns": {},
            }

        # 2. Run threat detection (pure domain logic)
        threats = ThreatDetector.detect_threats(connections)

        # 3. Analyze traffic patterns (pure domain logic)
        grouped_by_ip = ConnectionAnalytics.group_by_ip(connections)
        top_ips = ConnectionAnalytics.get_top_ips(grouped_by_ip)
        summary = ConnectionAnalytics.get_activity_summary(connections)

        # 4. Classify traffic (pure domain logic)
        classification = TrafficClassifier.classify_connections(connections)

        # 5. Store findings in threat repository (via interface)
        threat_findings = {
            "timestamp": self._get_timestamp(),
            "total_connections": summary["total_connections"],
            "threats_found": {
                "beacons": threats["beacons"],
                "unusual_ports": threats["unusual_ports"],
            },
            "suspicious_traffic": classification["suspicious"],
            "suspicious_ips": classification["suspicious_ips"],
        }
        self.threat_repo.store_findings(threat_findings)

        # 6. Send alerts for critical findings (via alert service port)
        if threats["beacons"] or classification["suspicious"] > 0:
            self._send_threat_alerts(threats, classification)

        # Return results to caller
        return {
            "status": "completed",
            "summary": summary,
            "threats": threats,
            "suspicious_traffic": classification,
            "top_destinations": top_ips[:5],
        }

    def _send_threat_alerts(self, threats: Dict, classification: Dict) -> None:
        """Send notifications for detected threats via alert service port."""
        alerts = []

        if threats["beacons"]:
            alerts.append({
                "severity": "high",
                "type": "beaconing_detected",
                "message": f"Potential C2 beaconing to {len(threats['beacons'])} IPs",
                "details": threats["beacons"],
            })

        if threats["unusual_ports"]:
            alerts.append({
                "severity": "medium",
                "type": "unusual_ports_detected",
                "message": f"Unusual port activity on {len(threats['unusual_ports'])} IPs",
                "details": threats["unusual_ports"],
            })

        if classification["suspicious"] > 0:
            alerts.append({
                "severity": "medium",
                "type": "suspicious_traffic_detected",
                "message": f"{classification['suspicious']} suspicious connections detected",
                "details": classification["suspicious_ips"],
            })

        # Send each alert via alert service port
        for alert in alerts:
            self.alert_service.send_alert(alert)

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp (can be mocked for testing)."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


class TrafficAnalysisUseCase:
    """
    Application Service: Analyze traffic patterns.
    
    Simpler use case: analyze traffic without threat detection.
    Useful for dashboards and reports.
    """

    def __init__(self, connection_repo: "ConnectionRepository"):
        """Initialize with repository for getting connections."""
        self.connection_repo = connection_repo

    def get_traffic_overview(self, limit: int = 100) -> Dict:
        """
        Get high-level traffic overview.
        
        Args:
            limit: Number of connections to analyze
            
        Returns:
            Dict with traffic overview
        """
        connections: List[Connection] = self.connection_repo.get_connections(limit=limit)

        if not connections:
            return {"status": "no_data"}

        # Use domain services to analyze
        summary = ConnectionAnalytics.get_activity_summary(connections)
        grouped_by_ip = ConnectionAnalytics.group_by_ip(connections)
        grouped_by_process = ConnectionAnalytics.group_by_process(connections)

        return {
            "status": "success",
            "summary": summary,
            "top_destinations": ConnectionAnalytics.get_top_ips(grouped_by_ip, limit=10),
            "top_processes": ConnectionAnalytics.get_top_processes(grouped_by_process, limit=10),
        }
