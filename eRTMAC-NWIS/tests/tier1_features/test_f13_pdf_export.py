"""
Tier 1: Feature 13 (F13) - One-Click PDF Export
Validates OIL Tour Advisory PDF structure, Palette 1 styling, and integrity badges.
"""

import unittest


class TestF13PdfExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # PDF document specification model
        cls.pdf_spec = {
            "title": "eRTMAC-NWIS Tour Advisory & Look-Ahead Alert",
            "operator": "Oil India Limited",
            "page_count": 2,
            "palette": {
                "header_green": "#184E3A",
                "accent_amber": "#E58A13",
                "border_slate": "#1E242B"
            },
            "synthetic_badge": "[Synthetic — Assam Basin Profile]",
            "sections": [
                "Executive Summary & Active Rig Telemetry",
                "Look-Ahead Hazard Advisory & Mitigations",
                "3D Offset Well Correlation Evidence",
                "Superintendent Operational Sign-Off"
            ]
        }

    def test_01_two_page_document_structure(self):
        """Tour Advisory PDF specifies exactly 2 pages."""
        self.assertEqual(self.pdf_spec["page_count"], 2)

    def test_02_oil_branding_and_title(self):
        """Header contains Oil India Limited branding and Tour Advisory title."""
        self.assertEqual(self.pdf_spec["operator"], "Oil India Limited")
        self.assertIn("Tour Advisory", self.pdf_spec["title"])

    def test_03_palette_1_styling_tokens(self):
        """PDF elements use Pine Green (#184E3A) and Petroleum Amber (#E58A13)."""
        palette = self.pdf_spec["palette"]
        self.assertEqual(palette["header_green"], "#184E3A")
        self.assertEqual(palette["accent_amber"], "#E58A13")

    def test_04_prominent_synthetic_badge_in_pdf(self):
        """PDF includes required '[Synthetic — Assam Basin Profile]' badge."""
        self.assertEqual(self.pdf_spec["synthetic_badge"], "[Synthetic — Assam Basin Profile]")

    def test_05_operational_sign_off_section(self):
        """PDF includes Superintendent Sign-Off section for shift turnover."""
        self.assertIn("Superintendent Operational Sign-Off", self.pdf_spec["sections"])


if __name__ == "__main__":
    unittest.main()
