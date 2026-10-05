"use client";

import React from "react";
import {
  ShieldAlert, AlertTriangle, RotateCw, Droplets,
  FileDown, X, Gauge, TrendingDown, Activity, FastForward, RefreshCw,
} from "lucide-react";
import { TelemetryData } from "./TelemetryTrack";

interface DoghouseViewProps {
  telemetry: TelemetryData;
  riskIndex: number;
  isAlertActive: boolean;
  distanceAheadM: number;
  onExitDoghouse: () => void;
  onExportPdf: () => void;
  onTriggerAlert: () => void;
  onResetSim: () => void;
}

export const DoghouseView: React.FC<DoghouseViewProps> = ({
  telemetry, riskIndex, isAlertActive, distanceAheadM,
  onExitDoghouse, onExportPdf, onTriggerAlert, onResetSim,
}) => {
  const riskColor = riskIndex > 70 ? "#dc2626" : riskIndex > 40 ? "#d97706" : "#059669";

  const mainGauges = [
    { label: "Bit Depth (MD)", value: telemetry.measured_depth_m.toFixed(2), unit: "m", color: "var(--pine)" },
    { label: "ROP", value: telemetry.rop_mhr.toFixed(1), unit: "m/h", color: isAlertActive ? "#dc2626" : "var(--text-primary)" },
    { label: "WOB", value: telemetry.wob_klbs.toFixed(1), unit: "klbs", color: "var(--text-primary)" },
    { label: "Torque", value: telemetry.surface_torque_kftlb.toFixed(1), unit: "kft-lb", color: isAlertActive ? "#dc2626" : "var(--text-primary)" },
    { label: "RPM", value: telemetry.rpm.toFixed(0), unit: "rpm", color: "var(--text-primary)" },
    { label: "SPP", value: telemetry.standpipe_pressure_psi.toFixed(0), unit: "psi", color: "#2563eb" },
    { label: "ECD", value: telemetry.ecd_downhole_sg.toFixed(3), unit: "SG", color: "#7c3aed" },
    { label: "Total Gas", value: telemetry.gas_total_pct.toFixed(2), unit: "%", color: isAlertActive ? "#dc2626" : "#059669" },
  ];

  return (
    <div
      className="min-h-screen flex flex-col p-4 md:p-6"
      style={{ background: "var(--canvas)" }}
    >
      {/* Doghouse Header */}
      <div
        className="flex items-center justify-between pb-4 mb-4"
        style={{ borderBottom: "2px solid var(--border)" }}
      >
        <div className="flex items-center gap-3">
          <div
            className="font-mono font-black text-xl px-3.5 py-1.5 rounded-xl"
            style={{ background: "var(--pine)", color: "white" }}
          >
            OIL
          </div>
          <div>
            <h1 className="text-xl font-heading font-black" style={{ color: "var(--text-primary)" }}>
              RIG DOGHOUSE CONSOLE · SYN-NHK-05
            </h1>
            <p className="text-xs font-mono mt-0.5" style={{ color: "var(--text-muted)" }}>
              SYNTHETIC — Assam Basin Profile · SPE-197489-MS Calibrated
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div
            className="px-3.5 py-2 rounded-xl text-right"
            style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
          >
            <div className="text-[10px] uppercase font-bold" style={{ color: "var(--text-muted)" }}>
              WITSML Telemetry
            </div>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className="live-dot" />
              <span className="text-xs font-mono font-bold" style={{ color: "var(--success)" }}>1 Hz LIVE</span>
            </div>
          </div>

          <button
            onClick={onExitDoghouse}
            className="btn btn-outline flex items-center gap-2"
          >
            <X className="w-4 h-4" style={{ color: "#dc2626" }} />
            Standard View
          </button>
        </div>
      </div>

      {/* Main Alert Banner */}
      <div
        className={`mb-5 p-5 rounded-2xl transition-all duration-300 ${isAlertActive ? "anim-breathe" : ""}`}
        style={{
          background: isAlertActive ? "#fef2f2" : "var(--pine-pale)",
          border: `3px solid ${isAlertActive ? "#dc2626" : "var(--pine)"}`,
          boxShadow: isAlertActive ? "0 0 30px rgba(220,38,38,0.18)" : "none"
        }}
      >
        <div className="flex items-center gap-3 mb-3">
          {isAlertActive
            ? <ShieldAlert className="w-8 h-8" style={{ color: "#dc2626" }} />
            : <AlertTriangle className="w-8 h-8" style={{ color: "var(--pine)" }} />
          }
          <div>
            <div className="text-2xl font-black font-heading" style={{ color: isAlertActive ? "#dc2626" : "var(--pine)" }}>
              {isAlertActive ? "🚨 CRITICAL HAZARD ACTIVE" : "⚠ ADVISORY WATCH — HAZARD APPROACHING"}
            </div>
            <div className="text-sm font-mono mt-0.5" style={{ color: "var(--text-secondary)" }}>
              Differential Sticking · Upper Tipam Depleted Sandstone (0.88 SG)
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "Bit Depth (MD)", value: `${telemetry.measured_depth_m.toFixed(2)} m`, color: isAlertActive ? "#dc2626" : "var(--pine)" },
            { label: "Delta to Hazard", value: `${distanceAheadM.toFixed(1)} m`, color: isAlertActive ? "#dc2626" : "#d97706" },
            { label: "Risk Index (R_H)", value: `${riskIndex.toFixed(1)}%`, color: riskColor },
            { label: "Teale MSE", value: `${telemetry.teale_mse_psi.toLocaleString()} psi`, color: isAlertActive ? "#dc2626" : "#d97706" },
          ].map((item) => (
            <div
              key={item.label}
              className="text-center p-3 rounded-xl"
              style={{ background: "rgba(255,255,255,0.6)", border: "1px solid rgba(255,255,255,0.8)" }}
            >
              <div className="text-xs uppercase font-bold tracking-wider mb-1" style={{ color: "var(--text-muted)" }}>
                {item.label}
              </div>
              <div className="font-mono font-black text-2xl" style={{ color: item.color }}>
                {item.value}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Live Sensor Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
        {mainGauges.map((g) => (
          <div
            key={g.label}
            className="rounded-xl p-4 text-center"
            style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
          >
            <div className="text-[10px] uppercase font-bold tracking-wider mb-2" style={{ color: "var(--text-muted)" }}>
              {g.label}
            </div>
            <div className="font-mono font-black text-3xl" style={{ color: g.color }}>
              {g.value}
            </div>
            <div className="text-xs mt-1 font-mono" style={{ color: "var(--text-muted)" }}>{g.unit}</div>
          </div>
        ))}
      </div>

      {/* Emergency SOP */}
      <div
        className="rounded-2xl p-5 mb-5"
        style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
      >
        <div className="font-heading font-bold text-lg mb-3 flex items-center gap-2" style={{ color: "var(--text-primary)" }}>
          <ShieldAlert className="w-5 h-5" style={{ color: isAlertActive ? "#dc2626" : "#d97706" }} />
          Emergency Mitigation Protocol — Driller SOP
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            { step: 1, action: "STOP — Immediately cease drillstring stationary time", critical: true },
            { step: 2, action: "ROTATE — Maintain >40 RPM continuous rotation", critical: true },
            { step: 3, action: "SPOT PILL — Spot 40 bbl lubricating pill if stuck", critical: false },
            { step: 4, action: "REDUCE MUD DENSITY — Adjust ECD to 1.10 SG if Girujan Clay permits", critical: false },
          ].map((s) => (
            <div
              key={s.step}
              className="flex items-start gap-3 p-3.5 rounded-xl"
              style={{
                background: s.critical ? "#fef2f2" : "var(--surface-2)",
                border: `1px solid ${s.critical ? "#fca5a5" : "var(--border)"}`
              }}
            >
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center font-black text-sm flex-shrink-0"
                style={{ background: s.critical ? "#dc2626" : "var(--pine)", color: "white" }}
              >
                {s.step}
              </div>
              <div>
                <div className="font-bold text-sm" style={{ color: s.critical ? "#dc2626" : "var(--text-primary)" }}>
                  {s.action}
                </div>
                {s.critical && (
                  <span className="badge badge-danger mt-1">MANDATORY</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Bar */}
      <div
        className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-2xl"
        style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
      >
        <div className="flex items-center gap-3">
          <button className="btn btn-danger flex items-center gap-2" onClick={onTriggerAlert}>
            <FastForward className="w-4 h-4" />
            Simulate Alert (2,414m)
          </button>
          <button className="btn btn-outline flex items-center gap-2" onClick={onResetSim}>
            <RefreshCw className="w-4 h-4" />
            Reset Simulation
          </button>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-xs font-mono px-3 py-1.5 rounded-lg" style={{ background: "#fffbeb", color: "#92400e", border: "1px solid #fde68a" }}>
            ⚠ Qualified Engineer Review Required — Decision Support Only
          </div>
          <button onClick={onExportPdf} className="btn btn-amber flex items-center gap-2">
            <FileDown className="w-4 h-4" />
            Download Tour Advisory PDF
          </button>
        </div>
      </div>
    </div>
  );
};
