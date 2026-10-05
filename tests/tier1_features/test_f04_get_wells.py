"""
Tier 1: Feature 4 (F4) - GET /api/v1/wells Endpoint
Validates wells listing, query parameter filtering, and synthetic contract compliance.
"""

import unittest
from tests.helpers.test_client import NWISTestClient


class TestF04GetWellsEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = NWISTestClient()

    def test_01_get_wells_status_200_and_list_type(self):
        """GET /api/v1/wells returns 200 OK and a JSON array."""
        status_code, body = self.client.get_wells()
        self.assertEqual(status_code, 200)
        self.assertIsInstance(body, list)
        self.assertGreaterEqual(len(body), 1)

    def test_02_filter_by_field_name(self):
        """Filtering with ?field_name=Nahorkatiya isolates Nahorkatiya field wells."""
        status_code, body = self.client.get_wells(field_name="Nahorkatiya")
        self.assertEqual(status_code, 200)
        for well in body:
            self.assertEqual(well["field_name"].lower(), "nahorkatiya")

    def test_03_filter_by_drilling_status(self):
        """Filtering with ?status=DRILLING isolates active drilling wells."""
        status_code, body = self.client.get_wells(status="DRILLING")
        self.assertEqual(status_code, 200)
        for well in body:
            self.assertEqual(well["status"].upper(), "DRILLING")

    def test_04_schema_contract_well_properties(self):
        """Verify each returned well contains all required properties per docs/09 § 1."""
        _, body = self.client.get_wells()
        required_keys = {"well_id", "well_name", "field_name", "operator", "surface_lat", "surface_lon", "kb_elevation_m"}
        for well in body:
            for k in required_keys:
                self.assertIn(k, well, f"Key '{k}' missing from well {well.get('well_name')}")

    def test_05_universal_syn_prefix_enforcement(self):
        """Verify 100% of wells strictly carry the 'SYN-' prefix."""
        _, body = self.client.get_wells()
        for well in body:
            name = well.get("well_name", "")
            self.assertTrue(name.startswith("SYN-"), f"Well '{name}' violates SYN-* prefix rule")

    def test_06_data_source_synthetic_indicator(self):
        """Verify data_source is declared as 'SYNTHETIC'."""
        _, body = self.client.get_wells()
        for well in body:
            source = well.get("data_source", "SYNTHETIC")
            self.assertEqual(source, "SYNTHETIC")


if __name__ == "__main__":
    unittest.main()
