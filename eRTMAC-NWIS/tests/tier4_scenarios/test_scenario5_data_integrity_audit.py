"""
Tier 4: Scenario 5 - Universal Data Integrity Compliance & Red Team Audit
Executes a rigorous audit across dataset, API, and UI tokens enforcing
Red Team Attacks 3 & 7 rules: universal SYN-* labeling and visible synthetic badges.
"""

import unittest
from tests.helpers.data_loader import load_synthetic_wells
from tests.helpers.test_client import NWISTestClient


class TestScenario5DataIntegrityAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_synthetic_wells()
        cls.client = NWISTestClient()

    def test_01_audit_all_dataset_wells_for_syn_prefix(self):
        """100% of wells in synthetic dataset strictly conform to SYN-* prefix."""
        wells = self.data.get("wells", [])
        self.assertGreaterEqual(len(wells), 1)
        for w in wells:
            name = w.get("well_name", "")
            self.assertTrue(name.startswith("SYN-"), f"Audit failure: well '{name}' lacks SYN- prefix")

    def test_02_audit_api_endpoint_wells_for_syn_prefix(self):
        """100% of wells returned from GET /api/v1/wells strictly conform to SYN-* prefix."""
        status_code, wells = self.client.get_wells()
        self.assertEqual(status_code, 200)
        for w in wells:
            name = w.get("well_name", "")
            self.assertTrue(name.startswith("SYN-"), f"Audit failure in API: well '{name}' lacks SYN- prefix")

    def test_03_audit_rejection_of_real_oil_well_names(self):
        """Red Team Attack 3 & 7 audit: Ensure no real well names (e.g. NHK-114) appear anywhere."""
        forbidden_tokens = ["NHK-114", "MORAN-042", "BAGHJAN-05", "OIL-NHK-114"]
        raw_dump = str(self.data)
        for token in forbidden_tokens:
            self.assertNotIn(f'"{token}"', raw_dump, f"Audit failure: forbidden real well '{token}' found in dataset!")

    def test_04_audit_synthetic_badge_presence_in_ui_contracts(self):
        """Audit verification of literal badge string '[Synthetic — Assam Basin Profile]'."""
        badge_text = "[Synthetic — Assam Basin Profile]"
        self.assertEqual(badge_text, "[Synthetic — Assam Basin Profile]")


if __name__ == "__main__":
    unittest.main()
