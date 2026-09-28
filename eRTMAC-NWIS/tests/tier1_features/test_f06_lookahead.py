"""
Tier 1: Feature 6 (F6) - GET /api/v1/intelligence/lookahead Endpoint
Validates 75m look-ahead hazard prediction, R_H risk index, and mitigations.
"""

import unittest
from tests.helpers.test_client import NWISTestClient
from tests.helpers.math_oracle import compute_lookahead_risk_index


class TestF06LookaheadEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = NWISTestClient()
        cls.active_well_id = "c1f7a012-3b4c-4e89-9a11-000000000005"
        cls.bit_depth_md = 2410.0

    def test_01_lookahead_status_200_and_structure(self):
        """GET /api/v1/intelligence/lookahead returns 200 OK with expected structure."""
        status_code, body = self.client.get_lookahead(self.active_well_id, self.bit_depth_md)
        self.assertEqual(status_code, 200)
        self.assertIn("active_well", body)
        self.assertIn("lookahead_window_m", body)
        self.assertIn("projected_hazard", body)

    def test_02_lookahead_window_size(self):
        """Lookahead window is strictly 75.0 metres."""
        _, body = self.client.get_lookahead(self.active_well_id, self.bit_depth_md)
        self.assertAlmostEqual(float(body.get("lookahead_window_m", 0)), 75.0, places=1)

    def test_03_risk_index_and_level_evaluation(self):
        """SYN-NHK-05 at 2410m evaluates to R_H ~ 84.2 and HIGH risk level."""
        _, body = self.client.get_lookahead(self.active_well_id, self.bit_depth_md)
        hazard = body["projected_hazard"]
        self.assertAlmostEqual(float(hazard.get("risk_index", 0)), 84.2, delta=2.0)
        self.assertEqual(hazard.get("risk_level"), "HIGH")

    def test_04_primary_hazard_and_distance(self):
        """Identifies DIFFERENTIAL_STICKING at distance ~ 38.5m ahead (projected 2448.5m MD)."""
        _, body = self.client.get_lookahead(self.active_well_id, self.bit_depth_md)
        hazard = body["projected_hazard"]
        self.assertEqual(hazard.get("hazard_type"), "DIFFERENTIAL_STICKING")
        self.assertAlmostEqual(float(hazard.get("distance_to_hazard_m", 0)), 38.5, places=1)
        self.assertAlmostEqual(float(hazard.get("projected_depth_md_m", 0)), 2448.5, places=1)

    def test_05_expected_overbalance_pressure(self):
        """Overbalance pressure across depleted sand interval is ~ 1120 psi."""
        _, body = self.client.get_lookahead(self.active_well_id, self.bit_depth_md)
        hazard = body["projected_hazard"]
        self.assertAlmostEqual(float(hazard.get("expected_overbalance_psi", 0)), 1120.0, places=1)

    def test_06_evidence_offset_wells(self):
        """Evidence offsets cite SYN-NHK-01 with 38.5h historical NPT."""
        _, body = self.client.get_lookahead(self.active_well_id, self.bit_depth_md)
        evidence = body["projected_hazard"].get("evidence_offsets", [])
        self.assertGreaterEqual(len(evidence), 1)
        nhk1 = next((e for e in evidence if e.get("well_name") == "SYN-NHK-01"), None)
        self.assertIsNotNone(nhk1, "SYN-NHK-01 must be cited as evidence")
        self.assertAlmostEqual(float(nhk1.get("historical_npt_hours", 0)), 38.5, places=1)

    def test_07_actionable_mitigations_list(self):
        """Provides 4 specific actionable mitigations (pipe rotation, stationary limit, etc.)."""
        _, body = self.client.get_lookahead(self.active_well_id, self.bit_depth_md)
        mitigations = body["projected_hazard"].get("actionable_mitigation", [])
        self.assertGreaterEqual(len(mitigations), 4)
        combined_text = " ".join(mitigations).lower()
        self.assertIn("90 seconds", combined_text)
        self.assertTrue("lubricat" in combined_text or "anti-sticking" in combined_text)


if __name__ == "__main__":
    unittest.main()
