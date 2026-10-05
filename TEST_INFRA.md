# eRTMAC-NWIS Test Infrastructure Specification (TEST_INFRA.md)
**Project**: eRTMAC-NWIS (Nearby Wells Intelligence System — SIH26121 - Oil India Limited)  
**Testing Track**: Opaque-Box Requirement-Driven E2E Test Suite  
**Author**: `e2e_test_writer_1`  
**Datum / Timestamp**: 2026-09-28T05:15:00Z  

---

## 1. Testing Philosophy

The testing architecture for **eRTMAC-NWIS** follows an **opaque-box, requirement-driven, physics-verified methodology**. 

1. **Opaque-Box Verification**: The test suite evaluates observable behavior against the explicit functional requirements in `ORIGINAL_REQUEST.md`, architectural contracts in `PROJECT.md`, physical equations in `docs/03_Mathematical_and_Physics_Formulations.md`, REST/WebSocket contracts in `docs/09_API_and_WebSocket_Specification.md`, and design tokens in `docs/10_Presentation_Design_System_and_Color_Language.md`. Tests treat implementation modules as black boxes, testing their inputs, outputs, invariants, and side effects.
2. **Authoritative Mathematical Oracles**: Physical calculations (Minimum Curvature Method, True Stratigraphic Depth dip correction, Teale's Mechanical Specific Energy, and the $R_H$ Proactive Look-Ahead Risk Index) are verified against independent analytical derivations rather than self-referential test mocks.
3. **Progressive Testability & Dual-Mode Execution**:
   - **Contract & Offline Specification Mode**: Verifies mathematical equations, database schema definitions (`01_schema.sql`), Docker orchestrations (`docker-compose.yml`), synthetic datasets (`synthetic_assam_wells.json`), and frontend design tokens/components without requiring external service up-time.
   - **Live Integration Mode**: When services are running (FastAPI on `:8000`, PostgreSQL on `:5432`, Next.js on `:3000`), the runner validates live HTTP/REST responses, TimescaleDB hypertable ingestion, WebSocket 1 Hz streaming, and PDF generation.
4. **Adversarial & Data Integrity Hardening**: Dedicated tests enforce Red Team compliance (Challenge Attacks 3 & 7) prohibiting unbadged or fabricated well names, ensuring universal `SYN-*` labeling and visible `[Synthetic — Assam Basin Profile]` indicators.

---

## 2. Feature Inventory (F1 – F14)

All 14 features defined in `PROJECT.md` are covered across the 4 test tiers:

| # | Feature Code | Feature Name | Milestone | Scope & Test Invariants |
|---|---|---|---|---|
| 1 | `F1` | Docker Infrastructure | M1 | Postgres 16 (`timescaledb-ha:pg16`), PostGIS 3.4, TimescaleDB, pgvector, `01_schema.sql` tables (`wells`, `trajectory_stations`, `formation_tops`, `drilling_hazards`, `live_telemetry`, `look_ahead_alerts`), hypertable setup, spatial function `find_offset_wells()`. |
| 2 | `F2` | MCM Trajectory Engine | M1 | Minimum Curvature Method (SPE/API) implementation: dogleg angle $\beta$, singularity protection ($RF=1.0$ for $\beta \to 0$), incremental $\Delta TVD$, $\Delta North$, $\Delta East$, $TVDSS = TVD - KB$, $DLS$ ($^\circ/30\text{m}$). |
| 3 | `F3` | Database Seed Engine | M1 | Loads `data/synthetic_assam_wells.json`, calculates 3D trajectories via MCM, inserts 10 wells across Nahorkatiya, Moran, and Baghjan fields, sets active well `SYN-NHK-05` at 2410m MD / 2180.5m TVDSS, populates historical hazard records. |
| 4 | `F4` | GET /api/v1/wells | M2 | Query wells filtered by `field_name` and `status`. Enforces `SYN-*` name schema, `data_source: SYNTHETIC`, coordinates, and elevation datums. |
| 5 | `F5` | POST /api/v1/spatial/offset-wells | M2 | Calls PostGIS `find_offset_wells()` with km-to-m conversion (e.g. 5.0 km $\to$ 5000 m), TSD structural dip calculation ($\Delta TVDSS = \Delta X \sin\theta \sin\alpha + \Delta Y \sin\theta \cos\alpha$), and hazard correlation. |
| 6 | `F6` | GET /api/v1/intelligence/lookahead | M2 | Evaluates 75m look-ahead window using $R_H(Z_{bit}) = \sum \frac{1}{d^\gamma} \exp(-\frac{\Delta Z^2}{2\sigma_z^2}) S_{severity}$. For `SYN-NHK-05` at 2410m MD, verifies $R_H \approx 84.2$ (HIGH/Amber), distance to hazard $+38.5\text{m}$, differential sticking evidence from `SYN-NHK-01`, and 4 mitigation steps. |
| 7 | `F7` | WS /ws/v1/telemetry Endpoint | M2 | Real-time 1 Hz WebSocket stream. Validates subscription protocol, 13 telemetry channels, 5 instantaneous physics channels (Teale's MSE), and 4 lookahead status channels. |
| 8 | `F8` | Next.js Foundation & Tokens | M3 | Tailwind configuration implementing Palette 1 ("Assam Crude & Industrial Amber"): Pine Green `#184E3A`, Petroleum Amber `#E58A13`, Charcoal Slate `#1E242B`, Canvas `#FFFFFF`, Card `#F8F9FA`, Red `#D9381E`. |
| 9 | `F9` | Data Integrity Badging | M3 | Universal UI enforcement: every well labeled `SYN-*` with visible badge `[Synthetic — Assam Basin Profile]`. Verifies immunity to Attack 3 & 7 (no fabricated real OIL well names like `NHK-114`). |
| 10 | `F10` | Dual-Engine Basin Map | M3 | 2D map component displaying well locations, radius slider (1–25 km, default 5 km), center controls, and automatic Leaflet fallback if `NEXT_PUBLIC_MAPBOX_TOKEN` is unset. |
| 11 | `F11` | Look-Ahead Alert Card | M3 | Interactive UI displaying live API look-ahead data for `SYN-NHK-05` $\to$ `SYN-NHK-01` scenario ($R_H=84.2$, $+38.5\text{m}$ distance, 1120 psi overbalance, 4-step actionable mitigations). |
| 12 | `F12` | WITSML Simulator | M4 | Python streaming script advancing `SYN-NHK-05` bit depth at 1 Hz from 2410m MD across hazard threshold (2448.5m MD) over WebSocket, triggering alert state escalation. |
| 13 | `F13` | One-Click PDF Export | M4 | 2-page OIL-branded Tour Advisory PDF generation adhering to Palette 1 styling, including active well telemetry, offset hazard correlation, and superintendent sign-off block. |
| 14 | `F14` | E2E Verification & Hardening| M5 | 100% test execution pass across all tiers, test runner CLI support (`--tier 1`, `--tier 2`, `--tier 3`, `--tier 4`, `--tier all`), and coverage threshold validation. |

---

## 3. 4-Tier Test Architecture

```
tests/
├── __init__.py
├── helpers/
│   ├── math_oracle.py          # Exact implementations of MCM, TSD, MSE, and R_H formulas
│   ├── schema_validator.py     # SQL DDL & database structure validator
│   ├── data_loader.py          # Synthetic dataset loader & schema checker
│   └── test_client.py          # Dual-mode HTTP/WS client (offline contract vs live HTTP)
├── tier1_features/             # >=5 test cases per feature (14 x 5 = 70+ tests)
│   ├── test_f01_docker_infra.py
│   ├── test_f02_mcm_engine.py
│   ├── test_f03_seed_engine.py
│   ├── test_f04_get_wells.py
│   ├── test_f05_offset_wells.py
│   ├── test_f06_lookahead.py
│   ├── test_f07_telemetry_ws.py
│   ├── test_f08_nextjs_tokens.py
│   ├── test_f09_data_integrity.py
│   ├── test_f10_basin_map.py
│   ├── test_f11_alert_card.py
│   ├── test_f12_witsml_sim.py
│   ├── test_f13_pdf_export.py
│   └── test_f14_e2e_verification.py
├── tier2_boundaries/           # >=5 boundary/corner test cases per feature (70+ tests)
│   ├── test_b01_docker_boundaries.py
│   ├── test_b02_mcm_singularities.py
│   ├── test_b03_seed_boundaries.py
│   ├── test_b04_wells_boundaries.py
│   ├── test_b05_offset_boundaries.py
│   ├── test_b06_lookahead_boundaries.py
│   ├── test_b07_ws_boundaries.py
│   ├── test_b08_tokens_boundaries.py
│   ├── test_b09_integrity_boundaries.py
│   ├── test_b10_map_boundaries.py
│   ├── test_b11_alert_boundaries.py
│   ├── test_b12_witsml_boundaries.py
│   ├── test_b13_pdf_boundaries.py
│   └── test_b14_system_boundaries.py
├── tier3_combinations/         # Cross-feature pairwise & pipeline tests (15+ tests)
│   ├── test_comb_seed_to_api.py
│   ├── test_comb_spatial_lookahead.py
│   ├── test_comb_witsml_telemetry.py
│   ├── test_comb_alert_pdf.py
│   └── test_comb_ui_backend_flow.py
├── tier4_scenarios/            # Real-world operational scenarios (5+ full-scale tests)
│   ├── test_scenario1_upper_tipam_entry.py
│   ├── test_scenario2_differential_sticking.py
│   ├── test_scenario3_offset_correlation.py
│   ├── test_scenario4_pdf_advisory_export.py
│   └── test_scenario5_data_integrity_audit.py
└── test_runner.py              # Standalone CLI test runner
```

---

## 4. Tier 4 Real-World Application Scenarios

The suite includes 5 fully specified operational application scenarios:

### Scenario 1: SYN-NHK-05 Upper Tipam Sandstone Interval Entry
- **Context**: Rig drills active well `SYN-NHK-05` at 2410.0m MD / 2180.5m TVDSS in Nahorkatiya field.
- **Verification**: Database and spatial queries reflect well status `DRILLING`, surface coordinate `(27.280000, 95.340000)`, KB elevation `112.0m`. As depth enters 2410m–2450m, formation top identifies `Upper Tipam Sandstone` with underpressured pore pressure ($0.92\text{ SG}$) and porous thief sands.

### Scenario 2: Proactive Differential Sticking Alert Escalation
- **Context**: Overbalance pressure calculated: $\Delta P = 0.052 \times (MW - PP) \times TVD = 0.052 \times (1.18 - 0.88) \times 7150\text{ ft} \approx 1120\text{ psi}$.
- **Verification**: $R_H$ formula with $\gamma=1.2, \sigma_z=15\text{m}$ outputs composite score $R_H \approx 84.2$ (`HIGH` risk level). Yellow caution alert triggers at $+38.5\text{m}$ distance ahead of 2448.5m MD horizon. Mitigations prescribe stationary pipe limit $<90\text{s}$, lubricant pill (40 bbls), and $>40\text{ RPM}$ rotation.

### Scenario 3: 3D Spatial Offset Well Correlation
- **Context**: Active bit at 2180.5m TVDSS calls `find_offset_wells(radius_km=5.0, tvdss_window_m=200.0)`.
- **Verification**: Successfully isolates `SYN-NHK-01` ($1.42\text{ km}$ NE) and `SYN-NHK-02` ($1.8\text{ km}$ NNE). Applies TSD bedding dip correction ($\theta=3.5^\circ, \alpha=145^\circ$) showing equivalent stratigraphic horizon correlation within $1.5\text{m}$ vertical delta.

### Scenario 4: OIL-Branded Tour Advisory PDF Export Validation
- **Context**: Company Man triggers 1-Click Tour Advisory PDF generation for drilling crew shift change.
- **Verification**: PDF document payload contains Palette 1 tokens (`#184E3A`, `#E58A13`, `#1E242B`), active well telemetry header, historical offset evidence table, 4-step actionable mitigations, and required superintendent sign-off block.

### Scenario 5: Universal Data Integrity & Red Team Compliance Audit
- **Context**: Comprehensive scan of all data payloads, API endpoints, mock fixtures, and UI templates against Red Team Challenge Attacks 3 & 7.
- **Verification**: 100% of wells carry `SYN-*` naming convention. Zero occurrences of unbadged real OIL well names (such as `NHK-114` or `MORAN-42`). Visible badge `[Synthetic — Assam Basin Profile]` accompanies every well presentation.

---

## 5. Coverage & Quality Thresholds

| Metric | Minimum Threshold | Target |
|---|---|---|
| **Tier 1 Feature Coverage** | $\ge 5$ test cases per feature (F1–F14) | 70+ test cases |
| **Tier 2 Boundary Cases** | $\ge 5$ boundary/corner cases per feature | 70+ test cases |
| **Tier 3 Cross-Feature** | $\ge 15$ pairwise/pipeline combinations | 15+ test cases |
| **Tier 4 Operational Scenarios** | 5 comprehensive real-world scenarios | 5 test cases |
| **Total Test Cases** | $\ge 160$ test assertions | 165+ test cases |
| **Execution Pass Rate** | 100% pass | 100% pass |
| **CLI Runner Support** | `--tier 1`, `--tier 2`, `--tier 3`, `--tier 4`, `--tier all` | Full support |
