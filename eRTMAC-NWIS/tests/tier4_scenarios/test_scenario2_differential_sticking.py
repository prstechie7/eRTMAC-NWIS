"""
Tier 4: Scenario 2 - Proactive Differential Sticking Alert Escalation
Simulates the live detection of differential sticking conditions as bit approaches
the depleted Upper Tipam thief zone under 1,120 psi overbalance.
"""

import unittest
from tests.helpers.test_client import NWISTestClient
from tests.helpers.math_oracle import compute_overbalance_pressure, compute_lookahead_risk_index


class TestScenario2DifferentialSticking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = NWISTestClient()
        cls.active_well_id = "c1f7a012-3b4c-4e89-9a11-000000000005"
        cls.bit_depth_md = 2410.0

    def test_01_overbalance_pressure_physics_derivation(self):
        """Mud density 1.18 SG vs 0.88 SG pore pressure at 2179m TVD yields ~1120 psi."""
        # Static overbalance at 1.18 SG mud weight
        dp_static = compute_overbalance_pressure(mud_weight_sg=1.18, pore_pressure_sg=0.88, tvd_m=2179.0)
        self.assertAlmostEqual(dp_static, 930.7, delta=20.0)

        # Dynamic overbalance with circulating ECD (1.24 SG) exceeds 1,120 psi per DDR report
        dp_dynamic = compute_overbalance_pressure(mud_weight_sg=1.241, pore_pressure_sg=0.88, tvd_m=2179.0)
        self.assertAlmostEqual(dp_dynamic, 1120.0, delta=20.0)

    def test_02_lookahead_alert_payload_verification(self):
        """GET /lookahead triggers HIGH alert with R_H=84.2 and primary hazard DIFFERENTIAL_STICKING."""
        status_code, body = self.client.get_lookahead(self.active_well_id, self.bit_depth_md)
        self.assertEqual(status_code, 200)
        proj = body["projected_hazard"]
        self.assertEqual(proj["hazard_type"], "DIFFERENTIAL_STICKING")
        self.assertEqual(proj["risk_level"], "HIGH")
        self.assertAlmostEqual(proj["risk_index"], 84.2, places=1)
        self.assertAlmostEqual(proj["distance_to_hazard_m"], 38.5, places=1)

    def test_03_four_step_actionable_mitigations_verified(self):
        """Alert provides the 4 specific mitigation steps required by Oil India standards."""
        _, body = self.client.get_lookahead(self.active_well_id, self.bit_depth_md)
        mitigations = body["projected_hazard"]["actionable_mitigation"]
        self.assertEqual(len(mitigations), 4)
        # Check critical operational parameters
        self.assertTrue(any("< 90 seconds" in m for m in mitigations))
        self.assertTrue(any("40 bbls" in m for m in mitigations))
        self.assertTrue(any(">40 RPM" in m for m in mitigations))


if __name__ == "__main__":
    unittest.main()
