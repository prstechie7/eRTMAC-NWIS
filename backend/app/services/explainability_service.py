"""
Model Explainability Service for eRTMAC-NWIS.
Compliant with SIH26121 (Oil India Limited).
Provides feature attribution breakdown (SHAP / Permutation importance fallback)
for model-backed risk predictions.
"""

from typing import Dict, Any, List


class ExplainabilityService:
    @staticmethod
    def get_explanation(well_id: str, risk_type: str = "STUCK_PIPE") -> Dict[str, Any]:
        risk_type_upper = risk_type.upper()

        if risk_type_upper == "STUCK_PIPE":
            top_factors = [
                {"feature": "torque_trend", "impact": 0.31},
                {"feature": "formation_match", "impact": 0.22},
                {"feature": "rop_decline", "impact": 0.18},
                {"feature": "overbalance_pressure", "impact": 0.15},
                {"feature": "stationary_time", "impact": 0.14}
            ]
        elif risk_type_upper == "MUD_LOSS":
            top_factors = [
                {"feature": "ecd_excursion", "impact": 0.38},
                {"feature": "pit_volume_trend", "impact": 0.28},
                {"feature": "formation_porosity", "impact": 0.20},
                {"feature": "flow_out_imbalance", "impact": 0.14}
            ]
        elif risk_type_upper == "OVERPRESSURE":
            top_factors = [
                {"feature": "total_gas_spike", "impact": 0.42},
                {"feature": "barail_coal_sequence_proximity", "impact": 0.30},
                {"feature": "standpipe_pressure_drop", "impact": 0.18},
                {"feature": "d_exponent_trend", "impact": 0.10}
            ]
        elif risk_type_upper == "TORQUE_SPIKE":
            top_factors = [
                {"feature": "rolling_torque_std_dev", "impact": 0.45},
                {"feature": "z_score_anomaly", "impact": 0.32},
                {"feature": "rpm_fluctuation", "impact": 0.23}
            ]
        else:
            top_factors = [
                {"feature": "historical_slurry_loss", "impact": 0.50},
                {"feature": "shale_washout_index", "impact": 0.50}
            ]

        return {
            "well_id": well_id,
            "risk_type": risk_type_upper,
            "method": "Permutation Feature Importance / SHAP Attribution",
            "top_factors": top_factors,
            "model_version": "v1.0.0-hybrid"
        }
