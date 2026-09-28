"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  ShieldAlert,
  FileDown,
  CheckCircle2,
  MapPin,
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
    2: true,
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
      desc: "Reduce mud density from 1.16 SG to 1.10 SG if overlying Girujan Clay permits.",
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
      className={`rounded-lg border shadow-sm overflow-hidden flex flex-col h-full transition-all duration-300 ${
        isAlertActive
          ? "border-red-400 bg-white ring-2 ring-red-500/20"
          : "border-[#E2E8F0] bg-white"
      }`}
    >
      {/* Alert Header Banner */}
      <div
        className={`px-3.5 py-2 flex items-center justify-between transition-colors ${
          isAlertActive
            ? "bg-[#D9381E] text-white animate-pulse-subtle"
            : "bg-[#184E3A] text-white"
        }`}
      >
        <div className="flex items-center gap-2">
          {isAlertActive ? (
            <ShieldAlert className="w-4 h-4 text-amber-300 animate-bounce" />
          ) : (
            <AlertTriangle className="w-4 h-4 text-[#E58A13]" />
          )}
          <div>
            <div className="font-extrabold text-xs tracking-wide uppercase flex items-center gap-1.5">
              <span>Panel 3 · Real-Time Look-Ahead Advisory</span>
              <span
                className={`text-[9.5px] px-1.5 py-0.2 rounded font-black tracking-wider ${
                  isAlertActive
                    ? "bg-white text-[#D9381E]"
                    : "bg-[#E58A13] text-[#1E242B]"
                }`}
              >
                {isAlertActive ? "CRITICAL ALERT" : "ADVISORY WATCH"}
              </span>
            </div>
          </div>
        </div>

        {/* Risk Index Badge */}
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] uppercase font-bold tracking-wider opacity-85">
            Risk Index (R_H):
          </span>
          <span className="font-black text-base font-mono bg-black/25 px-2 py-0.5 rounded">
            {riskIndex.toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Main Alert Content Body */}
      <div className="p-3 space-y-2.5 flex-1 flex flex-col justify-between">
        {/* Main Alert Box */}
        <div
          className={`p-2.5 rounded-lg border flex items-center justify-between gap-3 ${
            isAlertActive
              ? "bg-red-50/90 border-red-200"
              : "bg-amber-50/70 border-amber-200"
          }`}
        >
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span
                className={`font-black text-xs uppercase tracking-wide ${
                  isAlertActive ? "text-red-900" : "text-amber-900"
                }`}
              >
                Differential Sticking Hazard Ahead
              </span>
              <span className="text-[10px] font-bold text-gray-600 bg-white px-1.5 py-0.2 rounded border border-gray-200">
                Upper Tipam Sand
              </span>
            </div>
            <p className="text-[11px] text-gray-700 mt-0.5 leading-snug">
              Depleted sandstone pore pressure: <strong>0.88 SG</strong>. Overbalance pressure:{" "}
              <strong className="text-red-700">1,120 psi</strong>.
            </p>
          </div>

          <div className="flex items-center gap-3 border-l border-gray-200 pl-3 flex-shrink-0 text-center">
            <div>
              <div className="text-[9px] text-gray-500 font-bold uppercase">Delta Ahead</div>
              <div
                className={`font-mono text-base font-black ${
                  isAlertActive ? "text-red-600" : "text-amber-600"
                }`}
              >
                {distanceAheadM.toFixed(1)}m
              </div>
            </div>
            <div>
              <div className="text-[9px] text-gray-500 font-bold uppercase">Target Depth</div>
              <div className="font-mono text-xs font-bold text-gray-800">2,448.5m</div>
            </div>
          </div>
        </div>

        {/* Historical Evidence from SYN-NHK-01 */}
        <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-200 text-xs">
          <div className="flex items-center justify-between mb-1">
            <span className="font-bold text-[#184E3A] flex items-center gap-1 uppercase text-[10px] tracking-wider">
              <MapPin className="w-3 h-3 text-[#E58A13]" />
              Historical Grounding · SYN-NHK-01 Offset
            </span>
            <span className="font-mono text-gray-500 text-[10px]">
              1.42 km SW · Same Stratigraphic Horizon (+1.5m TSD)
            </span>
          </div>
          <div className="grid grid-cols-3 gap-2 bg-white p-2 rounded border border-slate-200 text-[11px]">
            <div>
              <div className="text-[9px] text-gray-500 uppercase font-semibold">Incident</div>
              <div className="font-bold text-red-700">Stuck Pipe (38.5h NPT)</div>
            </div>
            <div>
              <div className="text-[9px] text-gray-500 uppercase font-semibold">Root Cause</div>
              <div className="text-gray-800 text-[10px]">Stationary 45 min in survey</div>
            </div>
            <div>
              <div className="text-[9px] text-gray-500 uppercase font-semibold">Resolution</div>
              <div className="text-gray-800 text-[10px]">Spotted 40 bbls lubricant pill</div>
            </div>
          </div>
        </div>

        {/* Actionable Tour Advisory SOP Checklist */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="font-bold text-[#1E242B] text-[11px] uppercase tracking-wider flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#184E3A]" />
              Mandatory Tour Advisory Checklist (Driller SOP)
            </span>
            <span className="text-[10px] text-gray-500">Sign-off required</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
            {mitigations.map((item, idx) => (
              <div
                key={idx}
                onClick={() => toggleMitigation(idx)}
                className={`p-1.5 rounded border flex items-start gap-1.5 cursor-pointer transition text-xs ${
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
                <div className="flex-1 leading-tight">
                  <div className="font-bold text-[10.5px] flex items-center gap-1">
                    <span>{item.title}</span>
                    {item.critical && (
                      <span className="text-[8px] bg-red-100 text-red-700 px-1 py-0 rounded font-black uppercase">
                        Mandatory
                      </span>
                    )}
                  </div>
                  <p className="text-[9.5px] text-gray-500 mt-0.5 line-clamp-1">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Action Footer & Simulation Controls */}
      <div className="px-3 py-2 bg-gray-50 border-t border-[#E2E8F0] flex flex-wrap items-center justify-between gap-2">
        {/* Simulation Buttons */}
        <div className="flex items-center gap-1.5 text-xs">
          <button
            onClick={onTriggerAlert}
            className="flex items-center gap-1 px-2.5 py-1 bg-red-600 hover:bg-red-700 text-white font-bold rounded text-[11px] transition shadow-sm cursor-pointer"
            title="Jump to 2,414m MD to trigger live alert"
          >
            <FastForward className="w-3 h-3" />
            <span>Simulate (2,414m)</span>
          </button>
          <button
            onClick={onAdvanceDepth}
            className="flex items-center gap-1 px-2 py-1 bg-white hover:bg-gray-100 text-gray-800 font-semibold rounded border border-gray-300 text-[11px] transition cursor-pointer"
            title="Advance drill bit by +1.0m"
          >
            <ArrowRight className="w-3 h-3 text-[#184E3A]" />
            <span>+1m</span>
          </button>
          <button
            onClick={onResetSim}
            className="p-1 bg-white hover:bg-gray-100 text-gray-600 rounded border border-gray-300 text-[11px] transition cursor-pointer"
            title="Reset Simulation to 2,410m"
          >
            <RefreshCw className="w-3 h-3" />
          </button>
        </div>

        {/* 1-Click PDF Export Button */}
        <button
          onClick={onExportPdf}
          disabled={isExporting}
          className="flex items-center gap-1.5 px-3 py-1 bg-[#E58A13] hover:bg-[#cf7b0f] text-[#1E242B] font-extrabold text-xs rounded shadow transition cursor-pointer disabled:opacity-50"
        >
          <FileDown className="w-3.5 h-3.5" />
          <span>{isExporting ? "Exporting..." : "Download Tour Advisory PDF"}</span>
        </button>
      </div>
    </div>
  );
};
