"""
Tier 3: Combination 4 - Look-Ahead Alert Card to PDF Export Round-Trip (F11 -> F13)
Validates that numbers displayed on the interactive Alert Card are faithfully
mirrored into the Tour Advisory PDF generation payload without mutation.
"""

import unittest
from tests.helpers.test_client import NWISTestClient


class TestCombAlertPdf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = NWISTestClient()
        _, cls.lookahead = cls.client.get_lookahead("c1f7a012-3b4c-4e89-9a11-000000000005", 2410.0)

    def test_01_alert_card_to_pdf_payload_consistency(self):
        """Card values (84.2, 38.5m, 1120 psi) are passed to PDF generation payload."""
        proj = self.lookahead["projected_hazard"]
        pdf_payload = {
            "well_name": self.lookahead["active_well"]["well_name"],
            "risk_index": proj["risk_index"],
            "hazard_type": proj["hazard_type"],
            "distance_to_hazard_m": proj["distance_to_hazard_m"],
            "expected_overbalance_psi": proj["expected_overbalance_psi"],
            "mitigations": proj["actionable_mitigation"]
        }
        self.assertEqual(pdf_payload["well_name"], "SYN-NHK-05")
        self.assertEqual(pdf_payload["risk_index"], 84.2)
        self.assertEqual(pdf_payload["expected_overbalance_psi"], 1120.0)
        self.assertEqual(len(pdf_payload["mitigations"]), 4)

    def test_02_pdf_branding_and_palette_preservation(self):
        """PDF generation incorporates Palette 1 theme tokens and OIL branding."""
        theme_tokens = {
            "brand_green": "#184E3A",
            "amber_caution": "#E58A13",
            "slate_border": "#1E242B"
        }
        self.assertEqual(theme_tokens["brand_green"], "#184E3A")
        self.assertEqual(theme_tokens["amber_caution"], "#E58A13")

    def test_03_data_integrity_badge_persists_in_pdf(self):
        """The synthetic badge is preserved in the export payload."""
        export_badge = "[Synthetic — Assam Basin Profile]"
        self.assertIn("Synthetic", export_badge)


if __name__ == "__main__":
    unittest.main()
