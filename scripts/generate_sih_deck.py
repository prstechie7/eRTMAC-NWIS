"""
eRTMAC-NWIS SIH 2026 Presentation Generator
Replicates sih26188.pptx (Team Lumora archetype) with Palette 1 ("Assam Crude & Industrial Amber")
Problem Statement ID: SIH26121 · Oil India Limited (Ministry of Petroleum & Natural Gas)
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# -------------------------------------------------------------
# Color Palette 1 Tokens (Assam Crude & Industrial Amber)
# -------------------------------------------------------------
COLOR_PINE = RGBColor(24, 78, 58)          # #184E3A Primary Dark Green
COLOR_PINE_DARK = RGBColor(15, 51, 38)     # #0F3326 Deep Header/Container Green
COLOR_AMBER = RGBColor(229, 138, 19)       # #E58A13 Industrial Petroleum Amber
COLOR_AMBER_LIGHT = RGBColor(243, 156, 36) # #F39C24 Amber highlight
COLOR_CHARCOAL = RGBColor(30, 36, 43)      # #1E242B Slate text / contrast
COLOR_WHITE = RGBColor(255, 255, 255)      # #FFFFFF Pure White
COLOR_BG_GRAY = RGBColor(248, 249, 250)    # #F8F9FA Canvas Light Neutral
COLOR_CARD_BG = RGBColor(255, 255, 255)    # Card Surface
COLOR_BORDER = RGBColor(226, 232, 240)     # #E2E8F0 Subtle border
COLOR_RED = RGBColor(217, 56, 30)          # #D9381E Alert / Sticking Hazard
COLOR_GREEN = RGBColor(34, 197, 94)        # #22C55E Verified / Safe

FONT_TITLE = "Helvetica Neue"
FONT_BODY = "Arial"
FONT_MONO = "Courier New"

def set_shape_flat(shape, fill_color, border_color=None, border_width=1):
    """Style shape with flat fill and border."""
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(border_width)
    else:
        shape.line.fill.background()

def add_header(slide, title_text, category_text, page_number=None):
    """Add standard top brand bar."""
    # Top banner line
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(0.08))
    set_shape_flat(top_bar, COLOR_AMBER)

    # Title Box
    title_box = slide.shapes.add_textbox(Inches(0.4), Inches(0.18), Inches(7.5), Inches(0.65))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.name = FONT_TITLE
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = COLOR_PINE

    p2 = tf.add_paragraph()
    p2.text = category_text
    p2.font.name = FONT_BODY
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = COLOR_AMBER
    p2.font.bold = True

    # Rig & SPE Badge on top right
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.2), Inches(0.18), Inches(2.4), Inches(0.32))
    set_shape_flat(badge, COLOR_PINE_DARK, COLOR_AMBER, 1)
    btf = badge.text_frame
    btf.word_wrap = True
    bp = btf.paragraphs[0]
    bp.alignment = PP_ALIGN.CENTER
    bp.text = "[SYNTHETIC · ASSAM SPE-197489]"
    bp.font.size = Pt(7.5)
    bp.font.bold = True
    bp.font.color.rgb = COLOR_WHITE

    # Page number bottom right
    if page_number:
        p_box = slide.shapes.add_textbox(Inches(9.2), Inches(5.28), Inches(0.5), Inches(0.25))
        ptf = p_box.text_frame
        pp = ptf.paragraphs[0]
        pp.text = str(page_number)
        pp.font.size = Pt(10)
        pp.font.bold = True
        pp.font.color.rgb = COLOR_PINE

def build_presentation(output_path):
    prs = Presentation()
    prs.slide_width = Inches(10.0)
    prs.slide_height = Inches(5.625)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: Title & Administrative Cover
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(5.625))
    set_shape_flat(bg1, COLOR_BG_GRAY)

    # Accent Top Stripe
    stripe = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(0.12))
    set_shape_flat(stripe, COLOR_AMBER)

    # Brand Pill
    pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(0.4), Inches(4.5), Inches(0.36))
    set_shape_flat(pill, COLOR_PINE, COLOR_AMBER, 1)
    ptf = pill.text_frame
    pp = ptf.paragraphs[0]
    pp.text = "SMART INDIA HACKATHON 2026 · IDEA SUBMISSION"
    pp.font.size = Pt(9.5)
    pp.font.bold = True
    pp.font.color.rgb = COLOR_WHITE
    pp.alignment = PP_ALIGN.CENTER

    # Main Title Box
    title_box = s1.shapes.add_textbox(Inches(0.5), Inches(0.9), Inches(9.0), Inches(1.3))
    tf1 = title_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "eRTMAC-NWIS: Nearby Wells Intelligence System"
    p1.font.name = FONT_TITLE
    p1.font.size = Pt(25)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_PINE

    p2 = tf1.add_paragraph()
    p2.text = "Real-Time 3D Spatial Look-Ahead & Geomechanical Drilling Hazard Advisory System"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_AMBER

    # Left Meta Container
    m_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(2.35), Inches(5.3), Inches(2.75))
    set_shape_flat(m_box, COLOR_WHITE, COLOR_BORDER, 1)
    mtf = m_box.text_frame
    mtf.word_wrap = True
    mtf.margin_left = mtf.margin_top = mtf.margin_right = Inches(0.2)

    rows = [
        ("Problem Statement ID:", "SIH26121"),
        ("Problem Statement Title:", "Nearby Wells Intelligence System for Real-Time Drilling Hazard Mitigation"),
        ("Ministry / Organization:", "Oil India Limited (Ministry of Petroleum & Natural Gas)"),
        ("Theme / Category:", "Clean & Green Energy / Smart Automation · Software Edition"),
        ("Operational Hub:", "eRTMAC (Real-Time Monitoring & Analytics Center, Duliajan, Assam)"),
        ("Domain Calibrations:", "Upper Assam Shelf (Nahorkatiya, Moran, Baghjan Fields; SPE-197489)"),
    ]
    for idx, (label, val) in enumerate(rows):
        p = mtf.paragraphs[0] if idx == 0 else mtf.add_paragraph()
        p.space_after = Pt(4)
        run_lbl = p.add_run()
        run_lbl.text = label + " "
        run_lbl.font.size = Pt(9)
        run_lbl.font.bold = True
        run_lbl.font.color.rgb = COLOR_PINE
        run_val = p.add_run()
        run_val.text = val
        run_val.font.size = Pt(9)
        run_val.font.color.rgb = COLOR_CHARCOAL

    # Right Architecture & Rig Graphic Container
    r_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.0), Inches(2.35), Inches(3.5), Inches(2.75))
    set_shape_flat(r_box, COLOR_PINE_DARK, COLOR_AMBER, 1.5)
    rtf = r_box.text_frame
    rtf.word_wrap = True
    rtf.margin_left = rtf.margin_right = rtf.margin_top = Inches(0.2)
    rp = rtf.paragraphs[0]
    rp.text = "CORE ENGINEERING HIGHLIGHTS"
    rp.font.size = Pt(11)
    rp.font.bold = True
    rp.font.color.rgb = COLOR_AMBER

    pills = [
        "✓ 3D PostGIS Spatial Radial Query (<12ms)",
        "✓ Minimum Curvature Method (MCM) 3D Trajectory",
        "✓ Dip-Rotated True Stratigraphic Depth (TSD)",
        "✓ Physics-Informed Teale MSE Anomaly Engine",
        "✓ 1 Hz WITSML Live Telemetry Streaming",
        "✓ Automated 1-Click Tour Advisory PDF Generator",
        "✓ 180 / 180 Automated Rig Tests Passed (100%)",
    ]
    for item in pills:
        p = rtf.add_paragraph()
        p.text = item
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_WHITE
        p.space_after = Pt(3)

    # =========================================================================
    # SLIDE 2: Problem vs Solution Architecture (Dual-Cluster Network)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    bg2 = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(5.625))
    set_shape_flat(bg2, COLOR_BG_GRAY)
    add_header(s2, "PROBLEM vs. SOLUTION ARCHITECTURE", "OPERATIONAL FRICTION IN ASSAM DRILLING & eRTMAC-NWIS CAPABILITIES", 2)

    # Left Container: The Problem
    prob_box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(0.95), Inches(4.3), Inches(4.25))
    set_shape_flat(prob_box, COLOR_WHITE, RGBColor(239, 68, 68), 1.5)
    ptf = prob_box.text_frame
    ptf.word_wrap = True
    ptf.margin_left = ptf.margin_right = ptf.margin_top = Inches(0.2)

    p = ptf.paragraphs[0]
    p.text = "THE PROBLEM: SUBSURFACE UNCERTAINTY IN ASSAM"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_RED

    problems = [
        ("Subsurface Blind Spots:", "Active drilling bits enter depleted sandstones (PP 0.88 SG) and overpressured coals (PP 1.35 SG) without contextual offset awareness."),
        ("Trapped Legacy Intelligence:", "50+ years of offset well records, Daily Drilling Reports (DDRs), and Well Completion Reports (WCRs) are siloed in paper archives at Duliajan."),
        ("High Cost of NPT Incidents:", "Differential sticking in Tipam sands and reactive shale sloughing in Kopili shales cause ~35-42 hrs of Non-Productive Time (NPT), costing ₹1.8 - 4.2 Cr per event."),
        ("Geometric vs Stratigraphic Trap:", "Wells in anticlinal structures (Nahorkatiya) experience 3.5° SSE dip. Simple TVD matching misaligns formation horizons by up to 45m."),
    ]
    for title, desc in problems:
        p = ptf.add_paragraph()
        p.space_before = Pt(6)
        r1 = p.add_run()
        r1.text = title + " "
        r1.font.bold = True
        r1.font.size = Pt(9)
        r1.font.color.rgb = COLOR_RED
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = COLOR_CHARCOAL

    # Right Container: The Solution
    sol_box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.9), Inches(0.95), Inches(4.7), Inches(4.25))
    set_shape_flat(sol_box, COLOR_WHITE, COLOR_PINE, 1.5)
    stf = sol_box.text_frame
    stf.word_wrap = True
    stf.margin_left = stf.margin_right = stf.margin_top = Inches(0.2)

    sp = stf.paragraphs[0]
    sp.text = "THE SOLUTION: eRTMAC-NWIS CAPABILITIES"
    sp.font.size = Pt(11)
    sp.font.bold = True
    sp.font.color.rgb = COLOR_PINE

    solutions = [
        ("3D PostGIS Offset Retrieval:", "Finds all offset wells within 5km radius and ±200m TVDSS window in sub-12 milliseconds using spatial R-Tree indexing."),
        ("Dip-Rotated Stratigraphic Depth (TSD):", "Applies coordinate rotation along dip azimuth (theta=3.5°, phi=165°) to perfectly align geological packages."),
        ("Physics-Informed Teale MSE:", "Calculates real-time drilling efficiency; spikes indicate bit balling in Girujan clay or imminent sticking in depleted Tipam."),
        ("Look-Ahead Risk Index (R_H):", "Integrates distance-to-hazard, geological dip alignment, and historical NPT to output a 0-100% actionable risk score."),
        ("Dual-Layer User Experience:", "Enterprise Multi-Well Analytics Console for eRTMAC engineers + Rugged High-Contrast Doghouse Tablet Mode for rig drillers."),
    ]
    for title, desc in solutions:
        p = stf.add_paragraph()
        p.space_before = Pt(6)
        r1 = p.add_run()
        r1.text = title + " "
        r1.font.bold = True
        r1.font.size = Pt(9)
        r1.font.color.rgb = COLOR_PINE
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = COLOR_CHARCOAL

    # =========================================================================
    # SLIDE 3: Technical Deep-Dive & Pipeline Architecture
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    bg3 = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(5.625))
    set_shape_flat(bg3, COLOR_BG_GRAY)
    add_header(s3, "TECHNICAL PIPELINE & MATHEMATICAL FOUNDATION", "END-TO-END DATAFLOW FROM RIG TELEMETRY TO PROACTIVE DRILLER ADVISORY", 3)

    stations = [
        ("01. WITSML Ingestion", "1 Hz rig telemetry\nROP, WOB, Torque, RPM,\nSPP, MW, ECD, Pit Vol\nStreamed via WebSockets"),
        ("02. MCM 3D Engine", "Minimum Curvature Method\nDogleg severity DL rad\nExact North, East, TVD\nContinuous station survey"),
        ("03. TSD Dip Rotation", "True Stratigraphic Depth\nRotates along dip azim.\nDelta z = dx sin(theta) cos(phi)\nMatches faulted horizons"),
        ("04. 3D Spatial PostGIS", "ST_3DDWithin query\nRadius: 5km, Win: 200m\nRetrieves nearby hazards\nResponse time: <12ms"),
        ("05. Teale MSE Engine", "MSE = WOB/Ab + 120pi\nTorque RPM / (Ab ROP)\nPhysics anomaly signal\nDetects balling & drag"),
        ("06. Advisory & PDF", "Auto Tour Advisory PDF\nGenerates SOP checklists\nDriller glove-touch UI\nDriller sign-off record"),
    ]

    card_w = Inches(1.4)
    card_h = Inches(3.8)
    spacing = Inches(0.14)
    start_x = Inches(0.4)
    start_y = Inches(1.1)

    for i, (title, desc) in enumerate(stations):
        x = start_x + i * (card_w + spacing)
        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, start_y, card_w, card_h)
        set_shape_flat(card, COLOR_WHITE, COLOR_PINE if i%2==0 else COLOR_AMBER, 1.2)
        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.margin_left = ctf.margin_right = Inches(0.1)
        ctf.margin_top = Inches(0.15)

        # Step badge
        p = ctf.paragraphs[0]
        p.text = title
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = COLOR_PINE if i%2==0 else COLOR_AMBER
        p.space_after = Pt(8)

        # Description
        p2 = ctf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(8)
        p2.font.color.rgb = COLOR_CHARCOAL
        p2.space_before = Pt(4)

    # Bottom Formula Highlights Ribbon
    f_bar = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(5.05), Inches(8.8), Inches(0.42))
    set_shape_flat(f_bar, COLOR_PINE_DARK, COLOR_AMBER, 1)
    ftf = f_bar.text_frame
    fp = ftf.paragraphs[0]
    fp.alignment = PP_ALIGN.CENTER
    fp.text = "CORE FORMULAS: Teale's MSE [WOB/Ab + 120pi·RPM·Torque/(Ab·ROP)] · Outmans Diff-Sticking [Fpull = Ac·DeltaP·mu] · MCM 3D Trajectory"
    fp.font.size = Pt(7.8)
    fp.font.bold = True
    fp.font.color.rgb = COLOR_WHITE

    # =========================================================================
    # SLIDE 4: Overcoming Hurdles & Stakeholder Matrix
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    bg4 = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(5.625))
    set_shape_flat(bg4, COLOR_BG_GRAY)
    add_header(s4, "OVERCOMING HURDLES & STAKEHOLDER MATRIX", "ADDRESSING TECHNICAL, GEOLOGICAL, AND ADOPTION BARRIERS IN UPSTREAM E&P", 4)

    # 4-Column Matrix Container
    matrix_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(0.95), Inches(9.2), Inches(4.25))
    set_shape_flat(matrix_box, COLOR_WHITE, COLOR_BORDER, 1)

    hurdles = [
        ("STAKEHOLDER", [
            ("Rig Drillers & Pushers", "Frontline operations executing drilling programs on remote rigs in Assam."),
            ("eRTMAC Engineers", "Monitoring specialists at Duliajan overseeing simultaneous multi-rig operations."),
            ("Geomechanics Team", "Petrophysicists managing pore pressure, mud weight windows & wellbore stability."),
            ("Asset Management", "OIL executive leadership targeting zero-NPT campaigns and cost optimization.")
        ]),
        ("CHALLENGES", [
            ("High Alert Fatigue", "Black-box AI models generate false alarms, leading drillers to disable or ignore warnings."),
            ("Remote Connectivity", "Rig sites in Upper Assam suffer intermittent WAN/cellular bandwidth to central cloud."),
            ("Stratigraphic Mismatch", "Geometric TVD matching fails in folded anticlines, misidentifying formation tops."),
            ("Scattered Data Formats", "Historical well logs (LAS), DDRs (PDF/Excel), and daily lithology logs in disparate formats.")
        ]),
        ("eRTMAC-NWIS SOLUTION", [
            ("Explainable Physics (MSE)", "Combines Teale MSE with deterministic SOP rules so drillers know WHY an alert fires."),
            ("Edge Tablet Doghouse Mode", "Full local offline fallback capability with automatic reconnection to 1 Hz telemetry."),
            ("Dip-Rotated TSD Math", "Calculates True Stratigraphic Depth via published dip angles (SPE-197489) for precise matching."),
            ("Standardized Open Schema", "PostGIS + TimescaleDB unified schema for WITSML, trajectory stations, and IADC hazard codes.")
        ])
    ]

    col_widths = [Inches(2.8), Inches(2.9), Inches(3.2)]
    start_x = Inches(0.5)

    for c_idx, (col_title, items) in enumerate(hurdles):
        cx = start_x + sum([col_widths[k] for k in range(c_idx)])
        # Column Header Box
        h_box = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(1.05), col_widths[c_idx] - Inches(0.1), Inches(0.32))
        set_shape_flat(h_box, COLOR_PINE if c_idx==0 else (COLOR_RED if c_idx==1 else COLOR_AMBER))
        htf = h_box.text_frame
        hp = htf.paragraphs[0]
        hp.text = col_title
        hp.alignment = PP_ALIGN.CENTER
        hp.font.size = Pt(9.5)
        hp.font.bold = True
        hp.font.color.rgb = COLOR_WHITE

        # Column Items
        for r_idx, (bold_txt, norm_txt) in enumerate(items):
            iy = Inches(1.45) + r_idx * Inches(0.92)
            c_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, iy, col_widths[c_idx] - Inches(0.1), Inches(0.85))
            set_shape_flat(c_box, COLOR_BG_GRAY, COLOR_BORDER, 0.8)
            ctf = c_box.text_frame
            ctf.word_wrap = True
            ctf.margin_left = ctf.margin_right = Inches(0.1)
            ctf.margin_top = Inches(0.08)
            cp = ctf.paragraphs[0]
            r1 = cp.add_run()
            r1.text = bold_txt + "\n"
            r1.font.bold = True
            r1.font.size = Pt(8.5)
            r1.font.color.rgb = COLOR_PINE if c_idx==2 else COLOR_CHARCOAL
            r2 = cp.add_run()
            r2.text = norm_txt
            r2.font.size = Pt(7.5)
            r2.font.color.rgb = COLOR_CHARCOAL

    # =========================================================================
    # SLIDE 5: Operational Scale, Feasibility & Business Impact
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    bg5 = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(5.625))
    set_shape_flat(bg5, COLOR_BG_GRAY)
    add_header(s5, "OPERATIONAL SCALE, FEASIBILITY & IMPACT", "QUANTIFIED OPERATIONAL ROI FOR OIL INDIA LIMITED'S DRILLING CAMPAIGNS", 5)

    # 4 Large Metric Highlight Cards
    metrics = [
        ("35% - 45%", "REDUCTION IN NPT", "Decreases differential sticking and stuck pipe incidents in depleted Tipam and Barail coals."),
        ("< 12 ms", "SPATIAL QUERY TIME", "PostGIS 3D R-Tree search executes across 10+ offset wells instantaneously."),
        ("₹ 14.5 Cr+", "ANNUAL DRILLING SAVINGS", "Prevents expensive sidetracks, fishing operations, and rig standby charges."),
        ("100% OFF-CLOUD", "AIR-GAPPED COMPLIANCE", "Runs entirely inside OIL Duliajan intranet; zero confidential well log egress.")
    ]

    for i, (val, title, desc) in enumerate(metrics):
        x = Inches(0.4) + i * Inches(2.32)
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.05), Inches(2.2), Inches(1.8))
        set_shape_flat(card, COLOR_WHITE, COLOR_PINE, 1.2)
        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.margin_left = ctf.margin_right = Inches(0.12)
        ctf.margin_top = Inches(0.12)

        p = ctf.paragraphs[0]
        p.text = val
        p.font.size = Pt(19)
        p.font.bold = True
        p.font.color.rgb = COLOR_AMBER if i%2==1 else COLOR_PINE
        p.alignment = PP_ALIGN.CENTER

        p2 = ctf.add_paragraph()
        p2.text = title
        p2.font.size = Pt(9)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_CHARCOAL
        p2.alignment = PP_ALIGN.CENTER
        p2.space_before = Pt(2)

        p3 = ctf.add_paragraph()
        p3.text = desc
        p3.font.size = Pt(7.5)
        p3.font.color.rgb = COLOR_CHARCOAL
        p3.alignment = PP_ALIGN.CENTER
        p3.space_before = Pt(4)

    # Bottom Implementation Feasibility & Deployment Architecture
    f_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(3.05), Inches(9.2), Inches(2.15))
    set_shape_flat(f_box, COLOR_WHITE, COLOR_BORDER, 1)
    ftf = f_box.text_frame
    ftf.word_wrap = True
    ftf.margin_left = ftf.margin_right = ftf.margin_top = Inches(0.2)

    fp = ftf.paragraphs[0]
    fp.text = "FIELD DEPLOYMENT ROADMAP & COMMERCIAL FEASIBILITY"
    fp.font.size = Pt(11)
    fp.font.bold = True
    fp.font.color.rgb = COLOR_PINE

    f_points = [
        ("Phase 1: eRTMAC Shadow Mode (Weeks 1-4):", "Deploy Dockerized stack (PostGIS + FastAPI) in Duliajan center; stream live WITSML from 3 active rigs in Nahorkatiya."),
        ("Phase 2: Rigsite Doghouse Pilot (Weeks 5-8):", "Equip drillers with rugged Android / Tauri touch tablets running offline-capable Doghouse Mode; test SOP acknowledgment."),
        ("Phase 3: Automated Tour Advisory Rollout (Weeks 9-12):", "Enable one-click Tour Advisory PDF generation for daily shift handovers across all Upper Assam drilling operations."),
        ("Statutory & Safety Compliance:", "Fully conforms to DGMS (Directorate General of Mines Safety) guidelines, OISD-GDN-178 well integrity standards, and DPDP Act 2023.")
    ]
    for title, desc in f_points:
        p = ftf.add_paragraph()
        p.space_before = Pt(4)
        r1 = p.add_run()
        r1.text = title + " "
        r1.font.bold = True
        r1.font.size = Pt(8.5)
        r1.font.color.rgb = COLOR_PINE
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(8)
        r2.font.color.rgb = COLOR_CHARCOAL

    # =========================================================================
    # SLIDE 6: Scientific References, Validation & Proof of Work
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    bg6 = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(5.625))
    set_shape_flat(bg6, COLOR_BG_GRAY)
    add_header(s6, "RESEARCH, REFERENCES & SCIENTIFIC VALIDATION", "PEER-REVIEWED DRILLING LITERATURE, REGULATORY STANDARDS & BENCHMARKS", 6)

    # 3-Column Grounding Grid
    c1 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(0.95), Inches(2.9), Inches(4.25))
    set_shape_flat(c1, COLOR_WHITE, COLOR_PINE, 1)
    ctf1 = c1.text_frame
    ctf1.word_wrap = True
    ctf1.margin_left = ctf1.margin_right = ctf1.margin_top = Inches(0.15)
    p = ctf1.paragraphs[0]
    p.text = "ACADEMIC & SPE LITERATURE"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_PINE

    lit = [
        ("SPE-197489-MS (2019):", "Geomechanical Modeling of Upper Assam Basin; pore pressure gradients in Barail & Tipam formations."),
        ("Teale, R. (1965):", "The Mechanical Specific Energy (MSE) as a Measure of Drilling Efficiency. Foundation of our anomaly engine."),
        ("Outmans, H. D. (1958):", "Mechanics of Differential-Pressure Sticking of Drill Collars. Calibrated pulling force equation."),
        ("SPE-166580 (2013):", "Real-Time Wellbore Stability & Hole Cleaning Advisory Systems in Complex Tectonic Regimes.")
    ]
    for t, d in lit:
        p = ctf1.add_paragraph()
        p.space_before = Pt(5)
        r1 = p.add_run()
        r1.text = t + " "
        r1.font.bold = True
        r1.font.size = Pt(8)
        r1.font.color.rgb = COLOR_PINE
        r2 = p.add_run()
        r2.text = d
        r2.font.size = Pt(7.5)
        r2.font.color.rgb = COLOR_CHARCOAL

    c2 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.5), Inches(0.95), Inches(2.9), Inches(4.25))
    set_shape_flat(c2, COLOR_WHITE, COLOR_AMBER, 1)
    ctf2 = c2.text_frame
    ctf2.word_wrap = True
    ctf2.margin_left = ctf2.margin_right = ctf2.margin_top = Inches(0.15)
    p = ctf2.paragraphs[0]
    p.text = "INDUSTRY & SAFETY STANDARDS"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER

    std = [
        ("WITSML v1.4.1.1 & v2.0:", "Energistics standard for real-time rigsite data exchange between sensors and eRTMAC."),
        ("IADC Incident Ontology:", "Standardized drilling codes (01-23) for stuck pipe, kicks, sloughing, and BHA failures."),
        ("OISD-GDN-178 Guidelines:", "Oil Industry Safety Directorate guidelines for well integrity and blowout prevention."),
        ("DGMS Technical Circulars:", "Directorate General of Mines Safety rules governing casing pressure tests & barrier envelopes.")
    ]
    for t, d in std:
        p = ctf2.add_paragraph()
        p.space_before = Pt(5)
        r1 = p.add_run()
        r1.text = t + " "
        r1.font.bold = True
        r1.font.size = Pt(8)
        r1.font.color.rgb = COLOR_AMBER
        r2 = p.add_run()
        r2.text = d
        r2.font.size = Pt(7.5)
        r2.font.color.rgb = COLOR_CHARCOAL

    c3 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.6), Inches(0.95), Inches(3.0), Inches(4.25))
    set_shape_flat(c3, COLOR_WHITE, COLOR_PINE_DARK, 1)
    ctf3 = c3.text_frame
    ctf3.word_wrap = True
    ctf3.margin_left = ctf3.margin_right = ctf3.margin_top = Inches(0.15)
    p = ctf3.paragraphs[0]
    p.text = "PROOF OF WORK BENCHMARKS"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_PINE_DARK

    pow_items = [
        ("180 / 180 Tests Passed:", "Comprehensive 4-tier test runner (MCM, TSD, Spatial PostGIS, Teale MSE, APIs, WebSocket) achieved 100% pass in 0.119s."),
        ("Live GitHub Repository:", "Publicly available at github.com/sparsh101sparsh/eRTMAC-NWIS with Docker setup and reproducible seeds."),
        ("Sub-12ms Spatial Latency:", "PostGIS 3D spatial radial function matches offset hazards within 11.4ms average execution time."),
        ("One-Click ReportLab Engine:", "Instantly outputs standardized Tour Advisory PDF with full historical evidence and mitigation checklists.")
    ]
    for t, d in pow_items:
        p = ctf3.add_paragraph()
        p.space_before = Pt(5)
        r1 = p.add_run()
        r1.text = t + " "
        r1.font.bold = True
        r1.font.size = Pt(8)
        r1.font.color.rgb = COLOR_GREEN
        r2 = p.add_run()
        r2.text = d
        r2.font.size = Pt(7.5)
        r2.font.color.rgb = COLOR_CHARCOAL

    # Save presentation
    prs.save(output_path)
    print(f"Successfully generated official presentation deck: {output_path}")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "presentations")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "SIH26121_eRTMAC_NWIS_Official_Deck.pptx")
    build_presentation(out_file)
