# 07. IADC Drilling Operations & Event Codes Reference
## Standard Taxonomy for Legacy Report Digitization & Operational Event Classification

In drilling operations and Daily Drilling Reports (DDRs), operations are categorized using standard **International Association of Drilling Contractors (IADC)** operational codes. eRTMAC-NWIS uses this exact standard taxonomy to classify free-text remarks extracted from legacy reports into structured, queryable operational phases.

---

## 1. IADC Standard Daily Drilling Codes (1–23)

| Code | IADC Operational Activity | Description & Scope | NWIS Hazard Association |
| :--- | :--- | :--- | :--- |
| **01** | **Rig Service** | Routine maintenance, greasing drawworks, servicing top-drive/rotary. | Non-hazard operational baseline. |
| **02** | **Drilling** | Rotating or sliding the drill bit to make new hole. | Bit balling, ROP collapse, lithology transition, torque chatter. |
| **03** | **Reaming** | Enlarging or cleaning an under-gauge hole section. | Swelling shales (Girujan/Kopili), tight hole, borehole collapse. |
| **04** | **Coring** | Cutting and recovering geological core barrels. | Fragile coal recovery (Barail Group), jam-offs. |
| **05** | **Condition Mud & Circulate** | Pumping drilling fluid to clean hole, adjust mud weight, or treat gas cut mud. | Lost circulation, gas kick bottoms-up, high ECD, cutting accumulation. |
| **06** | **Tripping (POOH / RIH)** | Pulling drillstring out of hole or running drillstring into hole. | Swab & surge pressures, tight pull, overpull, mechanical pack-off. |
| **07** | **Lubricate Rig** | Periodic lubrication of rig floor and mast equipment. | Normal operations. |
| **08** | **Repair Rig** | Unscheduled mechanical or electrical rig repairs (NPT). | Equipment downtime. |
| **09** | **Cut Off Drilling Line** | Slipping and cutting the drilling wire rope per ton-mile schedule. | Scheduled maintenance. |
| **10** | **Deviation Survey** | Dropping or pumping down single-shot, multi-shot, or MWD directional survey tools. | **High differential sticking risk** (stationary pipe during survey: 15–45 min). |
| **11** | **Wireline Logging** | Rigging up and running electric wireline logging tools (GR, Resistivity, Sonic, Density). | Tool sticking in depleted sands or bridging in washouts. |
| **12** | **Run Casing & Cementing** | Running casing/liner strings, circulating, and pumping cement slurries. | High ECD fracturing weak sands, casing pack-off, poor cement bond. |
| **13** | **Wait on Cement (WOC)** | Waiting for downhole cement slurry to develop compressive strength. | Normal operations. |
| **14** | **Nipple Up / Test BOP** | Installing, pressure testing Blowout Preventer (BOP) stack and choke/kill manifolds. | Pressure barrier integrity verification. |
| **15** | **Drill Stem Test (DST)** | Downhole temporary completion to test formation fluid flow and pressure. | Hydrocarbon influx, high pressure gas kick. |
| **16** | **Fishing Operations** | Attempting to recover lost downhole equipment, parted drillstring, or stuck BHA. | **Major NPT event**; follows mechanical or differential stuck pipe. |
| **17** | **Directional Work / Steer** | Steering motor/RSS runs to hit trajectory target coordinates. | High dogleg severity, tortuosity, sliding friction. |
| **18** | **Well Control Operations** | Shutting in well, circulating out gas kicks via Driller's or Wait-and-Weight method. | **Critical safety hazard**; gas kick / overpressure in Barail/Sylhet. |
| **19** | **Waiting on Orders / Weather**| Rig shutdown due to environmental conditions (monsoon floods) or operator decisions. | External NPT. |
| **20** | **Rig Move / Skidding** | Disassembling, transporting, or skidding rig between pad slots. | Cluster pad development operations. |
| **21** | **Safety Meetings / Drills** | Rig floor safety meetings, pit drills, trip drills, choke drills. | Safety compliance. |
| **22** | **Special Operations** | Sidetracking, plug-and-abandon (P&A), casing cutting, radial jet drilling. | Remediating lost wellbores. |
| **23** | **Other / Miscellaneous** | Operations not falling into categories 1–22. | Unclassified narrative remarks. |

---

## 2. Downhole Hazard Taxonomy (NWIS Core Ontology)

NWIS maps DDR operations and morning tour remarks into 8 primary drilling hazard categories:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   NWIS DRILLING HAZARDS ONTOLOGY                                 │
├─────────────────────────┬─────────────────────────────────┬──────────────────────────────────────┤
│ Hazard Class            │ Physical Mechanism              │ Key Sensor / Log Indicators          │
├─────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ DIFFERENTIAL_STICKING   │ High hydrostatic overbalance    │ • Mud Weight >> Pore Pressure (ΔP)   │
│                         │ against permeable depleted sand │ • Stationary drillstring (RPM=0)     │
│                         │ with thick filter cake.         │ • Inability to rotate or pull string │
├─────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ LOST_CIRCULATION        │ Downhole ECD exceeds rock       │ • Flow out % drops below flow in %   │
│                         │ tensile fracture gradient / LOT.│ • Mud pit volume decreases rapidly   │
│                         │ Natural fault/karst loss.       │ • Standpipe pressure (SPP) drops     │
├─────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ GAS_KICK                │ Bottomhole pressure drops below │ • Active pit volume increases (gain) │
│                         │ formation fluid pore pressure.  │ • Flow out % exceeds flow in %       │
│                         │ Hydrocarbon influx expands.     │ • Total gas % (C1–C5) spikes         │
├─────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ MECHANICAL_PACK_OFF     │ Annular cuttings bed accumulation│• Overpull on upward pipe movement   │
│                         │ or unstable shale spalling      │ • Erratic torque and pressure spikes │
│                         │ collapses around drill collars. │ • Pump pressure climbs rapidly       │
├─────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ BIT_BALLING             │ Hydratable plastic swelling     │ • ROP collapses near zero            │
│                         │ clay (Girujan) sticks to bit    │ • Teale's MSE spikes exponentially   │
│                         │ cutters under low hydraulics.   │ • Surface torque flattens out        │
├─────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ WELLBORE_INSTABILITY    │ Tectonic in-situ stress contrast│ • Cavings / splintery shale in shakers│
│                         │ exceeds rock compressive strength│• Hole enlargement on Caliper log     │
│                         │ (shear breakout / spalling).    │ • Reaming torque increases           │
├─────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ WASHOUT                 │ Drillstring component erosion or│ • Gradual SPP drop at constant pump  │
│                         │ crack leaks mud into annulus.   │ • Mud pulse telemetry signal weakens │
├─────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ BHA_VIBRATION           │ Stick-slip, whirl, or axial bit │ • High-frequency torque oscillations │
│                         │ bounce in hard / cherty beds.   │ • Premature bit cutter fracture (PDC)│
└─────────────────────────┴─────────────────────────────────┴──────────────────────────────────────┘
```

---

## 3. Pydantic Event Extraction Schema

```python
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class IADCOperationCode(str, Enum):
    RIG_SERVICE = "01"
    DRILLING = "02"
    REAMING = "03"
    CORING = "04"
    CONDITION_MUD = "05"
    TRIPPING = "06"
    LUBRICATE_RIG = "07"
    REPAIR_RIG = "08"
    CUT_OFF_DRILLING_LINE = "09"
    DEVIATION_SURVEY = "10"
    WIRELINE_LOGGING = "11"
    RUN_CASING_CEMENT = "12"
    WAIT_ON_CEMENT = "13"
    TEST_BOP = "14"
    DRILL_STEM_TEST = "15"
    FISHING = "16"
    DIRECTIONAL_WORK = "17"
    WELL_CONTROL = "18"
    WAITING_ON_ORDERS = "19"
    RIG_MOVE = "20"
    SAFETY_MEETING = "21"
    SPECIAL_OPERATIONS = "22"
    OTHER = "23"

class HazardType(str, Enum):
    DIFFERENTIAL_STICKING = "DIFFERENTIAL_STICKING"
    LOST_CIRCULATION = "LOST_CIRCULATION"
    GAS_KICK = "GAS_KICK"
    MECHANICAL_PACK_OFF = "MECHANICAL_PACK_OFF"
    BIT_BALLING = "BIT_BALLING"
    WELLBORE_INSTABILITY = "WELLBORE_INSTABILITY"
    WASHOUT = "WASHOUT"
    BHA_VIBRATION = "BHA_VIBRATION"

class DDRParsedInterval(BaseModel):
    well_name: str
    report_number: int
    report_date: str
    from_depth_md_m: float = Field(..., description="Top depth of 24h interval")
    to_depth_md_m: float = Field(..., description="Bottom depth of 24h interval")
    tvdss_m: float = Field(..., description="Subsea true vertical depth")
    formation_name: str
    iadc_code: IADCOperationCode
    hazard_detected: Optional[HazardType] = None
    severity: int = Field(default=1, ge=1, le=5)
    npt_hours: float = Field(default=0.0, ge=0.0)
    mud_density_sg: Optional[float] = Field(None, ge=0.8, le=2.5)
    raw_remarks: str = Field(..., description="Original morning remarks text")
    mitigation_action: Optional[str] = Field(None, description="Action taken to cure hazard")
```
