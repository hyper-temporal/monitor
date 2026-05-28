"""
Repository Interface: ThreatIntelligenceRepository.

Abstract interface for storing and retrieving threat analysis findings.
Implementations: SQLite, PostgreSQL, Elasticsearch, etc.
"""

from typing import Protocol, Dict, Any, List


class ThreatIntelligenceRepository(Protocol):
    """
    Abstract interface for threat intelligence storage.
    
    Stores findings from threat analysis for:
    - Historical lookup
    - Alerting trends
    - Learning patterns
    - Reporting
    """

    def store_findings(self, findings: Dict[str, Any]) -> int:
        """
        Store threat analysis findings.
        
        Args:
            findings: Dict with threat analysis results:
                - timestamp: When analysis was run
                - total_connections: Number of connections analyzed
                - threats_found: Dict of threat types found
                - suspicious_traffic: Count of suspicious connections
                - suspicious_ips: List of suspicious IPs
        
        Returns:
            ID of stored finding
        """
        ...

    def get_findings(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent threat findings."""
        ...

    def get_findings_by_ip(self, dst_ip: str) -> List[Dict[str, Any]]:
        """Get all findings related to specific IP."""
        ...

    def get_threats_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get summary of threats over time period."""
        ...
