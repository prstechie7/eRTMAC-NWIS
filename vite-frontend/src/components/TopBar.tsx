import React from "react";
import {
  Search, Bell, ChevronDown, Download, Plus, AlertTriangle,
  Radio, Compass, ShieldCheck
} from "lucide-react";

interface TopBarProps {
  activeWellName?: string;
  depthMd?: number;
  ropValue?: number;
  stuckRisk?: number;
  onOpenModelCatalog?: () => void;
  onOpenAddScenario?: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({
  activeWellName = "NHK-062 (Duliajan)",
  depthMd = 2413.5,
  ropValue = 14.2,
  stuckRisk = 83.5,
  onOpenModelCatalog,
  onOpenAddScenario,
}) => {
  return (
    <header className="bg-white border-b border-slate-200/80 px-8 py-4 flex items-center justify-between sticky top-0 z-30 shadow-xs">
      {/* ── Left: Search Bar (Shopeers / Donezo Style) ── */}
      <div className="flex items-center gap-4 flex-1 max-w-lg">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search well, offset record, lithology or parameter... (⌘K)"
            className="w-full pl-10 pr-12 py-2 text-xs font-medium bg-slate-100/70 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 transition-all placeholder:text-slate-400"
          />
          <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-mono text-slate-400 bg-white px-1.5 py-0.5 rounded border border-slate-200 shadow-2xs">
            ⌘K
          </kbd>
        </div>
      </div>

      {/* ── Center: Live Telemetry Ticker ── */}
      <div className="hidden xl:flex items-center gap-6 px-4 py-1.5 bg-slate-50 border border-slate-200/80 rounded-2xl">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
          <span className="text-[11px] font-mono font-bold text-slate-700">{activeWellName}</span>
        </div>

        <div className="h-4 w-px bg-slate-200" />

        <div className="text-[11px] text-slate-600">
          <span className="text-slate-400 font-mono">DEPTH: </span>
          <span className="font-mono font-bold text-slate-900">{depthMd.toFixed(1)} m</span>
        </div>

        <div className="h-4 w-px bg-slate-200" />

        <div className="text-[11px] text-slate-600">
          <span className="text-slate-400 font-mono">ROP: </span>
          <span className="font-mono font-bold text-slate-900">{ropValue.toFixed(1)} m/h</span>
        </div>

        <div className="h-4 w-px bg-slate-200" />

        <div className="flex items-center gap-1.5">
          <AlertTriangle className="w-3.5 h-3.5 text-rose-500" />
          <span className="text-[11px] font-mono font-bold text-rose-600">
            RISK: {stuckRisk.toFixed(1)}%
          </span>
        </div>
      </div>

      {/* ── Right: Action Buttons & User Profile (Donezo Style) ── */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenModelCatalog}
          className="hidden sm:flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200/80 rounded-2xl transition-all border border-slate-200/60"
        >
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>14 ML Models</span>
        </button>

        <button
          onClick={onOpenAddScenario}
          className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-forest-900 hover:bg-forest-800 rounded-2xl shadow-sm transition-all shadow-forest-900/20 active:scale-95"
        >
          <Plus className="w-3.5 h-3.5 text-emerald-400" />
          <span>+ Add Scenario</span>
        </button>

        <div className="h-6 w-px bg-slate-200 mx-1" />

        {/* Notification Bell */}
        <button className="relative p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-2xl transition-all">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full ring-2 ring-white" />
        </button>

        {/* User Profile Avatar (Donezo Style) */}
        <div className="flex items-center gap-3 pl-2 cursor-pointer hover:opacity-90 transition-opacity">
          <div className="relative">
            <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-amber-500 to-rose-500 flex items-center justify-center text-white font-bold text-xs shadow-sm shadow-amber-500/20 ring-2 ring-emerald-500/30">
              AS
            </div>
            <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 rounded-full ring-2 ring-white" />
          </div>

          <div className="hidden lg:block text-left">
            <div className="text-xs font-bold text-slate-900 flex items-center gap-1">
              <span>Er. Alok Sharma</span>
              <ChevronDown className="w-3 h-3 text-slate-400" />
            </div>
            <div className="text-[10px] text-slate-400 font-medium">OIL Senior Drilling Supt.</div>
          </div>
        </div>
      </div>
    </header>
  );
};
