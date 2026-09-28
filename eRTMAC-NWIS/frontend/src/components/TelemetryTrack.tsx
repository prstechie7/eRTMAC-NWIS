"use client";

import React from "react";
import {
  Activity,
  Gauge,
  Zap,
  TrendingDown,
  RotateCw,
  Droplets,
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
      <div className="bg-[#F8F9FA] px-3.5 py-2 border-b border-[#E2E8F0] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#184E3A]"></div>
          <span className="font-bold text-xs uppercase tracking-wider text-[#184E3A]">
            Panel 4 · Live 1 Hz Telemetry & Physics Engine
          </span>
        </div>
        <div className="flex items-center gap-2 text-[11px] font-mono">
          <span className="text-gray-500">WITSML v1.4.1.1</span>
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        </div>
      </div>

      {/* Main Grid of Rig Sensor Gauges */}
      <div className="p-3 grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
        {/* Bit Depth */}
        <div className="bg-slate-50 p-2 rounded border border-slate-200">
          <div className="text-[9.5px] text-gray-500 uppercase font-bold flex items-center justify-between">
            <span>Bit Depth (MD)</span>
            <TrendingDown className="w-3 h-3 text-[#184E3A]" />
          </div>
          <div className="text-base font-black font-mono text-[#184E3A] mt-0.5">
            {telemetry.measured_depth_m.toFixed(2)}
            <span className="text-[9.5px] font-normal text-gray-500 ml-1">m</span>
          </div>
          <div className="text-[9.5px] text-gray-500 font-mono">
            TVDSS: {telemetry.tvdss_m.toFixed(1)}m
          </div>
        </div>

        {/* Rate of Penetration */}
        <div className="bg-slate-50 p-2 rounded border border-slate-200">
          <div className="text-[9.5px] text-gray-500 uppercase font-bold flex items-center justify-between">
            <span>ROP</span>
            <Activity className="w-3 h-3 text-[#E58A13]" />
          </div>
          <div className="text-base font-black font-mono text-[#1E242B] mt-0.5">
            {telemetry.rop_mhr.toFixed(1)}
            <span className="text-[9.5px] font-normal text-gray-500 ml-1">m/h</span>
          </div>
          <div className="text-[9.5px] text-gray-500 font-mono">Tipam Sand</div>
        </div>

        {/* Weight on Bit */}
        <div className="bg-slate-50 p-2 rounded border border-slate-200">
          <div className="text-[9.5px] text-gray-500 uppercase font-bold flex items-center justify-between">
            <span>WOB</span>
            <Gauge className="w-3 h-3 text-blue-600" />
          </div>
          <div className="text-base font-black font-mono text-[#1E242B] mt-0.5">
            {telemetry.wob_klbs.toFixed(1)}
            <span className="text-[9.5px] font-normal text-gray-500 ml-1">klbs</span>
          </div>
          <div className="text-[9.5px] text-gray-500 font-mono">Max: 25.0</div>
        </div>

        {/* Surface Torque */}
        <div className="bg-slate-50 p-2 rounded border border-slate-200">
          <div className="text-[9.5px] text-gray-500 uppercase font-bold flex items-center justify-between">
            <span>Torque</span>
            <RotateCw className="w-3 h-3 text-amber-600" />
          </div>
          <div className="text-base font-black font-mono text-[#1E242B] mt-0.5">
            {telemetry.surface_torque_kftlb.toFixed(1)}
            <span className="text-[9.5px] font-normal text-gray-500 ml-1">kft-lb</span>
          </div>
          <div className="text-[9.5px] text-gray-500 font-mono">RPM: {telemetry.rpm.toFixed(0)}</div>
        </div>

        {/* Teale's MSE Card */}
        <div
          className={`p-2 rounded border col-span-2 transition-colors ${
            telemetry.is_alert
              ? "bg-amber-50 border-amber-300 ring-1 ring-amber-400"
              : "bg-emerald-50/60 border-emerald-200"
          }`}
        >
          <div className="text-[9.5px] uppercase font-bold flex items-center justify-between">
            <span className="flex items-center gap-1 text-[#184E3A]">
              <Zap className="w-3 h-3 text-[#E58A13]" />
              Teale Mechanical Specific Energy (MSE)
            </span>
            <span
              className={`font-mono font-bold px-1.5 py-0.2 rounded text-[9.5px] ${
                telemetry.is_alert
                  ? "bg-amber-200 text-amber-900"
                  : "bg-emerald-200 text-emerald-900"
              }`}
            >
              {telemetry.mse_baseline_ratio.toFixed(2)}x Baseline
            </span>
          </div>
          <div className="flex items-baseline gap-1.5 mt-0.5">
            <span className="text-lg font-black font-mono text-[#184E3A]">
              {telemetry.teale_mse_psi.toLocaleString()}
            </span>
            <span className="text-[10px] text-gray-600 font-medium">psi (8½" Bit)</span>
          </div>
          <p className="text-[9.5px] text-gray-600 mt-0.5 line-clamp-1">
            {telemetry.is_alert
              ? "⚠️ Mechanical inefficiency: MSE rising while ROP stalls (differential drag)."
              : "✓ Mechanical efficiency within baseline envelope."}
          </p>
        </div>

        {/* Hydraulics & Mud Parameters */}
        <div className="bg-slate-50 p-2 rounded border border-slate-200 col-span-2">
          <div className="text-[9.5px] text-gray-500 uppercase font-bold flex items-center justify-between mb-0.5">
            <span className="flex items-center gap-1">
              <Droplets className="w-3 h-3 text-cyan-600" />
              Hydraulics & Mud Window
            </span>
            <span className="font-mono text-[9.5px]">SPP: {telemetry.standpipe_pressure_psi} psi</span>
          </div>
          <div className="grid grid-cols-3 gap-1 text-center pt-0.5 border-t border-slate-200 text-[10px]">
            <div>
              <div className="text-[8.5px] text-gray-500">MW In / Out</div>
              <div className="font-mono font-bold text-gray-800">
                {telemetry.mud_density_in_sg} SG
              </div>
            </div>
            <div>
              <div className="text-[8.5px] text-gray-500">ECD Downhole</div>
              <div className="font-mono font-bold text-blue-700">
                {telemetry.ecd_downhole_sg} SG
              </div>
            </div>
            <div>
              <div className="text-[8.5px] text-gray-500">Kick Margin</div>
              <div className="font-mono font-bold text-emerald-700">+0.06 SG</div>
            </div>
          </div>
        </div>
      </div>

      {/* Continuous Depth Trend Strip-Chart */}
      <div className="px-3 pb-2.5 flex-1 flex flex-col justify-end">
        <div className="text-[9.5px] font-bold text-gray-500 uppercase mb-1 flex items-center justify-between">
          <span>Continuous Depth Trend (Last 10 Meters)</span>
          <div className="flex items-center gap-3 text-[9.5px] font-mono">
            <span className="text-[#E58A13] flex items-center gap-1">
              <span className="w-2.5 h-0.5 bg-[#E58A13]"></span> Teale MSE
            </span>
            <span className="text-[#184E3A] flex items-center gap-1">
              <span className="w-2.5 h-0.5 bg-[#184E3A]"></span> ROP
            </span>
          </div>
        </div>
        <div className="h-16 bg-slate-50 rounded border border-slate-200 p-1 relative overflow-hidden flex items-end">
          <svg className="w-full h-full" viewBox="0 0 400 50">
            {/* Guide lines */}
            <line x1="0" y1="15" x2="400" y2="15" stroke="#E2E8F0" strokeWidth="0.8" strokeDasharray="3 3" />
            <line x1="0" y1="35" x2="400" y2="35" stroke="#E2E8F0" strokeWidth="0.8" strokeDasharray="3 3" />

            {/* ROP Curve (Green) */}
            <polyline
              fill="none"
              stroke="#184E3A"
              strokeWidth="2"
              points="0,30 40,28 80,26 120,32 160,29 200,28 240,36 280,41 320,43 360,45 400,46"
            />

            {/* MSE Curve (Orange - Spikes during hazard) */}
            <polyline
              fill="none"
              stroke="#E58A13"
              strokeWidth="2.2"
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
  );
};
