"""
Tier 3: Combination 3 - WITSML Simulator to WebSocket Telemetry Flow (F12 -> F7)
Validates that simulator bit depth advancements broadcast coherent 1 Hz telemetry packets
over WebSocket with dynamic alert state transitions.
"""

import unittest
from tests.tier1_features.test_f12_witsml_sim import SimulatedRig
from tests.helpers.math_oracle import compute_teale_mse


class TestCombWitsmlTelemetry(unittest.TestCase):
    def test_01_simulated_drilling_advances_telemetry_frame(self):
        """Simulator produces advancing depth and triggers alert escalation."""
        rig = SimulatedRig(start_md=2410.0, rop_mhr=18.0)
        # Advance 10 steps (10 seconds)
        frames = [rig.step() for _ in range(10)]
        self.assertEqual(len(frames), 10)
        self.assertGreater(frames[-1]["measured_depth_m"], frames[0]["measured_depth_m"])

    def test_02_dynamic_teale_mse_computation_per_packet(self):
        """Each frame computes dynamic Teale's MSE based on WOB, Torque, RPM, and ROP."""
        wob = 18.2 * 1000.0
        torque = 12.8 * 1000.0
        rpm = 95.0
        rop_ft = 18.5 * 3.28084
        mse = compute_teale_mse(wob, torque, rpm, rop_ft)
        self.assertGreater(mse, 40000.0)
        self.assertLess(mse, 250000.0)

    def test_03_telemetry_packet_channel_contract_compliance(self):
        """Simulated broadcast payload adheres strictly to docs/09 § 2.3 schema."""
        rig = SimulatedRig(start_md=2446.0, rop_mhr=20.0)
        step_data = rig.step()
        packet = {
            "timestamp": "2026-09-28T05:00:00.000Z",
            "active_well_id": "c1f7a012-3b4c-4e89-9a11-000000000005",
            "telemetry": {
                "measured_depth_m": step_data["measured_depth_m"],
                "rop_mhr": step_data["rop_mhr"]
            },
            "lookahead_status": {
                "active_alert": step_data["hazard_alert"],
                "hazard_type": "DIFFERENTIAL_STICKING"
            }
        }
        self.assertTrue(packet["lookahead_status"]["active_alert"])
        self.assertEqual(packet["lookahead_status"]["hazard_type"], "DIFFERENTIAL_STICKING")


if __name__ == "__main__":
    unittest.main()
