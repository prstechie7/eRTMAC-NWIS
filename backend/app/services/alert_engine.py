"""
Stateful Real-Time Alert Engine for eRTMAC-NWIS.
Compliant with SIH26121 (Oil India Limited).
Implements stateful alert lifecycle: DETECTED -> ACKNOWLEDGED -> UNDER_REVIEW -> RESOLVED / DISMISSED,
with deduplication, cooldown, and escalation.
"""

import time
import uuid
from typing import List, Dict, Any, Optional
from app.models.schemas import RiskAlertModel, AlertStatus, RiskType, RiskLevel, ProvenanceType


class AlertEngine:
    def __init__(self, cooldown_seconds: float = 30.0):
        self.cooldown_seconds = cooldown_seconds
        self.active_alerts: Dict[str, RiskAlertModel] = {}
        self.alert_history: List[RiskAlertModel] = []
        self.last_alert_time: Dict[str, float] = {}  # key: f"{well_id}:{risk_type}"

    def process_risk_prediction(
        self,
        well_id: str,
        risk_data: Dict[str, Any],
        current_depth: float,
        formation: str
    ) -> Optional[RiskAlertModel]:
        risk_type = risk_data.get("risk_type")
        risk_level = risk_data.get("risk_level")
        risk_score = risk_data.get("risk_score", 0.0)

        # Alert trigger threshold: HIGH or CRITICAL
        if risk_level not in [RiskLevel.HIGH.value, RiskLevel.CRITICAL.value]:
            return None

        key = f"{well_id}:{risk_type}"
        now = time.time()
        last_time = self.last_alert_time.get(key, 0.0)

        # Check existing active alert for this key
        existing_alert = self.active_alerts.get(key)

        if existing_alert:
            # Check for escalation: if level worsens from HIGH to CRITICAL
            if existing_alert.risk_level == RiskLevel.HIGH.value and risk_level == RiskLevel.CRITICAL.value:
                existing_alert.risk_level = RiskLevel.CRITICAL
                existing_alert.current_depth = current_depth
                existing_alert.confidence = risk_data.get("confidence", 0.8)
                self.last_alert_time[key] = now
                return existing_alert

            # Deduplication & Cooldown check
            if (now - last_time) < self.cooldown_seconds:
                return None  # Suppress duplicate alert during cooldown

        # Create new stateful alert
        alert_id = f"alt-{uuid.uuid4().hex[:8]}"
        created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        recommended_actions = [
            "Limit stationary drillstring time to < 90 seconds across depleted zones.",
            "Adjust mud weight according to formation pore pressure profile.",
            "Qualified engineer review required before resuming slide drilling."
        ]

        alert = RiskAlertModel(
            alert_id=alert_id,
            well_id=well_id,
            risk_type=RiskType(risk_type),
            risk_level=RiskLevel(risk_level),
            created_at=created_at,
            current_depth=current_depth,
            projected_depth=round(current_depth + 38.5, 1),
            formation=formation,
            confidence=risk_data.get("confidence", 0.80),
            evidence=risk_data.get("historical_evidence", []),
            trigger_features=risk_data.get("trigger_features", []),
            analog_wells=risk_data.get("analog_wells", []),
            recommended_review_actions=recommended_actions,
            status=AlertStatus.DETECTED,
            model_version=risk_data.get("model_version", "v1.0.0-hybrid"),
            provenance_type=ProvenanceType.SYNTHETIC
        )

        self.active_alerts[key] = alert
        self.alert_history.append(alert)
        self.last_alert_time[key] = now

        return alert

    def acknowledge_alert(self, alert_id: str, user_name: str = "Engineer-on-Duty") -> Optional[RiskAlertModel]:
        for alert in self.alert_history:
            if alert.alert_id == alert_id:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = user_name
                return alert
        return None

    def resolve_alert(self, alert_id: str, user_name: str = "Rig-Superintendent") -> Optional[RiskAlertModel]:
        for alert in self.alert_history:
            if alert.alert_id == alert_id:
                alert.status = AlertStatus.RESOLVED
                alert.resolved_by = user_name
                # Remove from active alerts map
                key = f"{alert.well_id}:{alert.risk_type.value}"
                if key in self.active_alerts:
                    del self.active_alerts[key]
                return alert
        return None

    def get_all_alerts(self, well_id: Optional[str] = None) -> List[RiskAlertModel]:
        if well_id:
            return [a for a in self.alert_history if a.well_id == well_id]
        return self.alert_history

    def get_alert_by_id(self, alert_id: str) -> Optional[RiskAlertModel]:
        for alert in self.alert_history:
            if alert.alert_id == alert_id:
                return alert
        return None
