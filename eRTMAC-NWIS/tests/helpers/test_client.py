"""
Resilient Test Client for eRTMAC-NWIS REST and WebSocket Interfaces.
Supports live execution when FastAPI backend is running on http://localhost:8000,
as well as offline specification contract validation.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple


class NWISTestClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self._is_live = None

    def is_backend_live(self) -> bool:
        """
        Pings /api/v1/health or /docs to check if the FastAPI backend is running.
        """
        if self._is_live is not None:
            return self._is_live

        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/v1/health",
                headers={"User-Agent": "eRTMAC-NWIS-TestRunner"}
            )
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                self._is_live = (resp.status == 200)
                return self._is_live
        except Exception:
            # Try root or docs
            try:
                req = urllib.request.Request(
                    f"{self.base_url}/docs",
                    headers={"User-Agent": "eRTMAC-NWIS-TestRunner"}
                )
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    self._is_live = (resp.status == 200)
                    return self._is_live
            except Exception:
                self._is_live = False
                return False

    def get_wells(self, field_name: Optional[str] = None, status: Optional[str] = None) -> Tuple[int, Any]:
        """
        Invokes GET /api/v1/wells with query parameters.
        """
        query_params = []
        if field_name:
            query_params.append(f"field_name={urllib.parse.quote(field_name)}")
        if status:
            query_params.append(f"status={urllib.parse.quote(status)}")

        qs = f"?{'&'.join(query_params)}" if query_params else ""
        url = f"{self.base_url}/api/v1/wells{qs}"

        if self.is_backend_live():
            try:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    return resp.status, json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                return e.code, json.loads(e.read().decode("utf-8"))
            except Exception as e:
                return 500, {"error": str(e)}

        # Offline Mock Contract Response per docs/09 § 1
        wells_mock = [
            {
                "well_id": "c1f7a012-3b4c-4e89-9a11-000000000001",
                "well_name": "SYN-NHK-01",
                "field_name": "Nahorkatiya",
                "operator": "Oil India Limited",
                "data_source": "SYNTHETIC",
                "surface_lat": 27.283100,
                "surface_lon": 95.342200,
                "kb_elevation_m": 112.5,
                "total_depth_m": 4520.0,
                "status": "COMPLETED"
            },
            {
                "well_id": "c1f7a012-3b4c-4e89-9a11-000000000005",
                "well_name": "SYN-NHK-05",
                "field_name": "Nahorkatiya",
                "operator": "Oil India Limited",
                "data_source": "SYNTHETIC",
                "surface_lat": 27.280000,
                "surface_lon": 95.340000,
                "kb_elevation_m": 112.0,
                "total_depth_m": 4500.0,
                "status": "DRILLING"
            }
        ]
        filtered = wells_mock
        if field_name:
            filtered = [w for w in filtered if w["field_name"].lower() == field_name.lower()]
        if status:
            filtered = [w for w in filtered if w["status"].lower() == status.lower()]
        return 200, filtered

    def post_offset_wells(self, payload: Dict[str, Any]) -> Tuple[int, Any]:
        """
        Invokes POST /api/v1/spatial/offset-wells with body.
        """
        url = f"{self.base_url}/api/v1/spatial/offset-wells"
        if self.is_backend_live():
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    return resp.status, json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                return e.code, json.loads(e.read().decode("utf-8"))
            except Exception as e:
                return 500, {"error": str(e)}

        # Offline Mock Contract Response per docs/09 § 2.1
        radius = payload.get("radius_km", 5.0)
        if radius <= 0:
            return 422, {"status": "error", "message": "radius_km must be positive"}

        return 200, {
            "status": "success",
            "query_time_ms": 11.4,
            "offset_wells_count": 1,
            "data": [
                {
                    "well_id": "c1f7a012-3b4c-4e89-9a11-000000000001",
                    "well_name": "SYN-NHK-01",
                    "field_name": "Nahorkatiya",
                    "surface_distance_m": 1420.5,
                    "stratigraphic_tvdss_offset_m": -1.5,
                    "closest_approach_tvdss_m": 2179.0,
                    "recorded_hazards_in_window": [
                        {
                            "hazard_id": "haz-001-01",
                            "hazard_type": "DIFFERENTIAL_STICKING",
                            "depth_md_m": 2448.5,
                            "depth_tvdss_m": 2179.0,
                            "severity_level": 4,
                            "npt_hours": 38.5,
                            "formation_name": "Upper Tipam Sandstone"
                        }
                    ]
                }
            ]
        }

    def get_lookahead(self, active_well_id: str, bit_depth_md: float) -> Tuple[int, Any]:
        """
        Invokes GET /api/v1/intelligence/lookahead?active_well_id=...&bit_depth_md=...
        """
        url = f"{self.base_url}/api/v1/intelligence/lookahead?active_well_id={active_well_id}&bit_depth_md={bit_depth_md}"
        if self.is_backend_live():
            try:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    return resp.status, json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                return e.code, json.loads(e.read().decode("utf-8"))
            except Exception as e:
                return 500, {"error": str(e)}

        # Offline Mock Contract Response per docs/09 § 2.2
        if bit_depth_md < 0:
            return 422, {"status": "error", "message": "bit_depth_md must be non-negative"}

        # SYN-NHK-05 at 2410m MD
        return 200, {
            "active_well": {
                "well_name": "SYN-NHK-05",
                "current_depth_md_m": bit_depth_md,
                "current_tvdss_m": 2180.5,
                "current_formation": "Upper Tipam Sandstone"
            },
            "lookahead_window_m": 75.0,
            "projected_hazard": {
                "hazard_type": "DIFFERENTIAL_STICKING",
                "risk_index": 84.2,
                "risk_level": "HIGH",
                "distance_to_hazard_m": 38.5,
                "projected_depth_md_m": 2448.5,
                "projected_depth_tvdss_m": 2179.0,
                "expected_overbalance_psi": 1120.0,
                "evidence_offsets": [
                    {
                        "well_name": "SYN-NHK-01",
                        "distance_surface_km": 1.42,
                        "structural_dip_alignment": "Identical stratigraphic horizon (+1.5m TSD delta)",
                        "historical_npt_hours": 38.5,
                        "historical_cause": "Pipe stationary for 45 min during directional survey in depleted sand (PP 0.88 SG).",
                        "historical_mitigation": "Spotted 40 bbls lubricant pill; reduced MW to 1.10 SG; rotated out with 55 RPM."
                    }
                ],
                "actionable_mitigation": [
                    "Limit stationary drillstring time to < 90 seconds across 2,430m - 2,480m.",
                    "Reduce active mud system density from 1.16 SG to 1.10 SG if overlying Girujan Clay permits.",
                    "Spot 40 bbls lubricating / anti-sticking pill prior to traversing depleted sand package.",
                    "Maintain continuous drillstring rotation (>40 RPM) during all survey operations."
                ]
            }
        }
