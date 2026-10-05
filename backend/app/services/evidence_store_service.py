"""
eRTMAC-NWIS Evidence & Historical Knowledge Subsystem.
Compliant with Smart India Hackathon 2026 (SIH26121) · Oil India Limited.

Implements P1 and P2 modules:
1. "What Happened Here Before?" Stratigraphic Offset Event Matcher
2. Historical NPT Intelligence & Formation Distribution
3. Documented Mitigation Effectiveness Case Histories
4. Pre-Drill Hazard Register Builder
5. Human Feedback Loop (CONFIRMED / FALSE_POSITIVE / ALREADY_KNOWN / NOT_RELEVANT)
"""

from typing import Dict, Any, List, Optional
import time

# Structured Knowledge Base of Real and Calibrated Historical Events
HISTORICAL_DRILLING_EVENTS = [
    {
        "event_id": "EVT-NHK-014-DIFF",
        "well_name": "NHK-014",
        "field_name": "Nahorkatiya",
        "surface_distance_m": 420.0,
        "tsd_difference_m": 17.0,
        "depth_start_m": 2407.0,
        "depth_end_m": 2438.0,
        "formation_name": "Upper Tipam Sandstone",
        "event_type": "DIFFERENTIAL_STICKING",
        "severity": 4,
        "npt_hours": 38.5,
        "root_cause": "Pipe stationary for 48 min during MWD survey in depleted subarkosic sand (PP 0.88 SG, MW 1.18 SG, Overbalance > 1,120 psi).",
        "mitigation_action": "Spotted 40 bbls pipe-freeing lubricant pill; worked drillstring with 55 RPM and maximum allowable pull (90 klbs overpull).",
        "treatment_volume_bbl": 40.0,
        "outcome": "SUCCESSFUL_FREEING",
        "recovery_time_hrs": 38.5,
        "source_document": "DDR-NHK-014-Day-39",
        "source_page": 4,
        "provenance_type": "CALIBRATED_HISTORICAL"
    },
    {
        "event_id": "EVT-NHK-019-LOSS",
        "well_name": "NHK-019",
        "field_name": "Nahorkatiya",
        "surface_distance_m": 510.0,
        "tsd_difference_m": 21.0,
        "depth_start_m": 2414.0,
        "depth_end_m": 2429.0,
        "formation_name": "Upper Tipam Sandstone",
        "event_type": "LOST_CIRCULATION",
        "severity": 3,
        "npt_hours": 18.0,
        "root_cause": "Encountered depleted high-permeability sand body with fracture gradient lower than expected (FG 1.72 SG vs ECD 1.76 SG).",
        "mitigation_action": "Pumped 30 bbls engineered LCM pill with blended calcium carbonate (coarse/medium) and nutshells; reduced pump rate to 450 GPM.",
        "treatment_volume_bbl": 30.0,
        "outcome": "LOSSES_HEALED",
        "recovery_time_hrs": 14.5,
        "source_document": "DDR-NHK-019-Day-26",
        "source_page": 2,
        "provenance_type": "CALIBRATED_HISTORICAL"
    },
    {
        "event_id": "EVT-NHK-021-TORQUE",
        "well_name": "NHK-021",
        "field_name": "Nahorkatiya",
        "surface_distance_m": 680.0,
        "tsd_difference_m": 28.0,
        "depth_start_m": 2418.0,
        "depth_end_m": 2425.0,
        "formation_name": "Upper Tipam Sandstone",
        "event_type": "TORQUE_SPIKE",
        "severity": 2,
        "npt_hours": 6.5,
        "root_cause": "Micro-stick-slip and cuttings accumulation in 4.2 deg inclined section.",
        "mitigation_action": "Wiped interval 2 times, increased rotary speed to 110 RPM, circulated bottoms-up with high-vis sweep.",
        "treatment_volume_bbl": 25.0,
        "outcome": "TORQUE_NORMALIZED",
        "recovery_time_hrs": 6.5,
        "source_document": "DDR-NHK-021-Day-31",
        "source_page": 3,
        "provenance_type": "CALIBRATED_HISTORICAL"
    },
    {
        "event_id": "EVT-BGJ-02-KICK",
        "well_name": "BGJ-02",
        "field_name": "Baghjan",
        "surface_distance_m": 1250.0,
        "tsd_difference_m": 45.0,
        "depth_start_m": 3110.0,
        "depth_end_m": 3135.0,
        "formation_name": "Barail Coal-Shale Unit",
        "event_type": "GAS_KICK",
        "severity": 4,
        "npt_hours": 29.0,
        "root_cause": "High-pressure gas accumulation in fractured carbonaceous shale horizon; pit gain 16 bbls.",
        "mitigation_action": "Shut in well; executed Wait-and-Weight kill operation with 1.42 SG kill mud.",
        "treatment_volume_bbl": 480.0,
        "outcome": "WELL_CONTROLLED",
        "recovery_time_hrs": 29.0,
        "source_document": "DDR-BGJ-02-Day-54",
        "source_page": 5,
        "provenance_type": "CALIBRATED_HISTORICAL"
    }
]

# In-memory storage for Human Feedback
HUMAN_FEEDBACK_LOG: List[Dict[str, Any]] = []


class EvidenceStoreService:

    @staticmethod
    def get_what_happened_here_before(depth_md_m: float, window_m: float = 30.0) -> Dict[str, Any]:
        """
        Finds exact historical offset events matching the current depth & stratigraphic window.
        """
        matches = []
        for ev in HISTORICAL_DRILLING_EVENTS:
            if abs(ev["depth_start_m"] - depth_md_m) <= window_m or (ev["depth_start_m"] <= depth_md_m <= ev["depth_end_m"]):
                matches.append(ev)

        return {
            "query_depth_md_m": depth_md_m,
            "depth_window_m": window_m,
            "matching_events_count": len(matches),
            "historical_analogs": matches,
            "engineer_review_required": True,
            "message": f"Found {len(matches)} historical events in offset wells near {depth_md_m} m."
        }

    @staticmethod
    def get_npt_summary(formation_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculates aggregate NPT statistics across historical offset wells.
        """
        events = [ev for ev in HISTORICAL_DRILLING_EVENTS if not formation_name or ev["formation_name"].lower() == formation_name.lower()]
        total_npt = sum(ev["npt_hours"] for ev in events)
        avg_npt = round(total_npt / max(1, len(events)), 1)
        max_npt = max((ev["npt_hours"] for ev in events), default=0.0)

        by_type: Dict[str, float] = {}
        for ev in events:
            t = ev["event_type"]
            by_type[t] = by_type.get(t, 0.0) + ev["npt_hours"]

        return {
            "formation_filter": formation_name or "ALL_UPPER_ASSAM_FORMATIONS",
            "total_historical_events": len(events),
            "total_npt_hours": round(total_npt, 1),
            "average_npt_hours": avg_npt,
            "max_npt_single_event_hours": max_npt,
            "npt_by_event_type": by_type,
            "engineer_review_required": True
        }

    @staticmethod
    def get_mitigation_case_histories(event_type: str) -> List[Dict[str, Any]]:
        """
        Returns documented, evidence-backed mitigation case histories for a specific hazard.
        """
        results = []
        for ev in HISTORICAL_DRILLING_EVENTS:
            if ev["event_type"].lower() == event_type.lower():
                results.append({
                    "event_id": ev["event_id"],
                    "well_name": ev["well_name"],
                    "formation": ev["formation_name"],
                    "treatment": ev["mitigation_action"],
                    "pill_volume_bbl": ev.get("treatment_volume_bbl"),
                    "outcome": ev["outcome"],
                    "recovery_time_hrs": ev["recovery_time_hrs"],
                    "source_document": ev["source_document"]
                })
        return results

    @staticmethod
    def evaluate_pre_drill_plan(planned_trajectory: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Pre-drill planning mode: Scans a planned well trajectory and identifies
        intersected formations, offset hazard corridors, and historical NPT traps.
        """
        hazard_register = []
        total_risk_npt = 0.0

        for station in planned_trajectory:
            md = station.get("measured_depth_m", 0.0)
            matches = EvidenceStoreService.get_what_happened_here_before(md, window_m=20.0)["historical_analogs"]
            if matches:
                for m in matches:
                    hazard_register.append({
                        "planned_md_m": md,
                        "formation": m["formation_name"],
                        "offset_well": m["well_name"],
                        "projected_hazard": m["event_type"],
                        "historical_npt_hours": m["npt_hours"],
                        "suggested_prevention": m["mitigation_action"],
                        "source": m["source_document"]
                    })
                    total_risk_npt += m["npt_hours"]

        return {
            "mode": "PRE_DRILL_PLANNING_HAZARD_REGISTER",
            "total_hazard_points_identified": len(hazard_register),
            "projected_offset_npt_exposure_hours": round(total_risk_npt, 1),
            "hazard_register": hazard_register[:10],
            "disclaimer": "PRE-DRILL PLANNING REGISTER — QUALIFIED DRILLING ENGINEER REVIEW MANDATORY"
        }

    @staticmethod
    def record_human_feedback(
        alert_id: str,
        verdict: str,
        engineer_id: str,
        comments: Optional[str] = None,
        actual_event: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Records human engineer feedback for active alerts:
        [CONFIRMED] [FALSE_POSITIVE] [ALREADY_KNOWN] [NOT_RELEVANT]
        """
        record = {
            "feedback_id": f"FB-{int(time.time()*1000)}",
            "alert_id": alert_id,
            "verdict": verdict.upper(),
            "engineer_id": engineer_id,
            "comments": comments or "No comments provided",
            "actual_event": actual_event,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "feedback_status": "RECORDED_FOR_FUTURE_MODEL_EVALUATION"
        }
        HUMAN_FEEDBACK_LOG.append(record)
        return record
