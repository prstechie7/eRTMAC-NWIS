"""
Tier 2: Boundary 6 (B06) - GET /api/v1/intelligence/lookahead Boundaries
Validates edge cases in look-ahead risk calculations: surface depth, negative depth,
extreme depth, and zero-distance singularity handling.
"""

import unittest
from tests.helpers.test_client import NWISTestClient
from tests.helpers.math_oracle import compute_lookahead_risk_index


class TestB06LookaheadBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = NWISTestClient()
        cls.active_well_id = "c1f7a012-3b4c-4e89-9a11-000000000005"

    def test_01_negative_depth_rejected(self):
        """Negative bit depth MD is rejected with 422 Unprocessable Entity."""
        status_code, body = self.client.get_lookahead(self.active_well_id, bit_depth_md=-50.0)
        self.assertIn(status_code, [400, 422])

    def test_02_surface_depth_zero(self):
        """At 0.0m MD (surface hole), lookahead executes safely without dividing by zero."""
        status_code, body = self.client.get_lookahead(self.active_well_id, bit_depth_md=0.0)
        self.assertIn(status_code, [200, 404])

    def test_03_zero_distance_singularity_protection(self):
        """When active bit position equals offset position (distance=0), formula does not divide by zero."""
        rh_res = compute_lookahead_risk_index(
            active_bit_pos=(100.0, 100.0, 2000.0),
            projected_tvdss=2000.0,
            offsets=[{
                "well_name": "SYN-NHK-TEST",
                "pos_3d": (100.0, 100.0, 2000.0),  # Exact same point (d3d = 0)
                "incident_tvdss": 2000.0,
                "severity": 4
            }]
        )
        self.assertGreater(rh_res["risk_index"], 0.0)
        self.assertLessEqual(rh_res["risk_index"], 100.0)

    def test_04_deep_beyond_td(self):
        """Bit depth exceeding well TD (e.g. 10,000m) is handled gracefully without crashing."""
        status_code, body = self.client.get_lookahead(self.active_well_id, bit_depth_md=10000.0)
        self.assertIn(status_code, [200, 400, 404, 422])

    def test_05_empty_offset_incident_list(self):
        """When no offset incidents exist within window, risk index evaluates safely to 0 (LOW)."""
        rh_res = compute_lookahead_risk_index(
            active_bit_pos=(0.0, 0.0, 1000.0),
            projected_tvdss=1000.0,
            offsets=[]
        )
        self.assertEqual(rh_res["risk_index"], 0.0)
        self.assertEqual(rh_res["risk_level"], "LOW")


if __name__ == "__main__":
    unittest.main()
