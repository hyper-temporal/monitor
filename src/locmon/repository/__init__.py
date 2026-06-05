"""
Repository Layer: Data Access Interface Abstractions.

Defines abstract contracts for data persistence, independent of specific database implementations.

Repository Interfaces:
  - ConnectionRepository: Get/store network connections
  - ThreatIntelligenceRepository: Store/retrieve threat analysis findings

Implementations (e.g., SQLiteRepository, ThreatIntelligenceStore) belong in Infrastructure Layer.

Responsibility:
  - Define WHAT data needs to be persisted
  - NOT HOW it's persisted (that's Infrastructure)
  - Enable swapping database implementations without affecting domain/core
"""

from locmon.repository.connection_repository import ConnectionRepository
from locmon.repository.threat_intelligence_repository import ThreatIntelligenceRepository

__all__ = [
    "ConnectionRepository",
    "ThreatIntelligenceRepository",
]
