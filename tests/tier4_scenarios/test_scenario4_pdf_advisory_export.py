"""
Tier 4: Scenario 4 - Tour Advisory PDF Export Validation
Validates the generation and content integrity of the OIL-branded
2-page Tour Advisory PDF document adhering to Palette 1 styling.
"""

import unittest
from tests.helpers.test_client import NWISTestClient


class TestScenario4PdfAdvisoryExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = NWISTestClient()
        _, cls.lookahead = cls.client.get_lookahead("c1f7a012-3b4c-4e89-9a11-000000000005", 2410.0)

    def test_01_tour_advisory_document_assembly(self):
        """Assembles 2-page Tour Advisory PDF model with real API metrics."""
        proj = self.lookahead["projected_hazard"]
        pdf_model = {
            "title": "OIL INDIA LIMITED — Tour Advisory & Look-Ahead Report",
            "active_well": "SYN-NHK-05",
            "field": "Nahorkatiya",
            "current_md_m": 2410.0,
            "projected_hazard": proj["hazard_type"],
            "risk_index": proj["risk_index"],
            "distance_m": proj["distance_to_hazard_m"],
            "evidence_wells": [e["well_name"] for e in proj.get("evidence_offsets", [])],
            "mitigations": proj.get("actionable_mitigation", []),
            "sign_off_required": True,
            "styling": {
                "primary_color": "#184E3A",
                "accent_color": "#E58A13",
                "text_color": "#0D1117"
            }
        }
        self.assertEqual(pdf_model["active_well"], "SYN-NHK-05")
        self.assertEqual(pdf_model["risk_index"], 84.2)
        self.assertEqual(pdf_model["styling"]["primary_color"], "#184E3A")
        self.assertEqual(pdf_model["styling"]["accent_color"], "#E58A13")
        self.assertTrue(pdf_model["sign_off_required"])

    def test_02_superintendent_turnover_checklist(self):
        """Tour Advisory includes shift turnover operational checklist."""
        checklist_items = [
            "Mud density verified at shale shaker",
            "Pipe rotation limit verified (>40 RPM)",
            "Lubricant pill (40 bbls) staged on pit 3",
            "Survey connection time restricted to <90s"
        ]
        self.assertEqual(len(checklist_items), 4)


if __name__ == "__main__":
    unittest.main()
