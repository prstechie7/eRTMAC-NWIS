"""
Tier 1: Feature 11 (F11) - Look-Ahead Alert Card
Validates component state, hazard data mapping, and mitigation display.
"""

import unittest
from tests.helpers.test_client import NWISTestClient


class TestF11AlertCard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = NWISTestClient()
        _, cls.lookahead_data = cls.client.get_lookahead(
            active_well_id="c1f7a012-3b4c-4e89-9a11-000000000005",
            bit_depth_md=2410.0
        )

    def test_01_risk_badge_value_and_level(self):
        """Alert card binds risk index (84.2) and severity label (HIGH)."""
        proj = self.lookahead_data["projected_hazard"]
        self.assertAlmostEqual(float(proj["risk_index"]), 84.2, places=1)
        self.assertEqual(proj["risk_level"], "HIGH")

    def test_02_distance_to_hazard_display(self):
        """Displays distance ahead: +38.5m."""
        proj = self.lookahead_data["projected_hazard"]
        self.assertAlmostEqual(float(proj["distance_to_hazard_m"]), 38.5, places=1)

    def test_03_overbalance_pressure_display(self):
        """Displays calculated hydrostatic overbalance: 1120 psi."""
        proj = self.lookahead_data["projected_hazard"]
        self.assertAlmostEqual(float(proj["expected_overbalance_psi"]), 1120.0, places=1)

    def test_04_evidence_offset_well_citation(self):
        """Displays historical offset evidence: SYN-NHK-01 with 38.5h NPT."""
        proj = self.lookahead_data["projected_hazard"]
        offsets = proj.get("evidence_offsets", [])
        self.assertGreaterEqual(len(offsets), 1)
        evidence = offsets[0]
        self.assertEqual(evidence["well_name"], "SYN-NHK-01")
        self.assertAlmostEqual(float(evidence["historical_npt_hours"]), 38.5, places=1)

    def test_05_four_step_mitigations_rendered(self):
        """Displays 4 actionable mitigation steps for drill crew."""
        proj = self.lookahead_data["projected_hazard"]
        mitigations = proj.get("actionable_mitigation", [])
        self.assertEqual(len(mitigations), 4)
        for m in mitigations:
            self.assertIsInstance(m, str)
            self.assertGreater(len(m), 10)


if __name__ == "__main__":
    unittest.main()
