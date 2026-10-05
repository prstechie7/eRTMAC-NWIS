"""
Canonical Data Models for eRTMAC-NWIS Drilling Intelligence System.
Compliant with SIH26121 (Oil India Limited).
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ProvenanceType(str, Enum):
    PUBLIC = "PUBLIC"
    SYNTHETIC = "SYNTHETIC"
    OIL_INTERNAL = "OIL_INTERNAL"


class DocumentType(str, Enum):
    WCR = "WCR"
    DDR = "DDR"
    EOWR = "EOWR"
    OTHER = "OTHER"


class RiskType(str, Enum):
    MUD_LOSS = "MUD_LOSS"
    STUCK_PIPE = "STUCK_PIPE"
    OVERPRESSURE = "OVERPRESSURE"
    TORQUE_SPIKE = "TORQUE_SPIKE"
    CEMENTING_ISSUE = "CEMENTING_ISSUE"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    DETECTED = "DETECTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


# --- 1. Well Schema ---
class WellModel(BaseModel):
    well_id: str
    uwi: Optional[str] = None
    well_name: str
    field: str
    latitude: float
    longitude: float
    datum: str = "KB"
    total_depth_md: float
    total_depth_tvd: float
    well_type: str = "EXPLORATION"  # DEVELOPMENT | EXPLORATION | APPRAISAL
    status: str = "COMPLETED"       # DRILLING | COMPLETED | SUSPENDED
    operator: str = "Oil India Limited"
    spud_date: Optional[str] = None
    completion_date: Optional[str] = None
    provenance_type: ProvenanceType = ProvenanceType.SYNTHETIC


# --- 2. Trajectory Station Schema ---
class TrajectoryStationModel(BaseModel):
    well_id: str
    measured_depth: float
    inclination: float
    azimuth: float
    TVD: float
    northing: float
    easting: float
    TVDSS: float


# --- 3. Formation Schema ---
class FormationModel(BaseModel):
    formation_id: str
    formation_name: str
    top_md: float
    base_md: float
    top_tvd: float
    base_tvd: float
    dip: float = 0.0
    dip_direction: float = 0.0
    lithology: str = "Sandstone/Shale"


# --- 4. Reservoir Schema ---
class ReservoirModel(BaseModel):
    reservoir_id: str
    formation_id: str
    reservoir_name: str
    pressure: float           # psi
    temperature: float        # deg C
    porosity: float           # % or fraction
    permeability: float       # mD
    fluid_type: str           # OIL | GAS | WATER
    depletion_indicator: float = 0.0  # 0 to 1
    pressure_window_min: float
    pressure_window_max: float


# --- 4b. Well Log Schema (FORCE 2020 / Wireline / LWD Standard) ---
class WellLogRecordModel(BaseModel):
    well_id: str
    md: float
    tvd: Optional[float] = None
    GR: Optional[float] = Field(None, description="Gamma Ray (gAPI)")
    RHOB: Optional[float] = Field(None, description="Bulk Density (g/cm3)")
    NPHI: Optional[float] = Field(None, description="Neutron Porosity (v/v)")
    DT: Optional[float] = Field(None, description="Acoustic Compressional Slowness (us/ft)")
    RES: Optional[float] = Field(None, description="Deep Resistivity (ohm.m)")
    SP: Optional[float] = Field(None, description="Spontaneous Potential (mV)")
    CALI: Optional[float] = Field(None, description="Caliper Hole Diameter (in)")
    ROP: Optional[float] = Field(None, description="Rate of Penetration (m/hr)")
    MUDWEIGHT: Optional[float] = Field(None, description="Mud Weight (SG)")
    lithology: Optional[str] = Field(None, description="Interpreted Lithofacies / Rock Type")
    provenance_type: ProvenanceType = ProvenanceType.SYNTHETIC


# --- 5. Drilling Parameters / Telemetry Schema ---
class DrillingParametersModel(BaseModel):
    timestamp: float
    well_id: str
    depth_md: float
    tvdss: float
    ROP: float
    WOB: float
    RPM: float
    torque: float
    hookload: float
    standpipe_pressure: float
    pump_rate: float
    mud_weight_in: float
    mud_weight_out: float
    ECD: float
    pit_volume: float
    flow_in: float
    flow_out: float
    provenance_type: ProvenanceType = ProvenanceType.SYNTHETIC


class StandardizedDrillingTelemetryModel(BaseModel):
    timestamp: float
    well_id: str
    md: float
    tvd: Optional[float] = None
    tvdss: Optional[float] = None
    rop: float
    wob: float
    rpm: float
    torque: float
    hook_load: float
    spp: float
    flow_rate: float
    mud_weight_in: float
    mud_weight_out: float
    ecd: float
    pit_volume: float
    pump_rate: Optional[float] = None
    mse: Optional[float] = Field(None, description="Mechanical Specific Energy (psi or MPa)")
    torque_anomaly: Optional[float] = None
    ecd_margin: Optional[float] = None
    rop_anomaly: Optional[float] = None
    pressure_anomaly: Optional[float] = None
    provenance_type: ProvenanceType = ProvenanceType.SYNTHETIC


# --- 6. Historical Event Schema ---
class HistoricalEventModel(BaseModel):
    event_id: str
    well_id: str
    timestamp: Optional[str] = None
    depth_md: float
    tvdss: float
    formation_id: Optional[str] = None
    reservoir_id: Optional[str] = None
    event_type: str              # STUCK_PIPE | MUD_LOSS | GAS_KICK | etc.
    severity: int = 3            # 1 to 5
    duration: float = 0.0        # hours
    NPT_hours: float = 0.0
    description: str
    root_cause: str
    mitigation: str
    outcome: str
    source_document_id: Optional[str] = None
    source_page: Optional[int] = None
    source_excerpt: Optional[str] = None
    provenance_type: ProvenanceType = ProvenanceType.SYNTHETIC


# --- 7. Document Schema ---
class DocumentModel(BaseModel):
    document_id: str
    well_id: str
    document_type: DocumentType = DocumentType.DDR
    file_name: str
    source: str
    upload_date: str
    page_count: int = 1
    extraction_status: str = "COMPLETED"
    extraction_confidence: float = 0.95
    provenance_type: ProvenanceType = ProvenanceType.SYNTHETIC


# --- 8. Analog Offset Well Response Schema ---
class OffsetAnalogWell(BaseModel):
    well_id: str
    well_name: str
    analog_score: float
    distance_km: float
    formation_match: float
    depth_delta_m: float
    reservoir_match: float
    trajectory_similarity: float
    drilling_signature: float
    historical_event_count: int
    risk_relevance: float
    provenance_type: ProvenanceType = ProvenanceType.SYNTHETIC


# --- 9. Risk Prediction Response Schema ---
class RiskPredictionItem(BaseModel):
    risk_type: RiskType
    risk_score: float
    risk_level: RiskLevel
    probability: float
    confidence: float
    prediction_horizon: str = "50m"
    trigger_features: List[str]
    historical_evidence: List[Dict[str, Any]]
    analog_wells: List[str]
    formation_context: str
    reservoir_context: str
    model_version: str = "v1.0.0-hybrid"
    timestamp: str
    provenance_type: ProvenanceType = ProvenanceType.SYNTHETIC


# --- 10. Alert Schema ---
class RiskAlertModel(BaseModel):
    alert_id: str
    well_id: str
    risk_type: RiskType
    risk_level: RiskLevel
    created_at: str
    current_depth: float
    projected_depth: float
    formation: str
    confidence: float
    evidence: List[Dict[str, Any]]
    trigger_features: List[str]
    analog_wells: List[str]
    recommended_review_actions: List[str]
    status: AlertStatus = AlertStatus.DETECTED
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    model_version: str = "v1.0.0-hybrid"
    provenance_type: ProvenanceType = ProvenanceType.SYNTHETIC


# --- 11. Evidence-Backed Recommendation Schema ---
class RecommendationItem(BaseModel):
    recommendation_id: str
    risk_type: RiskType
    summary: str
    historical_basis: str
    source_well: str
    source_event: str
    source_document: Optional[str] = None
    source_page: Optional[int] = None
    source_excerpt: Optional[str] = None
    confidence: float
    engineer_review_required: bool = True
    provenance_type: ProvenanceType = ProvenanceType.SYNTHETIC
