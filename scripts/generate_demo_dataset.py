#!/usr/bin/env python3
"""
Deterministic Demo Dataset Generator for eRTMAC-NWIS.
Compliant with SIH26121 (Oil India Limited).
Generates 15 synthetic wells with formations, reservoirs, trajectories,
historical events (stuck pipe, mud loss, overpressure, torque spike, cementing),
and telemetry streams. All output files are explicitly marked SYNTHETIC.
"""

import os
import csv
import json
import random
from pathlib import Path

# Fixed random seed for deterministic generation
random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent / "data" / "demo"
TELEMETRY_DIR = BASE_DIR / "telemetry"

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(TELEMETRY_DIR, exist_ok=True)

WELL_NAMES = [
    ("c1f7a012-3b4c-4e89-9a11-000000000005", "SYN-NHK-05", "Nahorkatiya", 27.2885, 95.3345, 122.5, 3150.0, "DRILLING"),
    ("c1f7a012-3b4c-4e89-9a11-000000000001", "SYN-NHK-01", "Nahorkatiya", 27.2798, 95.3211, 121.2, 4520.0, "COMPLETED"),
    ("c1f7a012-3b4c-4e89-9a11-000000000002", "SYN-NHK-02", "Nahorkatiya", 27.2954, 95.3488, 124.0, 4380.0, "COMPLETED"),
    ("c1f7a012-3b4c-4e89-9a11-000000000003", "SYN-NHK-03", "Nahorkatiya", 27.2655, 95.3122, 119.8, 3420.0, "COMPLETED"),
    ("c1f7a012-3b4c-4e89-9a11-000000000004", "SYN-NHK-04", "Nahorkatiya", 27.3112, 95.3621, 126.1, 2950.0, "COMPLETED"),
    ("c1f7a012-3b4c-4e89-9a11-000000000006", "SYN-MORAN-01", "Moran", 27.1855, 94.9312, 115.4, 3850.0, "COMPLETED"),
    ("c1f7a012-3b4c-4e89-9a11-000000000007", "SYN-MORAN-02", "Moran", 27.1992, 94.9455, 117.0, 3920.0, "COMPLETED"),
    ("c1f7a012-3b4c-4e89-9a11-000000000008", "SYN-BGJ-01", "Baghjan", 27.5812, 95.3522, 128.5, 4100.0, "COMPLETED"),
    ("c1f7a012-3b4c-4e89-9a11-000000000009", "SYN-BGJ-02", "Baghjan", 27.5925, 95.3688, 130.2, 4250.0, "COMPLETED"),
    ("c1f7a012-3b4c-4e89-9a11-000000000010", "SYN-BGJ-03", "Baghjan", 27.5701, 95.3395, 127.0, 3980.0, "COMPLETED"),
    ("c1f7a012-3b4c-4e89-9a11-000000000011", "SYN-NHK-06", "Nahorkatiya", 27.2750, 95.3300, 120.0, 3600.0, "COMPLETED"),
    ("c1f7a012-3b4c-4e89-9a11-000000000012", "SYN-NHK-07", "Nahorkatiya", 27.3050, 95.3550, 125.0, 3750.0, "COMPLETED"),
    ("c1f7a012-3b4c-4e89-9a11-000000000013", "SYN-MORAN-03", "Moran", 27.1900, 94.9400, 116.0, 4000.0, "COMPLETED"),
    ("c1f7a012-3b4c-4e89-9a11-000000000014", "SYN-BGJ-04", "Baghjan", 27.5850, 95.3600, 129.0, 4300.0, "COMPLETED"),
    ("c1f7a012-3b4c-4e89-9a11-000000000015", "SYN-BGJ-05", "Baghjan", 27.5750, 95.3450, 128.0, 4150.0, "COMPLETED"),
]

def generate_wells():
    wells_csv = BASE_DIR / "wells.csv"
    with open(wells_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "well_id", "uwi", "well_name", "field", "latitude", "longitude",
            "datum", "total_depth_md", "total_depth_tvd", "well_type", "status",
            "operator", "spud_date", "completion_date", "provenance_type"
        ])
        for w_id, w_name, field, lat, lon, kb, td_md, status in WELL_NAMES:
            writer.writerow([
                w_id, f"IN-OIL-{field.upper()}-{w_name}", w_name, field, lat, lon,
                "KB", td_md, td_md - kb, "EXPLORATION", status,
                "Oil India Limited", "2023-01-10", "2023-06-15", "SYNTHETIC"
            ])
    print(f"Generated {wells_csv}")

def generate_formations():
    form_csv = BASE_DIR / "formations.csv"
    formations_def = [
        ("fmt-01", "Dihing Group", 0.0, 450.0, 0.0, 337.5, 3.5, 145.0, "Pebble Bed / Sandstone"),
        ("fmt-02", "Namsang Formation", 450.0, 1150.0, 337.5, 1037.5, 3.5, 145.0, "Coarse Sandstone / Claystone"),
        ("fmt-03", "Girujan Clay", 1150.0, 2100.0, 1037.5, 1987.5, 3.5, 145.0, "Mottled Clay / Claystone"),
        ("fmt-04", "Upper Tipam Sandstone", 2100.0, 2680.0, 1987.5, 2567.5, 3.5, 145.0, "Depleted Subarkosic Sandstone"),
        ("fmt-05", "Lower Tipam Sandstone", 2680.0, 2950.0, 2567.5, 2837.5, 3.5, 145.0, "Sandstone / Siltstone"),
        ("fmt-06", "Barail Coal-Shale Unit", 2950.0, 3250.0, 2837.5, 3137.5, 3.5, 145.0, "Overpressured Carbonaceous Shale"),
        ("fmt-07", "Barail Main Sand Unit", 3250.0, 3750.0, 3137.5, 3637.5, 3.5, 145.0, "Fine to Medium Sandstone"),
        ("fmt-08", "Kopili Formation", 3750.0, 4150.0, 3637.5, 4037.5, 3.5, 145.0, "Splintery Shale / Marl"),
        ("fmt-09", "Sylhet Limestone", 4150.0, 4520.0, 4037.5, 4407.5, 3.5, 145.0, "Nummulitic Limestone")
    ]
    with open(form_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "formation_id", "formation_name", "top_md", "base_md",
            "top_tvd", "base_tvd", "dip", "dip_direction", "lithology"
        ])
        for row in formations_def:
            writer.writerow(row)
    print(f"Generated {form_csv}")

def generate_reservoirs():
    res_csv = BASE_DIR / "reservoirs.csv"
    reservoirs_def = [
        ("res-01", "fmt-04", "Tipam Main Sand", 2850.0, 75.0, 18.5, 250.0, "OIL", 0.35, 2100.0, 3400.0),
        ("res-02", "fmt-06", "Barail Coal-Shale Gas Horizon", 4250.0, 92.0, 14.0, 45.0, "GAS", 0.05, 3800.0, 4900.0),
        ("res-03", "fmt-07", "Barail 3rd Sand", 3450.0, 88.0, 21.0, 320.0, "OIL", 0.20, 3000.0, 4100.0)
    ]
    with open(res_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "reservoir_id", "formation_id", "reservoir_name", "pressure",
            "temperature", "porosity", "permeability", "fluid_type",
            "depletion_indicator", "pressure_window_min", "pressure_window_max"
        ])
        for row in reservoirs_def:
            writer.writerow(row)
    print(f"Generated {res_csv}")

def generate_events():
    events_jsonl = BASE_DIR / "events.jsonl"
    events_data = [
        {
            "event_id": "evt-001",
            "well_id": "c1f7a012-3b4c-4e89-9a11-000000000001",
            "timestamp": "2023-05-12T14:30:00Z",
            "depth_md": 2448.5,
            "tvdss": 2179.0,
            "formation_id": "fmt-04",
            "reservoir_id": "res-01",
            "event_type": "STUCK_PIPE",
            "severity": 4,
            "duration": 38.5,
            "NPT_hours": 38.5,
            "description": "Differential sticking in depleted Upper Tipam Sandstone during survey.",
            "root_cause": "Pipe stationary for 45 min in depleted sand package (PP 0.88 SG). Overbalance > 1,120 psi.",
            "mitigation": "Spotted 40 bbls lubricant pill; reduced MW to 1.10 SG; rotated out with 55 RPM.",
            "outcome": "Pipe freed successfully.",
            "source_document_id": "DDR-NHK-SYN01-Day-42",
            "source_page": 4,
            "source_excerpt": "Stuck at 2448.5m MD while surveying. Freeing pill spotted.",
            "provenance_type": "SYNTHETIC"
        },
        {
            "event_id": "evt-002",
            "well_id": "c1f7a012-3b4c-4e89-9a11-000000000001",
            "timestamp": "2023-06-02T08:15:00Z",
            "depth_md": 3020.0,
            "tvdss": 2907.5,
            "formation_id": "fmt-06",
            "reservoir_id": "res-02",
            "event_type": "OVERPRESSURE",
            "severity": 4,
            "duration": 24.0,
            "NPT_hours": 24.0,
            "description": "Gas kick in overpressured Barail Coal-Shale unit.",
            "root_cause": "Penetrated overpressured gas-bearing seam.",
            "mitigation": "Shut in well; circulated out gas kick using Wait & Weight method with 1.38 SG mud.",
            "outcome": "Well controlled.",
            "source_document_id": "DDR-NHK-SYN01-Day-61",
            "source_page": 6,
            "source_excerpt": "14 bbl pit gain observed. Total gas jumped to 28.5%.",
            "provenance_type": "SYNTHETIC"
        },
        {
            "event_id": "evt-003",
            "well_id": "c1f7a012-3b4c-4e89-9a11-000000000004",
            "timestamp": "2023-04-18T10:00:00Z",
            "depth_md": 2210.0,
            "tvdss": 2083.9,
            "formation_id": "fmt-04",
            "reservoir_id": "res-01",
            "event_type": "MUD_LOSS",
            "severity": 3,
            "duration": 16.0,
            "NPT_hours": 16.0,
            "description": "Partial mud loss in porous Tipam sand.",
            "root_cause": "High ECD in permeable clean sand interval.",
            "mitigation": "Pumped 25 bbl LCM pill (mica + nutshells); reduced pump rate.",
            "outcome": "Losses cured.",
            "source_document_id": "DDR-NHK-SYN04-Day-22",
            "source_page": 3,
            "source_excerpt": "Loss rate 35 bbl/hr. LCM pill cured losses.",
            "provenance_type": "SYNTHETIC"
        },
        {
            "event_id": "evt-004",
            "well_id": "c1f7a012-3b4c-4e89-9a11-000000000002",
            "timestamp": "2023-09-01T16:45:00Z",
            "depth_md": 1420.0,
            "tvdss": 1306.0,
            "formation_id": "fmt-03",
            "reservoir_id": None,
            "event_type": "TORQUE_SPIKE",
            "severity": 2,
            "duration": 8.0,
            "NPT_hours": 8.0,
            "description": "Severe bit balling and torque spikes in Girujan Clay.",
            "root_cause": "Sticky gumbo clay building on PDC cutters.",
            "mitigation": "Pumped high-viscosity anti-sticking wash; increased RPM to 110.",
            "outcome": "Torque stabilized.",
            "source_document_id": "DDR-NHK-SYN02-Day-15",
            "source_page": 2,
            "source_excerpt": "Torque erratic up to 18.5 kft-lbs.",
            "provenance_type": "SYNTHETIC"
        },
        {
            "event_id": "evt-005",
            "well_id": "c1f7a012-3b4c-4e89-9a11-000000000006",
            "timestamp": "2023-11-10T12:00:00Z",
            "depth_md": 3750.0,
            "tvdss": 3634.6,
            "formation_id": "fmt-08",
            "reservoir_id": None,
            "event_type": "CEMENTING_ISSUE",
            "severity": 3,
            "duration": 18.0,
            "NPT_hours": 18.0,
            "description": "Slurry loss during 9-5/8 in casing cement job.",
            "root_cause": "Loss of circulation in fractured Kopili shale horizon.",
            "mitigation": "Executed squeeze cementing job with thixotropic slurry.",
            "outcome": "CBL confirmed top of cement.",
            "source_document_id": "EOWR-MORAN-01-Cem",
            "source_page": 12,
            "source_excerpt": "Top of cement 120m below target.",
            "provenance_type": "SYNTHETIC"
        }
    ]
    with open(events_jsonl, "w", encoding="utf-8") as f:
        for ev in events_data:
            f.write(json.dumps(ev) + "\n")
    print(f"Generated {events_jsonl}")

def generate_trajectories():
    traj_csv = BASE_DIR / "trajectory.csv"
    with open(traj_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["well_id", "measured_depth", "inclination", "azimuth", "TVD", "northing", "easting", "TVDSS"])
        for w_id, w_name, field, lat, lon, kb, td_md, status in WELL_NAMES:
            for md in range(0, int(td_md) + 1, 100):
                inc = 0.0 if md < 500 else min(35.0, (md - 500) * 0.015)
                azi = 145.0
                tvd = md * 0.98 if md > 500 else md
                tvdss = tvd - kb
                writer.writerow([w_id, md, round(inc, 2), azi, round(tvd, 2), 0.0, 0.0, round(tvdss, 2)])
    print(f"Generated {traj_csv}")

def generate_telemetry():
    for w_id, w_name, field, lat, lon, kb, td_md, status in WELL_NAMES[:5]:
        t_csv = TELEMETRY_DIR / f"telemetry_{w_name}.csv"
        with open(t_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "well_id", "depth_md", "tvdss", "ROP", "WOB", "RPM",
                "torque", "hookload", "standpipe_pressure", "pump_rate",
                "mud_weight_in", "mud_weight_out", "ECD", "pit_volume",
                "flow_in", "flow_out", "provenance_type"
            ])
            cur_time = 1700000000.0
            for depth in range(2400, 2450):
                is_stuck_zone = depth >= 2413
                rop = 12.2 if is_stuck_zone else 18.5
                torque = 15.4 if is_stuck_zone else 12.8
                writer.writerow([
                    cur_time, w_id, float(depth), float(depth - kb), rop, 18.2, 95.0,
                    torque, 185.0, 2950.0, 640.0, 1.16, 1.16, 1.21, 320.0,
                    640.0, 639.8, "SYNTHETIC"
                ])
                cur_time += 1.0
        print(f"Generated {t_csv}")

if __name__ == "__main__":
    generate_wells()
    generate_formations()
    generate_reservoirs()
    generate_events()
    generate_trajectories()
    generate_telemetry()
    print("DEMO DATASET GENERATION COMPLETE [SYNTHETIC LOGGED].")
