"use client";

import React from "react";
import { Layers, AlertOctagon, TrendingDown, ShieldAlert } from "lucide-react";

interface Formation {
  name: string;
  top_m: number;
  bottom_m: number;
  color: string;
  hazardNote?: string;
  hazardSeverity?: "high" | "critical" | "warning";
}

const FORMATIONS: Formation[] = [
  { name: "Dihing Group (Pliocene)", top_m: 0, bottom_m: 350, color: "#F8FAFC" },
  { name: "Dupi Tila Sandstones", top_m: 350, bottom_m: 700, color: "#F1F5F9" },
  {
    name: "Girujan Clay (Smectite-rich)",
    top_m: 700,
    bottom_m: 1850,
    color: "#E8F0EA",
    hazardNote: "Swelling Shale · Bit Balling",
    hazardSeverity: "warning",
  },
  {
    name: "Upper Tipam Sandstone (Depleted)",
    top_m: 1850,
    bottom_m: 2520,
    color: "#FEF3C7",
    hazardNote: "Depleted Pressure (0.88 SG) · Diff Sticking Risk",
    hazardSeverity: "critical",
  },
  { name: "Lower Tipam Sandstone", top_m: 2520, bottom_m: 2900, color: "#FDE68A" },
  {
    name: "Barail Coal-Shale Group",
    top_m: 2900,
    bottom_m: 3500,
    color: "#FED7AA",
    hazardNote: "Overpressured Kicks (PP 1.35 SG)",
    hazardSeverity: "high",
  },
  {
    name: "Kopili Formation",
    top_m: 3500,
    bottom_m: 4100,
    color: "#E2E8F0",
    hazardNote: "Sloughing Reactive Shale",
    hazardSeverity: "warning",
  },
  {
    name: "Sylhet Limestone",
    top_m: 4100,
    bottom_m: 4500,
    color: "#CBD5E1",
    hazardNote: "Karst Total Mud Losses",
    hazardSeverity: "high",
  },
];

interface CurtainSectionProps {
  currentDepthMd: number;
  currentTvdss: number;
  hazardDepthMd: number;
  isAlertActive: boolean;
}

export const CurtainSection: React.FC<CurtainSectionProps> = ({
  currentDepthMd,
  currentTvdss,
  hazardDepthMd = 2448.5,
  isAlertActive,
}) => {
  const svgWidth = 560;
  const svgHeight = 320;

  // Depth range: 0m to 3200m TVDSS
  const maxDepth = 3200;
  const topPad = 32;
  const depthToY = (depth: number) => (depth / maxDepth) * (svgHeight - topPad - 20) + topPad;

  const bitY = depthToY(currentDepthMd);
  const hazardY = depthToY(hazardDepthMd);

  // Structural Dip ~3.5° across the section
  const dipDelta = 12;

  return (
    <div className="bg-white rounded-lg border border-[#E2E8F0] shadow-sm overflow-hidden flex flex-col h-full">
      {/* Header */}
      <div className="bg-[#F8F9FA] px-3.5 py-2 border-b border-[#E2E8F0] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#E58A13]"></div>
          <span className="font-bold text-xs uppercase tracking-wider text-[#184E3A]">
            Panel 2 · 2D Geological Curtain Cross-Section (TSD)
          </span>
        </div>
        <div className="flex items-center gap-2 text-[11px] font-mono text-gray-500">
          <span>Structural Dip: 3.5° SSE</span>
        </div>
      </div>

      {/* Cross-Section Graphic */}
      <div className="relative p-2 bg-[#F8FAFC] flex-1 flex items-center justify-center min-h-[250px]">
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="w-full h-auto max-h-[300px] bg-white rounded border border-slate-200"
        >
          {/* Depth Scale Grid on Left */}
          <g>
            {[0, 500, 1000, 1500, 2000, 2500, 3000].map((d) => (
              <g key={d}>
                <line
                  x1="38"
                  y1={depthToY(d)}
                  x2="520"
                  y2={depthToY(d)}
                  stroke="#F1F5F9"
                  strokeWidth="0.8"
                />
                <text
                  x="34"
                  y={depthToY(d) + 3}
                  fontSize="7.5"
                  fill="#94A3B8"
                  textAnchor="end"
                  fontFamily="monospace"
                >
                  {d}m
                </text>
              </g>
            ))}
          </g>

          {/* Stratigraphic Formation Layers */}
          {FORMATIONS.filter((f) => f.top_m < maxDepth).map((f) => {
            const y1 = depthToY(f.top_m);
            const y2 = depthToY(Math.min(f.bottom_m, maxDepth));
            const pathD = `M 40 ${y1} L 520 ${y1 + dipDelta} L 520 ${y2 + dipDelta} L 40 ${y2} Z`;

            return (
              <g key={f.name}>
                <path d={pathD} fill={f.color} stroke="#CBD5E1" strokeWidth="0.5" opacity="0.85" />
                {/* Formation Label */}
                <text
                  x="48"
                  y={y1 + (y2 - y1) / 2 + 2}
                  fontSize="8"
                  fontWeight="bold"
                  fill="#334155"
                >
                  {f.name}
                </text>

                {/* Hazard Note Badge (Placed toward center-right) */}
                {f.hazardNote && (
                  <g>
                    <rect
                      x="250"
                      y={y1 + (y2 - y1) / 2 - 7}
                      width={f.hazardSeverity === "critical" ? "215" : "175"}
                      height="14"
                      rx="3"
                      fill={
                        f.hazardSeverity === "critical"
                          ? "#FEE2E2"
                          : f.hazardSeverity === "high"
                          ? "#FFEDD5"
                          : "#FEF3C7"
                      }
                      stroke={
                        f.hazardSeverity === "critical"
                          ? "#DC2626"
                          : f.hazardSeverity === "high"
                          ? "#EA580C"
                          : "#D97706"
                      }
                      strokeWidth="0.7"
                    />
                    <text
                      x="256"
                      y={y1 + (y2 - y1) / 2 + 3}
                      fontSize="7"
                      fontWeight="bold"
                      fill={
                        f.hazardSeverity === "critical"
                          ? "#991B1B"
                          : f.hazardSeverity === "high"
                          ? "#9A3412"
                          : "#92400E"
                      }
                    >
                      {f.hazardNote}
                    </text>
                  </g>
                )}
              </g>
            );
          })}

          {/* Offset Well SYN-NHK-01 Trajectory (Left Well) */}
          <g>
            {/* Wellhead label */}
            <rect x="135" y="8" width="68" height="15" rx="3" fill="#1E242B" />
            <text x="169" y="19" fontSize="7.5" fill="#FFFFFF" fontWeight="bold" textAnchor="middle">
              SYN-NHK-01
            </text>
            <line x1="169" y1="23" x2="169" y2={topPad} stroke="#64748B" strokeWidth="2.5" />

            <path
              d={`M 169 ${topPad} Q 169 130 180 180 T 195 ${depthToY(2750)}`}
              fill="none"
              stroke="#64748B"
              strokeWidth="2"
              strokeDasharray="4 2"
            />

            {/* Historical Incident Marker */}
            <circle cx="191" cy={hazardY - 1} r="4.5" fill="#D9381E" stroke="#FFFFFF" strokeWidth="1.2" />
            <text x="200" y={hazardY + 2} fontSize="7.5" fontWeight="bold" fill="#D9381E">
              Stuck Pipe (38.5h NPT)
            </text>
          </g>

          {/* Active Well SYN-NHK-05 Trajectory (Right Well) */}
          <g>
            {/* Wellhead label */}
            <rect x="345" y="8" width="95" height="15" rx="3" fill="#184E3A" />
            <text x="392" y="19" fontSize="7.5" fill="#FFFFFF" fontWeight="bold" textAnchor="middle">
              SYN-NHK-05 (ACTIVE)
            </text>
            <line x1="392" y1="23" x2="392" y2={topPad} stroke="#184E3A" strokeWidth="3" />

            {/* Planned Trajectory */}
            <path
              d={`M 392 ${topPad} Q 392 140 405 200 T 420 ${depthToY(3150)}`}
              fill="none"
              stroke="#184E3A"
              strokeWidth="2"
              strokeDasharray="2 2"
              opacity="0.4"
            />
            {/* Drilled Path to current bit */}
            <path
              d={`M 392 ${topPad} Q 392 140 405 200 T 420 ${bitY}`}
              fill="none"
              stroke="#184E3A"
              strokeWidth="3.2"
            />

            {/* Active Bit Cursor */}
            <g>
              <circle
                cx="418"
                cy={bitY}
                r="6.5"
                fill={isAlertActive ? "#D9381E" : "#E58A13"}
                stroke="#FFFFFF"
                strokeWidth="2"
                className="animate-pulse"
              />
              <line
                x1="40"
                y1={bitY}
                x2="520"
                y2={bitY}
                stroke={isAlertActive ? "#D9381E" : "#E58A13"}
                strokeWidth="1"
                strokeDasharray="3 3"
              />

              {/* Bit Depth Tag (Offset cleanly to left of bit) */}
              <rect
                x="320"
                y={bitY - 8}
                width="90"
                height="16"
                rx="3"
                fill={isAlertActive ? "#D9381E" : "#1E242B"}
              />
              <text
                x="365"
                y={bitY + 3.5}
                fontSize="7.5"
                fontWeight="bold"
                fill="#FFFFFF"
                textAnchor="middle"
                fontFamily="monospace"
              >
                BIT: {currentDepthMd.toFixed(1)}m MD
              </text>
            </g>

            {/* Predicted Hazard Zone Horizon Line */}
            <line
              x1="40"
              y1={hazardY}
              x2="520"
              y2={hazardY + dipDelta}
              stroke="#DC2626"
              strokeWidth="1.5"
              strokeDasharray="5 3"
            />
          </g>
        </svg>

        {/* Hazard Target Overlay */}
        <div className="absolute top-3 right-3 bg-white/95 backdrop-blur px-2.5 py-1.5 rounded border border-amber-200 text-[9.5px] space-y-0.5 shadow-sm">
          <div className="flex items-center gap-1.5 font-bold text-red-700">
            <AlertOctagon className="w-3.5 h-3.5 text-red-600" />
            <span>Hazard Horizon: 2,448.5m MD</span>
          </div>
          <div className="text-gray-600">
            Delta Ahead:{" "}
            <span className="font-mono font-bold text-red-600">
              {Math.max(0, hazardDepthMd - currentDepthMd).toFixed(1)}m
            </span>
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="px-3 py-1.5 bg-[#F8F9FA] border-t border-[#E2E8F0] flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <TrendingDown className="w-3.5 h-3.5 text-[#184E3A]" />
          <span className="text-gray-700 text-[11px]">
            Active TVDSS: <strong className="font-mono text-[#184E3A]">{currentTvdss.toFixed(1)}m</strong>
          </span>
        </div>
        <div className="text-[11px] text-gray-500">
          Target Formation: <strong>Upper Tipam Depleted Sandstone</strong>
        </div>
      </div>
    </div>
  );
};
