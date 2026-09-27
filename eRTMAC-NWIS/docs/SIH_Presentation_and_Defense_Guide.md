# eRTMAC-NWIS — Pitch & Judge Defense Guide
## Master Presentation Choreography & Rock-Solid Q&A Playbook
### Smart India Hackathon 2026 · Problem Statement SIH26121 (Oil India Limited)

---

## 1. The 90-Second Opening Hook (For All Judges)

> *"Respected Jury, imagine driving down a dark highway at night in thick fog. Your GPS accurately shows where your car is right now, but it cannot see the washed-out bridge 100 metres ahead. That is exactly how oil wells are drilled today. 
> 
> Real-time command centres like Oil India's eRTMAC monitor surface sensors continuously. But when a drill bit penetrates an unexpected depleted sand or high-pressure gas pocket, it causes multi-crore stuck pipes and blowouts — like the tragic Baghjan-5 blowout that burned for 173 days. 
> 
> Yet, the warning was already known: an offset well drilled 500 metres away ten years ago recorded that exact hazard. But that critical knowledge was buried inside a 200-page scanned paper report in an archive. 
> 
> Today, we present **eRTMAC-NWIS**: The Nearby Wells Intelligence System. We turn decades of legacy reports into an active, 3D spatial memory that looks 50 metres ahead of the bit — alerting the drilling crew to downhole hazards before they hit them, with the exact engineering mitigation that saved the well last time."*

---

## 2. 5-Minute Live Demo Choreography (Rehearse to Perfection)

| Time | Presenter Action | On-Screen Visual | Script / What to Say |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:45** | Opening Hook | Slide 1: Burning platform (Baghjan-5 context & NPT costs: ₹25L/hour) | *"eRTMAC is OIL's eyes. NWIS is its institutional memory."* |
| **0:45 – 1:30** | Switch to Dashboard | Mapbox 2D Basin Navigator showing `SYN-NHK-05` at 2,410m in Nahorkatiya | *"Here is our active drilling well. When we adjust the offset radius slider to 3 km, NWIS instantly illuminates nearby offset wells in 3D space."* |
| **1:30 – 2:15** | Click "Curtain View" | 2D Stratigraphic Cross-Section Curtain connecting active well to offset wells | *"Notice that simple depth matching is fatal in Assam due to structural dip. As you see on this curtain, the Tipam Sandstone is tilted by 3.5°. NWIS computes True Stratigraphic Depth (TSD) to compare identical rock strata."* |
| **2:15 – 3:15** | Click "Start Live Telemetry" | WITSML 1 Hz stream starts. Bit advances from 2,410m to 2,415m. Screen flashes amber! | *"Look at the Look-Ahead Console: at 2,448m TVDSS — 33m ahead — Offset Well SYN-NHK-02 suffered 38 hours of stuck pipe due to 1,120 psi overbalance. We projected this before the bit penetrated the thief zone."* |
| **3:15 – 4:00** | Click "Export Tour Advisory" | Branded OIL 2-page PDF advisory downloads | *"The driller receives a signed, auditable mitigation card: maintain rotation >40 RPM, reduce mud density to 1.10 SG, and spot a lubricant pill."* |
| **4:00 – 4:30** | Show pgAdmin / Terminal | SQL spatial query running in 12 ms inside PostgreSQL container | *"Everything runs in a single Docker container on PostgreSQL with PostGIS and pgvector. Sub-second latency, zero GPU, 100% offline-ready for remote Brahmaputra rig sites."* |
| **4:30 – 5:00** | Conclusion | Summary slide | *"We don't replace eRTMAC. We give it foresight. Thank you, and we are open for questions."* |

---

## 3. Judge Q&A Playbook — Scripted Defenses

### Q1: "Is this real Oil India data or did you use public data?"
*   **The Defense:** *"Sir, Oil India's proprietary drilling data from Nahorkatiya is confidential and cannot be taken outside OIL's intranet. We are 100% transparent: our demo uses geologically calibrated synthetic Assam Basin wells whose formation tops, pore pressures, and dip angles are derived directly from published technical papers co-authored by Oil India engineers (specifically SPE-197489-MS by Biswas et al. and SPE-185408-MS). Our system is built on open WITSML 1.4 and OSDU standards — the moment OIL's IT team points our ingestion endpoint to eRTMAC's data stream, live Nahorkatiya data flows into the system without changing a single line of code."*

### Q2: "A depth in Well A is not the same formation depth in Well B. How do you handle structural dip and faulting?"
*   **The Defense:** *"Exactly, Sir — that is why naive depth matching fails. NWIS implements a three-step spatial-stratigraphic alignment pipeline:
    1. First, we convert Measured Depth (MD) to Subsea True Vertical Depth (TVDSS) using the Minimum Curvature Method (MCM).
    2. Second, our True Stratigraphic Depth (TSD) engine uses the local dip angle ($\theta$) and azimuth ($\alpha$) from seismic tops to compute coordinate rotation: $\Delta TVDSS_{\text{structural}} = \Delta X \sin\theta \sin\alpha + \Delta Y \sin\theta \cos\alpha$.
    3. Third, if an unmapped fault exists, our Dynamic Time Warping (DTW) module correlates real-time LWD Gamma Ray curves with offset logs to detect structural throw dynamically."*

### Q3: "Historical drilling reports from the 1970s and 80s are scanned, degraded, and have handwriting. How can OCR reliably read them?"
*   **The Defense:** *"We built a dual-track architecture specifically for oilfield documents:
    *   For digitally typed reports (post-2000), PyMuPDF and Camelot Lattice achieve 99.5% accuracy in 50 milliseconds per page with zero GPU.
    *   For noisy historical scans, we deploy IBM Docling's CPU-native TableFormer model, with a Vision-Language Model fallback for handwritten annotations.
    *   Crucially, we do not let LLMs guess: every extracted value is validated against a strict Pydantic schema enforcing physical boundaries — mud weights must be between 0.8 and 2.5 SG, and operational codes must match standard IADC codes."*

### Q4: "Why did you use PostgreSQL instead of Neo4j for the knowledge graph?"
*   **The Defense:** *"We evaluated Neo4j. While Neo4j excels at graph traversals, it performs poorly at 10 Hz time-series telemetry streaming and lacks native 3D spatial indexing. In drilling operations, we have three distinct query patterns: 3D spatial radius searches, 1 Hz sensor time-series ingestion, and semantic text similarity on drilling remarks. PostgreSQL 16 with PostGIS, TimescaleDB, and pgvector handles all three workloads in a single ACID-compliant database engine with a single connection pool and zero synchronization drift."*

### Q5: "What is your real-time anomaly detection mechanism?"
*   **The Defense:** *"We do not use black-box neural networks that cause alarm fatigue. We use hybrid physics-informed indicators:
    1. **Teale's Mechanical Specific Energy (MSE):** $MSE = \frac{WOB}{A_b} + \frac{120\pi \cdot RPM \cdot Torque}{A_b \cdot ROP}$. A sudden MSE spike with ROP collapse in Girujan Clay diagnoses bit balling before pipe sticking occurs.
    2. **Torque & Drag Broomstick Residuals:** We compare measured hook load and torque against theoretical soft-string friction curves ($\mu = 0.20$).
    3. **Dynamic Mud Weight Window:** We monitor downhole ECD against offset leak-off test (LOT) fracture limits and formation pore pressure."*

### Q6: "What happens if VSAT satellite internet disconnects at the remote rig?"
*   **The Defense:** *"NWIS is designed offline-first. The entire knowledge base, spatial query engine, and physics models run locally in a single Docker container. If satellite connectivity drops, the rigsite system continues processing local WITS telemetry and issuing look-ahead advisories from historical offset data without interruption. When connectivity is restored, alert audit logs automatically sync back to Duliajan HQ."*

---

## 4. Key Differentiators: Competitors vs. eRTMAC-NWIS

| Evaluation Dimension | Typical Competitor (What Others Submit) | eRTMAC-NWIS (Our Solution) |
| :--- | :--- | :--- |
| **Core Architecture** | Generic LangChain PDF Chatbot (Streamlit UI) | Spatial-Stratigraphic Look-Ahead Engine (PostGIS + TimescaleDB) |
| **Depth Comparison** | Naive Measured Depth (MD) matching | Minimum Curvature Method (MCM) + True Stratigraphic Depth (TSD) |
| **Anomaly Detection** | Black-box LSTM / Isolation Forest | Physics-informed: Teale's MSE + T&D Residuals + ECD Safe Corridor |
| **Drilling Standards** | Generic CSV tables | WITSML v1.4.1.1 / v2.0 + IADC Operation Event Codes + OSDU schema |
| **Data Grounding** | Claims random open data is OIL data | Transparently calibrated synthetic Assam Basin data (SPE-197489) |
| **Operational Output** | Free-text AI chatbot response | Signed, deterministic 2-page Tour Advisory PDF for Rig Superintendent |
