"use client";

import React, { useEffect, useRef, useState } from "react";
import { Layers, CheckCircle2, Database } from "lucide-react";
import gsap from "gsap";

export const AnalogCorrelationPanel: React.FC = () => {
  const [selectedAnalog, setSelectedAnalog] = useState("SYN-NHK-01");
  const cardRef = useRef<HTMLDivElement>(null);
  const itemRefs = useRef<(HTMLDivElement | null)[]>([]);

  const analogs = [
    {
      well: "SYN-NHK-01",
      score: 0.87,
      dist_km: 1.42,
      fmt_match: "100%",
      res_match: "91%",
      depth_delta: "+23.5m",
      hazards: 2,
    },
    {
      well: "SYN-NHK-03",
      score: 0.81,
      dist_km: 2.85,
      fmt_match: "100%",
      res_match: "85%",
      depth_delta: "-18.0m",
      hazards: 3,
    },
    {
      well: "SYN-NHK-02",
      score: 0.76,
      dist_km: 3.10,
      fmt_match: "90%",
      res_match: "80%",
      depth_delta: "+42.0m",
      hazards: 1,
    },
  ];

  useEffect(() => {
    if (!cardRef.current) return;
    gsap.fromTo(cardRef.current,
      { opacity: 0, y: 16 },
      { opacity: 1, y: 0, duration: 0.55, ease: "power2.out", delay: 0.15 }
    );

    const validItems = itemRefs.current.filter(Boolean);
    if (validItems.length) {
      gsap.fromTo(validItems,
        { opacity: 0, y: 10 },
        { opacity: 1, y: 0, duration: 0.4, stagger: 0.08, ease: "power2.out", delay: 0.3 }
      );
    }
  }, []);

  const scoreColor = (s: number) => {
    if (s >= 0.85) return "#059669";
    if (s >= 0.75) return "#d97706";
    return "#dc2626";
  };

  return (
    <div ref={cardRef} className="card h-full">
      {/* Header */}
      <div className="card-header">
        <div className="flex items-center gap-2.5">
          <div className="icon-chip icon-chip-amber">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-heading font-bold text-[13px]" style={{ color: "var(--text-primary)" }}>
              Reservoir + Formation Correlation Engine
            </h3>
            <p className="text-[11px]" style={{ color: "var(--text-muted)" }}>
              Transparent weighted 7-factor offset well similarity engine
            </p>
          </div>
        </div>
        <span
          className="text-[10.5px] font-mono font-semibold px-2.5 py-1 rounded-md"
          style={{ background: "var(--pine-pale)", color: "var(--pine)", border: "1px solid #b2d8c8" }}
        >
          7-Factor Score
        </span>
      </div>

      {/* Analog Well Cards */}
      <div className="card-body">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {analogs.map((a, i) => {
            const isSelected = selectedAnalog === a.well;
            const sc = scoreColor(a.score);

            return (
              <div
                key={a.well}
                ref={(el) => { itemRefs.current[i] = el; }}
                onClick={() => setSelectedAnalog(a.well)}
                className="rounded-xl p-3.5 cursor-pointer transition-all duration-200"
                style={{
                  background: isSelected ? "var(--pine-pale)" : "var(--surface-2)",
                  border: `1.5px solid ${isSelected ? "#2d8a67" : "var(--border)"}`,
                  boxShadow: isSelected ? "0 2px 12px rgba(26, 92, 69, 0.12)" : "none"
                }}
              >
                {/* Well Name + Score */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-1.5">
                    <span className="font-heading font-bold text-[13px]" style={{ color: "var(--text-primary)" }}>
                      {a.well.replace("SYN-", "")}
                    </span>
                    {isSelected && <CheckCircle2 className="w-4 h-4" style={{ color: "var(--pine)" }} />}
                  </div>
                  <div
                    className="font-mono font-black text-base"
                    style={{ color: sc }}
                  >
                    {(a.score * 100).toFixed(0)}
                    <span className="text-xs font-normal ml-0.5">%</span>
                  </div>
                </div>

                {/* Score Bar */}
                <div className="progress-track mb-3">
                  <div
                    className="progress-fill"
                    style={{ width: `${a.score * 100}%`, background: sc }}
                  />
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-x-3 gap-y-1.5 text-[11px] font-mono">
                  <div>
                    <div className="text-[9px] uppercase font-semibold mb-0.5" style={{ color: "var(--text-muted)" }}>
                      Distance
                    </div>
                    <div className="font-bold" style={{ color: "var(--text-primary)" }}>{a.dist_km} km</div>
                  </div>
                  <div>
                    <div className="text-[9px] uppercase font-semibold mb-0.5" style={{ color: "var(--text-muted)" }}>
                      Depth Delta
                    </div>
                    <div className="font-bold" style={{ color: "var(--text-primary)" }}>{a.depth_delta}</div>
                  </div>
                  <div>
                    <div className="text-[9px] uppercase font-semibold mb-0.5" style={{ color: "var(--text-muted)" }}>
                      Fmt Match
                    </div>
                    <div className="font-bold" style={{ color: "var(--success)" }}>{a.fmt_match}</div>
                  </div>
                  <div>
                    <div className="text-[9px] uppercase font-semibold mb-0.5" style={{ color: "var(--text-muted)" }}>
                      Res Match
                    </div>
                    <div className="font-bold" style={{ color: "var(--success)" }}>{a.res_match}</div>
                  </div>
                </div>

                {/* Hazards + Provenance */}
                <div
                  className="mt-3 pt-2.5 flex items-center justify-between text-[10px]"
                  style={{ borderTop: "1px solid var(--border)" }}
                >
                  <span className="font-semibold" style={{ color: a.hazards > 1 ? "#dc2626" : "var(--text-secondary)" }}>
                    {a.hazards} Historical Hazard{a.hazards !== 1 ? "s" : ""}
                  </span>
                  <span
                    className="font-mono px-1.5 py-0.5 rounded"
                    style={{
                      background: "var(--surface-3)",
                      color: "var(--text-muted)",
                      border: "1px solid var(--border)"
                    }}
                  >
                    SYNTHETIC
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
