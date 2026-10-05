# 03. Mathematical & Physics Formulations
## Complete Engineering Derivations for eRTMAC-NWIS

---

## 1. 3D Wellbore Trajectory: Minimum Curvature Method (MCM)

The Minimum Curvature Method is the industry standard (SPE / API) algorithm for calculating 3D directional well paths from directional survey stations. It assumes the wellbore trajectory between two consecutive survey stations lies on a circular arc in 3D space.

Given survey station 1 $(MD_1, I_1, A_1)$ and station 2 $(MD_2, I_2, A_2)$:
*   $MD$ = Measured Depth (metres)
*   $I$ = Inclination angle from vertical (radians)
*   $A$ = Azimuth angle from True North (radians)
*   $\Delta MD = MD_2 - MD_1$

### A. Subtended Dogleg Angle ($\beta$)
$$\cos\beta = \cos I_1 \cos I_2 + \sin I_1 \sin I_2 \cos(A_2 - A_1)$$

### B. Ratio Factor ($RF$)
$$RF = \frac{2}{\beta} \tan\left(\frac{\beta}{2}\right) \qquad \left(\text{For } \beta \to 0, \; RF = 1\right)$$

### C. 3D Incremental Displacements
$$\Delta TVD = \frac{\Delta MD}{2} (\cos I_1 + \cos I_2) \cdot RF$$

$$\Delta \text{Northing} = \frac{\Delta MD}{2} (\sin I_1 \cos A_1 + \sin I_2 \cos A_2) \cdot RF$$

$$\Delta \text{Easting} = \frac{\Delta MD}{2} (\sin I_1 \sin A_1 + \sin I_2 \sin A_2) \cdot RF$$

### D. Subsea True Vertical Depth ($TVDSS$)
$$TVDSS = TVD - KB_{\text{elevation}}$$
Where $KB_{\text{elevation}}$ is the Kelly Bushing elevation above Mean Sea Level (AMSL) (typically +112 m in Nahorkatiya).

### E. Dogleg Severity ($DLS$)
$$DLS = \frac{\beta}{\Delta MD} \times 30 \times \left(\frac{180}{\pi}\right) \quad [^\circ / 30\text{ m}]$$

---

## 2. True Stratigraphic Depth (TSD) Dip Normalization

When comparing an active drilling well $A$ with an offset well $B$ across a geological formation characterized by structural dip angle $\theta$ and dip azimuth $\alpha$:

$$\Delta X = X_B - X_A \qquad \Delta Y = Y_B - Y_A$$

The structural vertical shift induced by regional bedding tilt is:
$$\Delta TVDSS_{\text{structural}} = \Delta X \sin\theta \sin\alpha + \Delta Y \sin\theta \cos\alpha$$

The equivalent stratigraphic depth in the active well's reference frame is:
$$TVDSS_{\text{equivalent}} = TVDSS_A + \Delta TVDSS_{\text{structural}}$$

> **Significance:** In the Kumchai thrust belt where dip exceeds 35°, offset wells just 500 m apart exhibit stratigraphic vertical displacements of **80 m to 150 m**. Matching by Measured Depth (MD) or raw TVD compares completely different rock formations. TSD ensures that the system compares identical lithological layers.

---

## 3. Real-Time Mechanical Specific Energy (MSE) — Teale's Law

Mechanical Specific Energy measures the energy required to remove a unit volume of rock. For a drill bit of diameter $D_{\text{bit}}$ (cross-sectional area $A_b = \frac{\pi D_{\text{bit}}^2}{4}$):

$$MSE = \frac{WOB}{A_b} + \frac{120 \pi \cdot RPM \cdot \text{Torque}}{A_b \cdot ROP}$$

Where:
*   $WOB$ = Weight on Bit (lbs)
*   $\text{Torque}$ = Surface / Downhole Torque (ft-lbs)
*   $RPM$ = Rotary speed (revolutions per minute)
*   $ROP$ = Rate of Penetration (ft/hr)
*   $MSE$ is expressed in psi.

### Diagnostic Thresholds:
1.  **Bit Balling Indicator:** $MSE_{\text{live}} > 2.5 \times MSE_{\text{baseline}}$ accompanied by $ROP \to 0$ in Girujan Clay.
2.  **Differential Sticking Precursor:** Steady upward drift in torque component of MSE while $WOB$ remains constant in depleted Tipam Sandstone.
3.  **Mechanical Efficiency:** $\eta = \frac{UCS}{MSE} \times 100\%$. If efficiency drops below 25%, cutter degradation or severe vibration dysfunction is flagged.

---

## 4. Hydrostatic Overbalance & Differential Sticking Physics

The pullout force required to free a drillstring stuck differentially against a permeable mudcake is governed by the Outmans equation:

$$F_{\text{pull}} = A_c \cdot \Delta P \cdot \mu_f$$

Where:
*   $A_c$ = Contact area between drill collars and borehole wall ($A_c = h_{\text{cake}} \cdot L_{\text{collar}} \cdot \sin(\phi)$).
*   $\mu_f$ = Mudcake friction coefficient (typically 0.15 to 0.25).
*   $\Delta P$ = Hydrostatic overbalance pressure:
$$\Delta P = P_{\text{hydrostatic}} - P_{\text{pore}} = 0.052 \times (MW - PP_{\text{pore}}) \times TVD$$

When the drillstring remains stationary during survey connections ($RPM = 0, ROP = 0$) for duration $t > 90\text{ seconds}$ in depleted Tipam Sandstone where $\Delta P > 800\text{ psi}$, $F_{\text{pull}}$ rapidly exceeds the rig's maximum derrick hook load capacity, causing stuck pipe.

---

## 5. Proactive Look-Ahead Hazard Risk Index ($R_H$)

For an active drill bit at current depth $Z_{\text{bit}}$, the system computes a composite risk score for hazard category $H$ over a look-ahead window $\Delta Z = 75\text{ m}$:

$$R_H(Z_{\text{bit}}) = \sum_{w \in \text{Offsets}} \frac{1}{d_{3D}(w)^{\gamma}} \cdot \exp\left( -\frac{(TVDSS_{\text{incident}}(w) - TVDSS_{\text{projected}})^2}{2 \sigma_z^2} \right) \cdot S_{\text{severity}}(w)$$

Where:
*   $d_{3D}(w)$ = 3D Euclidean distance between active bit coordinate $(X_A, Y_A, Z_A)$ and offset trajectory station $(X_w, Y_w, Z_w)$ at target formation horizon.
*   $\gamma = 1.2$ = Spatial distance decay parameter.
*   $\sigma_z = 15\text{ m}$ = Stratigraphic depth tolerance window.
*   $S_{\text{severity}}(w) \in [1, 5]$ = Historical incident severity rating based on recorded NPT hours:
    *   Level 1: Minor seepage / tight hole ($<4\text{ hours NPT}$)
    *   Level 2: Moderate loss / reaming ($4–12\text{ hours NPT}$)
    *   Level 3: Severe loss / pack-off ($12–24\text{ hours NPT}$)
    *   Level 4: Stuck pipe requiring fishing or sidetrack ($24–72\text{ hours NPT}$)
    *   Level 5: Wellbore loss / blowout ($>72\text{ hours NPT}$)

The raw score is normalized to a **0 to 100 Risk Index**:
*   $R_H < 50$: LOW RISK (Normal drilling operations)
*   $50 \le R_H < 75$: MODERATE RISK (Display advisory notice)
*   $75 \le R_H < 85$: HIGH RISK (Trigger Yellow Caution alert; recommend mud weight & rotation limits)
*   $R_H \ge 85$: CRITICAL HAZARD (Trigger Red Emergency alert; require superintendent sign-off)

---

## 6. 3D Wellbore Proximity & Anti-Collision Separation Factor ($SF$)

In congested drilling pads, the Separation Factor ($SF$) evaluates collision risks with nearby existing wellbores:

$$SF = \frac{D_{\text{center-to-center}}}{R_{\text{active\_ellipse}} + R_{\text{offset\_ellipse}}}$$

Where:
*   $D_{\text{center-to-center}}$ = 3D minimum distance between active wellbore and offset wellbore.
*   $R_{\text{active\_ellipse}}, R_{\text{offset\_ellipse}}$ = Semi-major axes of the directional survey positional uncertainty error ellipses (derived via the Wolff & de Wardt error model).
*   **Operational Thresholds:**
    *   $SF > 2.0$: Safe clearance
    *   $1.5 \le SF \le 2.0$: Caution zone (directional driller notified)
    *   $SF < 1.5$: Emergency collision hazard (shut down pumps and verify gyro survey)
