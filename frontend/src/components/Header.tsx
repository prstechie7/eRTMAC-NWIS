"use client";

import React, { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import {
  FileDown, ChevronDown, Tablet,
  RefreshCw, FastForward, Radio, CheckCircle2,
  ShieldCheck, AlertTriangle
} from "lucide-react";

interface WellPoint {
  well_name: string;
  field_name: string;
  status: string;
}

interface HeaderProps {
  isDoghouseMode: boolean;
  setIsDoghouseMode: (v: boolean) => void;
  wsConnected: boolean;
  activeWellName: string;
  onSelectWell: (name: string) => void;
  wellsList: WellPoint[];
  onTriggerAlert: () => void;
  onResetSim: () => void;
  onExportPdf: () => void;
  isAlertActive?: boolean;
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
  isAlertActive = false,
}) => {
  const [wellDropOpen, setWellDropOpen] = useState(false);
  const headerRef = useRef<HTMLElement>(null);
  const logoRef = useRef<HTMLDivElement>(null);
  const rightRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!headerRef.current) return;
    const tl = gsap.timeline();
    tl.fromTo(logoRef.current, { opacity: 0, x: -15 }, { opacity: 1, x: 0, duration: 0.4, ease: "power2.out" })
      .fromTo(rightRef.current, { opacity: 0, x: 15 }, { opacity: 1, x: 0, duration: 0.4, ease: "power2.out" }, "-=0.25");
  }, []);

  const activeWell = wellsList.find((w) => w.well_name === activeWellName);

  return (
    <header
      ref={headerRef}
      className="w-full bg-white border-b border-slate-200 z-50 sticky top-0 shadow-xs"
    >
      <div
        className="flex items-center justify-between px-4 lg:px-6 h-14"
        style={{ maxWidth: 1720, margin: "0 auto" }}
      >
        {/* ── Left: Brand Identity ── */}
        <div ref={logoRef} className="flex items-center gap-3 flex-shrink-0">
          {/* OIL Pill */}
          <div className="flex items-center gap-2">
            <span className="font-mono font-black text-xs px-2.5 py-1 rounded-md bg-emerald-800 text-white tracking-widest shadow-xs">
              OIL
            </span>
            <div className="flex flex-col leading-none">
              <span className="font-heading font-black text-sm text-slate-900 tracking-tight">
                eRTMAC-NWIS
              </span>
              <span className="text-[10px] font-mono text-slate-500 mt-0.5">
                Oil India Limited · SIH26121
              </span>
            </div>
          </div>

          <div className="hidden sm:block w-px h-6 bg-slate-200 mx-1" />

          {/* Basin Tag */}
          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-slate-100 text-slate-700 border border-slate-200">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
            <span>Upper Assam Basin</span>
          </div>

          {/* Provenance Badge */}
          <div className="hidden lg:flex items-center gap-1 px-2.5 py-0.5 rounded-md text-[10px] font-mono font-semibold bg-amber-50 text-amber-800 border border-amber-200">
            <span>CALIBRATED SYNTHETIC DATA (SPE-197489-MS)</span>
          </div>
        </div>

        {/* ── Center: Active Rig Selector ── */}
        <div className="relative flex-shrink-0 mx-2">
          <button
            onClick={() => setWellDropOpen((p) => !p)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-300 bg-slate-50 hover:bg-white text-slate-800 transition-all text-xs font-semibold shadow-xs"
          >
            <span
              className={`w-2 h-2 rounded-full flex-shrink-0 ${
                activeWell?.status === "DRILLING" ? "bg-emerald-600 animate-pulse" : "bg-slate-400"
              }`}
            />
            <div className="text-left">
              <div className="font-mono font-black text-xs text-emerald-800">
                {activeWellName}
              </div>
              <div className="text-[9px] text-slate-500 leading-none">
                {activeWell?.field_name || "Field"} · Active Rig
              </div>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 ml-1" />
          </button>

          {wellDropOpen && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setWellDropOpen(false)} />
              <div className="absolute top-full left-0 mt-1.5 w-64 rounded-xl bg-white border border-slate-200 shadow-xl overflow-hidden z-50">
                <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-400 bg-slate-50 border-b border-slate-200">
                  Select Monitored Rig
                </div>
                <div className="max-h-64 overflow-y-auto">
                  {wellsList.map((w) => (
                    <button
                      key={w.well_name}
                      onClick={() => {
                        onSelectWell(w.well_name);
                        setWellDropOpen(false);
                      }}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 text-xs text-left transition-colors border-b border-slate-100 last:border-0 ${
                        w.well_name === activeWellName ? "bg-emerald-50 text-emerald-900" : "hover:bg-slate-50 text-slate-700"
                      }`}
                    >
                      <span
                        className={`w-2 h-2 rounded-full flex-shrink-0 ${
                          w.status === "DRILLING" ? "bg-emerald-600" : "bg-slate-300"
                        }`}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="font-mono font-bold truncate">{w.well_name}</div>
                        <div className="text-[10px] text-slate-400">{w.field_name}</div>
                      </div>
                      <span
                        className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                          w.status === "DRILLING"
                            ? "bg-emerald-100 text-emerald-800"
                            : "bg-slate-100 text-slate-500"
                        }`}
                      >
                        {w.status}
                      </span>
                      {w.well_name === activeWellName && (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700 flex-shrink-0" />
                      )}
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>

        {/* ── Right: Controls & Actions ── */}
        <div ref={rightRef} className="flex items-center gap-2 flex-shrink-0">
          {/* Live Hazard / Nominal Pill */}
          <div
            className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-bold border ${
              isAlertActive
                ? "bg-rose-50 text-rose-700 border-rose-300 animate-pulse"
                : "bg-emerald-50 text-emerald-800 border-emerald-200"
            }`}
          >
            {isAlertActive ? (
              <>
                <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
                <span>HAZARD ACTIVE</span>
              </>
            ) : (
              <>
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                <span>NOMINAL</span>
              </>
            )}
          </div>

          {/* WS Stream Status */}
          <div
            className={`hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-mono font-bold border ${
              wsConnected
                ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                : "bg-slate-100 text-slate-600 border-slate-200"
            }`}
          >
            <Radio className="w-3 h-3" />
            <span>{wsConnected ? "1 Hz LIVE" : "SIM ENGINE"}</span>
          </div>

          {/* Quick Simulation controls */}
          <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-lg border border-slate-200">
            <button
              onClick={onTriggerAlert}
              title="Simulate differential sticking hazard at 2,414m"
              className="flex items-center gap-1 px-2 py-1 rounded text-xs font-semibold bg-white text-rose-700 hover:bg-rose-50 border border-slate-200 transition-colors shadow-xs"
            >
              <FastForward className="w-3 h-3 text-rose-600" />
              <span className="hidden xl:inline">Kick Hazard</span>
            </button>
            <button
              onClick={onResetSim}
              title="Reset simulation to 2,410m"
              className="p-1 rounded text-slate-600 hover:text-slate-900 hover:bg-white transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* PDF Export Button */}
          <button
            onClick={onExportPdf}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-600 hover:bg-amber-700 text-white shadow-xs transition-colors"
          >
            <FileDown className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Tour Advisory PDF</span>
          </button>

          {/* Doghouse Mode Toggle */}
          <button
            onClick={() => setIsDoghouseMode(!isDoghouseMode)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold border transition-colors ${
              isDoghouseMode
                ? "bg-emerald-800 text-white border-emerald-900"
                : "bg-slate-100 hover:bg-slate-200 text-slate-800 border-slate-300"
            }`}
          >
            <Tablet className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Doghouse</span>
          </button>
        </div>
      </div>
    </header>
  );
};
