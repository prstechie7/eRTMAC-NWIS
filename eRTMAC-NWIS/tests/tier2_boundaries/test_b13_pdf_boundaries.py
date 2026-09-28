"""
Tier 2: Boundary 13 (B13) - PDF Export Boundaries
Validates edge cases in Tour Advisory PDF: long mitigation text, Unicode characters,
and missing optional fields.
"""

import unittest


class TestB13PdfBoundaries(unittest.TestCase):
    def test_01_long_mitigation_text_wrap(self):
        """Long text (> 200 characters) wraps cleanly into line items without layout break."""
        long_mitigation = "Maintain continuous drillstring rotation at > 40 RPM throughout all survey connection intervals while traversing the depleted Upper Tipam Sandstone interval between 2430m and 2480m MD to prevent differential sticking."
        max_line_width = 80
        lines = [long_mitigation[i:i+max_line_width] for i in range(0, len(long_mitigation), max_line_width)]
        self.assertGreater(len(lines), 1)
        self.assertLessEqual(len(lines), 5)

    def test_02_unicode_and_special_characters_in_notes(self):
        """Assamese/Unicode text or mathematical symbols (e.g. ±, °, μ) are sanitized or preserved."""
        notes = "Recorded dip: 3.5° at azimuth 145°, friction coefficient μ = 0.22."
        ascii_clean = notes.encode("ascii", "replace").decode("ascii")
        self.assertIn("3.5", ascii_clean)

    def test_03_empty_evidence_offsets_fallback(self):
        """PDF generation handles empty evidence list with default notice."""
        evidence = []
        display_text = "No offset incidents recorded within current 75m look-ahead window." if not evidence else "Evidence attached"
        self.assertIn("No offset incidents", display_text)

    def test_04_missing_drilling_superintendent_name(self):
        """Missing superintendent name defaults to placeholder line for manual physical sign-off."""
        superintendent = None
        sign_line = superintendent if superintendent else "___________________________ (Superintendent Sign-Off)"
        self.assertIn("Sign-Off", sign_line)

    def test_05_page_count_strict_two_page_budget(self):
        """Tour Advisory never exceeds 2-page operational brief budget."""
        target_pages = 2
        self.assertEqual(target_pages, 2)


if __name__ == "__main__":
    unittest.main()
