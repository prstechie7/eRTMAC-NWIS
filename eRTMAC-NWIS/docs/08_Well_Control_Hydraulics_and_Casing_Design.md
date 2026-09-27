# 08. Well Control, Hydraulics & Casing Design Reference
## Engineering Formulations & Operational Standards for eRTMAC-NWIS

---

## 1. Advanced Annular Hydraulics & Equivalent Circulating Density (ECD)

Downhole Equivalent Circulating Density (ECD) is the effective density exerted by the drilling fluid against the formation while circulating. In high-risk formations with narrow mud weight windows (such as the Kopili shales and depleted Tipam sandstones in Upper Assam), unmanaged ECD spikes induce formation fracturing and catastrophic mud losses.

### 1.1 Fundamental ECD Relationship
$$\text{ECD} = \text{MW}_{\text{static}} + \frac{\Delta P_{\text{annular}}}{0.052 \times TVD} \quad [\text{ppg}]$$

$$\text{ECD} = \text{MW}_{\text{static}} + \frac{\Delta P_{\text{annular}}}{0.0981 \times TVD} \quad [\text{SG EMW}]$$

Where:
*   $\text{MW}_{\text{static}}$ = Static surface mud density (SG or ppg)
*   $\Delta P_{\text{annular}}$ = Cumulative Annular Pressure Loss (APL) from bit to surface (bar or psi)
*   $TVD$ = True Vertical Depth (metres or feet)

### 1.2 Herschel-Bulkley (Yield Power Law - YPL) Model
While Newtonian and Bingham Plastic models oversimplify fluid shear at low annular shear rates, modern drilling fluids follow the **Herschel-Bulkley model** (API RP 13D standard):

$$\tau = \tau_0 + K \cdot \dot{\gamma}^n$$

Where:
*   $\tau_0$ = Yield stress ($\text{lb}/100\,\text{ft}^2$) — forces required to initiate flow
*   $K$ = Consistency index ($\text{lb}\cdot\text{s}^n/100\,\text{ft}^2$)
*   $\dot{\gamma}$ = Annular shear rate ($\text{s}^{-1}$)
*   $n$ = Flow behavior index (dimensionless; $n < 1$ indicates shear-thinning pseudoplastic behavior)

From standard Fann 35 viscometer dial readings ($\theta_{600}, \theta_{300}, \theta_6, \theta_3$):
$$\tau_0 = 2\theta_3 - \theta_6$$
$$n = 3.322 \log\left(\frac{\theta_{600} - \tau_0}{\theta_{300} - \tau_0}\right)$$
$$K = \frac{\theta_{300} - \tau_0}{511^n}$$

### 1.3 Annular Pressure Loss ($APL$) in Concentric & Eccentric Annulus
For annular flow between borehole diameter $D_h$ and drill pipe outside diameter $D_p$:
$$\text{Mean Annular Velocity } v_a = \frac{Q}{2.448 (D_h^2 - D_p^2)} \quad [\text{ft/min}]$$

The effective annular shear rate:
$$\dot{\gamma}_a = \left(\frac{2n + 1}{3n}\right) \left(\frac{12 v_a}{D_h - D_p}\right)$$

For laminar flow, the annular frictional pressure gradient is:
$$\frac{dP}{dL} = \left(\frac{4 K}{D_h - D_p}\right) \left[\left(\frac{2n + 1}{3n}\right)\left(\frac{12 v_a}{D_h - D_p}\right)\right]^n + \frac{4 \tau_0}{D_h - D_p}$$

**Eccentricity Correction Factor ($C_e$):** In directional and horizontal wells where drill pipe lies against the low side of the hole:
$$C_e = 1 - 0.072 \left(\frac{e}{n}\right) \left(\frac{D_p}{D_h}\right)^{0.84} - 1.5 e^2 \sqrt{n} \left(\frac{D_p}{D_h}\right)^{0.18} + 0.96 e^3 \sqrt{n} \left(\frac{D_p}{D_h}\right)^{0.14}$$
Where $e$ is pipe standoff eccentricity ($e = 0$ is centered; $e = 1$ is fully touching wall).

---

## 2. Well Control Mechanics & Kick Tolerance ($KT$)

A primary lesson from the **Baghjan-5 blowout** was the absence of automated, dynamic kick tolerance calculations during tripping and drilling operations.

### 2.1 Gas Influx Mechanics & Expansion
When formation pore pressure exceeds bottomhole hydrostatic pressure ($P_{\text{pore}} > BHP$), formation gas enters the wellbore. Under the real-gas law:
$$\frac{P_1 V_1}{Z_1 T_1} = \frac{P_2 V_2}{Z_2 T_2}$$
As the gas bubble migrates upward, hydrostatic head above the gas decreases, causing the gas to expand exponentially. If the well is not shut in early, bottomhole pressure rapidly drops, allowing secondary influx.

### 2.2 Maximum Allowable Annular Surface Pressure (MAASP)
The absolute maximum shut-in casing pressure allowed before fracturing the rock at the weakest point—the previous casing shoe:
$$\text{MAASP} = (\text{LOT} - \text{MW}_{\text{active}}) \times 0.052 \times TVD_{\text{shoe}} \quad [\text{psi}]$$
Where:
*   $\text{LOT}$ = Leak-Off Test equivalent mud weight at casing shoe (ppg)
*   $\text{MW}_{\text{active}}$ = Current active mud density in the hole (ppg)
*   $TVD_{\text{shoe}}$ = True Vertical Depth of the casing shoe (ft)

### 2.3 Kick Tolerance Calculation ($KT$)
Kick tolerance is the maximum gas influx volume (barrels) or intensity (ppg) that can be safely shut in and circulated out without exceeding the casing shoe fracture gradient:

$$\text{Intensity Limit: } KT_{\text{intensity}} = \text{LOT}_{\text{shoe}} - \left[\text{MW} + \frac{\text{SICP}}{0.052 \times TVD_{\text{shoe}}}\right] \quad [\text{ppg}]$$

$$\text{Maximum Influx Height: } H_{\text{influx}} = \frac{(\text{LOT} - \text{MW}) \times 0.052 \times TVD_{\text{shoe}} - \text{SICP}}{0.052 \times (\text{MW} - \rho_{\text{gas}})} \quad [\text{ft}]$$

$$\text{Maximum Kick Volume: } V_{\text{kick\_max}} = H_{\text{influx}} \times C_{\text{annular\_bit}} \quad [\text{bbls}]$$

Where $C_{\text{annular\_bit}}$ is the annular capacity between the bottomhole assembly (BHA) and open hole (bbls/ft).

---

## 3. Casing Program Design for Nahorkatiya & Moran Deep Wells

In Oil India Limited's operational theater, casing shoes are selected based on the pore pressure ($PP$) and fracture gradient ($FG$) envelope to isolate hazardous thief zones before entering overpressured sequences:

```
+──────────────────────────┬─────────────┬──────────────┬──────────────────────────────────────────────────────+
| Casing String            | OD (Inches) | Shoe TVD (m) | Geological Isolation Target & Engineering Purpose    |
+──────────────────────────┼─────────────┼──────────────┼──────────────────────────────────────────────────────+
| 1. Conductor Casing      | 20"         | 100 – 150 m  | Isolates unconsolidated surface gravels & boulders    |
|                          |             |              | in Dihing Alluvium; supports cellar structure.       |
+──────────────────────────┼─────────────┼──────────────┼──────────────────────────────────────────────────────+
| 2. Surface Casing        | 13-3/8"     | 800 – 1,150m | Set at base of Dupi Tila / Namsang sandstones;        |
|                          |             |              | isolates shallow potable aquifers; anchors BOP stack.|
+──────────────────────────┼─────────────┼──────────────┼──────────────────────────────────────────────────────+
| 3. Intermediate Casing   | 9-5/8"      | 2,800–2,950m | CRITICAL SEAT: Set at base of Tipam Sandstone;        |
|                          |             |              | isolates depleted Tipam sands (0.88–1.00 SG EMW)     |
|                          |             |              | before penetrating overpressured Barail coals.       |
+──────────────────────────┼─────────────┼──────────────┼──────────────────────────────────────────────────────+
| 4. Production Liner      | 7"          | 3,800–4,200m | Covers Barail gas sands & Kopili overpressured       |
|                          |             |              | reactive shales (1.45–1.58 SG EMW); lands in Sylhet. |
+──────────────────────────┼─────────────┼──────────────┼──────────────────────────────────────────────────────+
| 5. Drilling Liner / Open | 4-1/2" / 5" | 4,400–4,600m | Completes deep Sylhet/Therria limestone reservoir or |
|    Hole Completion       |             | (TD)         | fractured Precambrian basement play.                 |
+──────────────────────────┴─────────────┴──────────────┴──────────────────────────────────────────────────────+
```

> **The Casing Seat Rule of Thumb:** If the intermediate casing is set too shallow (e.g. at 2,400m inside the Tipam sand), drilling into the Barail Coal-Shale overpressure at 2,950m requires raising mud weight to 1.35 SG. This 1.35 SG mud will instantly fracture the exposed Tipam sands above, causing massive underground blowout / cross-flow losses! eRTMAC-NWIS automatically checks offset casing seats to prevent this exact design error.

---

## 4. IADC Drill Bit Dull Grading System (8-Character Taxonomy)

When digitizing legacy Well Completion Reports (WCRs) and bit records, NWIS parses and validates the standard 8-character IADC dull grading code:

$$\mathbf{[1]} \; \mathbf{[2]} \; \mathbf{[3]} \; \mathbf{[4]} \; \mathbf{[5]} \; \mathbf{[6]} \; \mathbf{[7]} \; \mathbf{[8]}$$

```
+───────┬───────────────────────────────┬──────────────────────────────────────────────────────────────+
| Pos   | Characteristic                | Permissible Industry Values / Meaning                        |
+───────┼───────────────────────────────┼──────────────────────────────────────────────────────────────+
| **1** | Inner Cutting Structure       | 0–8 scale (0 = no wear; 8 = 100% cutting structure lost)     |
| **2** | Outer Cutting Structure       | 0–8 scale                                                    |
| **3** | Dull Characteristics          | BC (Broken Cone), BF (Bond Failure), BT (Broken Teeth/PDC),  |
|       |                               | CC (Cracked Cone), CI (Cone Interference), CT (Chipped Teeth),|
|       |                               | ER (Erosion), HC (Heat Checking), JD (Junk Damage),          |
|       |                               | NO (No Dull), PN (Plugged Nozzle), RO (Ring Out),            |
|       |                               | SS (Self-Sharpening), TR (Tracking), WO (Washed Out Bit)     |
| **4** | Location                      | N (Nose), M (Middle), G (Gauge), S (Shoulder),               |
|       |                               | C (Cone), A (All areas)                                      |
| **5** | Bearings / Seals              | X (Fixed cutter / PDC); 0–8 (Roller cone bearing life used)  |
| **6** | Gauge Wear                    | I (In Gauge); or fractions of an inch out of gauge (1/16")   |
| **7** | Other Dull Characteristics     | Secondary wear mechanism (same codes as position 3)          |
| **8** | Reason Pulled                 | BHA (Change BHA), DMF (Downhole Motor Failure),               |
|       |                               | DP (Drill Plug), DSF (Drill String Failure),                  |
|       |                               | DTF (Downhole Tool Failure), LOG (Run Well Logs),             |
|       |                               | PR (Penetration Rate Drop), RIG (Rig Repair),                 |
|       |                               | TD (Total Depth reached), TQ (Torque spike), TW (Twist-off)  |
+───────┴───────────────────────────────┴──────────────────────────────────────────────────────────────+
```

*Example:* `1 - 2 - CT - S - X - I - NO - PR` represents a PDC bit with minor inner/outer tooth wear, chipped teeth on the shoulder, fixed cutters, in gauge, pulled due to penetration rate drop.
