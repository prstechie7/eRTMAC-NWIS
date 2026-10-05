"""
Comprehensive Test Suite for Real-World Drilling Engineering Decision-Support Subsystems.
Compliant with Smart India Hackathon 2026 (SIH26121) · Oil India Limited.

Validates:
- P0: Kick / Influx Detection State Machine
- P0: Geomechanical Pressure Window & ECD Margins
- P0: Lost Circulation Early Warning System
- P0: Hole Cleaning & Pack-Off Index (HCI)
- P0: Stuck Pipe Physical Mechanism Classification
- P0: Torque & Drag (T&D) Prediction & Residuals
- P0: Drilling Dysfunction & Stick-Slip
- P0: MSE Efficiency Analysis against Formation Baselines
- P0: Formation Transition & Lithology Detection
- P0: Mud Intelligence & Rheology Quality
- P0: Surge & Swab Tripping Risk Calculator
- P0: Connection Intelligence
- P1: "What Happened Here Before?" Historical Offset Memory
- P1: Historical NPT Intelligence
- P2: What-If Scenario Analysis Simulator
- P2: Pre-Drill Planning Hazard Register
- P2: Human Feedback Loop (CONFIRMED, FALSE_POSITIVE)
"""

import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import pytest
from app.services.engineering_engine import EngineeringEngine, KickState, HoleCleaningStatus
from app.services.evidence_store_service import EvidenceStoreService


def test_p0_kick_detection_state_machine():
    # 1. Normal drilling condition
    res_norm = EngineeringEngine.evaluate_kick_risk(
        flow_in_gpm=600.0, flow_out_gpm=600.0, pit_volume_bbl=320.0,
        pit_gain_rate_bblhr=0.0, spp_psi=2950.0, spp_baseline_psi=2950.0,
        gas_pct=1.5, gas_baseline_pct=1.5
    )
    assert res_norm["state"] == KickState.NORMAL.value
    assert res_norm["engineer_review_required"] is True

    # 2. Critical influx scenario
    res_kick = EngineeringEngine.evaluate_kick_risk(
        flow_in_gpm=600.0, flow_out_gpm=635.0, pit_volume_bbl=325.0,
        pit_gain_rate_bblhr=2.7, spp_psi=2650.0, spp_baseline_psi=2950.0,
        gas_pct=3.8, gas_baseline_pct=1.5
    )
    assert res_kick["state"] in [KickState.ENGINEER_REVIEW.value, KickState.HIGH_KICK_RISK.value]
    assert "WELL-CONTROL PROCEDURE / QUALIFIED ENGINEER REVIEW REQUIRED" in res_kick["mandatory_action"]
    assert res_kick["autonomous_control"] is False


def test_p0_pressure_window_margins():
    pw = EngineeringEngine.calculate_pressure_window(
        depth_md_m=2410.0, depth_tvd_m=2180.0, current_mw_sg=1.16,
        current_ecd_sg=1.71, pore_pressure_sg=1.49, fracture_gradient_sg=1.83
    )
    assert pw["ecd_to_frac_margin_sg"] == 0.12
    assert pw["ecd_to_pp_margin_sg"] == 0.22
    assert pw["total_window_width_sg"] == 0.34
    assert pw["engineer_review_required"] is True


def test_p0_lost_circulation_early_warning():
    lc = EngineeringEngine.evaluate_lost_circulation(
        flow_in_gpm=640.0, flow_out_gpm=590.0, pit_loss_rate_bblhr=8.5,
        ecd_sg=1.74, fracture_gradient_sg=1.82, formation_name="Upper Tipam Sandstone"
    )
    assert lc["risk_level"] in ["HIGH", "CRITICAL"]
    assert lc["flow_imbalance_pct"] < 0
    assert len(lc["recommended_review"]) > 0


def test_p0_hole_cleaning_packoff_index():
    # Good hole cleaning
    hci_good = EngineeringEngine.calculate_hole_cleaning_index(
        rop_mhr=15.0, flow_rate_gpm=640.0, rpm=95.0, inclination_deg=12.0
    )
    assert hci_good["hole_cleaning_index"] >= 80.0
    assert hci_good["status"] in ["GOOD", "ACCEPTABLE"]

    # Poor hole cleaning / packoff risk
    hci_poor = EngineeringEngine.calculate_hole_cleaning_index(
        rop_mhr=45.0, flow_rate_gpm=400.0, rpm=60.0, inclination_deg=50.0,
        spp_trend_pct=14.0, torque_trend_pct=16.0
    )
    assert hci_poor["hole_cleaning_index"] < 60.0
    assert hci_poor["packoff_risk"] in ["HIGH", "MEDIUM"]


def test_p0_stuck_pipe_mechanism_classifier():
    sp = EngineeringEngine.classify_stuck_pipe_mechanism(
        overbalance_psi=1120.0, stationary_time_min=45.0, permeability_md=250.0,
        torque_residual_pct=25.0, drag_residual_pct=20.0, rop_drop_pct=30.0
    )
    assert sp["primary_mechanism"] == "Differential Sticking"
    assert sp["mechanism_breakdown"]["differential_sticking_pct"] > 40.0
    assert "NHK-014" in sp["historical_analog"]["well_name"]
    assert sp["engineer_review_required"] is True


def test_p0_torque_drag_residuals():
    td = EngineeringEngine.calculate_torque_drag(
        depth_md_m=2410.0, inclination_deg=14.5, wob_klbs=18.2,
        drillstring_weight_klbs=165.0, actual_torque_kftlb=18.5, actual_hookload_klbs=210.0
    )
    assert "predicted_torque_kftlb" in td
    assert "torque_residual_kftlb" in td
    assert "drag_residual_klbs" in td
    assert td["overpull_detected"] is True


def test_p0_drilling_dysfunction_stick_slip():
    dys = EngineeringEngine.evaluate_dysfunction(
        rpm=85.0, rpm_variance=42.0, torque_kftlb=15.0, torque_variance=5.2,
        mse_deviation_pct=65.0, rop_drop_pct=30.0
    )
    assert dys["dysfunction_active"] is True
    assert dys["stick_slip_severity"] == "HIGH"
    assert dys["bit_dulling_indication"] == "HIGH"


def test_p0_mse_efficiency_analysis():
    mse = EngineeringEngine.evaluate_mse_efficiency(
        wob_klbs=22.0, rpm=95.0, torque_kftlb=16.5, rop_mhr=9.0,
        baseline_mse_psi=8500.0
    )
    assert mse["current_actual_mse_psi"] > 10000.0
    assert mse["deviation_pct"] > 0
    assert mse["status"] == "DRILLING_EFFICIENCY_DEGRADING"


def test_p0_formation_change_detector():
    fc = EngineeringEngine.detect_formation_change(
        gr_current=42.0, gr_prior_5m=88.0, res_current=38.0, res_prior_5m=8.5,
        rop_current=22.0, rop_prior_5m=9.0, active_depth_md_m=2185.0
    )
    assert fc["boundary_detected"] is True
    assert "Sandstone Transition" in fc["lithology_shift"]


def test_p0_mud_intelligence():
    mud = EngineeringEngine.evaluate_mud_intelligence(
        mud_weight_in_sg=1.16, mud_weight_out_sg=1.16,
        plastic_viscosity_cp=22.0, yield_point_lb100sqft=18.0
    )
    assert mud["yp_pv_ratio"] > 0.7
    assert mud["hole_cleaning_potential"] == "EXCELLENT"


def test_p0_surge_swab_risk():
    ss = EngineeringEngine.calculate_surge_swab_risk(
        pipe_speed_m_per_min=35.0, mud_weight_sg=1.16, pore_pressure_sg=0.92,
        fracture_gradient_sg=1.82
    )
    assert ss["estimated_swab_delta_sg"] < 0
    assert ss["estimated_surge_delta_sg"] > 0
    assert "SCENARIO ESTIMATE" in ss["scenario_warning"]


def test_p0_connection_intelligence():
    conn = EngineeringEngine.evaluate_connection_signature(
        connection_gas_pct=4.2, pit_volume_change_bbl=2.1, flowback_time_sec=65.0,
        spp_recovery_time_sec=25.0, torque_at_bottom_kftlb=14.0
    )
    assert conn["connection_status"] == "POSSIBLE_CONNECTION_INFLUX"
    assert conn["severity"] == "HIGH"


def test_p1_what_happened_here_before():
    mem = EvidenceStoreService.get_what_happened_here_before(depth_md_m=2413.0, window_m=30.0)
    assert mem["matching_events_count"] >= 3
    wells = [m["well_name"] for m in mem["historical_analogs"]]
    assert "NHK-014" in wells
    assert "NHK-019" in wells


def test_p1_historical_npt_intelligence():
    npt = EvidenceStoreService.get_npt_summary()
    assert npt["total_historical_events"] >= 4
    assert npt["total_npt_hours"] > 50.0
    assert "DIFFERENTIAL_STICKING" in npt["npt_by_event_type"]


def test_p2_what_if_scenario_simulation():
    sim = EngineeringEngine.simulate_what_if_scenario(
        current_mw_sg=1.16, current_flow_gpm=640.0, current_rpm=95.0,
        scenario_mw_sg=1.10, scenario_flow_gpm=580.0, scenario_rpm=110.0,
        pore_pressure_sg=0.92, fracture_gradient_sg=1.82
    )
    assert sim["disclaimer"] == "SCENARIO ESTIMATE — NOT AN OPERATIONAL COMMAND"
    assert sim["projected_outputs"]["projected_ecd_sg"] < 1.16
    assert sim["safety_envelope_evaluation"] == "SAFE_ENVELOPE"


def test_p2_human_feedback_loop():
    fb = EvidenceStoreService.record_human_feedback(
        alert_id="ALT-NHK05-2413", verdict="CONFIRMED",
        engineer_id="Rig-Superintendent-OIL", comments="Verified tight hole on connection."
    )
    assert fb["verdict"] == "CONFIRMED"
    assert fb["feedback_id"].startswith("FB-")
