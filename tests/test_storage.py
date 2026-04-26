"""
Tests for SQLite storage.
Uses inline mock data only — no external fixtures or data.
"""

import unittest
from backend.core import Connection
from backend.repository import SQLiteRepository


# Inline test data
TEST_IPS = {
    "local": "192.168.1.100",
    "google_dns": "8.8.8.8",
    "cloudflare_dns": "1.1.1.1",
}

TEST_PORTS = {
    "http": 80,
    "https": 443,
    "dns": 53,
}

TEST_EXES = {
    "chrome": "/usr/bin/chrome",
    "firefox": "/usr/bin/firefox",
}


class TestSQLiteRepository(unittest.TestCase):
    """Test Storage operations."""

    def setUp(self):
        """Create an in-memory database for testing."""
        self.storage = SQLiteRepository(db_path=":memory:")

    def test_insert_and_retrieve_connection(self):
        """Insert and retrieve a connection."""
        conn = Connection(
            timestamp="2026-04-25T12:00:00",
            src_ip=TEST_IPS["local"],
            dst_ip=TEST_IPS["google_dns"],
            dst_port=TEST_PORTS["https"],
            protocol="TCP",
        )
        conn_id = self.storage.insert_connection(conn)
        self.assertGreater(conn_id, 0)

        retrieved = self.storage.get_connections(limit=1)
        self.assertEqual(len(retrieved), 1)
        self.assertEqual(retrieved[0].dst_ip, TEST_IPS["google_dns"])

    def test_insert_multiple_connections(self):
        """Insert multiple connections and retrieve in order."""
        for i in range(5):
            conn = Connection(
                timestamp=f"2026-04-25T12:0{i}:00",
                src_ip=TEST_IPS["local"],
                dst_ip=f"8.8.8.{i}",
                dst_port=TEST_PORTS["https"] + i,
                protocol="TCP",
            )
            self.storage.insert_connection(conn)

        conns = self.storage.get_connections(limit=10)
        self.assertEqual(len(conns), 5)

    def test_get_connection_by_ip(self):
        """Query connections by destination IP."""
        for i in range(3):
            conn = Connection(
                timestamp=f"2026-04-25T12:0{i}:00",
                src_ip=TEST_IPS["local"],
                dst_ip=TEST_IPS["google_dns"] if i < 2 else TEST_IPS["cloudflare_dns"],
                dst_port=TEST_PORTS["https"],
                protocol="TCP",
            )
            self.storage.insert_connection(conn)

        by_ip = self.storage.get_connection_by_ip(TEST_IPS["google_dns"])
        self.assertEqual(len(by_ip), 2)
        self.assertTrue(all(c.dst_ip == TEST_IPS["google_dns"] for c in by_ip))

    def test_get_connection_by_exe(self):
        """Query connections by executable."""
        for i in range(3):
            conn = Connection(
                timestamp=f"2026-04-25T12:0{i}:00",
                src_ip=TEST_IPS["local"],
                dst_ip=TEST_IPS["google_dns"],
                dst_port=TEST_PORTS["https"],
                protocol="TCP",
                exe=TEST_EXES["chrome"] if i < 2 else TEST_EXES["firefox"],
            )
            self.storage.insert_connection(conn)

        by_exe = self.storage.get_connection_by_exe(TEST_EXES["chrome"])
        self.assertEqual(len(by_exe), 2)
        self.assertTrue(all(c.exe == TEST_EXES["chrome"] for c in by_exe))


    def test_update_connection_status(self):
        """Update connection status."""
        conn = Connection(
            timestamp="2026-04-25T12:00:00",
            src_ip=TEST_IPS["local"],
            dst_ip=TEST_IPS["google_dns"],
            dst_port=TEST_PORTS["https"],
            protocol="TCP",
        )
        conn_id = self.storage.insert_connection(conn)
        self.assertTrue(self.storage.update_connection_status(conn_id, "blocked"))

        updated = self.storage.get_connections(limit=1)
        self.assertEqual(updated[0].status, "blocked")


if __name__ == "__main__":
    unittest.main()
