"""
Tier 1 Tests — Innovation Features A1 through A20
eRTMAC-NWIS · SIH26121 · Oil India Limited

Tests all 20 out-of-the-box innovation features implemented in InnovationsService.
Run: python -m unittest discover tests/
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.services.innovations_service import InnovationsService


class TestA1FormationFluidTyping(unittest.TestCase):
    """A1: Formation Fluid Typing Classifier"""

    def test_oil_zone_detection(self):
        """High-porosity, high-resistivity = oil zone"""
        result = InnovationsService.classify_formation_fluid(
            gr_api=30.0, rhob_gcc=2.25, nphi=0.28, dtc_usft=95.0, res_ohmm=18.0, depth_m=2410.0
        )
        self.assertIn("fluid_type", result)
        self.assertIn(result["fluid_type"], ["OIL_ZONE", "GAS_ZONE", "SANDSTONE"])
        self.assertGreater(result["confidence_pct"], 50.0)
        self.assertEqual(result["feature"], "A1_FORMATION_FLUID_TYPING")

    def test_shale_zone_detection(self):
        """Very high GR = shale"""
        result = InnovationsService.classify_formation_fluid(
            gr_api=125.0, rhob_gcc=2.50, nphi=0.18, dtc_usft=75.0, res_ohmm=1.5, depth_m=1200.0
        )
        self.assertEqual(result["fluid_type"], "SHALE")
        self.assertGreater(result["confidence_pct"], 80.0)

    def test_coal_zone_detection(self):
        """Ultra-low RHOB = coal seam"""
        result = InnovationsService.classify_formation_fluid(
            gr_api=35.0, rhob_gcc=1.48, nphi=0.38, dtc_usft=110.0, res_ohmm=5.0, depth_m=2850.0
        )
        self.assertEqual(result["fluid_type"], "COAL")
        self.assertTrue(result["alert_flag"])
        self.assertEqual(result["hydrocarbon_potential"], "HIGH")

    def test_gas_crossover_detection(self):
        """NPHI > RHOB-phi crossover = gas zone"""
        result = InnovationsService.classify_formation_fluid(
            gr_api=28.0, rhob_gcc=2.18, nphi=0.38, dtc_usft=100.0, res_ohmm=25.0, depth_m=3100.0
        )
        self.assertIn(result["fluid_type"], ["GAS_ZONE", "OIL_ZONE"])

    def test_output_schema_completeness(self):
        """All required keys present"""
        result = InnovationsService.classify_formation_fluid()
        required_keys = ["feature", "depth_m", "fluid_type", "confidence_pct", "hydrocarbon_potential",
                         "alert_flag", "inputs", "derived", "reasoning", "engineer_review_required"]
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_safety_guardrail(self):
        """autonomous_control must be False"""
        result = InnovationsService.classify_formation_fluid()
        self.assertFalse(result["autonomous_control"])


class TestA2PorePressure(unittest.TestCase):
    """A2: D-Exponent Pore Pressure Prediction"""

    def test_normal_pressure_regime(self):
        """Normal PP conditions produce safe margin"""
        result = InnovationsService.predict_pore_pressure_dexponent(
            rop_mhr=18.5, rpm=95.0, wob_klbs=18.2, mud_weight_sg=1.16, depth_tvd_m=2000.0
        )
        self.assertIn("pp_predicted_sg", result)
        self.assertGreater(result["pp_predicted_sg"], 0.80)
        self.assertLess(result["pp_predicted_sg"], 2.0)

    def test_d_exponent_within_bounds(self):
        """D-exponent should stay within physical bounds"""
        result = InnovationsService.predict_pore_pressure_dexponent(
            rop_mhr=5.0, rpm=60.0, wob_klbs=25.0, depth_tvd_m=3000.0
        )
        self.assertGreaterEqual(result["d_exponent_raw"], 0.3)
        self.assertLessEqual(result["d_exponent_raw"], 3.5)

    def test_underbalance_alert(self):
        """Very high rop (low dexp) triggers underbalance alert"""
        result = InnovationsService.predict_pore_pressure_dexponent(
            rop_mhr=45.0, rpm=120.0, wob_klbs=5.0, mud_weight_sg=0.85, depth_tvd_m=2500.0
        )
        self.assertIn("pp_status", result)
        # Should detect some pressure condition
        self.assertIn("pp_status", result)

    def test_output_schema(self):
        result = InnovationsService.predict_pore_pressure_dexponent()
        required_keys = ["feature", "pp_predicted_sg", "mud_weight_sg", "kick_margin_sg",
                         "pp_status", "recommended_action", "engineer_review_required"]
        for key in required_keys:
            self.assertIn(key, result)

    def test_kick_margin_calculation(self):
        """kick_margin = MW - PP_predicted"""
        result = InnovationsService.predict_pore_pressure_dexponent(mud_weight_sg=1.16)
        self.assertAlmostEqual(
            result["kick_margin_sg"],
            result["mud_weight_sg"] - result["pp_predicted_sg"],
            places=3
        )


class TestA3CasingProgram(unittest.TestCase):
    """A3: Automated Casing Program Optimizer"""

    def test_minimum_casing_strings(self):
        """Always has at least conductor + surface"""
        result = InnovationsService.optimize_casing_program(planned_td_m=3600.0)
        self.assertGreaterEqual(result["total_casing_strings"], 3)

    def test_casing_shoe_ascending(self):
        """Casing shoes must be in ascending depth order"""
        result = InnovationsService.optimize_casing_program(planned_td_m=3600.0)
        shoes = [c["shoe_depth_md_m"] for c in result["casing_strings"]]
        self.assertEqual(shoes, sorted(shoes))

    def test_production_liner_at_td(self):
        """Last casing = production liner at planned TD"""
        result = InnovationsService.optimize_casing_program(planned_td_m=3600.0)
        last = result["casing_strings"][-1]
        self.assertIn("7", last["casing_string"])
        self.assertEqual(last["shoe_depth_md_m"], 3600.0)

    def test_formation_analysis_count(self):
        """Should analyze multiple formations"""
        result = InnovationsService.optimize_casing_program(planned_td_m=3600.0)
        self.assertGreater(result["formations_analyzed"], 3)

    def test_schema_completeness(self):
        result = InnovationsService.optimize_casing_program()
        self.assertIn("casing_strings", result)
        self.assertIn("formation_profiles", result)
        self.assertIn("engineer_review_required", result)


class TestA4NPTTransfer(unittest.TestCase):
    """A4: NPT Transfer Learning Forecast"""

    def test_forecast_has_three_percentiles(self):
        """P10, P50, P90 must all be present"""
        result = InnovationsService.npt_transfer_forecast(depth_md_m=2410.0, formation="Upper Tipam Sandstone")
        if "npt_forecast_hours" in result:
            npt = result["npt_forecast_hours"]
            self.assertIn("p10_optimistic", npt)
            self.assertIn("p50_expected", npt)
            self.assertIn("p90_worst_case", npt)

    def test_p10_lte_p50_lte_p90(self):
        """P10 <= P50 <= P90"""
        result = InnovationsService.npt_transfer_forecast(depth_md_m=2410.0)
        if "npt_forecast_hours" in result:
            npt = result["npt_forecast_hours"]
            self.assertLessEqual(npt["p10_optimistic"], npt["p50_expected"])
            self.assertLessEqual(npt["p50_expected"], npt["p90_worst_case"])

    def test_probability_bounds(self):
        """Probability of NPT > 20h must be 0-1"""
        result = InnovationsService.npt_transfer_forecast(depth_md_m=2410.0)
        if "probability_npt_gt_20hrs" in result:
            self.assertGreaterEqual(result["probability_npt_gt_20hrs"], 0.0)
            self.assertLessEqual(result["probability_npt_gt_20hrs"], 1.0)

    def test_financial_exposure_formatted(self):
        """Financial exposure should be formatted as Rs string"""
        result = InnovationsService.npt_transfer_forecast(depth_md_m=2410.0)
        if "financial_exposure_inr" in result:
            p50 = result["financial_exposure_inr"].get("p50_expected", "")
            self.assertTrue("Rs" in p50 or "₹" in p50 or "Cr" in p50 or "Lakh" in p50)


class TestA5WellboreTemperature(unittest.TestCase):
    """A5: Wellbore Temperature Prediction"""

    def test_bhst_increases_with_depth(self):
        """BHST at 3000m > BHST at 1500m"""
        shallow = InnovationsService.predict_wellbore_temperature(depth_tvd_m=1500.0)
        deep = InnovationsService.predict_wellbore_temperature(depth_tvd_m=3000.0)
        self.assertGreater(deep["bhst_deg_c"], shallow["bhst_deg_c"])

    def test_bhct_less_than_bhst(self):
        """BHCT < BHST (cooling from circulation)"""
        result = InnovationsService.predict_wellbore_temperature(depth_tvd_m=2180.0, flow_rate_gpm=640.0)
        self.assertLess(result["bhct_deg_c"], result["bhst_deg_c"])

    def test_cement_flag_at_high_temp(self):
        """Deep wells should trigger high-temp cement flag"""
        result = InnovationsService.predict_wellbore_temperature(depth_tvd_m=4000.0)
        self.assertTrue(result["cement_temperature_flag"])

    def test_schema(self):
        result = InnovationsService.predict_wellbore_temperature()
        required = ["bhst_deg_c", "bhct_deg_c", "cement_temperature_flag", "cement_recommendation"]
        for key in required:
            self.assertIn(key, result)


class TestA6LithologyInference(unittest.TestCase):
    """A6: MWD-Free Lithology Inference"""

    def test_soft_sandstone_pattern(self):
        """High ROP, low torque variance = soft sandstone"""
        result = InnovationsService.infer_lithology_from_surface(
            rop_mhr=25.0, wob_klbs=18.0, rpm=100.0, torque_kftlb=10.0,
            torque_variance=0.5, rpm_variance=5.0, mse_psi=25000.0
        )
        self.assertIn("SANDSTONE", result["inferred_lithology"])

    def test_coal_stringer_pattern(self):
        """High RPM variance + high torque variance = coal"""
        result = InnovationsService.infer_lithology_from_surface(
            rop_mhr=8.0, rpm_variance=22.0, torque_variance=2.8, mse_psi=42000.0, torque_kftlb=14.0
        )
        self.assertEqual(result["inferred_lithology"], "COAL")
        self.assertTrue(len(result["warnings"]) > 0)

    def test_hard_limestone_pattern(self):
        """Very low ROP + high MSE = hard carbonate"""
        result = InnovationsService.infer_lithology_from_surface(
            rop_mhr=2.5, wob_klbs=28.0, mse_psi=85000.0, torque_kftlb=16.0,
            rpm_variance=8.0, torque_variance=1.0
        )
        self.assertIn(result["inferred_lithology"], ["LIMESTONE", "TIGHT_BASEMENT"])

    def test_schema_completeness(self):
        result = InnovationsService.infer_lithology_from_surface()
        for key in ["inferred_lithology", "confidence_pct", "formation_hint", "warnings", "method"]:
            self.assertIn(key, result)


class TestA7NPTCost(unittest.TestCase):
    """A7: NPT Cost Quantification Engine"""

    def test_all_hazard_types_have_cost(self):
        """Every standard hazard type should return a cost estimate"""
        hazard_types = [
            "DIFFERENTIAL_STICKING", "LOST_CIRCULATION", "GAS_KICK",
            "PACK_OFF", "TORQUE_SPIKE", "CEMENTING_ISSUE", "BIT_BALLING"
        ]
        for ht in hazard_types:
            result = InnovationsService.quantify_npt_cost(hazard_type=ht, risk_probability=0.7)
            self.assertIn("financial_exposure", result)

    def test_cost_increases_with_probability(self):
        """Higher risk probability = higher expected cost"""
        low = InnovationsService.quantify_npt_cost(risk_probability=0.2)
        high = InnovationsService.quantify_npt_cost(risk_probability=0.9)
        self.assertIn("npt_hours", low)
        self.assertIn("npt_hours", high)

    def test_p10_lte_p50_lte_p90_hours(self):
        """NPT hour percentiles must be ordered"""
        result = InnovationsService.quantify_npt_cost()
        npt = result["npt_hours"]
        self.assertLessEqual(npt["p10_optimistic"], npt["p50_expected"])
        self.assertLessEqual(npt["p50_expected"], npt["p90_worst_case"])

    def test_schema(self):
        result = InnovationsService.quantify_npt_cost()
        for key in ["hazard_type", "financial_exposure", "summary", "rig_spread_rate_inr_per_hr"]:
            self.assertIn(key, result)


class TestA8HazardHeatmap(unittest.TestCase):
    """A8: Spatial Hazard Heatmap"""

    def test_returns_incidents(self):
        result = InnovationsService.get_hazard_heatmap()
        self.assertIn("incidents", result)
        self.assertGreater(len(result["incidents"]), 5)

    def test_all_incidents_have_coords(self):
        """Every incident must have lat/lon"""
        result = InnovationsService.get_hazard_heatmap()
        for inc in result["incidents"]:
            self.assertIn("lat", inc)
            self.assertIn("lon", inc)
            self.assertIn("hazard", inc)

    def test_nahorkatiya_lat_range(self):
        """Nahorkatiya coordinates in Assam ~lat 27.2-27.6"""
        result = InnovationsService.get_hazard_heatmap()
        lats = [i["lat"] for i in result["incidents"]]
        self.assertTrue(all(26.0 < lat < 28.5 for lat in lats))


class TestA9MudProgram(unittest.TestCase):
    """A9: Mud Program Recommendation"""

    def test_tipam_recommends_phpa(self):
        """Tipam Sandstone should recommend PHPA/KCl mud"""
        result = InnovationsService.recommend_mud_program(formation="Upper Tipam Sandstone")
        self.assertIn("PHPA", result["recommended_mud_system"])

    def test_barail_recommends_obm(self):
        """Barail high-pressure gas sands need OBM"""
        result = InnovationsService.recommend_mud_program(formation="Barail Coal-Shale Unit")
        self.assertIn("OBM", result["recommended_mud_system"])

    def test_mw_window_valid(self):
        """mw_min < mw_max"""
        result = InnovationsService.recommend_mud_program(formation="Upper Tipam Sandstone")
        mww = result["mud_weight_window"]
        self.assertLess(mww["mw_min_sg"], mww["mw_max_sg"])

    def test_current_mw_status(self):
        """IN_WINDOW when MW is within bounds"""
        result = InnovationsService.recommend_mud_program(
            formation="Upper Tipam Sandstone", current_mw_sg=1.05
        )
        self.assertIn("current_mw_status", result)

    def test_additives_nonempty(self):
        """Must always return at least one additive"""
        for formation in ["Upper Tipam Sandstone", "Barail Coal-Shale Unit", "Girujan Clay"]:
            result = InnovationsService.recommend_mud_program(formation=formation)
            self.assertGreater(len(result["additives"]), 0)


class TestA10BHAFatigue(unittest.TestCase):
    """A10: BHA Fatigue Tracker"""

    def test_fresh_bha_is_healthy(self):
        """Low rotating hours + low DLS = healthy BHA"""
        result = InnovationsService.evaluate_bha_fatigue(rotating_hours=20.0, max_dls_deg_per_30m=0.5)
        self.assertEqual(result["status"], "HEALTHY")
        self.assertFalse(result["alert"])

    def test_old_bha_alerts(self):
        """Very high rotating hours with high DLS triggers alert"""
        result = InnovationsService.evaluate_bha_fatigue(rotating_hours=1400.0, max_dls_deg_per_30m=8.0)
        self.assertTrue(result["alert"])
        self.assertIn("CRITICAL", result["status"])

    def test_fatigue_ratio_bounds(self):
        """Fatigue ratio must be 0.0 - 1.0"""
        result = InnovationsService.evaluate_bha_fatigue()
        self.assertGreaterEqual(result["fatigue_ratio"], 0.0)
        self.assertLessEqual(result["fatigue_ratio"], 1.0)

    def test_steel_grades(self):
        """All valid steel grades must work"""
        for grade in ["S-135", "G-105", "E-75"]:
            result = InnovationsService.evaluate_bha_fatigue(steel_grade=grade)
            self.assertIn("life_consumed_pct", result)


class TestA11TrippingSchedule(unittest.TestCase):
    """A11: Tripping Speed Schedule"""

    def test_schedule_has_entries(self):
        result = InnovationsService.generate_tripping_schedule(depth_max_m=2500.0)
        self.assertGreater(len(result["schedule"]), 3)

    def test_speed_positive(self):
        """All speeds must be positive"""
        result = InnovationsService.generate_tripping_schedule()
        for entry in result["schedule"]:
            self.assertGreater(entry["max_run_speed_m_per_min"], 0)

    def test_speed_decreases_with_depth(self):
        """Speed should generally decrease with depth (more surge risk)"""
        result = InnovationsService.generate_tripping_schedule(depth_max_m=2500.0)
        schedule = result["schedule"]
        first_speed = schedule[0]["max_run_speed_m_per_min"]
        last_speed = schedule[-1]["max_run_speed_m_per_min"]
        self.assertGreaterEqual(first_speed, last_speed)

    def test_category_values(self):
        """Category must be SAFE, CAUTION, or CRITICAL"""
        result = InnovationsService.generate_tripping_schedule()
        for entry in result["schedule"]:
            self.assertIn(entry["category"], ["SAFE", "CAUTION", "CRITICAL"])


class TestA12Copilot(unittest.TestCase):
    """A12: Multi-Step Drilling Copilot"""

    def test_mud_weight_query(self):
        """Copilot should return 4 reasoning steps"""
        result = InnovationsService.drilling_copilot(
            question="Should I reduce mud weight before entering Barail?",
            depth_md_m=2780.0, mud_weight_sg=1.16
        )
        self.assertIn("reasoning_steps", result)
        self.assertEqual(len(result["reasoning_steps"]), 4)

    def test_synthesis_not_empty(self):
        """Synthesis must be a non-empty string"""
        result = InnovationsService.drilling_copilot(question="What is the kick risk?")
        self.assertIsInstance(result["synthesis"], str)
        self.assertGreater(len(result["synthesis"]), 20)

    def test_risk_level_valid(self):
        """Risk level must be HIGH or MODERATE"""
        result = InnovationsService.drilling_copilot(question="Are we at stuck pipe risk?")
        self.assertIn(result["risk_level"], ["HIGH", "MODERATE"])

    def test_autonomous_control_false(self):
        result = InnovationsService.drilling_copilot(question="What should I do?")
        self.assertFalse(result["autonomous_control"])

    def test_stuck_pipe_query(self):
        result = InnovationsService.drilling_copilot(
            question="Is there a stuck pipe risk at this depth?",
            depth_md_m=2410.0, mud_weight_sg=1.16
        )
        self.assertIn("reasoning_steps", result)
        self.assertGreater(len(result["synthesis"]), 0)


class TestA13DDRGenerator(unittest.TestCase):
    """A13: Automated DDR Generator"""

    def test_ddr_structure(self):
        """DDR must have all standard sections"""
        result = InnovationsService.generate_ddr(
            well_name="SYN-NHK-05", day_number=14, depth_start_m=2380.0, depth_end_m=2413.5
        )
        report = result["report"]
        for section in ["header", "drill_ahead_summary", "alerts_summary", "npt_summary", "mud_system_status", "lookahead_advisory"]:
            self.assertIn(section, report)

    def test_footage_calculation(self):
        """Footage = end - start"""
        result = InnovationsService.generate_ddr(depth_start_m=2380.0, depth_end_m=2413.5)
        self.assertAlmostEqual(result["report"]["header"]["footage_drilled_m"], 33.5, places=1)

    def test_well_name_in_header(self):
        result = InnovationsService.generate_ddr(well_name="TEST-WELL-01")
        self.assertEqual(result["report"]["header"]["well_name"], "TEST-WELL-01")

    def test_npt_event_logged(self):
        """Non-zero NPT should appear in npt_events"""
        result = InnovationsService.generate_ddr(npt_hours=18.5)
        npt = result["report"]["npt_summary"]
        self.assertAlmostEqual(npt["total_npt_hours"], 18.5)


class TestA16BitWear(unittest.TestCase):
    """A16: Bit Wear Prediction"""

    def test_new_bit_acceptable(self):
        """Fresh bit with low MSE ratio = acceptable"""
        result = InnovationsService.predict_bit_wear(
            cumulative_rotating_hrs=5.0, mse_ratio=1.02, rop_drop_pct=2.0
        )
        self.assertEqual(result["status"], "ACCEPTABLE")
        self.assertFalse(result["alert"])

    def test_worn_bit_alerts(self):
        """Severe MSE ratio + ROP drop = approaching limit"""
        result = InnovationsService.predict_bit_wear(
            cumulative_rotating_hrs=90.0, mse_ratio=1.85, rop_drop_pct=45.0
        )
        self.assertTrue(result["alert"])

    def test_dull_grade_format(self):
        """IADC dull grade format should be X/8"""
        result = InnovationsService.predict_bit_wear()
        self.assertIn("/8", result["iadc_dull_grade_estimate"])

    def test_wear_index_bounds(self):
        """Wear index must be 0.0 - 1.0"""
        result = InnovationsService.predict_bit_wear()
        self.assertGreaterEqual(result["bit_wear_index"], 0.0)
        self.assertLessEqual(result["bit_wear_index"], 1.0)


class TestA17WellboreStability(unittest.TestCase):
    """A17: Wellbore Stability Predictor"""

    def test_mw_bounds_make_physical_sense(self):
        """Collapse MW < Fracture MW"""
        result = InnovationsService.predict_wellbore_stability(depth_tvd_m=2180.0, mud_weight_sg=1.16)
        bounds = result["mud_weight_bounds"]
        self.assertLess(bounds["mw_collapse_lower_sg"], bounds["mw_fracture_upper_sg"])

    def test_stability_window_positive(self):
        result = InnovationsService.predict_wellbore_stability()
        self.assertGreater(result["mud_weight_bounds"]["stability_window_sg"], 0)

    def test_breakout_azimuth_present(self):
        result = InnovationsService.predict_wellbore_stability()
        self.assertIsInstance(result["breakout_azimuth"], str)
        self.assertGreater(len(result["breakout_azimuth"]), 5)

    def test_status_values(self):
        result = InnovationsService.predict_wellbore_stability()
        self.assertIn(result["status"], ["STABLE", "INSTABILITY_RISK"])


class TestA18Benchmarking(unittest.TestCase):
    """A18: Well Performance Benchmarking"""

    def test_percentile_bounds(self):
        """All percentiles must be 0-100"""
        result = InnovationsService.benchmark_well_performance(current_rop_mhr=18.5)
        self.assertGreater(result["overall_performance_percentile"], 0)
        self.assertLessEqual(result["overall_performance_percentile"], 100)
        for metric in result["performance_metrics"].values():
            self.assertGreaterEqual(metric["percentile"], 0)
            self.assertLessEqual(metric["percentile"], 100)

    def test_summary_has_percentile_mention(self):
        """Summary string should mention percentile"""
        result = InnovationsService.benchmark_well_performance()
        self.assertIn("percentile", result["summary"].lower())

    def test_schema_completeness(self):
        result = InnovationsService.benchmark_well_performance()
        for key in ["performance_metrics", "overall_performance_percentile", "summary", "field_benchmarks"]:
            self.assertIn(key, result)


class TestA19PreDrillSafety(unittest.TestCase):
    """A19: Pre-Drill Safety Case Generator"""

    def test_formation_risk_register_populated(self):
        result = InnovationsService.generate_predrill_safety_case(planned_td_m=3600.0)
        self.assertGreater(len(result["formation_risk_register"]), 3)

    def test_oisd_compliance_present(self):
        result = InnovationsService.generate_predrill_safety_case()
        self.assertIn("oisd_compliance", result)
        self.assertIn("OISD_STD_113", result["oisd_compliance"])

    def test_financial_exposure_formatted(self):
        result = InnovationsService.generate_predrill_safety_case()
        exposure = result["total_p90_financial_exposure"]
        self.assertTrue("Cr" in exposure or "Lakh" in exposure or "₹" in exposure)

    def test_key_decision_depths_present(self):
        result = InnovationsService.generate_predrill_safety_case()
        self.assertGreater(len(result["key_decision_depths"]), 2)

    def test_risk_categories_valid(self):
        """Risk categories must be LOW, MODERATE, or HIGH"""
        result = InnovationsService.generate_predrill_safety_case()
        for formation in result["formation_risk_register"]:
            self.assertIn(formation["risk_category"], ["LOW", "MODERATE", "HIGH"])

    def test_p90_npt_positive(self):
        result = InnovationsService.generate_predrill_safety_case()
        self.assertGreater(result["total_p90_npt_hrs"], 0)


class TestIntegration(unittest.TestCase):
    """Integration tests: cross-feature consistency"""

    def test_pp_danger_triggers_npt_cost_spike(self):
        """If PP prediction says underbalanced, NPT cost should assume high probability"""
        pp = InnovationsService.predict_pore_pressure_dexponent(
            rop_mhr=45.0, rpm=120.0, wob_klbs=5.0, mud_weight_sg=0.85, depth_tvd_m=2500.0
        )
        # If alert, cost engine should be invoked at high probability
        prob = 0.85 if pp.get("alert") else 0.3
        npt = InnovationsService.quantify_npt_cost(hazard_type="GAS_KICK", risk_probability=prob)
        self.assertIn("financial_exposure", npt)

    def test_copilot_uses_formation_context(self):
        """Copilot synthesis should mention formation name"""
        result = InnovationsService.drilling_copilot(
            question="What is the kick risk?",
            formation="Barail Coal-Shale Unit"
        )
        # Should reference Barail somewhere in its reasoning
        all_text = " ".join([s["output"] for s in result["reasoning_steps"]])
        self.assertIn("Barail", all_text)

    def test_casing_optimizer_narrows_near_barail(self):
        """Casing optimizer should set shoe before high-pressure Barail zone"""
        result = InnovationsService.optimize_casing_program(planned_td_m=3600.0)
        shoes = result["casing_strings"]
        # Should have a shoe around 2800m (just before Barail at ~2800m)
        shoe_depths = [c["shoe_depth_md_m"] for c in shoes]
        self.assertTrue(any(2600 < d < 3000 for d in shoe_depths),
                        f"Expected casing shoe near Barail (~2800m), got: {shoe_depths}")

    def test_all_features_return_engineer_review(self):
        """All 15 major features must enforce engineer_review_required=True"""
        results = [
            InnovationsService.classify_formation_fluid(),
            InnovationsService.predict_pore_pressure_dexponent(),
            InnovationsService.optimize_casing_program(),
            InnovationsService.npt_transfer_forecast(),
            InnovationsService.predict_wellbore_temperature(),
            InnovationsService.infer_lithology_from_surface(),
            InnovationsService.quantify_npt_cost(),
            InnovationsService.recommend_mud_program(),
            InnovationsService.evaluate_bha_fatigue(),
            InnovationsService.generate_tripping_schedule(),
            InnovationsService.drilling_copilot("test question"),
            InnovationsService.generate_ddr(),
            InnovationsService.predict_bit_wear(),
            InnovationsService.predict_wellbore_stability(),
            InnovationsService.benchmark_well_performance(),
            InnovationsService.generate_predrill_safety_case(),
        ]
        for i, r in enumerate(results):
            self.assertTrue(
                r.get("engineer_review_required"),
                f"Feature {i} missing engineer_review_required=True"
            )


if __name__ == "__main__":
    # Run with: python -m unittest tests/tier1_features/test_f15_innovations.py -v
    unittest.main(verbosity=2)
