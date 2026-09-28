"use client";

import React from "react";
import {
  ShieldAlert,
  AlertTriangle,
  RotateCw,
  Droplets,
  FileDown,
  CheckCircle,
  X,
  Gauge,
  TrendingDown,
  Activity,
  Flame,
} from "lucide-react";
import { TelemetryData } from "./TelemetryTrack";

interface DoghouseViewProps {
  telemetry: TelemetryData;
  riskIndex: number;
  isAlertActive: boolean;
  distanceAheadM: number;
  onExitDoghouse: () => void;
  onExportPdf: () => void;
  onTriggerAlert: () => void;
  onResetSim: () => void;
}

export const DoghouseView: React.FC<DoghouseViewProps> = ({
  telemetry,
  riskIndex,
  isAlertActive,
  distanceAheadM,
  onExitDoghouse,
  onExportPdf,
  onTriggerAlert,
  onResetSim,
}) => {
  return (
    <div className="min-h-screen bg-[#12161A] text-white p-4 md:p-6 flex flex-col justify-between select-none">
      {/* Doghouse Header */}
      <div className="flex items-center justify-between border-b-2 border-slate-700 pb-3">
        <div className="flex items-center gap-3">
          <div className="bg-[#E58A13] text-black font-black text-xl px-3 py-1 rounded">
            OIL
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-black tracking-wider text-white">
              RIG DOGHOUSE CONSOLE · SYN-NHK-05
            </h1>
            <p className="text-xs text-amber-400 font-mono">
              [Synthetic — Assam Basin Profile · SPE-197489-MS Calibrated]
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-[#1E242B] border border-slate-600 px-3 py-1.5 rounded text-right">
            <div className="text-[10px] text-gray-400 uppercase font-bold">WITSML Telemetry</div>
            <div className="text-xs font-mono font-bold text-emerald-400">1 Hz ACTIVE</div>
          </div>

          <button
            onClick={onExitDoghouse}
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white font-bold px-4 py-2 rounded-lg border border-slate-600 text-sm"
          >
            <X className="w-5 h-5 text-red-400" />
            <span>Standard View</span>
          </button>
        </div>
      </div>

      {/* Main High-Visibility Warning Banner */}
      <div
        className={`my-4 p-5 rounded-xl border-4 transition-all duration-300 ${
          isAlertActive
            ? "bg-red-950/90 border-red-500 shadow-[0_0_50px_rgba(217,56,30,0.5)] animate-pulse"
            : "bg-[#184E3A]/40 border-[#184E3A]"
        }`}
      >
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            {isAlertActive ? (
              <ShieldAlert className="w-16 h-16 text-red-500 flex-shrink-0 animate-bounce" />
            ) : (
              <AlertTriangle className="w-14 h-14 text-amber-400 flex-shrink-0" />
            )}
            <div>
              <div className="text-xs uppercase font-bold tracking-widest text-amber-300">
                {isAlertActive ? "CRITICAL GEOMECHANICAL HAZARD" : "DRILLING ADVISORY WATCH"}
              </div>
              <h2 className="text-2xl md:text-3xl font-black text-white mt-1">
                {isAlertActive
                  ? "DIFFERENTIAL STICKING IMMINENT IN UPPER TIPAM"
                  : "APPROACHING DEPLETED SAND PACKAGE (UPPER TIPAM)"}
              </h2>
              <p className="text-sm text-gray-300 mt-1 max-w-3xl">
                Depleted sand pore pressure: <strong>0.88 SG</strong> · Current overbalance:{" "}
                <strong className="text-amber-400">1,120 psi</strong> · Offset well{" "}
                <strong className="text-white">SYN-NHK-01</strong> suffered 38.5 hrs stuck pipe
                NPT at this horizon.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 bg-black/50 p-4 rounded-xl border border-slate-700">
            <div className="text-center">
              <div className="text-xs text-gray-400 font-bold uppercase">Distance Ahead</div>
              <div className="text-3xl font-black font-mono text-amber-400">
                {distanceAheadM.toFixed(1)}m
              </div>
            </div>
            <div className="w-px h-12 bg-slate-700"></div>
            <div className="text-center">
              <div className="text-xs text-gray-400 font-bold uppercase">Risk Index (R_H)</div>
              <div
                className={`text-3xl font-black font-mono ${
                  isAlertActive ? "text-red-500" : "text-amber-400"
                }`}
              >
                {riskIndex.toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Large 6-Card Telemetry Grid for Gloved Hands */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-4">
        {/* Bit Depth */}
        <div className="bg-[#1E242B] border-2 border-slate-700 rounded-xl p-4 text-center">
          <div className="text-xs text-gray-400 font-bold uppercase flex items-center justify-center gap-1">
            <TrendingDown className="w-4 h-4 text-emerald-400" />
            <span>Bit Depth (MD)</span>
          </div>
          <div className="text-3xl font-black font-mono text-white mt-1">
            {telemetry.measured_depth_m.toFixed(1)}
            <span className="text-sm font-normal text-gray-400 ml-1">m</span>
          </div>
          <div className="text-xs text-gray-400 font-mono mt-1">
            TVD: {telemetry.tvdss_m.toFixed(1)}m
          </div>
        </div>

        {/* ROP */}
        <div className="bg-[#1E242B] border-2 border-slate-700 rounded-xl p-4 text-center">
          <div className="text-xs text-gray-400 font-bold uppercase flex items-center justify-center gap-1">
            <Activity className="w-4 h-4 text-[#E58A13]" />
            <span>ROP</span>
          </div>
          <div className="text-3xl font-black font-mono text-amber-300 mt-1">
            {telemetry.rop_mhr.toFixed(1)}
            <span className="text-sm font-normal text-gray-400 ml-1">m/h</span>
          </div>
          <div className="text-xs text-gray-400 font-mono mt-1">Target: 18.0</div>
        </div>

        {/* WOB */}
        <div className="bg-[#1E242B] border-2 border-slate-700 rounded-xl p-4 text-center">
          <div className="text-xs text-gray-400 font-bold uppercase flex items-center justify-center gap-1">
            <Gauge className="w-4 h-4 text-blue-400" />
            <span>WOB</span>
          </div>
          <div className="text-3xl font-black font-mono text-blue-300 mt-1">
            {telemetry.wob_klbs.toFixed(1)}
            <span className="text-sm font-normal text-gray-400 ml-1">klb</span>
          </div>
          <div className="text-xs text-gray-400 font-mono mt-1">Max: 25.0 klb</div>
        </div>

        {/* Torque */}
        <div className="bg-[#1E242B] border-2 border-slate-700 rounded-xl p-4 text-center">
          <div className="text-xs text-gray-400 font-bold uppercase flex items-center justify-center gap-1">
            <RotateCw className="w-4 h-4 text-amber-500" />
            <span>Torque</span>
          </div>
          <div className="text-3xl font-black font-mono text-amber-400 mt-1">
            {telemetry.surface_torque_kftlb.toFixed(1)}
            <span className="text-sm font-normal text-gray-400 ml-1">kft-lb</span>
          </div>
          <div className="text-xs text-gray-400 font-mono mt-1">
            RPM: {telemetry.rpm.toFixed(0)}
          </div>
        </div>

        {/* Teale MSE */}
        <div className="bg-[#1E242B] border-2 border-slate-700 rounded-xl p-4 text-center">
          <div className="text-xs text-gray-400 font-bold uppercase flex items-center justify-center gap-1">
            <Flame className="w-4 h-4 text-red-400" />
            <span>Teale MSE</span>
          </div>
          <div className="text-3xl font-black font-mono text-red-400 mt-1">
            {(telemetry.teale_mse_psi / 1000).toFixed(1)}k
            <span className="text-sm font-normal text-gray-400 ml-1">psi</span>
          </div>
          <div className="text-xs text-amber-300 font-mono mt-1">
            {telemetry.mse_baseline_ratio.toFixed(2)}x Base
          </div>
        </div>

        {/* Mud Weight & ECD */}
        <div className="bg-[#1E242B] border-2 border-slate-700 rounded-xl p-4 text-center">
          <div className="text-xs text-gray-400 font-bold uppercase flex items-center justify-center gap-1">
            <Droplets className="w-4 h-4 text-cyan-400" />
            <span>Mud / ECD</span>
          </div>
          <div className="text-3xl font-black font-mono text-cyan-300 mt-1">
            {telemetry.ecd_downhole_sg.toFixed(2)}
            <span className="text-sm font-normal text-gray-400 ml-1">SG</span>
          </div>
          <div className="text-xs text-gray-400 font-mono mt-1">
            MW: {telemetry.mud_density_in_sg} SG
          </div>
        </div>
      </div>

      {/* Big Action Buttons (Minimum 48px touch targets) */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <button
          onClick={onExportPdf}
          className="h-14 bg-[#E58A13] hover:bg-amber-600 text-black font-black text-sm uppercase rounded-xl flex items-center justify-center gap-2 shadow-lg cursor-pointer"
        >
          <FileDown className="w-5 h-5 text-black" />
          <span>Print / Export Tour Advisory</span>
        </button>

        <button
          onClick={onTriggerAlert}
          className="h-14 bg-red-700 hover:bg-red-600 text-white font-black text-sm uppercase rounded-xl flex items-center justify-center gap-2 shadow-lg cursor-pointer"
        >
          <ShieldAlert className="w-5 h-5 text-white" />
          <span>Simulate Hazard (2,414m)</span>
        </button>

        <button
          onClick={onResetSim}
          className="h-14 bg-slate-800 hover:bg-slate-700 text-white font-bold text-sm uppercase rounded-xl flex items-center justify-center gap-2 border border-slate-600 cursor-pointer"
        >
          <span>Reset Depth (2,410m)</span>
        </button>

        <button
          onClick={() => alert("Driller SOP Acknowledged: Stationary drillstring time locked to <90s.")}
          className="h-14 bg-emerald-800 hover:bg-emerald-700 text-white font-black text-sm uppercase rounded-xl flex items-center justify-center gap-2 shadow-lg cursor-pointer"
        >
          <CheckCircle className="w-5 h-5 text-emerald-300" />
          <span>Acknowledge SOP (Driller Sign)</span>
        </button>
      </div>
    </div>
  );
};
