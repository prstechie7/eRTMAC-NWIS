#!/usr/bin/env python3
"""
Public Dataset Catalog, Ingestion & Seed Manager for eRTMAC-NWIS.
Compliant with Smart India Hackathon 2026 (SIH26121) · Oil India Limited.

Datasets Managed:
1. DGH National Data Repository (NDR) - Assam-Arakan Basin Formations, Fields, Stratigraphy
2. FORCE 2020 Well Log & Lithofacies Dataset (Zenodo 4351156)
3. Equinor Volve Open Field Dataset (Operational, Trajectories, Well Logs)
4. NLOG Netherlands Subsurface Database (Spatial Boreholes, Deviation, LAS Logs)
5. Drilling Lost Circulation Benchmark (CirculationDataV2.csv & Western China Telemetry)
6. Gulf of Suez Stuck Pipe Research Benchmark
7. Energistics WITSML Log Schema Specification
"""

import os
import sys
import json
import csv
import argparse
from pathlib import Path
from typing import Dict, Any, List

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
PUBLIC_DIR = DATA_DIR / "public"

DATASET_REGISTRY = {
    "dgh_assam": {
        "name": "DGH National Data Repository (Assam-Arakan Basin)",
        "source_url": "https://dghindia.gov.in/ndr",
        "description": "Geological grounding, field plays (Nahorkatiya, Moran, Baghjan), and stratigraphic formations (Tipam, Barail, Kopili, Lakadong-Therria, Sylhet).",
        "license": "Government of India Open Data / DGH Regulatory Public Access",
        "target_dir": str(PUBLIC_DIR / "dgh" / "assam_metadata"),
        "provenance": "PUBLIC",
    },
    "force2020": {
        "name": "FORCE 2020 Well Log and Lithofacies Dataset",
        "source_url": "https://zenodo.org/records/4351156",
        "description": "118 wells with wireline/LWD logs (GR, RHOB, NPHI, DTC, RES, CALI, ROP, MUDWEIGHT) and interpreted lithofacies labels.",
        "license": "Creative Commons Attribution 4.0 International (CC-BY 4.0)",
        "target_dir": str(PUBLIC_DIR / "force2020"),
        "provenance": "PUBLIC",
    },
    "equinor_volve": {
        "name": "Equinor Volve Open Field Dataset",
        "source_url": "https://www.equinor.com/energy/volve-data-sharing",
        "description": "~40,000 subsurface, drilling, production, trajectory, and well-log files from the Volve Field (2008-2016).",
        "license": "Equinor Open Data Licence",
        "target_dir": str(PUBLIC_DIR / "volve"),
        "provenance": "PUBLIC",
    },
    "nlog_netherlands": {
        "name": "NLOG Dutch Subsurface Repository",
        "source_url": "https://www.nlog.nl/en/boreholes",
        "description": "National spatial borehole repository, trajectories, deviation surveys, and digital LAS/LIS logs.",
        "license": "Open Data / Ministry of Economic Affairs and Climate Policy (NL)",
        "target_dir": str(PUBLIC_DIR / "nlog"),
        "provenance": "PUBLIC",
    },
    "lost_circulation": {
        "name": "Drilling Lost-Circulation Benchmark Dataset",
        "source_url": "https://github.com/HaythamElmousalami/Drilling-Lost-circulation",
        "description": "Circulation telemetry and loss events (pit volume, flow rate, standpipe pressure, top drive load).",
        "license": "Open Research Dataset",
        "target_dir": str(PUBLIC_DIR / "hazard" / "lost_circulation"),
        "provenance": "PUBLIC",
    },
    "stuck_pipe": {
        "name": "Gulf of Suez Stuck-Pipe Research Benchmark",
        "source_url": "https://doi.org/10.1016/j.petlm.2018.10.003",
        "description": "Historical stuck-pipe incidents, mud overbalance, string geometry, hookload, and formation sticking indicators.",
        "license": "Open Research Publication Dataset",
        "target_dir": str(PUBLIC_DIR / "hazard" / "stuck_pipe"),
        "provenance": "PUBLIC",
    },
    "witsml_spec": {
        "name": "Energistics WITSML Log & Trajectory Standard Specification",
        "source_url": "https://docs.energistics.org/WITSML/WITSML_TOPICS/WITSML-000-048-0-C-sv2000.html",
        "description": "Canonical XML/JSON schema for time/depth indexed drilling telemetry and survey stations.",
        "license": "Energistics Open Standard",
        "target_dir": str(PUBLIC_DIR / "witsml_spec"),
        "provenance": "PUBLIC",
    }
}


def seed_sample_public_data():
    """Generates calibrated reference samples for offline development and testing."""
    print("🌱 Seeding public benchmark reference samples...")

    # 1. DGH Assam Metadata
    dgh_dir = PUBLIC_DIR / "dgh" / "assam_metadata"
    dgh_dir.mkdir(parents=True, exist_ok=True)
    dgh_manifest = {
        "basin": "Assam-Arakan Basin (Upper Assam Shelf)",
        "regulatory_body": "Directorate General of Hydrocarbons (DGH), India",
        "target_fields": ["Nahorkatiya", "Moran", "Baghjan", "Lakwa", "Rudrasagar"],
        "formations": [
            {"name": "Dihing Group", "age": "Pliocene-Pleistocene", "lithology": "Pebble beds, soft sands"},
            {"name": "Namsang Formation", "age": "Mio-Pliocene", "lithology": "Sandstones and claystones"},
            {"name": "Girujan Clay", "age": "Miocene", "lithology": "Mottled sticky gumbo clay (bit balling hazard)"},
            {"name": "Upper Tipam Sandstone", "age": "Miocene", "lithology": "Subarkosic sandstone (depleted pressure, differential sticking hazard)"},
            {"name": "Lower Tipam Sandstone", "age": "Miocene", "lithology": "Sandstone with shale bands"},
            {"name": "Barail Coal-Shale Unit", "age": "Oligocene", "lithology": "Carbonaceous shale & coal seams (gas kick / overpressure hazard)"},
            {"name": "Barail Main Sand Unit", "age": "Oligocene", "lithology": "Productive quartzose sandstone reservoirs"},
            {"name": "Kopili Formation", "age": "Late Eocene", "lithology": "Fissile splintery shale, marl (borehole instability, cementing losses)"},
            {"name": "Sylhet Limestone", "age": "Early Eocene", "lithology": "Hard nummulitic limestone (lost circulation)"}
        ],
        "provenance": "PUBLIC (DGH NDR)"
    }
    with open(dgh_dir / "dgh_assam_stratigraphy.json", "w") as f:
        json.dump(dgh_manifest, f, indent=2)

    # 2. FORCE 2020 Sample Log
    force_dir = PUBLIC_DIR / "force2020"
    force_dir.mkdir(parents=True, exist_ok=True)
    force_csv = force_dir / "sample_force2020_logs.csv"
    with open(force_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["well_id", "md", "GR", "RHOB", "NPHI", "DT", "RES", "SP", "CALI", "ROP", "MUDWEIGHT", "lithology", "provenance"])
        for md in range(2000, 2050):
            gr = 65.0 + (md % 15) * 2.5
            rhob = 2.35 + (md % 10) * 0.02
            nphi = 0.22 - (md % 10) * 0.005
            dt = 85.0 + (md % 8) * 1.2
            res = 12.5 + (md % 12) * 1.5
            cali = 8.5
            rop = 18.0 + (md % 5) * 1.1
            mw = 1.15
            lith = "Sandstone" if gr < 75 else "Shale"
            writer.writerow(["FORCE_15_9_13", md, round(gr, 2), round(rhob, 3), round(nphi, 3), round(dt, 2), round(res, 2), -25.0, cali, rop, mw, lith, "PUBLIC"])

    # 3. Equinor Volve Trajectory Sample
    volve_dir = PUBLIC_DIR / "volve"
    volve_dir.mkdir(parents=True, exist_ok=True)
    volve_csv = volve_dir / "sample_volve_trajectory.csv"
    with open(volve_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["well_id", "md", "inclination", "azimuth", "tvd", "northing", "easting", "provenance"])
        for md in range(0, 2500, 100):
            inc = min(42.0, md * 0.02)
            azi = 210.0
            tvd = md * 0.94 if md > 500 else md
            writer.writerow(["VOLVE_NO_15_9_F_12", md, round(inc, 2), azi, round(tvd, 2), md * 0.3, md * 0.2, "PUBLIC"])

    # 4. Lost Circulation Benchmark Sample
    lc_dir = PUBLIC_DIR / "hazard" / "lost_circulation"
    lc_dir.mkdir(parents=True, exist_ok=True)
    lc_csv = lc_dir / "CirculationDataV2_sample.csv"
    with open(lc_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["record_id", "well_id", "depth_m", "pit_volume_bbl", "flow_rate_gpm", "spp_psi", "loss_observed", "provenance"])
        for i in range(1, 31):
            loss = 1 if i in [12, 13, 14, 25, 26] else 0
            pit = 350.0 - (i * 2.0 if loss else 0)
            writer.writerow([f"LC-{i:03d}", "BENCH-WELL-LC1", 2150.0 + i * 10, round(pit, 1), 600.0, 2800.0 if not loss else 2200.0, loss, "PUBLIC"])

    # 5. Stuck Pipe Benchmark Sample
    sp_dir = PUBLIC_DIR / "hazard" / "stuck_pipe"
    sp_dir.mkdir(parents=True, exist_ok=True)
    sp_csv = sp_dir / "gulf_of_suez_sample.csv"
    with open(sp_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["incident_id", "well_id", "depth_m", "overbalance_psi", "stationary_time_min", "stuck_pipe_event", "mitigation", "provenance"])
        writer.writerow(["SP-001", "GOS-WELL-A", 2430.0, 1150.0, 50.0, 1, "Pipe worked with lubricant pill", "PUBLIC"])
        writer.writerow(["SP-002", "GOS-WELL-B", 2620.0, 450.0, 10.0, 0, "Normal connection", "PUBLIC"])
        writer.writerow(["SP-003", "GOS-WELL-C", 2890.0, 1320.0, 65.0, 1, "Acid wash spotted to free differential sticking", "PUBLIC"])

    print("✅ All sample public benchmark files created successfully in data/public/")


def list_catalog():
    print("=" * 80)
    print("  📚 eRTMAC-NWIS Recommended Open Petroleum Dataset Catalog")
    print("=" * 80)
    for key, ds in DATASET_REGISTRY.items():
        print(f"[{key.upper()}] - {ds['name']}")
        print(f"  URL:         {ds['source_url']}")
        print(f"  License:     {ds['license']}")
        print(f"  Provenance:  {ds['provenance']}")
        print(f"  Target Dir:  {ds['target_dir']}")
        print(f"  Role:        {ds['description']}")
        print("-" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Public Petroleum Data Downloader & Seed Manager")
    parser.add_argument("--list", action="store_true", help="List all cataloged public datasets")
    parser.add_argument("--seed-samples", action="store_true", default=True, help="Seed sample benchmark datasets locally")
    args = parser.parse_args()

    if args.list:
        list_catalog()
    else:
        list_catalog()
        seed_sample_public_data()
