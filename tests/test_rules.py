"""
Tests for rule matching engine.
Uses mocks only — no external fixtures or data.
"""

import unittest
from unittest.mock import Mock
from backend.capture import Connection
from backend.rules import RuleEngine


class TestRuleEngine(unittest.TestCase):
    """Test rule matching."""

    def test_no_rules_returns_pending(self):
        """No rules means pending status."""
        engine = RuleEngine(rules=[])
        conn = Connection(
            timestamp="2026-04-25T12:00:00",
            src_ip="192.168.1.100",
            dst_ip="8.8.8.8",
            dst_port=443,
            protocol="TCP",
        )
        self.assertEqual(engine.evaluate(conn), "pending")

    def test_match_by_dst_ip(self):
        """Match a connection by destination IP."""
        rules = [
            {"action": "block", "dst_ip": "8.8.8.8", "dst_port": None, "exe": None},
        ]
        engine = RuleEngine(rules=rules)
        conn = Connection(
            timestamp="2026-04-25T12:00:00",
            src_ip="192.168.1.100",
            dst_ip="8.8.8.8",
            dst_port=443,
            protocol="TCP",
        )
        self.assertEqual(engine.evaluate(conn), "block")

    def test_no_match_different_ip(self):
        """No match for different destination IP."""
        rules = [
            {"action": "block", "dst_ip": "8.8.8.8", "dst_port": None, "exe": None},
        ]
        engine = RuleEngine(rules=rules)
        conn = Connection(
            timestamp="2026-04-25T12:00:00",
            src_ip="192.168.1.100",
            dst_ip="1.1.1.1",
            dst_port=443,
            protocol="TCP",
        )
        self.assertEqual(engine.evaluate(conn), "pending")

    def test_match_by_port(self):
        """Match a connection by destination port."""
        rules = [
            {"action": "allow", "dst_ip": None, "dst_port": 443, "exe": None},
        ]
        engine = RuleEngine(rules=rules)
        conn = Connection(
            timestamp="2026-04-25T12:00:00",
            src_ip="192.168.1.100",
            dst_ip="8.8.8.8",
            dst_port=443,
            protocol="TCP",
        )
        self.assertEqual(engine.evaluate(conn), "allow")

    def test_match_by_exe(self):
        """Match a connection by executable."""
        rules = [
            {"action": "allow", "dst_ip": None, "dst_port": None, "exe": "/usr/bin/chrome"},
        ]
        engine = RuleEngine(rules=rules)
        conn = Connection(
            timestamp="2026-04-25T12:00:00",
            src_ip="192.168.1.100",
            dst_ip="8.8.8.8",
            dst_port=443,
            protocol="TCP",
            exe="/usr/bin/chrome",
        )
        self.assertEqual(engine.evaluate(conn), "allow")

    def test_match_combined_criteria(self):
        """Match with multiple criteria (AND logic)."""
        rules = [
            {"action": "block", "dst_ip": "8.8.8.8", "dst_port": 53, "exe": None},
        ]
        engine = RuleEngine(rules=rules)

        # Matches both IP and port
        conn1 = Connection(
            timestamp="2026-04-25T12:00:00",
            src_ip="192.168.1.100",
            dst_ip="8.8.8.8",
            dst_port=53,
            protocol="UDP",
        )
        self.assertEqual(engine.evaluate(conn1), "block")

        # Matches IP but not port
        conn2 = Connection(
            timestamp="2026-04-25T12:00:00",
            src_ip="192.168.1.100",
            dst_ip="8.8.8.8",
            dst_port=443,
            protocol="TCP",
        )
        self.assertEqual(engine.evaluate(conn2), "pending")

    def test_first_matching_rule_wins(self):
        """First matching rule determines the action."""
        rules = [
            {"action": "allow", "dst_ip": "8.8.8.8", "dst_port": None, "exe": None},
            {"action": "block", "dst_ip": "8.8.8.8", "dst_port": None, "exe": None},
        ]
        engine = RuleEngine(rules=rules)
        conn = Connection(
            timestamp="2026-04-25T12:00:00",
            src_ip="192.168.1.100",
            dst_ip="8.8.8.8",
            dst_port=443,
            protocol="TCP",
        )
        self.assertEqual(engine.evaluate(conn), "allow")  # First match


if __name__ == "__main__":
    unittest.main()
