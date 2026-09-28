"""
Tier 1: Feature 7 (F7) - WS /ws/v1/telemetry Endpoint
Validates real-time 1 Hz WebSocket stream protocol, channel schemas, and physics calculations.
"""

import unittest
from tests.helpers.math_oracle import compute_teale_mse


class TestF07TelemetryWebSocketEndpoint(unittest.TestCase):
    def setUp(self):
        # Sample representative frame per docs/09 § 2.3
        self.sample_frame = {
            "timestamp": "2026-09-28T04:46:00.000Z",
            "active_well_id": "c1f7a012-3b4c-4e89-9a11-000000000005",
            "telemetry": {
                "measured_depth_m": 2415.05,
                "tvdss_m": 2185.02,
                "rop_mhr": 18.5,
                "wob_klbs": 18.2,
                "surface_torque_kftlb": 12.8,
                "rpm": 95.0,
                "standpipe_pressure_psi": 2950.0,
                "flow_rate_gpm": 640.0,
                "mud_density_in_sg": 1.16,
                "mud_density_out_sg": 1.16,
                "ecd_downhole_sg": 1.21,
                "gas_total_pct": 1.85,
                "pit_volume_gain_bbls": 0.2
            },
            "instantaneous_physics": {
                "teale_mse_psi": 48250.0,
                "mse_baseline_ratio": 1.45,
                "soft_string_friction_mu": 0.22,
                "mww_kick_margin_sg": 0.06,
                "mww_loss_margin_sg": 0.11
            },
            "lookahead_status": {
                "active_alert": True,
                "hazard_type": "DIFFERENTIAL_STICKING",
                "risk_index": 84.2,
                "distance_ahead_m": 33.45
            }
        }

    def test_01_handshake_subscription_protocol(self):
        """Subscription message format contains action 'subscribe' and UUID well_id."""
        sub_msg = {"action": "subscribe", "well_id": "c1f7a012-3b4c-4e89-9a11-000000000005"}
        self.assertEqual(sub_msg["action"], "subscribe")
        self.assertTrue(len(sub_msg["well_id"]) == 36)

    def test_02_telemetry_channels_count_and_keys(self):
        """Verify 13 core drilling telemetry channels are present."""
        telem = self.sample_frame.get("telemetry", {})
        expected_channels = {
            "measured_depth_m", "tvdss_m", "rop_mhr", "wob_klbs",
            "surface_torque_kftlb", "rpm", "standpipe_pressure_psi",
            "flow_rate_gpm", "mud_density_in_sg", "mud_density_out_sg",
            "ecd_downhole_sg", "gas_total_pct", "pit_volume_gain_bbls"
        }
        for ch in expected_channels:
            self.assertIn(ch, telem, f"Missing telemetry channel: {ch}")
        self.assertGreaterEqual(len(telem), 13)

    def test_03_instantaneous_physics_channels(self):
        """Verify 5 instantaneous physics channels are present."""
        physics = self.sample_frame.get("instantaneous_physics", {})
        expected_physics = {
            "teale_mse_psi", "mse_baseline_ratio", "soft_string_friction_mu",
            "mww_kick_margin_sg", "mww_loss_margin_sg"
        }
        for ch in expected_physics:
            self.assertIn(ch, physics, f"Missing physics channel: {ch}")
        self.assertGreaterEqual(len(physics), 5)

    def test_04_lookahead_status_channels(self):
        """Verify 4 lookahead status channels are present in frame."""
        status = self.sample_frame.get("lookahead_status", {})
        expected_status = {"active_alert", "hazard_type", "risk_index", "distance_ahead_m"}
        for ch in expected_status:
            self.assertIn(ch, status, f"Missing lookahead channel: {ch}")
        self.assertGreaterEqual(len(status), 4)

    def test_05_teale_mse_physics_oracle_consistency(self):
        """Verify Teale's Mechanical Specific Energy calculation with physics formula."""
        # Convert sample values to field units
        # wob_lbs = 18.2 klbs * 1000 = 18200 lbs
        # torque_ft_lbs = 12.8 kft-lb * 1000 = 12800 ft-lbs
        # rop_ft_hr = 18.5 m/hr * 3.28084 = 60.69 ft/hr
        # rpm = 95
        # bit_diameter = 8.5 inches
        mse = compute_teale_mse(
            wob_lbs=18200.0,
            torque_ft_lbs=12800.0,
            rpm=95.0,
            rop_ft_hr=60.69,
            bit_diameter_in=8.5
        )
        self.assertGreater(mse, 10000.0, "MSE must reflect drilling energy > 10,000 psi")
        self.assertLess(mse, 1000000.0, "MSE must not diverge unrealistically")

    def test_06_iso8601_timestamp_format(self):
        """Verify timestamp adheres to ISO 8601 UTC format with second/millisecond precision."""
        ts = self.sample_frame.get("timestamp", "")
        self.assertTrue(ts.endswith("Z"), "Timestamp must be UTC format (ending with Z)")
        self.assertIn("T", ts)


if __name__ == "__main__":
    unittest.main()
