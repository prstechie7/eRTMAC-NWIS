"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldAlert, Activity, Gauge, Sliders, AlertTriangle,
  History, CheckCircle2, ChevronRight, HelpCircle, CornerDownRight, MessageSquare
} from "lucide-react";

interface KickData {
  state: string;
  risk_level: string;
  confidence_pct: number;
  triggered_indicators_count: string;
  flow_imbalance_pct: number;
  pit_gain_rate_bblhr: number;
  spp_deviation_pct: number;
  gas_increase_pct: number;
  mandatory_action: string;
  engineer_review_required: boolean;
}

interface PressureWindowData {
  depth_md_m: number;
  pore_pressure_sg: number;
  fracture_gradient_sg: number;
  current_ecd_sg: number;
  ecd_to_frac_margin_sg: number;
  ecd_to_pp_margin_sg: number;
  status: string;
}

interface HoleCleaningData {
  hole_cleaning_index: number;
  status: string;
  annular_velocity_fpm: number;
  required_velocity_fpm: number;
  cuttings_bed_risk: string;
  packoff_risk: string;
}

interface StuckPipeData {
  primary_mechanism: string;
  overall_stuck_pipe_risk: string;
  mechanism_breakdown: {
    differential_sticking_pct: number;
    pack_off_cuttings_bed_pct: number;
    wellbore_instability_pct: number;
    keyseat_geometry_pct: number;
  };
  evidence: string[];
  historical_analog: {
    well_name: string;
    depth_interval_m: string;
    event: string;
    npt_hours: number;
    source_document: string;
  };
}

interface WhatHappenedEvent {
  event_id: string;
  well_name: string;
  surface_distance_m: number;
  tsd_difference_m: number;
  depth_start_m: number;
  depth_end_m: number;
  formation_name: string;
  event_type: string;
  severity: number;
  npt_hours: number;
  root_cause: string;
  mitigation_action: string;
  source_document: string;
}

export const EngineeringConsole: React.FC<{ activeDepthMd?: number }> = ({ activeDepthMd = 2413.0 }) => {
  const [subTab, setSubTab] = useState<"well-control" | "hole-cleaning" | "stuck-pipe" | "what-happened" | "what-if">("well-control");

  // State for sub-modules
  const [kick, setKick] = useState<KickData | null>(null);
  const [pw, setPw] = useState<PressureWindowData | null>(null);
  const [hci, setHci] = useState<HoleCleaningData | null>(null);
  const [sp, setSp] = useState<StuckPipeData | null>(null);
  const [historicalEvents, setHistoricalEvents] = useState<WhatHappenedEvent[]>([]);

  // What-If sliders
  const [mwInput, setMwInput] = useState<number>(1.12);
  const [flowInput, setFlowInput] = useState<number>(600);
  const [rpmInput, setRpmInput] = useState<number>(100);
  const [whatIfResult, setWhatIfResult] = useState<any>(null);

  // Human Feedback
  const [feedbackAlertId, setFeedbackAlertId] = useState<string>("ALT-NHK05-2413");
  const [feedbackSent, setFeedbackSent] = useState<string | null>(null);

  // Load live engineering data
  useEffect(() => {
    fetch("http://localhost:8000/api/v1/engineering/kick-detection?flow_in_gpm=600&flow_out_gpm=628&pit_gain_rate_bblhr=2.1&spp_psi=2720&spp_baseline_psi=2950&gas_pct=3.1&gas_baseline_pct=1.5")
      .then((r) => r.json())
      .then((d) => setKick(d))
      .catch(() => {});

    fetch("http://localhost:8000/api/v1/engineering/pressure-window?depth_md_m=2410&current_ecd_sg=1.71&pore_pressure_sg=1.49&fracture_gradient_sg=1.83")
      .then((r) => r.json())
      .then((d) => setPw(d))
      .catch(() => {});

    fetch("http://localhost:8000/api/v1/engineering/hole-cleaning?rop_mhr=22&flow_rate_gpm=580&rpm=85&inclination_deg=28")
      .then((r) => r.json())
      .then((d) => setHci(d))
      .catch(() => {});

    fetch("http://localhost:8000/api/v1/engineering/stuck-pipe-mechanism?overbalance_psi=1120&stationary_time_min=45&torque_residual_pct=24")
      .then((r) => r.json())
      .then((d) => setSp(d))
      .catch(() => {});

    fetch(`http://localhost:8000/api/v1/knowledge/what-happened-here?depth_md_m=${activeDepthMd}`)
      .then((r) => r.json())
      .then((d) => setHistoricalEvents(d.historical_analogs || []))
      .catch(() => {});
  }, [activeDepthMd]);

  // Recalculate What-If scenario
  const handleWhatIfRun = () => {
    fetch("http://localhost:8000/api/v1/engineering/what-if", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        current_mw_sg: 1.16,
        current_flow_gpm: 640.0,
        current_rpm: 95.0,
        scenario_mw_sg: mwInput,
        scenario_flow_gpm: flowInput,
        scenario_rpm: rpmInput,
        pore_pressure_sg: 0.92,
        fracture_gradient_sg: 1.82
      })
    })
      .then((r) => r.json())
      .then((d) => setWhatIfResult(d))
      .catch(() => {});
  };

  useEffect(() => {
    handleWhatIfRun();
  }, [mwInput, flowInput, rpmInput]);

  const sendFeedback = (verdict: string) => {
    fetch(`http://localhost:8000/api/v1/alerts/${feedbackAlertId}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        verdict,
        engineer_id: "Rig-Superintendent-OIL",
        comments: `Reviewed at active bit depth ${activeDepthMd}m MD.`,
        actual_event: "Differential sticking indication"
      })
    })
      .then((r) => r.json())
      .then((d) => {
        setFeedbackSent(`Feedback recorded: ${d.verdict} (${d.feedback_id})`);
        setTimeout(() => setFeedbackSent(null), 4000);
      })
      .catch(() => {});
  };

  return (
    <div className="space-y-6">
      {/* ── Console Header ── */}
      <div className="bg-slate-900 text-white rounded-xl p-5 border border-slate-800 shadow-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30">
                <ShieldAlert className="w-3.5 h-3.5" /> P0/P1 DRILLING DECISION SUPPORT
              </span>
              <span className="text-xs text-slate-400 font-mono">Depth MD: {activeDepthMd.toFixed(1)}m</span>
            </div>
            <h2 className="text-lg font-bold tracking-tight">Rig Engineering & Physical Hazard Diagnostics</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Real-time well-control influx tracking, geomechanical pressure window, hole cleaning index, and offset history
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="px-3 py-1 text-xs font-semibold rounded bg-rose-950/80 text-rose-300 border border-rose-700/60 font-mono">
              ENGINEER_REVIEW_REQUIRED = TRUE
            </span>
          </div>
        </div>

        {/* ── Sub Navigation ── */}
        <div className="flex border-b border-slate-800 mt-5 -mb-2 space-x-2 overflow-x-auto">
          {[
            { id: "well-control", label: "Well Control & Pressure Window", icon: <ShieldAlert className="w-4 h-4" /> },
            { id: "hole-cleaning", label: "Hole Cleaning & Pack-Off", icon: <Gauge className="w-4 h-4" /> },
            { id: "stuck-pipe", label: "Stuck Pipe Mechanism", icon: <AlertTriangle className="w-4 h-4" /> },
            { id: "what-happened", label: "What Happened Here Before?", icon: <History className="w-4 h-4" /> },
            { id: "what-if", label: "What-If Scenario Simulator", icon: <Sliders className="w-4 h-4" /> },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSubTab(tab.id as any)}
              className={`pb-3 px-3 text-xs font-bold flex items-center gap-1.5 border-b-2 whitespace-nowrap transition-colors ${
                subTab === tab.id
                  ? "border-amber-400 text-amber-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* ── TAB 1: Well-Control & Pressure Window (P0) ── */}
      {subTab === "well-control" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Kick / Influx Monitor */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
                  <ShieldAlert className="w-4 h-4 text-rose-600" /> Real-Time Influx / Kick Detection
                </h3>
                <p className="text-xs text-slate-500">Multi-channel influx state machine (Flow, Pit, SPP, Gas, ROP)</p>
              </div>
              <span className={`px-2.5 py-1 text-xs font-black rounded font-mono ${
                kick?.state === "NORMAL" ? "bg-emerald-100 text-emerald-800" : "bg-rose-100 text-rose-800 border border-rose-300 animate-pulse"
              }`}>
                STATE: {kick?.state || "NORMAL"}
              </span>
            </div>

            {/* Influx Indicators Matrix */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 font-mono text-center">
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-[10px] text-slate-500 block uppercase">Flow Imbalance</span>
                <span className={`text-base font-black ${(kick?.flow_imbalance_pct || 0) > 2 ? "text-rose-600" : "text-slate-800"}`}>
                  {(kick?.flow_imbalance_pct || 0) > 0 ? `+${kick?.flow_imbalance_pct}` : kick?.flow_imbalance_pct}%
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-[10px] text-slate-500 block uppercase">Pit Gain Rate</span>
                <span className={`text-base font-black ${(kick?.pit_gain_rate_bblhr || 0) > 1.5 ? "text-rose-600" : "text-slate-800"}`}>
                  +{kick?.pit_gain_rate_bblhr} bbl/h
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-[10px] text-slate-500 block uppercase">SPP Deviation</span>
                <span className={`text-base font-black ${(kick?.spp_deviation_pct || 0) < -5 ? "text-rose-600" : "text-slate-800"}`}>
                  {kick?.spp_deviation_pct}%
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-[10px] text-slate-500 block uppercase">Gas Influx</span>
                <span className={`text-base font-black ${(kick?.gas_increase_pct || 0) > 20 ? "text-rose-600" : "text-slate-800"}`}>
                  +{kick?.gas_increase_pct}%
                </span>
              </div>
            </div>

            {/* Mandatory Action Banner */}
            <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs flex items-center justify-between">
              <div>
                <span className="font-bold text-rose-900 block font-mono text-[11px]">
                  {kick?.mandatory_action}
                </span>
                <span className="text-[11px] text-rose-700">
                  Confidence: {kick?.confidence_pct}% • Triggered: {kick?.triggered_indicators_count} indicators
                </span>
              </div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-200 text-rose-900">
                NO AUTO SHUT-IN
              </span>
            </div>
          </div>

          {/* Pressure Window Module */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
                  <Gauge className="w-4 h-4 text-sky-600" /> Real-Time Geomechanical Pressure Window
                </h3>
                <p className="text-xs text-slate-500">ECD relative to Pore Pressure and Fracture Gradient</p>
              </div>
              <span className="px-2.5 py-1 text-[11px] font-bold rounded bg-sky-100 text-sky-800 border border-sky-300">
                {pw?.status || "OPTIMAL"}
              </span>
            </div>

            {/* Visual Pressure Window Bar */}
            <div className="space-y-2 py-2">
              <div className="flex justify-between text-xs font-mono font-semibold">
                <span className="text-amber-800">PP: {pw?.pore_pressure_sg} SG</span>
                <span className="text-slate-900 font-bold bg-slate-100 px-2 py-0.5 rounded border border-slate-300">
                  Current ECD: {pw?.current_ecd_sg} SG
                </span>
                <span className="text-rose-800">FG: {pw?.fracture_gradient_sg} SG</span>
              </div>
              <div className="h-6 w-full bg-slate-100 rounded-lg relative overflow-hidden flex border border-slate-300">
                <div style={{ width: "35%" }} className="bg-amber-200/80 flex items-center justify-center text-[10px] font-mono text-amber-900">
                  Underbalance Zone
                </div>
                <div style={{ width: "45%" }} className="bg-emerald-200/80 flex items-center justify-center text-[10px] font-bold font-mono text-emerald-900">
                  Safe Operating Window
                </div>
                <div style={{ width: "20%" }} className="bg-rose-200/80 flex items-center justify-center text-[10px] font-mono text-rose-900">
                  Loss Zone
                </div>
              </div>
              <div className="flex justify-between text-[11px] font-mono text-slate-500 pt-1">
                <span>ECD → PP Margin: +{pw?.ecd_to_pp_margin_sg} SG</span>
                <span>ECD → Frac Margin: +{pw?.ecd_to_frac_margin_sg} SG</span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600">
              <span className="font-bold text-slate-800 block">Operating Guideline:</span>
              Maintain ECD within 1.55 – 1.75 SG. Never provide autonomous mud-weight changes without domain engineer verification.
            </div>
          </div>
        </div>
      )}

      {/* ── TAB 2: Hole Cleaning & Pack-Off Index (P0) ── */}
      {subTab === "hole-cleaning" && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Gauge className="w-5 h-5 text-indigo-600" /> Hole Cleaning Index (HCI) & Cuttings Transport
              </h3>
              <p className="text-xs text-slate-500">
                Annular velocity, cuttings loading, and pack-off risk derived from ROP, RPM, and flow rate
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-black font-mono text-indigo-900">
                HCI: {hci?.hole_cleaning_index ?? 92.5}
              </span>
              <span className="px-3 py-1 rounded text-xs font-bold bg-indigo-100 text-indigo-800 border border-indigo-300">
                {hci?.status || "GOOD"}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-center">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-xs text-slate-500 block uppercase">Annular Velocity</span>
              <span className="text-xl font-black text-slate-900">{hci?.annular_velocity_fpm ?? 214.5} fpm</span>
              <span className="text-[11px] text-slate-500 block mt-1">Req: {hci?.required_velocity_fpm ?? 165} fpm</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-xs text-slate-500 block uppercase">Cuttings Bed Risk</span>
              <span className="text-xl font-black text-emerald-700">{hci?.cuttings_bed_risk || "LOW"}</span>
              <span className="text-[11px] text-slate-500 block mt-1">Section Inclination: 28°</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-xs text-slate-500 block uppercase">Pack-Off Risk</span>
              <span className="text-xl font-black text-emerald-700">{hci?.packoff_risk || "LOW"}</span>
              <span className="text-[11px] text-slate-500 block mt-1">SPP / Torque Coherence</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900 text-slate-200 text-xs font-mono space-y-1.5">
            <span className="text-amber-400 font-bold uppercase">Hole Cleaning Grading Scale:</span>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 pt-1 text-[11px]">
              <span className="text-emerald-400 font-bold">90–100: GOOD</span>
              <span className="text-emerald-300">75–89: ACCEPTABLE</span>
              <span className="text-amber-400">50–74: WATCH</span>
              <span className="text-rose-400">25–49: POOR</span>
              <span className="text-rose-600 font-bold">0–24: CRITICAL</span>
            </div>
          </div>
        </div>
      )}

      {/* ── TAB 3: Stuck Pipe Mechanism Classification (P0) ── */}
      {subTab === "stuck-pipe" && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-rose-600" /> Stuck Pipe Physical Mechanism Classifier
              </h3>
              <p className="text-xs text-slate-500">
                Breaks down stuck pipe probability into distinct physical root causes with evidence and analog offset well
              </p>
            </div>
            <span className="px-3 py-1 rounded text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300 font-mono">
              RISK: {sp?.overall_stuck_pipe_risk || "HIGH"}
            </span>
          </div>

          {/* Breakdown bars */}
          <div className="space-y-3 font-mono">
            <div>
              <div className="flex justify-between text-xs font-bold mb-1 text-slate-800">
                <span>Differential Sticking (Depleted Sandstone Overbalance)</span>
                <span className="text-rose-700">{sp?.mechanism_breakdown?.differential_sticking_pct || 64.0}%</span>
              </div>
              <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden">
                <div style={{ width: `${sp?.mechanism_breakdown?.differential_sticking_pct || 64}%` }} className="h-full bg-rose-600 rounded-full" />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold mb-1 text-slate-800">
                <span>Pack-Off / Cuttings Bed Loading</span>
                <span className="text-amber-700">{sp?.mechanism_breakdown?.pack_off_cuttings_bed_pct || 23.0}%</span>
              </div>
              <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden">
                <div style={{ width: `${sp?.mechanism_breakdown?.pack_off_cuttings_bed_pct || 23}%` }} className="h-full bg-amber-500 rounded-full" />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold mb-1 text-slate-800">
                <span>Wellbore Instability / Cavings</span>
                <span className="text-slate-700">{sp?.mechanism_breakdown?.wellbore_instability_pct || 13.0}%</span>
              </div>
              <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden">
                <div style={{ width: `${sp?.mechanism_breakdown?.wellbore_instability_pct || 13}%` }} className="h-full bg-slate-500 rounded-full" />
              </div>
            </div>
          </div>

          {/* Historical Analog Box */}
          <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200 text-xs space-y-2">
            <div className="font-bold text-amber-900 flex items-center gap-1.5">
              <History className="w-4 h-4 text-amber-700" />
              Historical Analog: {sp?.historical_analog?.well_name} ({sp?.historical_analog?.depth_interval_m})
            </div>
            <p className="text-amber-800">
              <strong>Event:</strong> {sp?.historical_analog?.event} • <strong>NPT:</strong> {sp?.historical_analog?.npt_hours} hours • <strong>Source:</strong> {sp?.historical_analog?.source_document}
            </p>
          </div>
        </div>
      )}

      {/* ── TAB 4: What Happened Here Before? (P1) ── */}
      {subTab === "what-happened" && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <History className="w-5 h-5 text-emerald-600" /> What Happened Here Before?
              </h3>
              <p className="text-xs text-slate-500">
                Historical hazards experienced in comparable offset wells within vertical ±30m stratigraphic depth corridor
              </p>
            </div>
            <span className="text-xs font-mono font-bold px-2.5 py-1 bg-slate-100 text-slate-700 rounded border border-slate-300">
              Depth Window: {activeDepthMd}m ± 30m
            </span>
          </div>

          <div className="space-y-3">
            {historicalEvents.map((ev) => (
              <div key={ev.event_id} className="p-4 rounded-xl border border-slate-200 hover:border-slate-300 bg-slate-50/50 transition-colors text-xs space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900 font-mono text-sm">{ev.well_name}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-200">
                      {ev.event_type}
                    </span>
                    <span className="text-slate-500 font-mono">({ev.surface_distance_m}m distance • TSD diff {ev.tsd_difference_m}m)</span>
                  </div>
                  <span className="font-mono font-bold text-amber-800">NPT: {ev.npt_hours} hrs</span>
                </div>
                <p className="text-slate-700"><strong>Root Cause:</strong> {ev.root_cause}</p>
                <div className="flex items-center justify-between pt-1 text-[11px] text-slate-500 border-t border-slate-200/60 font-mono">
                  <span>Mitigation: {ev.mitigation_action}</span>
                  <span className="text-slate-700 font-semibold">Source: {ev.source_document}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── TAB 5: What-If Scenario Analysis Simulator (P2) ── */}
      {subTab === "what-if" && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Sliders className="w-5 h-5 text-indigo-600" /> What-If Drilling Parameter Simulator
              </h3>
              <p className="text-xs text-slate-500">
                Test hypothetical parameter adjustments on projected ECD, MSE, and margin safety
              </p>
            </div>
            <span className="px-3 py-1 rounded text-xs font-black bg-rose-100 text-rose-900 border border-rose-300 font-mono">
              SCENARIO ESTIMATE — NOT AN OPERATIONAL COMMAND
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-4 rounded-xl bg-slate-50 border border-slate-200">
            {/* Slider 1: Mud Weight */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-bold text-slate-800">
                <span>Scenario Mud Weight</span>
                <span className="font-mono text-indigo-700">{mwInput.toFixed(2)} SG</span>
              </div>
              <input
                type="range"
                min="0.95"
                max="1.70"
                step="0.01"
                value={mwInput}
                onChange={(e) => setMwInput(parseFloat(e.target.value))}
                className="w-full accent-indigo-600"
              />
              <span className="text-[10px] text-slate-400 block">Baseline: 1.16 SG</span>
            </div>

            {/* Slider 2: Flow Rate */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-bold text-slate-800">
                <span>Scenario Flow Rate</span>
                <span className="font-mono text-indigo-700">{flowInput} GPM</span>
              </div>
              <input
                type="range"
                min="350"
                max="750"
                step="10"
                value={flowInput}
                onChange={(e) => setFlowInput(parseInt(e.target.value))}
                className="w-full accent-indigo-600"
              />
              <span className="text-[10px] text-slate-400 block">Baseline: 640 GPM</span>
            </div>

            {/* Slider 3: RPM */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-bold text-slate-800">
                <span>Scenario Rotary RPM</span>
                <span className="font-mono text-indigo-700">{rpmInput} RPM</span>
              </div>
              <input
                type="range"
                min="40"
                max="150"
                step="5"
                value={rpmInput}
                onChange={(e) => setRpmInput(parseInt(e.target.value))}
                className="w-full accent-indigo-600"
              />
              <span className="text-[10px] text-slate-400 block">Baseline: 95 RPM</span>
            </div>
          </div>

          {/* Projected Outcomes */}
          {whatIfResult && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-center">
              <div className="p-3 rounded-lg bg-indigo-50/60 border border-indigo-200">
                <span className="text-[10px] text-indigo-800 block uppercase">Projected ECD</span>
                <span className="text-base font-black text-indigo-900">{whatIfResult.projected_outputs?.projected_ecd_sg} SG</span>
              </div>
              <div className="p-3 rounded-lg bg-emerald-50/60 border border-emerald-200">
                <span className="text-[10px] text-emerald-800 block uppercase">Projected Loss Margin</span>
                <span className="text-base font-black text-emerald-900">+{whatIfResult.projected_outputs?.projected_loss_margin_sg} SG</span>
              </div>
              <div className="p-3 rounded-lg bg-sky-50/60 border border-sky-200">
                <span className="text-[10px] text-sky-800 block uppercase">Projected Kick Margin</span>
                <span className="text-base font-black text-sky-900">+{whatIfResult.projected_outputs?.projected_kick_margin_sg} SG</span>
              </div>
              <div className="p-3 rounded-lg bg-amber-50/60 border border-amber-200">
                <span className="text-[10px] text-amber-800 block uppercase">Projected MSE</span>
                <span className="text-base font-black text-amber-900">{whatIfResult.projected_outputs?.projected_mse_psi} psi</span>
              </div>
            </div>
          )}

          {/* ── Human Feedback Loop (P2) ── */}
          <div className="pt-4 border-t border-slate-200 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                  <MessageSquare className="w-3.5 h-3.5 text-slate-600" /> Human Engineer Feedback on Current Prediction
                </h4>
                <p className="text-[11px] text-slate-500">Validate or dismiss predictions to build future labeled field data</p>
              </div>
              {feedbackSent && (
                <span className="text-xs font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">
                  {feedbackSent}
                </span>
              )}
            </div>

            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => sendFeedback("CONFIRMED")}
                className="px-3 py-1.5 rounded text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white transition-colors"
              >
                [ CONFIRMED ]
              </button>
              <button
                onClick={() => sendFeedback("FALSE_POSITIVE")}
                className="px-3 py-1.5 rounded text-xs font-bold bg-rose-600 hover:bg-rose-700 text-white transition-colors"
              >
                [ FALSE POSITIVE ]
              </button>
              <button
                onClick={() => sendFeedback("ALREADY_KNOWN")}
                className="px-3 py-1.5 rounded text-xs font-bold bg-amber-600 hover:bg-amber-700 text-white transition-colors"
              >
                [ ALREADY KNOWN ]
              </button>
              <button
                onClick={() => sendFeedback("NOT_RELEVANT")}
                className="px-3 py-1.5 rounded text-xs font-bold bg-slate-600 hover:bg-slate-700 text-white transition-colors"
              >
                [ NOT RELEVANT ]
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
