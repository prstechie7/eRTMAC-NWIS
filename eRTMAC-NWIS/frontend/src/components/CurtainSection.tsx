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
  { name: "Dihing Group (Pliocene)", top_m: 0, bottom_m: 350, color: "#F1F5F9" },
  { name: "Dupi Tila Sandstones", top_m: 350, bottom_m: 700, color: "#E2E8F0" },
  {
    name: "Girujan Clay (Smectite-rich)",
    top_m: 700,
    bottom_m: 1850,
    color: "#E5ECE6",
    hazardNote: "Swelling Shale · Bit Balling Risk",
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
    hazardNote: "Reactive Sloughing Shale Instability",
    hazardSeverity: "warning",
  },
  {
    name: "Sylhet Limestone",
    top_m: 4100,
    bottom_m: 4500,
    color: "#CBD5E1",
    hazardNote: "Vugular / Karst Total Losses",
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
  // SVG Canvas dimensions
  const svgWidth = 520;
  const svgHeight = 400;

  // Depth range: 0m to 3200m TVDSS
  const maxDepth = 3200;
  const depthToY = (depth: number) => (depth / maxDepth) * (svgHeight - 40) + 20;

  const bitY = depthToY(currentDepthMd);
  const hazardY = depthToY(hazardDepthMd);

  // Dip offset across horizontal section (structural dip ~3.5°)
  const dipDelta = 14;

  return (
    <div className="bg-white rounded-lg border border-[#E2E8F0] shadow-sm overflow-hidden flex flex-col h-full">
      {/* Header */}
      <div className="bg-[#F8F9FA] px-4 py-2.5 border-b border-[#E2E8F0] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#E58A13]"></div>
          <span className="font-bold text-xs uppercase tracking-wider text-[#184E3A]">
            Panel 2 · 2D Geological Curtain Cross-Section (TSD)
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono text-gray-500">
          <span>Structural Dip: 3.5° SSE</span>
        </div>
      </div>

      {/* Cross-Section Graphic */}
      <div className="relative p-2 bg-[#F8FAFC] flex-1 flex items-center justify-center">
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="w-full h-auto max-h-[400px] bg-white rounded border border-slate-200"
        >
          {/* Depth Scale on Left */}
          <g>
            {[0, 500, 1000, 1500, 2000, 2500, 3000].map((d) => (
              <g key={d}>
                <line
                  x1="35"
                  y1={depthToY(d)}
                  x2="480"
                  y2={depthToY(d)}
                  stroke="#F1F5F9"
                  strokeWidth="1"
                />
                <text
                  x="30"
                  y={depthToY(d) + 3}
                  fontSize="8.5"
                  fill="#94A3B8"
                  textAnchor="end"
                  fontFamily="monospace"
                >
                  {d}m
                </text>
              </g>
            ))}
          </g>

          {/* Formation Layers (Stratigraphic Slices with Dip) */}
          {FORMATIONS.filter((f) => f.top_m < maxDepth).map((f) => {
            const y1 = depthToY(f.top_m);
            const y2 = depthToY(Math.min(f.bottom_m, maxDepth));
            const pathD = `M 40 ${y1} L 480 ${y1 + dipDelta} L 480 ${y2 + dipDelta} L 40 ${y2} Z`;

            return (
              <g key={f.name}>
                <path d={pathD} fill={f.color} stroke="#CBD5E1" strokeWidth="0.6" opacity="0.85" />
                {/* Formation Label */}
                <text
                  x="50"
                  y={y1 + (y2 - y1) / 2 + 3}
                  fontSize="9"
                  fontWeight="bold"
                  fill="#334155"
                >
                  {f.name}
                </text>

                {/* Hazard Note Badge */}
                {f.hazardNote && (
                  <g>
                    <rect
                      x="230"
                      y={y1 + (y2 - y1) / 2 - 7}
                      width={f.hazardSeverity === "critical" ? "240" : "195"}
                      height="15"
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
                      strokeWidth="0.8"
                    />
                    <text
                      x="236"
                      y={y1 + (y2 - y1) / 2 + 4}
                      fontSize="8"
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
            <line x1="160" y1="20" x2="160" y2="40" stroke="#64748B" strokeWidth="3" />
            <path
              d={`M 160 40 Q 160 160 175 220 T 190 ${depthToY(2750)}`}
              fill="none"
              stroke="#64748B"
              strokeWidth="2.2"
              strokeDasharray="4 2"
            />
            <rect x="125" y="6" width="70" height="13" rx="2" fill="#1E242B" />
            <text x="160" y="15" fontSize="7.5" fill="#FFFFFF" fontWeight="bold" textAnchor="middle">
              SYN-NHK-01
            </text>

            {/* Historical Stuck Pipe Incident Marker */}
            <circle cx="185" cy={hazardY - 2} r="5" fill="#D9381E" stroke="#FFFFFF" strokeWidth="1.5" />
            <text x="195" y={hazardY + 1} fontSize="8" fontWeight="bold" fill="#D9381E">
              Stuck Pipe (38.5h NPT)
            </text>
          </g>

          {/* Active Well SYN-NHK-05 Trajectory (Right Well) */}
          <g>
            <line x1="330" y1="20" x2="330" y2="40" stroke="#184E3A" strokeWidth="3.5" />
            <path
              d={`M 330 40 Q 330 180 345 250 T 360 ${depthToY(3150)}`}
              fill="none"
              stroke="#184E3A"
              strokeWidth="2.5"
              strokeDasharray="2 2"
              opacity="0.5"
            />
            {/* Drilled path up to active bit depth */}
            <path
              d={`M 330 40 Q 330 180 345 250 T 360 ${bitY}`}
              fill="none"
              stroke="#184E3A"
              strokeWidth="3.5"
            />

            <rect x="295" y="6" width="70" height="13" rx="2" fill="#184E3A" />
            <text x="330" y="15" fontSize="7.5" fill="#FFFFFF" fontWeight="bold" textAnchor="middle">
              SYN-NHK-05 (ACTIVE)
            </text>

            {/* Active Bit Marker */}
            <g>
              <circle
                cx="357"
                cy={bitY}
                r="7"
                fill={isAlertActive ? "#D9381E" : "#E58A13"}
                stroke="#FFFFFF"
                strokeWidth="2"
                className="animate-pulse"
              />
              <line
                x1="40"
                y1={bitY}
                x2="480"
                y2={bitY}
                stroke={isAlertActive ? "#D9381E" : "#E58A13"}
                strokeWidth="1.2"
                strokeDasharray="3 3"
              />
              {/* Bit Depth Tag */}
              <rect
                x="370"
                y={bitY - 9}
                width="95"
                height="18"
                rx="3"
                fill={isAlertActive ? "#D9381E" : "#1E242B"}
              />
              <text
                x="417"
                y={bitY + 3}
                fontSize="8.5"
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
              x2="480"
              y2={hazardY + dipDelta}
              stroke="#DC2626"
              strokeWidth="1.8"
              strokeDasharray="6 3"
            />
          </g>
        </svg>

        {/* Hazard Target Legend */}
        <div className="absolute top-4 right-4 bg-white/95 backdrop-blur px-2.5 py-1.5 rounded border border-amber-200 text-[10px] space-y-1 shadow-sm">
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
      <div className="p-3 bg-[#F8F9FA] border-t border-[#E2E8F0] flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <TrendingDown className="w-4 h-4 text-[#184E3A]" />
          <span className="text-gray-700">
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
