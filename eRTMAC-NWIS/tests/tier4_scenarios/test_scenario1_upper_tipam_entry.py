"""
Tier 4: Scenario 1 - SYN-NHK-05 Upper Tipam Sandstone Interval Entry
Simulates active well SYN-NHK-05 drilling at 2410m MD / 2180.5m TVDSS in Nahorkatiya field,
penetrating the depleted, underpressured Upper Tipam Sandstone package.
"""

import unittest
from tests.helpers.data_loader import load_synthetic_wells
from tests.helpers.math_oracle import compute_mcm_station
from tests.helpers.test_client import NWISTestClient


class TestScenario1UpperTipamEntry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_synthetic_wells()
        cls.client = NWISTestClient()

    def test_01_active_well_demographics_and_coordinates(self):
        """Active well SYN-NHK-05 is correctly registered with Nahorkatiya coordinates."""
        nhk5 = next(w for w in self.data["wells"] if w["well_name"] == "SYN-NHK-05")
        self.assertEqual(nhk5["field_name"], "Nahorkatiya")
        self.assertEqual(nhk5["status"], "DRILLING")
        self.assertAlmostEqual(nhk5["surface_lat"], 27.280000, places=4)
        self.assertAlmostEqual(nhk5["surface_lon"], 95.340000, places=4)
        self.assertAlmostEqual(nhk5["kb_elevation_m"], 112.0, places=1)

    def test_02_current_depth_and_tvdss_alignment(self):
        """At 2410m MD, current TVDSS is ~2180.5m."""
        nhk5 = next(w for w in self.data["wells"] if w["well_name"] == "SYN-NHK-05")
        self.assertAlmostEqual(nhk5["current_bit_md_m"], 2410.0, places=1)
        self.assertAlmostEqual(nhk5["current_bit_tvdss_m"], 2180.5, places=1)

    def test_03_lithology_and_pore_pressure_characteristics(self):
        """Upper Tipam Sandstone represents a depleted reservoir (PP ~ 0.92 SG)."""
        nhk1 = next(w for w in self.data["wells"] if w["well_name"] == "SYN-NHK-01")
        tipam_top = next(t for t in nhk1["formation_tops"] if t["name"] == "Upper Tipam Sandstone")
        self.assertAlmostEqual(tipam_top["pore_pressure_sg"], 0.92, places=2)
        # Normal hydrostatic gradient is ~1.0 SG; 0.92 SG is depleted
        self.assertLess(tipam_top["pore_pressure_sg"], 1.0)

    def test_04_api_reflection_of_active_well(self):
        """REST API /wells?status=DRILLING returns active well SYN-NHK-05."""
        status_code, wells = self.client.get_wells(status="DRILLING")
        self.assertEqual(status_code, 200)
        active = next((w for w in wells if w["well_name"] == "SYN-NHK-05"), None)
        self.assertIsNotNone(active)
        self.assertEqual(active["status"], "DRILLING")


if __name__ == "__main__":
    unittest.main()
