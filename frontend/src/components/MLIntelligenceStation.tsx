"use client";

import React, { useState, useEffect } from "react";
import {
  Brain, Cpu, Activity, AlertTriangle, ShieldCheck, Clock,
  ArrowRight, Search, BarChart3, Layers, CheckCircle2,
  TrendingDown, TrendingUp, Info, HelpCircle, ChevronRight, Zap
} from "lucide-react";

interface MLModelCatalogItem {
  priority: string;
  name: string;
  models: string;
  target: string;
  published_benchmark: string;
  project_fit_pct: number;
  status: string;
  features: string[];
  decision_support: string;
}

interface MLPredictionData {
  depth_md_m: number;
  tvdss_m: number;
  formation: string;
  stuck_pipe: {
    probability: number;
    risk_level: string;
    likely_mechanism: string;
    ensemble_breakdown: {
      extra_trees_prob: number;
      gradient_boosting_prob: number;
      model_consensus_pct: number;
    };
    shap_factors: Array<{ feature: string; contribution_pct: number; status: string }>;
  };
  lost_circulation: {
    loss_probability: number;
    severity: string;
    expected_interval: string;
    supporting_offset_wells: string[];
    shap_factors: Array<{ feature: string; contribution_pct: number }>;
  };
  kick_detection: {
    activity: string;
    kick_probability: number;
    risk_level: string;
    isolation_forest_anomaly: boolean;
    anomaly_score: number;
    recommended_action: string;
  };
  rop_prediction: {
    actual_rop_mhr: number;
    expected_rop_mhr: number;
    deviation_pct: number;
    anomaly_status: string;
  };
  torque_prediction: {
    actual_torque_kftlb: number;
    expected_torque_kftlb: number;
    torque_residual_kftlb: number;
    status: string;
  };
  drag_prediction: {
    actual_drag_klbs: number;
    expected_drag_klbs: number;
    drag_residual_klbs: number;
    status: string;
  };
  stick_slip: {
    severity: string;
    confidence_pct: number;
    torque_variability: number;
    rpm_variability: number;
  };
  lithology: {
    predicted_lithology: string;
    confidence_pct: number;
    gamma_ray_api: number;
  };
  change_point: {
    regime_status: string;
    transition_detected: boolean;
    detected_change_depth_m: number | null;
    regime_description: string;
    current_regime_name: string;
    detected_shifts: {
      rop_regime_shift_pct: number;
      mse_regime_shift_pct: number;
      torque_variance_shift_pct: number;
    };
  };
  dtw_historical_matches: Array<{
    well_name: string;
    event_type: string;
    similarity_pct: number;
    formation: string;
    depth_range: string;
    npt_hours: number;
    source_document: string;
  }>;
  physics_ml_fusion: {
    fused_risk_score: number;
    fused_risk_level: string;
    physics_weight: number;
    ml_weight: number;
    primary_driver: string;
  };
  engineer_review_required: boolean;
  autonomous_control: boolean;
}

export const MLIntelligenceStation: React.FC<{ activeDepthMd?: number }> = ({
  activeDepthMd = 2413.5
}) => {
  const [data, setData] = useState<MLPredictionData | null>(null);
  const [catalog, setCatalog] = useState<MLModelCatalogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCatalogModal, setShowCatalogModal] = useState(false);

  // Context-aware station chat
  const [stationQuery, setStationQuery] = useState("");
  const [stationAnswer, setStationAnswer] = useState<string | null>(null);
  const [queryLoading, setQueryLoading] = useState(false);

  useEffect(() => {
    // Fetch predictions and catalog
    Promise.all([
      fetch("http://localhost:8000/api/v1/ml/predict-all", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bit_depth_md: activeDepthMd, formation_name: "Upper Tipam Sandstone" })
      }).then((r) => r.json()),
      fetch("http://localhost:8000/api/v1/ml/models").then((r) => r.json())
    ])
      .then(([predData, catData]) => {
        setData(predData);
        setCatalog(catData);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load ML stack:", err);
        setLoading(false);
      });
  }, [activeDepthMd]);

  const handleAskStation = async (qText?: string) => {
    const q = (qText || stationQuery).trim();
    if (!q) return;

    setQueryLoading(true);
    setStationAnswer(null);

    try {
      const res = await fetch("http://localhost:8000/api/v1/ml/intelligence-station/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: q,
          current_depth_md: activeDepthMd,
          active_well: "SYN-NHK-05",
          active_formation: "Upper Tipam Sandstone"
        })
      });
      const resData = await res.json();
      setStationAnswer(resData.answer);
      setStationQuery(q);
    } catch (err) {
      console.error("Station query error:", err);
    } finally {
      setQueryLoading(false);
    }
  };

  if (loading || !data) {
    return (
      <div className="card p-12 text-center flex flex-col items-center justify-center min-h-[450px]">
        <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mb-4" />
        <h3 className="font-bold text-slate-800 text-sm">Initializing Enterprise ML Stack...</h3>
        <p className="text-xs text-slate-500 mt-1">Executing forward pass on Extra Trees, XGBoost, and Dynamic Time Warping</p>
      </div>
    );
  }

  const isHazard = activeDepthMd >= 2413.0;

  return (
    <div className="space-y-4">
      {/* ── Station Header Banner ── */}
      <div className="bg-gradient-to-r from-indigo-950 via-slate-900 to-purple-950 text-white rounded-xl p-4 border border-indigo-800/50 shadow-md">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-indigo-600 text-white shadow-xs">
                <Brain className="w-4 h-4" />
              </span>
              <h2 className="text-base font-black tracking-tight flex items-center gap-2">
                <span>🧠 NWIS ML INTELLIGENCE STATION</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-500/30 text-indigo-300 border border-indigo-400/40">
                  14-MODEL MULTI-TIER STACK
                </span>
              </h2>
            </div>
            <p className="text-xs text-slate-300">
              Physics + Supervised ML (Extra Trees / XGBoost / RF) + Anomaly (Isolation Forest) + Sequence (DTW) + SHAP Attribution
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowCatalogModal(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-700/80 hover:bg-indigo-600 text-white text-xs font-bold transition-all shadow-xs border border-indigo-500/50"
            >
              <Cpu className="w-3.5 h-3.5 text-indigo-200" />
              <span>Inspect 14-Model Catalog ({catalog.length})</span>
            </button>

            <div className="text-right hidden sm:block border-l border-slate-700/70 pl-3">
              <div className="text-[10px] font-mono text-slate-400">DECISION-SUPPORT SYSTEM</div>
              <div className="text-xs font-bold text-amber-300 flex items-center gap-1 justify-end">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>Engineer Review Enforced</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Top Metric Residuals Track ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* Expected ROP vs Actual */}
        <div className="card p-3 border-l-4 border-l-amber-500">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span className="font-semibold">ROP Model (XGB)</span>
            <TrendingDown className="w-3.5 h-3.5 text-rose-500" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-bold font-mono text-slate-800">{data.rop_prediction.actual_rop_mhr}</span>
            <span className="text-xs text-slate-400">/ Exp: {data.rop_prediction.expected_rop_mhr} m/h</span>
          </div>
          <div className="mt-1 text-[11px] font-bold text-rose-600 font-mono">
            {data.rop_prediction.deviation_pct}% Deviation ({data.rop_prediction.anomaly_status})
          </div>
        </div>

        {/* Torque Residual */}
        <div className="card p-3 border-l-4 border-l-rose-500">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span className="font-semibold">Torque Residual (XGB)</span>
            <TrendingUp className="w-3.5 h-3.5 text-rose-500" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-bold font-mono text-slate-800">{data.torque_prediction.actual_torque_kftlb}</span>
            <span className="text-xs text-slate-400">/ Exp: {data.torque_prediction.expected_torque_kftlb} kft-lb</span>
          </div>
          <div className="mt-1 text-[11px] font-bold text-rose-600 font-mono">
            +{data.torque_prediction.torque_residual_kftlb} kft-lb Residual ({data.torque_prediction.status})
          </div>
        </div>

        {/* Drag Residual */}
        <div className="card p-3 border-l-4 border-l-sky-500">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span className="font-semibold">Drag Residual (XGB)</span>
            <Activity className="w-3.5 h-3.5 text-sky-500" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-bold font-mono text-slate-800">{data.drag_prediction.actual_drag_klbs}</span>
            <span className="text-xs text-slate-400">/ Exp: {data.drag_prediction.expected_drag_klbs} klbs</span>
          </div>
          <div className="mt-1 text-[11px] font-bold text-sky-700 font-mono">
            +{data.drag_prediction.drag_residual_klbs} klbs Residual ({data.drag_prediction.status})
          </div>
        </div>

        {/* Stick-Slip / Dysfunction */}
        <div className="card p-3 border-l-4 border-l-purple-500">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span className="font-semibold">Stick-Slip (RF)</span>
            <Zap className="w-3.5 h-3.5 text-purple-500" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-bold font-mono text-purple-700">{data.stick_slip.severity}</span>
            <span className="text-xs text-slate-400">Conf: {data.stick_slip.confidence_pct}%</span>
          </div>
          <div className="mt-1 text-[11px] text-slate-500 font-mono">
            Torque σ: {data.stick_slip.torque_variability} · RPM σ: {data.stick_slip.rpm_variability}
          </div>
        </div>
      </div>

      {/* ── Main 2-Column Grid: ML Models + DTW Historical Intelligence ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left Column (7 cols): Flagship Ensembles & SHAP Attributions */}
        <div className="lg:col-span-7 space-y-4">
          {/* 🔴 Flagship Model 1: Stuck Pipe (Extra Trees + XGBoost Ensemble) */}
          <div className="card p-4 border border-rose-200 bg-gradient-to-br from-white to-rose-50/20">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-600 animate-pulse" />
                <h3 className="font-heading font-black text-sm text-slate-900">
                  FLAGSHIP P0: STUCK-PIPE MULTI-MODEL ENSEMBLE
                </h3>
              </div>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-rose-100 text-rose-800 border border-rose-300">
                FIT: 97% · EXTRA TREES + XGB
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
              <div className="p-3 bg-white rounded-lg border border-slate-200">
                <div className="text-[11px] text-slate-500">Ensemble Probability</div>
                <div className="text-2xl font-black font-mono text-rose-600">
                  {(data.stuck_pipe.probability * 100).toFixed(1)}%
                </div>
                <div className="text-[10px] font-bold text-rose-700 mt-0.5">
                  LEVEL: {data.stuck_pipe.risk_level}
                </div>
              </div>

              <div className="p-3 bg-white rounded-lg border border-slate-200">
                <div className="text-[11px] text-slate-500">Model Breakdown</div>
                <div className="text-xs font-mono font-semibold text-slate-700 space-y-0.5 mt-1">
                  <div>Extra Trees: {(data.stuck_pipe.ensemble_breakdown.extra_trees_prob * 100).toFixed(0)}%</div>
                  <div>XGBoost: {(data.stuck_pipe.ensemble_breakdown.gradient_boosting_prob * 100).toFixed(0)}%</div>
                </div>
                <div className="text-[10px] text-slate-400 mt-1">
                  Consensus: {data.stuck_pipe.ensemble_breakdown.model_consensus_pct}%
                </div>
              </div>

              <div className="p-3 bg-white rounded-lg border border-slate-200">
                <div className="text-[11px] text-slate-500">Likely Mechanism</div>
                <div className="text-xs font-bold text-slate-900 mt-1 leading-snug">
                  {data.stuck_pipe.likely_mechanism}
                </div>
              </div>
            </div>

            {/* SHAP Feature Contribution Bars */}
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <div className="flex items-center justify-between text-xs font-bold text-slate-700 mb-2">
                <span>SHAP Feature Attribution (Why is Risk Elevated?)</span>
                <span className="text-[10px] font-mono text-slate-400">Phase 5 Explainability</span>
              </div>
              <div className="space-y-1.5">
                {data.stuck_pipe.shap_factors.map((f) => (
                  <div key={f.feature} className="flex items-center text-xs">
                    <span className="w-44 text-slate-600 truncate">{f.feature}</span>
                    <div className="flex-1 bg-slate-200 h-2 rounded-full overflow-hidden mx-2">
                      <div
                        className={`h-full rounded-full ${
                          f.contribution_pct > 20
                            ? "bg-rose-500"
                            : f.contribution_pct > 10
                            ? "bg-amber-500"
                            : "bg-indigo-500"
                        }`}
                        style={{ width: `${Math.min(100, Math.abs(f.contribution_pct) * 2.8)}%` }}
                      />
                    </div>
                    <span className="font-mono font-bold text-[11px] text-slate-800 w-12 text-right">
                      {f.contribution_pct > 0 ? `+${f.contribution_pct}%` : `${f.contribution_pct}%`}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 🔴 P0 Model 2 & 3: Lost Circulation & Kick Detection */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Lost Circulation */}
            <div className="card p-3 border border-amber-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                  <span>Lost Circulation (Extra Trees + XGB)</span>
                </span>
                <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-amber-100 text-amber-800">
                  FIT: 95%
                </span>
              </div>
              <div className="flex items-baseline justify-between mb-2">
                <span className="text-xl font-bold font-mono text-amber-700">
                  {(data.lost_circulation.loss_probability * 100).toFixed(1)}%
                </span>
                <span className="text-xs font-bold text-slate-600">
                  SEVERITY: {data.lost_circulation.severity}
                </span>
              </div>
              <div className="text-[11px] text-slate-600 bg-amber-50/60 p-2 rounded border border-amber-200/50">
                <strong>Expected Loss Interval:</strong> {data.lost_circulation.expected_interval}
              </div>
            </div>

            {/* 3-Stage Kick Detector */}
            <div className="card p-3 border border-indigo-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-800">Kick Influx (3-Stage Stack)</span>
                <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-800">
                  FIT: 93%
                </span>
              </div>
              <div className="flex items-baseline justify-between mb-2">
                <div>
                  <span className="text-xl font-bold font-mono text-indigo-700">
                    {(data.kick_detection.kick_probability * 100).toFixed(1)}%
                  </span>
                  <span className="text-xs text-slate-400 ml-1">({data.kick_detection.risk_level})</span>
                </div>
                <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                  Activity: {data.kick_detection.activity}
                </span>
              </div>
              <div className="text-[11px] text-slate-600 bg-indigo-50/60 p-2 rounded border border-indigo-200/50">
                <strong>Isolation Forest Anomaly:</strong> {data.kick_detection.isolation_forest_anomaly ? "ANOMALY DETECTED (Score: " + data.kick_detection.anomaly_score + ")" : "NOMINAL"}
              </div>
            </div>
          </div>

          {/* Change-Point Detection (CUSUM) */}
          <div className="card p-3 border border-slate-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-purple-600" />
                <span>Change-Point Detection (CUSUM Regime Detector)</span>
              </span>
              <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-purple-100 text-purple-800">
                FIT: 89% · STATISTICAL
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <div className="font-mono font-bold text-purple-800 whitespace-nowrap">
                {data.change_point.regime_status}
              </div>
              <div className="text-slate-600 text-xs border-l border-slate-200 pl-3">
                {data.change_point.regime_description}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column (5 cols): DTW Telemetry Matching + Context Answering Station */}
        <div className="lg:col-span-5 space-y-4">
          {/* Dynamic Time Warping (DTW) Signature Alignment */}
          <div className="card p-4 border border-indigo-200 bg-gradient-to-br from-white to-indigo-50/20">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-100">
              <div className="flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-indigo-600" />
                <h3 className="font-heading font-black text-xs text-slate-900">
                  DYNAMIC TIME WARPING (DTW) SIGNATURE MATCHING
                </h3>
              </div>
              <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-800">
                FIT: 94%
              </span>
            </div>
            <p className="text-[11px] text-slate-500 mb-3">
              Compares rolling multi-variate telemetry trajectory (Torque, Drag, ROP, SPP, MSE) against historical incident profiles:
            </p>

            <div className="space-y-2">
              {data.dtw_historical_matches.map((item, idx) => (
                <div
                  key={item.well_name}
                  className={`p-2.5 rounded-lg border text-xs transition-all ${
                    idx === 0
                      ? "bg-indigo-50/80 border-indigo-300 shadow-xs"
                      : "bg-white border-slate-200"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-1.5">
                      <span className="font-bold text-slate-900">{item.well_name}</span>
                      <span className="text-[10px] font-mono px-1 rounded bg-slate-100 text-slate-600">
                        {item.event_type}
                      </span>
                    </div>
                    <span
                      className={`font-mono font-bold text-xs ${
                        item.similarity_pct >= 90
                          ? "text-rose-600"
                          : item.similarity_pct >= 80
                          ? "text-indigo-600"
                          : "text-slate-600"
                      }`}
                    >
                      {item.similarity_pct}% MATCH
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-500 flex justify-between items-center">
                    <span>{item.formation} ({item.depth_range})</span>
                    <span className="font-mono text-slate-700 font-semibold">{item.npt_hours} hrs NPT</span>
                  </div>
                  <div className="text-[10px] font-mono text-slate-400 mt-0.5">
                    Source: `{item.source_document}`
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 🧠 Context-Aware Intelligence Station Terminal */}
          <div className="card p-4 border border-purple-200 bg-white">
            <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100">
              <Brain className="w-4 h-4 text-purple-600" />
              <h3 className="font-heading font-black text-xs text-slate-900">
                INTELLIGENCE STATION CONTEXT QUERY
              </h3>
            </div>
            <p className="text-[11px] text-slate-500 mb-3">
              Context router injects active well (<strong>SYN-NHK-05</strong>), depth (<strong>{activeDepthMd.toFixed(1)}m</strong>), formation (<strong>Upper Tipam</strong>), and live ML residuals:
            </p>

            {/* 1-Click Quick Prompts */}
            <div className="grid grid-cols-2 gap-1.5 mb-3">
              {[
                { label: "Why is stuck-pipe risk high?", icon: "❓" },
                { label: "What happened here?", icon: "📜" },
                { label: "Which wells are similar?", icon: "🔍" },
                { label: "What's ahead?", icon: "🔭" }
              ].map((btn) => (
                <button
                  key={btn.label}
                  onClick={() => handleAskStation(btn.label)}
                  disabled={queryLoading}
                  className="px-2.5 py-1.5 text-left rounded-lg bg-slate-50 hover:bg-purple-50 hover:border-purple-300 border border-slate-200 text-xs font-semibold text-slate-700 transition-all flex items-center justify-between group"
                >
                  <span className="truncate">{btn.icon} {btn.label}</span>
                  <ChevronRight className="w-3 h-3 text-slate-400 group-hover:text-purple-600 flex-shrink-0" />
                </button>
              ))}
            </div>

            {/* Query Output Display */}
            {queryLoading && (
              <div className="p-4 bg-purple-50/50 rounded-lg border border-purple-200 text-center text-xs text-purple-700 animate-pulse font-semibold">
                Synthesizing multi-model evidence, DTW signatures, and DDR records...
              </div>
            )}

            {stationAnswer && !queryLoading && (
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 max-h-64 overflow-y-auto text-xs leading-relaxed text-slate-800 space-y-2 font-sans">
                {stationAnswer.split("\n\n").map((para, i) => (
                  <p key={i} className={para.startsWith("###") ? "font-bold text-slate-900" : ""}>
                    {para.replace("### ", "")}
                  </p>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── 14-Model Catalog Modal ── */}
      {showCatalogModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden border border-slate-200">
            <div className="p-4 bg-gradient-to-r from-indigo-900 to-slate-900 text-white flex items-center justify-between">
              <div>
                <h3 className="font-bold text-base flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-indigo-400" />
                  <span>eRTMAC-NWIS Enterprise ML Model Catalog</span>
                </h3>
                <p className="text-xs text-slate-300">
                  14 specialized machine learning models and physics regressors mapped to drilling operations
                </p>
              </div>
              <button
                onClick={() => setShowCatalogModal(false)}
                className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white"
              >
                ✕
              </button>
            </div>

            <div className="p-4 overflow-y-auto space-y-3 flex-1">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {catalog.map((m) => (
                  <div key={m.name} className="p-3 rounded-lg border border-slate-200 bg-slate-50/50 hover:bg-slate-50">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-xs text-slate-900">{m.name}</span>
                      <span
                        className={`text-[9px] font-mono font-bold px-1.5 py-0.2 rounded border ${
                          m.priority === "P0"
                            ? "bg-rose-100 text-rose-800 border-rose-300"
                            : m.priority === "P1"
                            ? "bg-amber-100 text-amber-800 border-amber-300"
                            : "bg-blue-100 text-blue-800 border-blue-300"
                        }`}
                      >
                        {m.priority} · FIT: {m.project_fit_pct}%
                      </span>
                    </div>
                    <div className="text-[11px] font-mono font-semibold text-indigo-700 mb-1">
                      Model: {m.models}
                    </div>
                    <div className="text-[11px] text-slate-600 mb-1">
                      <strong>Published:</strong> {m.published_benchmark}
                    </div>
                    <div className="text-[10px] text-slate-500 bg-white p-1.5 rounded border border-slate-200">
                      <strong>Decision Support:</strong> {m.decision_support}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-3 bg-slate-100 border-t border-slate-200 flex justify-between items-center text-xs">
              <span className="text-slate-500 font-mono text-[11px]">
                Enforces engineer_review_required = true across all models
              </span>
              <button
                onClick={() => setShowCatalogModal(false)}
                className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-bold"
              >
                Close Catalog
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
