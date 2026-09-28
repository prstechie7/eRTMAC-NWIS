"""
Tier 1: Feature 12 (F12) - WITSML Rig Simulator
Validates 1 Hz bit depth advancement, hazard crossing trigger, and telemetry framing.
"""

import unittest


class SimulatedRig:
    def __init__(self, start_md: float = 2410.0, target_md: float = 2450.0, rop_mhr: float = 18.0):
        self.current_md = start_md
        self.target_md = target_md
        self.rop_mhr = rop_mhr
        # Step increment per second: rop (m/hr) / 3600
        self.step_delta = rop_mhr / 3600.0

    def step(self):
        self.current_md += self.step_delta
        is_hazard_zone = (self.current_md >= 2445.0)
        return {
            "measured_depth_m": round(self.current_md, 3),
            "hazard_alert": is_hazard_zone,
            "rop_mhr": self.rop_mhr
        }


class TestF12WitsmlSimulator(unittest.TestCase):
    def test_01_simulator_initial_depth(self):
        """Simulator begins at 2410.0m MD for SYN-NHK-05."""
        rig = SimulatedRig(start_md=2410.0)
        self.assertAlmostEqual(rig.current_md, 2410.0, places=2)

    def test_02_monotonic_depth_advance(self):
        """Bit depth strictly increases on each 1-second simulation tick."""
        rig = SimulatedRig(start_md=2410.0, rop_mhr=20.0)
        p1 = rig.step()
        p2 = rig.step()
        self.assertGreater(p2["measured_depth_m"], p1["measured_depth_m"])

    def test_03_hazard_zone_alert_trigger(self):
        """Crossing into Upper Tipam Sandstone depleted horizon (2445m+) triggers alert."""
        rig = SimulatedRig(start_md=2444.9, rop_mhr=3600.0)  # 1m/sec for rapid test
        f1 = rig.step()  # 2445.9m
        self.assertTrue(f1["hazard_alert"], "Alert failed to fire upon crossing 2445m threshold")

    def test_04_realistic_rop_step_size(self):
        """At 18 m/hr ROP, 1-second step advance is ~0.005m."""
        rig = SimulatedRig(start_md=2410.0, rop_mhr=18.0)
        expected_step = 18.0 / 3600.0  # 0.005 m
        self.assertAlmostEqual(rig.step_delta, expected_step, places=5)

    def test_05_witsml_telemetry_fields(self):
        """Simulator produces required WITSML channels: MD, alert, and ROP."""
        rig = SimulatedRig()
        frame = rig.step()
        self.assertIn("measured_depth_m", frame)
        self.assertIn("hazard_alert", frame)
        self.assertIn("rop_mhr", frame)


if __name__ == "__main__":
    unittest.main()
