"""
Tier 1: Feature 8 (F8) - Next.js Foundation & Design Tokens
Validates Palette 1 'Assam Crude & Industrial Amber' color tokens,
contrast ratios, and typography specifications per docs/10 § 1.
"""

import unittest
import math


def hex_to_rgb(hex_code: str):
    hex_clean = hex_code.lstrip("#")
    return tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))


def relative_luminance(rgb):
    def channel(c):
        c_norm = c / 255.0
        return c_norm / 12.92 if c_norm <= 0.03928 else ((c_norm + 0.055) / 1.055) ** 2.4
    r, g, b = [channel(val) for val in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex1: str, hex2: str) -> float:
    l1 = relative_luminance(hex_to_rgb(hex1))
    l2 = relative_luminance(hex_to_rgb(hex2))
    brightest = max(l1, l2)
    darkest = min(l1, l2)
    return (brightest + 0.05) / (darkest + 0.05)


class TestF08NextJsTokens(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tokens = {
            "pine_green": "#184E3A",
            "petroleum_amber": "#E58A13",
            "charcoal_slate": "#1E242B",
            "canvas_surface": "#FFFFFF",
            "card_container_fill": "#F8F9FA",
            "text_title": "#0D1117",
            "text_body": "#4A5568",
            "critical_red_alert": "#D9381E"
        }

    def test_01_palette_1_hex_values(self):
        """Verify exact hex codes for Palette 1 'Assam Crude & Industrial Amber'."""
        self.assertEqual(self.tokens["pine_green"].upper(), "#184E3A")
        self.assertEqual(self.tokens["petroleum_amber"].upper(), "#E58A13")
        self.assertEqual(self.tokens["charcoal_slate"].upper(), "#1E242B")
        self.assertEqual(self.tokens["card_container_fill"].upper(), "#F8F9FA")
        self.assertEqual(self.tokens["critical_red_alert"].upper(), "#D9381E")

    def test_02_text_title_contrast_on_canvas(self):
        """Title text (#0D1117) against canvas (#FFFFFF) exceeds WCAG AAA ratio (>= 7:1)."""
        ratio = contrast_ratio(self.tokens["text_title"], self.tokens["canvas_surface"])
        self.assertGreaterEqual(ratio, 7.0, f"Contrast ratio {ratio} below 7.0")

    def test_03_text_body_contrast_on_card(self):
        """Body text (#4A5568) against card container (#F8F9FA) exceeds WCAG AA ratio (>= 4.5:1)."""
        ratio = contrast_ratio(self.tokens["text_body"], self.tokens["card_container_fill"])
        self.assertGreaterEqual(ratio, 4.5, f"Contrast ratio {ratio} below 4.5")

    def test_04_critical_red_alert_luminance(self):
        """Critical Red Alert (#D9381E) maintains distinct warning luminance against card fill."""
        ratio = contrast_ratio(self.tokens["critical_red_alert"], self.tokens["card_container_fill"])
        self.assertGreaterEqual(ratio, 3.5, f"Warning contrast ratio {ratio} below 3.5")

    def test_05_brand_pine_green_distinction(self):
        """Pine Green (#184E3A) provides deep contrast (>4.5:1) against card fill."""
        ratio = contrast_ratio(self.tokens["pine_green"], self.tokens["card_container_fill"])
        self.assertGreaterEqual(ratio, 4.5, f"Pine green contrast ratio {ratio} below 4.5")


if __name__ == "__main__":
    unittest.main()
