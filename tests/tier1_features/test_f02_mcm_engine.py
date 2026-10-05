"""
Tier 1: Feature 2 (F2) - MCM Trajectory Engine
Validates the mathematical precision and physical invariants of the
Minimum Curvature Method implementation per docs/03 § 1.
"""

import math
import unittest
from tests.helpers.math_oracle import compute_mcm_station
from backend.app.services.mcm import MCMTrajectoryEngine, compute_mcm_station as backend_compute_mcm_station


class TestF02MCMTrajectoryEngine(unittest.TestCase):
    def test_01_straight_vertical_hole(self):
        """Straight vertical well (0 deg inc): Delta TVD = Delta MD, displacement = 0, RF = 1.0."""
        st = compute_mcm_station(
            md1=0.0, inc1_deg=0.0, azi1_deg=0.0,
            md2=100.0, inc2_deg=0.0, azi2_deg=0.0,
            prev_tvd=0.0, prev_north=0.0, prev_east=0.0,
            kb_elevation_m=112.0
        )
        self.assertAlmostEqual(st["delta_tvd"], 100.0, places=4)
        self.assertAlmostEqual(st["delta_north"], 0.0, places=4)
        self.assertAlmostEqual(st["delta_east"], 0.0, places=4)
        self.assertAlmostEqual(st["rf"], 1.0, places=6)
        self.assertAlmostEqual(st["dls_deg_per_30m"], 0.0, places=4)
        self.assertAlmostEqual(st["tvdss_m"], 100.0 - 112.0, places=4)

    def test_02_build_section_inclination_change(self):
        """Build section (inc 0 to 30 deg, azi 0 deg): Delta TVD, Delta North, and DLS positive."""
        delta_md = 100.0
        st = compute_mcm_station(
            md1=500.0, inc1_deg=0.0, azi1_deg=0.0,
            md2=600.0, inc2_deg=30.0, azi2_deg=0.0,
            prev_tvd=500.0, prev_north=0.0, prev_east=0.0
        )
        # Expected beta is 30 degrees = pi / 6 radians
        expected_beta = math.radians(30.0)
        self.assertAlmostEqual(st["beta_rad"], expected_beta, places=5)
        # RF = (2 / beta) * tan(beta / 2)
        expected_rf = (2.0 / expected_beta) * math.tan(expected_beta / 2.0)
        self.assertAlmostEqual(st["rf"], expected_rf, places=5)
        # Delta TVD = (100 / 2) * (cos(0) + cos(30)) * RF
        expected_delta_tvd = (100.0 / 2.0) * (1.0 + math.cos(math.radians(30.0))) * expected_rf
        self.assertAlmostEqual(st["delta_tvd"], expected_delta_tvd, places=4)
        # DLS = (30 deg / 100m) * 30m = 9.0 deg/30m
        self.assertAlmostEqual(st["dls_deg_per_30m"], 9.0, places=4)

    def test_03_turn_section_azimuth_change(self):
        """Turn section at constant inclination (inc 45 deg, azi 0 to 90 deg)."""
        st = compute_mcm_station(
            md1=1000.0, inc1_deg=45.0, azi1_deg=0.0,
            md2=1050.0, inc2_deg=45.0, azi2_deg=90.0
        )
        # Both north and east displacements must be strictly positive
        self.assertGreater(st["delta_north"], 0.0)
        self.assertGreater(st["delta_east"], 0.0)
        self.assertGreater(st["dls_deg_per_30m"], 0.0)

    def test_04_tvdss_subsea_depth_datum(self):
        """TVDSS calculation: TVDSS = TVD - KB_elevation."""
        kb = 112.5
        tvd_val = 2100.0
        st = compute_mcm_station(
            md1=2000.0, inc1_deg=0.0, azi1_deg=0.0,
            md2=2100.0, inc2_deg=0.0, azi2_deg=0.0,
            prev_tvd=2000.0, kb_elevation_m=kb
        )
        self.assertAlmostEqual(st["tvd_m"], tvd_val, places=3)
        self.assertAlmostEqual(st["tvdss_m"], tvd_val - kb, places=3)

    def test_05_singularity_protection_rf_limit(self):
        """Verify RF = 1.0 when beta approaches zero (< 1e-6 rad)."""
        # Stations with identical inclination and azimuth
        st = compute_mcm_station(
            md1=100.0, inc1_deg=15.123456, azi1_deg=84.56789,
            md2=130.0, inc2_deg=15.123456, azi2_deg=84.56789
        )
        self.assertAlmostEqual(st["rf"], 1.0, places=7)
        self.assertAlmostEqual(st["beta_rad"], 0.0, places=7)

    def test_06_dls_reference_normalization(self):
        """Verify DLS scales inversely with delta MD and normalizes to 30m standard."""
        st1 = compute_mcm_station(0.0, 0.0, 0.0, 30.0, 3.0, 0.0)
        st2 = compute_mcm_station(0.0, 0.0, 0.0, 60.0, 6.0, 0.0)
        # Both represent a 3 deg per 30m curvature rate
        self.assertAlmostEqual(st1["dls_deg_per_30m"], 3.0, places=2)
        self.assertAlmostEqual(st2["dls_deg_per_30m"], 3.0, places=2)

    def test_07_backend_mcm_service_parity(self):
        """Verify backend.app.services.mcm produces identical results to reference oracle."""
        oracle_st = compute_mcm_station(
            md1=500.0, inc1_deg=5.0, azi1_deg=120.0,
            md2=600.0, inc2_deg=22.5, azi2_deg=145.0,
            prev_tvd=500.0, prev_north=10.0, prev_east=20.0,
            kb_elevation_m=112.0
        )
        backend_st = backend_compute_mcm_station(
            md1=500.0, inc1_deg=5.0, azi1_deg=120.0,
            md2=600.0, inc2_deg=22.5, azi2_deg=145.0,
            prev_tvd=500.0, prev_north=10.0, prev_east=20.0,
            kb_elevation_m=112.0
        )
        self.assertAlmostEqual(oracle_st["tvd_m"], backend_st["tvd_m"], places=4)
        self.assertAlmostEqual(oracle_st["tvdss_m"], backend_st["tvdss_m"], places=4)
        self.assertAlmostEqual(oracle_st["north_m"], backend_st["north_m"], places=4)
        self.assertAlmostEqual(oracle_st["east_m"], backend_st["east_m"], places=4)
        self.assertAlmostEqual(oracle_st["dls_deg_per_30m"], backend_st["dls_deg_per_30m"], places=4)

    def test_08_mcm_trajectory_engine_full_trajectory(self):
        """Verify MCMTrajectoryEngine computes full trajectory with EWKT and AMSL elevation."""
        surveys = [
            (0.0, 0.0, 145.0),
            (500.0, 0.0, 145.0),
            (1100.0, 22.75, 145.0),
            (2410.0, 22.75, 145.0),
        ]
        stations = MCMTrajectoryEngine.calculate_trajectory(
            surveys=surveys,
            surface_lat=27.28,
            surface_lon=95.34,
            kb_elevation_m=112.0,
            z_elevation_mode="AMSL"
        )
        self.assertEqual(len(stations), 4)
        # Station 0 at surface
        self.assertEqual(stations[0].md_m, 0.0)
        self.assertEqual(stations[0].tvd_m, 0.0)
        self.assertEqual(stations[0].tvdss_m, -112.0)
        self.assertEqual(stations[0].z_3857, 112.0)
        self.assertTrue(stations[0].geom_ewkt.startswith("SRID=3857;POINT Z"))
        # Final station at 2410m MD
        final_st = stations[-1]
        self.assertEqual(final_st.md_m, 2410.0)
        self.assertAlmostEqual(final_st.tvdss_m, 2180.5, delta=1.0)
        self.assertAlmostEqual(final_st.z_3857, -2180.5, delta=1.0)

    def test_09_mcm_web_mercator_projection(self):
        """Verify EPSG:3857 coordinate projection accurately maps lat/lon origin."""
        x, y = MCMTrajectoryEngine.wgs84_to_epsg3857(27.28, 95.34)
        # Expected approximate Web Mercator bounds for Upper Assam
        self.assertGreater(x, 10_000_000.0)
        self.assertLess(x, 11_000_000.0)
        self.assertGreater(y, 3_000_000.0)
        self.assertLess(y, 4_000_000.0)


if __name__ == "__main__":
    unittest.main()
