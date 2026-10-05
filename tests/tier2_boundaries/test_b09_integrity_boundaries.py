"""
Tier 2: Boundary 9 (B09) - Data Integrity & Red Team Attack Boundaries
Validates edge cases in well name validation: lowercase prefixes, missing hyphens,
script tags, and forbidden real-name variants.
"""

import unittest
import re


def is_valid_nwis_well_name(name: str) -> bool:
    """Universal strict validator for eRTMAC-NWIS well names."""
    if not name or not isinstance(name, str):
        return False
    # Strictly require SYN-<FIELD>-<NUM> uppercase
    pattern = r"^SYN-[A-Z]+-[0-9]{2,}$"
    return bool(re.match(pattern, name))


class TestB09IntegrityBoundaries(unittest.TestCase):
    def test_01_lowercase_syn_prefix_rejected(self):
        """Lowercase 'syn-nhk-01' is strictly rejected."""
        self.assertFalse(is_valid_nwis_well_name("syn-nhk-01"))

    def test_02_missing_hyphen_rejected(self):
        """Name without hyphen 'SYNNHK01' is strictly rejected."""
        self.assertFalse(is_valid_nwis_well_name("SYNNHK01"))

    def test_03_injection_script_tag_rejected(self):
        """XSS injection attempt in well name is rejected."""
        self.assertFalse(is_valid_nwis_well_name("SYN-NHK-<script>alert(1)</script>"))

    def test_04_real_oil_well_variants_rejected(self):
        """Real well variations without SYN- prefix are rejected."""
        self.assertFalse(is_valid_nwis_well_name("NHK-114"))
        self.assertFalse(is_valid_nwis_well_name("MORAN-42"))
        self.assertFalse(is_valid_nwis_well_name("BAGHJAN-5"))

    def test_05_valid_synthetic_names_accepted(self):
        """Valid synthetic names pass without exception."""
        self.assertTrue(is_valid_nwis_well_name("SYN-NHK-01"))
        self.assertTrue(is_valid_nwis_well_name("SYN-NHK-05"))
        self.assertTrue(is_valid_nwis_well_name("SYN-MORAN-02"))
        self.assertTrue(is_valid_nwis_well_name("SYN-BGJ-01"))


if __name__ == "__main__":
    unittest.main()
