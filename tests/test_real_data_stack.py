"""
Test suite validating real data stack connectivity and endpoints.
Verifies DGH NDR Indian wells, FORCE 2020 wireline logs, and CirculationDataV2 telemetry.
"""

import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import pytest
from app.main import app
from app.services.real_data_service import RealDataService
from tests.helpers.test_client import NWISTestClient


def test_data_sources_summary_connected():
    summary = RealDataService.get_data_sources_summary()
    assert summary["status"] == "CONNECTED_AND_ACTIVE"
    assert summary["dgh_ndr"]["connected_wells"] >= 5
    assert summary["force2020"]["status"] == "LOADED"
    assert summary["lost_circulation"]["status"] == "LOADED"
    assert summary["lost_circulation"]["total_telemetry_records"] > 60000


def test_dgh_real_wells_grounding():
    wells = RealDataService.get_dgh_real_wells()
    assert len(wells) >= 5
    well_names = [w["well_name"] for w in wells]
    assert any("Nahorkatiya" in name for name in well_names)
    assert any("Moran" in name for name in well_names)
    assert any("Baghjan" in name for name in well_names)

    nhk = next(w for w in wells if "NHK-01" in w["well_id"])
    assert nhk["surface_lat"] > 27.0
    assert nhk["surface_lon"] > 95.0
    assert nhk["provenance_type"] == "PUBLIC"
    assert len(nhk["formation_tops"]) > 0


def test_force2020_real_logs_query():
    logs = RealDataService.get_real_force_logs(well_name="15/9-14", limit=10)
    assert len(logs) == 10
    first = logs[0]
    assert first["well_name"] == "15/9-14"
    assert first["depth_md"] > 400.0
    assert "gamma_ray_gapi" in first
    assert "bulk_density_gcm3" in first
    assert "deep_resistivity_ohmm" in first
    assert first["provenance_type"] == "PUBLIC (FORCE 2020)"


def test_circulation_real_telemetry_query():
    records = RealDataService.get_real_circulation_data(limit=10)
    assert len(records) == 10
    first = records[0]
    assert "measured_depth_m" in first
    assert "rop_mhr" in first
    assert "surface_torque_kftlb" in first
    assert "standpipe_pressure_psi" in first
    assert "flow_rate_in_gpm" in first
    assert "flow_rate_out_gpm" in first
    assert first["provenance_type"] == "PUBLIC (CirculationDataV2)"


def test_api_wells_with_real_included():
    from app.main import list_wells
    all_wells = list_wells(include_real=True)
    assert len(all_wells) >= 8
    public_wells = [w for w in all_wells if w["provenance_type"] == "PUBLIC"]
    assert len(public_wells) >= 5
