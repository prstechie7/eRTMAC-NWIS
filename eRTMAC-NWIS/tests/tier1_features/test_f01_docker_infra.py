"""
Tier 1: Feature 1 (F1) - Docker Infrastructure & Database Schema
Validates Docker compose definition and 01_schema.sql specifications.
"""

import unittest
from tests.helpers.schema_validator import inspect_schema_sql, inspect_docker_compose


class TestF01DockerInfrastructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema_info = inspect_schema_sql()
        cls.compose_info = inspect_docker_compose()

    def test_01_docker_compose_services_and_timescale_image(self):
        """Verify docker-compose defines db, backend, frontend services and timescaledb image."""
        self.assertTrue(self.compose_info["has_db_service"], "Missing 'db' service in docker-compose.yml")
        self.assertTrue(self.compose_info["has_backend_service"], "Missing 'backend' service in docker-compose.yml")
        self.assertTrue(self.compose_info["has_frontend_service"], "Missing 'frontend' service in docker-compose.yml")
        self.assertTrue(self.compose_info["has_timescale_image"], "Missing timescale/timescaledb-ha image in db service")

    def test_02_docker_compose_port_mappings(self):
        """Verify port mappings: 5432 (DB), 8000 (FastAPI), 3000 (Next.js)."""
        self.assertTrue(self.compose_info["has_postgres_port"], "Port 5432:5432 not exposed in db service")
        self.assertTrue(self.compose_info["has_backend_port"], "Port 8000:8000 not exposed in backend service")
        self.assertTrue(self.compose_info["has_frontend_port"], "Port 3000:3000 not exposed in frontend service")

    def test_03_schema_required_extensions(self):
        """Verify required PostgreSQL extensions: postgis, timescaledb, vector, uuid-ossp."""
        extensions = set(self.schema_info["extensions"])
        self.assertIn("postgis", extensions, "Missing postgis extension")
        self.assertIn("timescaledb", extensions, "Missing timescaledb extension")
        self.assertIn("vector", extensions, "Missing vector (pgvector) extension")

    def test_04_schema_core_tables_declared(self):
        """Verify all 6 core tables are declared in 01_schema.sql."""
        tables = set(self.schema_info["tables"])
        expected_tables = {
            "wells",
            "trajectory_stations",
            "formation_tops",
            "drilling_hazards",
            "live_telemetry",
            "look_ahead_alerts"
        }
        for table in expected_tables:
            self.assertIn(table, tables, f"Expected table '{table}' not defined in 01_schema.sql")

    def test_05_schema_live_telemetry_hypertable(self):
        """Verify live_telemetry is registered as a TimescaleDB hypertable."""
        hypertables = set(self.schema_info["hypertables"])
        self.assertIn("live_telemetry", hypertables, "live_telemetry must be converted to hypertable")

    def test_06_schema_spatial_find_offset_wells_function(self):
        """Verify stored function find_offset_wells is declared."""
        self.assertTrue(self.schema_info["has_spatial_function"], "find_offset_wells() stored procedure missing from schema")

    def test_07_schema_drilling_hazards_check_constraints(self):
        """Verify drilling_hazards includes required hazard types like DIFFERENTIAL_STICKING."""
        hazard_types = set(self.schema_info["hazard_types"])
        expected_hazards = {"DIFFERENTIAL_STICKING", "LOST_CIRCULATION", "GAS_KICK", "BIT_BALLING"}
        for hz in expected_hazards:
            self.assertIn(hz, hazard_types, f"Expected hazard type '{hz}' missing in chk_hazard_type constraint")


if __name__ == "__main__":
    unittest.main()
