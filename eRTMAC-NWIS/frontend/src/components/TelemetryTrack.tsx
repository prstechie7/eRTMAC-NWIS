"use client";

import React from "react";
import {
  Activity,
  Gauge,
  Zap,
  TrendingDown,
  RotateCw,
  Droplets,
  Flame,
  BarChart3,
} from "lucide-react";

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
  return (
    <div className="bg-white rounded-lg border border-[#E2E8F0] shadow-sm overflow-hidden flex flex-col h-full">
      {/* Header */}
      <div className="bg-[#F8F9FA] px-4 py-2.5 border-b border-[#E2E8F0] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#184E3A]"></div>
          <span className="font-bold text-xs uppercase tracking-wider text-[#184E3A]">
            Panel 4 · Live 1 Hz Telemetry & Physics Engine
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-gray-500">WITSML v1.4.1.1 Stream</span>
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        </div>
      </div>

      {/* Main Grid of Rig Sensor Gauges */}
      <div className="p-4 grid grid-cols-2 md:grid-cols-4 gap-2.5 text-xs">
        {/* Bit Depth */}
        <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
          <div className="text-[10px] text-gray-500 uppercase font-bold flex items-center justify-between">
            <span>Bit Depth (MD)</span>
            <TrendingDown className="w-3 h-3 text-[#184E3A]" />
          </div>
          <div className="text-lg font-black font-mono text-[#184E3A] mt-0.5">
            {telemetry.measured_depth_m.toFixed(2)}
            <span className="text-[10px] font-normal text-gray-500 ml-1">m</span>
          </div>
          <div className="text-[10px] text-gray-500 font-mono">
            TVDSS: {telemetry.tvdss_m.toFixed(1)}m
          </div>
        </div>

        {/* Rate of Penetration */}
        <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
          <div className="text-[10px] text-gray-500 uppercase font-bold flex items-center justify-between">
            <span>ROP (Instantaneous)</span>
            <Activity className="w-3 h-3 text-[#E58A13]" />
          </div>
          <div className="text-lg font-black font-mono text-[#1E242B] mt-0.5">
            {telemetry.rop_mhr.toFixed(1)}
            <span className="text-[10px] font-normal text-gray-500 ml-1">m/hr</span>
          </div>
          <div className="text-[10px] text-gray-500 font-mono">Formation: Tipam Sand</div>
        </div>

        {/* Weight on Bit */}
        <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
          <div className="text-[10px] text-gray-500 uppercase font-bold flex items-center justify-between">
            <span>Weight on Bit (WOB)</span>
            <Gauge className="w-3 h-3 text-blue-600" />
          </div>
          <div className="text-lg font-black font-mono text-[#1E242B] mt-0.5">
            {telemetry.wob_klbs.toFixed(1)}
            <span className="text-[10px] font-normal text-gray-500 ml-1">klbs</span>
          </div>
          <div className="text-[10px] text-gray-500 font-mono">Limit: 25.0 klbs</div>
        </div>

        {/* Surface Torque */}
        <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
          <div className="text-[10px] text-gray-500 uppercase font-bold flex items-center justify-between">
            <span>Surface Torque</span>
            <RotateCw className="w-3 h-3 text-amber-600" />
          </div>
          <div className="text-lg font-black font-mono text-[#1E242B] mt-0.5">
            {telemetry.surface_torque_kftlb.toFixed(1)}
            <span className="text-[10px] font-normal text-gray-500 ml-1">kft-lb</span>
          </div>
          <div className="text-[10px] text-gray-500 font-mono">RPM: {telemetry.rpm.toFixed(0)}</div>
        </div>

        {/* Teale's MSE (Physics-Informed Anomaly Indicator) */}
        <div
          className={`p-2.5 rounded border col-span-2 transition-colors ${
            telemetry.is_alert
              ? "bg-amber-50 border-amber-300 ring-1 ring-amber-400"
              : "bg-emerald-50/60 border-emerald-200"
          }`}
        >
          <div className="text-[10px] uppercase font-bold flex items-center justify-between">
            <span className="flex items-center gap-1 text-[#184E3A]">
              <Zap className="w-3 h-3 text-[#E58A13]" />
              Teale Mechanical Specific Energy (MSE)
            </span>
            <span
              className={`font-mono font-bold px-1.5 py-0.2 rounded text-[10px] ${
                telemetry.is_alert
                  ? "bg-amber-200 text-amber-900"
                  : "bg-emerald-200 text-emerald-900"
              }`}
            >
              {telemetry.mse_baseline_ratio.toFixed(2)}x Baseline
            </span>
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-xl font-black font-mono text-[#184E3A]">
              {telemetry.teale_mse_psi.toLocaleString()}
            </span>
            <span className="text-[11px] text-gray-600 font-medium">psi (8½" Bit)</span>
          </div>
          <p className="text-[10px] text-gray-600 mt-0.5">
            {telemetry.is_alert
              ? "⚠️ Inefficient drilling detected: MSE rising while ROP stalls. Indicates drag increase / imminent sticking."
              : "✓ Mechanical efficiency within baseline envelope."}
          </p>
        </div>

        {/* Hydraulics & Mud Parameters */}
        <div className="bg-slate-50 p-2.5 rounded border border-slate-200 col-span-2">
          <div className="text-[10px] text-gray-500 uppercase font-bold flex items-center justify-between mb-1">
            <span className="flex items-center gap-1">
              <Droplets className="w-3 h-3 text-cyan-600" />
              Hydraulics & Mud Window
            </span>
            <span className="font-mono text-[10px]">SPP: {telemetry.standpipe_pressure_psi} psi</span>
          </div>
          <div className="grid grid-cols-3 gap-2 text-center pt-1 border-t border-slate-200">
            <div>
              <div className="text-[9px] text-gray-500">MW In / Out</div>
              <div className="font-mono font-bold text-gray-800">
                {telemetry.mud_density_in_sg} SG
              </div>
            </div>
            <div>
              <div className="text-[9px] text-gray-500">ECD Downhole</div>
              <div className="font-mono font-bold text-blue-700">
                {telemetry.ecd_downhole_sg} SG
              </div>
            </div>
            <div>
              <div className="text-[9px] text-gray-500">Kick Margin</div>
              <div className="font-mono font-bold text-emerald-700">+0.06 SG</div>
            </div>
          </div>
        </div>
      </div>

      {/* Mini Strip-Chart / Log Tracks Visualization */}
      <div className="px-4 pb-3 flex-1 flex flex-col justify-end">
        <div className="text-[10px] font-bold text-gray-500 uppercase mb-1 flex items-center justify-between">
          <span>Continuous Depth Trend (Last 10 Meters)</span>
          <span className="text-[#E58A13] font-mono">Teale MSE (Orange) vs ROP (Green)</span>
        </div>
        <div className="h-20 bg-slate-50 rounded border border-slate-200 p-1.5 relative overflow-hidden flex items-end">
          <svg className="w-full h-full" viewBox="0 0 400 60">
            {/* Guide lines */}
            <line x1="0" y1="20" x2="400" y2="20" stroke="#E2E8F0" strokeWidth="1" strokeDasharray="3 3" />
            <line x1="0" y1="40" x2="400" y2="40" stroke="#E2E8F0" strokeWidth="1" strokeDasharray="3 3" />

            {/* ROP Curve (Green) */}
            <polyline
              fill="none"
              stroke="#184E3A"
              strokeWidth="2"
              points="0,35 40,32 80,30 120,38 160,33 200,31 240,42 280,48 320,50 360,52 400,53"
            />

            {/* MSE Curve (Orange - Spikes during hazard) */}
            <polyline
              fill="none"
              stroke="#E58A13"
              strokeWidth="2.2"
              points={
                telemetry.is_alert
                  ? "0,45 40,43 80,42 120,40 160,38 200,35 240,25 280,18 320,12 360,10 400,8"
                  : "0,45 40,43 80,42 120,40 160,38 200,42 240,41 280,43 320,42 360,40 400,39"
              }
            />
          </svg>
        </div>
      </div>
    </div>
  );
};
