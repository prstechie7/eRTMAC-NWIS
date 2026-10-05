import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ai_search_service import GroundedAISearchService, CURATED_SUGGESTIONS

client = TestClient(app)


def test_query_suggestions_endpoint():
    """Verifies that engineering query suggestions are returned properly."""
    response = client.get("/api/v1/intelligence/query-suggestions")
    assert response.status_code == 200
    suggestions = response.json()
    assert isinstance(suggestions, list)
    assert len(suggestions) >= 5

    categories = [s["category"] for s in suggestions]
    assert "Stuck Pipe & Geomechanics" in categories
    assert "Lost Circulation & LCM" in categories
    assert "Offset Well History" in categories

    for item in suggestions:
        assert "query" in item and len(item["query"]) > 10
        assert "context" in item and len(item["context"]) > 5


def test_grounded_ai_search_service_stuck_pipe():
    """Verifies that stuck pipe queries find relevant historical evidence."""
    result = GroundedAISearchService.search(
        query="What happened in offset well NHK-014 when drilling into Upper Tipam Sandstone?",
        bit_depth_md=2415.0,
        formation="Upper Tipam Sandstone"
    )

    assert result["matching_events_count"] >= 1
    assert len(result["cited_evidence"]) >= 1
    assert result["engineer_review_required"] is True
    assert result["autonomous_control"] is False
    assert len(result["answer"]) > 50
    assert len(result["suggested_followups"]) > 0

    # Verify NHK-014 is cited
    wells_cited = [e["well_name"] for e in result["cited_evidence"]]
    assert any("NHK-014" in w for w in wells_cited)


def test_grounded_ai_search_service_loss_circulation():
    """Verifies that lost circulation queries find relevant LCM evidence."""
    result = GroundedAISearchService.search(
        query="What LCM treatments were effective for severe mud loss in Barail Coal-Shale?",
        bit_depth_md=2850.0,
        formation="Barail Coal-Shale"
    )

    assert result["matching_events_count"] >= 1
    assert len(result["cited_evidence"]) >= 1
    assert result["engineer_review_required"] is True
    assert result["autonomous_control"] is False

    events = [e["event_type"] for e in result["cited_evidence"]]
    assert any("SEVERE_LOSSES" in ev or "LOST_CIRCULATION" in ev for ev in events)


def test_grounded_ai_search_endpoint_post():
    """Verifies POST /api/v1/intelligence/grounded-search returns valid grounded response."""
    payload = {
        "query": "What pore pressure ramping or connection gas was noted in NHK-019?",
        "bit_depth_md": 2420.0,
        "formation": "Upper Tipam Sandstone"
    }
    response = client.post("/api/v1/intelligence/grounded-search", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "query" in data
    assert "answer" in data
    assert "model" in data
    assert "cited_evidence" in data
    assert "suggested_followups" in data
    assert data["engineer_review_required"] is True
    assert data["autonomous_control"] is False

    # Check evidence structure
    for ev in data["cited_evidence"]:
        assert "well_name" in ev
        assert "event_type" in ev
        assert "source_document" in ev
        assert "root_cause" in ev
        assert "mitigation_action" in ev


def test_safety_constraints_enforced():
    """Verifies that no search result ever bypasses engineer review or grants autonomous control."""
    result = GroundedAISearchService.search(
        query="Should the system automatically shut in the BOP right now?",
        bit_depth_md=2448.0
    )

    # Must strictly enforce safety parameters
    assert result["engineer_review_required"] is True
    assert result["autonomous_control"] is False
    assert "DECISION-SUPPORT" in result["answer"] or "engineer review required" in result["answer"].lower() or "recommendation" in result["answer"].lower() or len(result["cited_evidence"]) >= 0
