"""
Core layer: Application orchestrators - pure business logic.

Coordinates domain logic to implement business workflows.
Does NOT handle I/O, serialization, or infrastructure details.

Examples: ConnectionAnalytics (groups and analyzes connections)
"""

from cyb.core.analytics import ConnectionAnalytics

__all__ = [
    "ConnectionAnalytics",
]
