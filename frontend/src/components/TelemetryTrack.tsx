"use client";

import React, { useEffect, useRef } from "react";
import {
  Activity, Gauge, Zap, TrendingDown, RotateCw, Droplets, BarChart3
} from "lucide-react";
import gsap from "gsap";

export interface TelemetryData {
  measured_depth_m: number;
  tvdss_m: number;
  rop_mhr: number;
  wob_klbs: number;
  surface_torque_kftlb: number;
  rpm: number;
  standpipe_pressure_psi: number;
  flow_rate_gpm: number;
  mud_density_in_sg: number;
  mud_density_out_sg: number;
  ecd_downhole_sg: number;
  gas_total_pct: number;
  pit_volume_gain_bbls: number;
  teale_mse_psi: number;
  mse_baseline_ratio: number;
  is_alert: boolean;
}

interface TelemetryTrackProps {
  telemetry: TelemetryData;
  history: Array<{ depth: number; mse: number; rop: number; torque: number }>;
}

export const TelemetryTrack: React.FC<TelemetryTrackProps> = ({ telemetry, history }) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const mseRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (cardRef.current) {
      gsap.fromTo(cardRef.current,
        { opacity: 0, y: 16 },
        { opacity: 1, y: 0, duration: 0.6, ease: "power2.out", delay: 0.3 }
      );
    }
  }, []);

  useEffect(() => {
    if (mseRef.current && telemetry.is_alert) {
      gsap.fromTo(mseRef.current,
        { borderColor: "#fde68a" },
        { borderColor: "#fca5a5", duration: 0.6, repeat: -1, yoyo: true, ease: "sine.inOut" }
      );
    } else if (mseRef.current) {
      gsap.killTweensOf(mseRef.current);
    }
  }, [telemetry.is_alert]);

  const gauges = [
    {
      label: "Bit Depth (MD)",
      value: telemetry.measured_depth_m.toFixed(2),
      unit: "m",
      sub: `TVDSS: ${telemetry.tvdss_m.toFixed(1)}m`,
      icon: <TrendingDown className="w-4 h-4" />,
      color: "var(--pine)",
      alert: false,
    },
    {
      label: "ROP",
      value: telemetry.rop_mhr.toFixed(1),
      unit: "m/h",
      sub: "Tipam Sand",
      icon: <Activity className="w-4 h-4" />,
      color: telemetry.is_alert ? "#dc2626" : "var(--text-primary)",
      alert: telemetry.is_alert && telemetry.rop_mhr < 14,
    },
    {
      label: "WOB",
      value: telemetry.wob_klbs.toFixed(1),
      unit: "klbs",
      sub: "Max: 25.0",
      icon: <Gauge className="w-4 h-4" />,
      color: "var(--text-primary)",
      alert: false,
    },
    {
      label: "Torque",
      value: telemetry.surface_torque_kftlb.toFixed(1),
      unit: "kft-lb",
      sub: `RPM: ${telemetry.rpm.toFixed(0)}`,
      icon: <RotateCw className="w-4 h-4" />,
      color: telemetry.is_alert ? "#dc2626" : "var(--text-primary)",
      alert: telemetry.is_alert && telemetry.surface_torque_kftlb > 14,
    },
  ];

  return (
    <div ref={cardRef} className="card flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="card-header">
        <div className="flex items-center gap-2.5">
          <span className="live-dot" />
          <div>
            <h3 className="font-heading font-bold text-[13px]" style={{ color: "var(--text-primary)" }}>
              Panel 4 · Live 1 Hz Telemetry & Physics Engine
            </h3>
            <p className="text-[11px]" style={{ color: "var(--text-muted)" }}>WITSML v1.4.1.1</p>
          </div>
        </div>
        <span className="badge badge-success">LIVE</span>
      </div>

      <div className="card-body space-y-3">
        {/* Gauge Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
          {gauges.map((g) => (
            <div
              key={g.label}
              className="metric-tile"
              style={g.alert ? {
                background: "#fef2f2",
                borderColor: "#fca5a5"
              } : {}}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[9.5px] uppercase font-bold tracking-wider" style={{ color: "var(--text-muted)" }}>
                  {g.label}
                </span>
                <span style={{ color: g.alert ? "#dc2626" : "var(--text-muted)" }}>{g.icon}</span>
              </div>
              <div className="font-mono font-black text-xl leading-none" style={{ color: g.color }}>
                {g.value}
                <span className="text-[11px] font-normal ml-1" style={{ color: "var(--text-muted)" }}>{g.unit}</span>
              </div>
              <div className="text-[10px] mt-1 font-mono" style={{ color: "var(--text-muted)" }}>{g.sub}</div>
            </div>
          ))}
        </div>

        {/* Teale MSE */}
        <div
          ref={mseRef}
          className="rounded-xl p-3.5 col-span-2 transition-all"
          style={{
            background: telemetry.is_alert ? "#fffbeb" : "#ecfdf5",
            border: `1px solid ${telemetry.is_alert ? "#fde68a" : "#a7f3d0"}`,
            borderLeft: `4px solid ${telemetry.is_alert ? "#d97706" : "#059669"}`
          }}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="flex items-center gap-1.5 font-heading font-bold text-[12px]" style={{ color: "var(--text-primary)" }}>
              <Zap className="w-4 h-4" style={{ color: telemetry.is_alert ? "#d97706" : "#059669" }} />
              Teale Mechanical Specific Energy (MSE)
            </span>
            <span
              className="font-mono text-[10px] font-bold px-2 py-0.5 rounded"
              style={{
                background: telemetry.is_alert ? "#fef3c7" : "#d1fae5",
                color: telemetry.is_alert ? "#92400e" : "#065f46",
                border: `1px solid ${telemetry.is_alert ? "#fde68a" : "#a7f3d0"}`
              }}
            >
              {telemetry.mse_baseline_ratio.toFixed(2)}× Baseline
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="font-mono font-black text-2xl" style={{ color: telemetry.is_alert ? "#d97706" : "#059669" }}>
              {telemetry.teale_mse_psi.toLocaleString()}
            </span>
            <span className="text-xs" style={{ color: "var(--text-muted)" }}>psi (8½″ Bit)</span>
          </div>
          <p className="text-[11px] mt-1" style={{ color: "var(--text-secondary)" }}>
            {telemetry.is_alert
              ? "⚠️ Mechanical inefficiency: MSE rising while ROP stalls — differential drag signature."
              : "✓ Mechanical efficiency within normal baseline envelope."}
          </p>
        </div>

        {/* Hydraulics */}
        <div className="metric-tile">
          <div className="flex items-center justify-between mb-2.5">
            <span className="flex items-center gap-1.5 font-heading font-bold text-[12px]" style={{ color: "var(--text-primary)" }}>
              <Droplets className="w-4 h-4" style={{ color: "#2563eb" }} />
              Hydraulics & Mud Window
            </span>
            <span className="font-mono text-[10px]" style={{ color: "var(--text-secondary)" }}>
              SPP: {telemetry.standpipe_pressure_psi} psi · Flow: {telemetry.flow_rate_gpm} gpm
            </span>
          </div>
          <div
            className="grid grid-cols-3 gap-2 text-center pt-2"
            style={{ borderTop: "1px solid var(--border)" }}
          >
            {[
              { label: "MW In / Out", value: `${telemetry.mud_density_in_sg} SG`, color: "var(--text-primary)" },
              { label: "ECD Downhole", value: `${telemetry.ecd_downhole_sg} SG`, color: "#2563eb" },
              { label: "Kick Margin", value: "+0.06 SG", color: "#059669" },
            ].map((item) => (
              <div key={item.label}>
                <div className="text-[9px] uppercase font-semibold mb-1" style={{ color: "var(--text-muted)" }}>
                  {item.label}
                </div>
                <div className="font-mono font-black text-sm" style={{ color: item.color }}>
                  {item.value}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Strip Chart */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
              Continuous Depth Trend (Last 10 Meters)
            </span>
            <div className="flex items-center gap-3 text-[10px] font-mono">
              <span className="flex items-center gap-1" style={{ color: "#d97706" }}>
                <span className="inline-block w-3 h-0.5" style={{ background: "#d97706" }} /> MSE
              </span>
              <span className="flex items-center gap-1" style={{ color: "#059669" }}>
                <span className="inline-block w-3 h-0.5" style={{ background: "#059669" }} /> ROP
              </span>
            </div>
          </div>
          <div
            className="h-16 rounded-xl p-2 relative overflow-hidden"
            style={{ background: "var(--surface-2)", border: "1px solid var(--border)" }}
          >
            <svg className="w-full h-full" viewBox="0 0 400 50">
              {/* Guide lines */}
              <line x1="0" y1="15" x2="400" y2="15" stroke="var(--border)" strokeWidth="0.8" strokeDasharray="3 3" />
              <line x1="0" y1="35" x2="400" y2="35" stroke="var(--border)" strokeWidth="0.8" strokeDasharray="3 3" />

              {/* ROP Curve */}
              <polyline
                fill="none" stroke="#059669" strokeWidth="2"
                points="0,30 40,28 80,26 120,32 160,29 200,28 240,36 280,41 320,43 360,45 400,46"
              />

              {/* MSE Curve */}
              <polyline
                fill="none" stroke="#d97706" strokeWidth="2.5"
                points={
                  telemetry.is_alert
                    ? "0,38 40,36 80,35 120,34 160,32 200,28 240,20 280,14 320,9 360,7 400,5"
                    : "0,38 40,36 80,35 120,34 160,32 200,34 240,33 280,35 320,34 360,33 400,32"
                }
              />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
};
