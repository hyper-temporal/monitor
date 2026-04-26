"""
Core layer: Re-exports public APIs from backend, service, infrastructure, and domain.

This module serves as the primary interface for accessing Cyb functionality.
Actual implementation lives in:
- cyb.backend (IPC API)
- cyb.service (application services/orchestrators)
- cyb.infrastructure (technical implementations)
- cyb.domain (data models)
"""

# Re-export backend IPC API
from cyb.backend import BackendAPI

# Re-export service layer for backward compatibility
from cyb.service import NetworkMonitorService

# Re-export infrastructure for direct access if needed
from cyb.infrastructure import PacketCapture, ConnectionStorage, ProcessEnricher, Config, get_logger

__all__ = [
    # Backend IPC
    "BackendAPI",
    # Service orchestrators
    "NetworkMonitorService",
    # Infrastructure components
    "PacketCapture",
    "ConnectionStorage",
    "ProcessEnricher",
    "Config",
    "get_logger",
]
