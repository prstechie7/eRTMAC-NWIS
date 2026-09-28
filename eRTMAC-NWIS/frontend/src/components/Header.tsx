"use client";

import React from "react";
import { Activity, ShieldAlert, Tablet, Radio, Compass, FileText } from "lucide-react";

interface HeaderProps {
  isDoghouseMode: boolean;
  setIsDoghouseMode: (val: boolean) => void;
  wsConnected: boolean;
  activeWellName: string;
  onSelectWell: (name: string) => void;
  wellsList: Array<{ well_id: string; well_name: string; field_name: string }>;
  onTriggerAlert: () => void;
  onResetSim: () => void;
  onExportPdf: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  isDoghouseMode,
  setIsDoghouseMode,
  wsConnected,
  activeWellName,
  onSelectWell,
  wellsList,
  onTriggerAlert,
  onResetSim,
  onExportPdf,
}) => {
  return (
    <header className="bg-[#184E3A] text-white border-b-4 border-[#E58A13] shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-2.5 flex flex-wrap items-center justify-between gap-3">
        {/* Left Branding */}
        <div className="flex items-center space-x-3">
          <div className="bg-[#E58A13] text-[#1E242B] font-black px-2.5 py-1 rounded text-base tracking-wider flex items-center gap-1 shadow-sm">
            <span>OIL</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-extrabold text-lg tracking-tight leading-tight">
                eRTMAC-NWIS
              </h1>
              <span className="text-[11px] font-mono uppercase bg-[#0F3326] text-[#E58A13] px-2 py-0.5 rounded border border-[#236E53]">
                Nearby Wells Intelligence
              </span>
            </div>
            <p className="text-xs text-emerald-100/90 font-medium">
              Oil India Limited · Real-Time Monitoring & Analytics Center (Duliajan)
            </p>
          </div>
        </div>

        {/* Center Grounding Badge (NON-NEGOTIABLE COMPLIANCE) */}
        <div className="flex items-center">
          <div className="bg-[#0F3326] border border-[#E58A13]/60 px-3 py-1 rounded-full text-xs font-semibold text-amber-300 flex items-center gap-1.5 shadow-inner">
            <span className="w-2 h-2 rounded-full bg-[#E58A13] animate-pulse"></span>
            <span>[Synthetic — Assam Basin Profile · SPE-197489-MS Calibrated]</span>
          </div>
        </div>

        {/* Right Controls & Status */}
        <div className="flex items-center gap-3">
          {/* Active Well Dropdown */}
          <div className="flex items-center bg-[#0F3326] px-2.5 py-1 rounded border border-[#236E53] text-xs">
            <Compass className="w-3.5 h-3.5 text-[#E58A13] mr-1.5" />
            <span className="text-gray-300 mr-1.5 font-medium">Active:</span>
            <select
              value={activeWellName}
              onChange={(e) => onSelectWell(e.target.value)}
              className="bg-transparent text-white font-bold focus:outline-none cursor-pointer"
            >
              {wellsList.map((w) => (
                <option key={w.well_name} value={w.well_name} className="bg-[#1E242B] text-white">
                  {w.well_name} ({w.field_name})
                </option>
              ))}
            </select>
          </div>

          {/* WebSocket 1Hz Status Pill */}
          <div className="flex items-center gap-1.5 bg-[#0F3326] px-2.5 py-1 rounded border border-[#236E53] text-xs">
            <Radio className={`w-3.5 h-3.5 ${wsConnected ? "text-emerald-400" : "text-amber-400"}`} />
            <span className="font-mono text-[11px]">
              {wsConnected ? "1 Hz WITSML LIVE" : "SIM RUNNING"}
            </span>
          </div>

          {/* PDF Quick Export Button */}
          <button
            onClick={onExportPdf}
            className="flex items-center gap-1 bg-[#E58A13] hover:bg-[#d07b0e] text-[#1E242B] font-bold text-xs px-3 py-1.5 rounded transition shadow-sm"
            title="Download Official Tour Advisory PDF"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Tour Advisory PDF</span>
          </button>

          {/* Doghouse Mode Toggle */}
          <button
            onClick={() => setIsDoghouseMode(!isDoghouseMode)}
            className={`flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1.5 rounded transition border ${
              isDoghouseMode
                ? "bg-amber-400 text-black border-amber-500 font-bold"
                : "bg-[#0F3326] text-gray-200 border-[#236E53] hover:bg-[#154634]"
            }`}
            title="Toggle Rugged Doghouse Touch Console Mode"
          >
            <Tablet className="w-3.5 h-3.5" />
            <span>{isDoghouseMode ? "Console Active" : "Doghouse Mode"}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
