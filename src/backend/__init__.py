"""
Backend layer: IPC interface for frontend-backend communication.

Exports:
- BackendAPI: Query interface and event callbacks
"""

from cyb.backend.api import BackendAPI

__all__ = [
    "BackendAPI",
]
