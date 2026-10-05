"use client";

import React from "react";
import {
  LayoutDashboard, Map, Layers, ShieldAlert,
  Activity, GitCompare, AlertTriangle, Tablet, Database, Wrench, Compass, Sparkles, Brain
} from "lucide-react";

export type NavTab =
  | "overview" | "innovations" | "engineering" | "ml-station" | "indian-basins" | "ai-assistant" | "real-data" | "basin-map" | "geological"
  | "risk-engine" | "telemetry" | "correlation"
  | "lookahead" | "doghouse";

interface TabItem {
  id: NavTab;
  label: string;
  icon: React.ReactNode;
  badge?: string;
  badgeColor?: string;
}

const TABS: TabItem[] = [
  { id: "overview",       label: "Overview",       icon: <LayoutDashboard className="w-4 h-4" /> },
  { id: "innovations",    label: "Innovations (Top 5)", icon: <Sparkles className="w-4 h-4 text-emerald-600" />, badge: "NEW", badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300" },
  { id: "engineering",    label: "Engineering",    icon: <Wrench className="w-4 h-4" />,          badge: "P0/P1", badgeColor: "bg-amber-100 text-amber-800 border-amber-300" },
  { id: "ml-station",     label: "ML Station",     icon: <Brain className="w-4 h-4 text-indigo-600" />, badge: "14 MODELS", badgeColor: "bg-indigo-100 text-indigo-800 border-indigo-300" },
  { id: "indian-basins",  label: "Indian Basins",  icon: <Compass className="w-4 h-4 text-orange-600" />, badge: "DGH NDR", badgeColor: "bg-orange-100 text-orange-800 border-orange-300" },
  { id: "ai-assistant",   label: "AI Evidence",   icon: <Sparkles className="w-4 h-4 text-purple-600" />, badge: "GEMINI 2.5", badgeColor: "bg-purple-100 text-purple-800 border-purple-300" },
  { id: "real-data",      label: "Real Data",      icon: <Database className="w-4 h-4" />,        badge: "CONNECTED", badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300" },
  { id: "basin-map",      label: "Basin Map",      icon: <Map className="w-4 h-4" />,          badge: "MAPTILER", badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300" },
  { id: "geological",     label: "Geology",        icon: <Layers className="w-4 h-4" /> },
  { id: "risk-engine",    label: "Risk Engine",    icon: <ShieldAlert className="w-4 h-4" /> },
  { id: "telemetry",      label: "Telemetry",      icon: <Activity className="w-4 h-4" />,        badge: "1 Hz", badgeColor: "bg-sky-100 text-sky-800 border-sky-300" },
  { id: "correlation",    label: "Correlation",    icon: <GitCompare className="w-4 h-4" /> },
  { id: "lookahead",      label: "Look-Ahead",     icon: <AlertTriangle className="w-4 h-4" /> },
  { id: "doghouse",       label: "Doghouse",       icon: <Tablet className="w-4 h-4" /> },
];

interface TopNavProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  isAlertActive: boolean;
  currentDepthMd: number;
  currentTvdss: number;
  riskIndex: number;
}

export const TopNav: React.FC<TopNavProps> = ({
  activeTab,
  onTabChange,
  isAlertActive,
  currentDepthMd,
  currentTvdss,
  riskIndex,
}) => {
  return (
    <nav className="w-full bg-slate-50 border-b border-slate-200">
      <div
        className="flex items-center justify-between px-4 lg:px-6 overflow-x-auto"
        style={{ maxWidth: 1720, margin: "0 auto" }}
      >
        {/* ── Tab List ── */}
        <div className="flex items-center space-x-1 py-1.5 flex-shrink-0">
          {TABS.map((tab) => {
            const isActive = activeTab === tab.id;
            const isAlertTab = tab.id === "lookahead" && isAlertActive;

            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg transition-all whitespace-nowrap relative ${
                  isActive
                    ? "bg-white text-emerald-800 shadow-xs border border-slate-200 font-bold"
                    : isAlertTab
                    ? "text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/60"
                }`}
              >
                <span className={isActive ? "text-emerald-700" : isAlertTab ? "text-rose-600" : "text-slate-500"}>
                  {tab.icon}
                </span>
                <span>{tab.label}</span>

                {tab.badge && (
                  <span
                    className={`text-[9px] font-mono font-bold px-1.5 py-0.2 rounded border ${tab.badgeColor}`}
                  >
                    {tab.badge}
                  </span>
                )}

                {isAlertTab && (
                  <span className="w-2 h-2 rounded-full bg-rose-600 animate-ping ml-0.5" />
                )}
              </button>
            );
          })}
        </div>

        {/* ── Right Telemetry Ticker ── */}
        <div className="hidden lg:flex items-center gap-4 py-1.5 pl-4 border-l border-slate-200 flex-shrink-0 text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">MD:</span>
            <span className="font-bold text-slate-800">{currentDepthMd.toFixed(1)} m</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">TVDSS:</span>
            <span className="font-bold text-slate-800">{currentTvdss.toFixed(1)} m</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">Hazard Index:</span>
            <span
              className={`font-bold px-1.5 py-0.5 rounded text-[11px] ${
                isAlertActive
                  ? "bg-rose-100 text-rose-800 border border-rose-300 animate-pulse"
                  : "bg-slate-100 text-slate-700"
              }`}
            >
              {riskIndex.toFixed(1)}%
            </span>
          </div>
        </div>
      </div>
    </nav>
  );
};
