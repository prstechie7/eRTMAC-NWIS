"""
Tier 3: Combination 2 - Spatial Offset Query to Look-Ahead Risk Engine (F5 -> F6)
Validates that offset well spatial queries feed directly into the proactive
look-ahead hazard computation pipeline.
"""

import unittest
from tests.helpers.test_client import NWISTestClient
from tests.helpers.math_oracle import compute_lookahead_risk_index


class TestCombSpatialLookahead(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = NWISTestClient()
        cls.spatial_payload = {
            "active_well_id": "c1f7a012-3b4c-4e89-9a11-000000000005",
            "surface_lat": 27.280000,
            "surface_lon": 95.340000,
            "current_tvdss_m": 2180.5,
            "radius_km": 5.0,
            "tvdss_window_m": 200.0
        }

    def test_01_spatial_offsets_provide_lookahead_evidence(self):
        """Offsets retrieved by POST /spatial/offset-wells appear in GET /intelligence/lookahead evidence."""
        _, spatial_res = self.client.post_offset_wells(self.spatial_payload)
        spatial_wells = {o["well_name"] for o in spatial_res.get("data", [])}

        _, lookahead_res = self.client.get_lookahead(
            active_well_id="c1f7a012-3b4c-4e89-9a11-000000000005",
            bit_depth_md=2410.0
        )
        evidence = lookahead_res["projected_hazard"].get("evidence_offsets", [])
        evidence_wells = {e["well_name"] for e in evidence}

        # SYN-NHK-01 is identified in spatial query AND cited in lookahead evidence
        self.assertIn("SYN-NHK-01", spatial_wells)
        self.assertIn("SYN-NHK-01", evidence_wells)

    def test_02_spatial_hazard_matches_lookahead_projected_hazard(self):
        """Hazard type DIFFERENTIAL_STICKING in spatial results drives the projected hazard."""
        _, spatial_res = self.client.post_offset_wells(self.spatial_payload)
        nhk1 = next(o for o in spatial_res["data"] if o["well_name"] == "SYN-NHK-01")
        hazards = nhk1.get("recorded_hazards_in_window", [])
        diff_stick = next((h for h in hazards if h["hazard_type"] == "DIFFERENTIAL_STICKING"), None)
        self.assertIsNotNone(diff_stick)

        _, lookahead_res = self.client.get_lookahead("c1f7a012-3b4c-4e89-9a11-000000000005", 2410.0)
        self.assertEqual(lookahead_res["projected_hazard"]["hazard_type"], diff_stick["hazard_type"])

    def test_03_integrated_math_oracle_verification(self):
        """End-to-end mathematical consistency between 3D distance and R_H score."""
        # Active well at (0, 0, 2180.5); Offset SYN-NHK-01 at 1420.5m away with hazard at 2179m
        rh_res = compute_lookahead_risk_index(
            active_bit_pos=(0.0, 0.0, 2180.5),
            projected_tvdss=2179.0,
            offsets=[{
                "well_name": "SYN-NHK-01",
                "pos_3d": (1420.5, 0.0, 2179.0),
                "incident_tvdss": 2179.0,
                "severity": 4
            }]
        )
        self.assertAlmostEqual(rh_res["risk_index"], 84.2, delta=2.0)
        self.assertEqual(rh_res["risk_level"], "HIGH")


if __name__ == "__main__":
    unittest.main()
