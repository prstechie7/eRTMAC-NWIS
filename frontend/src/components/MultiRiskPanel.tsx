"use client";

import React, { useRef, useEffect } from "react";
import { ShieldAlert, FileText } from "lucide-react";
import gsap from "gsap";

interface MultiRiskPanelProps {
  currentDepthMd: number;
}

export const MultiRiskPanel: React.FC<MultiRiskPanelProps> = ({ currentDepthMd }) => {
  const isAlert = currentDepthMd >= 2413.0;
  const cardRef = useRef<HTMLDivElement>(null);
  const barsRef = useRef<(HTMLDivElement | null)[]>([]);

  const risks = [
    {
      type: "STUCK PIPE",
      score: isAlert ? 81 : 20,
      level: isAlert ? "HIGH" : "LOW",
      levelColor: isAlert ? "#dc2626" : "#059669",
      levelBg: isAlert ? "#fef2f2" : "#ecfdf5",
      levelBorder: isAlert ? "#fca5a5" : "#a7f3d0",
      barColor: isAlert ? "#dc2626" : "#059669",
      trigger: isAlert ? "Torque trend elevated (>15 kft-lbs), ROP declining" : "Normal torque band",
    },
    {
      type: "MUD LOSS",
      score: 15,
      level: "LOW",
      levelColor: "#059669",
      levelBg: "#ecfdf5",
      levelBorder: "#a7f3d0",
      barColor: "#059669",
      trigger: "Stable pit volume balance",
    },
    {
      type: "OVERPRESSURE",
      score: isAlert ? 45 : 18,
      level: isAlert ? "MEDIUM" : "LOW",
      levelColor: isAlert ? "#d97706" : "#059669",
      levelBg: isAlert ? "#fffbeb" : "#ecfdf5",
      levelBorder: isAlert ? "#fde68a" : "#a7f3d0",
      barColor: isAlert ? "#d97706" : "#059669",
      trigger: isAlert ? "Elevated total gas (3.2%)" : "Normal pore pressure trend",
    },
    {
      type: "TORQUE SPIKE",
      score: isAlert ? 50 : 12,
      level: isAlert ? "MEDIUM" : "LOW",
      levelColor: isAlert ? "#d97706" : "#059669",
      levelBg: isAlert ? "#fffbeb" : "#ecfdf5",
      levelBorder: isAlert ? "#fde68a" : "#a7f3d0",
      barColor: isAlert ? "#d97706" : "#059669",
      trigger: isAlert ? "Torque z-score anomaly (>2.5σ)" : "Torque within normal band",
    },
    {
      type: "CEMENTING",
      score: 0,
      level: "NO DATA",
      levelColor: "#64748b",
      levelBg: "#f8fafc",
      levelBorder: "#e2e8f0",
      barColor: "#cbd5e1",
      trigger: "Insufficient cementing parameters available",
    },
  ];

  useEffect(() => {
    if (cardRef.current) {
      gsap.fromTo(cardRef.current,
        { opacity: 0, y: 16 },
        { opacity: 1, y: 0, duration: 0.55, ease: "power2.out", delay: 0.2 }
      );
    }

    // Animate bars
    const validBars = barsRef.current.filter(Boolean);
    if (validBars.length) {
      validBars.forEach((bar, i) => {
        if (!bar) return;
        const targetWidth = bar.getAttribute("data-width") || "0%";
        gsap.fromTo(bar,
          { width: "0%" },
          { width: targetWidth, duration: 0.8, ease: "power2.out", delay: 0.5 + i * 0.07 }
        );
      });
    }
  }, [isAlert]);

  return (
    <div ref={cardRef} className="card h-full">
      {/* Header */}
      <div className="card-header">
        <div className="flex items-center gap-2.5">
          <div className="icon-chip icon-chip-danger">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-heading font-bold text-[13px]" style={{ color: "var(--text-primary)" }}>
              Multi-Risk Prediction Engine
            </h3>
            <p className="text-[11px]" style={{ color: "var(--text-muted)" }}>
              5-Risk hybrid physics & ML feature detection pipeline
            </p>
          </div>
        </div>
        <span
          className="text-[10.5px] font-mono font-semibold px-2.5 py-1 rounded-md"
          style={{ background: "#f5f3ff", color: "#6d28d9", border: "1px solid #ddd6fe" }}
        >
          PROVENANCE: SYNTHETIC
        </span>
      </div>

      <div className="card-body space-y-3">
        {/* Risk Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-2.5">
          {risks.map((r, i) => (
            <div
              key={r.type}
              className="rounded-xl p-3 transition-all"
              style={{
                background: "var(--surface-2)",
                border: "1px solid var(--border)"
              }}
            >
              <div className="flex items-start justify-between mb-2 gap-1">
                <span className="font-heading font-bold text-[11px]" style={{ color: "var(--text-primary)" }}>
                  {r.type}
                </span>
                <span
                  className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded flex-shrink-0"
                  style={{
                    background: r.levelBg,
                    color: r.levelColor,
                    border: `1px solid ${r.levelBorder}`
                  }}
                >
                  {r.level}
                </span>
              </div>

              {/* Probability */}
              <div className="flex items-baseline justify-between mb-1.5">
                <span className="text-[10px] font-mono" style={{ color: "var(--text-muted)" }}>
                  Probability
                </span>
                <span
                  className="font-mono font-black text-sm"
                  style={{ color: r.levelColor }}
                >
                  {r.score}%
                </span>
              </div>

              {/* Progress Bar */}
              <div className="progress-track mb-2">
                <div
                  ref={(el) => { barsRef.current[i] = el; }}
                  className="progress-fill"
                  data-width={`${r.score}%`}
                  style={{
                    width: `${r.score}%`,
                    background: r.barColor
                  }}
                />
              </div>

              <p className="text-[10px] leading-snug" style={{ color: "var(--text-secondary)" }}>
                {r.trigger}
              </p>
            </div>
          ))}
        </div>

        {/* Evidence Grounding Block */}
        <div
          className="rounded-xl p-3.5 text-xs"
          style={{
            background: "var(--surface-2)",
            border: "1px solid var(--border)"
          }}
        >
          <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4" style={{ color: "var(--amber)" }} />
              <span className="font-heading font-bold text-[12px]" style={{ color: "var(--text-primary)" }}>
                Document & Historical Evidence Grounding
              </span>
            </div>
            <span
              className="text-[10px] font-mono font-bold uppercase px-2.5 py-1 rounded-md"
              style={{ background: "#ecfdf5", color: "#065f46", border: "1px solid #a7f3d0" }}
            >
              Qualified Engineer Review Required
            </span>
          </div>
          <p className="text-[11.5px] leading-relaxed" style={{ color: "var(--text-secondary)" }}>
            <strong style={{ color: "var(--text-primary)" }}>Well SYN-NHK-01 (Depth 2,448.5m MD):</strong>{" "}
            Differential Sticking in depleted Upper Tipam Sandstone. NPT:{" "}
            <span className="font-mono font-black" style={{ color: "var(--amber)" }}>38.5h</span>. Report:{" "}
            <span
              className="font-mono px-1.5 py-0.5 rounded text-[11px]"
              style={{ background: "#fffbeb", color: "#92400e", border: "1px solid #fde68a" }}
            >
              DDR-NHK-SYN01-Day-42 (Page 4)
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};
