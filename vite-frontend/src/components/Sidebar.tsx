import React from "react";
import {
  LayoutDashboard, Brain, Box, Sparkles, Compass, Database,
  Activity, ShieldAlert, FileText, Settings, LogOut, ChevronRight, Tablet
} from "lucide-react";

export type ViewTab =
  | "dashboard"
  | "ml-station"
  | "3d-wellbore"
  | "ai-assistant"
  | "indian-basins"
  | "real-data"
  | "telemetry"
  | "doghouse";

interface SidebarProps {
  activeTab: ViewTab;
  onSelectTab: (tab: ViewTab) => void;
  activeWellName: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  activeWellName,
}) => {
  const menuItems = [
    { id: "dashboard",     label: "Dashboard",       icon: LayoutDashboard, badge: "LIVE" },
    { id: "ml-station",    label: "ML Station",      icon: Brain,           badge: "14 MODELS", badgeColor: "bg-indigo-100 text-indigo-800" },
    { id: "3d-wellbore",   label: "Live Field Map",  icon: Compass,         badge: "MAPTILER",  badgeColor: "bg-emerald-100 text-emerald-800" },
    { id: "ai-assistant",  label: "AI Evidence",     icon: Sparkles,        badge: "GEMINI 2.5", badgeColor: "bg-purple-100 text-purple-800" },
    { id: "indian-basins", label: "Indian Basins",   icon: Box,             badge: "DGH NDR",   badgeColor: "bg-amber-100 text-amber-800" },
    { id: "real-data",     label: "Real Data Stack", icon: Database,        badge: "CONNECTED", badgeColor: "bg-emerald-100 text-emerald-800" },
    { id: "telemetry",     label: "Telemetry 1Hz",   icon: Activity,        badge: "WITSML",    badgeColor: "bg-sky-100 text-sky-800" },
  ];

  const generalItems = [
    { id: "doghouse",      label: "Doghouse Mode",   icon: Tablet },
    { id: "settings",      label: "Rig Parameters",  icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200/80 flex flex-col justify-between p-5 min-h-screen flex-shrink-0 select-none">
      {/* ── Brand Logo Header ── */}
      <div>
        <div className="flex items-center gap-3 px-2 mb-8">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-emerald-600 to-forest-900 flex items-center justify-center text-white shadow-md shadow-emerald-900/20">
            <span className="font-mono font-black text-sm tracking-wider">OIL</span>
          </div>
          <div>
            <div className="font-extrabold text-[15px] tracking-tight text-slate-900 flex items-center gap-1.5">
              <span>eRTMAC</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold">
                NWIS
              </span>
            </div>
            <div className="text-[11px] font-medium text-slate-400">Oil India Limited · SIH26121</div>
          </div>
        </div>

        {/* ── Navigation Menu Section ── */}
        <div className="space-y-6">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-3 mb-2 font-mono">
              MENU
            </div>
            <nav className="space-y-1">
              {menuItems.map((item) => {
                const isActive = activeTab === item.id;
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => onSelectTab(item.id as ViewTab)}
                    className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-2xl text-xs font-semibold transition-all relative ${
                      isActive
                        ? "bg-slate-900 text-white font-bold shadow-md shadow-slate-900/10"
                        : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/70"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon
                        className={`w-4 h-4 transition-colors ${
                          isActive ? "text-emerald-400" : "text-slate-400"
                        }`}
                      />
                      <span>{item.label}</span>
                    </div>

                    {item.badge && (
                      <span
                        className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded-md ${
                          isActive
                            ? "bg-white/20 text-emerald-300"
                            : item.badgeColor || "bg-slate-100 text-slate-600"
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>

          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-3 mb-2 font-mono">
              OPERATIONS
            </div>
            <nav className="space-y-1">
              {generalItems.map((item) => {
                const isActive = activeTab === item.id;
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => onSelectTab(item.id as ViewTab)}
                    className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-xs font-semibold transition-all ${
                      isActive
                        ? "bg-slate-900 text-white font-bold"
                        : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/70"
                    }`}
                  >
                    <Icon className="w-4 h-4 text-slate-400" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>
      </div>

      {/* ── Bottom Donezo-Style Dark Highlight Card ── */}
      <div className="pt-4">
        <div className="forest-hero-card p-4 text-white relative">
          <div className="hatch-pattern absolute inset-0 opacity-40 pointer-events-none" />
          <div className="relative z-10 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                ACTIVE RIG
              </span>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            </div>
            <div>
              <div className="font-extrabold text-sm">{activeWellName}</div>
              <div className="text-[11px] text-emerald-200/80">Nahorkatiya Field · Rig 04</div>
            </div>
            <div className="pt-1">
              <div className="w-full bg-black/30 rounded-full h-1.5 overflow-hidden">
                <div className="bg-emerald-400 h-full rounded-full" style={{ width: "84%" }} />
              </div>
              <div className="flex justify-between items-center text-[10px] text-emerald-300/80 mt-1 font-mono">
                <span>Depth: 2,413.5m</span>
                <span>Tgt: 2,850m</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};
