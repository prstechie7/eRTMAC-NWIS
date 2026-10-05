"use client";

import React, { useEffect, useRef } from "react";
import { Layers, AlertOctagon, TrendingDown } from "lucide-react";
import gsap from "gsap";

interface Formation {
  name: string;
  top_m: number;
  bottom_m: number;
  fillColor: string;
  strokeColor: string;
  labelColor: string;
  hazardNote?: string;
  hazardSeverity?: "high" | "critical" | "warning";
}

const FORMATIONS: Formation[] = [
  {
    name: "Dihing Group (Pliocene)",
    top_m: 0, bottom_m: 350,
    fillColor: "#e8f0f7", strokeColor: "#c5d5e3", labelColor: "#475569"
  },
  {
    name: "Dupi Tila Sandstones",
    top_m: 350, bottom_m: 700,
    fillColor: "#dce8f3", strokeColor: "#b8cfe6", labelColor: "#475569"
  },
  {
    name: "Girujan Clay (Smectite-rich)",
    top_m: 700, bottom_m: 1850,
    fillColor: "#e8f5e9", strokeColor: "#a5d6a7", labelColor: "#2e7d32",
    hazardNote: "Swelling Shale · Bit Balling",
    hazardSeverity: "warning"
  },
  {
    name: "Upper Tipam Sandstone (Depleted)",
    top_m: 1850, bottom_m: 2520,
    fillColor: "#fff8e1", strokeColor: "#ffcc02", labelColor: "#e65100",
    hazardNote: "Depleted PP 0.88 SG · Diff Sticking Risk",
    hazardSeverity: "critical"
  },
  {
    name: "Lower Tipam Sandstone",
    top_m: 2520, bottom_m: 2900,
    fillColor: "#f3e8ff", strokeColor: "#c4a8e8", labelColor: "#5b21b6"
  },
  {
    name: "Barail Coal-Shale Group",
    top_m: 2900, bottom_m: 3500,
    fillColor: "#fef2f2", strokeColor: "#fca5a5", labelColor: "#991b1b",
    hazardNote: "Overpressured Kicks (PP 1.35 SG)",
    hazardSeverity: "high"
  },
  {
    name: "Kopili Formation",
    top_m: 3500, bottom_m: 4100,
    fillColor: "#eff6ff", strokeColor: "#93c5fd", labelColor: "#1e40af",
    hazardNote: "Sloughing Reactive Shale",
    hazardSeverity: "warning"
  },
  {
    name: "Sylhet Limestone",
    top_m: 4100, bottom_m: 4500,
    fillColor: "#f0fdf4", strokeColor: "#86efac", labelColor: "#15803d",
    hazardNote: "Karst Total Mud Losses",
    hazardSeverity: "high"
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
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (cardRef.current) {
      gsap.fromTo(cardRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.6, ease: "power2.out", delay: 0.2 }
      );
    }
  }, []);

  const svgW = 560; const svgH = 300;
  const maxDepth = 3200;
  const topPad = 32;
  const depthToY = (d: number) => (d / maxDepth) * (svgH - topPad - 20) + topPad;
  const bitY = depthToY(currentDepthMd);
  const hazardY = depthToY(hazardDepthMd);
  const dipDelta = 10;

  const hazardBg = {
    critical: { fill: "#fffbeb", stroke: "#f59e0b", text: "#92400e" },
    high:     { fill: "#fef2f2", stroke: "#fca5a5", text: "#991b1b" },
    warning:  { fill: "#eff6ff", stroke: "#93c5fd", text: "#1e40af" },
  };

  return (
    <div ref={cardRef} className="card flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="card-header">
        <div className="flex items-center gap-2.5">
          <div className="icon-chip icon-chip-amber">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-heading font-bold text-[13px]" style={{ color: "var(--text-primary)" }}>
              Panel 2 · Geological Curtain Cross-Section (TSD)
            </h3>
            <p className="text-[11px]" style={{ color: "var(--text-muted)" }}>Structural Dip: 3.5° SSE</p>
          </div>
        </div>
        {isAlertActive && (
          <span className="badge badge-danger anim-breathe">
            <AlertOctagon className="w-3 h-3" />
            HAZARD ACTIVE
          </span>
        )}
      </div>

      {/* SVG Cross Section */}
      <div className="relative p-3 flex-1 flex items-center justify-center" style={{ background: "#f7fafd" }}>
        <svg
          viewBox={`0 0 ${svgW} ${svgH}`}
          className="w-full h-auto rounded-lg"
          style={{
            maxHeight: 280,
            border: "1px solid var(--border)",
            background: "linear-gradient(180deg, #f0f6fb 0%, #e8f2f9 100%)"
          }}
        >
          {/* Depth Grid Lines */}
          {[0, 500, 1000, 1500, 2000, 2500, 3000].map((d) => (
            <g key={d}>
              <line x1="38" y1={depthToY(d)} x2="520" y2={depthToY(d)}
                stroke="#cbd5e1" strokeWidth="0.7" />
              <text x="34" y={depthToY(d) + 3} fontSize="7.5"
                fill="#94a3b8" textAnchor="end" fontFamily="JetBrains Mono, monospace">
                {d}m
              </text>
            </g>
          ))}

          {/* Formation Layers */}
          {FORMATIONS.filter((f) => f.top_m < maxDepth).map((f) => {
            const y1 = depthToY(f.top_m);
            const y2 = depthToY(Math.min(f.bottom_m, maxDepth));
            const d = `M 40 ${y1} L 520 ${y1 + dipDelta} L 520 ${y2 + dipDelta} L 40 ${y2} Z`;
            const hz = f.hazardSeverity ? hazardBg[f.hazardSeverity] : null;

            return (
              <g key={f.name}>
                <path d={d} fill={f.fillColor} stroke={f.strokeColor} strokeWidth="0.8" />
                <text x="48" y={y1 + (y2 - y1) / 2 + 3}
                  fontSize="8" fontWeight="700" fill={f.labelColor}>
                  {f.name}
                </text>

                {/* Hazard Badge */}
                {f.hazardNote && hz && (
                  <g>
                    <rect
                      x="240" y={y1 + (y2 - y1) / 2 - 8}
                      width={f.hazardSeverity === "critical" ? "225" : "190"}
                      height="15" rx="4"
                      fill={hz.fill} stroke={hz.stroke} strokeWidth="0.8"
                    />
                    <text
                      x="246" y={y1 + (y2 - y1) / 2 + 3}
                      fontSize="7.5" fontWeight="700" fill={hz.text}>
                      {f.hazardNote}
                    </text>
                  </g>
                )}
              </g>
            );
          })}

          {/* Offset Well SYN-NHK-01 */}
          <g>
            <rect x="130" y="8" width="72" height="16" rx="4"
              fill="#f1f5f9" stroke="#94a3b8" strokeWidth="1" />
            <text x="166" y="19" fontSize="7.5" fill="#475569" fontWeight="700" textAnchor="middle">
              SYN-NHK-01
            </text>
            <line x1="166" y1="24" x2="166" y2={topPad} stroke="#94a3b8" strokeWidth="2" />
            <path
              d={`M 166 ${topPad} Q 166 130 178 180 T 192 ${depthToY(2750)}`}
              fill="none" stroke="#94a3b8" strokeWidth="2" strokeDasharray="4 3"
            />
            {/* Historical stuck marker */}
            <circle cx="188" cy={hazardY - 1} r="5" fill="#dc2626" stroke="white" strokeWidth="1.5" />
            <text x="198" y={hazardY + 3} fontSize="7.5" fontWeight="700" fill="#dc2626">
              Stuck Pipe (38.5h NPT)
            </text>
          </g>

          {/* Active Well SYN-NHK-05 */}
          <g>
            <rect x="340" y="8" width="100" height="16" rx="4"
              fill="#e8f5ef" stroke="#1a5c45" strokeWidth="1.2" />
            <text x="390" y="19" fontSize="7.5" fill="#1a5c45" fontWeight="800" textAnchor="middle">
              SYN-NHK-05 (ACTIVE)
            </text>
            <line x1="390" y1="24" x2="390" y2={topPad} stroke="#1a5c45" strokeWidth="2.5" />

            {/* Planned trajectory */}
            <path
              d={`M 390 ${topPad} Q 390 140 405 200 T 420 ${depthToY(3150)}`}
              fill="none" stroke="#1a5c45" strokeWidth="1.5" strokeDasharray="3 3" opacity="0.35"
            />
            {/* Drilled path */}
            <path
              d={`M 390 ${topPad} Q 390 140 405 200 T 420 ${bitY}`}
              fill="none" stroke="#1a5c45" strokeWidth="3"
            />

            {/* Active Bit */}
            <g>
              <circle cx="418" cy={bitY} r="8"
                fill={isAlertActive ? "#fef2f2" : "#e8f5ef"}
                stroke={isAlertActive ? "#dc2626" : "#1a5c45"}
                strokeWidth="2.5"
              />
              <circle cx="418" cy={bitY} r="3.5"
                fill={isAlertActive ? "#dc2626" : "#1a5c45"}
              />
              {/* Bit depth line */}
              <line
                x1="40" y1={bitY} x2="520" y2={bitY}
                stroke={isAlertActive ? "#dc2626" : "#d97706"}
                strokeWidth="1" strokeDasharray="4 3"
              />
              {/* Depth Tag */}
              <rect x="318" y={bitY - 9} width="92" height="18" rx="4"
                fill={isAlertActive ? "#fef2f2" : "white"}
                stroke={isAlertActive ? "#dc2626" : "#d97706"}
                strokeWidth="1"
              />
              <text x="364" y={bitY + 4} fontSize="7.5" fontWeight="800"
                fill={isAlertActive ? "#dc2626" : "#0f172a"}
                textAnchor="middle" fontFamily="JetBrains Mono, monospace">
                BIT: {currentDepthMd.toFixed(1)}m MD
              </text>
            </g>

            {/* Hazard Horizon */}
            <line
              x1="40" y1={hazardY} x2="520" y2={hazardY + dipDelta}
              stroke="#dc2626" strokeWidth="1.5" strokeDasharray="6 3"
            />
          </g>
        </svg>

        {/* Hazard Overlay */}
        <div
          className={`absolute top-4 right-4 p-3 rounded-xl text-xs space-y-1 shadow-lg ${isAlertActive ? "anim-breathe" : ""}`}
          style={{
            background: isAlertActive ? "#fef2f2" : "white",
            border: `1px solid ${isAlertActive ? "#fca5a5" : "var(--border)"}`,
            borderLeft: `4px solid ${isAlertActive ? "#dc2626" : "#d97706"}`,
          }}
        >
          <div className="flex items-center gap-1.5 font-bold" style={{ color: "#dc2626" }}>
            <AlertOctagon className="w-3.5 h-3.5" />
            Hazard Horizon: 2,448.5m MD
          </div>
          <div className="font-mono" style={{ color: "var(--text-secondary)" }}>
            Delta Ahead:{" "}
            <span className="font-black" style={{ color: isAlertActive ? "#dc2626" : "#d97706" }}>
              {Math.max(0, hazardDepthMd - currentDepthMd).toFixed(1)}m
            </span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="card-footer flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <TrendingDown className="w-3.5 h-3.5" style={{ color: "var(--pine)" }} />
          <span>
            Active TVDSS:{" "}
            <strong className="font-mono" style={{ color: "var(--pine)" }}>
              {currentTvdss.toFixed(1)}m
            </strong>
          </span>
        </div>
        <div className="text-[11px]" style={{ color: "var(--text-secondary)" }}>
          Target Formation:{" "}
          <strong style={{ color: "var(--amber)" }}>Upper Tipam Depleted Sandstone</strong>
        </div>
      </div>
    </div>
  );
};
