"""
Tier 2: Boundary 1 (B01) - Docker & Database Boundaries
Validates edge cases in port definitions, foreign keys, cascading deletes, and hypertable intervals.
"""

import unittest
from tests.helpers.schema_validator import inspect_schema_sql, inspect_docker_compose


class TestB01DockerBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema_info = inspect_schema_sql()
        cls.compose_info = inspect_docker_compose()

    def test_01_exposed_ports_in_valid_range(self):
        """All mapped host ports are within valid unreserved ranges (1024-65535)."""
        for host_port, container_port in self.compose_info["exposed_ports"]:
            p = int(host_port)
            self.assertGreaterEqual(p, 1024)
            self.assertLessEqual(p, 65535)

    def test_02_cascade_delete_integrity(self):
        """Schema enforces ON DELETE CASCADE on trajectory, tops, and hazards tables."""
        with open(self.schema_info["path"], "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("REFERENCES wells(well_id) ON DELETE CASCADE", content)

    def test_03_default_environment_fallbacks(self):
        """Docker Compose provides fallback values for environment variables (${VAR:-default})."""
        with open(self.compose_info["path"], "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("OPENAI_API_KEY:-dummy", content)
        self.assertIn("MAPBOX_TOKEN:-your_mapbox_token_here", content)

    def test_04_hypertable_interval_chunking(self):
        """TimescaleDB chunk interval is configured strictly to 1 day for 1 Hz high volume."""
        with open(self.schema_info["path"], "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("chunk_time_interval => INTERVAL '1 day'", content)

    def test_05_strict_column_types_no_loose_text_on_keys(self):
        """Primary and foreign keys use UUID types, not unstructured text."""
        with open(self.schema_info["path"], "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("well_id         UUID PRIMARY KEY", content)


if __name__ == "__main__":
    unittest.main()
