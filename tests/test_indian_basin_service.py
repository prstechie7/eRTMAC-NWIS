import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import pytest
from app.services.indian_basin_service import IndianBasinService, INDIAN_BASINS, INDIAN_ALL_WELLS
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_indian_basins_registry():
    """Verifies all Category-I Indian basins are loaded with DGH classifications and stratigraphy."""
    basins = IndianBasinService.get_all_basins()
    assert len(basins) >= 6

    basin_names = [b["name"] for b in basins]
    assert any("Assam-Arakan" in name for name in basin_names)
    assert any("Cambay" in name for name in basin_names)
    assert any("Barmer" in name for name in basin_names)
    assert any("Krishna-Godavari" in name for name in basin_names)
    assert any("Mumbai High" in name for name in basin_names)
    assert any("Cauvery" in name for name in basin_names)

    # Check Assam Basin details
    assam = next(b for b in basins if "Assam-Arakan" in b["name"])
    assert "Oil India Limited" in assam["primary_operator"]
    assert len(assam["stratigraphic_column"]) >= 7
    assert any("Upper Tipam Sandstone" in u["formation"] for u in assam["stratigraphic_column"])
    assert len(assam["regional_hazards"]) > 0


def test_indian_discovery_wells_registry():
    """Verifies DGH NDR Indian discovery and operational wells."""
    wells = IndianBasinService.get_all_indian_wells()
    assert len(wells) >= 10

    well_ids = [w["well_id"] for w in wells]
    assert "DGH-IND-NHK-01" in well_ids
    assert "DGH-IND-MORAN-01" in well_ids
    assert "DGH-IND-BGJ-05" in well_ids
    assert "DGH-IND-DIGBOI-01" in well_ids
    assert "DGH-IND-MANGALA-01" in well_ids
    assert "DGH-IND-ANK-01" in well_ids
    assert "DGH-IND-RAVVA-01" in well_ids
    assert "DGH-IND-BH-01" in well_ids


def test_haversine_distance():
    """Tests great-circle distance calculations."""
    # Nahorkatiya (27.2831, 95.3422) to Digboi (27.3800, 95.6300) is approx ~30.4 km
    d = IndianBasinService.haversine_distance_km(27.2831, 95.3422, 27.3800, 95.6300)
    assert 25.0 < d < 35.0

    # Same point distance should be zero
    d_zero = IndianBasinService.haversine_distance_km(27.2831, 95.3422, 27.2831, 95.3422)
    assert d_zero == 0.0


def test_location_resolution_upper_assam():
    """Tests proximity resolution when user coordinates are in Upper Assam."""
    res = IndianBasinService.resolve_location_intelligence(27.2831, 95.3422)

    assert res["user_location"]["within_oil_field_perimeter"] is True
    assert "Assam-Arakan" in res["nearest_basin"]["name"]
    assert "Oil India Limited" in res["nearest_basin"]["primary_operator"]
    assert res["nearest_offset_well"]["well_id"] == "DGH-IND-NHK-01"
    assert res["nearest_offset_well"]["distance_km"] == 0.0
    assert len(res["nearby_offset_wells"]) == 5
    assert len(res["all_indian_basins_ranked"]) == 6
    assert res["engineer_review_required"] is True


def test_location_resolution_barmer_rajasthan():
    """Tests proximity resolution when user coordinates are in Rajasthan (Barmer)."""
    res = IndianBasinService.resolve_location_intelligence(25.8200, 71.4200)

    assert res["user_location"]["within_oil_field_perimeter"] is True
    assert "Barmer" in res["nearest_basin"]["name"]
    assert "Cairn" in res["nearest_basin"]["primary_operator"]
    assert res["nearest_offset_well"]["well_id"] == "DGH-IND-MANGALA-01"
    assert res["nearest_offset_well"]["distance_km"] == 0.0


def test_location_resolution_mumbai_offshore():
    """Tests proximity resolution when user coordinates are offshore Mumbai."""
    res = IndianBasinService.resolve_location_intelligence(19.4200, 71.3300)

    assert "Mumbai High" in res["nearest_basin"]["name"]
    assert "ONGC" in res["nearest_basin"]["primary_operator"]
    assert res["nearest_offset_well"]["well_id"] == "DGH-IND-BH-01"


def test_api_endpoints_indian_intelligence():
    """Tests FastAPI HTTP endpoints for Indian basins and location lookup."""
    # 1. GET Basins
    resp = client.get("/api/v1/india/basins")
    assert resp.status_code == 200
    basins = resp.json()
    assert len(basins) >= 6

    # 2. GET Wells
    resp = client.get("/api/v1/india/wells")
    assert resp.status_code == 200
    wells = resp.json()
    assert len(wells) >= 10

    # 3. GET Locate
    resp = client.get("/api/v1/india/locate?lat=27.2831&lon=95.3422")
    assert resp.status_code == 200
    data = resp.json()
    assert data["nearest_basin"]["name"] == "Assam-Arakan Basin (Upper Assam Shelf)"
    assert data["nearest_offset_well"]["field_name"] == "Nahorkatiya"

    # 4. POST Locate
    resp = client.post("/api/v1/india/locate", json={"latitude": 21.6312, "longitude": 73.0125})
    assert resp.status_code == 200
    data = resp.json()
    assert "Cambay" in data["nearest_basin"]["name"]
    assert data["nearest_offset_well"]["field_name"] == "Ankleshwar"
