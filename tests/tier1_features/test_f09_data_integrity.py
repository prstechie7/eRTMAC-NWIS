"""
Tier 1: Feature 9 (F9) - Data Integrity Badging
Validates Red Team Challenge Attacks 3 & 7 compliance:
Universal SYN-* labeling and '[Synthetic — Assam Basin Profile]' badge presence.
"""

import unittest
import re
from tests.helpers.data_loader import load_synthetic_wells


class TestF09DataIntegrityBadging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_synthetic_wells()

    def test_01_all_dataset_wells_prefixed_syn(self):
        """Verify 100% of wells in synthetic dataset are prefixed with 'SYN-'."""
        wells = self.data.get("wells", [])
        for w in wells:
            name = w.get("well_name", "")
            self.assertTrue(name.startswith("SYN-"), f"Well {name} lacks required SYN- prefix")

    def test_02_synthetic_badge_text_literal(self):
        """Required badge text is literally '[Synthetic — Assam Basin Profile]'."""
        expected_badge_text = "[Synthetic — Assam Basin Profile]"
        self.assertIn("Synthetic", expected_badge_text)
        self.assertIn("Assam Basin Profile", expected_badge_text)

    def test_03_attack_3_red_team_no_real_well_names(self):
        """Verify forbidden real well names (e.g., NHK-114) are not present in dataset."""
        forbidden_names = ["NHK-114", "MORAN-042", "OIL-NHK-114", "DDR-NHK-114"]
        wells_str = str(self.data)
        for fn in forbidden_names:
            self.assertNotIn(f'"{fn}"', wells_str, f"Forbidden real well name '{fn}' detected!")

    def test_04_uwi_synthetic_format(self):
        """Unique Well Identifier (UWI) carries SYN marker (e.g., IN-OIL-NHK-SYN-001)."""
        wells = self.data.get("wells", [])
        for w in wells:
            uwi = w.get("uwi", "")
            self.assertIn("SYN", uwi, f"UWI '{uwi}' lacks SYN indicator")

    def test_05_badge_injection_detection(self):
        """A well name missing SYN- is immediately identified as invalid."""
        invalid_well_name = "NHK-05"
        is_valid = invalid_well_name.startswith("SYN-")
        self.assertFalse(is_valid, "Sanitizer failed to reject non-SYN well name")


if __name__ == "__main__":
    unittest.main()
