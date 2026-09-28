"""
Tier 2: Boundary 3 (B03) - Seed Data Boundaries
Validates edge cases and corruption detection in synthetic dataset records.
"""

import unittest
from tests.helpers.data_loader import validate_well_record


class TestB03SeedBoundaries(unittest.TestCase):
    def test_01_missing_syn_prefix_detected(self):
        """Record lacking SYN- prefix fails validation with explicit error."""
        bad_well = {
            "well_name": "NHK-114",
            "surface_lat": 27.28,
            "surface_lon": 95.34,
            "kb_elevation_m": 112.0
        }
        errors = validate_well_record(bad_well)
        self.assertTrue(any("SYN-" in e for e in errors))

    def test_02_negative_kb_elevation_detected(self):
        """Negative Kelly Bushing elevation fails validation."""
        bad_well = {
            "well_name": "SYN-NHK-99",
            "surface_lat": 27.28,
            "surface_lon": 95.34,
            "kb_elevation_m": -10.0
        }
        errors = validate_well_record(bad_well)
        self.assertTrue(any("Kelly Bushing" in e for e in errors))

    def test_03_out_of_bounds_latitude_detected(self):
        """Coordinates outside Upper Assam basin boundaries fail validation."""
        bad_well = {
            "well_name": "SYN-NHK-99",
            "surface_lat": 18.5204,  # Mumbai latitude
            "surface_lon": 95.34,
            "kb_elevation_m": 112.0
        }
        errors = validate_well_record(bad_well)
        self.assertTrue(any("latitude" in e for e in errors))

    def test_04_out_of_bounds_longitude_detected(self):
        """Longitude outside Upper Assam basin boundaries fails validation."""
        bad_well = {
            "well_name": "SYN-NHK-99",
            "surface_lat": 27.28,
            "surface_lon": 72.8777,  # Mumbai longitude
            "kb_elevation_m": 112.0
        }
        errors = validate_well_record(bad_well)
        self.assertTrue(any("longitude" in e for e in errors))

    def test_05_unrealistically_shallow_target_depth(self):
        """Total depth less than 1000m fails validation for deep exploration targets."""
        bad_well = {
            "well_name": "SYN-NHK-99",
            "surface_lat": 27.28,
            "surface_lon": 95.34,
            "kb_elevation_m": 112.0,
            "total_depth_md_m": 250.0
        }
        errors = validate_well_record(bad_well)
        self.assertTrue(any("Total depth" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
