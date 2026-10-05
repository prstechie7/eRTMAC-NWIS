"use client";

import React, { useEffect, useRef, useState } from "react";
import {
  AlertTriangle,
  ShieldAlert,
  FileDown,
  CheckCircle2,
  MapPin,
  ArrowRight,
  RefreshCw,
  FastForward,
  Eye,
} from "lucide-react";
import gsap from "gsap";

interface LookAheadProps {
  currentDepthMd: number;
  currentTvdss: number;
  riskIndex: number;
  isAlertActive: boolean;
  distanceAheadM: number;
  onExportPdf: () => void;
  onTriggerAlert: () => void;
  onAdvanceDepth: () => void;
  onResetSim: () => void;
  isExporting: boolean;
}

export const LookAheadCard: React.FC<LookAheadProps> = ({
  currentDepthMd,
  currentTvdss,
  riskIndex,
  isAlertActive,
  distanceAheadM,
  onExportPdf,
  onTriggerAlert,
  onAdvanceDepth,
  onResetSim,
  isExporting,
}) => {
  const [windowSize, setWindowSize] = useState(100);
  const [mitigationsChecked, setMitigationsChecked] = useState<{ [key: number]: boolean }>({
    0: true, 1: false, 2: true, 3: false,
  });
  const cardRef = useRef<HTMLDivElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);

  const toggleMitigation = (index: number) => {
    setMitigationsChecked((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  const mitigations = [
    {
      title: "Stationary Drillstring Limitation",
      desc: "Strictly limit stationary drillstring time to < 90 seconds across 2,430m – 2,480m MD.",
      critical: true,
    },
    {
      title: "Mud Density Adjustment",
      desc: "Reduce mud density from 1.16 SG to 1.10 SG if Girujan Clay permits.",
      critical: false,
    },
    {
      title: "Lubricating Pill Pre-Spotting",
      desc: "Spot 40 bbls lubricating / anti-sticking pill prior to traversing depleted sand package.",
      critical: true,
    },
    {
      title: "Continuous Drillstring Rotation",
      desc: "Maintain continuous drillstring rotation (>40 RPM) during all MWD survey operations.",
      critical: false,
    },
  ];

  useEffect(() => {
    if (!cardRef.current) return;
    gsap.fromTo(cardRef.current,
      { opacity: 0, y: 16 },
      { opacity: 1, y: 0, duration: 0.6, ease: "power2.out", delay: 0.25 }
    );
  }, []);

  useEffect(() => {
    if (isAlertActive && headerRef.current) {
      gsap.fromTo(headerRef.current,
        { backgroundColor: "#fef2f2" },
        {
          backgroundColor: "#fee2e2",
          duration: 0.8,
          repeat: -1,
          yoyo: true,
          ease: "sine.inOut"
        }
      );
    } else if (headerRef.current) {
      gsap.killTweensOf(headerRef.current);
    }
    return () => {
      if (headerRef.current) gsap.killTweensOf(headerRef.current);
    };
  }, [isAlertActive]);

  const riskBarColor = riskIndex > 70 ? "#dc2626" : riskIndex > 40 ? "#d97706" : "#059669";
  const checkedCount = Object.values(mitigationsChecked).filter(Boolean).length;

  return (
    <div
      ref={cardRef}
      className="card flex flex-col h-full overflow-hidden"
      style={{
        borderColor: isAlertActive ? "#fca5a5" : "var(--border)",
        borderWidth: isAlertActive ? "1.5px" : "1px",
      }}
    >
      {/* Header */}
      <div
        ref={headerRef}
        className="px-4 py-3 flex items-center justify-between"
        style={{
          background: isAlertActive ? "#fef2f2" : "var(--surface-2)",
          borderBottom: `1px solid ${isAlertActive ? "#fca5a5" : "var(--border)"}`
        }}
      >
        <div className="flex items-center gap-2.5">
          <div className={`icon-chip ${isAlertActive ? "icon-chip-danger" : "icon-chip-amber"}`}>
            {isAlertActive
              ? <ShieldAlert className="w-4 h-4" />
              : <AlertTriangle className="w-4 h-4" />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-heading font-bold text-[13px]" style={{ color: "var(--text-primary)" }}>
                Panel 3 · Real-Time Look-Ahead Advisory
              </h3>
              <span className={`badge ${isAlertActive ? "badge-danger" : "badge-warning"}`}>
                {isAlertActive ? "CRITICAL ALERT" : "ADVISORY WATCH"}
              </span>
            </div>
          </div>
        </div>

        {/* Window + Risk Index */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 text-[10px]">
            <Eye className="w-3.5 h-3.5" style={{ color: "var(--text-muted)" }} />
            {[50, 100, 150].map((w) => (
              <button
                key={w}
                onClick={() => setWindowSize(w)}
                className="font-mono px-1.5 py-0.5 rounded transition-all"
                style={{
                  background: windowSize === w ? "var(--amber)" : "var(--surface-3)",
                  color: windowSize === w ? "white" : "var(--text-muted)",
                  border: `1px solid ${windowSize === w ? "var(--amber)" : "var(--border)"}`,
                  fontSize: 10
                }}
              >
                {w}m
              </button>
            ))}
          </div>
          <div className="text-right">
            <div className="text-[9px] uppercase font-bold tracking-wider" style={{ color: "var(--text-muted)" }}>
              Risk Index R_H
            </div>
            <div
              className="font-mono font-black text-lg leading-none"
              style={{ color: riskBarColor }}
            >
              {riskIndex.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      <div className="card-body flex flex-col gap-3 flex-1">
        {/* Main Alert Box */}
        <div
          className={`p-3.5 rounded-xl ${isAlertActive ? "alert-critical" : "alert-warning"}`}
        >
          <div className="flex items-center justify-between gap-3">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1.5">
                <span className="font-heading font-bold text-[13px]" style={{ color: "var(--text-primary)" }}>
                  Differential Sticking Hazard Ahead
                </span>
                <span className="badge badge-warning">Upper Tipam Sand</span>
              </div>
              <p className="text-[11.5px]" style={{ color: "var(--text-secondary)" }}>
                Depleted sandstone pore pressure:{" "}
                <strong style={{ color: "var(--text-primary)" }}>0.88 SG</strong>. Overbalance:{" "}
                <strong className="font-mono" style={{ color: "#dc2626" }}>1,120 psi</strong>
              </p>
            </div>

            {/* Stats */}
            <div
              className="flex gap-4 pl-3.5 flex-shrink-0 text-center"
              style={{ borderLeft: "1px solid var(--border)" }}
            >
              <div>
                <div className="text-[9px] uppercase font-bold tracking-wider mb-0.5" style={{ color: "var(--text-muted)" }}>
                  Delta Ahead
                </div>
                <div
                  className="font-mono font-black text-xl leading-none"
                  style={{ color: isAlertActive ? "#dc2626" : "#d97706" }}
                >
                  {distanceAheadM.toFixed(1)}m
                </div>
              </div>
              <div>
                <div className="text-[9px] uppercase font-bold tracking-wider mb-0.5" style={{ color: "var(--text-muted)" }}>
                  Target Depth
                </div>
                <div className="font-mono font-bold text-sm" style={{ color: "var(--text-primary)" }}>2,448.5m</div>
              </div>
            </div>
          </div>

          {/* Risk bar */}
          <div className="mt-3">
            <div className="progress-track" style={{ height: 5 }}>
              <div
                className="progress-fill"
                style={{ width: `${riskIndex}%`, background: riskBarColor }}
              />
            </div>
          </div>
        </div>

        {/* Historical Evidence */}
        <div
          className="rounded-xl p-3.5 text-xs"
          style={{ background: "var(--surface-2)", border: "1px solid var(--border)" }}
        >
          <div className="flex items-center justify-between mb-2.5">
            <span className="font-heading font-bold text-[12px] flex items-center gap-1.5" style={{ color: "var(--text-primary)" }}>
              <MapPin className="w-3.5 h-3.5" style={{ color: "var(--amber)" }} />
              Historical Grounding · SYN-NHK-01 Offset
            </span>
            <span className="font-mono text-[10px]" style={{ color: "var(--text-muted)" }}>
              1.42 km SW · Same Stratigraphic Horizon (+1.5m TSD)
            </span>
          </div>
          <div
            className="grid grid-cols-3 gap-3 p-3 rounded-lg"
            style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
          >
            {[
              { label: "Incident", value: "Stuck Pipe (38.5h NPT)", color: "#dc2626" },
              { label: "Root Cause", value: "Stationary 45 min in survey", color: "var(--text-secondary)" },
              { label: "Resolution", value: "Spotted 40 bbls lubricant pill", color: "var(--text-secondary)" },
            ].map((item) => (
              <div key={item.label}>
                <div className="text-[9px] uppercase font-semibold mb-1" style={{ color: "var(--text-muted)" }}>
                  {item.label}
                </div>
                <div className="font-bold text-[11px]" style={{ color: item.color }}>
                  {item.value}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Checklist */}
        <div>
          <div className="flex items-center justify-between mb-2.5">
            <span className="font-heading font-bold text-[12px] flex items-center gap-1.5" style={{ color: "var(--text-primary)" }}>
              <CheckCircle2 className="w-4 h-4" style={{ color: "var(--success)" }} />
              Mandatory Tour Advisory Checklist (Driller SOP)
              <span className="font-mono text-[10px] px-1.5 py-0.5 rounded" style={{ background: "#ecfdf5", color: "#065f46", border: "1px solid #a7f3d0" }}>
                {checkedCount}/{mitigations.length}
              </span>
            </span>
            <span className="text-[10px] font-mono" style={{ color: "var(--text-muted)" }}>
              Qualified Engineer Review Required
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {mitigations.map((item, idx) => (
              <div
                key={idx}
                onClick={() => toggleMitigation(idx)}
                className={`checklist-item ${mitigationsChecked[idx] ? "checked" : ""} flex items-start gap-2.5`}
              >
                <input
                  type="checkbox"
                  checked={!!mitigationsChecked[idx]}
                  onChange={() => {}}
                  className="mt-0.5 cursor-pointer rounded"
                  style={{ accentColor: "var(--success)" }}
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 mb-0.5">
                    <span className="font-semibold text-[11px]" style={{ color: "var(--text-primary)" }}>
                      {item.title}
                    </span>
                    {item.critical && (
                      <span className="badge badge-danger" style={{ fontSize: 8 }}>Mandatory</span>
                    )}
                  </div>
                  <p className="text-[10px] leading-snug line-clamp-1" style={{ color: "var(--text-secondary)" }}>
                    {item.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="card-footer flex flex-wrap items-center justify-between gap-2.5">
        <div className="flex items-center gap-2">
          <button
            onClick={onTriggerAlert}
            className="btn btn-danger text-[11px]"
          >
            <FastForward className="w-3.5 h-3.5" />
            Simulate (2,414m)
          </button>
          <button
            onClick={onAdvanceDepth}
            className="btn btn-outline text-[11px]"
          >
            <ArrowRight className="w-3.5 h-3.5" style={{ color: "var(--pine)" }} />
            +1m
          </button>
          <button
            onClick={onResetSim}
            className="btn btn-ghost"
            title="Reset Simulation to 2,410m"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>

        <button
          onClick={onExportPdf}
          disabled={isExporting}
          className="btn btn-amber"
          style={{ fontSize: 12 }}
        >
          <FileDown className="w-4 h-4" />
          {isExporting ? "Exporting..." : "Download Tour Advisory PDF"}
        </button>
      </div>
    </div>
  );
};
