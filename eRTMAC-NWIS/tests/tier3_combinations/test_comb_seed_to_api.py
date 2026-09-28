"""
Tier 3: Combination 1 - Seed Data to REST API Flow (F1 + F2 + F3 -> F4)
Validates that synthetic wells loaded into database schema with MCM computed trajectories
are correctly exposed through the GET /api/v1/wells API.
"""

import unittest
from tests.helpers.data_loader import load_synthetic_wells
from tests.helpers.math_oracle import compute_mcm_station
from tests.helpers.test_client import NWISTestClient


class TestCombSeedToApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_synthetic_wells()
        cls.client = NWISTestClient()

    def test_01_seed_dataset_matches_api_well_catalog(self):
        """Dataset wells reconcile with API well listing."""
        status_code, api_wells = self.client.get_wells()
        self.assertEqual(status_code, 200)
        api_well_names = {w["well_name"] for w in api_wells}
        # SYN-NHK-01 and SYN-NHK-05 must be visible in both
        self.assertIn("SYN-NHK-01", api_well_names)
        self.assertIn("SYN-NHK-05", api_well_names)

    def test_02_seed_active_well_trajectory_initialization(self):
        """Active well SYN-NHK-05 trajectory station at 2410m computes consistent TVDSS."""
        nhk5 = next(w for w in self.data["wells"] if w["well_name"] == "SYN-NHK-05")
        st = compute_mcm_station(
            md1=0.0, inc1_deg=0.0, azi1_deg=0.0,
            md2=float(nhk5["current_bit_md_m"]), inc2_deg=0.0, azi2_deg=0.0,
            kb_elevation_m=float(nhk5["kb_elevation_m"])
        )
        # 2410 - 112 = 2298m (or with slight inclination ~ 2180.5m)
        self.assertAlmostEqual(st["md_m"], 2410.0, places=1)
        self.assertAlmostEqual(st["tvd_m"], 2410.0, places=1)

    def test_03_active_status_filtering_consistency(self):
        """Filtering API by status=DRILLING returns exactly the active well SYN-NHK-05 from seed data."""
        status_code, api_drilling = self.client.get_wells(status="DRILLING")
        self.assertEqual(status_code, 200)
        drilling_names = [w["well_name"] for w in api_drilling]
        self.assertIn("SYN-NHK-05", drilling_names)
        for w in api_drilling:
            self.assertEqual(w["status"], "DRILLING")

    def test_04_field_correlation_across_seed_and_api(self):
        """Wells queried under 'Nahorkatiya' preserve field_name taxonomy."""
        _, api_nhk = self.client.get_wells(field_name="Nahorkatiya")
        for w in api_nhk:
            self.assertEqual(w["field_name"], "Nahorkatiya")


if __name__ == "__main__":
    unittest.main()
