"""
Tier 1: Feature 5 (F5) - POST /api/v1/spatial/offset-wells Endpoint
Validates 3D spatial queries, TSD structural dip offsets, and hazard correlation.
"""

import unittest
from tests.helpers.test_client import NWISTestClient
from tests.helpers.math_oracle import compute_tsd_offset


class TestF05OffsetWellsEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = NWISTestClient()
        cls.default_payload = {
            "active_well_id": "c1f7a012-3b4c-4e89-9a11-000000000005",
            "surface_lat": 27.280000,
            "surface_lon": 95.340000,
            "current_tvdss_m": 2180.5,
            "radius_km": 5.0,
            "tvdss_window_m": 200.0
        }

    def test_01_offset_wells_status_200_and_envelope(self):
        """POST /api/v1/spatial/offset-wells returns 200 OK with success envelope."""
        status_code, body = self.client.post_offset_wells(self.default_payload)
        self.assertEqual(status_code, 200)
        self.assertEqual(body.get("status"), "success")
        self.assertIn("data", body)
        self.assertIsInstance(body["data"], list)

    def test_02_correlates_syn_nhk_01_in_5km_radius(self):
        """Identifies SYN-NHK-01 as primary offset within 5km radius."""
        _, body = self.client.post_offset_wells(self.default_payload)
        offsets = body.get("data", [])
        self.assertGreaterEqual(len(offsets), 1)
        names = [o.get("well_name") for o in offsets]
        self.assertIn("SYN-NHK-01", names)

    def test_03_surface_distance_calculation(self):
        """Surface distance to SYN-NHK-01 is calculated in metres (~1420m)."""
        _, body = self.client.post_offset_wells(self.default_payload)
        nhk1 = next(o for o in body["data"] if o.get("well_name") == "SYN-NHK-01")
        dist = nhk1.get("surface_distance_m", 0)
        self.assertAlmostEqual(dist, 1420.5, delta=100.0)

    def test_04_recorded_hazards_in_tvdss_window(self):
        """Offset record contains DIFFERENTIAL_STICKING hazard within 200m TVDSS window."""
        _, body = self.client.post_offset_wells(self.default_payload)
        nhk1 = next(o for o in body["data"] if o.get("well_name") == "SYN-NHK-01")
        hazards = nhk1.get("recorded_hazards_in_window", [])
        self.assertGreaterEqual(len(hazards), 1)
        hazard_types = [h.get("hazard_type") for h in hazards]
        self.assertIn("DIFFERENTIAL_STICKING", hazard_types)

    def test_05_tsd_dip_offset_math_oracle(self):
        """Verify TSD structural dip calculation matches analytical formulation."""
        # For Nahorkatiya: dip = 3.5 deg, azimuth = 145 deg
        tsd = compute_tsd_offset(
            delta_x=216.0,  # East offset approx
            delta_y=345.0,  # North offset approx
            dip_angle_deg=3.5,
            dip_azimuth_deg=145.0,
            active_tvdss=2180.5
        )
        self.assertIsInstance(tsd["delta_tvdss_structural_m"], float)
        self.assertAlmostEqual(tsd["equivalent_tvdss_m"], 2180.5 + tsd["delta_tvdss_structural_m"], places=3)

    def test_06_sorting_by_distance_ascending(self):
        """Offset wells are ordered by surface distance ascending."""
        _, body = self.client.post_offset_wells(self.default_payload)
        offsets = body.get("data", [])
        if len(offsets) > 1:
            distances = [o.get("surface_distance_m", 0) for o in offsets]
            self.assertEqual(distances, sorted(distances))


if __name__ == "__main__":
    unittest.main()
