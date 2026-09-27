# 01. Problem Statement & Industrial Operational Context
## Smart India Hackathon 2026 · Problem Statement SIH26121
### Organization: Oil India Limited (Ministry of Petroleum and Natural Gas, Govt. of India)

---

## 1. The Operational Reality of Drilling Operations

Drilling deep exploration and development wells in geologically complex, tectonically active basins—such as Oil India Limited's (OIL) primary operational theater in the Upper Assam Shelf (Nahorkatiya, Moran, Baghjan, Kumchai, Mechaki)—presents extreme geomechanical, hydraulic, and commercial risks. 

Drilling operations run continuously (24 hours/day, 365 days/year) under severe hydrostatic downhole pressures (>6,000 psi) and elevated bottomhole temperatures (>140°C). Operating decisions cannot be made in isolation; they depend decisively on the historical behavior and downhole hazards recorded by nearby wells drilled through the same rock strata.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE DRILLING ENGINEER'S REALITY                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│  [PRE-SPUD PLANNING PHASE]                                                                       │
│   ├── Manual retrieval of 8–15 offset Well Completion Reports (WCRs) & Daily Drilling Reports     │
│   │   (takes 3–7 business days from physical paper archives at Field HQ Duliajan).              │
│   ├── Identifying depleted pressure zones (differential sticking risk) & overpressured shales.    │
│   └── Formulating the Casing Program, Mud Weight Window (MWW), and BHA cutter design.            │
│                                         │                                                        │
│                                         ▼                                                        │
│  [LIVE DRILLING PHASE (Bit Depth: 2,410m MD)]                                                    │
│   ├── Real-time rig sensor stream indicates surface torque fluctuating +3 kft-lb, ROP drops.     │
│   ├── Driller asks: "Is this bit wear, cuttings bed pack-off, or a porous depleted thief zone?"  │
│   ├── UNANSWERED: Offset Well NHK-114 suffered 400 bbls total loss and 38.5 hours of stuck pipe  │
│   │   at 2,448m MD in this exact sand package 12 years ago!                                      │
│   └── CONSEQUENCE: Bit penetrates thief zone, drillstring differentially sticks, NPT mounts.     │
│                                                                                                  │
│  FINANCIAL TOLL: 38.5 Hours NPT × ₹22 Lakhs/hour rig spread cost = ₹8.47 Crore preventable loss.  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Core Challenge: The "Air-Gapped Institutional Memory" Deficit

While Oil India Limited has successfully deployed **eRTMAC 2.0** (Enhanced Real-Time Monitoring & Analytics Centre) at its Field Headquarters in Duliajan, Assam, to monitor live surface and downhole WITSML rig telemetry:

> **Real-time monitoring reveals what is happening right now, but cannot see what is about to happen 50 metres ahead.**

The critical context required to anticipate downhole hazards resides buried inside decades of legacy, heterogeneous documents:
1. **Scanned PDF Reports:** Decades of Well Completion Reports (WCRs), Daily Drilling Reports (DDRs), and End of Well Reports (EOWRs), many dating back to the 1970s and 1980s with dot-matrix printing and handwritten tour sheet annotations.
2. **Petrophysical Wireline Logs:** Heterogeneous `.las` (LAS v2.0/v3.0) and `.dlis` wireline log files stored across disparate department drives.
3. **Cognitive Overload in the Command Center:** During peak operations, an eRTMAC operations engineer monitors 15 to 20 active drilling rigs simultaneously. Expecting engineers to manually retrieve, review, and cross-reference 500-page legacy reports while monitoring high-frequency sensor streams guarantees that impending hazard precedents are missed.

---

## 3. Oil India Limited Context: Operating Fields & Unique Hazards

### 3.1 Primary Operational Fields
*   **Nahorkatiya (NHK):** Discovered in 1953; one of India's oldest and most prolifically drilled onshore fields. Features 500+ drilled wells. Characterized by extensive sand depletion in the Tipam and Barail groups, creating severe differential sticking risks.
*   **Moran Field:** Located ~40 km southwest of Nahorkatiya; deep shelf anticlinal play targeting Barail sands at ~3,355 m (11,000 ft).
*   **Baghjan Field:** Deep north-bank structural play targeting Sylhet and Lakadong-Therria gas sands at 3,700–3,900 m depth under severe pore pressures.
*   **Kumchai Field (Arunachal Foothills):** Situated within the deformed Naga Schuppen Belt; characterized by steep structural dips (30°–45°), thrust fault splays, and severe tectonic compressive stresses.

### 3.2 The Baghjan-5 Blowout: Why Look-Ahead Intelligence Matters
On **27 May 2020**, Oil India Limited's **Baghjan Well-5** in Tinsukia district blew out during workover operations, catching fire on 9 June 2020 and burning for **173 days** before being successfully capped. The incident caused massive environmental damage to the adjacent Maguri-Motapung wetland and displaced thousands of local residents.

The official High-Level Technical Investigation confirmed the primary root causes:
1.  Inadequate early kick detection and sole reliance on surface pit gain monitoring.
2.  Lack of dynamic look-ahead intelligence regarding sudden pore pressure surges in the Barail Group and underlying Langpar/Sylhet gas sands.
3.  Failure to actively correlate live wellbore indicators with historical blowout and high-pressure gas influx precedents from adjacent offset wells in the block.

**eRTMAC-NWIS is engineered specifically to prevent another Baghjan incident by making offset hazard precedents dynamically available in real time.**
