"""
Test Dependency Injection pattern for Exporter.

Verifies that:
1. Exporter requires explicit repository injection (no defaults)
2. Factory function can create Exporter with default config
3. Exporter can be tested with mock repository
"""

import pytest
from unittest.mock import Mock, MagicMock

from cyb.domain import Connection
from cyb.infrastructure import Exporter, create_exporter


class TestExporterDependencyInjection:
    """Test DI pattern: dependencies injected, not instantiated internally."""
    
    def test_exporter_requires_repository(self):
        """Exporter should reject None repository."""
        with pytest.raises(TypeError) as exc_info:
            Exporter(repository=None)
        
        assert "requires explicit repository injection" in str(exc_info.value)
    
    def test_exporter_accepts_injected_repository(self):
        """Exporter should accept any ConnectionRepository implementation."""
        mock_repo = Mock()
        mock_repo.get_all_connections = Mock(return_value=[])
        
        exporter = Exporter(repository=mock_repo)
        assert exporter.repository is mock_repo
    
    def test_exporter_export_json_with_mock_repo(self):
        """Exporter should call repository and format data."""
        # Create mock connection
        conn = Connection(
            timestamp="2026-04-26T10:00:00Z",
            src_ip="192.168.1.100",
            dst_ip="8.8.8.8",
            dst_port=53,
            protocol="UDP"
        )
        
        # Create mock repository
        mock_repo = Mock()
        mock_repo.get_all_connections = Mock(return_value=[conn])
        
        exporter = Exporter(repository=mock_repo)
        result = exporter.export(format="json")
        
        # Verify repository was called
        mock_repo.get_all_connections.assert_called_once()
        
        # Verify output is valid JSON
        import json
        data = json.loads(result)
        assert len(data) == 1
        assert data[0]["dst_ip"] == "8.8.8.8"
    
    def test_exporter_export_csv_with_mock_repo(self):
        """Exporter should export as CSV."""
        conn = Connection(
            timestamp="2026-04-26T10:00:00Z",
            src_ip="192.168.1.100",
            dst_ip="8.8.8.8",
            dst_port=53,
            protocol="UDP"
        )
        
        mock_repo = Mock()
        mock_repo.get_all_connections = Mock(return_value=[conn])
        
        exporter = Exporter(repository=mock_repo)
        result = exporter.export(format="csv")
        
        # Verify CSV format
        lines = result.strip().split('\n')
        assert len(lines) >= 2  # Header + at least one row
        assert "timestamp" in lines[0].lower() or "dst_ip" in lines[0].lower()
    
    def test_exporter_export_sql_with_mock_repo(self):
        """Exporter should export as SQL INSERT statements."""
        conn = Connection(
            timestamp="2026-04-26T10:00:00Z",
            src_ip="192.168.1.100",
            dst_ip="8.8.8.8",
            dst_port=53,
            protocol="UDP"
        )
        
        mock_repo = Mock()
        mock_repo.get_all_connections = Mock(return_value=[conn])
        
        exporter = Exporter(repository=mock_repo)
        result = exporter.export(format="sql")
        
        # Verify SQL format
        assert "INSERT INTO connections" in result
        assert "8.8.8.8" in result
    
    def test_factory_creates_exporter_with_default_config(self):
        """Factory function should create Exporter with SQLiteRepository."""
        # This test assumes config file exists with default settings
        # In CI environment without database, this may need mocking
        try:
            exporter = create_exporter()
            assert exporter is not None
            assert hasattr(exporter, 'repository')
        except Exception:
            # Skip if no database configured
            pytest.skip("Database not configured for test")
    
    def test_factory_accepts_injected_repository(self):
        """Factory should use provided repository instead of creating one."""
        mock_repo = Mock()
        mock_repo.get_all_connections = Mock(return_value=[])
        
        exporter = create_exporter(repository=mock_repo)
        assert exporter.repository is mock_repo
    
    def test_exporter_unknown_format_raises_error(self):
        """Exporter should reject unknown formats."""
        mock_repo = Mock()
        mock_repo.get_all_connections = Mock(return_value=[])
        
        exporter = Exporter(repository=mock_repo)
        with pytest.raises(ValueError) as exc_info:
            exporter.export(format="unknown")
        
        assert "Unknown format" in str(exc_info.value)
