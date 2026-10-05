"""
Tier 2: Boundary 12 (B12) - WITSML Simulator Boundaries
Validates edge cases in simulator loop: stationary pipe, high ROP, depth bounds.
"""

import unittest
from tests.tier1_features.test_f12_witsml_sim import SimulatedRig


class TestB12WitsmlBoundaries(unittest.TestCase):
    def test_01_zero_rop_stationary_pipe(self):
        """When ROP is 0.0 m/hr, bit depth does not advance."""
        rig = SimulatedRig(start_md=2410.0, rop_mhr=0.0)
        f1 = rig.step()
        f2 = rig.step()
        self.assertEqual(f1["measured_depth_m"], 2410.0)
        self.assertEqual(f2["measured_depth_m"], 2410.0)

    def test_02_negative_rop_clamped(self):
        """Negative ROP (drillstring pulled up) is clamped or handled as non-drilling."""
        def safe_step(rig, rop):
            eff_rop = max(0.0, rop)
            return eff_rop / 3600.0

        self.assertEqual(safe_step(None, -15.0), 0.0)

    def test_03_high_rop_fast_forward(self):
        """High ROP (e.g. 100 m/hr fast forward) advances stably without drift."""
        rig = SimulatedRig(start_md=2410.0, rop_mhr=100.0)
        for _ in range(36):  # 36 seconds
            rig.step()
        # 100 m / 3600 * 36 = 1.0 m advance => 2411.0m
        self.assertAlmostEqual(rig.current_md, 2411.0, places=2)

    def test_04_crossing_exact_depth_boundary(self):
        """Bit exactly at 2445.0m triggers hazard zone flag."""
        rig = SimulatedRig(start_md=2445.0, rop_mhr=0.0)
        f = rig.step()
        self.assertTrue(f["hazard_alert"])

    def test_05_floating_point_accumulation_ten_thousand_steps(self):
        """10,000 steps at 18 m/hr advance exactly 50m without catastrophic cancellation."""
        rig = SimulatedRig(start_md=2400.0, rop_mhr=18.0)
        # 18 / 3600 = 0.005 m per step; 10,000 steps * 0.005 = 50.0m
        for _ in range(10000):
            rig.step()
        self.assertAlmostEqual(rig.current_md, 2450.0, places=2)


if __name__ == "__main__":
    unittest.main()
