"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  ShieldAlert,
  FileDown,
  CheckCircle2,
  Clock,
  MapPin,
  TrendingUp,
  Flame,
  ArrowRight,
  RefreshCw,
  FastForward,
} from "lucide-react";

interface LookAheadProps {
  currentDepthMd: number;
  currentTvdss: number;
  riskIndex: number;
  isAlertActive: boolean;
  distanceAheadM: number;
  onExportPdf: () => void;
  onTriggerAlert: () => void;
  onAdvanceDepth: () => void;
  onResetSim: () => void;
  isExporting: boolean;
}

export const LookAheadCard: React.FC<LookAheadProps> = ({
  currentDepthMd,
  currentTvdss,
  riskIndex,
  isAlertActive,
  distanceAheadM,
  onExportPdf,
  onTriggerAlert,
  onAdvanceDepth,
  onResetSim,
  isExporting,
}) => {
  const [mitigationsChecked, setMitigationsChecked] = useState<{ [key: number]: boolean }>({
    0: true,
    1: false,
    2: false,
    3: false,
  });

  const toggleMitigation = (index: number) => {
    setMitigationsChecked((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const mitigations = [
    {
      title: "Stationary Drillstring Limitation",
      desc: "Strictly limit stationary drillstring time to < 90 seconds across 2,430m – 2,480m MD.",
      critical: true,
    },
    {
      title: "Mud Density Adjustment",
      desc: "Reduce active mud system density from 1.16 SG to 1.10 SG if overlying Girujan Clay permits.",
      critical: false,
    },
    {
      title: "Lubricating Pill Pre-Spotting",
      desc: "Spot 40 bbls lubricating / anti-sticking pill prior to traversing depleted sand package.",
      critical: true,
    },
    {
      title: "Continuous Drillstring Rotation",
      desc: "Maintain continuous drillstring rotation (>40 RPM) during all MWD survey operations.",
      critical: false,
    },
  ];

  return (
    <div
      className={`rounded-lg border shadow-md overflow-hidden flex flex-col h-full transition-all duration-300 ${
        isAlertActive
          ? "border-red-400 bg-white ring-2 ring-red-500/20"
          : "border-[#E2E8F0] bg-white"
      }`}
    >
      {/* Alert Header Banner */}
      <div
        className={`px-4 py-3 flex items-center justify-between transition-colors ${
          isAlertActive
            ? "bg-[#D9381E] text-white animate-pulse-subtle"
            : "bg-[#184E3A] text-white"
        }`}
      >
        <div className="flex items-center gap-2.5">
          {isAlertActive ? (
            <ShieldAlert className="w-5 h-5 text-amber-300 animate-bounce" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-[#E58A13]" />
          )}
          <div>
            <div className="font-extrabold text-sm tracking-wide uppercase flex items-center gap-2">
              <span>Panel 3 · Real-Time Look-Ahead Advisory</span>
              <span
                className={`text-[10px] px-2 py-0.5 rounded font-black tracking-wider ${
                  isAlertActive
                    ? "bg-white text-[#D9381E]"
                    : "bg-[#E58A13] text-[#1E242B]"
                }`}
              >
                {isAlertActive ? "CRITICAL ALERT" : "ADVISORY WATCH"}
              </span>
            </div>
            <p className="text-[11px] opacity-90">
              Offset-calibrated predictive hazard intelligence for active drill bit
            </p>
          </div>
        </div>

        {/* Risk Index Badge */}
        <div className="text-right">
          <div className="text-[10px] uppercase font-bold tracking-wider opacity-85">
            Risk Index (R_H)
          </div>
          <div className="font-black text-xl font-mono">
            {riskIndex.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Hazard Summary Card */}
      <div className="p-4 space-y-4 flex-1">
        {/* Main Alert Box */}
        <div
          className={`p-3.5 rounded-lg border flex flex-col md:flex-row gap-3 items-start justify-between ${
            isAlertActive
              ? "bg-red-50/90 border-red-200"
              : "bg-amber-50/70 border-amber-200"
          }`}
        >
          <div>
            <div className="flex items-center gap-2">
              <span
                className={`font-black text-sm uppercase tracking-wide ${
                  isAlertActive ? "text-red-900" : "text-amber-900"
                }`}
              >
                Differential Sticking Hazard Ahead
              </span>
              <span className="text-[11px] font-bold text-gray-600 bg-white px-2 py-0.5 rounded border border-gray-200">
                Upper Tipam Sandstone
              </span>
            </div>
            <p className="text-xs text-gray-700 mt-1">
              Active bit is approaching a depleted sandstone horizon (Pore Pressure:{" "}
              <strong>0.88 SG</strong>). Differential overbalance pressure is{" "}
              <strong className="text-red-700">1,120 psi</strong>.
            </p>
          </div>

          <div className="flex items-center gap-4 border-l border-gray-200 pl-3 min-w-[140px]">
            <div>
              <div className="text-[10px] text-gray-500 font-bold uppercase">
                Distance Ahead
              </div>
              <div
                className={`font-mono text-lg font-black ${
                  isAlertActive ? "text-red-600" : "text-amber-600"
                }`}
              >
                {distanceAheadM.toFixed(1)}m
              </div>
            </div>
            <div>
              <div className="text-[10px] text-gray-500 font-bold uppercase">
                Horizon Depth
              </div>
              <div className="font-mono text-sm font-bold text-gray-800">
                2,448.5m MD
              </div>
            </div>
          </div>
        </div>

        {/* Corroborating Historical Offset Evidence */}
        <div className="bg-slate-50 rounded-lg p-3 border border-slate-200 text-xs">
          <div className="flex items-center justify-between mb-2">
            <span className="font-bold text-[#184E3A] flex items-center gap-1.5 uppercase text-[11px] tracking-wider">
              <MapPin className="w-3.5 h-3.5 text-[#E58A13]" />
              Corroborating Historical Evidence · SYN-NHK-01
            </span>
            <span className="font-mono text-gray-500 text-[11px]">
              Distance: 1.42 km SW · Identical Stratigraphic Horizon
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2 bg-white p-2.5 rounded border border-slate-200">
            <div>
              <div className="text-[10px] text-gray-500 uppercase font-semibold">
                Recorded Incident
              </div>
              <div className="font-bold text-red-700">Stuck Pipe (38.5 hrs NPT)</div>
            </div>
            <div>
              <div className="text-[10px] text-gray-500 uppercase font-semibold">
                Root Cause
              </div>
              <div className="text-gray-800">
                Stationary for 45 min during directional survey in depleted sand.
              </div>
            </div>
            <div>
              <div className="text-[10px] text-gray-500 uppercase font-semibold">
                Resolved By
              </div>
              <div className="text-gray-800">
                Spotted 40 bbls lubricating pill, rotated out with 55 RPM.
              </div>
            </div>
          </div>
        </div>

        {/* Actionable Tour Advisory Checklist */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="font-bold text-[#1E242B] text-xs uppercase tracking-wider flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-[#184E3A]" />
              Mandatory Tour Advisory Action Items
            </span>
            <span className="text-[11px] text-gray-500">
              Driller Sign-Off Required
            </span>
          </div>

          <div className="space-y-1.5">
            {mitigations.map((item, idx) => (
              <div
                key={idx}
                onClick={() => toggleMitigation(idx)}
                className={`p-2 rounded border flex items-start gap-2.5 cursor-pointer transition text-xs ${
                  mitigationsChecked[idx]
                    ? "bg-emerald-50/80 border-emerald-200 text-gray-900"
                    : "bg-white border-gray-200 text-gray-700 hover:bg-gray-50"
                }`}
              >
                <input
                  type="checkbox"
                  checked={!!mitigationsChecked[idx]}
                  onChange={() => {}}
                  className="mt-0.5 rounded text-[#184E3A] focus:ring-[#184E3A] cursor-pointer"
                />
                <div className="flex-1">
                  <div className="font-bold flex items-center gap-1.5">
                    <span>{item.title}</span>
                    {item.critical && (
                      <span className="text-[9px] bg-red-100 text-red-700 px-1.5 py-0.2 rounded font-black uppercase">
                        Mandatory
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-gray-600 mt-0.5">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Action Footer & Simulation Controls */}
      <div className="p-3 bg-gray-50 border-t border-[#E2E8F0] flex flex-wrap items-center justify-between gap-2">
        {/* Simulation Buttons for Live Demo */}
        <div className="flex items-center gap-1.5 text-xs">
          <button
            onClick={onTriggerAlert}
            className="flex items-center gap-1 px-2.5 py-1.5 bg-red-600 hover:bg-red-700 text-white font-bold rounded transition shadow-sm"
            title="Jump to 2,414m MD to trigger live alert"
          >
            <FastForward className="w-3.5 h-3.5" />
            <span>Simulate Threshold (2,414m)</span>
          </button>
          <button
            onClick={onAdvanceDepth}
            className="flex items-center gap-1 px-2 py-1.5 bg-white hover:bg-gray-100 text-gray-800 font-semibold rounded border border-gray-300 transition"
            title="Advance drill bit by +1.0m"
          >
            <ArrowRight className="w-3.5 h-3.5 text-[#184E3A]" />
            <span>+1m MD</span>
          </button>
          <button
            onClick={onResetSim}
            className="p-1.5 bg-white hover:bg-gray-100 text-gray-600 rounded border border-gray-300 transition"
            title="Reset Simulation to 2,410m"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* 1-Click PDF Export Button */}
        <button
          onClick={onExportPdf}
          disabled={isExporting}
          className="flex items-center gap-2 px-4 py-2 bg-[#E58A13] hover:bg-[#c9750b] text-[#1E242B] font-extrabold text-xs rounded shadow transition cursor-pointer disabled:opacity-50"
        >
          <FileDown className="w-4 h-4 text-[#1E242B]" />
          <span>{isExporting ? "Generating PDF..." : "Export Tour Advisory PDF"}</span>
        </button>
      </div>
    </div>
  );
};
