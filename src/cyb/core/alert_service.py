"""
Core/Application Layer: Alert Service Port.

Abstract interface for sending alerts/notifications to users.
This is a PORT (abstraction) defined at the application layer.

Implementations (email, webhook, syslog, etc.) belong in Infrastructure Layer.
"""

from typing import Protocol, Dict, Any


class AlertService(Protocol):
    """
    Application Service Port: Notification system.
    
    This is an abstraction (port) for sending alerts/notifications.
    Concrete implementations (email, webhook, Slack, etc.) belong in Infrastructure Layer.
    
    The application layer (use cases) depends on this abstraction,
    not on any specific implementation.
    """

    def send_alert(self, alert: Dict[str, Any]) -> None:
        """
        Send an alert to users.
        
        Args:
            alert: Alert dict with fields:
                - severity: "low", "medium", "high", "critical"
                - type: alert type identifier (e.g., "beaconing_detected")
                - message: Human-readable message
                - details: Optional additional data
                - timestamp: Optional timestamp
        """
        ...

    def send_batch(self, alerts: list) -> None:
        """Send multiple alerts at once."""
        ...
