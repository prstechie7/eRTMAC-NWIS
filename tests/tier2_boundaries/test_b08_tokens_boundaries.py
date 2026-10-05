"""
Tier 2: Boundary 8 (B08) - Design Token Boundaries
Validates edge cases in color tokens: invalid hex strings, contrast calculation limits,
and identical color contrast ratios.
"""

import unittest
from tests.tier1_features.test_f08_nextjs_tokens import contrast_ratio, hex_to_rgb


class TestB08TokensBoundaries(unittest.TestCase):
    def test_01_identical_color_contrast_ratio_is_one(self):
        """Contrast ratio between identical colors is exactly 1.0."""
        ratio = contrast_ratio("#184E3A", "#184E3A")
        self.assertAlmostEqual(ratio, 1.0, places=4)

    def test_02_pure_black_and_white_contrast_ratio_is_twenty_one(self):
        """Contrast ratio between pure black (#000000) and pure white (#FFFFFF) is 21.0."""
        ratio = contrast_ratio("#000000", "#FFFFFF")
        self.assertAlmostEqual(ratio, 21.0, places=1)

    def test_03_invalid_hex_length_handling(self):
        """Malformed hex string length is detected."""
        with self.assertRaises(Exception):
            hex_to_rgb("#184E")

    def test_04_amber_on_charcoal_slate_contrast(self):
        """Petroleum Amber (#E58A13) on Charcoal Slate (#1E242B) provides high readability (> 4.5:1)."""
        ratio = contrast_ratio("#E58A13", "#1E242B")
        self.assertGreaterEqual(ratio, 4.5)

    def test_05_critical_red_on_canvas_contrast(self):
        """Critical Red (#D9381E) on white Canvas (#FFFFFF) maintains strong alert visibility (> 4.5:1)."""
        ratio = contrast_ratio("#D9381E", "#FFFFFF")
        self.assertGreaterEqual(ratio, 4.5)


if __name__ == "__main__":
    unittest.main()
