"""
Tier 2: Boundary 10 (B10) - Basin Map Boundaries
Validates edge cases in map interactions: slider clamping, invalid token handling,
and boundary coordinates.
"""

import unittest


def clamp_radius_slider(val: float, min_km: float = 1.0, max_km: float = 25.0) -> float:
    """Clamps radius slider input to legal [1.0, 25.0] km range."""
    try:
        f_val = float(val)
    except (ValueError, TypeError):
        return 5.0  # Default fallback
    return max(min_km, min(max_km, f_val))


class TestB10MapBoundaries(unittest.TestCase):
    def test_01_slider_below_minimum_clamped(self):
        """Slider value < 1.0km is clamped to 1.0km."""
        self.assertEqual(clamp_radius_slider(0.2), 1.0)
        self.assertEqual(clamp_radius_slider(-10.0), 1.0)

    def test_02_slider_above_maximum_clamped(self):
        """Slider value > 25.0km is clamped to 25.0km."""
        self.assertEqual(clamp_radius_slider(50.0), 25.0)
        self.assertEqual(clamp_radius_slider(100.0), 25.0)

    def test_03_non_numeric_slider_input_defaults_to_five(self):
        """Non-numeric string input defaults safely to 5.0km."""
        self.assertEqual(clamp_radius_slider("invalid"), 5.0)
        self.assertEqual(clamp_radius_slider(None), 5.0)

    def test_04_valid_slider_range_preserved(self):
        """Slider values inside [1.0, 25.0] km are preserved exactly."""
        self.assertEqual(clamp_radius_slider(1.0), 1.0)
        self.assertEqual(clamp_radius_slider(12.5), 12.5)
        self.assertEqual(clamp_radius_slider(25.0), 25.0)

    def test_05_mapbox_token_whitespace_fallback(self):
        """Mapbox token with only whitespace or placeholder defaults to Leaflet."""
        def is_mapbox_valid(token: str) -> bool:
            if not token or not token.strip():
                return False
            if "your_mapbox_token" in token:
                return False
            return True

        self.assertFalse(is_mapbox_valid("   "))
        self.assertFalse(is_mapbox_valid("your_mapbox_token_here"))
        self.assertTrue(is_mapbox_valid("pk.eyJ1IjoiYWxwaGEifQ.valid"))


if __name__ == "__main__":
    unittest.main()
