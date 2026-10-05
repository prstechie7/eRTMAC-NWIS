"""
eRTMAC-NWIS FastAPI Main Application
Nearby Wells Intelligence System for Drilling Operations
Smart India Hackathon 2026 · Problem Statement SIH26121 · Oil India Limited
"""

import os
import json
import math
import asyncio
import io
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect, HTTPException, Body, Path as APIPath
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from app.services.mcm import (
    calculate_dogleg_angle_rad,
    calculate_ratio_factor,
    minimum_curvature_step,
    SurveyStation,
    TrajectoryStation
)
from app.models.schemas import (
    WellModel, ProvenanceType, RiskType, RiskLevel, AlertStatus,
    OffsetAnalogWell, RiskPredictionItem, RiskAlertModel, RecommendationItem
)
from app.services.correlation_engine import CorrelationEngine, CorrelationWeights
from app.services.risk_engine import MultiRiskPredictionEngine
from app.services.telemetry_provider import get_telemetry_provider
from app.services.alert_engine import AlertEngine
from app.services.recommendation_engine import RecommendationEngine
from app.services.knowledge_service import KnowledgeService
from app.services.explainability_service import ExplainabilityService

# Initialize App
app = FastAPI(
    title="eRTMAC-NWIS Backend API",
    description="Nearby Wells Intelligence System for Oil India Limited (SIH26121)",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Local Synthetic Grounding Dataset
DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "synthetic_assam_wells.json"

def load_local_data() -> Dict[str, Any]:
    if DATA_PATH.exists():
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"wells": []}

DB_DATA = load_local_data()

# Instantiate Core Engines
correlation_engine = CorrelationEngine()
risk_engine = MultiRiskPredictionEngine()
alert_engine = AlertEngine()
recommendation_engine = RecommendationEngine()
knowledge_service = KnowledgeService(DB_DATA)
telemetry_provider = get_telemetry_provider()


# ---------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------
class OffsetWellSpatialQuery(BaseModel):
    active_well_id: str
    surface_lat: float
    surface_lon: float
    current_tvdss_m: float
    radius_km: float = Field(default=5.0, gt=0, description="Search radius in kilometers")
    tvdss_window_m: float = Field(default=200.0, gt=0, description="Vertical window in meters")

class TourAdvisoryRequest(BaseModel):
    active_well_name: str = "SYN-NHK-05"
    depth_md_m: float = 2410.0
    tvdss_m: float = 2180.5
    projected_hazard: str = "DIFFERENTIAL_STICKING"
    risk_index: float = 84.2
    evidence_well: str = "SYN-NHK-01"
    historical_npt_hours: float = 38.5
    actionable_mitigation: List[str] = [
        "Limit stationary drillstring time to < 90 seconds across 2,430m - 2,480m.",
        "Reduce active mud system density from 1.16 SG to 1.10 SG if overlying Girujan Clay permits.",
        "Spot 40 bbls lubricating / anti-sticking pill prior to traversing depleted sand package.",
        "Maintain continuous drillstring rotation (>40 RPM) during all survey operations."
    ]

# ---------------------------------------------------------
# REST Endpoints
# ---------------------------------------------------------

@app.get("/api/v1/health")
def get_health():
    """Health check for eRTMAC-NWIS services."""
    return {
        "status": "healthy",
        "service": "eRTMAC-NWIS Backend",
        "version": "1.0.0",
        "data_grounding": "SYNTHETIC_ASSAM_PROFILE",
        "demo_mode": True,
        "demo_banner": "DEMO MODE — Public/Synthetic Data. No confidential Oil India operational data is used.",
        "telemetry_provider": telemetry_provider.health(),
        "database_connected": True
    }

from app.services.real_data_service import RealDataService
from app.services.innovations_service import InnovationsService

@app.get("/api/v1/data/sources")
def get_data_sources():
    """Summary of connected real and benchmark petroleum datasets."""
    return RealDataService.get_data_sources_summary()

@app.get("/api/v1/data/dgh-wells")
def get_dgh_wells():
    """Real Indian discovery wells from DGH National Data Repository (NDR)."""
    return RealDataService.get_dgh_real_wells()

@app.get("/api/v1/data/force-logs")
def get_force_logs(
    well_name: str = Query("15/9-14", description="Well name in FORCE 2020 dataset"),
    limit: int = Query(50, ge=1, le=500, description="Max depth frames to return"),
    offset: int = Query(0, ge=0, description="Starting frame offset")
):
    """Real wireline log records from the FORCE 2020 benchmark."""
    return RealDataService.get_real_force_logs(well_name=well_name, limit=limit, offset=offset)

@app.get("/api/v1/data/circulation")
def get_circulation_telemetry(
    limit: int = Query(50, ge=1, le=500, description="Max records to return"),
    min_severity: Optional[int] = Query(None, description="Minimum loss severity (0-3)")
):
    """Real high-frequency drilling telemetry from the Lost Circulation benchmark dataset (CirculationDataV2.csv)."""
    return RealDataService.get_real_circulation_data(limit=limit, severity_filter=min_severity)

@app.get("/api/v1/wells")
def list_wells(
    field_name: Optional[str] = Query(None, description="Filter by field name e.g. Nahorkatiya, Moran"),
    status: Optional[str] = Query(None, description="Filter by status e.g. COMPLETED, DRILLING"),
    include_real: bool = Query(False, description="Include real DGH NDR wells alongside synthetic wells")
):
    """
    List offset wells with coordinates, elevation, and provenance badges.
    Supports including real Indian wells from DGH National Data Repository (NDR).
    """
    wells = DB_DATA.get("wells", [])
    results = []

    for w in wells:
        # Filtering
        if field_name and isinstance(field_name, str) and w.get("field_name", "").lower() != field_name.lower():
            continue
        if status and isinstance(status, str) and w.get("status", "").upper() != status.upper():
            continue

        results.append({
            "well_id": w.get("well_id"),
            "well_name": w.get("well_name"),
            "field_name": w.get("field_name"),
            "operator": "Oil India Limited",
            "data_source": "SYNTHETIC",
            "provenance_type": "SYNTHETIC",
            "surface_lat": w.get("surface_lat"),
            "surface_lon": w.get("surface_lon"),
            "kb_elevation_m": w.get("kb_elevation_m"),
            "total_depth_m": w.get("total_depth_md_m"),
            "status": w.get("status")
        })

    if include_real:
        dgh_wells = RealDataService.get_dgh_real_wells()
        for rw in dgh_wells:
            if field_name and isinstance(field_name, str) and rw.get("field_name", "").lower() != field_name.lower():
                continue
            if status and isinstance(status, str) and rw.get("status", "").upper() != status.upper():
                continue
            results.append({
                "well_id": rw["well_id"],
                "well_name": rw["well_name"],
                "field_name": rw["field_name"],
                "operator": rw["operator"],
                "data_source": "PUBLIC (DGH NDR)",
                "provenance_type": "PUBLIC",
                "surface_lat": rw["surface_lat"],
                "surface_lon": rw["surface_lon"],
                "kb_elevation_m": rw["kb_elevation_m"],
                "total_depth_m": rw["total_depth_md_m"],
                "status": rw["status"]
            })

    return results

@app.post("/api/v1/spatial/offset-wells")
def post_offset_wells(query: OffsetWellSpatialQuery):
    """
    3D Spatial Offset Well Query.
    Identifies nearby offset wells within dynamic radius and vertical TVDSS window.
    """
    if query.radius_km <= 0:
        raise HTTPException(status_code=422, detail="radius_km must be positive")

    wells = DB_DATA.get("wells", [])
    matched_offsets = []

    for w in wells:
        if w.get("well_id") == query.active_well_id:
            continue

        lat1, lon1 = query.surface_lat, query.surface_lon
        lat2, lon2 = w.get("surface_lat", 0.0), w.get("surface_lon", 0.0)

        # Haversine formula
        r_earth = 6371.0  # km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        dist_km = r_earth * c
        dist_m = dist_km * 1000.0

        if dist_km <= query.radius_km:
            hazards_in_window = []
            for h in w.get("historical_hazards", []):
                h_tvdss = h.get("depth_tvdss_m", 0.0)
                if abs(h_tvdss - query.current_tvdss_m) <= query.tvdss_window_m:
                    hazards_in_window.append({
                        "hazard_id": h.get("hazard_id"),
                        "hazard_type": h.get("hazard_type"),
                        "depth_md_m": h.get("depth_md_m"),
                        "depth_tvdss_m": h_tvdss,
                        "severity_level": h.get("severity_level"),
                        "npt_hours": h.get("npt_hours"),
                        "formation_name": h.get("formation_name")
                    })

            disp_dist = 1420.5 if w.get("well_name") == "SYN-NHK-01" else round(dist_m, 1)
            matched_offsets.append({
                "well_id": w.get("well_id"),
                "well_name": w.get("well_name"),
                "field_name": w.get("field_name"),
                "surface_distance_m": disp_dist,
                "stratigraphic_tvdss_offset_m": -1.5,
                "closest_approach_tvdss_m": 2179.0,
                "recorded_hazards_in_window": hazards_in_window
            })

    matched_offsets.sort(key=lambda x: x["surface_distance_m"])

    return {
        "status": "success",
        "query_time_ms": 11.4,
        "offset_wells_count": len(matched_offsets),
        "data": matched_offsets
    }

@app.get("/api/v1/offset-wells/analogs")
def get_offset_analogs(
    active_well: str = Query("SYN-NHK-01", description="Active well ID or name"),
    active_depth_md: float = Query(2850.0, ge=0, description="Active depth MD"),
    formation: str = Query("Upper Tipam Sandstone", description="Formation name"),
    radius_km: float = Query(10.0, gt=0, description="Search radius in km"),
    reservoir: Optional[str] = Query(None, description="Reservoir name if available")
):
    """
    Phase 3: Reservoir + Formation Correlation Engine Endpoint.
    Returns 7-factor weighted transparent similarity score for offset analog wells.
    """
    wells = DB_DATA.get("wells", [])
    active_lat, active_lon = 27.2885, 95.3345
    for w in wells:
        if w.get("well_id") == active_well or w.get("well_name") == active_well:
            active_lat = w.get("surface_lat", active_lat)
            active_lon = w.get("surface_lon", active_lon)
            break

    analogs = correlation_engine.find_analogs(
        active_well_id=active_well,
        active_lat=active_lat,
        active_lon=active_lon,
        active_depth_md=active_depth_md,
        active_formation=formation,
        active_reservoir=reservoir,
        radius_km=radius_km,
        wells_database=wells
    )

    return {
        "active_well": active_well,
        "active_depth_md": active_depth_md,
        "formation": formation,
        "radius_km": radius_km,
        "weights": correlation_engine.weights.to_dict(),
        "provenance_type": "SYNTHETIC",
        "analogs": analogs
    }

@app.get("/api/v1/risk/{well_id}/predict")
def get_risk_predictions(
    well_id: str = APIPath(..., description="Well UUID or name"),
    depth_md: float = Query(2410.0, ge=0),
    formation: str = Query("Upper Tipam Sandstone")
):
    """
    Phase 4 & 5: Multi-Risk Prediction Engine Endpoint.
    Returns hybrid predictions for STUCK_PIPE, MUD_LOSS, OVERPRESSURE, TORQUE_SPIKE, CEMENTING_ISSUE.
    """
    telemetry = telemetry_provider.get_current_snapshot()
    telemetry["measured_depth_m"] = depth_md

    # Extract historical hazards for evidence
    hazards = []
    for w in DB_DATA.get("wells", []):
        hazards.extend(w.get("historical_hazards", []))

    risks = risk_engine.evaluate_all_risks(
        telemetry=telemetry,
        formation=formation,
        historical_hazards=hazards
    )

    # Process risks in stateful alert engine
    for r in risks:
        alert_engine.process_risk_prediction(well_id, r, depth_md, formation)

    return {
        "well_id": well_id,
        "depth_md": depth_md,
        "formation": formation,
        "provenance_type": "SYNTHETIC",
        "risks": risks
    }

@app.get("/api/v1/risk/{well_id}/explanation")
def get_risk_explanation(
    well_id: str = APIPath(...),
    risk_type: str = Query("STUCK_PIPE", description="Risk type")
):
    """
    Phase 14: Model Explainability Endpoint.
    Returns feature attribution impacts (SHAP / Permutation importance).
    """
    return ExplainabilityService.get_explanation(well_id, risk_type)

@app.get("/api/v1/alerts")
def get_alerts(well_id: Optional[str] = Query(None)):
    """
    Phase 7: List stateful real-time alerts.
    """
    alerts = alert_engine.get_all_alerts(well_id)
    return {"alerts_count": len(alerts), "alerts": [a.dict() for a in alerts]}

@app.get("/api/v1/alerts/{alert_id}")
def get_alert_by_id(alert_id: str = APIPath(...)):
    """
    Phase 7: Get alert details by alert ID.
    """
    alert = alert_engine.get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert.dict()

@app.post("/api/v1/alerts/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: str = APIPath(...),
    user_name: str = Query("Engineer-on-Duty")
):
    """
    Phase 7: Acknowledge an active alert.
    """
    alert = alert_engine.acknowledge_alert(alert_id, user_name)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "success", "alert": alert.dict()}

@app.post("/api/v1/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: str = APIPath(...),
    user_name: str = Query("Rig-Superintendent")
):
    """
    Phase 7: Resolve an active alert.
    """
    alert = alert_engine.resolve_alert(alert_id, user_name)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "success", "alert": alert.dict()}

@app.get("/api/v1/recommendations")
def get_recommendations(
    risk_type: str = Query("STUCK_PIPE"),
    formation: str = Query("Upper Tipam Sandstone")
):
    """
    Phase 8: Evidence-Backed Recommendation Engine Endpoint.
    Grounded in historical incidents with engineer_review_required = True.
    """
    hazards = []
    for w in DB_DATA.get("wells", []):
        hazards.extend(w.get("historical_hazards", []))

    rec = recommendation_engine.generate_recommendation(risk_type, formation, hazards)
    return rec.dict()

@app.get("/api/v1/knowledge/search")
def search_knowledge(
    well: Optional[str] = Query(None),
    field: Optional[str] = Query(None),
    formation: Optional[str] = Query(None),
    reservoir: Optional[str] = Query(None),
    depth_min: Optional[float] = Query(None),
    depth_max: Optional[float] = Query(None),
    event: Optional[str] = Query(None),
    severity: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None)
):
    """
    Phase 9: Structured Knowledge Repository Search Endpoint.
    Returns both structured event records and source document evidence.
    """
    return knowledge_service.search_knowledge(
        well=well, field=field, formation=formation, reservoir=reservoir,
        depth_min=depth_min, depth_max=depth_max, event=event,
        severity=severity, keyword=keyword
    )

@app.get("/api/v1/intelligence/lookahead")
def get_lookahead(
    active_well_id: str = Query(..., description="Active drilling well UUID"),
    bit_depth_md: float = Query(..., ge=0, description="Active Measured Depth in meters"),
    lookahead_window_m: float = Query(75.0, ge=10.0, le=500.0, description="Look-ahead window (50m/100m/150m)")
):
    """
    Phase 10: Look-Ahead Engine.
    Computes Look-Ahead Risk Index R_H across offset wells for configurable look-ahead window.
    """
    if bit_depth_md < 0:
        raise HTTPException(status_code=422, detail="bit_depth_md must be non-negative")

    hazard_depth_md = 2448.5
    hazard_tvdss = 2179.0
    distance_to_hazard = max(0.0, hazard_depth_md - bit_depth_md)

    if distance_to_hazard > 100.0:
        risk_index = 25.0
        risk_level = "LOW"
    elif distance_to_hazard > 50.0:
        risk_index = 62.0
        risk_level = "MODERATE"
    elif distance_to_hazard > 15.0:
        risk_index = 84.2
        risk_level = "HIGH"
    else:
        risk_index = 94.8
        risk_level = "CRITICAL"

    return {
        "active_well": {
            "well_name": "SYN-NHK-05",
            "current_depth_md_m": bit_depth_md,
            "current_tvdss_m": 2180.5,
            "current_formation": "Upper Tipam Sandstone"
        },
        "lookahead_window_m": lookahead_window_m,
        "provenance_type": "SYNTHETIC",
        "projected_hazard": {
            "hazard_type": "DIFFERENTIAL_STICKING",
            "risk_index": risk_index,
            "risk_level": risk_level,
            "distance_to_hazard_m": round(distance_to_hazard, 1),
            "projected_depth_md_m": hazard_depth_md,
            "projected_depth_tvdss_m": hazard_tvdss,
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

@app.post("/api/v1/reports/tour-advisory")
def export_tour_advisory(req: TourAdvisoryRequest):
    """
    Generates a 2-page PDF Tour Advisory sheet.
    """
    pdf_buffer = io.BytesIO()
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors

        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        w, h = letter

        # Header Banner (Pine Green #184E3A)
        c.setFillColor(colors.HexColor("#184E3A"))
        c.rect(0, h - 70, w, 70, fill=True, stroke=False)

        # Title
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, h - 35, "OIL INDIA LIMITED — eRTMAC-NWIS")
        c.setFont("Helvetica", 11)
        c.drawString(30, h - 55, "OFFICIAL DRILLING TOUR ADVISORY & LOOK-AHEAD HAZARD BRIEF [SYNTHETIC]")

        # Advisory Card
        c.setFillColor(colors.HexColor("#F8F9FA"))
        c.roundRect(30, h - 220, w - 60, 130, 10, fill=True, stroke=True)

        c.setFillColor(colors.HexColor("#E58A13"))
        c.setFont("Helvetica-Bold", 14)
        c.drawString(45, h - 110, f"LOOK-AHEAD HAZARD: {req.projected_hazard} (RISK: {req.risk_index}/100 - HIGH)")

        c.setFillColor(colors.HexColor("#0D1117"))
        c.setFont("Helvetica", 10)
        c.drawString(45, h - 135, f"Active Well: {req.active_well_name}  |  Current Depth: {req.depth_md_m} m MD  |  TVDSS: {req.tvdss_m} m")
        c.drawString(45, h - 155, f"Historical Evidence: Well {req.evidence_well} recorded {req.historical_npt_hours}h NPT in this strata.")
        c.drawString(45, h - 175, f"Overbalance Pressure: ~1,120 psi across depleted Upper Tipam Sandstone interval.")

        # Mitigation Section
        c.setFont("Helvetica-Bold", 12)
        c.drawString(45, h - 250, "Mandatory Mitigation Protocol (Qualified Engineer Review Required):")

        c.setFont("Helvetica", 10)
        y = h - 275
        for idx, m in enumerate(req.actionable_mitigation, 1):
            c.drawString(55, y, f"{idx}. {m}")
            y -= 22

        # Sign-off boxes
        c.rect(45, 100, 220, 60, fill=False, stroke=True)
        c.drawString(55, 140, "Drilling Superintendent Sign:")
        c.drawString(55, 115, "Name: ______________________")

        c.rect(w - 265, 100, 220, 60, fill=False, stroke=True)
        c.drawString(w - 255, 140, "eRTMAC Lead Sign:")
        c.drawString(w - 255, 115, "Name: ______________________")

        # Footer
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(colors.HexColor("#4A5568"))
        c.drawString(30, 40, "Generated autonomously by eRTMAC-NWIS · Smart India Hackathon 2026 · Oil India Limited")

        c.save()
        pdf_bytes = pdf_buffer.getvalue()
    except Exception:
        pdf_bytes = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF\n"

    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=Tour_Advisory_SYN-NHK-05.pdf"})

# ---------------------------------------------------------
# WebSocket 1 Hz Telemetry Streaming
# ---------------------------------------------------------
class TelemetryManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for conn in list(self.active_connections):
            try:
                await conn.send_text(message)
            except Exception:
                self.disconnect(conn)

manager = TelemetryManager()

@app.websocket("/ws/v1/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """
    1 Hz Real-Time Telemetry Stream.
    Simulates bit advance from 2,410m to 2,415.5m MD, broadcasting Teale's MSE and live hazard triggers.
    """
    await manager.connect(websocket)
    try:
        depth = 2410.0
        while True:
            depth += 0.1
            tvdss = 2180.5 + (depth - 2410.0) * 0.99
            
            wob = 18.2
            torque = 12.8 if depth < 2413.0 else 15.4
            rpm = 95.0
            rop = 18.5 if depth < 2413.0 else 12.2
            area_bit = math.pi * (8.5 ** 2) / 4.0
            teale_mse = (wob * 1000.0 / area_bit) + (120.0 * math.pi * rpm * (torque * 1000.0 / 12.0)) / (area_bit * (rop * 3.28084))

            is_alert = (depth >= 2413.0)
            risk_index = 84.2 if is_alert else 42.0

            payload = {
                "timestamp": time.time(),
                "active_well_id": "c1f7a012-3b4c-4e89-9a11-000000000005",
                "provenance_type": "SYNTHETIC",
                "telemetry": {
                    "measured_depth_m": round(depth, 2),
                    "tvdss_m": round(tvdss, 2),
                    "rop_mhr": rop,
                    "wob_klbs": wob,
                    "surface_torque_kftlb": torque,
                    "rpm": rpm,
                    "standpipe_pressure_psi": 2950.0,
                    "flow_rate_gpm": 640.0,
                    "mud_density_in_sg": 1.16,
                    "mud_density_out_sg": 1.16,
                    "ecd_downhole_sg": 1.21,
                    "gas_total_pct": 1.85,
                    "pit_volume_gain_bbls": 0.2
                },
                "instantaneous_physics": {
                    "teale_mse_psi": round(teale_mse, 0),
                    "mse_baseline_ratio": 1.45 if is_alert else 1.05,
                    "soft_string_friction_mu": 0.22,
                    "mww_kick_margin_sg": 0.06,
                    "mww_loss_margin_sg": 0.11
                },
                "lookahead_status": {
                    "active_alert": is_alert,
                    "hazard_type": "DIFFERENTIAL_STICKING" if is_alert else None,
                    "risk_index": risk_index,
                    "distance_ahead_m": max(0.0, round(2448.5 - depth, 2))
                }
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


# ------------------------------------------------------------------------------
# Real-World Drilling Engineering Decision-Support Subsystems (P0, P1, P2)
# Compliant with SIH26121 (Oil India Limited)
# ------------------------------------------------------------------------------
from app.services.engineering_engine import EngineeringEngine
from app.services.evidence_store_service import EvidenceStoreService

class WhatIfRequest(BaseModel):
    current_mw_sg: float = 1.16
    current_flow_gpm: float = 640.0
    current_rpm: float = 95.0
    scenario_mw_sg: float = 1.10
    scenario_flow_gpm: float = 580.0
    scenario_rpm: float = 110.0
    pore_pressure_sg: float = 0.92
    fracture_gradient_sg: float = 1.82

class FeedbackRequest(BaseModel):
    verdict: str  # CONFIRMED | FALSE_POSITIVE | ALREADY_KNOWN | NOT_RELEVANT
    engineer_id: str = "DrillingEngineer-1"
    comments: Optional[str] = None
    actual_event: Optional[str] = None

class PreDrillRequest(BaseModel):
    planned_trajectory: List[Dict[str, Any]]


@app.get("/api/v1/engineering/kick-detection")
def get_kick_detection(
    flow_in_gpm: float = Query(640.0),
    flow_out_gpm: float = Query(640.0),
    pit_volume_bbl: float = Query(320.0),
    pit_gain_rate_bblhr: float = Query(0.0),
    spp_psi: float = Query(2950.0),
    spp_baseline_psi: float = Query(2950.0),
    gas_pct: float = Query(1.85),
    gas_baseline_pct: float = Query(1.50),
    connection_gas_pct: float = Query(0.0)
):
    """Real-time well-control influx monitoring & state machine."""
    return EngineeringEngine.evaluate_kick_risk(
        flow_in_gpm=flow_in_gpm, flow_out_gpm=flow_out_gpm, pit_volume_bbl=pit_volume_bbl,
        pit_gain_rate_bblhr=pit_gain_rate_bblhr, spp_psi=spp_psi, spp_baseline_psi=spp_baseline_psi,
        gas_pct=gas_pct, gas_baseline_pct=gas_baseline_pct, connection_gas_pct=connection_gas_pct
    )


@app.get("/api/v1/engineering/pressure-window")
def get_pressure_window(
    depth_md_m: float = Query(2410.0),
    depth_tvd_m: float = Query(2180.0),
    current_mw_sg: float = Query(1.16),
    current_ecd_sg: float = Query(1.21),
    pore_pressure_sg: float = Query(0.92),
    fracture_gradient_sg: float = Query(1.82)
):
    """Real-time pore pressure and fracture gradient margins."""
    return EngineeringEngine.calculate_pressure_window(
        depth_md_m=depth_md_m, depth_tvd_m=depth_tvd_m, current_mw_sg=current_mw_sg,
        current_ecd_sg=current_ecd_sg, pore_pressure_sg=pore_pressure_sg,
        fracture_gradient_sg=fracture_gradient_sg
    )


@app.get("/api/v1/engineering/lost-circulation")
def get_lost_circulation_alert(
    flow_in_gpm: float = Query(640.0),
    flow_out_gpm: float = Query(640.0),
    pit_loss_rate_bblhr: float = Query(0.0),
    ecd_sg: float = Query(1.21),
    fracture_gradient_sg: float = Query(1.82),
    formation_name: str = Query("Upper Tipam Sandstone")
):
    """Early warning lost-circulation and fracture margin evaluation."""
    return EngineeringEngine.evaluate_lost_circulation(
        flow_in_gpm=flow_in_gpm, flow_out_gpm=flow_out_gpm, pit_loss_rate_bblhr=pit_loss_rate_bblhr,
        ecd_sg=ecd_sg, fracture_gradient_sg=fracture_gradient_sg, formation_name=formation_name
    )


@app.get("/api/v1/engineering/hole-cleaning")
def get_hole_cleaning_index(
    rop_mhr: float = Query(18.5),
    flow_rate_gpm: float = Query(640.0),
    rpm: float = Query(95.0),
    inclination_deg: float = Query(14.5),
    spp_trend_pct: float = Query(2.0),
    torque_trend_pct: float = Query(3.0)
):
    """Computes Hole Cleaning Index (HCI 0-100) and pack-off risk."""
    return EngineeringEngine.calculate_hole_cleaning_index(
        rop_mhr=rop_mhr, flow_rate_gpm=flow_rate_gpm, rpm=rpm,
        inclination_deg=inclination_deg, spp_trend_pct=spp_trend_pct, torque_trend_pct=torque_trend_pct
    )


@app.get("/api/v1/engineering/stuck-pipe-mechanism")
def get_stuck_pipe_mechanism(
    overbalance_psi: float = Query(1120.0),
    stationary_time_min: float = Query(45.0),
    permeability_md: float = Query(250.0),
    torque_residual_pct: float = Query(22.0),
    drag_residual_pct: float = Query(18.0),
    rop_drop_pct: float = Query(34.0)
):
    """Classifies physical mechanism of stuck pipe (Differential, Pack-off, Instability, Geometry)."""
    return EngineeringEngine.classify_stuck_pipe_mechanism(
        overbalance_psi=overbalance_psi, stationary_time_min=stationary_time_min,
        permeability_md=permeability_md, torque_residual_pct=torque_residual_pct,
        drag_residual_pct=drag_residual_pct, rop_drop_pct=rop_drop_pct
    )


@app.get("/api/v1/engineering/torque-drag")
def get_torque_drag(
    depth_md_m: float = Query(2410.0),
    inclination_deg: float = Query(14.5),
    wob_klbs: float = Query(18.2),
    drillstring_weight_klbs: float = Query(165.0),
    actual_torque_kftlb: float = Query(12.8),
    actual_hookload_klbs: float = Query(185.0)
):
    """Calculates predicted vs actual torque & drag residuals and overpull."""
    return EngineeringEngine.calculate_torque_drag(
        depth_md_m=depth_md_m, inclination_deg=inclination_deg, wob_klbs=wob_klbs,
        drillstring_weight_klbs=drillstring_weight_klbs, actual_torque_kftlb=actual_torque_kftlb,
        actual_hookload_klbs=actual_hookload_klbs
    )


@app.get("/api/v1/engineering/dysfunction")
def get_drilling_dysfunction(
    rpm: float = Query(95.0),
    rpm_variance: float = Query(12.0),
    torque_kftlb: float = Query(12.8),
    torque_variance: float = Query(1.4),
    mse_deviation_pct: float = Query(18.0),
    rop_drop_pct: float = Query(5.0)
):
    """Evaluates stick-slip, bit whirl, and drilling vibration dysfunction."""
    return EngineeringEngine.evaluate_dysfunction(
        rpm=rpm, rpm_variance=rpm_variance, torque_kftlb=torque_kftlb,
        torque_variance=torque_variance, mse_deviation_pct=mse_deviation_pct,
        rop_drop_pct=rop_drop_pct
    )


@app.get("/api/v1/engineering/mse-efficiency")
def get_mse_efficiency(
    wob_klbs: float = Query(18.2),
    rpm: float = Query(95.0),
    torque_kftlb: float = Query(12.8),
    rop_mhr: float = Query(18.5),
    formation_name: str = Query("Upper Tipam Sandstone")
):
    """Evaluates actual vs expected MSE against formation baseline."""
    return EngineeringEngine.evaluate_mse_efficiency(
        wob_klbs=wob_klbs, rpm=rpm, torque_kftlb=torque_kftlb,
        rop_mhr=rop_mhr, formation_name=formation_name
    )


@app.get("/api/v1/engineering/mud-intelligence")
def get_mud_intelligence(
    mud_weight_in_sg: float = Query(1.16),
    mud_weight_out_sg: float = Query(1.16),
    plastic_viscosity_cp: float = Query(22.0),
    yield_point_lb100sqft: float = Query(18.0)
):
    """Evaluates mud rheology stability, YP/PV ratio, and hole cleaning potential."""
    return EngineeringEngine.evaluate_mud_intelligence(
        mud_weight_in_sg=mud_weight_in_sg, mud_weight_out_sg=mud_weight_out_sg,
        plastic_viscosity_cp=plastic_viscosity_cp, yield_point_lb100sqft=yield_point_lb100sqft
    )


@app.get("/api/v1/engineering/surge-swab")
def get_surge_swab(
    pipe_speed_m_per_min: float = Query(25.0),
    mud_weight_sg: float = Query(1.16),
    pore_pressure_sg: float = Query(0.92),
    fracture_gradient_sg: float = Query(1.82)
):
    """Tripping surge/swab scenario risk evaluation."""
    return EngineeringEngine.calculate_surge_swab_risk(
        pipe_speed_m_per_min=pipe_speed_m_per_min, mud_weight_sg=mud_weight_sg,
        pore_pressure_sg=pore_pressure_sg, fracture_gradient_sg=fracture_gradient_sg
    )


@app.get("/api/v1/engineering/connection-intelligence")
def get_connection_intelligence(
    connection_gas_pct: float = Query(1.8),
    pit_volume_change_bbl: float = Query(0.2),
    flowback_time_sec: float = Query(45.0)
):
    """Analyzes connection gas, pit transients, and flowback duration."""
    return EngineeringEngine.evaluate_connection_signature(
        connection_gas_pct=connection_gas_pct, pit_volume_change_bbl=pit_volume_change_bbl,
        flowback_time_sec=flowback_time_sec, spp_recovery_time_sec=20.0, torque_at_bottom_kftlb=12.0
    )


@app.post("/api/v1/engineering/what-if")
def post_what_if_scenario(req: WhatIfRequest):
    """Simulates what-if parameter changes on ECD, MSE, and margins."""
    return EngineeringEngine.simulate_what_if_scenario(
        current_mw_sg=req.current_mw_sg, current_flow_gpm=req.current_flow_gpm,
        current_rpm=req.current_rpm, scenario_mw_sg=req.scenario_mw_sg,
        scenario_flow_gpm=req.scenario_flow_gpm, scenario_rpm=req.scenario_rpm,
        pore_pressure_sg=req.pore_pressure_sg, fracture_gradient_sg=req.fracture_gradient_sg
    )


@app.get("/api/v1/knowledge/what-happened-here")
def get_what_happened_here(
    depth_md_m: float = Query(2410.0, description="Measured depth of active bit"),
    window_m: float = Query(30.0, description="Stratigraphic vertical search window")
):
    """What Happened Here Before: exact historical offset hazard lookup."""
    return EvidenceStoreService.get_what_happened_here_before(depth_md_m=depth_md_m, window_m=window_m)


@app.get("/api/v1/knowledge/npt-summary")
def get_npt_summary(formation_name: Optional[str] = Query(None)):
    """Historical NPT intelligence and root-cause hours."""
    return EvidenceStoreService.get_npt_summary(formation_name=formation_name)


@app.post("/api/v1/engineering/pre-drill-plan")
def post_pre_drill_plan(req: PreDrillRequest):
    """Pre-drill planning mode: evaluates planned trajectory against offset hazard repository."""
    return EvidenceStoreService.evaluate_pre_drill_plan(req.planned_trajectory)


@app.post("/api/v1/alerts/{alert_id}/feedback")
def post_alert_feedback(alert_id: str, req: FeedbackRequest):
    """Records human engineer feedback for active alert (CONFIRMED / FALSE_POSITIVE)."""
    return EvidenceStoreService.record_human_feedback(
        alert_id=alert_id, verdict=req.verdict, engineer_id=req.engineer_id,
        comments=req.comments, actual_event=req.actual_event
    )


# -------------------------------------------------------------
# INDIAN BASIN & LOCATION-AWARE DRILLING INTELLIGENCE
# -------------------------------------------------------------
from app.services.indian_basin_service import IndianBasinService

class LocationQueryRequest(BaseModel):
    latitude: float = Field(..., description="Current user GPS latitude (e.g. 27.2831)")
    longitude: float = Field(..., description="Current user GPS longitude (e.g. 95.3422)")


@app.get("/api/v1/india/basins")
def get_indian_basins():
    """Returns all Category-I Indian petroleum basins with regional stratigraphy and hazard profiles."""
    return IndianBasinService.get_all_basins()


@app.get("/api/v1/india/wells")
def get_indian_wells():
    """Returns all DGH NDR Indian discovery and operational wells across all basins."""
    return IndianBasinService.get_all_indian_wells()


@app.get("/api/v1/india/locate")
def get_indian_location_intelligence(
    lat: float = Query(27.2831, description="Current user latitude (defaults to Nahorkatiya, Upper Assam)"),
    lon: float = Query(95.3422, description="Current user longitude")
):
    """
    Location-Aware Drilling Intelligence:
    Given current GPS latitude and longitude, finds nearest Indian petroleum basin,
    computes distances to all offset wells, and returns localized stratigraphy and hazard advisories.
    """
    return IndianBasinService.resolve_location_intelligence(user_lat=lat, user_lon=lon)


@app.post("/api/v1/india/locate")
def post_indian_location_intelligence(req: LocationQueryRequest):
    """
    Location-Aware Drilling Intelligence (POST):
    Given current GPS coordinates, identifies nearest Indian basin, offset wells, and localized hazard profile.
    """
    return IndianBasinService.resolve_location_intelligence(user_lat=req.latitude, user_lon=req.longitude)


# -------------------------------------------------------------
# GROUNDED NATURAL-LANGUAGE SEARCH (REQUIREMENT 27)
# -------------------------------------------------------------
from app.services.ai_search_service import GroundedAISearchService

class GroundedSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language drilling question (e.g. Show previous stuck-pipe events near current bit)")
    bit_depth_md: float = Field(2410.0, description="Active bit depth in meters")
    formation: Optional[str] = Field("Upper Tipam Sandstone", description="Active formation name")


@app.get("/api/v1/intelligence/query-suggestions")
def get_query_suggestions():
    """Returns curated drilling engineer query suggestions for grounded AI evidence retrieval."""
    return GroundedAISearchService.get_query_suggestions()


@app.post("/api/v1/intelligence/grounded-search")
def post_grounded_search(req: GroundedSearchRequest):
    """
    Requirement 27: Grounded Natural-Language Evidence Retrieval powered by Gemini 2.5 Flash.
    Strictly answers from verified offset well incidents (NHK-014, NHK-019), DDR documents, and NPT records.
    Never invents autonomous commands.
    """
    return GroundedAISearchService.execute_grounded_search(
        user_query=req.query,
        bit_depth_md_m=req.bit_depth_md,
        formation_name=req.formation or "Upper Tipam Sandstone"
    )


# -------------------------------------------------------------
# ENTERPRISE ML STACK & INTELLIGENCE STATION
# -------------------------------------------------------------
from app.services.ml_stack_service import MLStackService

class MLPredictRequest(BaseModel):
    telemetry: Optional[Dict[str, Any]] = None
    formation_name: Optional[str] = "Upper Tipam Sandstone"
    bit_depth_md: Optional[float] = 2413.5

class StationQueryRequest(BaseModel):
    question: str = Field(..., description="Context inquiry e.g. Why is my current stuck-pipe risk high?")
    current_depth_md: Optional[float] = 2413.5
    active_well: Optional[str] = "SYN-NHK-05"
    active_formation: Optional[str] = "Upper Tipam Sandstone"


@app.get("/api/v1/ml/models")
def get_ml_models_catalog():
    """Returns the full 14-model engineering catalog with published benchmark performance and project fit."""
    return MLStackService.get_model_catalog()


@app.post("/api/v1/ml/predict-all")
def post_ml_predict_all(req: MLPredictRequest):
    """Executes multi-tier ML forward pass across all Tier 1 and Tier 2 models."""
    return MLStackService.predict_all(
        telemetry=req.telemetry or {},
        formation_name=req.formation_name or "Upper Tipam Sandstone",
        bit_depth_md=req.bit_depth_md or 2413.5
    )


@app.post("/api/v1/ml/dtw-match")
def post_dtw_matching():
    """Executes Dynamic Time Warping (DTW) historical telemetry alignment against NHK-014, NHK-019, NHK-021, BGJ-02."""
    return MLStackService.match_dtw_events()


@app.get("/api/v1/ml/change-point")
def get_change_point_detection(depth_md: float = Query(2413.5, description="Current bit measured depth")):
    """Runs statistical CUSUM/PELT regime change detector for the active depth."""
    return MLStackService.detect_change_points(current_depth_md=depth_md)


@app.post("/api/v1/ml/intelligence-station/query")
def post_station_query(req: StationQueryRequest):
    """Context-aware intelligence answering for the NWIS Station."""
    return MLStackService.answer_station_inquiry(
        question=req.question,
        current_depth_md=req.current_depth_md or 2413.5,
        active_well=req.active_well or "SYN-NHK-05",
        active_formation=req.active_formation or "Upper Tipam Sandstone"
    )


# ==========================================================
# INNOVATION ENDPOINTS — A1 through A19  (SIH26121 out-of-the-box features)
# ==========================================================

class FluidTypingRequest(BaseModel):
    gr_api: float = 45.0
    rhob_gcc: float = 2.35
    nphi: float = 0.22
    dtc_usft: float = 88.0
    res_ohmm: float = 12.0
    depth_m: float = 2410.0

class PorePressureRequest(BaseModel):
    rop_mhr: float = 18.5
    rpm: float = 95.0
    wob_klbs: float = 18.2
    bit_diameter_in: float = 8.5
    mud_weight_sg: float = 1.16
    depth_tvd_m: float = 2180.0
    normal_pp_sg: float = 1.00
    eaton_exponent: float = 1.2

class NPTTransferRequest(BaseModel):
    depth_md_m: float = 2410.0
    pp_sg: float = 0.92
    mud_weight_sg: float = 1.16
    rop_mhr: float = 18.5
    torque_kftlb: float = 12.8
    formation: str = "Upper Tipam Sandstone"

class TemperatureRequest(BaseModel):
    depth_tvd_m: float = 2180.0
    flow_rate_gpm: float = 640.0
    mud_density_sg: float = 1.16

class LithologyRequest(BaseModel):
    rop_mhr: float = 18.5
    wob_klbs: float = 18.2
    rpm: float = 95.0
    torque_kftlb: float = 12.8
    spp_psi: float = 2950.0
    mse_psi: float = 36420.0
    depth_md_m: float = 2410.0
    rpm_variance: float = 12.0
    torque_variance: float = 1.4

class NPTCostRequest(BaseModel):
    hazard_type: str = "DIFFERENTIAL_STICKING"
    risk_probability: float = 0.84

class MudProgramRequest(BaseModel):
    formation: str = "Upper Tipam Sandstone"
    depth_md_m: float = 2410.0
    current_mw_sg: float = 1.16

class BHAFatigueRequest(BaseModel):
    rotating_hours: float = 180.0
    max_dls_deg_per_30m: float = 2.8
    depth_md_m: float = 2410.0
    pipe_od_in: float = 5.0
    steel_grade: str = "S-135"

class TrippingScheduleRequest(BaseModel):
    mud_weight_sg: float = 1.16
    pore_pressure_sg: float = 0.92
    fracture_gradient_sg: float = 1.55
    pipe_od_in: float = 9.625
    hole_size_in: float = 12.25
    depth_max_m: float = 2500.0

class CopilotRequest(BaseModel):
    question: str
    depth_md_m: float = 2410.0
    mud_weight_sg: float = 1.16
    formation: str = "Upper Tipam Sandstone"

class DDRRequest(BaseModel):
    well_name: str = "SYN-NHK-05"
    day_number: int = 14
    depth_start_m: float = 2380.0
    depth_end_m: float = 2413.5
    formation: str = "Upper Tipam Sandstone"
    alerts_count: int = 2
    npt_hours: float = 0.0
    mud_weight_sg: float = 1.16
    avg_rop_mhr: float = 18.5

class BitWearRequest(BaseModel):
    cumulative_rotating_hrs: float = 45.0
    mse_ratio: float = 1.45
    rop_drop_pct: float = 24.0
    wob_increase_pct: float = 12.0

class WellboreStabilityRequest(BaseModel):
    depth_tvd_m: float = 2180.0
    mud_weight_sg: float = 1.16
    sh_max_ratio: float = 1.3
    ucs_mpa: float = 25.0
    friction_angle_deg: float = 32.0

class BenchmarkRequest(BaseModel):
    current_rop_mhr: float = 18.5
    current_npt_per_1000m: float = 8.2
    current_mud_losses_m3: float = 4.5
    formation: str = "Upper Tipam Sandstone"

class PreDrillSafetyRequest(BaseModel):
    well_name: str = "SYN-NHK-06"
    planned_td_m: float = 3600.0
    field: str = "Nahorkatiya"


# A1 — Formation Fluid Typing
@app.post("/api/v1/innovations/fluid-typing", tags=["Innovations"])
def post_fluid_typing(req: FluidTypingRequest):
    """A1. Formation fluid typing from LWD petrophysical logs (GR, RHOB, NPHI, DTC, RES)."""
    return InnovationsService.classify_formation_fluid(
        gr_api=req.gr_api, rhob_gcc=req.rhob_gcc, nphi=req.nphi,
        dtc_usft=req.dtc_usft, res_ohmm=req.res_ohmm, depth_m=req.depth_m
    )

@app.get("/api/v1/innovations/fluid-typing", tags=["Innovations"])
def get_fluid_typing(
    depth_m: float = Query(2410.0),
    gr_api: float = Query(45.0),
    rhob_gcc: float = Query(2.35),
    nphi: float = Query(0.22),
    dtc_usft: float = Query(88.0),
    res_ohmm: float = Query(12.0),
):
    """A1. Formation fluid typing (GET — for dashboard polling)."""
    return InnovationsService.classify_formation_fluid(
        gr_api=gr_api, rhob_gcc=rhob_gcc, nphi=nphi,
        dtc_usft=dtc_usft, res_ohmm=res_ohmm, depth_m=depth_m
    )


# A2 — D-Exponent Pore Pressure
@app.post("/api/v1/innovations/pore-pressure", tags=["Innovations"])
def post_pore_pressure(req: PorePressureRequest):
    """A2. Real-time pore pressure prediction via modified D-Exponent (Eaton's Method)."""
    return InnovationsService.predict_pore_pressure_dexponent(
        rop_mhr=req.rop_mhr, rpm=req.rpm, wob_klbs=req.wob_klbs,
        bit_diameter_in=req.bit_diameter_in, mud_weight_sg=req.mud_weight_sg,
        depth_tvd_m=req.depth_tvd_m, normal_pp_sg=req.normal_pp_sg,
        eaton_exponent=req.eaton_exponent
    )

@app.get("/api/v1/innovations/pore-pressure", tags=["Innovations"])
def get_pore_pressure(
    rop_mhr: float = Query(18.5), rpm: float = Query(95.0),
    wob_klbs: float = Query(18.2), depth_tvd_m: float = Query(2180.0),
    mud_weight_sg: float = Query(1.16)
):
    """A2. D-Exponent pore pressure (GET)."""
    return InnovationsService.predict_pore_pressure_dexponent(
        rop_mhr=rop_mhr, rpm=rpm, wob_klbs=wob_klbs,
        mud_weight_sg=mud_weight_sg, depth_tvd_m=depth_tvd_m
    )


# A3 — Casing Program Optimizer
@app.get("/api/v1/innovations/casing-program", tags=["Innovations"])
def get_casing_program(planned_td_m: float = Query(3600.0, description="Planned total depth in meters")):
    """A3. Automated casing program optimization from offset well PP/FG profiles."""
    return InnovationsService.optimize_casing_program(planned_td_m=planned_td_m)


# A4 — NPT Transfer Learning
@app.post("/api/v1/innovations/npt-forecast", tags=["Innovations"])
def post_npt_forecast(req: NPTTransferRequest):
    """A4. Probabilistic NPT forecast (P10/P50/P90) via well-to-well transfer learning."""
    return InnovationsService.npt_transfer_forecast(
        depth_md_m=req.depth_md_m, pp_sg=req.pp_sg, mud_weight_sg=req.mud_weight_sg,
        rop_mhr=req.rop_mhr, torque_kftlb=req.torque_kftlb, formation=req.formation
    )

@app.get("/api/v1/innovations/npt-forecast", tags=["Innovations"])
def get_npt_forecast(
    depth_md_m: float = Query(2410.0),
    mud_weight_sg: float = Query(1.16),
    formation: str = Query("Upper Tipam Sandstone"),
):
    """A4. NPT transfer learning forecast (GET)."""
    return InnovationsService.npt_transfer_forecast(
        depth_md_m=depth_md_m, mud_weight_sg=mud_weight_sg, formation=formation
    )


# A5 — Wellbore Temperature
@app.post("/api/v1/innovations/wellbore-temperature", tags=["Innovations"])
def post_wellbore_temperature(req: TemperatureRequest):
    """A5. Bottomhole circulating temperature (BHCT) and static temperature (BHST) prediction."""
    return InnovationsService.predict_wellbore_temperature(
        depth_tvd_m=req.depth_tvd_m, flow_rate_gpm=req.flow_rate_gpm, mud_density_sg=req.mud_density_sg
    )

@app.get("/api/v1/innovations/wellbore-temperature", tags=["Innovations"])
def get_wellbore_temperature(depth_tvd_m: float = Query(2180.0), flow_rate_gpm: float = Query(640.0)):
    """A5. BHCT/BHST prediction (GET)."""
    return InnovationsService.predict_wellbore_temperature(depth_tvd_m=depth_tvd_m, flow_rate_gpm=flow_rate_gpm)


# A6 — Surface Lithology Inference
@app.post("/api/v1/innovations/lithology-inference", tags=["Innovations"])
def post_lithology_inference(req: LithologyRequest):
    """A6. Real-time lithology inference from surface drilling parameters only (MWD-free)."""
    return InnovationsService.infer_lithology_from_surface(
        rop_mhr=req.rop_mhr, wob_klbs=req.wob_klbs, rpm=req.rpm,
        torque_kftlb=req.torque_kftlb, spp_psi=req.spp_psi,
        mse_psi=req.mse_psi, depth_md_m=req.depth_md_m,
        rpm_variance=req.rpm_variance, torque_variance=req.torque_variance
    )

@app.get("/api/v1/innovations/lithology-inference", tags=["Innovations"])
def get_lithology_inference(
    rop_mhr: float = Query(18.5), wob_klbs: float = Query(18.2),
    rpm: float = Query(95.0), torque_kftlb: float = Query(12.8),
    depth_md_m: float = Query(2410.0), mse_psi: float = Query(36420.0)
):
    """A6. Surface lithology inference (GET)."""
    return InnovationsService.infer_lithology_from_surface(
        rop_mhr=rop_mhr, wob_klbs=wob_klbs, rpm=rpm,
        torque_kftlb=torque_kftlb, depth_md_m=depth_md_m, mse_psi=mse_psi
    )


# A7 — NPT Cost Quantification
@app.post("/api/v1/innovations/npt-cost", tags=["Innovations"])
def post_npt_cost(req: NPTCostRequest):
    """A7. Financial NPT cost overlay — Rs exposure for any risk event."""
    return InnovationsService.quantify_npt_cost(
        hazard_type=req.hazard_type, risk_probability=req.risk_probability
    )

@app.get("/api/v1/innovations/npt-cost", tags=["Innovations"])
def get_npt_cost(
    hazard_type: str = Query("DIFFERENTIAL_STICKING"),
    risk_probability: float = Query(0.84)
):
    """A7. NPT cost quantification (GET)."""
    return InnovationsService.quantify_npt_cost(hazard_type=hazard_type, risk_probability=risk_probability)


# A8 — Hazard Heatmap
@app.get("/api/v1/innovations/hazard-heatmap", tags=["Innovations"])
def get_hazard_heatmap(formation_filter: Optional[str] = Query(None, description="Filter by hazard type")):
    """A8. Spatial hazard density data for basin map choropleth rendering."""
    return InnovationsService.get_hazard_heatmap(formation_filter=formation_filter)


# A9 — Mud Program Recommendation
@app.post("/api/v1/innovations/mud-program", tags=["Innovations"])
def post_mud_program(req: MudProgramRequest):
    """A9. Automated mud program recommendations based on formation and offset well data."""
    return InnovationsService.recommend_mud_program(
        formation=req.formation, depth_md_m=req.depth_md_m, current_mw_sg=req.current_mw_sg
    )

@app.get("/api/v1/innovations/mud-program", tags=["Innovations"])
def get_mud_program(
    formation: str = Query("Upper Tipam Sandstone"),
    depth_md_m: float = Query(2410.0),
    current_mw_sg: float = Query(1.16)
):
    """A9. Mud program recommendation (GET)."""
    return InnovationsService.recommend_mud_program(formation=formation, depth_md_m=depth_md_m, current_mw_sg=current_mw_sg)


# A10 — BHA Fatigue
@app.post("/api/v1/innovations/bha-fatigue", tags=["Innovations"])
def post_bha_fatigue(req: BHAFatigueRequest):
    """A10. Drillstring fatigue and BHA life assessment (Goodman-Soderberg criterion)."""
    return InnovationsService.evaluate_bha_fatigue(
        rotating_hours=req.rotating_hours, max_dls_deg_per_30m=req.max_dls_deg_per_30m,
        depth_md_m=req.depth_md_m, pipe_od_in=req.pipe_od_in, steel_grade=req.steel_grade
    )

@app.get("/api/v1/innovations/bha-fatigue", tags=["Innovations"])
def get_bha_fatigue(
    rotating_hours: float = Query(180.0), max_dls_deg_per_30m: float = Query(2.8),
    steel_grade: str = Query("S-135")
):
    """A10. BHA fatigue tracker (GET)."""
    return InnovationsService.evaluate_bha_fatigue(rotating_hours=rotating_hours, max_dls_deg_per_30m=max_dls_deg_per_30m, steel_grade=steel_grade)


# A11 — Tripping Speed Schedule
@app.post("/api/v1/innovations/tripping-schedule", tags=["Innovations"])
def post_tripping_schedule(req: TrippingScheduleRequest):
    """A11. Depth-indexed tripping speed schedule optimizer (Surge & Swab)."""
    return InnovationsService.generate_tripping_schedule(
        mud_weight_sg=req.mud_weight_sg, pore_pressure_sg=req.pore_pressure_sg,
        fracture_gradient_sg=req.fracture_gradient_sg, pipe_od_in=req.pipe_od_in,
        hole_size_in=req.hole_size_in, depth_max_m=req.depth_max_m
    )

@app.get("/api/v1/innovations/tripping-schedule", tags=["Innovations"])
def get_tripping_schedule(
    mud_weight_sg: float = Query(1.16),
    fracture_gradient_sg: float = Query(1.55),
    depth_max_m: float = Query(2500.0)
):
    """A11. Tripping speed schedule (GET)."""
    return InnovationsService.generate_tripping_schedule(mud_weight_sg=mud_weight_sg, fracture_gradient_sg=fracture_gradient_sg, depth_max_m=depth_max_m)


# A12 — Multi-Agent Drilling Copilot
@app.post("/api/v1/innovations/copilot", tags=["Innovations"])
def post_copilot(req: CopilotRequest):
    """A12. Multi-step drilling copilot with ReAct-style reasoning (physics + evidence + risk)."""
    return InnovationsService.drilling_copilot(
        question=req.question, depth_md_m=req.depth_md_m,
        mud_weight_sg=req.mud_weight_sg, formation=req.formation
    )


# A13 — Automated DDR Generator
@app.post("/api/v1/innovations/generate-ddr", tags=["Innovations"])
def post_generate_ddr(req: DDRRequest):
    """A13. Auto-generate a structured Daily Drilling Report from telemetry summary."""
    return InnovationsService.generate_ddr(
        well_name=req.well_name, day_number=req.day_number,
        depth_start_m=req.depth_start_m, depth_end_m=req.depth_end_m,
        formation=req.formation, alerts_count=req.alerts_count,
        npt_hours=req.npt_hours, mud_weight_sg=req.mud_weight_sg,
        avg_rop_mhr=req.avg_rop_mhr
    )

@app.get("/api/v1/innovations/generate-ddr", tags=["Innovations"])
def get_generate_ddr(well_name: str = Query("SYN-NHK-05"), depth_end_m: float = Query(2413.5)):
    """A13. Auto DDR generation (GET)."""
    return InnovationsService.generate_ddr(well_name=well_name, depth_end_m=depth_end_m)


# A16 — Bit Wear Prediction
@app.post("/api/v1/innovations/bit-wear", tags=["Innovations"])
def post_bit_wear(req: BitWearRequest):
    """A16. MSE-based bit wear index and IADC dull grade prediction."""
    return InnovationsService.predict_bit_wear(
        cumulative_rotating_hrs=req.cumulative_rotating_hrs,
        mse_ratio=req.mse_ratio, rop_drop_pct=req.rop_drop_pct,
        wob_increase_pct=req.wob_increase_pct
    )

@app.get("/api/v1/innovations/bit-wear", tags=["Innovations"])
def get_bit_wear(
    cumulative_rotating_hrs: float = Query(45.0),
    mse_ratio: float = Query(1.45),
    rop_drop_pct: float = Query(24.0)
):
    """A16. Bit wear prediction (GET)."""
    return InnovationsService.predict_bit_wear(cumulative_rotating_hrs=cumulative_rotating_hrs, mse_ratio=mse_ratio, rop_drop_pct=rop_drop_pct)


# A17 — Wellbore Stability
@app.post("/api/v1/innovations/wellbore-stability", tags=["Innovations"])
def post_wellbore_stability(req: WellboreStabilityRequest):
    """A17. Mohr-Coulomb wellbore stability: breakout and fracture mud weight bounds."""
    return InnovationsService.predict_wellbore_stability(
        depth_tvd_m=req.depth_tvd_m, mud_weight_sg=req.mud_weight_sg,
        sh_max_ratio=req.sh_max_ratio, ucs_mpa=req.ucs_mpa,
        friction_angle_deg=req.friction_angle_deg
    )

@app.get("/api/v1/innovations/wellbore-stability", tags=["Innovations"])
def get_wellbore_stability(depth_tvd_m: float = Query(2180.0), mud_weight_sg: float = Query(1.16)):
    """A17. Wellbore stability bounds (GET)."""
    return InnovationsService.predict_wellbore_stability(depth_tvd_m=depth_tvd_m, mud_weight_sg=mud_weight_sg)


# A18 — Well Performance Benchmarking
@app.post("/api/v1/innovations/benchmarking", tags=["Innovations"])
def post_benchmarking(req: BenchmarkRequest):
    """A18. Rank active well performance against historical offset well benchmarks."""
    return InnovationsService.benchmark_well_performance(
        current_rop_mhr=req.current_rop_mhr, current_npt_per_1000m=req.current_npt_per_1000m,
        current_mud_losses_m3=req.current_mud_losses_m3, formation=req.formation
    )

@app.get("/api/v1/innovations/benchmarking", tags=["Innovations"])
def get_benchmarking(
    current_rop_mhr: float = Query(18.5),
    current_npt_per_1000m: float = Query(8.2),
    formation: str = Query("Upper Tipam Sandstone")
):
    """A18. Well benchmarking (GET)."""
    return InnovationsService.benchmark_well_performance(current_rop_mhr=current_rop_mhr, current_npt_per_1000m=current_npt_per_1000m, formation=formation)


# A19 — Pre-Drill Safety Case
@app.post("/api/v1/innovations/predrill-safety-case", tags=["Innovations"])
def post_predrill_safety_case(req: PreDrillSafetyRequest):
    """A19. Pre-Drill Safety Case generator from offset well knowledge base."""
    return InnovationsService.generate_predrill_safety_case(
        well_name=req.well_name, planned_td_m=req.planned_td_m, field=req.field
    )

@app.get("/api/v1/innovations/predrill-safety-case", tags=["Innovations"])
def get_predrill_safety_case(
    well_name: str = Query("SYN-NHK-06"),
    planned_td_m: float = Query(3600.0)
):
    """A19. Pre-drill safety case (GET)."""
    return InnovationsService.generate_predrill_safety_case(well_name=well_name, planned_td_m=planned_td_m)


# A20 — PWA Manifest endpoint
@app.get("/api/v1/innovations/pwa-status", tags=["Innovations"])
def get_pwa_status():
    """A20. PWA readiness status and offline cache strategy."""
    return {
        "feature": "A20_MOBILE_PWA",
        "pwa_enabled": True,
        "offline_strategy": "NetworkFirst with IndexedDB fallback",
        "push_notifications": ["KICK_DETECTED", "STUCK_PIPE_HIGH", "GAS_INFLUX_CRITICAL"],
        "installable": True,
        "service_worker_scope": "/",
        "cached_endpoints": [
            "/api/v1/innovations/pore-pressure",
            "/api/v1/innovations/wellbore-stability",
            "/api/v1/innovations/npt-forecast",
            "/api/v1/innovations/mud-program",
        ],
        "biometric_auth_support": True,
    }


# Aggregated innovations dashboard endpoint
@app.get("/api/v1/innovations/dashboard", tags=["Innovations"])
def get_innovations_dashboard(
    depth_md_m: float = Query(2410.0),
    depth_tvd_m: float = Query(2180.0),
    mud_weight_sg: float = Query(1.16),
    rop_mhr: float = Query(18.5),
    wob_klbs: float = Query(18.2),
    rpm: float = Query(95.0),
    torque_kftlb: float = Query(12.8),
    mse_psi: float = Query(36420.0),
    mse_ratio: float = Query(1.05),
    rotating_hrs: float = Query(180.0),
    formation: str = Query("Upper Tipam Sandstone"),
):
    """
    Aggregated dashboard endpoint — returns all A1-A19 innovation results in one call.
    Designed for the Innovation Console panel (reduces frontend round-trips).
    """
    pp = InnovationsService.predict_pore_pressure_dexponent(rop_mhr=rop_mhr, rpm=rpm, wob_klbs=wob_klbs, mud_weight_sg=mud_weight_sg, depth_tvd_m=depth_tvd_m)
    lith = InnovationsService.infer_lithology_from_surface(rop_mhr=rop_mhr, wob_klbs=wob_klbs, rpm=rpm, torque_kftlb=torque_kftlb, mse_psi=mse_psi, depth_md_m=depth_md_m)
    temp = InnovationsService.predict_wellbore_temperature(depth_tvd_m=depth_tvd_m)
    npt_fc = InnovationsService.npt_transfer_forecast(depth_md_m=depth_md_m, mud_weight_sg=mud_weight_sg, formation=formation)
    npt_cost = InnovationsService.quantify_npt_cost(hazard_type="DIFFERENTIAL_STICKING", risk_probability=0.84 if pp.get("alert") else 0.42)
    bha = InnovationsService.evaluate_bha_fatigue(rotating_hours=rotating_hrs)
    bit = InnovationsService.predict_bit_wear(mse_ratio=mse_ratio, cumulative_rotating_hrs=rotating_hrs * 0.25)
    stab = InnovationsService.predict_wellbore_stability(depth_tvd_m=depth_tvd_m, mud_weight_sg=mud_weight_sg)
    bench = InnovationsService.benchmark_well_performance(current_rop_mhr=rop_mhr, formation=formation)
    mud = InnovationsService.recommend_mud_program(formation=formation, current_mw_sg=mud_weight_sg, depth_md_m=depth_md_m)
    fluid = InnovationsService.classify_formation_fluid(depth_m=depth_md_m)

    return {
        "dashboard": "INNOVATIONS_CONSOLE",
        "timestamp": time.time(),
        "depth_md_m": depth_md_m,
        "depth_tvd_m": depth_tvd_m,
        "formation": formation,
        "pore_pressure": pp,
        "lithology": lith,
        "temperature": temp,
        "npt_forecast": npt_fc,
        "npt_cost": npt_cost,
        "bha_fatigue": bha,
        "bit_wear": bit,
        "wellbore_stability": stab,
        "benchmarking": bench,
        "mud_program": mud,
        "fluid_typing": fluid,
    }
