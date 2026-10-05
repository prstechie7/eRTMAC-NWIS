import React, { useState } from "react";
import { Compass, MapPin, Sliders, ShieldCheck, ChevronRight, Layers, Eye } from "lucide-react";

interface WellPin {
  id: string;
  name: string;
  basin: string;
  field: string;
  lat: number;
  lng: number;
  distanceKm: number;
  depth: number;
  riskStatus: "critical" | "warning" | "safe";
  formation: string;
}

interface IndianBasinsMapCardProps {
  onSelectWell?: (well: WellPin) => void;
}

export const IndianBasinsMapCard: React.FC<IndianBasinsMapCardProps> = ({
  onSelectWell,
}) => {
  const [selectedRangeKm, setSelectedRangeKm] = useState<number>(25);
  const [selectedBasin, setSelectedBasin] = useState<string>("Assam-Arakan");

  // Key provided by user
  const maptilerKey = "o8Qhn3wgKrPhpfkNBiVU";

  const wells: WellPin[] = [
    {
      id: "NHK-062",
      name: "NHK-062 (Current Rig)",
      basin: "Assam-Arakan",
      field: "Duliajan Block",
      lat: 27.352,
      lng: 95.319,
      distanceKm: 0.0,
      depth: 2413.5,
      riskStatus: "critical",
      formation: "Barail Coal-Shale",
    },
    {
      id: "NHK-014",
      name: "NHK-014 (Historical Stuck)",
      basin: "Assam-Arakan",
      field: "Duliajan Block",
      lat: 27.361,
      lng: 95.328,
      distanceKm: 1.4,
      depth: 2850.0,
      riskStatus: "critical",
      formation: "Barail Coal-Shale",
    },
    {
      id: "NHK-019",
      name: "NHK-019 (Lost Circulation)",
      basin: "Assam-Arakan",
      field: "Nahorkatiya Block",
      lat: 27.291,
      lng: 95.278,
      distanceKm: 7.8,
      depth: 2920.0,
      riskStatus: "warning",
      formation: "Upper Tipam Sandstone",
    },
    {
      id: "NHK-021",
      name: "NHK-021 (Swelling Shale)",
      basin: "Assam-Arakan",
      field: "Moran Field",
      lat: 27.189,
      lng: 95.042,
      distanceKm: 21.2,
      depth: 2450.0,
      riskStatus: "safe",
      formation: "Girujan Clay",
    },
    {
      id: "JRH-005",
      name: "JRH-005 (Exploration)",
      basin: "Assam-Arakan",
      field: "Jorhat Basin",
      lat: 26.751,
      lng: 94.215,
      distanceKm: 42.0,
      depth: 3200.0,
      riskStatus: "safe",
      formation: "Kopili Formation",
    },
    {
      id: "KGD6-A1",
      name: "KG-D6 Deepwater A1",
      basin: "Krishna-Godavari",
      field: "Offshore Andhra",
      lat: 16.512,
      lng: 82.289,
      distanceKm: 1420.0,
      depth: 3800.0,
      riskStatus: "warning",
      formation: "Pleistocene Channel Sand",
    },
  ];

  const filteredWells = wells.filter(
    (w) => w.basin === selectedBasin && w.distanceKm <= selectedRangeKm
  );

  return (
    <div className="luxury-card rounded-3xl p-6 bg-white border border-slate-200/90 flex flex-col justify-between">
      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-slate-900 tracking-tight">
              Indian Basin & Offset Well Proximity Scanner
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold">
              MAPTILER SATELLITE
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-medium mt-0.5">
            Real-time geospatial distance matrix to historical DGH NDR well trajectories
          </p>
        </div>

        {/* Basin Selector Pills */}
        <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-2xl">
          {["Assam-Arakan", "Krishna-Godavari", "Cambay"].map((b) => (
            <button
              key={b}
              onClick={() => setSelectedBasin(b)}
              className={`px-3 py-1 text-xs font-semibold rounded-xl transition-all ${
                selectedBasin === b
                  ? "bg-white text-slate-900 shadow-xs font-bold"
                  : "text-slate-500 hover:text-slate-900"
              }`}
            >
              {b}
            </button>
          ))}
        </div>
      </div>

      {/* ── Interactive Range Proximity Slider ── */}
      <div className="bg-slate-50 p-3.5 rounded-2xl border border-slate-200/80 mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <Sliders className="w-4 h-4 text-emerald-600" />
          <span className="text-xs font-bold text-slate-800">
            Offset Proximity Radius: <span className="font-mono text-emerald-700">{selectedRangeKm} km</span>
          </span>
        </div>

        <div className="flex items-center gap-3 flex-1 max-w-xs">
          <span className="text-[10px] font-mono text-slate-400">5km</span>
          <input
            type="range"
            min="5"
            max="50"
            step="1"
            value={selectedRangeKm}
            onChange={(e) => setSelectedRangeKm(Number(e.target.value))}
            className="w-full accent-emerald-600 h-1.5 bg-slate-200 rounded-lg cursor-pointer"
          />
          <span className="text-[10px] font-mono text-slate-400">50km</span>
        </div>

        <span className="text-xs font-mono font-bold text-slate-700">
          {filteredWells.length} Wells in Range
        </span>
      </div>

      {/* ── Interactive Map Viewport with MapTiler Tiles ── */}
      <div className="relative rounded-2xl overflow-hidden h-72 border border-slate-200/90 shadow-inner group">
        {/* MapTiler Satellite / Street Hybrid Tile Background */}
        <iframe
          title="MapTiler Basin Map"
          className="w-full h-full border-0 pointer-events-auto"
          src={`https://api.maptiler.com/maps/streets-v2/?key=${maptilerKey}#12.5/27.352/95.319`}
        />

        {/* Floating Proximity Overlay Badge */}
        <div className="absolute top-3 left-3 bg-white/95 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-200 shadow-md text-xs font-semibold text-slate-800 flex items-center gap-2">
          <MapPin className="w-3.5 h-3.5 text-rose-500 animate-bounce" />
          <span>Active Rig: Duliajan Block (Assam)</span>
        </div>

        {/* Floating Mini Range Radius Indicator */}
        <div className="absolute bottom-3 right-3 bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-xl text-white text-[11px] font-mono flex items-center gap-2 shadow-lg">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Radius: {selectedRangeKm} km | {filteredWells.length} Offsets Calibrated</span>
        </div>
      </div>

      {/* ── Offset Well Cards in Radius ── */}
      <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3">
        {filteredWells.slice(0, 3).map((w) => (
          <div
            key={w.id}
            onClick={() => onSelectWell?.(w)}
            className="p-3 bg-slate-50 hover:bg-slate-100/80 rounded-2xl border border-slate-200/80 cursor-pointer transition-all hover:scale-[1.01]"
          >
            <div className="flex items-center justify-between">
              <span className="font-mono font-bold text-xs text-slate-900">{w.id}</span>
              <span
                className={`text-[9px] font-mono font-bold px-1.5 py-0.2 rounded ${
                  w.riskStatus === "critical"
                    ? "bg-rose-100 text-rose-700"
                    : w.riskStatus === "warning"
                    ? "bg-amber-100 text-amber-700"
                    : "bg-emerald-100 text-emerald-700"
                }`}
              >
                {w.distanceKm.toFixed(1)} km
              </span>
            </div>
            <div className="text-[11px] text-slate-500 font-medium mt-1 truncate">
              {w.field}
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-0.5">
              {w.formation} · {w.depth.toFixed(0)}m
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
