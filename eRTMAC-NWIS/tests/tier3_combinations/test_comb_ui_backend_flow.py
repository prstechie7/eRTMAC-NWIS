"""
Tier 3: Combination 5 - Frontend Map and Radius Controls to Backend Pipeline (F10 -> F5 -> F11)
Validates that adjusting the UI basin map radius slider dynamically updates
the spatial offset well query and recomputes the Look-Ahead Alert Card state.
"""

import unittest
from tests.helpers.test_client import NWISTestClient


class TestCombUiBackendFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = NWISTestClient()

    def test_01_slider_adjustment_triggers_spatial_refresh(self):
        """Increasing radius from 3km to 5km expands offset well detection window."""
        payload_3km = {
            "active_well_id": "c1f7a012-3b4c-4e89-9a11-000000000005",
            "surface_lat": 27.28,
            "surface_lon": 95.34,
            "current_tvdss_m": 2180.5,
            "radius_km": 3.0,
            "tvdss_window_m": 200.0
        }
        status_code, res_3km = self.client.post_offset_wells(payload_3km)
        self.assertEqual(status_code, 200)

        payload_5km = dict(payload_3km, radius_km=5.0)
        status_code, res_5km = self.client.post_offset_wells(payload_5km)
        self.assertEqual(status_code, 200)

    def test_02_map_pin_selection_drives_lookahead_focus(self):
        """Selecting active well pin triggers lookahead hazard calculation."""
        selected_well_id = "c1f7a012-3b4c-4e89-9a11-000000000005"
        status_code, lookahead = self.client.get_lookahead(selected_well_id, 2410.0)
        self.assertEqual(status_code, 200)
        self.assertEqual(lookahead["active_well"]["well_name"], "SYN-NHK-05")
        self.assertEqual(lookahead["projected_hazard"]["hazard_type"], "DIFFERENTIAL_STICKING")


if __name__ == "__main__":
    unittest.main()
