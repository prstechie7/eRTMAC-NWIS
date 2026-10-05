import React from "react";
import { ShieldAlert, CheckCircle, Info, ChevronRight, AlertTriangle } from "lucide-react";

interface RadialGaugeCardProps {
  riskPercentage?: number;
  consensusScore?: number;
  primaryMechanism?: string;
  onExploreRemedy?: () => void;
}

export const RadialGaugeCard: React.FC<RadialGaugeCardProps> = ({
  riskPercentage = 83.5,
  consensusScore = 97.0,
  primaryMechanism = "Mechanical Sticking · Barail Coal-Shale",
  onExploreRemedy,
}) => {
  // SVG Donut Calculations
  // Total circumference for radius 65 = 2 * PI * 65 ≈ 408.4
  const radius = 65;
  const strokeWidth = 18;
  const circumference = 2 * Math.PI * radius;

  // Segment allocations based on 83.5%
  // Arc 1: Safe baseline (16.5%)
  // Arc 2: Swelling pack-off (27.0%)
  // Arc 3: Critical mechanical wedge (40.0%) - With Diagonal Hatch Pattern!
  const seg1Pct = 0.165;
  const seg2Pct = 0.270;
  const seg3Pct = 0.400; // Remaining 16.5% is open background track

  const seg1Len = circumference * seg1Pct;
  const seg2Len = circumference * seg2Pct;
  const seg3Len = circumference * seg3Pct;

  // Offsets
  // Start from top (-90 deg)
  const offset1 = 0;
  const offset2 = -seg1Len;
  const offset3 = -(seg1Len + seg2Len);

  return (
    <div className="luxury-card rounded-3xl p-6 bg-white border border-slate-200/90 flex flex-col justify-between h-full">
      {/* ── Card Header ── */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <span>Stuck-Pipe Risk Consensus</span>
            <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
          </h3>
          <p className="text-[11px] text-slate-400 font-medium">
            Multi-model consensus across 14 enterprise algorithms
          </p>
        </div>
        <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-rose-50 text-rose-600 border border-rose-200">
          LEVEL 3 ESCALATION
        </span>
      </div>

      {/* ── Center: Donezo-Style Segmented Radial Gauge with Diagonal Hatch Pattern ── */}
      <div className="relative flex flex-col items-center justify-center my-3">
        <svg width="220" height="220" viewBox="0 0 180 180" className="transform -rotate-90">
          <defs>
            {/* Donezo Diagonal Hatch Pattern for SVG */}
            <pattern
              id="gaugeHatchPattern"
              patternUnits="userSpaceOnUse"
              width="6"
              height="6"
              patternTransform="rotate(45)"
            >
              <line
                x1="0"
                y1="0"
                x2="0"
                y2="6"
                stroke="#0e3b28"
                strokeWidth="2.5"
              />
            </pattern>

            <pattern
              id="roseHatchPattern"
              patternUnits="userSpaceOnUse"
              width="6"
              height="6"
              patternTransform="rotate(45)"
            >
              <line
                x1="0"
                y1="0"
                x2="0"
                y2="6"
                stroke="#e11d48"
                strokeWidth="2.5"
              />
            </pattern>
          </defs>

          {/* Background circle track */}
          <circle
            cx="90"
            cy="90"
            r={radius}
            fill="transparent"
            stroke="#f1f5f9"
            strokeWidth={strokeWidth}
          />

          {/* Segment 1: Safe baseline (Light Emerald) */}
          <circle
            cx="90"
            cy="90"
            r={radius}
            fill="transparent"
            stroke="#10b981"
            strokeWidth={strokeWidth}
            strokeDasharray={`${seg1Len} ${circumference}`}
            strokeDashoffset={offset1}
            strokeLinecap="round"
          />

          {/* Segment 2: Swelling pack-off (Deep Forest Green) */}
          <circle
            cx="90"
            cy="90"
            r={radius}
            fill="transparent"
            stroke="#064e3b"
            strokeWidth={strokeWidth}
            strokeDasharray={`${seg2Len} ${circumference}`}
            strokeDashoffset={offset2}
          />

          {/* Segment 3: Critical Hazard Arc (Hatched Pattern) */}
          <circle
            cx="90"
            cy="90"
            r={radius}
            fill="transparent"
            stroke="url(#gaugeHatchPattern)"
            strokeWidth={strokeWidth}
            strokeDasharray={`${seg3Len} ${circumference}`}
            strokeDashoffset={offset3}
            strokeLinecap="round"
          />
        </svg>

        {/* Center Text inside Donut */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <div className="text-3xl font-extrabold text-slate-900 tracking-tight font-mono">
            {riskPercentage.toFixed(1)}%
          </div>
          <div className="text-[11px] font-semibold text-rose-600 mt-0.5 uppercase tracking-wide">
            Critical Risk
          </div>
          <div className="text-[9px] font-mono text-slate-400 mt-0.5">
            Consensus: {consensusScore}%
          </div>
        </div>
      </div>

      {/* ── Donezo-Style Legend with Hatched Dot ── */}
      <div className="flex items-center justify-center gap-4 text-[11px] font-medium text-slate-600 pt-2 border-t border-slate-100">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
          <span>Safe Margin</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-forest-900" />
          <span>Hole Pack-off</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span
            className="w-2.5 h-2.5 rounded-full border border-slate-400 hatch-pattern"
            style={{ width: "10px", height: "10px" }}
          />
          <span>Severe Jamming</span>
        </div>
      </div>

      {/* ── Bottom Advisory Card ── */}
      <div className="mt-4 p-3.5 bg-slate-50 border border-slate-200/80 rounded-2xl flex items-center justify-between">
        <div className="flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <div className="text-xs font-bold text-slate-900">{primaryMechanism}</div>
            <div className="text-[11px] text-slate-500 font-medium">
              Recommend: Flow ↑ 680 gpm + 12 rpm rotary oscillation
            </div>
          </div>
        </div>
        <button
          onClick={onExploreRemedy}
          className="p-1.5 hover:bg-slate-200/80 rounded-xl transition-all text-slate-500 hover:text-slate-900"
          title="View Engineering Action Plan"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
