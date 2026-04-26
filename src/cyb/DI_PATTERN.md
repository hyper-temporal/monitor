# Dependency Injection Pattern in Cyb

## Overview
The Exporter class implements proper Dependency Injection (DI) following SOLID principles. Dependencies are injected from outside, not instantiated internally.

## Architecture Decision

### Before (Anti-pattern)
```python
class Exporter:
    def __init__(self, repository=None):
        if repository is None:
            # Exporter creates its own dependency - tight coupling!
            from cyb.infrastructure import SQLiteRepository, Config
            config = Config()
            self.repository = SQLiteRepository(...)
```

**Problems:**
- Exporter creates concrete dependencies (SQLiteRepository)
- Violates Dependency Inversion Principle (SOLID-D)
- Hard to test (requires real database or mocking imports)
- Tight coupling to infrastructure details
- No way to swap implementations without modifying Exporter

### After (DI Pattern)
```python
class Exporter:
    def __init__(self, repository: ConnectionRepository) -> None:
        # Repository MUST be injected - no defaults
        if repository is None:
            raise TypeError("Exporter requires explicit repository injection")
        self.repository = repository

# Factory handles instantiation (infrastructure concern)
def create_exporter(repository: ConnectionRepository = None) -> Exporter:
    if repository is None:
        # Only the factory knows about concrete implementations
        from cyb.infrastructure.sqlite_repository import SQLiteRepository
        config = Config()
        repository = SQLiteRepository(...)
    return Exporter(repository=repository)
```

**Benefits:**
- Exporter depends only on interface (ConnectionRepository Protocol)
- Factory pattern isolates infrastructure concerns
- Easy to test: inject mock repository
- Easy to extend: swap SQLiteRepository for PostgresRepository without touching Exporter
- Follows Dependency Inversion Principle

## Layer Responsibilities

### Domain Layer (`cyb/domain/`)
- **Responsibility**: Pure domain logic (entities, value objects)
- **Exports**: Connection, Packet, ProcessInfo
- **Dependencies**: None (inbound only)

### Repository Layer (`cyb/repository/`)
- **Responsibility**: Define data access interface
- **Exports**: ConnectionRepository (Protocol)
- **Dependencies**: Domain entities
- **Note**: Interface only, no implementation

### Infrastructure Layer (`cyb/infrastructure/`)
- **Responsibility**: Technical implementations and I/O
- **Exports**: SQLiteRepository, Exporter, create_exporter, Config, etc.
- **Exports**: ConnectionRepository interface (for typing)
- **Dependencies**: Domain, Repository interfaces
- **Key**: Concrete implementations live here

### CLI Layer (`cyb/cli/`)
- **Responsibility**: User interface and dependency wiring
- **Uses**: create_exporter factory function
- **Dependencies**: Infrastructure layer (for factories)

## Usage

### CLI Export Command
```python
@cli.command()
def export(ctx, format, output):
    """Export connection history."""
    from cyb.infrastructure import create_exporter
    
    # Factory handles DI - creates exporter with default config
    exporter = create_exporter()
    data = exporter.export(format=format)
```

### Testing with Mock Repository
```python
def test_exporter_json_export():
    # Create mock repository (satisfies ConnectionRepository protocol)
    mock_repo = Mock()
    mock_repo.get_all_connections = Mock(return_value=[conn1, conn2])
    
    # Inject mock - no database needed!
    exporter = Exporter(repository=mock_repo)
    result = exporter.export(format="json")
    
    assert json.loads(result)  # Valid JSON
```

### Custom Repository Implementation
```python
# Create new implementation (e.g., PostgreSQL)
class PostgresRepository:
    def get_all_connections(self):
        # Custom implementation
        pass

# Use with Exporter - no modifications needed!
postgres_repo = PostgresRepository()
exporter = Exporter(repository=postgres_repo)
data = exporter.export(format="json")
```

## Key Design Principles

### 1. Inversion of Control (IoC)
- Exporter doesn't control repository creation
- Factory controls instantiation
- Dependencies flow inward (infrastructure → domain)

### 2. Dependency Inversion (SOLID-D)
- Exporter depends on ConnectionRepository *interface*
- Not on SQLiteRepository *implementation*
- Abstractions don't depend on details; details depend on abstractions

### 3. Single Responsibility
- **Exporter**: Format connections (export logic)
- **Factory**: Wire dependencies (infrastructure concern)
- **Repository**: Persist/retrieve data (storage concern)

### 4. Interface Segregation (SOLID-I)
- Exporter only requires get_all_connections()
- Doesn't depend on insert_connection(), delete(), etc.
- Focused, minimal interface

## Anti-patterns to Avoid

### ❌ Don't do this:
```python
# Direct instantiation - tight coupling
from cyb.infrastructure import Exporter, SQLiteRepository
repo = SQLiteRepository()
exporter = Exporter(repo)  # Works but tightly coupled

# Worse: no injection at all
exporter = Exporter()  # Now Exporter creates SQLiteRepository internally
```

### ✓ Do this instead:
```python
# Use factory (DI container)
from cyb.infrastructure import create_exporter
exporter = create_exporter()  # Factory wires dependencies

# Or explicit injection for testing
exporter = Exporter(repository=mock_repo)  # Clean, testable
```

## Future Extensions

### Add PostgreSQL Support
```python
# New infrastructure implementation (no changes to Exporter!)
class PostgresRepository:
    def get_all_connections(self):
        pass

# Wire it up
def create_exporter_postgres():
    repo = PostgresRepository(...)
    return Exporter(repository=repo)
```

### Add Caching
```python
# Decorator pattern (DI composition)
class CachedRepository:
    def __init__(self, wrapped: ConnectionRepository):
        self.wrapped = wrapped
    
    def get_all_connections(self):
        # Cache logic
        return self.wrapped.get_all_connections()

# Compose dependencies
base_repo = SQLiteRepository()
cached_repo = CachedRepository(wrapped=base_repo)
exporter = Exporter(repository=cached_repo)
```

## Testing Strategy

### Unit Tests (test_exporter_di.py)
1. **Exporter rejects None repository** → Enforces DI
2. **Exporter accepts injected repository** → Interface works
3. **Export formats work with mock repo** → No database needed
4. **Factory creates with default config** → Bootstrap works
5. **Factory uses injected dependency** → DI wiring correct

### Running Tests
```bash
cd cyb
uv run pytest tests/test_exporter_di.py -v
```

## References

- **SOLID Principles**: https://en.wikipedia.org/wiki/SOLID
- **Dependency Injection Pattern**: https://en.wikipedia.org/wiki/Dependency_injection
- **Factory Pattern**: https://refactoring.guru/design-patterns/factory-method
- **Clean Architecture**: Robert C. Martin (Uncle Bob)
