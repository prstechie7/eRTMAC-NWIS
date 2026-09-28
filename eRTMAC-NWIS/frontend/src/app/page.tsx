"use client";

import React, { useState, useEffect, useRef } from "react";
import { Header } from "@/components/Header";
import { BasinMap, WellPoint } from "@/components/BasinMap";
import { CurtainSection } from "@/components/CurtainSection";
import { LookAheadCard } from "@/components/LookAheadCard";
import { TelemetryTrack, TelemetryData } from "@/components/TelemetryTrack";
import { DoghouseView } from "@/components/DoghouseView";

// Fallback Calibrated Synthetic Wells (SPE-197489-MS Nahorkatiya, Moran, Baghjan)
const DEFAULT_WELLS: WellPoint[] = [
  {
    well_id: "c1f7a012-3b4c-4e89-9a11-000000000005",
    well_name: "SYN-NHK-05",
    field_name: "Nahorkatiya",
    surface_lat: 27.2885,
    surface_lon: 95.3345,
    kb_elevation_m: 122.5,
    total_depth_m: 3150.0,
    status: "DRILLING",
  },
  {
    well_id: "c1f7a012-3b4c-4e89-9a11-000000000001",
    well_name: "SYN-NHK-01",
    field_name: "Nahorkatiya",
    surface_lat: 27.2798,
    surface_lon: 95.3211,
    kb_elevation_m: 121.2,
    total_depth_m: 3250.0,
    status: "COMPLETED",
  },
  {
    well_id: "c1f7a012-3b4c-4e89-9a11-000000000002",
    well_name: "SYN-NHK-02",
    field_name: "Nahorkatiya",
    surface_lat: 27.2954,
    surface_lon: 95.3488,
    kb_elevation_m: 124.0,
    total_depth_m: 3180.0,
    status: "COMPLETED",
  },
  {
    well_id: "c1f7a012-3b4c-4e89-9a11-000000000003",
    well_name: "SYN-NHK-03",
    field_name: "Nahorkatiya",
    surface_lat: 27.2655,
    surface_lon: 95.3122,
    kb_elevation_m: 119.8,
    total_depth_m: 3420.0,
    status: "COMPLETED",
  },
  {
    well_id: "c1f7a012-3b4c-4e89-9a11-000000000004",
    well_name: "SYN-NHK-04",
    field_name: "Nahorkatiya",
    surface_lat: 27.3112,
    surface_lon: 95.3621,
    kb_elevation_m: 126.1,
    total_depth_m: 2950.0,
    status: "COMPLETED",
  },
  {
    well_id: "c1f7a012-3b4c-4e89-9a11-000000000006",
    well_name: "SYN-MORAN-01",
    field_name: "Moran",
    surface_lat: 27.1855,
    surface_lon: 94.9312,
    kb_elevation_m: 115.4,
    total_depth_m: 3850.0,
    status: "COMPLETED",
  },
  {
    well_id: "c1f7a012-3b4c-4e89-9a11-000000000007",
    well_name: "SYN-MORAN-02",
    field_name: "Moran",
    surface_lat: 27.1992,
    surface_lon: 94.9455,
    kb_elevation_m: 117.0,
    total_depth_m: 3920.0,
    status: "COMPLETED",
  },
  {
    well_id: "c1f7a012-3b4c-4e89-9a11-000000000008",
    well_name: "SYN-BGJ-01",
    field_name: "Baghjan",
    surface_lat: 27.5812,
    surface_lon: 95.3522,
    kb_elevation_m: 128.5,
    total_depth_m: 4100.0,
    status: "COMPLETED",
  },
  {
    well_id: "c1f7a012-3b4c-4e89-9a11-000000000009",
    well_name: "SYN-BGJ-02",
    field_name: "Baghjan",
    surface_lat: 27.5925,
    surface_lon: 95.3688,
    kb_elevation_m: 130.2,
    total_depth_m: 4250.0,
    status: "COMPLETED",
  },
  {
    well_id: "c1f7a012-3b4c-4e89-9a11-000000000010",
    well_name: "SYN-BGJ-03",
    field_name: "Baghjan",
    surface_lat: 27.5701,
    surface_lon: 95.3395,
    kb_elevation_m: 127.0,
    total_depth_m: 3980.0,
    status: "COMPLETED",
  },
];

export default function Home() {
  const [wells, setWells] = useState<WellPoint[]>(DEFAULT_WELLS);
  const [activeWellName, setActiveWellName] = useState<string>("SYN-NHK-05");
  const [radiusKm, setRadiusKm] = useState<number>(5.0);
  const [isDoghouseMode, setIsDoghouseMode] = useState<boolean>(false);
  const [wsConnected, setWsConnected] = useState<boolean>(false);
  const [isExporting, setIsExporting] = useState<boolean>(false);

  // Active drilling bit depth and state
  const [depthMd, setDepthMd] = useState<number>(2410.0);
  const [history, setHistory] = useState<
    Array<{ depth: number; mse: number; rop: number; torque: number }>
  >([]);

  const activeWell = wells.find((w) => w.well_name === activeWellName) || wells[0];
  const hazardDepthMd = 2448.5;
  const isAlertActive = depthMd >= 2413.0;
  const distanceAheadM = Math.max(0, hazardDepthMd - depthMd);
  const riskIndex = isAlertActive
    ? Math.min(94.8, 84.2 + (depthMd - 2413.0) * 3.5)
    : 42.0;

  const tvdss = 2180.5 + (depthMd - 2410.0) * 0.99;

  // Real-time telemetry state
  const [telemetry, setTelemetry] = useState<TelemetryData>({
    measured_depth_m: 2410.0,
    tvdss_m: 2180.5,
    rop_mhr: 18.5,
    wob_klbs: 18.2,
    surface_torque_kftlb: 12.8,
    rpm: 95.0,
    standpipe_pressure_psi: 2950.0,
    flow_rate_gpm: 640.0,
    mud_density_in_sg: 1.16,
    mud_density_out_sg: 1.16,
    ecd_downhole_sg: 1.21,
    gas_total_pct: 1.85,
    pit_volume_gain_bbls: 0.2,
    teale_mse_psi: 36420,
    mse_baseline_ratio: 1.05,
    is_alert: false,
  });

  // Fetch Wells from backend API on mount
  useEffect(() => {
    fetch("http://localhost:8000/api/v1/wells")
      .then((res) => {
        if (!res.ok) throw new Error("API not ok");
        return res.json();
      })
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setWells(data);
        }
      })
      .catch(() => {
        // Fallback already preloaded
      });
  }, []);

  // WebSocket Live Connection with Local Timer Fallback
  useEffect(() => {
    let ws: WebSocket | null = null;
    let localInterval: NodeJS.Timeout | null = null;

    try {
      ws = new WebSocket("ws://localhost:8000/ws/v1/telemetry");

      ws.onopen = () => {
        setWsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data && data.telemetry) {
            const curDepth = data.telemetry.measured_depth_m;
            setDepthMd(curDepth);
            const alertActive = data.lookahead_status?.active_alert || curDepth >= 2413.0;

            const tData: TelemetryData = {
              measured_depth_m: curDepth,
              tvdss_m: data.telemetry.tvdss_m,
              rop_mhr: data.telemetry.rop_mhr,
              wob_klbs: data.telemetry.wob_klbs,
              surface_torque_kftlb: data.telemetry.surface_torque_kftlb,
              rpm: data.telemetry.rpm,
              standpipe_pressure_psi: data.telemetry.standpipe_pressure_psi,
              flow_rate_gpm: data.telemetry.flow_rate_gpm,
              mud_density_in_sg: data.telemetry.mud_density_in_sg,
              mud_density_out_sg: data.telemetry.mud_density_out_sg,
              ecd_downhole_sg: data.telemetry.ecd_downhole_sg,
              gas_total_pct: data.telemetry.gas_total_pct,
              pit_volume_gain_bbls: data.telemetry.pit_volume_gain_bbls,
              teale_mse_psi: data.instantaneous_physics?.teale_mse_psi || 36420,
              mse_baseline_ratio: alertActive ? 1.45 : 1.05,
              is_alert: alertActive,
            };
            setTelemetry(tData);

            setHistory((prev) => [
              ...prev.slice(-15),
              {
                depth: curDepth,
                mse: tData.teale_mse_psi,
                rop: tData.rop_mhr,
                torque: tData.surface_torque_kftlb,
              },
            ]);
          }
        } catch (e) {
          console.error("WS Parse error", e);
        }
      };

      ws.onerror = () => {
        setWsConnected(false);
      };

      ws.onclose = () => {
        setWsConnected(false);
      };
    } catch (e) {
      setWsConnected(false);
    }

    // Always maintain steady simulation advance if WS is idle or offline
    localInterval = setInterval(() => {
      setDepthMd((prev) => {
        const nextDepth = Number((prev + 0.1).toFixed(2));
        const alert = nextDepth >= 2413.0;
        const mse = alert ? 52800 : 36420;

        setTelemetry((cur) => ({
          ...cur,
          measured_depth_m: nextDepth,
          tvdss_m: Number((2180.5 + (nextDepth - 2410.0) * 0.99).toFixed(1)),
          teale_mse_psi: mse,
          mse_baseline_ratio: alert ? 1.45 : 1.05,
          is_alert: alert,
          rop_mhr: alert ? 12.2 : 18.5,
          surface_torque_kftlb: alert ? 15.4 : 12.8,
        }));

        return nextDepth;
      });
    }, 1000);

    return () => {
      if (ws) ws.close();
      if (localInterval) clearInterval(localInterval);
    };
  }, []);

  // PDF Export Trigger
  const handleExportPdf = async () => {
    setIsExporting(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/reports/tour-advisory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          active_well_name: activeWellName,
          depth_md_m: depthMd,
          tvdss_m: tvdss,
          projected_hazard: "DIFFERENTIAL_STICKING",
          risk_index: riskIndex,
          evidence_well: "SYN-NHK-01",
          historical_npt_hours: 38.5,
        }),
      });

      if (!response.ok) {
        throw new Error("PDF export failed");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `OIL_TourAdvisory_${activeWellName}_${depthMd.toFixed(0)}m.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert("Generated Tour Advisory PDF locally. Ensure backend is running at http://localhost:8000.");
    } finally {
      setIsExporting(false);
    }
  };

  // Simulation Controls
  const handleTriggerAlert = () => {
    setDepthMd(2414.0);
  };

  const handleAdvanceDepth = () => {
    setDepthMd((d) => Number((d + 1.0).toFixed(1)));
  };

  const handleResetSim = () => {
    setDepthMd(2410.0);
  };

  if (isDoghouseMode) {
    return (
      <DoghouseView
        telemetry={telemetry}
        riskIndex={riskIndex}
        isAlertActive={isAlertActive}
        distanceAheadM={distanceAheadM}
        onExitDoghouse={() => setIsDoghouseMode(false)}
        onExportPdf={handleExportPdf}
        onTriggerAlert={handleTriggerAlert}
        onResetSim={handleResetSim}
      />
    );
  }

  return (
    <div className="min-h-screen bg-[#F8F9FA] flex flex-col">
      {/* Top Navigation & Compliance Bar */}
      <Header
        isDoghouseMode={isDoghouseMode}
        setIsDoghouseMode={setIsDoghouseMode}
        wsConnected={wsConnected}
        activeWellName={activeWellName}
        onSelectWell={setActiveWellName}
        wellsList={wells}
        onTriggerAlert={handleTriggerAlert}
        onResetSim={handleResetSim}
        onExportPdf={handleExportPdf}
      />

      {/* Main 4-Panel Enterprise Drilling Intelligence Grid */}
      <main className="flex-1 max-w-[1600px] w-full mx-auto p-3 md:p-3.5 space-y-3">
        {/* Top Row: Panel 1 (Map) + Panel 2 (Curtain Cross-Section) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
          {/* Panel 1: 2D Basin Navigator & Spatial Radius Filter */}
          <div className="h-full">
            <BasinMap
              wells={wells}
              activeWell={activeWell}
              radiusKm={radiusKm}
              setRadiusKm={setRadiusKm}
              onSelectWell={(w) => setActiveWellName(w.well_name)}
            />
          </div>

          {/* Panel 2: 2D Geological Curtain Cross-Section */}
          <div className="h-full">
            <CurtainSection
              currentDepthMd={depthMd}
              currentTvdss={tvdss}
              hazardDepthMd={hazardDepthMd}
              isAlertActive={isAlertActive}
            />
          </div>
        </div>

        {/* Bottom Row: Panel 3 (Look-Ahead Alert Card) + Panel 4 (Telemetry & Physics Track) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
          {/* Panel 3: Real-Time Look-Ahead Advisory & Mitigations */}
          <div className="h-full">
            <LookAheadCard
              currentDepthMd={depthMd}
              currentTvdss={tvdss}
              riskIndex={riskIndex}
              isAlertActive={isAlertActive}
              distanceAheadM={distanceAheadM}
              onExportPdf={handleExportPdf}
              onTriggerAlert={handleTriggerAlert}
              onAdvanceDepth={handleAdvanceDepth}
              onResetSim={handleResetSim}
              isExporting={isExporting}
            />
          </div>

          {/* Panel 4: Live 1 Hz Telemetry & Teale MSE Physics */}
          <div className="h-full">
            <TelemetryTrack telemetry={telemetry} history={history} />
          </div>
        </div>
      </main>

      {/* Industrial Footer */}
      <footer className="bg-[#1E242B] text-gray-400 border-t border-slate-800 text-xs py-2 px-4">
        <div className="max-w-[1600px] mx-auto flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white">Oil India Limited · eRTMAC</span>
            <span>|</span>
            <span>SIH26121 Nearby Wells Intelligence System</span>
          </div>
          <div className="font-mono text-[10.5px] text-gray-400">
            Formulation: MCM 3D · Dip-Rotated TSD · Teale MSE · Outmans Differential Sticking Model
          </div>
        </div>
      </footer>
    </div>
  );
}
