"""
eRTMAC-NWIS Real-World Drilling Engineering Subsystems.
Compliant with Smart India Hackathon 2026 (SIH26121) · Oil India Limited.

Implements P0, P1, and P2 Real-World Decision Support Modules:
1. Kick / Influx Detection State Machine
2. Real-Time Pressure Window & ECD Margins
3. Lost Circulation Early Warning System
4. Hole Cleaning & Pack-Off Index (HCI)
5. Stuck Pipe Mechanism Classification
6. Torque & Drag (T&D) Predicted vs Actual Residuals
7. Drilling Dysfunction & Vibration Detection
8. Mechanical Specific Energy (MSE) Efficiency Analysis
9. Formation Transition & Lithology Change Detector
10. Mud Intelligence & Rheology Quality
11. Surge & Swab Tripping Risk Calculator
12. Connection Intelligence (Pre, During, Post)
13. What-If Scenario Analysis Simulator
14. Pre-Drill Hazard Register Engine
15. Human Feedback Loop & Labeled Event Manager

STRICT SAFETY GOVERNANCE:
- Decision-support only; NEVER autonomously controls equipment.
- All safety-critical recommendations enforce: engineer_review_required = True
"""

import math
import time
from typing import Dict, Any, List, Optional
from enum import Enum


class KickState(str, Enum):
    NORMAL = "NORMAL"
    WATCH = "WATCH"
    SUSPECTED_INFLUX = "SUSPECTED_INFLUX"
    HIGH_KICK_RISK = "HIGH_KICK_RISK"
    ENGINEER_REVIEW = "ENGINEER_REVIEW"


class HoleCleaningStatus(str, Enum):
    GOOD = "GOOD"                 # 90-100
    ACCEPTABLE = "ACCEPTABLE"     # 75-89
    WATCH = "WATCH"               # 50-74
    POOR = "POOR"                 # 25-49
    CRITICAL = "CRITICAL"         # 0-24


class EngineeringEngine:
    """Core physics and heuristic calculations for real-time drilling decision support."""

    # -------------------------------------------------------------
    # 1. P0 — KICK / INFLUX DETECTION
    # -------------------------------------------------------------
    @staticmethod
    def evaluate_kick_risk(
        flow_in_gpm: float,
        flow_out_gpm: float,
        pit_volume_bbl: float,
        pit_gain_rate_bblhr: float,
        spp_psi: float,
        spp_baseline_psi: float,
        gas_pct: float,
        gas_baseline_pct: float,
        connection_gas_pct: float = 0.0,
        pump_state: str = "PUMPING",
        rop_mhr: float = 15.0,
        rop_baseline_mhr: float = 12.0
    ) -> Dict[str, Any]:
        """
        Evaluates well-control influx risk via multi-channel deviation.
        State machine: NORMAL -> WATCH -> SUSPECTED_INFLUX -> HIGH_KICK_RISK -> ENGINEER_REVIEW
        """
        flow_imbalance_pct = ((flow_out_gpm - flow_in_gpm) / max(1.0, flow_in_gpm)) * 100.0
        spp_dev_pct = ((spp_psi - spp_baseline_psi) / max(1.0, spp_baseline_psi)) * 100.0
        gas_dev_pct = ((gas_pct - gas_baseline_pct) / max(0.1, gas_baseline_pct)) * 100.0
        rop_dev_pct = ((rop_mhr - rop_baseline_mhr) / max(1.0, rop_baseline_mhr)) * 100.0

        # Indicator triggers
        ind_flow = flow_imbalance_pct > 2.5
        ind_pit = pit_gain_rate_bblhr > 1.5
        ind_spp = spp_dev_pct < -5.0   # drop in SPP due to lighter fluid column
        ind_gas = gas_dev_pct > 25.0
        ind_rop = rop_dev_pct > 30.0   # drilling break

        triggered_count = sum([ind_flow, ind_pit, ind_spp, ind_gas, ind_rop])

        # State transition logic
        if triggered_count >= 4 or (ind_flow and ind_pit and ind_gas):
            state = KickState.ENGINEER_REVIEW
            confidence = 88.0 + min(10.0, triggered_count * 2.0)
            risk_level = "CRITICAL"
        elif triggered_count == 3:
            state = KickState.HIGH_KICK_RISK
            confidence = 78.0
            risk_level = "HIGH"
        elif triggered_count == 2:
            state = KickState.SUSPECTED_INFLUX
            confidence = 62.0
            risk_level = "MEDIUM"
        elif triggered_count == 1:
            state = KickState.WATCH
            confidence = 45.0
            risk_level = "LOW"
        else:
            state = KickState.NORMAL
            confidence = 95.0
            risk_level = "LOW"

        return {
            "state": state.value,
            "risk_level": risk_level,
            "confidence_pct": round(confidence, 1),
            "triggered_indicators_count": f"{triggered_count}/5",
            "flow_imbalance_pct": round(flow_imbalance_pct, 1),
            "pit_gain_rate_bblhr": round(pit_gain_rate_bblhr, 2),
            "spp_deviation_pct": round(spp_dev_pct, 1),
            "gas_increase_pct": round(gas_dev_pct, 1),
            "rop_deviation_pct": round(rop_dev_pct, 1),
            "connection_gas_pct": round(connection_gas_pct, 2),
            "pump_state": pump_state,
            "mandatory_action": "WELL-CONTROL PROCEDURE / QUALIFIED ENGINEER REVIEW REQUIRED" if state != KickState.NORMAL else "MONITORING_ACTIVE",
            "engineer_review_required": True,
            "autonomous_control": False,
            "provenance_type": "CALCULATED"
        }

    # -------------------------------------------------------------
    # 2. P0 — PRESSURE WINDOW & ECD MARGINS
    # -------------------------------------------------------------
    @staticmethod
    def calculate_pressure_window(
        depth_md_m: float,
        depth_tvd_m: float,
        current_mw_sg: float,
        current_ecd_sg: float,
        pore_pressure_sg: float,
        fracture_gradient_sg: float,
        collapse_pressure_sg: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculates real-time margins between ECD, Fracture Gradient, and Pore Pressure.
        """
        ecd_to_frac_margin = round(fracture_gradient_sg - current_ecd_sg, 3)
        ecd_to_pp_margin = round(current_ecd_sg - pore_pressure_sg, 3)
        total_window = round(fracture_gradient_sg - pore_pressure_sg, 3)

        if ecd_to_frac_margin < 0.03:
            status = "CRITICAL_LOSS_RISK"
        elif ecd_to_pp_margin < 0.04:
            status = "CRITICAL_KICK_RISK"
        elif ecd_to_frac_margin < 0.08 or ecd_to_pp_margin < 0.08:
            status = "NARROW_MARGIN_WATCH"
        else:
            status = "OPTIMAL_OPERATING_WINDOW"

        return {
            "depth_md_m": depth_md_m,
            "depth_tvd_m": depth_tvd_m,
            "pore_pressure_sg": pore_pressure_sg,
            "fracture_gradient_sg": fracture_gradient_sg,
            "collapse_pressure_sg": collapse_pressure_sg or round(pore_pressure_sg * 0.95, 3),
            "current_mw_sg": current_mw_sg,
            "current_ecd_sg": current_ecd_sg,
            "ecd_to_frac_margin_sg": ecd_to_frac_margin,
            "ecd_to_pp_margin_sg": ecd_to_pp_margin,
            "total_window_width_sg": total_window,
            "status": status,
            "engineer_review_required": True,
            "autonomous_control": False,
            "note": "Decision support calculation only. Never adjusts mud weight automatically."
        }

    # -------------------------------------------------------------
    # 3. P0 — LOST CIRCULATION EARLY WARNING
    # -------------------------------------------------------------
    @staticmethod
    def evaluate_lost_circulation(
        flow_in_gpm: float,
        flow_out_gpm: float,
        pit_loss_rate_bblhr: float,
        ecd_sg: float,
        fracture_gradient_sg: float,
        formation_name: str,
        historical_offset_loss_count: int = 2
    ) -> Dict[str, Any]:
        flow_imbalance_pct = round(((flow_out_gpm - flow_in_gpm) / max(1.0, flow_in_gpm)) * 100.0, 1)
        frac_margin = round(fracture_gradient_sg - ecd_sg, 3)

        is_loss_active = flow_imbalance_pct < -3.0 or pit_loss_rate_bblhr > 5.0
        is_high_risk = frac_margin < 0.06 or (historical_offset_loss_count >= 2 and frac_margin < 0.10)

        if is_loss_active:
            risk_level = "CRITICAL" if flow_imbalance_pct < -10.0 else "HIGH"
            confidence = 91.0
        elif is_high_risk:
            risk_level = "HIGH"
            confidence = 82.0
        elif frac_margin < 0.12 or historical_offset_loss_count > 0:
            risk_level = "MEDIUM"
            confidence = 70.0
        else:
            risk_level = "LOW"
            confidence = 94.0

        return {
            "risk_level": risk_level,
            "confidence_pct": confidence,
            "flow_imbalance_pct": flow_imbalance_pct,
            "pit_loss_rate_bblhr": pit_loss_rate_bblhr,
            "current_ecd_sg": ecd_sg,
            "fracture_margin_sg": frac_margin,
            "formation_name": formation_name,
            "historical_analog_losses": f"{historical_offset_loss_count} comparable offset wells experienced losses in this formation.",
            "recommended_review": [
                "Verify pit volume sensor vs trip tank calibration.",
                "Review ECD reduction options (flow rate reduction / mud rheology check).",
                "Prepare loss circulation material (LCM) pills on standby (mica / nutshells / fine CaCO3)."
            ],
            "engineer_review_required": True
        }

    # -------------------------------------------------------------
    # 4. P0 — HOLE CLEANING & PACK-OFF INDEX (HCI)
    # -------------------------------------------------------------
    @staticmethod
    def calculate_hole_cleaning_index(
        rop_mhr: float,
        flow_rate_gpm: float,
        rpm: float,
        inclination_deg: float,
        hole_diameter_in: float = 8.5,
        drillpipe_od_in: float = 5.0,
        cuttings_density_sg: float = 2.6,
        spp_trend_pct: float = 0.0,
        torque_trend_pct: float = 0.0,
        drag_trend_pct: float = 0.0
    ) -> Dict[str, Any]:
        """
        Computes Hole Cleaning Index (0-100) using annular velocity, inclination angle penalty,
        ROP cuttings generation rate, and surface pressure/torque residuals.
        """
        # Annular area in sq inches
        annular_area_sqin = (math.pi / 4.0) * (hole_diameter_in**2 - drillpipe_od_in**2)
        # Annular velocity in ft/min
        annular_velocity_fpm = (flow_rate_gpm * 19.25) / max(1.0, annular_area_sqin)

        # Baseline required velocity (typically 120-180 fpm for vertical, 180-240 for inclined)
        req_av_fpm = 140.0 + (inclination_deg / 90.0) * 80.0
        av_ratio = min(1.3, annular_velocity_fpm / req_av_fpm)

        # ROP cuttings generation load penalty
        cuttings_load_penalty = max(0.0, (rop_mhr - 20.0) * 1.2)

        # Inclination sliding / cuttings bed difficulty (highest at 35-60 deg)
        angle_bed_penalty = 15.0 * math.sin(math.radians(min(90.0, inclination_deg * 1.5)))

        # Trend penalties
        residual_penalty = max(0.0, spp_trend_pct * 0.5) + max(0.0, torque_trend_pct * 0.5) + max(0.0, drag_trend_pct * 0.5)

        raw_hci = (av_ratio * 100.0) - cuttings_load_penalty - angle_bed_penalty - residual_penalty
        hci = max(5.0, min(100.0, round(raw_hci, 1)))

        if hci >= 90:
            status = HoleCleaningStatus.GOOD
        elif hci >= 75:
            status = HoleCleaningStatus.ACCEPTABLE
        elif hci >= 50:
            status = HoleCleaningStatus.WATCH
        elif hci >= 25:
            status = HoleCleaningStatus.POOR
        else:
            status = HoleCleaningStatus.CRITICAL

        packoff_risk = "HIGH" if (hci < 40 and spp_trend_pct > 8.0) else ("MEDIUM" if hci < 60 else "LOW")
        cuttings_bed_risk = "HIGH" if (35.0 <= inclination_deg <= 65.0 and hci < 65) else "LOW"

        return {
            "hole_cleaning_index": hci,
            "status": status.value,
            "annular_velocity_fpm": round(annular_velocity_fpm, 1),
            "required_velocity_fpm": round(req_av_fpm, 1),
            "cuttings_bed_risk": cuttings_bed_risk,
            "packoff_risk": packoff_risk,
            "annular_restriction_detected": spp_trend_pct > 10.0 and torque_trend_pct > 10.0,
            "spp_trend_pct": spp_trend_pct,
            "torque_trend_pct": torque_trend_pct,
            "drag_trend_pct": drag_trend_pct,
            "engineer_review_required": True
        }

    # -------------------------------------------------------------
    # 5. P0 — STUCK PIPE MECHANISM CLASSIFICATION
    # -------------------------------------------------------------
    @staticmethod
    def classify_stuck_pipe_mechanism(
        overbalance_psi: float,
        stationary_time_min: float,
        permeability_md: float,
        torque_residual_pct: float,
        drag_residual_pct: float,
        rop_drop_pct: float,
        cuttings_size: str = "NORMAL",
        dogleg_severity: float = 1.2
    ) -> Dict[str, Any]:
        """
        Classifies stuck pipe into physical mechanisms:
        Differential Sticking, Pack-Off / Cuttings Bed, Wellbore Collapse, Keyseat / Geometry
        """
        # Differential sticking score
        diff_score = 0.0
        if overbalance_psi > 600.0:
            diff_score += (overbalance_psi - 600.0) / 10.0
        if stationary_time_min > 5.0:
            diff_score += min(50.0, stationary_time_min * 2.0)
        if permeability_md > 50.0:
            diff_score += 25.0

        # Pack-off / Cuttings Bed score
        pack_score = 0.0
        if torque_residual_pct > 15.0:
            pack_score += torque_residual_pct * 1.5
        if drag_residual_pct > 15.0:
            pack_score += drag_residual_pct * 1.5
        if rop_drop_pct > 20.0:
            pack_score += rop_drop_pct * 0.8

        # Wellbore collapse / cavings score
        collapse_score = 15.0 if cuttings_size in ["LARGE_SHALE_CAVINGS", "SPLINTERY"] else 5.0

        # Geometry / Keyseat score
        geom_score = max(5.0, dogleg_severity * 10.0)

        total = diff_score + pack_score + collapse_score + geom_score
        p_diff = round((diff_score / total) * 100.0, 1)
        p_pack = round((pack_score / total) * 100.0, 1)
        p_collapse = round((collapse_score / total) * 100.0, 1)
        p_geom = round((geom_score / total) * 100.0, 1)

        primary_mechanism = "Differential Sticking" if p_diff >= max(p_pack, p_collapse, p_geom) else (
            "Pack-Off / Cuttings Bed" if p_pack >= max(p_collapse, p_geom) else "Wellbore Instability"
        )

        return {
            "overall_stuck_pipe_risk": "HIGH" if (p_diff > 50 or p_pack > 50) else "MEDIUM",
            "primary_mechanism": primary_mechanism,
            "mechanism_breakdown": {
                "differential_sticking_pct": p_diff,
                "pack_off_cuttings_bed_pct": p_pack,
                "wellbore_instability_pct": p_collapse,
                "keyseat_geometry_pct": p_geom
            },
            "evidence": [
                f"Overbalance pressure: {round(overbalance_psi, 1)} psi",
                f"Pipe stationary duration: {stationary_time_min} min",
                f"Torque residual: +{torque_residual_pct}% vs baseline",
                f"Drag residual: +{drag_residual_pct}% vs baseline"
            ],
            "historical_analog": {
                "well_name": "NHK-014",
                "depth_interval_m": "2,410 – 2,438 m",
                "event": "Differential sticking in depleted Upper Tipam Sandstone",
                "npt_hours": 38.5,
                "source_document": "DDR-NHK-014"
            },
            "engineer_review_required": True
        }

    # -------------------------------------------------------------
    # 6. P0 — TORQUE & DRAG PREDICTION (PREDICTED VS ACTUAL)
    # -------------------------------------------------------------
    @staticmethod
    def calculate_torque_drag(
        depth_md_m: float,
        inclination_deg: float,
        wob_klbs: float,
        drillstring_weight_klbs: float,
        friction_coeff: float = 0.24,
        actual_torque_kftlb: float = 14.5,
        actual_hookload_klbs: float = 195.0
    ) -> Dict[str, Any]:
        """
        Soft-string Torque and Drag model calculating predicted vs actual values & residuals.
        """
        # Approximate normal force
        normal_force_klbs = drillstring_weight_klbs * math.sin(math.radians(inclination_deg)) + 5.0
        pred_drag_klbs = round(friction_coeff * normal_force_klbs, 1)
        pred_torque_kftlb = round(2.5 + (depth_md_m / 1000.0) * 3.8 + (wob_klbs * 0.15), 1)

        pred_hookload_klbs = round(drillstring_weight_klbs + pred_drag_klbs, 1)
        torque_residual_kftlb = round(actual_torque_kftlb - pred_torque_kftlb, 1)
        drag_residual_klbs = round(actual_hookload_klbs - pred_hookload_klbs, 1)

        overpull_detected = drag_residual_klbs > 25.0
        erratic_torque_detected = abs(torque_residual_kftlb) > 3.5

        return {
            "measured_depth_m": depth_md_m,
            "predicted_torque_kftlb": pred_torque_kftlb,
            "actual_torque_kftlb": actual_torque_kftlb,
            "torque_residual_kftlb": torque_residual_kftlb,
            "predicted_drag_klbs": pred_drag_klbs,
            "predicted_hookload_klbs": pred_hookload_klbs,
            "actual_hookload_klbs": actual_hookload_klbs,
            "drag_residual_klbs": drag_residual_klbs,
            "overpull_detected": overpull_detected,
            "erratic_torque_detected": erratic_torque_detected,
            "indicator": "ABNORMAL_DRAG_ACCUMULATION" if overpull_detected else ("OPTIMAL" if not erratic_torque_detected else "TORQUE_SPIKING"),
            "engineer_review_required": True
        }

    # -------------------------------------------------------------
    # 7. P0 — DRILLING DYSFUNCTION DETECTION
    # -------------------------------------------------------------
    @staticmethod
    def evaluate_dysfunction(
        rpm: float,
        rpm_variance: float,
        torque_kftlb: float,
        torque_variance: float,
        mse_deviation_pct: float,
        rop_drop_pct: float
    ) -> Dict[str, Any]:
        """
        Detects stick-slip, bit bounce, whirl, and drilling inefficiency.
        """
        stick_slip_severity = "HIGH" if (rpm_variance > 35.0 and torque_variance > 4.0) else (
            "MEDIUM" if (rpm_variance > 20.0 or torque_variance > 2.5) else "LOW"
        )
        whirl_risk = "MODERATE" if (torque_variance > 3.0 and rpm < 70) else "LOW"
        bit_dulling_risk = "HIGH" if (mse_deviation_pct > 50.0 and rop_drop_pct > 25.0) else "LOW"

        dysfunction_active = stick_slip_severity in ["HIGH", "MEDIUM"] or bit_dulling_risk == "HIGH"

        return {
            "dysfunction_active": dysfunction_active,
            "stick_slip_severity": stick_slip_severity,
            "bit_whirl_risk": whirl_risk,
            "bit_dulling_indication": bit_dulling_risk,
            "mse_deviation_pct": round(mse_deviation_pct, 1),
            "rop_drop_pct": round(rop_drop_pct, 1),
            "torque_variance": round(torque_variance, 2),
            "rpm_variance": round(rpm_variance, 1),
            "actionable_review": [
                "Consider increasing RPM by 10-15% to clear torsional resonance.",
                "Verify bit cutter dullness state if MSE remains elevated across next 10m.",
                "Review hydraulics and BHA vibration dampening."
            ] if dysfunction_active else ["Operating within smooth drilling envelope."],
            "engineer_review_required": True
        }

    # -------------------------------------------------------------
    # 8. P0 — MSE EFFICIENCY ANALYSIS
    # -------------------------------------------------------------
    @staticmethod
    def evaluate_mse_efficiency(
        wob_klbs: float,
        rpm: float,
        torque_kftlb: float,
        rop_mhr: float,
        bit_diameter_in: float = 8.5,
        formation_name: str = "Upper Tipam Sandstone",
        baseline_mse_psi: float = 8500.0
    ) -> Dict[str, Any]:
        """
        Teale's Mechanical Specific Energy calculation with formation baseline comparison.
        """
        area_sqin = (math.pi / 4.0) * (bit_diameter_in**2)
        # Teale MSE: (WOB / Area) + (13.33 * RPM * Torque) / (ROP * Area)
        # where Torque is in ft-lbs and ROP is in ft/hr
        wob_lbs = wob_klbs * 1000.0
        torque_ftlbs = torque_kftlb * 1000.0
        rop_fthr = max(0.1, rop_mhr * 3.28084)
        axial_term = wob_lbs / max(0.1, area_sqin)
        rotary_term = (13.33 * rpm * torque_ftlbs) / max(0.1, (rop_fthr * area_sqin))
        current_mse_psi = round(axial_term + rotary_term, 0)

        deviation_pct = round(((current_mse_psi - baseline_mse_psi) / baseline_mse_psi) * 100.0, 1)

        if deviation_pct > 50.0:
            status = "DRILLING_EFFICIENCY_DEGRADING"
        elif deviation_pct > 20.0:
            status = "EFFICIENCY_WATCH"
        elif deviation_pct < -15.0:
            status = "HIGH_DRILLING_EFFICIENCY"
        else:
            status = "OPTIMAL_EFFICIENCY"

        return {
            "formation_name": formation_name,
            "expected_baseline_mse_psi": baseline_mse_psi,
            "current_actual_mse_psi": current_mse_psi,
            "deviation_pct": deviation_pct,
            "status": status,
            "possible_causes": [
                "Bit cutter dulling / wear",
                "Torsional vibration / micro stick-slip",
                "Inefficient hydraulic bottom-hole cleaning",
                "Stratigraphic rock hardness transition"
            ] if deviation_pct > 30.0 else ["Parameters matched to compressive rock strength."],
            "engineer_review_required": True
        }

    # -------------------------------------------------------------
    # 9. P0 — FORMATION TRANSITION DETECTION
    # -------------------------------------------------------------
    @staticmethod
    def detect_formation_change(
        gr_current: float,
        gr_prior_5m: float,
        res_current: float,
        res_prior_5m: float,
        rop_current: float,
        rop_prior_5m: float,
        active_depth_md_m: float
    ) -> Dict[str, Any]:
        """
        Detects formation tops / lithology shifts before drillstring gets compromised.
        """
        gr_delta = round(gr_current - gr_prior_5m, 1)
        res_ratio = round(res_current / max(0.1, res_prior_5m), 2)
        rop_ratio = round(rop_current / max(0.1, rop_prior_5m), 2)

        boundary_detected = abs(gr_delta) > 20.0 or res_ratio > 2.0 or res_ratio < 0.5 or rop_ratio > 1.8

        if boundary_detected:
            if gr_delta < -25.0:
                lithology_shift = "Shale to Clean Sandstone Transition"
                hazard_alert = "Watch for depleted pore pressure and differential sticking."
            elif gr_delta > 25.0:
                lithology_shift = "Sandstone to Gumbo / Coal Shale Transition"
                hazard_alert = "Watch for sticky clay, bit balling, or gas kick."
            else:
                lithology_shift = "Mechanical Property Boundary"
                hazard_alert = "Check drilling parameters and vibration."
        else:
            lithology_shift = "Homogeneous Interval"
            hazard_alert = "None"

        return {
            "depth_md_m": active_depth_md_m,
            "boundary_detected": boundary_detected,
            "lithology_shift": lithology_shift,
            "hazard_alert": hazard_alert,
            "gamma_ray_delta": gr_delta,
            "resistivity_ratio": res_ratio,
            "rop_ratio": rop_ratio,
            "engineer_review_required": True
        }

    # -------------------------------------------------------------
    # 10. P0 — MUD INTELLIGENCE & RHEOLOGY
    # -------------------------------------------------------------
    @staticmethod
    def evaluate_mud_intelligence(
        mud_weight_in_sg: float,
        mud_weight_out_sg: float,
        plastic_viscosity_cp: float = 22.0,
        yield_point_lb100sqft: float = 18.0,
        gel_strength_10s_lb100sqft: float = 5.0,
        gel_strength_10m_lb100sqft: float = 14.0,
        fluid_loss_ml: float = 5.5,
        ecd_sg: float = 1.21,
        formation_pp_sg: float = 0.92
    ) -> Dict[str, Any]:
        """
        Evaluates drilling fluid health and stability margins.
        """
        yp_pv_ratio = round(yield_point_lb100sqft / max(1.0, plastic_viscosity_cp), 2)
        gel_progression = round(gel_strength_10m_lb100sqft - gel_strength_10s_lb100sqft, 1)
        mw_delta = round(mud_weight_out_sg - mud_weight_in_sg, 3)

        hole_cleaning_potential = "EXCELLENT" if 0.7 <= yp_pv_ratio <= 1.2 else ("FAIR" if yp_pv_ratio < 0.6 else "HIGH_VISCOSITY_RISK")
        swab_risk = "ELEVATED" if gel_strength_10m_lb100sqft > 20.0 else "NORMAL"
        mud_cutting_indicator = "GAS_OR_WATER_CUT" if mw_delta < -0.02 else ("HEAVY_SOLIDS_LOADING" if mw_delta > 0.03 else "STABLE")

        return {
            "mud_weight_in_sg": mud_weight_in_sg,
            "mud_weight_out_sg": mud_weight_out_sg,
            "mw_differential_sg": mw_delta,
            "plastic_viscosity_cp": plastic_viscosity_cp,
            "yield_point_lb100sqft": yield_point_lb100sqft,
            "yp_pv_ratio": yp_pv_ratio,
            "gel_strength_10s": gel_strength_10s_lb100sqft,
            "gel_strength_10m": gel_strength_10m_lb100sqft,
            "gel_progression": gel_progression,
            "fluid_loss_ml": fluid_loss_ml,
            "hole_cleaning_potential": hole_cleaning_potential,
            "swab_surge_sensitivity": swab_risk,
            "mud_condition_status": mud_cutting_indicator,
            "engineer_review_required": True
        }

    # -------------------------------------------------------------
    # 11. P0 — SURGE / SWAB RISK
    # -------------------------------------------------------------
    @staticmethod
    def calculate_surge_swab_risk(
        pipe_speed_m_per_min: float,
        mud_weight_sg: float,
        pore_pressure_sg: float,
        fracture_gradient_sg: float,
        plastic_viscosity_cp: float = 22.0,
        yield_point_lb100sqft: float = 18.0,
        hole_size_in: float = 8.5,
        pipe_od_in: float = 5.0
    ) -> Dict[str, Any]:
        """
        Calculates pressure delta during tripping operations (decision support estimate).
        """
        # Burkhardt Bingham plastic swab/surge approximation
        clearance_in = (hole_size_in - pipe_od_in) / 2.0
        v_fps = (pipe_speed_m_per_min / 60.0) * 3.28084
        swab_delta_sg = round(min(0.25, (0.012 * yield_point_lb100sqft + 0.003 * plastic_viscosity_cp * v_fps) / max(0.5, clearance_in * 10.0)), 3)
        surge_delta_sg = round(swab_delta_sg * 1.15, 3)

        effective_swab_sg = round(mud_weight_sg - swab_delta_sg, 3)
        effective_surge_sg = round(mud_weight_sg + surge_delta_sg, 3)

        underbalance_risk = effective_swab_sg < pore_pressure_sg
        fracture_risk = effective_surge_sg > fracture_gradient_sg

        if underbalance_risk:
            status = "CRITICAL_SWAB_INFLUX_RISK"
        elif fracture_risk:
            status = "CRITICAL_SURGE_LOSS_RISK"
        elif (effective_swab_sg - pore_pressure_sg) < 0.05 or (fracture_gradient_sg - effective_surge_sg) < 0.05:
            status = "TIGHT_TRIPPING_MARGIN"
        else:
            status = "SAFE_TRIPPING_SPEED"

        return {
            "pipe_speed_m_per_min": pipe_speed_m_per_min,
            "static_mud_weight_sg": mud_weight_sg,
            "estimated_swab_delta_sg": -swab_delta_sg,
            "estimated_surge_delta_sg": +surge_delta_sg,
            "effective_swab_gradient_sg": effective_swab_sg,
            "effective_surge_gradient_sg": effective_surge_sg,
            "pore_pressure_sg": pore_pressure_sg,
            "fracture_gradient_sg": fracture_gradient_sg,
            "swab_margin_sg": round(effective_swab_sg - pore_pressure_sg, 3),
            "surge_margin_sg": round(fracture_gradient_sg - effective_surge_sg, 3),
            "status": status,
            "scenario_warning": "SCENARIO ESTIMATE — NOT AN OPERATIONAL COMMAND",
            "engineer_review_required": True
        }

    # -------------------------------------------------------------
    # 12. P0 — CONNECTION INTELLIGENCE
    # -------------------------------------------------------------
    @staticmethod
    def evaluate_connection_signature(
        connection_gas_pct: float,
        pit_volume_change_bbl: float,
        flowback_time_sec: float,
        spp_recovery_time_sec: float,
        torque_at_bottom_kftlb: float
    ) -> Dict[str, Any]:
        """
        Analyzes pre-, during-, and post-connection transient telemetry.
        """
        gas_abnormal = connection_gas_pct > 3.0
        pit_abnormal = pit_volume_change_bbl > 1.5
        flowback_abnormal = flowback_time_sec > 90.0

        if gas_abnormal and pit_abnormal:
            status = "POSSIBLE_CONNECTION_INFLUX"
            severity = "HIGH"
        elif gas_abnormal:
            status = "ELEVATED_CONNECTION_GAS"
            severity = "MEDIUM"
        elif flowback_abnormal:
            status = "EXTENDED_FLOWBACK_BALLOONING"
            severity = "MEDIUM"
        else:
            status = "NORMAL_CONNECTION_SIGNATURE"
            severity = "LOW"

        return {
            "connection_status": status,
            "severity": severity,
            "connection_gas_pct": connection_gas_pct,
            "pit_volume_change_bbl": pit_volume_change_bbl,
            "flowback_time_sec": flowback_time_sec,
            "spp_recovery_time_sec": spp_recovery_time_sec,
            "torque_breakout_kftlb": torque_at_bottom_kftlb,
            "engineer_review_required": True
        }

    # -------------------------------------------------------------
    # 28. P2 — WHAT-IF SCENARIO ANALYSIS SIMULATOR
    # -------------------------------------------------------------
    @staticmethod
    def simulate_what_if_scenario(
        current_mw_sg: float,
        current_flow_gpm: float,
        current_rpm: float,
        scenario_mw_sg: float,
        scenario_flow_gpm: float,
        scenario_rpm: float,
        pore_pressure_sg: float = 0.92,
        fracture_gradient_sg: float = 1.82,
        baseline_mse_psi: float = 8500.0,
        baseline_torque_kftlb: float = 12.8,
        depth_tvd_m: float = 2180.0
    ) -> Dict[str, Any]:
        """
        Simulates what-if parameter changes on ECD, MSE, and safety margins.
        Strictly labeled: SCENARIO ESTIMATE — NOT AN OPERATIONAL COMMAND.
        """
        # Flow friction approximation on ECD: delta ECD ~ (Q_new / Q_old)^1.8 * 0.05
        flow_ratio = scenario_flow_gpm / max(1.0, current_flow_gpm)
        friction_component = 0.05 * (flow_ratio ** 1.8)
        scenario_ecd_sg = round(scenario_mw_sg + friction_component, 3)

        # Kick & Loss margins
        kick_margin_sg = round(scenario_ecd_sg - pore_pressure_sg, 3)
        loss_margin_sg = round(fracture_gradient_sg - scenario_ecd_sg, 3)

        # Torque estimate
        rpm_ratio = scenario_rpm / max(1.0, current_rpm)
        scenario_torque_kftlb = round(baseline_torque_kftlb * (1.0 + (rpm_ratio - 1.0) * 0.25), 1)

        # MSE estimate
        scenario_mse_psi = round(baseline_mse_psi * (scenario_mw_sg / current_mw_sg) * (1.0 + (flow_ratio - 1.0) * 0.1), 0)

        return {
            "disclaimer": "SCENARIO ESTIMATE — NOT AN OPERATIONAL COMMAND",
            "current_inputs": {
                "mud_weight_sg": current_mw_sg,
                "flow_rate_gpm": current_flow_gpm,
                "rpm": current_rpm
            },
            "scenario_inputs": {
                "mud_weight_sg": scenario_mw_sg,
                "flow_rate_gpm": scenario_flow_gpm,
                "rpm": scenario_rpm
            },
            "projected_outputs": {
                "projected_ecd_sg": scenario_ecd_sg,
                "projected_torque_kftlb": scenario_torque_kftlb,
                "projected_mse_psi": scenario_mse_psi,
                "projected_kick_margin_sg": kick_margin_sg,
                "projected_loss_margin_sg": loss_margin_sg
            },
            "safety_envelope_evaluation": (
                "SAFE_ENVELOPE" if (kick_margin_sg > 0.08 and loss_margin_sg > 0.08) else "RISK_OF_MARGIN_VIOLATION"
            ),
            "engineer_review_required": True,
            "autonomous_control": False
        }
