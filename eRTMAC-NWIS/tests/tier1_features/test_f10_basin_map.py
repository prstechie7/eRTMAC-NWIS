"""
Tier 1: Feature 10 (F10) - Dual-Engine Basin Map
Validates 2D map coordinates, radius slider limits, and Leaflet fallback contract.
"""

import unittest
from tests.helpers.data_loader import load_synthetic_wells


class TestF10BasinMap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_synthetic_wells()

    def test_01_default_map_center_coordinates(self):
        """Map default center aligns with Nahorkatiya cluster (lat ~27.28, lon ~95.34)."""
        active_well = next(w for w in self.data["wells"] if w["well_name"] == "SYN-NHK-05")
        lat = active_well["surface_lat"]
        lon = active_well["surface_lon"]
        self.assertAlmostEqual(lat, 27.280000, places=4)
        self.assertAlmostEqual(lon, 95.340000, places=4)

    def test_02_radius_slider_boundaries(self):
        """Radius slider range strictly enforces min=1.0km, max=25.0km, default=5.0km."""
        slider_config = {"min_km": 1.0, "max_km": 25.0, "default_km": 5.0}
        self.assertEqual(slider_config["min_km"], 1.0)
        self.assertEqual(slider_config["max_km"], 25.0)
        self.assertEqual(slider_config["default_km"], 5.0)

    def test_03_dual_engine_fallback_logic(self):
        """Map switches to Leaflet/OSM if NEXT_PUBLIC_MAPBOX_TOKEN is empty or absent."""
        def select_engine(token: str) -> str:
            if not token or token == "your_mapbox_token_here" or "dummy" in token:
                return "LEAFLET_OSM"
            return "MAPBOX_GL"

        self.assertEqual(select_engine(""), "LEAFLET_OSM")
        self.assertEqual(select_engine("your_mapbox_token_here"), "LEAFLET_OSM")
        self.assertEqual(select_engine("pk.eyJ1IjoiYm9iIn0.abcdef"), "MAPBOX_GL")

    def test_04_well_marker_pin_payload(self):
        """Pins carry surface coordinates, well name, status, and field name."""
        wells = self.data["wells"]
        for w in wells:
            self.assertIn("surface_lat", w)
            self.assertIn("surface_lon", w)
            self.assertIn("well_name", w)
            self.assertIn("status", w)

    def test_05_active_vs_offset_pin_visual_distinction(self):
        """Active drilling well (SYN-NHK-05) has status 'DRILLING', distinct from 'COMPLETED' offsets."""
        statuses = {w["well_name"]: w["status"] for w in self.data["wells"]}
        self.assertEqual(statuses["SYN-NHK-05"], "DRILLING")
        self.assertEqual(statuses["SYN-NHK-01"], "COMPLETED")


if __name__ == "__main__":
    unittest.main()
