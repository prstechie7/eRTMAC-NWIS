#!/usr/bin/env python3
"""
Calibrated Upper Assam Synthetic Dataset Generator for eRTMAC-NWIS.
Compliant with Smart India Hackathon 2026 (SIH26121) · Oil India Limited.

Geologically Grounded Targets:
- Basin: Assam-Arakan Basin (Upper Assam Shelf)
- Fields: Nahorkatiya (NHK), Moran, Baghjan (BGJ)
- Stratigraphic Column: Dihing -> Namsang -> Girujan -> Tipam -> Barail -> Kopili -> Sylhet
- Outputs: wells.csv, trajectory.csv, formations.csv, reservoirs.csv, logs.csv,
           drilling_telemetry.csv, events.jsonl
All generated records have provenance_type = 'SYNTHETIC'.
"""

import os
import csv
import json
import random
from pathlib import Path

# Fixed random seed for deterministic reproduction
random.seed(42)

ROOT_DIR = Path(__file__).resolve().parent.parent
TARGET_DIR = ROOT_DIR / "data" / "synthetic" / "assam"
DEMO_DIR = ROOT_DIR / "data" / "demo"
TELEMETRY_DIR = TARGET_DIR / "telemetry"

TARGET_DIR.mkdir(parents=True, exist_ok=True)
TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)

WELLS = [
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

FORMATIONS = [
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


def generate_wells_csv(out_path: Path):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "well_id", "uwi", "well_name", "field", "latitude", "longitude",
            "datum", "total_depth_md", "total_depth_tvd", "well_type", "status",
            "operator", "spud_date", "completion_date", "provenance_type"
        ])
        for w_id, w_name, field, lat, lon, kb, td_md, status in WELLS:
            writer.writerow([
                w_id, f"IN-OIL-{field.upper()}-{w_name}", w_name, field, lat, lon,
                "KB", td_md, round(td_md - kb, 2), "EXPLORATION", status,
                "Oil India Limited", "2023-01-10", "2023-06-15", "SYNTHETIC"
            ])


def generate_formations_csv(out_path: Path):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "formation_id", "formation_name", "top_md", "base_md",
            "top_tvd", "base_tvd", "dip", "dip_direction", "lithology", "provenance_type"
        ])
        for row in FORMATIONS:
            writer.writerow(list(row) + ["SYNTHETIC"])


def generate_reservoirs_csv(out_path: Path):
    reservoirs = [
        ("res-01", "fmt-04", "Tipam Main Sand", 2850.0, 75.0, 18.5, 250.0, "OIL", 0.35, 2100.0, 3400.0, "SYNTHETIC"),
        ("res-02", "fmt-06", "Barail Coal-Shale Gas Horizon", 4250.0, 92.0, 14.0, 45.0, "GAS", 0.05, 3800.0, 4900.0, "SYNTHETIC"),
        ("res-03", "fmt-07", "Barail 3rd Sand", 3450.0, 88.0, 21.0, 320.0, "OIL", 0.20, 3000.0, 4100.0, "SYNTHETIC")
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "reservoir_id", "formation_id", "reservoir_name", "pressure",
            "temperature", "porosity", "permeability", "fluid_type",
            "depletion_indicator", "pressure_window_min", "pressure_window_max", "provenance_type"
        ])
        for row in reservoirs:
            writer.writerow(row)


def generate_logs_csv(out_path: Path):
    """Generates synthetic wireline/LWD logs matching FORCE 2020 curve standards for Assam stratigraphy."""
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["well_id", "md", "GR", "RHOB", "NPHI", "DT", "RES", "SP", "CALI", "ROP", "MUDWEIGHT", "lithology", "provenance_type"])
        for w_id, w_name, field, lat, lon, kb, td_md, status in WELLS[:4]:
            for md in range(2100, 2500, 5):
                # Depleted Upper Tipam Sandstone profile
                is_clean_sand = (2200 <= md <= 2460)
                gr = 45.0 + random.uniform(-5, 8) if is_clean_sand else 95.0 + random.uniform(-10, 15)
                rhob = 2.22 + random.uniform(-0.02, 0.03) if is_clean_sand else 2.50 + random.uniform(-0.03, 0.04)
                nphi = 0.24 + random.uniform(-0.02, 0.02) if is_clean_sand else 0.15 + random.uniform(-0.02, 0.02)
                dt = 82.0 + random.uniform(-2, 3)
                res = 35.0 + random.uniform(-5, 10) if is_clean_sand else 8.5 + random.uniform(-1, 2)
                sp = -45.0 if is_clean_sand else -10.0
                cali = 8.5 + (0.4 if not is_clean_sand else 0.0)
                rop = 14.5 + random.uniform(-2, 3)
                mw = 1.16
                lith = "Depleted Sandstone" if is_clean_sand else "Carbonaceous Shale"
                writer.writerow([w_name, md, round(gr, 1), round(rhob, 3), round(nphi, 3), round(dt, 1), round(res, 2), sp, round(cali, 2), round(rop, 1), mw, lith, "SYNTHETIC"])


def generate_standardized_telemetry_csv(out_path: Path):
    """Standardized high-frequency drilling telemetry with MSE and anomaly indicators."""
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp", "well_id", "md", "tvd", "tvdss", "rop", "wob", "rpm",
            "torque", "hook_load", "spp", "flow_rate", "mud_weight_in",
            "mud_weight_out", "ecd", "pit_volume", "pump_rate", "mse",
            "torque_anomaly", "ecd_margin", "rop_anomaly", "pressure_anomaly", "provenance_type"
        ])
        t = 1700000000.0
        active_well = WELLS[0][1] # SYN-NHK-05
        for md in range(2400, 2450):
            is_hazard_zone = (md >= 2413)
            rop = 12.2 if is_hazard_zone else 18.5
            wob = 18.2
            rpm = 95.0
            torque = 15.4 if is_hazard_zone else 12.8
            hook_load = 185.0
            spp = 2950.0
            flow_rate = 640.0
            mwi = 1.16
            mwo = 1.16
            ecd = 1.21
            pit_vol = 320.0
            pump_rate = 640.0
            # Mechanical Specific Energy calculation
            mse = round((wob * 1000) / (0.7854 * (8.5**2)) + (13.33 * rpm * torque) / (rop * (8.5**2)), 1)
            t_anom = 1.25 if is_hazard_zone else 1.0
            ecd_marg = round(ecd - 1.14, 2)
            rop_anom = -0.34 if is_hazard_zone else 0.0
            p_anom = 0.05
            writer.writerow([
                t, active_well, md, round(md * 0.98, 1), round(md * 0.98 - 122.5, 1),
                rop, wob, rpm, torque, hook_load, spp, flow_rate, mwi, mwo,
                ecd, pit_vol, pump_rate, mse, t_anom, ecd_marg, rop_anom, p_anom, "SYNTHETIC"
            ])
            t += 1.0


def generate_all():
    print("🚜 Generating Calibrated Upper Assam Synthetic Dataset...")
    generate_wells_csv(TARGET_DIR / "wells.csv")
    generate_formations_csv(TARGET_DIR / "formations.csv")
    generate_reservoirs_csv(TARGET_DIR / "reservoirs.csv")
    generate_logs_csv(TARGET_DIR / "logs.csv")
    generate_standardized_telemetry_csv(TARGET_DIR / "drilling_telemetry.csv")

    # Also sync demo logs.csv for immediate UI/API availability
    generate_logs_csv(DEMO_DIR / "logs.csv")

    print(f"✅ Calibrated Upper Assam Dataset created in {TARGET_DIR}")


if __name__ == "__main__":
    generate_all()
