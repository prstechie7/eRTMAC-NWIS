"""
Tier 1: Feature 3 (F3) - Database Seed Engine & Dataset
Validates the synthetic dataset structure, geological calibration,
and seed integrity per ORIGINAL_REQUEST § 2.
"""

import unittest
from tests.helpers.data_loader import load_synthetic_wells, validate_well_record


class TestF03DatabaseSeedEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_synthetic_wells()

    def test_01_dataset_metadata_and_calibration(self):
        """Verify dataset basin is Upper Assam Shelf and operator is Oil India Limited."""
        meta = self.data.get("metadata", {})
        self.assertEqual(meta.get("basin"), "Upper Assam Shelf")
        self.assertEqual(meta.get("operator"), "Oil India Limited")
        self.assertIn("calibrated_from", meta)

    def test_02_fields_catalog(self):
        """Verify Nahorkatiya, Moran, and Baghjan fields are configured with structural dips."""
        fields = {f["field_name"]: f for f in self.data.get("fields", [])}
        self.assertIn("Nahorkatiya", fields)
        self.assertIn("Moran", fields)
        self.assertIn("Baghjan", fields)
        self.assertGreater(fields["Nahorkatiya"].get("formation_dip_deg", 0), 0)

    def test_03_wells_schema_and_integrity_compliance(self):
        """Verify all wells comply with SYN-* naming and geographical boundaries."""
        wells = self.data.get("wells", [])
        self.assertGreaterEqual(len(wells), 3, "Dataset must contain defined synthetic wells")
        for well in wells:
            errors = validate_well_record(well)
            self.assertEqual(len(errors), 0, f"Well {well.get('well_name')} failed validation: {errors}")

    def test_04_active_well_syn_nhk_05_configuration(self):
        """Verify active well SYN-NHK-05 has status DRILLING and starting depth 2410m MD."""
        wells = {w["well_name"]: w for w in self.data.get("wells", [])}
        self.assertIn("SYN-NHK-05", wells, "SYN-NHK-05 active demo well must be present")
        nhk5 = wells["SYN-NHK-05"]
        self.assertEqual(nhk5.get("status"), "DRILLING")
        self.assertAlmostEqual(float(nhk5.get("current_bit_md_m", 0)), 2410.0, places=1)
        self.assertAlmostEqual(float(nhk5.get("current_bit_tvdss_m", 0)), 2180.5, places=1)

    def test_05_offset_hazard_record_syn_nhk_01(self):
        """Verify SYN-NHK-01 records DIFFERENTIAL_STICKING in Upper Tipam Sandstone with 38.5h NPT."""
        wells = {w["well_name"]: w for w in self.data.get("wells", [])}
        self.assertIn("SYN-NHK-01", wells)
        nhk1 = wells["SYN-NHK-01"]
        hazards = nhk1.get("historical_hazards", [])
        self.assertGreaterEqual(len(hazards), 1)

        diff_stick = next((h for h in hazards if h["hazard_type"] == "DIFFERENTIAL_STICKING"), None)
        self.assertIsNotNone(diff_stick, "SYN-NHK-01 must record DIFFERENTIAL_STICKING")
        self.assertEqual(diff_stick["formation_name"], "Upper Tipam Sandstone")
        self.assertAlmostEqual(float(diff_stick["npt_hours"]), 38.5, places=1)
        self.assertAlmostEqual(float(diff_stick["depth_md_m"]), 2448.5, places=1)

    def test_06_formation_tops_catalog(self):
        """Verify formation tops define Upper Tipam Sandstone, Girujan Clay, and Barail."""
        wells = {w["well_name"]: w for w in self.data.get("wells", [])}
        nhk1_tops = [t["name"] for t in wells["SYN-NHK-01"].get("formation_tops", [])]
        self.assertIn("Upper Tipam Sandstone", nhk1_tops)
        self.assertIn("Girujan Clay", nhk1_tops)
        self.assertIn("Barail Coal-Shale Unit", nhk1_tops)


if __name__ == "__main__":
    unittest.main()
