"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { Header } from "@/components/Header";
import { TopNav, NavTab } from "@/components/TopNav";
import { CurtainSection } from "@/components/CurtainSection";
import { LookAheadCard } from "@/components/LookAheadCard";
import { TelemetryTrack, TelemetryData } from "@/components/TelemetryTrack";
import { DoghouseView } from "@/components/DoghouseView";
import { MultiRiskPanel } from "@/components/MultiRiskPanel";
import { AnalogCorrelationPanel } from "@/components/AnalogCorrelationPanel";
import { RigWeatherWidget } from "@/components/RigWeatherWidget";
import { BasinMap } from "@/components/BasinMap";
import { RealDataViewer } from "@/components/RealDataViewer";
import { EngineeringConsole } from "@/components/EngineeringConsole";
import { IndianLocationConsole } from "@/components/IndianLocationConsole";
import { GroundedAIAssistant } from "@/components/GroundedAIAssistant";
import { MLIntelligenceStation } from "@/components/MLIntelligenceStation";
import { InnovationsConsole } from "@/components/InnovationsConsole";

// Dynamic import for MapLibre (client-side only)
const MapTilerLiveMap = dynamic(
  () => import("@/components/MapTilerLiveMap").then((m) => ({ default: m.MapTilerLiveMap })),
  {
    ssr: false,
    loading: () => (
      <div
        className="card flex items-center justify-center"
        style={{ minHeight: 560 }}
      >
        <div className="text-center">
          <div
            className="w-10 h-10 rounded-full mx-auto mb-3 animate-spin"
            style={{ border: "3px solid var(--border)", borderTopColor: "var(--pine)" }}
          />
          <p className="text-sm font-semibold" style={{ color: "var(--text-secondary)" }}>
            Loading Interactive Map…
          </p>
        </div>
      </div>
    ),
  }
);

export interface WellPoint {
  well_id?: string;
  well_name: string;
  field_name: string;
  surface_lat: number;
  surface_lon: number;
  kb_elevation_m?: number;
  total_depth_md_m?: number;
  total_depth_m?: number;
  status: string;
  historical_hazards?: any[];
}

const DEFAULT_WELLS: WellPoint[] = [
  { well_id: "c1f7a012-3b4c-4e89-9a11-000000000005", well_name: "SYN-NHK-05", field_name: "Nahorkatiya", surface_lat: 27.2885, surface_lon: 95.3345, kb_elevation_m: 122.5, total_depth_m: 3150.0, status: "DRILLING" },
  { well_id: "c1f7a012-3b4c-4e89-9a11-000000000001", well_name: "SYN-NHK-01", field_name: "Nahorkatiya", surface_lat: 27.2798, surface_lon: 95.3211, kb_elevation_m: 121.2, total_depth_m: 3250.0, status: "COMPLETED" },
  { well_id: "c1f7a012-3b4c-4e89-9a11-000000000002", well_name: "SYN-NHK-02", field_name: "Nahorkatiya", surface_lat: 27.2954, surface_lon: 95.3488, kb_elevation_m: 124.0, total_depth_m: 3180.0, status: "COMPLETED" },
  { well_id: "c1f7a012-3b4c-4e89-9a11-000000000003", well_name: "SYN-NHK-03", field_name: "Nahorkatiya", surface_lat: 27.2655, surface_lon: 95.3122, kb_elevation_m: 119.8, total_depth_m: 3420.0, status: "COMPLETED" },
  { well_id: "c1f7a012-3b4c-4e89-9a11-000000000004", well_name: "SYN-NHK-04", field_name: "Nahorkatiya", surface_lat: 27.3112, surface_lon: 95.3621, kb_elevation_m: 126.1, total_depth_m: 2950.0, status: "COMPLETED" },
  { well_id: "c1f7a012-3b4c-4e89-9a11-000000000006", well_name: "SYN-MORAN-01", field_name: "Moran", surface_lat: 27.1855, surface_lon: 94.9312, kb_elevation_m: 115.4, total_depth_m: 3850.0, status: "COMPLETED" },
  { well_id: "c1f7a012-3b4c-4e89-9a11-000000000007", well_name: "SYN-MORAN-02", field_name: "Moran", surface_lat: 27.1992, surface_lon: 94.9455, kb_elevation_m: 117.0, total_depth_m: 3920.0, status: "COMPLETED" },
  { well_id: "c1f7a012-3b4c-4e89-9a11-000000000008", well_name: "SYN-BGJ-01", field_name: "Baghjan", surface_lat: 27.5812, surface_lon: 95.3522, kb_elevation_m: 128.5, total_depth_m: 4100.0, status: "COMPLETED" },
  { well_id: "c1f7a012-3b4c-4e89-9a11-000000000009", well_name: "SYN-BGJ-02", field_name: "Baghjan", surface_lat: 27.5925, surface_lon: 95.3688, kb_elevation_m: 130.2, total_depth_m: 4250.0, status: "COMPLETED" },
  { well_id: "c1f7a012-3b4c-4e89-9a11-000000000010", well_name: "SYN-BGJ-03", field_name: "Baghjan", surface_lat: 27.5701, surface_lon: 95.3395, kb_elevation_m: 127.0, total_depth_m: 3980.0, status: "COMPLETED" },
];

export default function Home() {
  const [wells, setWells] = useState<WellPoint[]>(DEFAULT_WELLS);
  const [activeWellName, setActiveWellName] = useState<string>("SYN-NHK-05");
  const [radiusKm, setRadiusKm] = useState<number>(5.0);
  const [activeTab, setActiveTab] = useState<NavTab>("overview");
  const [wsConnected, setWsConnected] = useState<boolean>(false);
  const [isExporting, setIsExporting] = useState<boolean>(false);

  const [depthMd, setDepthMd] = useState<number>(2410.0);
  const [history, setHistory] = useState<Array<{ depth: number; mse: number; rop: number; torque: number }>>([]);

  const activeWell = wells.find((w) => w.well_name === activeWellName) || wells[0];
  const hazardDepthMd = 2448.5;
  const isAlertActive = depthMd >= 2413.0;
  const distanceAheadM = Math.max(0, hazardDepthMd - depthMd);
  const riskIndex = isAlertActive ? Math.min(94.8, 84.2 + (depthMd - 2413.0) * 3.5) : 42.0;
  const tvdss = 2180.5 + (depthMd - 2410.0) * 0.99;

  const [telemetry, setTelemetry] = useState<TelemetryData>({
    measured_depth_m: 2410.0, tvdss_m: 2180.5, rop_mhr: 18.5, wob_klbs: 18.2,
    surface_torque_kftlb: 12.8, rpm: 95.0, standpipe_pressure_psi: 2950.0,
    flow_rate_gpm: 640.0, mud_density_in_sg: 1.16, mud_density_out_sg: 1.16,
    ecd_downhole_sg: 1.21, gas_total_pct: 1.85, pit_volume_gain_bbls: 0.2,
    teale_mse_psi: 36420, mse_baseline_ratio: 1.05, is_alert: false,
  });

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/wells?include_real=true`)
      .then((r) => { if (!r.ok) throw 0; return r.json(); })
      .then((d) => { if (Array.isArray(d) && d.length > 0) setWells(d); })
      .catch(() => {});
  }, []);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let interval: NodeJS.Timeout | null = null;
    try {
      ws = new WebSocket(`${process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"}/ws/v1/telemetry`);
      ws.onopen = () => setWsConnected(true);
      ws.onmessage = (ev) => {
        try {
          const d = JSON.parse(ev.data);
          if (d?.telemetry) {
            const cur = d.telemetry.measured_depth_m;
            const alert = d.lookahead_status?.active_alert || cur >= 2413.0;
            setDepthMd(cur);
            const td: TelemetryData = {
              measured_depth_m: cur, tvdss_m: d.telemetry.tvdss_m,
              rop_mhr: d.telemetry.rop_mhr, wob_klbs: d.telemetry.wob_klbs,
              surface_torque_kftlb: d.telemetry.surface_torque_kftlb, rpm: d.telemetry.rpm,
              standpipe_pressure_psi: d.telemetry.standpipe_pressure_psi,
              flow_rate_gpm: d.telemetry.flow_rate_gpm,
              mud_density_in_sg: d.telemetry.mud_density_in_sg,
              mud_density_out_sg: d.telemetry.mud_density_out_sg,
              ecd_downhole_sg: d.telemetry.ecd_downhole_sg,
              gas_total_pct: d.telemetry.gas_total_pct,
              pit_volume_gain_bbls: d.telemetry.pit_volume_gain_bbls,
              teale_mse_psi: d.instantaneous_physics?.teale_mse_psi || 36420,
              mse_baseline_ratio: alert ? 1.45 : 1.05, is_alert: alert,
            };
            setTelemetry(td);
            setHistory((p) => [...p.slice(-15), { depth: cur, mse: td.teale_mse_psi, rop: td.rop_mhr, torque: td.surface_torque_kftlb }]);
          }
        } catch {}
      };
      ws.onerror = ws.onclose = () => setWsConnected(false);
    } catch { setWsConnected(false); }

    interval = setInterval(() => {
      setDepthMd((p) => {
        const n = Number((p + 0.1).toFixed(2));
        const a = n >= 2413.0;
        setTelemetry((c) => ({
          ...c, measured_depth_m: n,
          tvdss_m: Number((2180.5 + (n - 2410.0) * 0.99).toFixed(1)),
          teale_mse_psi: a ? 52800 : 36420, mse_baseline_ratio: a ? 1.45 : 1.05,
          is_alert: a, rop_mhr: a ? 12.2 : 18.5, surface_torque_kftlb: a ? 15.4 : 12.8,
        }));
        return n;
      });
    }, 1000);

    return () => { ws?.close(); if (interval) clearInterval(interval); };
  }, []);

  const handleExportPdf = async () => {
    setIsExporting(true);
    try {
      const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/reports/tour-advisory`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ active_well_name: activeWellName, depth_md_m: depthMd, tvdss_m: tvdss, projected_hazard: "DIFFERENTIAL_STICKING", risk_index: riskIndex, evidence_well: "SYN-NHK-01", historical_npt_hours: 38.5 }),
      });
      if (!r.ok) throw 0;
      const blob = await r.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = `OIL_TourAdvisory_${activeWellName}_${depthMd.toFixed(0)}m.pdf`;
      document.body.appendChild(a); a.click(); URL.revokeObjectURL(url); a.remove();
    } catch { alert("PDF export — ensure backend at http://localhost:8000"); }
    finally { setIsExporting(false); }
  };

  const handleTriggerAlert = () => setDepthMd(2414.0);
  const handleAdvanceDepth = () => setDepthMd((d) => Number((d + 1.0).toFixed(1)));
  const handleResetSim = () => setDepthMd(2410.0);

  // ── Shared props ──
  const mapProps = {
    wells,
    activeWell,
    radiusKm,
    setRadiusKm,
    onSelectWell: (w: WellPoint) => setActiveWellName(w.well_name),
  };
  const curtainProps = { currentDepthMd: depthMd, currentTvdss: tvdss, hazardDepthMd, isAlertActive };
  const lookAheadProps = { currentDepthMd: depthMd, currentTvdss: tvdss, riskIndex, isAlertActive, distanceAheadM, onExportPdf: handleExportPdf, onTriggerAlert: handleTriggerAlert, onAdvanceDepth: handleAdvanceDepth, onResetSim: handleResetSim, isExporting };
  const telemetryProps = { telemetry, history };

  // ── Doghouse is special ──
  if (activeTab === "doghouse") {
    return (
      <div className="min-h-screen flex flex-col bg-slate-50">
        <Header
          isDoghouseMode={true}
          setIsDoghouseMode={() => setActiveTab("overview")}
          wsConnected={wsConnected}
          activeWellName={activeWellName}
          onSelectWell={setActiveWellName}
          wellsList={wells}
          onTriggerAlert={handleTriggerAlert}
          onResetSim={handleResetSim}
          onExportPdf={handleExportPdf}
          isAlertActive={isAlertActive}
        />
        <TopNav
          activeTab={activeTab}
          onTabChange={setActiveTab}
          isAlertActive={isAlertActive}
          currentDepthMd={depthMd}
          currentTvdss={tvdss}
          riskIndex={riskIndex}
        />
        <DoghouseView
          telemetry={telemetry}
          riskIndex={riskIndex}
          isAlertActive={isAlertActive}
          distanceAheadM={distanceAheadM}
          onExitDoghouse={() => setActiveTab("overview")}
          onExportPdf={handleExportPdf}
          onTriggerAlert={handleTriggerAlert}
          onResetSim={handleResetSim}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      {/* ── Unified Executive Header ── */}
      <Header
        isDoghouseMode={false}
        setIsDoghouseMode={() => setActiveTab("doghouse")}
        wsConnected={wsConnected}
        activeWellName={activeWellName}
        onSelectWell={setActiveWellName}
        wellsList={wells}
        onTriggerAlert={handleTriggerAlert}
        onResetSim={handleResetSim}
        onExportPdf={handleExportPdf}
        isAlertActive={isAlertActive}
      />

      {/* ── Navigation Tab Bar ── */}
      <TopNav
        activeTab={activeTab}
        onTabChange={setActiveTab}
        isAlertActive={isAlertActive}
        currentDepthMd={depthMd}
        currentTvdss={tvdss}
        riskIndex={riskIndex}
      />

      {/* ── Panel Content ── */}
      <main className="flex-1 w-full mx-auto px-4 py-4" style={{ maxWidth: 1720 }}>

        {/* ════ INNOVATIONS ════ */}
        {activeTab === "innovations" && (
          <InnovationsConsole currentDepthMd={depthMd} />
        )}

        {/* ════ OVERVIEW ════ */}
        {activeTab === "overview" && (
          <div className="space-y-4">
            {/* 🇮🇳 Indian Location & Rig Proximity Quick Banner */}
            <div className="bg-gradient-to-r from-emerald-950 via-slate-900 to-amber-950 text-white rounded-xl p-3 px-4 border border-emerald-800/40 shadow-sm flex flex-wrap items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                <span className="font-mono font-bold text-amber-300">🇮🇳 INDIAN BASIN CORRELATION ACTIVE:</span>
                <span className="text-slate-200">
                  Assam-Arakan Basin (Upper Assam Shelf) · Nahorkatiya Play · Operator: <strong>Oil India Limited</strong>
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setActiveTab("ml-station")}
                  className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-indigo-700 hover:bg-indigo-600 text-white text-[11px] font-bold transition-all shadow-xs"
                >
                  <span>🧠 ML Station (14 Models)</span>
                  <span>→</span>
                </button>
                <button
                  onClick={() => setActiveTab("indian-basins")}
                  className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-bold transition-all shadow-xs"
                >
                  <span>📍 GPS & Proximity Map</span>
                  <span>→</span>
                </button>
                <button
                  onClick={() => setActiveTab("ai-assistant")}
                  className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-purple-700 hover:bg-purple-600 text-white text-[11px] font-bold transition-all shadow-xs"
                >
                  <span>✨ AI Evidence (Gemini 2.5)</span>
                  <span>→</span>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <MapTilerLiveMap {...mapProps} />
              <CurtainSection {...curtainProps} />
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <AnalogCorrelationPanel />
              <MultiRiskPanel currentDepthMd={depthMd} />
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <LookAheadCard {...lookAheadProps} />
              <TelemetryTrack {...telemetryProps} />
            </div>
          </div>
        )}

        {/* ════ BASIN MAP ════ */}
        {activeTab === "basin-map" && (
          <div className="space-y-4">
            <MapTilerLiveMap {...mapProps} />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {/* Well roster */}
              <div className="card col-span-1">
                <div className="card-header">
                  <div className="flex items-center gap-2">
                    <div className="icon-chip icon-chip-pine">
                      <span className="text-xs font-black">🛢</span>
                    </div>
                    <h3 className="font-heading font-bold text-[13px]" style={{ color: "var(--text-primary)" }}>
                      Well Roster — {wells.length} Loaded
                    </h3>
                  </div>
                </div>
                <div className="card-body space-y-1.5 max-h-72 overflow-y-auto">
                  {wells.map((w) => {
                    const isActive = w.well_name === activeWellName;
                    return (
                      <button
                        key={w.well_name}
                        onClick={() => setActiveWellName(w.well_name)}
                        className="w-full text-left flex items-center justify-between px-3 py-2 rounded-lg transition-all text-xs"
                        style={{
                          background: isActive ? "var(--pine-pale)" : "var(--surface-2)",
                          border: `1px solid ${isActive ? "#2d8a67" : "var(--border)"}`,
                        }}
                      >
                        <div>
                          <div className="font-mono font-bold" style={{ color: isActive ? "var(--pine)" : "var(--text-primary)" }}>
                            {w.well_name}
                          </div>
                          <div className="text-[10px]" style={{ color: "var(--text-muted)" }}>{w.field_name} · TD {w.total_depth_m}m</div>
                        </div>
                        <span
                          className="badge"
                          style={{
                            background: w.status === "DRILLING" ? "#ecfdf5" : "#f1f5f9",
                            color: w.status === "DRILLING" ? "#059669" : "#64748b",
                            borderColor: w.status === "DRILLING" ? "#a7f3d0" : "#e2e8f0",
                          }}
                        >
                          {w.status}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Weather + Info */}
              <div className="card col-span-2 p-4 space-y-4">
                <RigWeatherWidget lat={activeWell?.surface_lat} lon={activeWell?.surface_lon} />
                <div
                  className="rounded-xl p-4 text-xs space-y-2"
                  style={{ background: "var(--surface-2)", border: "1px solid var(--border)" }}
                >
                  <div className="font-heading font-bold text-[13px] mb-3" style={{ color: "var(--text-primary)" }}>
                    Active Well Details
                  </div>
                  <div className="grid grid-cols-2 gap-x-6 gap-y-2 font-mono">
                    {[
                      { label: "Well Name", val: activeWell?.well_name },
                      { label: "Field", val: activeWell?.field_name },
                      { label: "Status", val: activeWell?.status },
                      { label: "Total Depth", val: `${activeWell?.total_depth_m || "—"}m` },
                      { label: "KB Elevation", val: `${activeWell?.kb_elevation_m || "—"}m` },
                      { label: "Latitude", val: `${activeWell?.surface_lat.toFixed(4)}°N` },
                      { label: "Longitude", val: `${activeWell?.surface_lon.toFixed(4)}°E` },
                      { label: "Bit Depth (MD)", val: `${depthMd.toFixed(2)}m` },
                    ].map((r) => (
                      <div key={r.label}>
                        <div className="text-[9px] uppercase font-semibold mb-0.5" style={{ color: "var(--text-muted)" }}>{r.label}</div>
                        <div className="font-bold" style={{ color: "var(--text-primary)" }}>{r.val}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ════ GEOLOGICAL SECTION ════ */}
        {activeTab === "geological" && (
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
            <div className="xl:col-span-2">
              <CurtainSection {...curtainProps} />
            </div>
            <div className="space-y-4">
              {/* Formation Table */}
              <div className="card">
                <div className="card-header">
                  <h3 className="font-heading font-bold text-[13px]" style={{ color: "var(--text-primary)" }}>
                    Stratigraphic Column
                  </h3>
                </div>
                <div className="card-body p-0">
                  <table className="w-full text-xs">
                    <thead>
                      <tr style={{ background: "var(--surface-2)", borderBottom: "1px solid var(--border)" }}>
                        {["Formation", "Top (m)", "Hazard"].map((h) => (
                          <th key={h} className="px-3 py-2 text-left text-[10px] font-bold uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { name: "Dihing Group", top: 0, hazard: null },
                        { name: "Dupi Tila Ss.", top: 350, hazard: null },
                        { name: "Girujan Clay", top: 700, hazard: "Swelling Shale" },
                        { name: "Upper Tipam Ss.", top: 1850, hazard: "Diff. Sticking ⚠" },
                        { name: "Lower Tipam Ss.", top: 2520, hazard: null },
                        { name: "Barail Coal-Shale", top: 2900, hazard: "Overpressure" },
                        { name: "Kopili Fm.", top: 3500, hazard: "Sloughing Shale" },
                        { name: "Sylhet Ls.", top: 4100, hazard: "Karst Losses" },
                      ].map((f, i) => (
                        <tr key={f.name} style={{ borderBottom: "1px solid var(--border)", background: i % 2 === 0 ? "var(--surface)" : "var(--surface-2)" }}>
                          <td className="px-3 py-2 font-semibold" style={{ color: "var(--text-primary)" }}>{f.name}</td>
                          <td className="px-3 py-2 font-mono" style={{ color: "var(--text-secondary)" }}>{f.top}</td>
                          <td className="px-3 py-2">
                            {f.hazard ? (
                              <span className="badge badge-warning" style={{ fontSize: 9 }}>{f.hazard}</span>
                            ) : (
                              <span className="text-[10px]" style={{ color: "var(--text-muted)" }}>—</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Current Depth */}
              <div
                className="card p-4 text-center"
                style={{ background: isAlertActive ? "#fef2f2" : "var(--surface)", borderColor: isAlertActive ? "#fca5a5" : "var(--border)" }}
              >
                <div className="text-[10px] uppercase font-bold tracking-wider mb-1" style={{ color: "var(--text-muted)" }}>Active Bit Position</div>
                <div className="font-mono font-black text-3xl mb-1" style={{ color: isAlertActive ? "#dc2626" : "var(--pine)" }}>
                  {depthMd.toFixed(2)} m
                </div>
                <div className="text-[11px] font-mono" style={{ color: "var(--text-secondary)" }}>TVDSS: {tvdss.toFixed(1)}m</div>
                <div className="mt-2 pt-2" style={{ borderTop: "1px solid var(--border)" }}>
                  <span className={`badge ${isAlertActive ? "badge-danger" : "badge-success"}`}>
                    {isAlertActive ? "HAZARD ZONE" : "NORMAL"}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ════ RISK ENGINE ════ */}
        {activeTab === "risk-engine" && (
          <div className="space-y-4">
            <MultiRiskPanel currentDepthMd={depthMd} />
            <AnalogCorrelationPanel />
          </div>
        )}

        {/* ════ TELEMETRY ════ */}
        {activeTab === "telemetry" && (
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
            <div className="xl:col-span-2">
              <TelemetryTrack {...telemetryProps} />
            </div>
            <div className="space-y-4">
              {/* Quick stats */}
              <div className="card p-4">
                <h3 className="font-heading font-bold text-[13px] mb-3" style={{ color: "var(--text-primary)" }}>
                  Real-Time Rig Parameters
                </h3>
                <div className="space-y-2">
                  {[
                    { label: "Bit Depth (MD)", val: `${telemetry.measured_depth_m.toFixed(2)} m`, alert: false },
                    { label: "TVDSS", val: `${telemetry.tvdss_m.toFixed(1)} m`, alert: false },
                    { label: "ROP", val: `${telemetry.rop_mhr.toFixed(1)} m/h`, alert: telemetry.is_alert },
                    { label: "WOB", val: `${telemetry.wob_klbs.toFixed(1)} klbs`, alert: false },
                    { label: "Torque", val: `${telemetry.surface_torque_kftlb.toFixed(1)} kft-lb`, alert: telemetry.is_alert },
                    { label: "RPM", val: `${telemetry.rpm.toFixed(0)} rpm`, alert: false },
                    { label: "SPP", val: `${telemetry.standpipe_pressure_psi} psi`, alert: false },
                    { label: "Flow Rate", val: `${telemetry.flow_rate_gpm} gpm`, alert: false },
                    { label: "MW In", val: `${telemetry.mud_density_in_sg} SG`, alert: false },
                    { label: "ECD", val: `${telemetry.ecd_downhole_sg} SG`, alert: false },
                    { label: "Total Gas", val: `${telemetry.gas_total_pct.toFixed(2)}%`, alert: telemetry.is_alert },
                    { label: "Teale MSE", val: `${telemetry.teale_mse_psi.toLocaleString()} psi`, alert: telemetry.is_alert },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center justify-between px-3 py-2 rounded-lg text-xs"
                      style={{ background: item.alert ? "#fef2f2" : "var(--surface-2)", border: `1px solid ${item.alert ? "#fca5a5" : "var(--border)"}` }}>
                      <span style={{ color: "var(--text-secondary)" }}>{item.label}</span>
                      <span className="font-mono font-bold" style={{ color: item.alert ? "#dc2626" : "var(--text-primary)" }}>{item.val}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ════ CORRELATION ════ */}
        {activeTab === "correlation" && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            <div className="xl:col-span-2">
              <AnalogCorrelationPanel />
            </div>
          </div>
        )}

        {/* ════ LOOK-AHEAD ════ */}
        {activeTab === "lookahead" && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            <LookAheadCard {...lookAheadProps} />
            <div className="space-y-4">
              <CurtainSection {...curtainProps} />
            </div>
          </div>
        )}

        {/* ════ ENGINEERING CONSOLE (P0/P1) ════ */}
        {activeTab === "engineering" && (
          <EngineeringConsole activeDepthMd={depthMd} />
        )}

        {/* ════ INDIAN BASINS & RIG LOCATOR ════ */}
        {activeTab === "indian-basins" && (
          <IndianLocationConsole />
        )}

        {/* ════ ML INTELLIGENCE STATION (14 MODELS & DTW) ════ */}
        {activeTab === "ml-station" && (
          <MLIntelligenceStation activeDepthMd={depthMd} />
        )}

        {/* ════ AI GROUNDED EVIDENCE ASSISTANT (GEMINI 2.5) ════ */}
        {activeTab === "ai-assistant" && (
          <GroundedAIAssistant activeDepthMd={depthMd} />
        )}

        {/* ════ REAL DATA STACK ════ */}
        {activeTab === "real-data" && (
          <RealDataViewer />
        )}
      </main>

      {/* ── Footer ── */}
      <footer className="py-3 px-6 mt-2" style={{ background: "var(--surface)", borderTop: "1px solid var(--border)" }}>
        <div className="flex flex-wrap items-center justify-between gap-3 text-xs" style={{ maxWidth: 1720, margin: "0 auto" }}>
          <div className="flex items-center gap-3">
            <span className="font-mono font-black text-[11px] px-2 py-0.5 rounded" style={{ background: "var(--pine)", color: "white" }}>OIL</span>
            <span className="font-heading font-bold" style={{ color: "var(--text-primary)" }}>Oil India Limited · eRTMAC-NWIS</span>
            <span style={{ color: "var(--border-strong)" }}>|</span>
            <span style={{ color: "var(--text-muted)" }}>SIH26121 · Nearby Wells Intelligence System</span>
          </div>
          <span className="font-mono" style={{ color: "var(--text-muted)", fontSize: 10 }}>
            MCM 3D · Dip-Rotated TSD · Teale MSE · Outmans Differential Sticking Model · MapTiler v4
          </span>
        </div>
      </footer>
    </div>
  );
}
