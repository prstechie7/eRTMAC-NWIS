"""
Tier 2: Boundary 4 (B04) - GET /api/v1/wells Boundaries
Validates edge cases in wells queries: nonexistent filters, injection attempts, and empty sets.
"""

import unittest
from tests.helpers.test_client import NWISTestClient


class TestB04WellsBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = NWISTestClient()

    def test_01_nonexistent_field_returns_empty_list(self):
        """Querying an unknown field (e.g., 'NonExistentField') safely returns 200 with empty array []."""
        status_code, body = self.client.get_wells(field_name="NonExistentField")
        self.assertEqual(status_code, 200)
        self.assertIsInstance(body, list)
        self.assertEqual(len(body), 0)

    def test_02_nonexistent_status_returns_empty_list(self):
        """Querying an unknown status (e.g., 'DECOMMISSIONED') returns empty array without error."""
        status_code, body = self.client.get_wells(status="DECOMMISSIONED")
        self.assertEqual(status_code, 200)
        self.assertIsInstance(body, list)
        self.assertEqual(len(body), 0)

    def test_03_sql_injection_attempt_in_field_name(self):
        """SQL injection string in field_name parameter does not execute or crash service."""
        injection_param = "' OR 1=1 --"
        status_code, body = self.client.get_wells(field_name=injection_param)
        self.assertIn(status_code, [200, 400, 422])
        if status_code == 200:
            self.assertEqual(len(body), 0)

    def test_04_special_characters_in_query(self):
        """Special characters (!@#$%^&*()_+<>?) in query handled safely."""
        status_code, body = self.client.get_wells(field_name="<script>alert(1)</script>")
        self.assertIn(status_code, [200, 400, 422])
        if status_code == 200:
            self.assertEqual(len(body), 0)

    def test_05_case_insensitivity_of_field_filter(self):
        """Filter field_name is case-insensitive ('nahorkatiya' matches 'Nahorkatiya')."""
        status_code, body = self.client.get_wells(field_name="nahorkatiya")
        self.assertEqual(status_code, 200)
        self.assertGreaterEqual(len(body), 1)


if __name__ == "__main__":
    unittest.main()
