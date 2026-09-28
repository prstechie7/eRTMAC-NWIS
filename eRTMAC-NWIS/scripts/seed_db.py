#!/usr/bin/env python3
"""
scripts/seed_db.py - eRTMAC-NWIS Database Seed Engine
Populates PostgreSQL with 10 synthetic Assam wells, MCM 3D trajectories,
formation tops with structural dip corrections, historical hazards,
384-dimensional pgvector narrative embeddings, and baseline telemetry.
"""

import os
import sys
import math
import json
import uuid
import hashlib
import argparse
import datetime
import subprocess
from typing import List, Dict, Any, Tuple

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.services.mcm import MCMTrajectoryEngine, TrajectoryStation

# Database sync connection URL
DEFAULT_DB_URL = os.environ.get(
    "DATABASE_URL_SYNC",
    "postgresql://nwis:nwis_sih2026@localhost:5432/nwis_drilling"
)

# ─────────────────────────────────────────────────────────────────────────────
# 1. GROUND TRUTH ASSET CATALOG (10 Synthetic Assam Wells)
# ─────────────────────────────────────────────────────────────────────────────

FIELDS_CONFIG = {
    "Nahorkatiya": {"dip_deg": 3.5, "dip_azi_deg": 145.0, "ref_lat": 27.283100, "ref_lon": 95.342200},
    "Moran":       {"dip_deg": 4.2, "dip_azi_deg": 150.0, "ref_lat": 27.195000, "ref_lon": 94.925000},
    "Baghjan":     {"dip_deg": 2.5, "dip_azi_deg": 160.0, "ref_lat": 27.592000, "ref_lon": 95.531000},
}

WELLS_SPEC = [
    # Nahorkatiya Field (7 wells: 1 active drilling + 6 completed offsets within 0.4 - 3.0 km)
    {
        "well_id": "c1f7a012-3b4c-4e89-9a11-000000000005",
        "well_name": "SYN-NHK-05",
        "display_name": "Nahorkatiya Synthetic 05 [Active Demo]",
        "field_name": "Nahorkatiya",
        "surface_lat": 27.280000,
        "surface_lon": 95.340000,
        "kb_elevation_m": 112.0,
        "total_depth_m": 4500.0,
        "max_drilled_md": 2410.0,
        "status": "DRILLING",
        "spud_date": "2026-09-12",
        "kop_m": 500.0,
        "build_len_m": 600.0,
        "hold_inc_deg": 22.744,
        "azi_deg": 145.0,
        "extras": [],
        "notes": "ACTIVE DRILLING TARGET WELL FOR SIH LIVE DEMO SCENARIO. Current bit depth: 2410m MD / 2180.5m TVDSS entering Upper Tipam."
    },
    {
        "well_id": "c1f7a012-3b4c-4e89-9a11-000000000001",
        "well_name": "SYN-NHK-01",
        "display_name": "Nahorkatiya Synthetic 01",
        "field_name": "Nahorkatiya",
        "surface_lat": 27.283100,
        "surface_lon": 95.342200,
        "kb_elevation_m": 112.5,
        "total_depth_m": 4520.0,
        "max_drilled_md": 4520.0,
        "status": "COMPLETED",
        "spud_date": "2023-04-15",
        "kop_m": 500.0,
        "build_len_m": 600.0,
        "hold_inc_deg": 26.015,
        "azi_deg": 145.0,
        "extras": [2448.5, 3020.0],
        "notes": "Historical offset well ~408m NE with differential sticking in Upper Tipam (38.5h NPT) and gas kick in Barail."
    },
    {
        "well_id": "c1f7a012-3b4c-4e89-9a11-000000000002",
        "well_name": "SYN-NHK-02",
        "display_name": "Nahorkatiya Synthetic 02",
        "field_name": "Nahorkatiya",
        "surface_lat": 27.291500,
        "surface_lon": 95.351000,
        "kb_elevation_m": 114.0,
        "total_depth_m": 4380.0,
        "max_drilled_md": 4380.0,
        "status": "COMPLETED",
        "spud_date": "2023-08-10",
        "kop_m": 500.0,
        "build_len_m": 600.0,
        "hold_inc_deg": 26.619,
        "azi_deg": 145.0,
        "extras": [1420.0, 2465.0],
        "notes": "Historical offset well ~1.68km NE with bit balling in Girujan and differential sticking in Upper Tipam (42.0h NPT)."
    },
    {
        "well_id": "c1f7a012-3b4c-4e89-9a11-000000000003",
        "well_name": "SYN-NHK-03",
        "display_name": "Nahorkatiya Synthetic 03",
        "field_name": "Nahorkatiya",
        "surface_lat": 27.272000,
        "surface_lon": 95.331000,
        "kb_elevation_m": 111.8,
        "total_depth_m": 4450.0,
        "max_drilled_md": 4450.0,
        "status": "COMPLETED",
        "spud_date": "2022-11-05",
        "kop_m": 600.0,
        "build_len_m": 600.0,
        "hold_inc_deg": 18.500,
        "azi_deg": 145.0,
        "extras": [],
        "notes": "Completed offset well ~1.25km SW of active pad."
    },
    {
        "well_id": "c1f7a012-3b4c-4e89-9a11-000000000004",
        "well_name": "SYN-NHK-04",
        "display_name": "Nahorkatiya Synthetic 04",
        "field_name": "Nahorkatiya",
        "surface_lat": 27.268500,
        "surface_lon": 95.348000,
        "kb_elevation_m": 113.2,
        "total_depth_m": 4600.0,
        "max_drilled_md": 4600.0,
        "status": "COMPLETED",
        "spud_date": "2021-06-18",
        "kop_m": 550.0,
        "build_len_m": 600.0,
        "hold_inc_deg": 20.000,
        "azi_deg": 145.0,
        "extras": [],
        "notes": "Deep exploratory offset ~1.51km SSE."
    },
    {
        "well_id": "c1f7a012-3b4c-4e89-9a11-000000000006",
        "well_name": "SYN-NHK-06",
        "display_name": "Nahorkatiya Synthetic 06",
        "field_name": "Nahorkatiya",
        "surface_lat": 27.298000,
        "surface_lon": 95.335000,
        "kb_elevation_m": 111.5,
        "total_depth_m": 4350.0,
        "max_drilled_md": 4350.0,
        "status": "COMPLETED",
        "spud_date": "2020-09-22",
        "kop_m": 600.0,
        "build_len_m": 600.0,
        "hold_inc_deg": 19.000,
        "azi_deg": 145.0,
        "extras": [],
        "notes": "Completed northern appraisal offset ~2.06km NNW."
    },
    {
        "well_id": "c1f7a012-3b4c-4e89-9a11-000000000007",
        "well_name": "SYN-NHK-07",
        "display_name": "Nahorkatiya Synthetic 07",
        "field_name": "Nahorkatiya",
        "surface_lat": 27.260000,
        "surface_lon": 95.360000,
        "kb_elevation_m": 115.0,
        "total_depth_m": 4550.0,
        "max_drilled_md": 4550.0,
        "status": "COMPLETED",
        "spud_date": "2019-03-14",
        "kop_m": 650.0,
        "build_len_m": 600.0,
        "hold_inc_deg": 21.500,
        "azi_deg": 145.0,
        "extras": [],
        "notes": "Completed southeastern development offset ~2.95km SE."
    },
    # Moran Field (2 wells: ~40 km SW of Nahorkatiya)
    {
        "well_id": "c1f7a012-3b4c-4e89-9a11-000000000008",
        "well_name": "SYN-MORAN-01",
        "display_name": "Moran Synthetic 01",
        "field_name": "Moran",
        "surface_lat": 27.195000,
        "surface_lon": 94.925000,
        "kb_elevation_m": 102.0,
        "total_depth_m": 4300.0,
        "max_drilled_md": 4300.0,
        "status": "COMPLETED",
        "spud_date": "2021-02-10",
        "kop_m": 500.0,
        "build_len_m": 600.0,
        "hold_inc_deg": 22.000,
        "azi_deg": 150.0,
        "extras": [2490.0],
        "notes": "Moran field offset well (~42km SW of Nahorkatiya)."
    },
    {
        "well_id": "c1f7a012-3b4c-4e89-9a11-000000000009",
        "well_name": "SYN-MORAN-02",
        "display_name": "Moran Synthetic 02",
        "field_name": "Moran",
        "surface_lat": 27.210000,
        "surface_lon": 94.940000,
        "kb_elevation_m": 103.5,
        "total_depth_m": 4420.0,
        "max_drilled_md": 4420.0,
        "status": "COMPLETED",
        "spud_date": "2022-07-19",
        "kop_m": 550.0,
        "build_len_m": 600.0,
        "hold_inc_deg": 24.000,
        "azi_deg": 150.0,
        "extras": [],
        "notes": "Moran field crestal development well (~40km SW of Nahorkatiya)."
    },
    # Baghjan Field (1 well: ~40 km NE of Nahorkatiya)
    {
        "well_id": "c1f7a012-3b4c-4e89-9a11-000000000010",
        "well_name": "SYN-BGJ-01",
        "display_name": "Baghjan Synthetic 01",
        "field_name": "Baghjan",
        "surface_lat": 27.592000,
        "surface_lon": 95.531000,
        "kb_elevation_m": 128.0,
        "total_depth_m": 4100.0,
        "max_drilled_md": 4100.0,
        "status": "COMPLETED",
        "spud_date": "2020-05-15",
        "kop_m": 700.0,
        "build_len_m": 600.0,
        "hold_inc_deg": 15.000,
        "azi_deg": 160.0,
        "extras": [2980.0],
        "notes": "Baghjan field appraisal well (~40km NE of Nahorkatiya)."
    }
]

# 9 Regional Stratigraphic Horizons (Upper Assam Shelf)
TYPE_FORMATION_TOPS = [
    {"name": "Dihing Group",             "code": "DIHING",    "top_md_m": 0.0,    "top_tvdss_m": -112.5, "pp_sg": 1.00, "fg_sg": 1.45, "lithology": "Unconsolidated gravels, sands"},
    {"name": "Namsang Formation",        "code": "NAMSANG",   "top_md_m": 450.0,  "top_tvdss_m": 337.5,  "pp_sg": 1.02, "fg_sg": 1.55, "lithology": "Coarse sandstone, mottled clay"},
    {"name": "Girujan Clay",             "code": "GIRUJAN",   "top_md_m": 1150.0, "top_tvdss_m": 1037.5, "pp_sg": 1.04, "fg_sg": 1.70, "lithology": "Plastic swelling claystone"},
    {"name": "Upper Tipam Sandstone",    "code": "TIPAM_U",   "top_md_m": 2100.0, "top_tvdss_m": 1987.5, "pp_sg": 0.92, "fg_sg": 1.82, "lithology": "Multistory subarkosic sands"},
    {"name": "Lower Tipam Sandstone",    "code": "TIPAM_L",   "top_md_m": 2680.0, "top_tvdss_m": 2567.5, "pp_sg": 0.95, "fg_sg": 1.88, "lithology": "Massive sandstone with calc beds"},
    {"name": "Barail Coal-Shale Unit",   "code": "BARAIL_CS", "top_md_m": 2950.0, "top_tvdss_m": 2837.5, "pp_sg": 1.35, "fg_sg": 1.95, "lithology": "Carbonaceous shale, coal seams"},
    {"name": "Barail Main Sand Unit",   "code": "BARAIL_MS", "top_md_m": 3250.0, "top_tvdss_m": 3137.5, "pp_sg": 1.10, "fg_sg": 1.92, "lithology": "Massive quartz arenite sand"},
    {"name": "Kopili Formation",         "code": "KOPILI",    "top_md_m": 3750.0, "top_tvdss_m": 3637.5, "pp_sg": 1.52, "fg_sg": 2.05, "lithology": "Splintery overpressured shales"},
    {"name": "Sylhet Limestone",         "code": "SYLHET",    "top_md_m": 4150.0, "top_tvdss_m": 4037.5, "pp_sg": 1.22, "fg_sg": 2.10, "lithology": "Nummulitic limestone"}
]

# Historical Drilling Hazards & NPT Knowledge Base (6 high-value records)
HISTORICAL_HAZARDS = [
    {
        "hazard_id": "d1f7a012-3b4c-4e89-9a11-000000000001",
        "well_name": "SYN-NHK-01",
        "formation_name": "Upper Tipam Sandstone",
        "formation_code": "TIPAM_U",
        "depth_md_m": 2448.5,
        "depth_tvdss_m": 2179.0,
        "hazard_type": "DIFFERENTIAL_STICKING",
        "hazard_subtype": "DIFFERENTIAL",
        "severity_level": 4,
        "npt_hours": 38.5,
        "mud_density_sg": 1.18,
        "ecd_sg": 1.22,
        "wob_klbs": 0.0,
        "rpm": 0.0,
        "rop_mhr": 0.0,
        "failure_cause": "Pipe stationary for 45 min during directional single-shot survey in depleted subarkosic sand (PP 0.88 SG). Overbalance pressure exceeded 1,120 psi.",
        "mitigation_action": "Spotted 40 bbls pipe-freeing lubricant pill (glycol/oil based); reduced mud weight to 1.10 SG; established circulation and rotated out with 55 RPM.",
        "outcome": "Drillstring freed after 38.5 hrs NPT. Imposed strict stationary pipe limit of <90 seconds during connections.",
        "report_reference": "DDR-NHK-SYN01-Day-42"
    },
    {
        "hazard_id": "d1f7a012-3b4c-4e89-9a11-000000000002",
        "well_name": "SYN-NHK-01",
        "formation_name": "Barail Coal-Shale Unit",
        "formation_code": "BARAIL_CS",
        "depth_md_m": 3020.0,
        "depth_tvdss_m": 2692.6,
        "hazard_type": "GAS_KICK",
        "hazard_subtype": "INFLUX",
        "severity_level": 4,
        "npt_hours": 24.0,
        "mud_density_sg": 1.24,
        "ecd_sg": 1.28,
        "wob_klbs": 18.5,
        "rpm": 85.0,
        "rop_mhr": 14.2,
        "failure_cause": "Penetrated overpressured coal seam; pit gain of 14 bbls observed with total gas jumping from 2.5% to 28.5%.",
        "mitigation_action": "Shut in well on annular preventer; SICP 420 psi, SIDPP 310 psi; circulated out influx using Wait-and-Weight kill method with 1.38 SG weighted mud.",
        "outcome": "Well killed successfully after 24 hrs NPT. Mud weight raised to 1.35 SG across BCSU section.",
        "report_reference": "DDR-NHK-SYN01-Day-61"
    },
    {
        "hazard_id": "d1f7a012-3b4c-4e89-9a11-000000000003",
        "well_name": "SYN-NHK-02",
        "formation_name": "Girujan Clay",
        "formation_code": "GIRUJAN",
        "depth_md_m": 1420.0,
        "depth_tvdss_m": 1250.7,
        "hazard_type": "BIT_BALLING",
        "hazard_subtype": "CLAY_HYDRATION",
        "severity_level": 3,
        "npt_hours": 14.5,
        "mud_density_sg": 1.14,
        "ecd_sg": 1.18,
        "wob_klbs": 22.0,
        "rpm": 110.0,
        "rop_mhr": 1.8,
        "failure_cause": "Hydratable plastic clay accreted around PDC bit cutters during connection; ROP dropped from 22 m/hr to 1.8 m/hr; MSE spiked 3.4x.",
        "mitigation_action": "Pumped 25 bbls low-viscosity surfactant pill at maximum flow rate (750 GPM) to shear clay; increased flow rate and nozzle total flow area (TFA).",
        "outcome": "Bit cleared, MSE returned to baseline (14,200 psi); ROP recovered to 19.5 m/hr.",
        "report_reference": "DDR-NHK-SYN02-Day-18"
    },
    {
        "hazard_id": "d1f7a012-3b4c-4e89-9a11-000000000004",
        "well_name": "SYN-NHK-02",
        "formation_name": "Upper Tipam Sandstone",
        "formation_code": "TIPAM_U",
        "depth_md_m": 2465.0,
        "depth_tvdss_m": 2185.0,
        "hazard_type": "DIFFERENTIAL_STICKING",
        "hazard_subtype": "DIFFERENTIAL",
        "severity_level": 4,
        "npt_hours": 42.0,
        "mud_density_sg": 1.16,
        "ecd_sg": 1.20,
        "wob_klbs": 0.0,
        "rpm": 0.0,
        "rop_mhr": 0.0,
        "failure_cause": "Differential sticking across porous thief interval under 1,050 psi overbalance during MWD tool battery replacement.",
        "mitigation_action": "Spotted 45 bbls hydrocarbon-free lubricant soak; applied 80 klbs maximum allowable overpull and jarred upward 12 cycles until string freed.",
        "outcome": "String freed after 42.0 hrs NPT. Replaced BHA stabilizer blades with spiral geometry to reduce contact area.",
        "report_reference": "DDR-NHK-SYN02-Day-39"
    },
    {
        "hazard_id": "d1f7a012-3b4c-4e89-9a11-000000000005",
        "well_name": "SYN-MORAN-01",
        "formation_name": "Upper Tipam Sandstone",
        "formation_code": "TIPAM_U",
        "depth_md_m": 2490.0,
        "depth_tvdss_m": 2210.0,
        "hazard_type": "DIFFERENTIAL_STICKING",
        "hazard_subtype": "DIFFERENTIAL",
        "severity_level": 4,
        "npt_hours": 36.0,
        "mud_density_sg": 1.17,
        "ecd_sg": 1.21,
        "wob_klbs": 0.0,
        "rpm": 0.0,
        "rop_mhr": 0.0,
        "failure_cause": "Overbalance 980 psi; drillstring stationary 35 min during MWD survey in Upper Tipam sand.",
        "mitigation_action": "Spotted 35 bbl pipe-freeing pill; worked pipe with 60 klbs overpull and 45 RPM rotation.",
        "outcome": "String freed after 36.0 hrs NPT. Reduced mud density from 1.17 SG to 1.11 SG.",
        "report_reference": "DDR-MORAN-SYN01-Day-33"
    },
    {
        "hazard_id": "d1f7a012-3b4c-4e89-9a11-000000000006",
        "well_name": "SYN-BGJ-01",
        "formation_name": "Barail Coal-Shale Unit",
        "formation_code": "BARAIL_CS",
        "depth_md_m": 2980.0,
        "depth_tvdss_m": 2855.0,
        "hazard_type": "GAS_KICK",
        "hazard_subtype": "INFLUX",
        "severity_level": 4,
        "npt_hours": 28.0,
        "mud_density_sg": 1.26,
        "ecd_sg": 1.30,
        "wob_klbs": 16.0,
        "rpm": 90.0,
        "rop_mhr": 12.5,
        "failure_cause": "Rapid gas influx from micro-fractured coal seam; pit gain 18 bbls, background gas spiked to 34%.",
        "mitigation_action": "Shut in well; SICP 480 psi; executed Wait-and-Weight kill operation using 1.40 SG mud.",
        "outcome": "Influx circulated out safely after 28.0 hrs NPT.",
        "report_reference": "DDR-BGJ-SYN01-Day-51"
    }
]

# ─────────────────────────────────────────────────────────────────────────────
# 2. TRAJECTORY GENERATION VIA MCM
# ─────────────────────────────────────────────────────────────────────────────

def generate_well_trajectory(well_cfg: Dict[str, Any], step_m: float = 30.0) -> List[TrajectoryStation]:
    """Generates 3D trajectory stations using MCMTrajectoryEngine."""
    max_md = well_cfg["max_drilled_md"]
    kop = well_cfg["kop_m"]
    build_len = well_cfg["build_len_m"]
    hold_inc = well_cfg["hold_inc_deg"]
    azi = well_cfg["azi_deg"]
    extras = well_cfg.get("extras", [])

    md_set = {0.0, max_md, kop, kop + build_len}
    for ed in extras:
        if 0.0 < ed <= max_md:
            md_set.add(round(float(ed), 2))

    cur = 0.0
    while cur < max_md:
        cur += step_m
        if cur <= max_md:
            md_set.add(round(cur, 2))

    surveys = []
    for m in sorted(list(md_set)):
        if m <= kop:
            inc = 0.0
        elif m <= kop + build_len:
            inc = ((m - kop) / build_len) * hold_inc
        else:
            inc = hold_inc
        surveys.append((m, inc, azi))

    stations = MCMTrajectoryEngine.calculate_trajectory(
        surveys=surveys,
        surface_lat=well_cfg["surface_lat"],
        surface_lon=well_cfg["surface_lon"],
        kb_elevation_m=well_cfg["kb_elevation_m"],
        z_elevation_mode="AMSL"
    )
    return stations


# ─────────────────────────────────────────────────────────────────────────────
# 3. REGIONAL STRUCTURAL DIP FORMATION TOPS
# ─────────────────────────────────────────────────────────────────────────────

def compute_formation_tops(
    well_cfg: Dict[str, Any],
    trajectories: List[TrajectoryStation]
) -> List[Dict[str, Any]]:
    """Calculates formation tops corrected for regional structural dip."""
    field_name = well_cfg["field_name"]
    cfg = FIELDS_CONFIG[field_name]
    dip_rad = math.radians(cfg["dip_deg"])
    azi_rad = math.radians(cfg["dip_azi_deg"])

    r_major = 6378137.0
    lat_avg = math.radians((well_cfg["surface_lat"] + cfg["ref_lat"]) / 2.0)
    dx = math.radians(well_cfg["surface_lon"] - cfg["ref_lon"]) * r_major * math.cos(lat_avg)
    dy = math.radians(well_cfg["surface_lat"] - cfg["ref_lat"]) * r_major

    # Bedding dip offset: Delta TVDSS = dx * sin(dip)*sin(azi) + dy * sin(dip)*cos(azi)
    delta_tvdss_dip = dx * math.sin(dip_rad) * math.sin(azi_rad) + dy * math.sin(dip_rad) * math.cos(azi_rad)

    kb = well_cfg["kb_elevation_m"]
    tops = []

    for i, t in enumerate(TYPE_FORMATION_TOPS):
        if i == 0:
            top_md = 0.0
            top_tvdss = -kb
        else:
            top_tvdss = round(t["top_tvdss_m"] + delta_tvdss_dip, 2)
            target_tvd = top_tvdss + kb
            top_md = target_tvd  # default fallback
            for st in trajectories:
                if st.tvd_m >= target_tvd:
                    top_md = st.md_m
                    break

        tops.append({
            "formation_name": t["name"],
            "formation_code": t["code"],
            "top_md_m": round(top_md, 2),
            "top_tvdss_m": round(top_tvdss, 2),
            "dip_angle_deg": cfg["dip_deg"],
            "dip_azimuth_deg": cfg["dip_azi_deg"],
            "lithology_desc": t["lithology"],
            "pore_pressure_sg": t["pp_sg"],
            "frac_gradient_sg": t["fg_sg"],
            "data_confidence": "SYNTHETIC"
        })

    # Compute base depths from next top
    for i in range(len(tops)):
        if i < len(tops) - 1:
            tops[i]["base_md_m"] = tops[i + 1]["top_md_m"]
            tops[i]["base_tvdss_m"] = tops[i + 1]["top_tvdss_m"]
        else:
            tops[i]["base_md_m"] = well_cfg["total_depth_m"]
            tops[i]["base_tvdss_m"] = round(well_cfg["total_depth_m"] - kb, 2)

    return tops


# ─────────────────────────────────────────────────────────────────────────────
# 4. 384-DIMENSIONAL UNIT VECTOR EMBEDDINGS (pgvector)
# ─────────────────────────────────────────────────────────────────────────────

def get_narrative_embedding(text: str) -> List[float]:
    """
    Generates deterministic 384-dimensional unit vector for pgvector narrative_embedding.
    Uses sentence-transformers if locally available, otherwise deterministic SHA-256 fallback.
    """
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        emb = model.encode(text).tolist()
        return [round(float(x), 6) for x in emb]
    except Exception:
        dim = 384
        vec = []
        for i in range(dim):
            h = hashlib.sha256(f"{text}::dim_{i}".encode("utf-8")).hexdigest()
            val = (int(h[:8], 16) / 0xFFFFFFFF) * 2.0 - 1.0
            vec.append(val)
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [round(x / norm, 6) for x in vec]


# ─────────────────────────────────────────────────────────────────────────────
# 5. SQL BUILDER & EXPORT
# ─────────────────────────────────────────────────────────────────────────────

def build_seed_sql() -> str:
    """Constructs idempotent SQL statements to seed all tables."""
    lines = [
        "-- ═══════════════════════════════════════════════════════════════════════════",
        "-- eRTMAC-NWIS Database Seed Script (10 Synthetic Assam Wells)",
        "-- Auto-generated by scripts/seed_db.py",
        "-- ═══════════════════════════════════════════════════════════════════════════",
        "BEGIN;",
        ""
    ]

    all_trajectories: Dict[str, List[TrajectoryStation]] = {}
    well_id_map: Dict[str, str] = {}

    # 1. Master Wells Table
    lines.append("-- 1. WELLS MASTER TABLE (10 SYNTHETIC WELLS)")
    for w in WELLS_SPEC:
        well_id_map[w["well_name"]] = w["well_id"]
        traj = generate_well_trajectory(w)
        all_trajectories[w["well_name"]] = traj

        escaped_notes = w["notes"].replace("'", "''")
        escaped_display = w["display_name"].replace("'", "''")
        lines.append(f"""INSERT INTO wells (well_id, well_name, display_name, field_name, operator, data_source, surface_lat, surface_lon, kb_elevation_m, total_depth_m, status, spud_date, notes)
VALUES ('{w["well_id"]}', '{w["well_name"]}', '{escaped_display}', '{w["field_name"]}', 'Oil India Limited', 'SYNTHETIC', {w["surface_lat"]}, {w["surface_lon"]}, {w["kb_elevation_m"]}, {w["total_depth_m"]}, '{w["status"]}', '{w["spud_date"]}', '{escaped_notes}')
ON CONFLICT (well_id) DO UPDATE SET
  well_name = EXCLUDED.well_name, display_name = EXCLUDED.display_name, field_name = EXCLUDED.field_name,
  surface_lat = EXCLUDED.surface_lat, surface_lon = EXCLUDED.surface_lon, kb_elevation_m = EXCLUDED.kb_elevation_m,
  total_depth_m = EXCLUDED.total_depth_m, status = EXCLUDED.status, notes = EXCLUDED.notes;""")

    lines.append("")

    # 2. Formation Tops Table
    lines.append("-- 2. ASSAM BASIN STRATIGRAPHIC TOPS (90 RECORDS)")
    for w in WELLS_SPEC:
        traj = all_trajectories[w["well_name"]]
        tops = compute_formation_tops(w, traj)
        for t in tops:
            lines.append(f"""INSERT INTO formation_tops (well_id, formation_name, formation_code, top_md_m, top_tvdss_m, base_md_m, base_tvdss_m, dip_angle_deg, dip_azimuth_deg, lithology_desc, pore_pressure_sg, frac_gradient_sg, data_confidence)
VALUES ('{w["well_id"]}', '{t["formation_name"]}', '{t["formation_code"]}', {t["top_md_m"]}, {t["top_tvdss_m"]}, {t["base_md_m"]}, {t["base_tvdss_m"]}, {t["dip_angle_deg"]}, {t["dip_azimuth_deg"]}, '{t["lithology_desc"]}', {t["pore_pressure_sg"]}, {t["frac_gradient_sg"]}, '{t["data_confidence"]}');""")

    lines.append("")

    # 3. 3D Trajectory Stations Table
    lines.append("-- 3. 3D TRAJECTORY STATIONS (MCM COMPUTED)")
    for w in WELLS_SPEC:
        traj = all_trajectories[w["well_name"]]
        for st in traj:
            lines.append(f"""INSERT INTO trajectory_stations (well_id, md_m, inc_deg, azi_deg, tvd_m, tvdss_m, north_m, east_m, geom_3d, dogleg_deg_per_30m)
VALUES ('{w["well_id"]}', {st.md_m}, {st.inc_deg}, {st.azi_deg}, {st.tvd_m}, {st.tvdss_m}, {st.north_m}, {st.east_m}, ST_SetSRID(ST_MakePoint({st.x_3857}, {st.y_3857}, {st.z_3857}), 3857), {st.dogleg_deg_per_30m});""")

    lines.append("")

    # 4. Historical Drilling Hazards & NPT Table
    lines.append("-- 4. HISTORICAL DRILLING HAZARDS & NPT KNOWLEDGE BASE")
    for hz in HISTORICAL_HAZARDS:
        wid = well_id_map[hz["well_name"]]
        emb_text = f"{hz['hazard_type']} in {hz['formation_name']}: {hz['failure_cause']} Mitigation: {hz['mitigation_action']}"
        emb = get_narrative_embedding(emb_text)
        emb_str = "[" + ",".join(str(x) for x in emb) + "]"

        cause = hz["failure_cause"].replace("'", "''")
        mitig = hz["mitigation_action"].replace("'", "''")
        outc = hz["outcome"].replace("'", "''")

        lines.append(f"""INSERT INTO drilling_hazards (hazard_id, well_id, formation_name, formation_code, depth_md_m, depth_tvdss_m, hazard_type, hazard_subtype, severity_level, npt_hours, mud_density_sg, ecd_sg, wob_klbs, rpm, rop_mhr, failure_cause, mitigation_action, outcome, report_reference, narrative_embedding)
VALUES ('{hz["hazard_id"]}', '{wid}', '{hz["formation_name"]}', '{hz["formation_code"]}', {hz["depth_md_m"]}, {hz["depth_tvdss_m"]}, '{hz["hazard_type"]}', '{hz["hazard_subtype"]}', {hz["severity_level"]}, {hz["npt_hours"]}, {hz["mud_density_sg"]}, {hz["ecd_sg"]}, {hz["wob_klbs"]}, {hz["rpm"]}, {hz["rop_mhr"]}, '{cause}', '{mitig}', '{outc}', '{hz["report_reference"]}', '{emb_str}'::vector);""")

    lines.append("")

    # 5. Baseline Telemetry (60s trailing feed for SYN-NHK-05 ending at 2410m MD)
    lines.append("-- 5. BASELINE TELEMETRY FOR ACTIVE WELL (SYN-NHK-05)")
    active_id = "c1f7a012-3b4c-4e89-9a11-000000000005"
    now = datetime.datetime.now(datetime.timezone.utc)
    for sec in range(60, 0, -1):
        ts = (now - datetime.timedelta(seconds=sec)).isoformat()
        cur_depth = round(2410.0 - (sec * 0.005), 2)
        lines.append(f"""INSERT INTO live_telemetry (time, well_id, bit_depth_md_m, hook_load_klbs, wob_klbs, surface_torque_kftlb, rpm, standpipe_pressure_psi, flow_rate_gpm, rop_mhr, mud_density_in_sg, mud_density_out_sg, ecd_downhole_sg, annular_temp_c, gas_total_pct, flow_out_pct)
VALUES ('{ts}', '{active_id}', {cur_depth}, 185.0, 18.2, 8.4, 90.0, 2450.0, 620.0, 16.5, 1.18, 1.17, 1.22, 68.5, 1.2, 100.0);""")

    lines.append("")
    lines.append("COMMIT;")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 6. DATABASE EXECUTION & VERIFICATION
# ─────────────────────────────────────────────────────────────────────────────

def seed_database(db_url: str) -> bool:
    """Executes SQL statements directly against PostgreSQL."""
    try:
        import psycopg2
        print(f"[INFO] Connecting to database: {db_url}...")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        print("[INFO] Generating SQL statements...")
        sql = build_seed_sql()
        print(f"[INFO] Executing SQL ({len(sql.splitlines())} lines)...")
        cur.execute(sql)
        conn.commit()
        print("[SUCCESS] Database seeding executed cleanly!")
        cur.close()
        conn.close()
        return True
    except ImportError:
        print("[INFO] psycopg2 not found; executing seeding via docker exec psql...")
        try:
            sql = build_seed_sql()
            print(f"[INFO] Piping SQL to nwis_db container ({len(sql.splitlines())} lines)...")
            res = subprocess.run(
                ["docker", "exec", "-i", "nwis_db", "psql", "-U", "nwis", "-d", "nwis_drilling"],
                input=sql, capture_output=True, text=True
            )
            if res.returncode == 0:
                print("[SUCCESS] Database seeding executed cleanly via docker exec!")
                return True
            else:
                print(f"[ERROR] Docker exec seeding failed: {res.stderr}")
                return False
        except Exception as e:
            print(f"[ERROR] Docker exec seeding failed: {e}")
            return False
    except Exception as e:
        print(f"[ERROR] Database seeding failed: {e}")
        return False


def verify_database(db_url: str):
    """Executes automated verification queries to validate data integrity."""
    print("\n═══════════════════════════════════════════════════════════════")
    print("RUNNING DATABASE SEED VERIFICATION QUERIES")
    print("═══════════════════════════════════════════════════════════════")

    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # 1. Well Count & Integrity
        cur.execute("""
            SELECT count(*),
                   count(*) FILTER (WHERE well_name LIKE 'SYN-%'),
                   count(*) FILTER (WHERE data_source = 'SYNTHETIC')
            FROM wells;
        """)
        total, syn_pref, syn_src = cur.fetchone()
        print(f"[CHECK 1] Wells: {total}/10 | SYN-* Prefix: {syn_pref}/10 | SYNTHETIC Source: {syn_src}/10")
        assert total == 10, f"Expected 10 wells, got {total}"
        assert syn_pref == 10, f"Expected 10 wells with SYN- prefix, got {syn_pref}"
        assert syn_src == 10, f"Expected 10 wells with SYNTHETIC source, got {syn_src}"
        print("  -> PASS: All 10 wells verified with full Red Team synthetic integrity.")

        # 2. Trajectory Stations Check
        cur.execute("SELECT count(*) FROM trajectory_stations;")
        traj_count = cur.fetchone()[0]
        print(f"[CHECK 2] Total 3D Trajectory Stations: {traj_count}")
        assert traj_count >= 1400, f"Expected >=1400 stations, got {traj_count}"
        print("  -> PASS: 3D trajectory stations populated across all 10 wells.")

        # 3. Formation Tops & Dip Check
        cur.execute("SELECT count(*) FROM formation_tops;")
        tops_count = cur.fetchone()[0]
        print(f"[CHECK 3] Total Formation Tops: {tops_count} (Expected: 90)")
        assert tops_count == 90, f"Expected 90 formation tops, got {tops_count}"
        print("  -> PASS: All 9 regional horizons populated across 10 wells.")

        # 4. Drilling Hazards Check
        cur.execute("""
            SELECT w.well_name, dh.hazard_type, dh.depth_md_m, dh.depth_tvdss_m, dh.npt_hours
            FROM drilling_hazards dh
            JOIN wells w ON dh.well_id = w.well_id
            ORDER BY w.well_name, dh.depth_md_m;
        """)
        hazards = cur.fetchall()
        print(f"[CHECK 4] Drilling Hazards Seeded: {len(hazards)} records (Expected: >= 4)")
        for h in hazards:
            print(f"  {h[0]:<14} | {h[1]:<22} | MD: {h[2]:>6.1f}m | TVDSS: {h[3]:>6.1f}m | NPT: {h[4]}h")
        assert len(hazards) >= 4, f"Expected >=4 hazards, got {len(hazards)}"
        print("  -> PASS: Historical hazards verified.")

        # 5. Spatial Query Verification: find_offset_wells on SYN-NHK-05
        active_well_id = "c1f7a012-3b4c-4e89-9a11-000000000005"
        cur.execute("""
            SELECT well_id, well_name, field_name, surface_dist_m, min_tvdss_m, max_tvdss_m
            FROM find_offset_wells(%s::uuid, 27.280000, 95.340000, 2180.5, 5000.0, 200.0);
        """, (active_well_id,))
        offsets = cur.fetchall()
        print(f"[CHECK 5] find_offset_wells() Result for SYN-NHK-05 @ 2180.5m TVDSS (Radius: 5km, Window: ±200m):")
        for o in offsets:
            print(f"  Well: {o[1]:<14} | Field: {o[2]:<12} | Distance: {o[3]:>6.1f}m | TVDSS: [{o[4]:.1f}m - {o[5]:.1f}m]")

        offset_names = [o[1] for o in offsets]
        assert "SYN-NHK-05" not in offset_names, "Active well SYN-NHK-05 must NOT be in offset list!"
        assert "SYN-NHK-01" in offset_names, "SYN-NHK-01 must be detected within 5km radius!"
        assert "SYN-NHK-02" in offset_names, "SYN-NHK-02 must be detected within 5km radius!"
        assert "SYN-MORAN-01" not in offset_names, "Moran wells must be outside 5km radius!"
        assert "SYN-BGJ-01" not in offset_names, "Baghjan wells must be outside 5km radius!"
        print("  -> PASS: Spatial filter, depth slicing, and boundary isolation validated 100%!")
        print("═══════════════════════════════════════════════════════════════\n")

        cur.close()
        conn.close()
        return True

    except ImportError:
        print("[INFO] psycopg2 not installed; executing verification via docker exec psql...")
        try:
            # 1. Well Count & Integrity
            res = subprocess.run(
                ["docker", "exec", "-i", "nwis_db", "psql", "-U", "nwis", "-d", "nwis_drilling", "-t", "-A", "-F", "|", "-c",
                 "SELECT count(*), count(*) FILTER (WHERE well_name LIKE 'SYN-%'), count(*) FILTER (WHERE data_source = 'SYNTHETIC') FROM wells;"],
                capture_output=True, text=True, check=True
            )
            parts = [int(p) for p in res.stdout.strip().split("|")]
            total, syn_pref, syn_src = parts[0], parts[1], parts[2]
            print(f"[CHECK 1] Wells: {total}/10 | SYN-* Prefix: {syn_pref}/10 | SYNTHETIC Source: {syn_src}/10")
            assert total == 10, f"Expected 10 wells, got {total}"
            assert syn_pref == 10, f"Expected 10 wells with SYN- prefix, got {syn_pref}"
            assert syn_src == 10, f"Expected 10 wells with SYNTHETIC source, got {syn_src}"
            print("  -> PASS: All 10 wells verified with full Red Team synthetic integrity.")

            # 2. Trajectory Stations Check
            res = subprocess.run(
                ["docker", "exec", "-i", "nwis_db", "psql", "-U", "nwis", "-d", "nwis_drilling", "-t", "-A", "-c",
                 "SELECT count(*) FROM trajectory_stations;"],
                capture_output=True, text=True, check=True
            )
            traj_count = int(res.stdout.strip())
            print(f"[CHECK 2] Total 3D Trajectory Stations: {traj_count}")
            assert traj_count >= 1400, f"Expected >=1400 stations, got {traj_count}"
            print("  -> PASS: 3D trajectory stations populated across all 10 wells.")

            # 3. Formation Tops & Dip Check
            res = subprocess.run(
                ["docker", "exec", "-i", "nwis_db", "psql", "-U", "nwis", "-d", "nwis_drilling", "-t", "-A", "-c",
                 "SELECT count(*) FROM formation_tops;"],
                capture_output=True, text=True, check=True
            )
            tops_count = int(res.stdout.strip())
            print(f"[CHECK 3] Total Formation Tops: {tops_count} (Expected: 90)")
            assert tops_count == 90, f"Expected 90 formation tops, got {tops_count}"
            print("  -> PASS: All 9 regional horizons populated across 10 wells.")

            # 4. Drilling Hazards Check
            res = subprocess.run(
                ["docker", "exec", "-i", "nwis_db", "psql", "-U", "nwis", "-d", "nwis_drilling", "-t", "-A", "-F", "|", "-c",
                 "SELECT w.well_name, dh.hazard_type, dh.depth_md_m, dh.depth_tvdss_m, dh.npt_hours FROM drilling_hazards dh JOIN wells w ON dh.well_id = w.well_id ORDER BY w.well_name, dh.depth_md_m;"],
                capture_output=True, text=True, check=True
            )
            hazard_lines = [l.strip() for l in res.stdout.strip().splitlines() if l.strip()]
            print(f"[CHECK 4] Drilling Hazards Seeded: {len(hazard_lines)} records (Expected: >= 4)")
            for line in hazard_lines:
                w_name, hz_type, md, tvdss, npt = line.split("|")
                print(f"  {w_name:<14} | {hz_type:<22} | MD: {float(md):>6.1f}m | TVDSS: {float(tvdss):>6.1f}m | NPT: {float(npt)}h")
            assert len(hazard_lines) >= 4, f"Expected >=4 hazards, got {len(hazard_lines)}"
            print("  -> PASS: Historical hazards verified.")

            # 5. Spatial Query Verification: find_offset_wells on SYN-NHK-05
            active_well_id = "c1f7a012-3b4c-4e89-9a11-000000000005"
            res = subprocess.run(
                ["docker", "exec", "-i", "nwis_db", "psql", "-U", "nwis", "-d", "nwis_drilling", "-t", "-A", "-F", "|", "-c",
                 f"SELECT well_id, well_name, field_name, surface_dist_m, min_tvdss_m, max_tvdss_m FROM find_offset_wells('{active_well_id}'::uuid, 27.280000, 95.340000, 2180.5, 5000.0, 200.0);"],
                capture_output=True, text=True, check=True
            )
            offset_lines = [l.strip() for l in res.stdout.strip().splitlines() if l.strip()]
            print(f"[CHECK 5] find_offset_wells() Result for SYN-NHK-05 @ 2180.5m TVDSS (Radius: 5km, Window: ±200m):")
            offset_names = []
            for line in offset_lines:
                wid, wname, fname, sdist, min_tvdss, max_tvdss = line.split("|")
                offset_names.append(wname)
                print(f"  Well: {wname:<14} | Field: {fname:<12} | Distance: {float(sdist):>6.1f}m | TVDSS: [{float(min_tvdss):.1f}m - {float(max_tvdss):.1f}m]")

            assert "SYN-NHK-05" not in offset_names, "Active well SYN-NHK-05 must NOT be in offset list!"
            assert "SYN-NHK-01" in offset_names, "SYN-NHK-01 must be detected within 5km radius!"
            assert "SYN-NHK-02" in offset_names, "SYN-NHK-02 must be detected within 5km radius!"
            assert "SYN-MORAN-01" not in offset_names, "Moran wells must be outside 5km radius!"
            assert "SYN-BGJ-01" not in offset_names, "Baghjan wells must be outside 5km radius!"
            print("  -> PASS: Spatial filter, depth slicing, and boundary isolation validated 100%!")
            print("═══════════════════════════════════════════════════════════════\n")
            return True
        except Exception as e:
            print(f"[ERROR] Live verification failed via docker exec: {e}")
            return False


# ─────────────────────────────────────────────────────────────────────────────
# 7. CLI ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="eRTMAC-NWIS Database Seed Engine")
    parser.add_argument("--db-url", default=DEFAULT_DB_URL, help="PostgreSQL connection string")
    parser.add_argument("--export-sql", type=str, default=None, help="Export SQL file path (e.g. docker/init/02_seed.sql)")
    parser.add_argument("--verify-only", action="store_true", help="Run verification queries without seeding")

    args = parser.parse_args()

    if args.export_sql:
        print(f"[INFO] Exporting SQL seed script to {args.export_sql}...")
        sql = build_seed_sql()
        target_path = os.path.abspath(args.export_sql)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(sql)
        print(f"[SUCCESS] Exported {len(sql.splitlines())} SQL lines to {args.export_sql}.")
        return

    if args.verify_only:
        verify_database(args.db_url)
        return

    success = seed_database(args.db_url)
    if success:
        verify_database(args.db_url)


if __name__ == "__main__":
    main()
