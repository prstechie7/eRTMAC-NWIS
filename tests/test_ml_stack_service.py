import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ml_stack_service import MLStackService

client = TestClient(app)


def test_ml_model_catalog_endpoint():
    """Verifies that all 14 models across P0/P1/P2 tiers are present in the catalog."""
    response = client.get("/api/v1/ml/models")
    assert response.status_code == 200
    catalog = response.json()
    assert len(catalog) == 14

    names = [m["name"] for m in catalog]
    assert any("Stuck Pipe" in n for n in names)
    assert any("Lost Circulation" in n for n in names)
    assert any("Kick" in n for n in names)
    assert any("ROP" in n for n in names)
    assert any("Torque" in n for n in names)
    assert any("Drag" in n for n in names)
    assert any("Stick-Slip" in n for n in names)
    assert any("Lithology" in n for n in names)
    assert any("Anomaly Detector" in n or "Isolation Forest" in n for n in names)
    assert any("Isolation Forest" in m["models"] for m in catalog)
    assert any("Change-Point" in n for n in names)
    assert any("Dynamic Time Warping" in n for n in names)
    assert any("KNN" in n for n in names)
    assert any("SHAP" in n for n in names)

    for m in catalog:
        assert "priority" in m
        assert "project_fit_pct" in m and m["project_fit_pct"] >= 80
        assert "published_benchmark" in m
        assert "decision_support" in m


def test_ml_predict_all_stuck_pipe_ensemble():
    """Verifies Extra Trees + Gradient Boosting ensemble prediction for Stuck Pipe."""
    payload = {
        "telemetry": {
            "measured_depth_m": 2415.0,
            "surface_torque_kftlb": 15.8,
            "rop_mhr": 10.5,
            "wob_klbs": 22.0
        },
        "formation_name": "Upper Tipam Sandstone",
        "bit_depth_md": 2415.0
    }
    response = client.post("/api/v1/ml/predict-all", json=payload)
    assert response.status_code == 200
    data = response.json()

    stuck = data["stuck_pipe"]
    assert "probability" in stuck
    assert stuck["risk_level"] in ["MEDIUM", "HIGH"]
    assert "likely_mechanism" in stuck
    assert "ensemble_breakdown" in stuck
    assert "extra_trees_prob" in stuck["ensemble_breakdown"]
    assert "gradient_boosting_prob" in stuck["ensemble_breakdown"]
    assert len(stuck["shap_factors"]) >= 4

    # Verify safety guardrails
    assert data["engineer_review_required"] is True
    assert data["autonomous_control"] is False


def test_ml_dtw_historical_matching():
    """Verifies Dynamic Time Warping (DTW) matching against offset incident templates."""
    response = client.post("/api/v1/ml/dtw-match")
    assert response.status_code == 200
    matches = response.json()
    assert len(matches) >= 4

    well_names = [m["well_name"] for m in matches]
    assert "NHK-014" in well_names
    assert "NHK-019" in well_names
    assert "NHK-021" in well_names
    assert "BGJ-02" in well_names

    # Check top match similarity percentage
    top_match = matches[0]
    assert top_match["similarity_pct"] >= 75.0
    assert "source_document" in top_match


def test_ml_change_point_regime_detection():
    """Verifies CUSUM change-point detection flags formation transition at 2,397m."""
    # Pre-transition
    res_normal = client.get("/api/v1/ml/change-point?depth_md=2350.0")
    assert res_normal.status_code == 200
    data_normal = res_normal.json()
    assert data_normal["regime_status"] == "STEADY_DRILLING"
    assert data_normal["transition_detected"] is False

    # Hazard regime
    res_hazard = client.get("/api/v1/ml/change-point?depth_md=2415.0")
    assert res_hazard.status_code == 200
    data_hazard = res_hazard.json()
    assert data_hazard["regime_status"] == "HAZARD_REGIME_ACTIVE"
    assert data_hazard["transition_detected"] is True
    assert data_hazard["detected_change_depth_m"] == 2397.5


def test_ml_intelligence_station_query():
    """Verifies context-aware Intelligence Station answering."""
    payload = {
        "question": "Why is my current stuck-pipe risk high?",
        "current_depth_md": 2415.0,
        "active_well": "SYN-NHK-05",
        "active_formation": "Upper Tipam Sandstone"
    }
    response = client.post("/api/v1/ml/intelligence-station/query", json=payload)
    assert response.status_code == 200
    station_data = response.json()

    assert "answer" in station_data
    assert len(station_data["answer"]) > 100
    assert "Torque Residual" in station_data["answer"]
    assert "NHK-014" in station_data["answer"]
    assert station_data["engineer_review_required"] is True
    assert station_data["autonomous_control"] is False
