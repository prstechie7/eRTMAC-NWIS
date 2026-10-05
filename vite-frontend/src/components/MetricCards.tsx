import React from "react";
import {
  ArrowUpRight, AlertOctagon, GitCompare, Gauge, Activity,
  TrendingDown, TrendingUp, Sparkles, CheckCircle2
} from "lucide-react";

interface MetricCardsProps {
  stuckRisk?: number;
  dtwTopWell?: string;
  dtwSimilarity?: number;
  ropDeviation?: number;
  activeWellsCount?: number;
  onSelectCard?: (metricId: string) => void;
}

export const MetricCards: React.FC<MetricCardsProps> = ({
  stuckRisk = 83.5,
  dtwTopWell = "NHK-014",
  dtwSimilarity = 98.4,
  ropDeviation = -33.0,
  activeWellsCount = 24,
  onSelectCard,
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
      {/* ── Card 1: Donezo Forest Green Hero Card ── */}
      <div
        onClick={() => onSelectCard?.("hero")}
        className="forest-hero-card rounded-3xl p-6 text-white flex flex-col justify-between min-h-[175px] shadow-lg cursor-pointer hover:shadow-2xl hover:scale-[1.01] transition-all group relative overflow-hidden"
      >
        {/* Subtle patterned watermark background */}
        <div className="absolute -right-6 -bottom-6 w-32 h-32 rounded-full border-[18px] border-emerald-500/10 pointer-events-none" />
        <div className="absolute right-10 -bottom-10 w-24 h-24 rounded-full border-[10px] border-emerald-400/10 pointer-events-none" />

        <div className="flex items-start justify-between relative z-10">
          <div>
            <div className="text-[12px] font-medium text-emerald-200/90 tracking-wide">
              Total Offset Wells
            </div>
            <div className="text-3xl font-extrabold tracking-tight mt-1 text-white font-mono">
              {activeWellsCount}
            </div>
          </div>
          <div className="w-9 h-9 rounded-2xl bg-white/10 backdrop-blur-md flex items-center justify-center text-emerald-300 group-hover:bg-emerald-500 group-hover:text-forest-900 transition-all">
            <ArrowUpRight className="w-5 h-5 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
          </div>
        </div>

        <div className="pt-4 flex items-center justify-between relative z-10 border-t border-emerald-800/60 mt-3">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>10 Calibrated Basins</span>
          </div>
          <span className="text-[11px] font-mono text-emerald-200/70 font-semibold bg-emerald-900/60 px-2 py-0.5 rounded-full border border-emerald-700/50">
            +14% vs avg
          </span>
        </div>
      </div>

      {/* ── Card 2: Stuck-Pipe Risk (P0 XGBoost / Extra Trees) ── */}
      <div
        onClick={() => onSelectCard?.("stuck-pipe")}
        className="luxury-card rounded-3xl p-6 flex flex-col justify-between min-h-[175px] cursor-pointer hover:shadow-lg hover:scale-[1.01] transition-all group relative border border-slate-200/90 bg-white"
      >
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-500">Stuck-Pipe Probability</span>
              <span className="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded bg-rose-50 text-rose-600 border border-rose-200">
                P0 ALERT
              </span>
            </div>
            <div className="text-3xl font-extrabold tracking-tight mt-1 text-slate-900 font-mono flex items-baseline gap-2">
              <span>{stuckRisk.toFixed(1)}%</span>
              <span className="text-xs font-mono font-bold text-rose-600 bg-rose-100/60 px-1.5 py-0.5 rounded-md">
                +12.4%
              </span>
            </div>
          </div>
          <div className="w-9 h-9 rounded-2xl bg-rose-50 flex items-center justify-center text-rose-600 group-hover:bg-rose-600 group-hover:text-white transition-all">
            <AlertOctagon className="w-4 h-4" />
          </div>
        </div>

        <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
          <div className="text-[11px] font-medium text-slate-500 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
            <span>Barail Coal-Shale pack-off</span>
          </div>
          <span className="text-[10px] font-mono font-bold text-slate-400">
            96.6% AUC
          </span>
        </div>
      </div>

      {/* ── Card 3: Dynamic Time Warping (DTW) Closest Offset ── */}
      <div
        onClick={() => onSelectCard?.("dtw")}
        className="luxury-card rounded-3xl p-6 flex flex-col justify-between min-h-[175px] cursor-pointer hover:shadow-lg hover:scale-[1.01] transition-all group relative border border-slate-200/90 bg-white"
      >
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-500">DTW Offset Match</span>
              <span className="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded bg-indigo-50 text-indigo-600 border border-indigo-200">
                98.4%
              </span>
            </div>
            <div className="text-2xl font-extrabold tracking-tight mt-1 text-slate-900 font-mono flex items-baseline gap-2">
              <span>{dtwTopWell}</span>
              <span className="text-xs font-mono font-bold text-indigo-600">
                (Duliajan)
              </span>
            </div>
          </div>
          <div className="w-9 h-9 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-all">
            <GitCompare className="w-4 h-4" />
          </div>
        </div>

        <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
          <div className="text-[11px] font-medium text-slate-500 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
            <span>Stuck at 2,420 m (6.5m deeper)</span>
          </div>
          <span className="text-[10px] font-mono font-bold text-slate-400">
            14h NPT Saved
          </span>
        </div>
      </div>

      {/* ── Card 4: ROP Deviation & Drag ── */}
      <div
        onClick={() => onSelectCard?.("rop")}
        className="luxury-card rounded-3xl p-6 flex flex-col justify-between min-h-[175px] cursor-pointer hover:shadow-lg hover:scale-[1.01] transition-all group relative border border-slate-200/90 bg-white"
      >
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-500">ROP Deviation</span>
              <span className="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded bg-amber-50 text-amber-700 border border-amber-200">
                ANOMALY
              </span>
            </div>
            <div className="text-3xl font-extrabold tracking-tight mt-1 text-slate-900 font-mono flex items-baseline gap-2">
              <span>{ropDeviation.toFixed(1)}%</span>
              <span className="text-xs font-mono font-bold text-amber-600 bg-amber-100/60 px-1.5 py-0.5 rounded-md">
                Slowdown
              </span>
            </div>
          </div>
          <div className="w-9 h-9 rounded-2xl bg-amber-50 flex items-center justify-center text-amber-600 group-hover:bg-amber-600 group-hover:text-white transition-all">
            <TrendingDown className="w-4 h-4" />
          </div>
        </div>

        <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
          <div className="text-[11px] font-medium text-slate-500 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
            <span>Actual: 14.2 m/h · Exp: 21.2</span>
          </div>
          <span className="text-[10px] font-mono font-bold text-slate-400">
            Drag +18.2k
          </span>
        </div>
      </div>
    </div>
  );
};
