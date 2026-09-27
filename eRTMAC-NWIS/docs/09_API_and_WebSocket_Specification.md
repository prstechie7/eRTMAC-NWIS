# 09. REST API & WebSocket Telemetry Specification
## Technical Interface Contracts for eRTMAC-NWIS Backend

---

## 1. REST Endpoints Overview

| Method | Endpoint | Description | Query / Body Params | Response Code |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service liveness and extension health check | None | `200 OK` |
| `GET` | `/api/v1/wells` | List all wells filtered by field and status | `field_name`, `status`, `limit` | `200 OK` |
| `GET` | `/api/v1/wells/{well_id}` | Detailed well profile, trajectory, and tops | Path: `well_id` | `200 OK` |
| `POST` | `/api/v1/spatial/offset-wells` | Retrieve offset wells within 3D radius | Body: `SpatialQueryRequest` | `200 OK` |
| `GET` | `/api/v1/intelligence/lookahead` | Compute look-ahead risk index $R_H$ | `active_well_id`, `bit_depth_md` | `200 OK` |
| `GET` | `/api/v1/hazards` | Query historical offset hazards | `formation`, `hazard_type`, `tvdss_min` | `200 OK` |
| `POST` | `/api/v1/reports/tour-advisory` | Generate signed 2-page Tour Advisory PDF | Body: `TourAdvisoryRequest` | `200 OK` (binary PDF) |
| `WS` | `/ws/v1/telemetry` | 1 Hz real-time WITSML sensor stream | WebSocket Handshake | `101 Switching Protocols` |

---

## 2. Request & Response Payload Examples

### 2.1 Spatial Offset Well Query (`POST /api/v1/spatial/offset-wells`)

#### Request Payload:
```json
{
  "active_well_id": "c1f7a012-3b4c-4e89-9a11-000000000005",
  "surface_lat": 27.280000,
  "surface_lon": 95.340000,
  "current_tvdss_m": 2180.5,
  "radius_km": 5.0,
  "tvdss_window_m": 200.0
}
```

#### Response Payload (`200 OK`):
```json
{
  "status": "success",
  "query_time_ms": 11.4,
  "offset_wells_count": 4,
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
```

---

### 2.2 Proactive Look-Ahead Hazard Prediction (`GET /api/v1/intelligence/lookahead`)

#### Query:
`GET /api/v1/intelligence/lookahead?active_well_id=c1f7a012-3b4c-4e89-9a11-000000000005&bit_depth_md=2410.0`

#### Response Payload (`200 OK`):
```json
{
  "active_well": {
    "well_name": "SYN-NHK-05",
    "current_depth_md_m": 2410.0,
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
```

---

### 2.3 WebSocket 1 Hz Rig Telemetry Streaming (`WS /ws/v1/telemetry`)

Each 1-second telemetry payload broadcasts active drilling parameters from the WITSML simulator:

```json
{
  "timestamp": "2026-09-28T04:46:00.000Z",
  "active_well_id": "c1f7a012-3b4c-4e89-9a11-000000000005",
  "telemetry": {
    "measured_depth_m": 2415.05,
    "tvdss_m": 2185.02,
    "rop_mhr": 18.5,
    "wob_klbs": 18.2,
    "surface_torque_kftlb": 12.8,
    "rpm": 95.0,
    "standpipe_pressure_psi": 2950.0,
    "flow_rate_gpm": 640.0,
    "mud_density_in_sg": 1.16,
    "mud_density_out_sg": 1.16,
    "ecd_downhole_sg": 1.21,
    "gas_total_pct": 1.85,
    "pit_volume_gain_bbls": 0.2
  },
  "instantaneous_physics": {
    "teale_mse_psi": 48250.0,
    "mse_baseline_ratio": 1.45,
    "soft_string_friction_mu": 0.22,
    "mww_kick_margin_sg": 0.06,
    "mww_loss_margin_sg": 0.11
  },
  "lookahead_status": {
    "active_alert": true,
    "hazard_type": "DIFFERENTIAL_STICKING",
    "risk_index": 84.2,
    "distance_ahead_m": 33.45
  }
}
```
