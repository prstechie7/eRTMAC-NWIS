"""
Reservoir + Formation Correlation Engine for eRTMAC-NWIS.
Compliant with SIH26121 (Oil India Limited).
"""

import math
from typing import List, Dict, Any, Optional
from app.models.schemas import OffsetAnalogWell, ProvenanceType


class CorrelationWeights:
    def __init__(
        self,
        distance_weight: float = 0.20,
        formation_weight: float = 0.20,
        depth_weight: float = 0.15,
        reservoir_weight: float = 0.15,
        trajectory_weight: float = 0.10,
        drilling_signature_weight: float = 0.10,
        event_similarity_weight: float = 0.10
    ):
        total = (distance_weight + formation_weight + depth_weight + reservoir_weight + 
                 trajectory_weight + drilling_signature_weight + event_similarity_weight)
        # Normalize weights so they sum to 1.0
        if total <= 0:
            total = 1.0
        self.w_distance = distance_weight / total
        self.w_formation = formation_weight / total
        self.w_depth = depth_weight / total
        self.w_reservoir = reservoir_weight / total
        self.w_trajectory = trajectory_weight / total
        self.w_drilling = drilling_signature_weight / total
        self.w_event = event_similarity_weight / total

    def to_dict(self) -> Dict[str, float]:
        return {
            "distance_weight": round(self.w_distance, 3),
            "formation_weight": round(self.w_formation, 3),
            "depth_weight": round(self.w_depth, 3),
            "reservoir_weight": round(self.w_reservoir, 3),
            "trajectory_weight": round(self.w_trajectory, 3),
            "drilling_signature_weight": round(self.w_drilling, 3),
            "event_similarity_weight": round(self.w_event, 3)
        }


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r_earth = 6371.0  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r_earth * c


class CorrelationEngine:
    def __init__(self, weights: Optional[CorrelationWeights] = None):
        self.weights = weights or CorrelationWeights()

    def find_analogs(
        self,
        active_well_id: str,
        active_lat: float,
        active_lon: float,
        active_depth_md: float,
        active_formation: str,
        active_reservoir: Optional[str] = None,
        radius_km: float = 10.0,
        wells_database: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Computes transparent 7-factor analog correlation scores for offset wells.
        """
        if wells_database is None:
            wells_database = []

        analogs = []

        for w in wells_database:
            well_id = w.get("well_id", "")
            if well_id == active_well_id:
                continue

            well_name = w.get("well_name", well_id)
            w_lat = w.get("surface_lat", w.get("latitude", 0.0))
            w_lon = w.get("surface_lon", w.get("longitude", 0.0))

            dist_km = haversine_distance_km(active_lat, active_lon, w_lat, w_lon)
            if dist_km > radius_km:
                continue

            # 1. Distance score (1 - dist / radius_km)
            distance_score = max(0.0, 1.0 - (dist_km / max(0.1, radius_km)))

            # 2. Formation similarity
            formations = [f.get("name", f.get("formation_name", "")) for f in w.get("formation_tops", [])]
            formation_match = 1.0 if active_formation in formations else 0.5 if len(formations) > 0 else 0.2

            # 3. Depth delta score
            w_td = w.get("total_depth_md_m", w.get("total_depth_md", 3000.0))
            depth_delta = abs(active_depth_md - w_td)
            depth_score = max(0.0, 1.0 - (depth_delta / 3000.0))

            # 4. Reservoir similarity
            w_reservoirs = w.get("reservoirs", [])
            if active_reservoir:
                reservoir_match = 1.0 if any(r.get("reservoir_name") == active_reservoir for r in w_reservoirs) else 0.6
            else:
                reservoir_match = 0.85

            # 5. Trajectory similarity (default baseline for vertical/directional wells)
            trajectory_similarity = 0.90 if w.get("status") == "COMPLETED" else 0.80

            # 6. Drilling signature similarity
            drilling_signature = 0.88

            # 7. Historical event similarity / relevance
            hazards = w.get("historical_hazards", w.get("events", []))
            event_count = len(hazards)
            event_similarity = min(1.0, 0.4 + (event_count * 0.15))
            risk_relevance = round(min(1.0, event_similarity * 0.9), 2)

            # Combined transparent weighted score
            score = (
                self.weights.w_distance * distance_score +
                self.weights.w_formation * formation_match +
                self.weights.w_depth * depth_score +
                self.weights.w_reservoir * reservoir_match +
                self.weights.w_trajectory * trajectory_similarity +
                self.weights.w_drilling * drilling_signature +
                self.weights.w_event * event_similarity
            )

            analog_score = round(score, 2)

            analogs.append({
                "well_id": well_id,
                "well_name": well_name,
                "analog_score": analog_score,
                "distance_km": round(dist_km, 2),
                "formation_match": round(formation_match, 2),
                "depth_delta_m": round(depth_delta, 1),
                "reservoir_match": round(reservoir_match, 2),
                "trajectory_similarity": round(trajectory_similarity, 2),
                "drilling_signature": round(drilling_signature, 2),
                "historical_event_count": event_count,
                "risk_relevance": risk_relevance,
                "provenance_type": w.get("provenance_type", ProvenanceType.SYNTHETIC.value)
            })

        analogs.sort(key=lambda x: x["analog_score"], reverse=True)
        return analogs
