# 🗄️ eRTMAC-NWIS Data Stack & Architecture
### Nearby Wells Intelligence System for Drilling Operations
**Smart India Hackathon 2026 · Problem Statement SIH26121 · Oil India Limited**

---

## 📌 Executive Data Strategy: The Dual-Layer Architecture

A critical question for any industrial AI drilling intelligence platform is **data provenance and grounding**. Rather than relying solely on purely random synthetic generation or naively attempting to claim that international offshore datasets represent Oil India's onshore Assam fields, **eRTMAC-NWIS** deploys a **scientifically sound Dual-Layer Architecture**:

```
                       ┌──────────────────────────────────────────────┐
                       │           eRTMAC-NWIS DATA STACK             │
                       └──────────────────────┬───────────────────────┘
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    │                                                   │
        ┌───────────▼───────────┐                           ┌───────────▼───────────┐
        │  ASSAM GEOLOGICAL     │                           │  GENERIC ML & PHYSICS │
        │  GROUNDING LAYER      │                           │  BENCHMARK LAYER      │
        ├───────────────────────┤                           ├───────────────────────┤
        │ • DGH NDR Stratigraphy│                           │ • FORCE 2020 Logs     │
        │ • Assam-Arakan Basin  │                           │ • Equinor Volve Field │
        │ • Nahorkatiya / Moran │                           │ • NLOG Netherlands   │
        │ • Baghjan Formations  │                           │ • Gulf of Suez Stuck  │
        │ • Calibrated Synthetic│                           │ • Lost Circulation V2 │
        └───────────┬───────────┘                           └───────────┬───────────┘
                    │                                                   │
                    └─────────────────────────┬─────────────────────────┘
                                              │
                                   ┌──────────▼──────────┐
                                   │  CANONICAL DRILLING │
                                   │  SCHEMA & STORE     │
                                   └──────────┬──────────┘
                                              │
                         ┌────────────────────┼────────────────────┐
                         │                    │                    │
                  ┌──────▼──────┐      ┌──────▼──────┐      ┌──────▼──────┐
                  │ 7-Factor    │      │ Multi-Risk  │      │ Knowledge   │
                  │ Correlation │      │ Prediction  │      │ & Handover  │
                  └─────────────┘      └─────────────┘      └─────────────┘
```

> **The Hackathon Judge Defense:**
> *"Indian and Assam geological context is strictly grounded using Directorate General of Hydrocarbons (DGH) NDR disclosures and published Upper Assam Basin literature (Nahorkatiya, Moran, Baghjan fields). Openly licensed international petroleum datasets (FORCE 2020, Volve, NLOG, Gulf of Suez) are utilized to train and validate generic drilling physics, well-log responses, trajectory mathematics, and downhole hazard classifiers. Operational telemetry remains calibrated synthetic until live Oil India eRTMAC/WITSML integration access is granted."*

---

## 🏛️ Authoritative Data Sources

| Requirement | Dataset / Source | Role in eRTMAC-NWIS | Provenance Tag |
| :--- | :--- | :--- | :--- |
| **Assam Geological Grounding** | **DGH National Data Repository (NDR)** / Assam-Arakan Basin | Formation tops, stratigraphy, basin profile, regional field targets (Nahorkatiya, Moran, Baghjan). | `PUBLIC` (DGH) |
| **Well Coordinates & Trajectories** | **DGH NDR + NLOG Subsurface Repository** | Well header metadata, geographic coordinates, 3D spatial radius searches, survey stations. | `PUBLIC` |
| **Well Logs & Lithology** | **FORCE 2020 Well Log & Lithofacies** (Zenodo 4351156) | GR, RHOB, NPHI, DT, RES, SP, CALI, ROP, MUDWEIGHT curves and interpreted lithofacies labels across 118 wells. | `PUBLIC` |
| **Multi-Well Field Operations** | **Equinor Volve Open Field Dataset** | ~40,000 files spanning multi-well drilling, trajectories, logging, casing, and daily drilling reports. | `PUBLIC` |
| **Lost Circulation Hazard Data** | **Public Lost Circulation Dataset (CirculationDataV2)** | 4 MB circulation dataset with pit volume, standpipe pressure, and mud-loss incident records. | `PUBLIC` |
| **Stuck Pipe Hazard Data** | **Gulf of Suez Research Dataset** | Sticking incidents, differential pressure overbalance, hookload anomalies, and string mechanics. | `PUBLIC` |
| **Real-Time Telemetry Standard** | **Energistics WITSML Log Specification v2.0** | Time- and depth-indexed XML/JSON telemetry interchange format matching eRTMAC rig feeds. | `STANDARDIZED` |
| **Operational Demo Grounding** | **Calibrated Upper Assam Profile** | Deterministic, geologically tuned well trajectories and telemetry matching Assam formations. | `SYNTHETIC` |

---

## 🗃️ Canonical Schema & Entity Architecture

The eRTMAC-NWIS data layer models drilling operations hierarchically:

```
                            ┌─────────────────┐
                            │      WELL       │
                            └────────┬────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           │                         │                         │
    ┌──────▼──────┐           ┌──────▼──────┐           ┌──────▼──────┐
    │ TRAJECTORY  │           │ FORMATIONS  │           │ RESERVOIRS  │
    └──────┬──────┘           └──────┬──────┘           └──────┬──────┘
           │                         │                         │
           └─────────────────────────┼─────────────────────────┘
                                     │
                           ┌─────────▼─────────┐
                           │ DRILLING INTERVAL │
                           └─────────┬─────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           │                         │                         │
    ┌──────▼──────┐           ┌──────▼──────┐           ┌──────▼──────┐
    │  TELEMETRY  │           │  WELL LOGS  │           │   EVENTS    │
    │  (WITSML)   │           │ (FORCE2020) │           │  (KNOWLEDGE)│
    └──────┬──────┘           └──────┬──────┘           └──────┬──────┘
           │                         │                         │
           └─────────────────────────┼─────────────────────────┘
                                     │
                           ┌─────────▼─────────┐
                           │  RISK PREDICTION  │
                           │   (5 HAZARDS)     │
                           └─────────┬─────────┘
                                     │
                           ┌─────────▼─────────┐
                           │  RECOMMENDATIONS  │
                           │(ENGINEER REVIEWED)│
                           └───────────────────┘
```

### Table Specifications

#### 1. `wells.csv`
```csv
well_id,uwi,well_name,field,latitude,longitude,datum,total_depth_md,total_depth_tvd,well_type,status,operator,spud_date,completion_date,provenance_type
```
*   `provenance_type`: `PUBLIC`, `SYNTHETIC`, or `OIL_INTERNAL`.

#### 2. `trajectory.csv`
```csv
well_id,measured_depth,inclination,azimuth,TVD,northing,easting,TVDSS,provenance_type
```
*   Calculated using Minimum Curvature Method (MCM).

#### 3. `formations.csv`
```csv
formation_id,formation_name,top_md,base_md,top_tvd,base_tvd,dip,dip_direction,lithology,provenance_type
```
*   Calibrated to Upper Assam: Dihing, Namsang, Girujan Clay, Upper Tipam, Lower Tipam, Barail Coal-Shale, Barail Main Sand, Kopili, Sylhet Limestone.

#### 4. `reservoirs.csv`
```csv
reservoir_id,formation_id,reservoir_name,pressure,temperature,porosity,permeability,fluid_type,depletion_indicator,pressure_window_min,pressure_window_max,provenance_type
```

#### 5. `logs.csv` (Standardized Wireline / LWD)
```csv
well_id,md,GR,RHOB,NPHI,DT,RES,SP,CALI,ROP,MUDWEIGHT,lithology,provenance_type
```
*   Adheres to the FORCE 2020 curve naming conventions.

#### 6. `drilling_telemetry.csv` (Standardized Real-Time Stream)
```csv
timestamp,well_id,md,tvd,tvdss,rop,wob,rpm,torque,hook_load,spp,flow_rate,mud_weight_in,mud_weight_out,ecd,pit_volume,pump_rate,mse,torque_anomaly,ecd_margin,rop_anomaly,pressure_anomaly,provenance_type
```
*   Includes derived drilling physics curves: Mechanical Specific Energy (MSE), ECD margin, torque anomaly, and pressure delta.

#### 7. `events.jsonl` (Historical Hazards Knowledge Store)
```json
{
  "event_id": "EVT-001",
  "well_id": "c1f7a012-3b4c-4e89-9a11-000000000001",
  "event_type": "STUCK_PIPE",
  "depth_md": 2448.5,
  "tvdss": 2179.0,
  "formation_id": "fmt-04",
  "reservoir_id": "res-01",
  "severity": 4,
  "duration": 38.5,
  "NPT_hours": 38.5,
  "description": "Differential sticking in depleted Upper Tipam Sandstone during survey.",
  "root_cause": "Pipe stationary for 45 min in depleted sand package. Overbalance > 1,120 psi.",
  "mitigation": "Spotted 40 bbls lubricant pill; reduced MW to 1.10 SG; rotated out with 55 RPM.",
  "outcome": "Pipe freed successfully.",
  "source_document_id": "DDR-NHK-SYN01-Day-42",
  "source_page": 4,
  "provenance_type": "SYNTHETIC"
}
```

---

## 🎯 Hazard-by-Hazard Data & Model Mapping

| Hazard / Risk | Primary Training Data | Secondary Validation Data | Model Type |
| :--- | :--- | :--- | :--- |
| **Stuck Pipe** | Gulf of Suez Stuck-Pipe Dataset | Equinor Volve + Calibrated Assam | Random Forest Classifier (`stuck_pipe_model.joblib`) |
| **Mud Loss** | CirculationDataV2 Lost Circulation | Western China Telemetry + Volve | Random Forest Classifier (`mud_loss_model.joblib`) |
| **Overpressure Gas Kick** | DGH Assam Stratigraphy + Published Studies | Volve / NLOG High Pressure Logs | Random Forest Classifier (`overpressure_model.joblib`) |
| **Torque Spike / Bit Balling** | Equinor Volve Drilling + FORCE 2020 Curves | Synthetic High-Frequency Telemetry | Random Forest Classifier (`torque_model.joblib`) |
| **Cementing Issue** | Volve Casing/Cement Data | Synthetic Offset Case Histories | **Rule-Based Engine** (`cementing_metadata.json`) with Sparse-Data Guard |

---

## 🛠️ Multi-Stage Pipeline Execution

The system provides an enterprise multi-stage pipeline:

```bash
# Step 1: Catalog and download/seed open benchmark datasets
python3 scripts/download_public_data.py

# Step 2: Normalize heterogeneous public sources to Canonical Drilling Schema
python3 scripts/normalize_public_data.py

# Step 3: Generate Calibrated Upper Assam Synthetic Datasets
python3 scripts/generate_assam_synthetic.py

# Step 4: Assemble Unified Training & Correlation Feature Store (CSV & Parquet)
python3 scripts/build_unified_dataset.py

# Step 5: Train & Evaluate Risk ML Models
python3 scripts/train_risk_models.py
```

---

## 🔗 Official Benchmark References & Documentation
- **[DGH National Data Repository (NDR)](https://dghindia.gov.in/ndr):** Indian National E&P well archive.
- **[DGH Assam-Arakan Basin Profile](https://www.ndrdgh.gov.in/NDR/?page_id=617):** Basin stratigraphy, hydrocarbon plays, and field profiles.
- **[FORCE 2020 Benchmark](https://zenodo.org/records/4351156):** Norwegian Continental Shelf well-log and lithofacies open dataset.
- **[Equinor Volve Data Sharing](https://www.equinor.com/energy/volve-data-sharing):** Open subsurface and operational field records.
- **[NLOG Dutch Subsurface Repository](https://www.nlog.nl/en/boreholes):** Spatial borehole and trajectory GIS database.
- **[Energistics WITSML Specification](https://docs.energistics.org/WITSML/WITSML_TOPICS/WITSML-000-048-0-C-sv2000.html):** Real-time drilling telemetry schema.
- **[Drilling Lost-Circulation Benchmark](https://github.com/HaythamElmousalami/Drilling-Lost-circulation):** Open loss incident dataset.
