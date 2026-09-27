# 02. System Architecture & Data Pipelines
## End-to-End Architectural Blueprint for eRTMAC-NWIS

---

## 1. High-Level Architecture Overview

eRTMAC-NWIS is built on a 5-layer modular, service-oriented architecture designed to run on-premise within Oil India Limited's Duliajan private cloud or air-gapped rigsite infrastructure.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 eRTMAC-NWIS SYSTEM ARCHITECTURE                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│  [LAYER 1: HETEROGENEOUS INGESTION LAYER]                                                        │
│   ├── Real-Time Telemetry: WITSML v1.4.1.1 & v2.0 (1 Hz Rig Telemetry via jeng parser)            │
│   ├── Structured Well Logs: Wireline/LWD Logs (.LAS v2.0/3.0 via lasio)                          │
│   ├── Directional Well Surveys: Survey stations (.csv, .xlsx) via wellpathpy Minimum Curvature   │
│   └── Legacy Drilling Reports: Scanned WCRs, DDRs, and Mud Logs (.pdf, .tiff, images)            │
│                                         │                                                        │
│                                         ▼                                                        │
│  [LAYER 2: DUAL-TRACK DOCUMENT AI & STRUCTURING PIPELINE (CPU-NATIVE)]                           │
│   ├── Pre-Flight Probe: PyMuPDF char-count probe (<10ms/page)                                    │
│   │   ├── [Track 1: Digital Born PDFs] → PyMuPDF find_tables() + Camelot Lattice (99.5% acc)    │
│   │   └── [Track 2: Scanned/Degraded PDFs] → IBM Docling (TableFormer) / Gemini 1.5 Flash Vision│
│   └── Pydantic Schema Validation: Enforces IADC operation codes, physical mud weights (0.8-2.5SG)│
│                                         │                                                        │
│                                         ▼                                                        │
│  [LAYER 3: UNIFIED SPATIAL-GEOLOGICAL STORAGE ENGINE (PostgreSQL 16+)]                           │
│   ├── PostGIS 3.4: 3D Trajectory Splines, ST_3DDistance, ST_DWithin 3D Cylindrical Buffers      │
│   ├── TimescaleDB 2.x: Hypertables for 1 Hz WITSML sensor streams (90%+ compression)            │
│   ├── Relational Core: Wells, Assam Stratigraphic Tops Ontology, Casing Tallies, Hazard Records   │
│   └── pgvector: 384-dim flat cosine similarity on historical narrative remarks (all-MiniLM-L6-v2)│
│                                         │                                                        │
│                                         ▼                                                        │
│  [LAYER 4: SPATIAL-STRATIGRAPHIC INTELLIGENCE ENGINE]                                            │
│   ├── Minimum Curvature Method (MCM): MD → TVD, Northing, Easting, TVDSS calculation             │
│   ├── True Stratigraphic Depth (TSD): 3D coordinate rotation for structural dip & fault throw   │
│   ├── Constrained Dynamic Time Warping (CDTW): Sakoe-Chiba windowed Gamma Ray log correlation     │
│   ├── Physics Surrogate Models: Teale's Mechanical Specific Energy (MSE), Soft-String T&D, ECD  │
│   └── Spatial Look-Ahead Scanner: Evaluates historical offset incidents 50m–150m ahead of bit    │
│                                         │                                                        │
│                                         ▼                                                        │
│  [LAYER 5: INDUSTRIAL DASHBOARD & DECISION SUPPORT LAYER]                                        │
│   ├── Geospatial Basin Navigator: Mapbox GL JS (2D offset well selection within dynamic radius)  │
│   ├── 2D Geological Correlation Curtain: Cross-section connecting active well to offset horizons │
│   ├── 3D Wellbore & Horizon Visualizer: Three.js / WebGL multi-well trajectory rendering         │
│   ├── Synchronized Multi-Well Log Tracks: react-plotly.js WebGL with linked vertical depth axis  │
│   ├── Proactive Look-Ahead Hazard Console: Real-time risk cards with source well attribution     │
│   └── Operational Handover: 1-click export of signed 2-page Tour Advisory PDF                    │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Layer-by-Layer Technical Specifications

### Layer 1: Ingestion Layer
*   **WITSML Telemetry Ingestion:** Uses the `jeng` (v1.0.1) library to parse WITSML v1.4.1.1 XML data streams directly into pandas DataFrames. Supports channels: `DEPTH`, `HKLD`, `WOB`, `TORQ`, `RPM`, `SPP`, `FLOWIN`, `FLOWOUT`, `MUDIN`, `MUDOUT`, `ECD`, `GAS_TOTAL`.
*   **Petrophysical Wireline Logs:** Ingests LAS v2.0 files using `lasio` (v0.32) with automatic Latin-1 character encoding detection to prevent Unicode crashes on degree (`°`) and microsecond (`µs/ft`) symbols.
*   **Directional Surveys:** Directional surveys containing Measured Depth (`MD`), Inclination (`INC`), and Azimuth (`AZI`) are processed using `wellpathpy` (v0.5.2) to compute continuous 3D coordinate trajectories and Dogleg Severity (DLS).

### Layer 2: Dual-Track Document AI Pipeline
To eliminate the high-latency GPU dependency of models like LayoutLMv3, NWIS employs an intelligent triage router:
*   **Track 1 (Fast Path for Digital PDFs):** Scans the character stream using PyMuPDF. If character density exceeds 150 characters per page, the PDF is processed using PyMuPDF's C++ table extraction engine and `camelot-py` (Lattice mode). Runs in **<50 ms per page on CPU** with 99.5% numerical precision.
*   **Track 2 (Deep Path for Scanned Reports):** For image-only legacy scans, the pipeline routes to **IBM Docling** utilizing **TableFormer** for CPU-native table structure extraction, or an optional multimodal Vision API (Gemini 1.5 Flash Vision / GPT-4o Vision) for degraded handwriting.
*   **Pydantic Schema Validation:** All extracted values are validated against the `DrillingHazardRecord` schema:
    ```python
    class DrillingHazardRecord(BaseModel):
        well_name: str
        formation_name: str
        depth_md_m: float = Field(gt=0, lt=10000)
        depth_tvdss_m: float
        hazard_type: Literal['DIFFERENTIAL_STICKING', 'LOST_CIRCULATION', 'GAS_KICK', 'PACK_OFF', 'BIT_BALLING']
        severity_level: int = Field(ge=1, le=5)
        npt_hours: float = Field(ge=0)
        mud_density_sg: float = Field(ge=0.8, le=2.5)
        failure_cause: str
        mitigation_action: str
    ```

### Layer 3: Unified PostgreSQL Engine
Consolidates four database technologies into a single PostgreSQL 16 container (`timescale/timescaledb-ha:pg16`):
1.  **PostGIS 3.4:** Handles 3D spatial geometry (`PointZ`), spatial indexing (`GIST`), and 3D distance calculations between active bit position and offset trajectories (`ST_3DDistance`, `ST_DWithin`).
2.  **TimescaleDB 2.x:** Manages high-frequency 1 Hz drilling sensor telemetry using partitioned hypertables with 90%+ chunk compression.
3.  **pgvector:** Provides 384-dimensional vector similarity search on historical drilling remarks using exact flat cosine distance.
4.  **Relational Core:** Enforces relational integrity across wells, formations, casings, and drilling hazards.

### Layer 4: Spatial-Stratigraphic Look-Ahead Engine
Performs continuous proactive hazard scanning:
1.  **Offset Well Selection:** Queries PostGIS for completed offset wells within a dynamic surface radius (1–15 km) and vertical TVDSS window (±200 m).
2.  **Stratigraphic Depth Normalization:** Applies Minimum Curvature Method (MCM) and structural dip coordinate rotation to convert Measured Depth to True Stratigraphic Depth (TSD).
3.  **Log Correlation:** Executes Constrained Dynamic Time Warping (CDTW via `dtaidistance`) on real-time Gamma Ray logs against offset type logs with a Sakoe-Chiba window constraint.
4.  **Physics Residual Computation:** Computes instantaneous Mechanical Specific Energy (MSE), soft-string torque & drag broomstick residuals, and downhole ECD margins against offset Leak-Off Test (LOT) fracture limits.
5.  **Composite Risk Scoring:** Calculates the look-ahead risk index $R_H(Z_{\text{bit}})$ across all nearby offset historical incidents.

### Layer 5: Industrial Control Room Dashboard
Built with Next.js 15, React 19, Tailwind CSS, and WebGL:
*   **Basin Map:** Mapbox GL JS 2D interactive basin navigation with dynamic radius slider, geological fault overlays, and well state indicators.
*   **Curtain View:** 2D stratigraphic cross-section connecting active well to offset wells, displaying tilted formation horizons.
*   **3D Trajectory Viewer:** Three.js WebGL visualization showing 3D wellbores penetrating semi-transparent geological formation planes.
*   **Synchronized Log Viewer:** `react-plotly.js` WebGL multi-track log viewer with linked vertical depth axes, auto-synchronized crosshairs, and inverted depth display.
*   **Telemetry Streaming:** WebSocket connection (`react-use-websocket`) with a `useRef` rolling circular buffer to stream 1 Hz sensor data without UI frame drops.
