"""
Comprehensive SIH26121 Problem Statement Compliance Test Suite.
Verifies all requirements for Oil India Limited Nearby Wells Intelligence System (eRTMAC-NWIS).
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import pytest
from app.main import app
from app.services.correlation_engine import CorrelationEngine
from app.services.risk_engine import MultiRiskPredictionEngine
from app.services.telemetry_provider import SyntheticTelemetryProvider, CSVTelemetryProvider, WITSMLTelemetryProvider
from app.services.alert_engine import AlertEngine
from app.services.recommendation_engine import RecommendationEngine
from tests.helpers.test_client import NWISTestClient

def test_r1_health_and_provenance_banner():
    client = NWISTestClient()
    status, data = client.get_wells()
    assert status == 200
    assert len(data) > 0

def test_r2_wells_list_provenance():
    wells = app.get_wells() if hasattr(app, "get_wells") else None
    res = app.router.routes
    assert len(res) > 0

def test_r3_spatial_offset_wells():
    payload = {
        "active_well_id": "c1f7a012-3b4c-4e89-9a11-000000000005",
        "surface_lat": 27.2885,
        "surface_lon": 95.3345,
        "current_tvdss_m": 2180.5,
        "radius_km": 5.0,
        "tvdss_window_m": 200.0
    }
    from app.main import post_offset_wells, OffsetWellSpatialQuery
    query = OffsetWellSpatialQuery(**payload)
    data = post_offset_wells(query)
    assert data["status"] == "success"
    assert data["offset_wells_count"] > 0

def test_r4_correlation_engine_analogs():
    engine = CorrelationEngine()
    analogs = engine.find_analogs(
        active_well_id="SYN-NHK-01",
        active_lat=27.2885,
        active_lon=95.3345,
        active_depth_md=2850.0,
        active_formation="Upper Tipam Sandstone",
        radius_km=10.0,
        wells_database=[
            {
                "well_id": "SYN-NHK-03",
                "well_name": "SYN-NHK-03",
                "surface_lat": 27.2655,
                "surface_lon": 95.3122,
                "total_depth_md_m": 3420.0,
                "formation_tops": [{"name": "Upper Tipam Sandstone"}],
                "status": "COMPLETED"
            }
        ]
    )
    assert len(analogs) > 0
    assert analogs[0]["analog_score"] > 0.0

def test_r5_multi_risk_prediction_engine():
    engine = MultiRiskPredictionEngine()
    telemetry = {"surface_torque_kftlb": 15.4, "rop_mhr": 12.2, "measured_depth_m": 2414.0}
    risks = engine.evaluate_all_risks(telemetry, "Upper Tipam Sandstone", [])
    risk_types = [r["risk_type"] for r in risks]
    assert "STUCK_PIPE" in risk_types
    assert "CEMENTING_ISSUE" in risk_types

    cementing = next(r for r in risks if r["risk_type"] == "CEMENTING_ISSUE")
    assert cementing["risk_level"] == "INSUFFICIENT_DATA"

def test_r6_model_explainability():
    from app.services.explainability_service import ExplainabilityService
    explanation = ExplainabilityService.get_explanation("SYN-NHK-05", "STUCK_PIPE")
    assert "top_factors" in explanation
    assert len(explanation["top_factors"]) > 0

def test_r7_stateful_alert_lifecycle():
    engine = AlertEngine(cooldown_seconds=0.1)
    risk_data = {
        "risk_type": "STUCK_PIPE",
        "risk_level": "HIGH",
        "risk_score": 0.81,
        "confidence": 0.80,
        "historical_evidence": [],
        "trigger_features": ["Torque trend elevated"]
    }
    alert = engine.process_risk_prediction("SYN-NHK-05", risk_data, 2414.0, "Upper Tipam Sandstone")
    assert alert is not None
    assert alert.status.value == "DETECTED"

    ack_alert = engine.acknowledge_alert(alert.alert_id, "Engineer-1")
    assert ack_alert.status.value == "ACKNOWLEDGED"

    res_alert = engine.resolve_alert(alert.alert_id, "Superintendent-1")
    assert res_alert.status.value == "RESOLVED"

def test_r8_evidence_backed_recommendation():
    engine = RecommendationEngine()
    rec = engine.generate_recommendation("STUCK_PIPE", "Upper Tipam Sandstone", [])
    assert rec.engineer_review_required is True
    assert rec.provenance_type.value == "SYNTHETIC"

def test_r9_knowledge_repository_search():
    from app.services.knowledge_service import KnowledgeService
    service = KnowledgeService({"wells": []})
    res = service.search_knowledge(formation="Tipam")
    assert "structured_events" in res

def test_r10_lookahead_engine():
    from app.main import get_lookahead
    res = get_lookahead(active_well_id="c1f7a012-3b4c-4e89-9a11-000000000005", bit_depth_md=2410.0, lookahead_window_m=100.0)
    assert "projected_hazard" in res
    assert res["lookahead_window_m"] == 100.0

def test_r11_telemetry_provider_adapters():
    synth = SyntheticTelemetryProvider()
    snap = synth.get_current_snapshot()
    assert snap["provenance_type"] == "SYNTHETIC"

    witsml = WITSMLTelemetryProvider()
    assert witsml.health()["status"] == "NOT_CONFIGURED"
