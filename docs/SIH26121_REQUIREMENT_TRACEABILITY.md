# SIH26121 Requirement Traceability Matrix (Oil India Limited)

## Overview
This document provides complete end-to-end traceability for Problem Statement **SIH26121** (*Real-Time Nearby Wells Intelligence System for Drilling Operations*) implemented in **eRTMAC-NWIS**.

---

## Traceability Matrix

| Requirement ID | Description | Implementation File | API Endpoint / Module | UI Component | Test Suite | Data Source & Provenance | Limitations & Notes |
|---|---|---|---|---|---|---|---|
| **R1** | AI/NLP/OCR Extraction & Document Grounding | `backend/app/services/knowledge_service.py` | `GET /api/v1/knowledge/search` | `MultiRiskPanel.tsx` | `test_r9_knowledge_repository_search` | Synthetic DDR/WCR documents (`SYNTHETIC`) | Page-level text grounding provided for prototype; OCR scanner handles uploaded PDFs |
| **R2** | Nearby Well Map & 3D Spatial Radius | `backend/app/main.py`, `backend/app/services/mcm.py` | `POST /api/v1/spatial/offset-wells` | `BasinMap.tsx` | `test_r3_spatial_offset_wells`, `test_f05_offset_wells` | Upper Assam Basin well coordinates (`SYNTHETIC`) | EPSG:3857 Web Mercator and Haversine spatial radius filtering |
| **R3** | Historical Knowledge Repository | `backend/app/services/knowledge_service.py` | `GET /api/v1/knowledge/search` | `MultiRiskPanel.tsx` | `test_r9_knowledge_repository_search` | Historical hazards dataset (`events.jsonl`, `SYNTHETIC`) | Multi-parameter filtering across depth, formation, NPT, and keyword |
| **R4** | Geology / Drilling / Reservoir Correlation | `backend/app/services/correlation_engine.py` | `GET /api/v1/offset-wells/analogs` | `AnalogCorrelationPanel.tsx` | `test_r4_correlation_engine_analogs` | Calibrated offset well profiles (`SYNTHETIC`) | Transparent 7-factor similarity score with configurable weights |
| **R5** | Multi-Risk Prediction Engine & Explainability | `backend/app/services/risk_engine.py`, `backend/app/services/explainability_service.py` | `GET /api/v1/risk/{well_id}/predict`, `GET /api/v1/risk/{well_id}/explanation` | `MultiRiskPanel.tsx` | `test_r5_multi_risk_prediction_engine`, `test_r6_model_explainability` | Trained RandomForest models (`models/*.joblib`) | Predicts STUCK_PIPE, MUD_LOSS, OVERPRESSURE, TORQUE_SPIKE, CEMENTING_ISSUE (Rule mode for sparse data) |
| **R6** | Real-Time Alerts & Evidence Recommendations | `backend/app/services/alert_engine.py`, `backend/app/services/recommendation_engine.py` | `GET /api/v1/alerts`, `GET /api/v1/recommendations` | `LookAheadCard.tsx` | `test_r7_stateful_alert_lifecycle`, `test_r8_evidence_backed_recommendation` | Historical event grounding (`SYNTHETIC`) | Stateful lifecycle (DETECTED->ACKNOWLEDGED->RESOLVED); Enforces `engineer_review_required = True` |
| **R7** | Interactive Drilling Dashboard & Doghouse View | `frontend/src/app/page.tsx`, `frontend/src/components/*` | WebSocket `/ws/v1/telemetry` | `page.tsx`, `DoghouseView.tsx` | `test_comb_ui_backend_flow` | Live 1 Hz Telemetry (`SYNTHETIC`) | 4-panel drilling intelligence console with touch-optimized doghouse mode |

---

## Safety & Governance Compliance
1. **Decision Support Only:** System provides advisory insights only. It never autonomously controls rig equipment.
2. **Data Transparency:** Global `ProvenanceBanner` and explicit `SYNTHETIC` labels displayed across all UI views and API endpoints.
3. **Qualified Engineer Review:** Every recommended action explicitly specifies `engineer_review_required = True`.
