"""
Synthetic Dataset Loader and Inspector for eRTMAC-NWIS.
Validates data/synthetic_assam_wells.json.
"""

import json
import os
import re
from typing import Dict, List, Any


def get_project_root() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(current_dir, "..", ".."))


def load_synthetic_wells(data_path: str = None) -> Dict[str, Any]:
    """
    Loads and parses data/synthetic_assam_wells.json.
    """
    if data_path is None:
        data_path = os.path.join(get_project_root(), "data", "synthetic_assam_wells.json")

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Synthetic dataset not found at: {data_path}")

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def validate_well_record(well: Dict[str, Any]) -> List[str]:
    """
    Validates a single well object for schema compliance and geographic plausibility.
    Returns list of validation errors (empty if valid).
    """
    errors = []

    # Well Name must start with SYN-
    name = well.get("well_name", "")
    if not name.startswith("SYN-"):
        errors.append(f"Well name '{name}' does not start with 'SYN-'")

    # Name format SYN-<FIELD>-<NUMBER>
    if not re.match(r"^SYN-[A-Z]+-[0-9]{2,}$", name):
        errors.append(f"Well name '{name}' does not conform to pattern SYN-<FIELD>-<NUM>")

    # Surface coordinates for Upper Assam Shelf
    lat = well.get("surface_lat")
    lon = well.get("surface_lon")
    if lat is None or not (26.0 <= lat <= 28.5):
        errors.append(f"Invalid surface latitude for Assam Basin: {lat}")
    if lon is None or not (94.0 <= lon <= 96.5):
        errors.append(f"Invalid surface longitude for Assam Basin: {lon}")

    # KB elevation
    kb = well.get("kb_elevation_m")
    if kb is None or kb <= 0 or kb > 500:
        errors.append(f"Invalid Kelly Bushing elevation: {kb}")

    # Total depth
    td = well.get("total_depth_md_m")
    if td is not None and td < 1000:
        errors.append(f"Total depth {td} is unrealistically shallow for Assam basin targets")

    return errors
