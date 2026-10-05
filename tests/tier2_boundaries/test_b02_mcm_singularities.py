"""
Tier 2: Boundary 2 (B02) - MCM Singularities & Mathematical Boundaries
Validates edge cases in 3D trajectory math: beta -> 0, antiparallel beta -> pi,
sub-millimeter intervals, negative delta MD, and cosine clamping.
"""

import math
import unittest
from tests.helpers.math_oracle import compute_mcm_station


class TestB02MCMSingularities(unittest.TestCase):
    def test_01_negative_delta_md_raises_error(self):
        """Negative delta MD (out-of-order surveys) raises ValueError."""
        with self.assertRaises(ValueError):
            compute_mcm_station(
                md1=500.0, inc1_deg=10.0, azi1_deg=45.0,
                md2=450.0, inc2_deg=10.0, azi2_deg=45.0
            )

    def test_02_zero_delta_md_station(self):
        """Zero delta MD produces zero displacement and zero DLS without division error."""
        st = compute_mcm_station(
            md1=500.0, inc1_deg=15.0, azi1_deg=30.0,
            md2=500.0, inc2_deg=15.0, azi2_deg=30.0,
            prev_tvd=480.0
        )
        self.assertAlmostEqual(st["delta_tvd"], 0.0)
        self.assertAlmostEqual(st["delta_north"], 0.0)
        self.assertAlmostEqual(st["delta_east"], 0.0)
        self.assertAlmostEqual(st["dls_deg_per_30m"], 0.0)

    def test_03_sub_millimeter_interval_stability(self):
        """Sub-millimeter delta MD (1e-4 m) computes stably without floating underflow."""
        st = compute_mcm_station(
            md1=100.0, inc1_deg=10.0, azi1_deg=20.0,
            md2=100.0001, inc2_deg=10.0001, azi2_deg=20.0001
        )
        self.assertGreater(st["delta_md"], 0.0)
        self.assertTrue(math.isfinite(st["rf"]))
        self.assertTrue(math.isfinite(st["delta_tvd"]))

    def test_04_cosine_clamping_domain_protection(self):
        """Precision rounding resulting in cos(beta) slightly outside [-1, 1] is safely clamped."""
        # Using exact vertical stations where precision could yield 1.0000000000000002
        st = compute_mcm_station(
            md1=0.0, inc1_deg=0.0, azi1_deg=0.0,
            md2=30.0, inc2_deg=0.0, azi2_deg=0.0
        )
        self.assertAlmostEqual(st["beta_rad"], 0.0, places=9)

    def test_05_antiparallel_extreme_dogleg(self):
        """Near-180 degree extreme dogleg angle handles tangent expansion stably."""
        st = compute_mcm_station(
            md1=100.0, inc1_deg=0.0, azi1_deg=0.0,
            md2=200.0, inc2_deg=179.99, azi2_deg=0.0
        )
        self.assertTrue(math.isfinite(st["delta_tvd"]))
        self.assertGreater(st["dls_deg_per_30m"], 50.0)


if __name__ == "__main__":
    unittest.main()
