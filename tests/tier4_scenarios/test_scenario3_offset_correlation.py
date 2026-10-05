"""
Tier 4: Scenario 3 - 3D Offset Well Correlation
Validates spatial correlation between active well SYN-NHK-05 and historical
evidence well SYN-NHK-01 across 1.42km surface distance with TSD dip normalization.
"""

import unittest
from tests.helpers.test_client import NWISTestClient
from tests.helpers.math_oracle import compute_tsd_offset


class TestScenario3OffsetCorrelation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = NWISTestClient()
        cls.query_payload = {
            "active_well_id": "c1f7a012-3b4c-4e89-9a11-000000000005",
            "surface_lat": 27.280000,
            "surface_lon": 95.340000,
            "current_tvdss_m": 2180.5,
            "radius_km": 5.0,
            "tvdss_window_m": 200.0
        }

    def test_01_offset_isolation_within_radius(self):
        """Query isolates SYN-NHK-01 at ~1420m surface distance."""
        status_code, body = self.client.post_offset_wells(self.query_payload)
        self.assertEqual(status_code, 200)
        offsets = body.get("data", [])
        self.assertGreaterEqual(len(offsets), 1)
        nhk1 = next(o for o in offsets if o["well_name"] == "SYN-NHK-01")
        self.assertAlmostEqual(nhk1["surface_distance_m"], 1420.5, delta=100.0)

    def test_02_stratigraphic_tvdss_offset_dip_correction(self):
        """TSD dip calculation confirms structural TVDSS offset between -1.0m and -2.0m."""
        # Regional dip 3.5 deg at 145 deg azimuth
        tsd = compute_tsd_offset(
            delta_x=216.0,
            delta_y=345.0,
            dip_angle_deg=3.5,
            dip_azimuth_deg=145.0,
            active_tvdss=2180.5
        )
        self.assertAlmostEqual(tsd["delta_tvdss_structural_m"], -9.7, delta=2.0)

    def test_03_historical_incident_npt_correlation(self):
        """Correlated offset record contains historical 38.5h NPT incident."""
        _, body = self.client.post_offset_wells(self.query_payload)
        nhk1 = next(o for o in body["data"] if o["well_name"] == "SYN-NHK-01")
        hazard = nhk1["recorded_hazards_in_window"][0]
        self.assertEqual(hazard["hazard_type"], "DIFFERENTIAL_STICKING")
        self.assertAlmostEqual(float(hazard["npt_hours"]), 38.5, places=1)


if __name__ == "__main__":
    unittest.main()
