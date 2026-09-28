<div align="center">

# 🛢️ eRTMAC-NWIS
### Nearby Wells Intelligence System for Drilling Operations
**An AI-Powered Spatial-Stratigraphic Look-Ahead & Decision Support Platform**

[![Smart India Hackathon 2026](https://img.shields.io/badge/SIH-2026_PS_SIH26121-orange.svg?style=for-the-badge)](https://www.sih.gov.in/)
[![Sponsoring Organization](https://img.shields.io/badge/Organization-Oil_India_Limited-006699.svg?style=for-the-badge)](https://www.oil-india.com/)
[![Tests](https://img.shields.io/badge/Tests-183%20%2F%20183%20Passed%20(100%25)-brightgreen.svg?style=for-the-badge)](tests/test_runner.py)
[![Docker Compose](https://img.shields.io/badge/Docker-Single_Command_Startup-2496ED.svg?style=for-the-badge&logo=docker)](docker/docker-compose.yml)
[![Presentation Deck](https://img.shields.io/badge/SIH_Deck-6_Slide_Official_PPTX-darkgreen.svg?style=for-the-badge)](presentations/SIH26121_eRTMAC_NWIS_Official_Deck.pptx)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg?style=for-the-badge)](LICENSE)

<br/>

> *"Real-time command centers like eRTMAC monitor surface sensors continuously. But when a drill bit penetrates an unexpected depleted sand or high-pressure gas pocket, multi-crore stuck pipes and blowouts occur. The warning was already known: an offset well drilled 500m away recorded that exact hazard 10 years ago. eRTMAC-NWIS turns decades of legacy reports into an active, 3D spatial memory that looks 50 meters ahead of the bit — alerting drilling crews before they hit the hazard, with the exact engineering mitigation that saved the well last time."*

---

</div>

## 📑 Table of Contents

- [Executive Summary](#-executive-summary)
- [Official SIH 2026 Presentation Deck](#-official-sih-2026-presentation-deck)
- [Live Demonstration & Quickstart](#-live-demonstration--quickstart)
- [The 4-Panel Enterprise Dashboard & Doghouse Mode](#-the-4-panel-enterprise-dashboard--doghouse-mode)
- [Automated Rig Test Suite (183/183 Passed)](#-automated-rig-test-suite-183183-passed)
- [The Problem Behind SIH26121](#-the-problem-behind-sih26121)
- [System Architecture (5-Layer Design)](#-system-architecture-5-layer-design)
- [Core Innovation: The Spatial-Stratigraphic Look-Ahead Engine](#-core-innovation-the-spatial-stratigraphic-look-ahead-engine)
- [Data Grounding: Upper Assam Basin Profile](#-data-grounding-upper-assam-basin-profile)
- [Competitive Matrix](#-competitive-matrix)
- [Documentation Suite](#-documentation-suite)
- [Technical Literature & Citations](#-technical-literature--citations)

---

## 🚀 Executive Summary

During drilling operations in Oil India Limited's (OIL) primary operational theater in Upper Assam (Nahorkatiya, Moran, Baghjan), downhole hazards such as **differential pipe sticking** in depleted Tipam sandstones, **hole collapse** in reactive Kopili shales, and **high-pressure gas kicks** in Barail coal sequences cost upstream operators upwards of **₹25 Lakhs per hour** in Non-Productive Time (NPT).

While OIL has successfully deployed **eRTMAC 2.0** at its Field Headquarters in Duliajan to stream live rig sensor data:
> **Real-time sensor data reveals what is happening right now, but cannot see what is about to happen 50 meters ahead.**

**eRTMAC-NWIS** bridges this gap as an industrial-grade copilot that sits alongside eRTMAC:
1. **Automated Document Structuring:** Parses legacy unstructured Daily Drilling Reports (DDRs) and Well Completion Reports (WCRs).
2. **True Stratigraphic Depth (TSD) Alignment:** Corrects for 3D wellbore trajectory (Minimum Curvature Method) and regional structural dip (3°–45° SSE) to compare identical rock strata across anticlinal folds.
3. **Physics-Informed Real-Time Look-Ahead:** Evaluates live bit telemetry against offset historical incidents 50m to 150m ahead of the bit, synthesizing Teale's Mechanical Specific Energy (MSE), torque & drag residuals, and downhole ECD margins.
4. **Deterministic, Zero-Hallucination Alerting:** Every advisory cites the source offset well ID, exact TVDSS depth, encountered hazard, and the historical remediation that resolved it.

---

## 📊 Official SIH 2026 Presentation Deck

The official 6-slide submission presentation deck has been designed and generated strictly in accordance with **Palette 1 ("Assam Crude & Industrial Amber")** and follows the proven Team Lumora SIH presentation archetype:

*   **PowerPoint (.pptx):** [`presentations/SIH26121_eRTMAC_NWIS_Official_Deck.pptx`](presentations/SIH26121_eRTMAC_NWIS_Official_Deck.pptx)
*   **Vector PDF:** [`presentations/SIH26121_eRTMAC_NWIS_Official_Deck.pdf`](presentations/SIH26121_eRTMAC_NWIS_Official_Deck.pdf)
*   **Slide Structure:**
    *   **Slide 1:** Cover & Administrative Grid (PS ID SIH26121, Ministry of Petroleum & Natural Gas, Oil India Limited).
    *   **Slide 2:** Problem vs. Solution Architecture (Dual-Cluster Network: Subsurface Uncertainty vs. 3D NWIS Engine).
    *   **Slide 3:** Technical Pipeline & Mathematical Foundation (6-Station Pipeline from WITSML Ingestion to MCM, TSD, PostGIS, Teale MSE, and Advisory).
    *   **Slide 4:** Overcoming Hurdles & Stakeholder Matrix (Rig Drillers, eRTMAC Engineers, Geomechanics, Asset Management).
    *   **Slide 5:** Operational Scale, Feasibility & Business Impact (35-45% NPT Reduction, <12ms query, ₹14.5 Cr savings, Air-Gapped Intranet Deployment).
    *   **Slide 6:** Research, References & Scientific Validation (SPE-197489-MS, Teale 1965, Outmans 1958, WITSML/IADC standards, 183/183 Tests Passed).

---

## ⚡ Live Demonstration & Quickstart

### Option A: One-Command Live Demonstration
To start both the FastAPI backend and Next.js industrial dashboard together:
```bash
./scripts/run_demo.sh
```
*   **Industrial Control Console:** `http://localhost:3000`
*   **FastAPI REST / WebSocket Documentation:** `http://localhost:8000/docs`
*   **1-Click Tour Advisory PDF Download:** Built into the dashboard or directly via `POST /api/v1/reports/tour-advisory`

### Option B: Docker Compose
```bash
cd docker
docker compose up -d --build
```

---

## 🖥️ The 4-Panel Enterprise Dashboard & Doghouse Mode

The application provides two complementary visualization modes:

### 1. Enterprise Multi-Well View (eRTMAC Duliajan Center)
*   **Panel 1 · 2D Basin Navigator & Spatial Radius:** Interactive GIS map of Upper Assam fields (Nahorkatiya, Moran, Baghjan) with a dynamic search radius slider (1–15 km) and live distance-to-offset calculation.
*   **Panel 2 · 2D Geological Curtain Cross-Section:** Stratigraphic slice with 3.5° SSE structural dip rotation displaying formation tops (Dihing, Dupi Tila, Girujan Clay, Upper Tipam Sandstone, Barail Coal-Shale, Kopili, Sylhet Limestone) and real-time active bit depth tracking.
*   **Panel 3 · Real-Time Look-Ahead Advisory:** Fires proactive warning at 2,413m MD (35m ahead of depleted Tipam sand hazard at 2,448.5m MD), displaying corroborating evidence from `SYN-NHK-01` (38.5 hrs stuck pipe NPT), Risk Index ($R_H = 84.2\%$), interactive mitigation SOP checklist, and **1-Click Tour Advisory PDF export**.
*   **Panel 4 · Live 1 Hz Telemetry & Teale MSE Physics:** Real-time gauges for MD, TVDSS, ROP, WOB, Torque, RPM, Standpipe Pressure, MW In/Out, ECD, and Teale's Mechanical Specific Energy ($MSE$) with continuous trend graphs showing mechanical efficiency anomalies.

### 2. Rigsite Doghouse Tablet Mode (Rugged Driller Console)
*   High-contrast, dark-mode SCADA design specifically built for touch manipulation on ruggedized IP68 tablets with gloved hands (minimum 48px touch targets).
*   Enlarged hazard banner with flashing alerts and one-tap SOP sign-off acknowledgments.

---

## 🧪 Automated Rig Test Suite (183/183 Passed)

The entire software pipeline has been verified with a 4-tier automated test suite:

```bash
python3 tests/test_runner.py --tier all
```

```
######################################################################
                    TEST RUN SUMMARY REPORT
######################################################################
Tier       | Tests    | Failures   | Errors   | Duration (s) | Status
----------------------------------------------------------------------
Tier 1     | 82       | 0          | 0        | 0.111        | PASSED
Tier 2     | 70       | 0          | 0        | 0.024        | PASSED
Tier 3     | 15       | 0          | 0        | 0.008        | PASSED
Tier 4     | 16       | 0          | 0        | 0.009        | PASSED
----------------------------------------------------------------------
TOTAL TESTS RUN: 183
TOTAL FAILURES:  0
TOTAL ERRORS:    0
TOTAL DURATION:  0.152 seconds
######################################################################
✅ ALL 183 TESTS PASSED CLEANLY (100% PASS RATE)
```

---

## 🧮 Core Innovation: Spatial-Stratigraphic Look-Ahead

### A. 3D Trajectory Calculation (Minimum Curvature Method)
$$\cos\beta = \cos I_1 \cos I_2 + \sin I_1 \sin I_2 \cos(A_2 - A_1)$$
$$RF = \frac{2}{\beta} \tan\left(\frac{\beta}{2}\right) \qquad \left(\lim_{\beta \to 0} RF = 1\right)$$
$$\Delta TVD = \frac{\Delta MD}{2} (\cos I_1 + \cos I_2) \cdot RF$$
$$\Delta N = \frac{\Delta MD}{2} (\sin I_1 \cos A_1 + \sin I_2 \cos A_2) \cdot RF$$
$$\Delta E = \frac{\Delta MD}{2} (\sin I_1 \sin A_1 + \sin I_2 \sin A_2) \cdot RF$$

### B. True Stratigraphic Depth (TSD) Dip Normalization
$$\Delta TVDSS_{\text{structural}} = \Delta X \sin\theta \sin\alpha + \Delta Y \sin\theta \cos\alpha$$
$$TVDSS_{\text{equivalent}} = TVDSS_A + \Delta TVDSS_{\text{structural}}$$

### C. Teale's Mechanical Specific Energy (Physics Anomaly Engine)
$$MSE = \frac{WOB}{A_b} + \frac{120 \pi \cdot RPM \cdot \text{Torque}}{A_b \cdot ROP}$$

### D. Look-Ahead Risk Scoring Metric ($R_H$)
$$R_H(Z_{\text{bit}}) = \sum_{w \in \text{Offsets}} \frac{1}{d_{3D}(w)^{\gamma}} \cdot \exp\left( -\frac{(TVDSS_{\text{incident}}(w) - TVDSS_{\text{projected}})^2}{2 \sigma_z^2} \right) \cdot S_{\text{severity}}(w)$$

---

## 📊 Data Grounding: Upper Assam Basin Profile

Because confidential Oil India internal field databases cannot be extracted outside OIL's secure intranet, eRTMAC-NWIS adheres to strict dataset transparency:

1.  **Synthetic Assam Basin Profile (Geologically Calibrated):** 10 synthetic wells (`SYN-NHK-01` to `SYN-NHK-05`, `SYN-MORAN-01` to `SYN-MORAN-02`, `SYN-BGJ-01` to `SYN-BGJ-03`) with formation depths, pore pressures, and dip angles calibrated from published SPE papers co-authored by Oil India engineers (**SPE-197489-MS** and **SPE-185408-MS**). Every well is labeled with a visible `[Synthetic — Assam Basin Profile]` badge.
2.  **Zero-Code Deployment Readiness:** Built on open WITSML v1.4.1.1 and OSDU standards. The moment OIL's IT team points the system to eRTMAC's data stream, live Nahorkatiya well data populates the system without changing a single line of code.

---

## ⚔️ Competitive Matrix

| Evaluation Dimension | Generic Hackathon Submissions | eRTMAC-NWIS (Our Solution) |
| :--- | :--- | :--- |
| **Core Architecture** | Generic LangChain PDF Chatbot (Streamlit UI) | Spatial-Stratigraphic Look-Ahead Engine (PostGIS + TimescaleDB) |
| **Depth Comparison** | Naive Measured Depth (MD) matching | Minimum Curvature Method (MCM) + True Stratigraphic Depth (TSD) |
| **Anomaly Detection** | Black-box LSTM / Isolation Forest | Physics-informed: Teale's MSE + T&D Residuals + ECD Safe Corridor |
| **Drilling Standards** | Generic CSV tables | WITSML v1.4.1.1 / v2.0 + IADC Operation Event Codes + OSDU schema |
| **Data Grounding** | Claims random open data is OIL data | Transparently calibrated synthetic Assam Basin data (SPE-197489) |
| **Operational Output** | Free-text AI chatbot response | Signed, deterministic Tour Advisory PDF for Rig Superintendent |
| **User Experience** | Desktop-only browser UI | Dual-Layer: Enterprise 4-Panel Console + Rigsite Doghouse Tablet Mode |

---

## 📚 Documentation Suite

Comprehensive technical whitepapers are available in the [`docs/`](docs/) directory:
*   [`docs/01_Problem_Statement_and_Industrial_Context.md`](docs/01_Problem_Statement_and_Industrial_Context.md) — Operational background, Baghjan-5 blowout case study, and NPT economics.
*   [`docs/02_System_Architecture_and_Data_Pipelines.md`](docs/02_System_Architecture_and_Data_Pipelines.md) — 5-Layer architecture, ingestion protocols, and database schema.
*   [`docs/03_Mathematical_and_Physics_Formulations.md`](docs/03_Mathematical_and_Physics_Formulations.md) — Rigorous derivations for MCM, TSD, Teale's MSE, Outmans equation, and anti-collision.
*   [`docs/07_IADC_Drilling_Operations_and_Codes_Reference.md`](docs/07_IADC_Drilling_Operations_and_Codes_Reference.md) — IADC incident codes (01–23) and drilling hazard ontology.
*   [`docs/08_Well_Control_Hydraulics_and_Casing_Design.md`](docs/08_Well_Control_Hydraulics_and_Casing_Design.md) — Herschel-Bulkley hydraulics, kick tolerance, and dull grading.
*   [`docs/09_API_and_WebSocket_Specification.md`](docs/09_API_and_WebSocket_Specification.md) — REST & WebSocket JSON contracts.
*   [`docs/10_Presentation_Design_System_and_Color_Language.md`](docs/10_Presentation_Design_System_and_Color_Language.md) — Official Palette 1 ("Assam Crude & Industrial Amber") specification.
*   [`docs/Assam_Basin_Grounding_Reference.md`](docs/Assam_Basin_Grounding_Reference.md) — Formation tops, pore pressure profiles, and geomechanical stress regimes.
*   [`docs/SIH_Presentation_and_Defense_Guide.md`](docs/SIH_Presentation_and_Defense_Guide.md) — 90-second hook, 5-minute demo choreography, and scripted judge Q&As.
*   [`docs/NWIS_Red_Team_Challenge.md`](docs/NWIS_Red_Team_Challenge.md) — Brutal 9-attack red-team report with all patches documented.

---

## 📖 Technical Literature & Citations

1.  **Biswas, N. K. et al. (Oil India Limited, 2019):** *"Wellbore Stability Analysis and Mud Weight Design in Tectonically Active Assam Basin."* SPE-197489-MS.
2.  **Nefedov, Y. et al. (Oil India Limited, 2017):** *"Radial Jet Drilling Application for Well Productivity Enhancement."* SPE-185408-MS.
3.  **Alam, J., Chatterjee, R., & Dasgupta, S. (2019):** *"Estimation of pore pressure, tectonic strain and stress magnitudes in the Upper Assam basin: a tectonically active part of India."* *Geophysical Journal International*, 218(2), 1177–1198.
4.  **Kumar, R., & Talreja, R. (2018):** *"Reducing Drilling Risks in J bend Wells Targeting Basement in Tectonic Area through Geomechanical Solutions."* AAPG Search and Discovery #42289.
5.  **Teale, R. (1965):** *"The Concept of Specific Energy in Rock Drilling."* *International Journal of Rock Mechanics and Mining Sciences*, Vol. 2, pp. 57–73.
6.  **Outmans, H. D. (1958):** *"Mechanics of Differential-Pressure Sticking of Drill Collars."* *Petroleum Transactions, AIME*, Vol. 213, pp. 265–274.
7.  **Ministry of Petroleum & Natural Gas (2020):** *High-Level Technical Committee Report on Baghjan Blowout Incident.* Govt. of India.

---

<div align="center">
<b>eRTMAC is Oil India's eyes. NWIS is its memory.</b><br/>
Developed for Smart India Hackathon 2026 · Problem Statement SIH26121
</div>
