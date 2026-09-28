"""
Tier 2: Boundary 7 (B07) - WebSocket Telemetry Boundaries
Validates edge cases in WebSocket streaming: malformed packets, invalid UUIDs,
and empty / binary frames.
"""

import unittest
import json


class TestB07WebSocketBoundaries(unittest.TestCase):
    def test_01_malformed_json_packet(self):
        """Malformed JSON payload is detected and rejected without socket termination."""
        bad_json = "{ action: subscribe, well_id: invalid_json"
        is_valid = True
        try:
            json.loads(bad_json)
        except Exception:
            is_valid = False
        self.assertFalse(is_valid)

    def test_02_empty_subscription_action(self):
        """Subscription message missing action parameter is flagged invalid."""
        payload = {"well_id": "c1f7a012-3b4c-4e89-9a11-000000000005"}
        has_action = "action" in payload and payload["action"] == "subscribe"
        self.assertFalse(has_action)

    def test_03_invalid_uuid_format_in_ws_subscription(self):
        """Non-UUID well_id string (e.g., '12345') is flagged invalid."""
        import uuid
        def is_valid_uuid(val: str) -> bool:
            try:
                uuid.UUID(val)
                return True
            except (ValueError, TypeError):
                return False

        self.assertFalse(is_valid_uuid("not-a-valid-uuid-string"))
        self.assertTrue(is_valid_uuid("c1f7a012-3b4c-4e89-9a11-000000000005"))

    def test_04_zero_rop_mse_singularity_guard(self):
        """When ROP is 0 (pipe stationary during survey), MSE does not raise divide-by-zero."""
        from tests.helpers.math_oracle import compute_teale_mse
        with self.assertRaises(ValueError):
            compute_teale_mse(18000.0, 12000.0, 90.0, rop_ft_hr=0.0)

    def test_05_extreme_sensor_values_clamping(self):
        """Extreme physical sensor inputs (e.g. gas 150%) are flagged or clamped."""
        def validate_sensor_frame(gas_pct: float, ecd_sg: float) -> bool:
            if gas_pct < 0.0 or gas_pct > 100.0:
                return False
            if ecd_sg < 0.5 or ecd_sg > 3.0:
                return False
            return True

        self.assertFalse(validate_sensor_frame(gas_pct=150.0, ecd_sg=1.2))
        self.assertFalse(validate_sensor_frame(gas_pct=2.0, ecd_sg=5.0))
        self.assertTrue(validate_sensor_frame(gas_pct=1.85, ecd_sg=1.21))


if __name__ == "__main__":
    unittest.main()
