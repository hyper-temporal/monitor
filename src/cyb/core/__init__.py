"""
Core layer: Re-exports public APIs from backend, infrastructure, and domain.

This module serves as the primary interface for accessing Cyb functionality.
Actual implementation lives in:
- cyb.backend (orchestrators)
- cyb.infrastructure (technical implementations)
- cyb.domain (data models)
"""

# Re-export backend orchestrators for backward compatibility
from cyb.backend import BackendAPI, Monitor

# Re-export infrastructure for direct access if needed
from cyb.infrastructure import PacketCapture, ConnectionStorage, ProcessEnricher, Config, get_logger

__all__ = [
    # Backend orchestrators
    "BackendAPI",
    "Monitor",
    # Infrastructure components
    "PacketCapture",
    "ConnectionStorage",
    "ProcessEnricher",
    "Config",
    "get_logger",
]
