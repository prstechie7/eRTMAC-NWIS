# eRTMAC-NWIS (Nearby Wells Intelligence System)

**An AI-Powered Offset Well Knowledge and Decision Support Platform for Drilling Operations**

![Project Status](https://img.shields.io/badge/Status-Complete-brightgreen)
![Hackathon](https://img.shields.io/badge/SIH-26121-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/Frontend-Next.js-black)

## 📌 Problem Statement Background (SIH26121 - Oil India Limited)
Oil India Limited’s digital real-time monitoring system (eRTMAC) provides real-time drilling data, mud logging information, and wellsite analytics. However, drilling decisions in geologically complex formations require insights from nearby historical wells. Historical data currently resides across numerous unstructured PDF reports and individual experiences, making retrieval time-consuming. 

**eRTMAC-NWIS** solves this by unifying historical offset well data, real-time WITSML telemetry, and advanced Machine Learning hazard models into a single, proactive decision-support console.

---

## 🏗 System Architecture

The architecture is built on a modern, decoupled stack designed for high-frequency data ingestion and real-time inference.

1. **Frontend (Next.js / React)**
   - **Framework:** Next.js (App Router), TailwindCSS, Recharts.
   - **Features:** 
     - **Innovations Console:** A dashboard aggregating the top AI/Physics innovations (Pore pressure, NPT Cost, Hazard Heatmap).
     - **Multi-Agent Copilot:** An intelligent drilling assistant powered by Gemini 2.5 Flash, providing synthesized reasoning for complex operational queries.
     - **Real-Time Telemetry Track:** Sub-second visualization of WITSML simulated metrics (ROP, WOB, RPM, Standpipe Pressure).
     - **MapTiler Integration:** Interactive geographical mapping of Indian Basins and offset wells.

2. **Backend (Python / FastAPI)**
   - **Framework:** FastAPI, Uvicorn, Pydantic.
   - **Features:**
     - **Real-time WebSockets:** High-frequency telemetry streaming (`/ws/v1/telemetry`).
     - **Innovations Service:** 20 distinct physics and AI models (A1-A20), including D-Exponent Pore Pressure, Mechanical Specific Energy (MSE), BHA Fatigue tracking, and NPT Cost quantification.
     - **AI Search & Copilot Service:** Generative AI powered by Google Gemini, capable of automatically drafting Daily Drilling Reports (DDR) and cross-referencing offset historical anomalies.
     - **Stateless ML Inference:** Joblib-based Scikit-Learn models for stuck pipe, mud loss, and torque predictions.

3. **Data Layer**
   - Geologically calibrated synthetic dataset for the Nahorkatiya/Upper Assam basin.
   - Simulated offset well logs, Daily Drilling Reports (DDRs), and historical non-productive time (NPT) events.

---

## 🚀 Setup & Installation

### Prerequisites
- **Node.js** (v20+ recommended)
- **Python** (v3.9+ recommended)
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/prstechie7/eRTMAC-NWIS.git
cd eRTMAC-NWIS
```

### 2. Start the Backend (FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*The API documentation will be available at `http://localhost:8000/docs`.*

### 3. Start the Frontend (Next.js)
Open a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
*The dashboard will be available at `http://localhost:3000`.*

---

## 🔌 Core APIs Used

### WebSockets
- **`ws://localhost:8000/ws/v1/telemetry`**: Streams 1Hz synthetic drilling telemetry. Automatically injects hazard anomalies (like differential sticking) as depth progresses.

### REST Endpoints
- **`GET /api/v1/innovations/dashboard`**: Returns a unified JSON payload of the Top 5 Innovations (Pore Pressure, Lithology, NPT Cost Forecast, etc.).
- **`POST /api/v1/innovations/copilot`**: Conversational interface for the Multi-Agent Copilot. Accepts `question` and `depth_md_m`.
- **`GET /api/v1/innovations/generate-ddr`**: Automatically generates a Daily Drilling Report (DDR) summary based on the current depth and active hazards.
- **`GET /api/v1/innovations/hazard-heatmap`**: Returns the geographic distribution and count of historical incidents in the basin.
- **`GET /api/v1/wells`**: Fetches all available offset wells and their metadata.

---

## 💎 Key Innovations (Top 5)
1. **Financial NPT Exposure (A7):** Quantifies risk in actual USD using P10/P50/P90 probabilistic models based on historical offset events.
2. **D-Exponent Pore Pressure (A2):** Real-time kick margin and pore pressure tracking using normalized D-Exponent physics equations.
3. **Multi-Agent Copilot (A12):** A multi-agent AI system that cross-references real-time parameters with historical well completion reports before synthesizing an advisory.
4. **Auto DDR Generation (A13):** Eliminates manual reporting by drafting comprehensive shift reports instantly.
5. **Basin Hazard Heatmap (A8):** Visually maps historical sticking, kicking, and mud loss events across the target reservoir.

---

## 🛡 Testing
The backend features a robust test suite covering all tier 1 features and boundary conditions.
```bash
cd backend
pytest ../tests/tier1_features/test_f15_innovations.py -v
```

## 📝 License
This project was developed for **Smart India Hackathon (SIH 26121)**. All rights reserved.
