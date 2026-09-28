"use client";

import React, { useState } from "react";
import { Compass, Filter, MapPin, AlertTriangle, Layers, Info, Eye } from "lucide-react";

export interface WellPoint {
  well_id?: string;
  well_name: string;
  field_name: string;
  surface_lat: number;
  surface_lon: number;
  kb_elevation_m?: number;
  total_depth_md_m?: number;
  total_depth_m?: number;
  status: string;
  historical_hazards?: any[];
}

interface BasinMapProps {
  wells: WellPoint[];
  activeWell: WellPoint | null;
  radiusKm: number;
  setRadiusKm: (r: number) => void;
  onSelectWell: (w: WellPoint) => void;
}

export const BasinMap: React.FC<BasinMapProps> = ({
  wells,
  activeWell,
  radiusKm,
  setRadiusKm,
  onSelectWell,
}) => {
  const [hoveredWell, setHoveredWell] = useState<WellPoint | null>(null);

  // Geographic Bounding Box covering Moran (SW), Nahorkatiya (Center), Baghjan (NE)
  const minLat = 27.12;
  const maxLat = 27.65;
  const minLon = 94.80;
  const maxLon = 95.65;

  const mapWidth = 560;
  const mapHeight = 320;

  // Project coordinates to SVG canvas
  const project = (lat: number, lon: number) => {
    const x = ((lon - minLon) / (maxLon - minLon)) * (mapWidth - 80) + 40;
    const y = ((maxLat - lat) / (maxLat - minLat)) * (mapHeight - 60) + 30;
    return { x, y };
  };

  // Convert km radius to SVG pixels at 27.3°N latitude
  // 1 deg lon ~ 99.2 km at this latitude; totalLonKm ~ (maxLon - minLon) * 99.2
  const kmToPixels = (km: number) => {
    const totalKmX = (maxLon - minLon) * 99.2; // ~84.3 km
    return (km / totalKmX) * (mapWidth - 80);
  };

  const activePos = activeWell
    ? project(activeWell.surface_lat, activeWell.surface_lon)
    : { x: 380, y: 200 };
  const radiusPx = kmToPixels(radiusKm);

  // Haversine distance in km
  const getDistanceKm = (w: WellPoint) => {
    if (!activeWell) return 0;
    const R = 6371;
    const dLat = ((w.surface_lat - activeWell.surface_lat) * Math.PI) / 180;
    const dLon = ((w.surface_lon - activeWell.surface_lon) * Math.PI) / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((activeWell.surface_lat * Math.PI) / 180) *
        Math.cos((w.surface_lat * Math.PI) / 180) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  // Smart label offsets to prevent collision for Nahorkatiya cluster
  const getLabelOffset = (name: string) => {
    switch (name) {
      case "SYN-NHK-05":
        return { dx: 10, dy: -8, anchor: "start" as const };
      case "SYN-NHK-01":
        return { dx: 10, dy: 14, anchor: "start" as const };
      case "SYN-NHK-02":
        return { dx: 10, dy: -2, anchor: "start" as const };
      case "SYN-NHK-03":
        return { dx: -10, dy: 14, anchor: "end" as const };
      case "SYN-NHK-04":
        return { dx: 10, dy: 12, anchor: "start" as const };
      case "SYN-NHK-06":
        return { dx: -10, dy: -8, anchor: "end" as const };
      case "SYN-NHK-07":
        return { dx: 10, dy: 14, anchor: "start" as const };
      default:
        return { dx: 8, dy: 4, anchor: "start" as const };
    }
  };

  return (
    <div className="bg-white rounded-lg border border-[#E2E8F0] shadow-sm overflow-hidden flex flex-col h-full">
      {/* Top Header */}
      <div className="bg-[#F8F9FA] px-3.5 py-2 border-b border-[#E2E8F0] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#184E3A]"></div>
          <span className="font-bold text-xs uppercase tracking-wider text-[#184E3A]">
            Panel 1 · 2D Basin Navigator & Spatial Radius
          </span>
        </div>
        <div className="flex items-center gap-2 text-[11px] text-gray-500">
          <span className="font-medium">Upper Assam Structural Corridor</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
        </div>
      </div>

      {/* Control Bar: Radius Slider */}
      <div className="px-3.5 py-1.5 bg-slate-50 border-b border-[#E2E8F0] flex items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-[#E58A13]" />
          <span className="font-semibold text-gray-700 text-[11.5px]">Offset Search Radius:</span>
          <span className="font-mono font-bold text-[#184E3A] bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 text-xs">
            {radiusKm.toFixed(1)} km
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-gray-400">1 km</span>
          <input
            type="range"
            min="1.0"
            max="15.0"
            step="0.5"
            value={radiusKm}
            onChange={(e) => setRadiusKm(parseFloat(e.target.value))}
            className="w-32 h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#184E3A]"
          />
          <span className="text-[10px] text-gray-400">15 km</span>
        </div>
      </div>

      {/* Map SVG Canvas */}
      <div className="relative p-2 bg-[#F8FAFC] flex-1 flex items-center justify-center min-h-[250px]">
        <svg
          viewBox={`0 0 ${mapWidth} ${mapHeight}`}
          className="w-full h-auto max-h-[300px] bg-white rounded border border-slate-200 shadow-inner"
        >
          <defs>
            <pattern id="grid" width="35" height="35" patternUnits="userSpaceOnUse">
              <path d="M 35 0 L 0 0 0 35" fill="none" stroke="#F1F5F9" strokeWidth="0.8" />
            </pattern>
            {/* Radius Gradient */}
            <radialGradient id="radiusGradient" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#E58A13" stopOpacity="0.22" />
              <stop offset="70%" stopColor="#E58A13" stopOpacity="0.10" />
              <stop offset="100%" stopColor="#E58A13" stopOpacity="0.35" />
            </radialGradient>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />

          {/* Regional Geographic Fault & River Guidelines */}
          <path
            d="M 30 190 Q 220 150 530 80"
            fill="none"
            stroke="#CBD5E1"
            strokeWidth="1.8"
            strokeDasharray="4 4"
          />
          <text x="180" y="140" fill="#94A3B8" fontSize="8" fontStyle="italic">
            Brahmaputra Regional Alluvial Fault Line
          </text>

          {/* Field Area Boundaries (Subtle polygons) */}
          {/* Moran Field */}
          <g>
            <rect x="35" y="195" width="105" height="75" rx="6" fill="#F1F5F9" stroke="#E2E8F0" strokeWidth="1" opacity="0.7" />
            <text x="42" y="210" fill="#64748B" fontSize="9" fontWeight="bold" letterSpacing="0.5">
              MORAN FIELD
            </text>
            <text x="42" y="222" fill="#94A3B8" fontSize="7.5">
              Dip: 4.2° SSE
            </text>
          </g>

          {/* Nahorkatiya Field (Active Central Hub) */}
          <g>
            <rect x="320" y="170" width="165" height="120" rx="6" fill="#ECFDF5" stroke="#A7F3D0" strokeWidth="1.2" opacity="0.75" />
            <text x="328" y="185" fill="#184E3A" fontSize="9" fontWeight="bold" letterSpacing="0.5">
              NAHORKATIYA FIELD (ACTIVE)
            </text>
            <text x="328" y="196" fill="#047857" fontSize="7.5">
              Anticline · Dip: 3.5° SSE
            </text>
          </g>

          {/* Baghjan Field */}
          <g>
            <rect x="420" y="30" width="125" height="70" rx="6" fill="#FFFBEB" stroke="#FDE68A" strokeWidth="1" opacity="0.7" />
            <text x="428" y="45" fill="#B45309" fontSize="9" fontWeight="bold" letterSpacing="0.5">
              BAGHJAN FIELD
            </text>
            <text x="428" y="56" fill="#D97706" fontSize="7.5">
              Overpressured · Dip: 2.5°
            </text>
          </g>

          {/* Active Well Radius Circle */}
          {activeWell && (
            <g>
              <circle
                cx={activePos.x}
                cy={activePos.y}
                r={radiusPx}
                fill="url(#radiusGradient)"
                stroke="#E58A13"
                strokeWidth="1.8"
                strokeDasharray="4 2"
              />
              <circle
                cx={activePos.x}
                cy={activePos.y}
                r={radiusPx + 2}
                fill="none"
                stroke="#184E3A"
                strokeWidth="0.8"
                opacity="0.4"
              />
            </g>
          )}

          {/* Well Pins */}
          {wells.map((w) => {
            const pos = project(w.surface_lat, w.surface_lon);
            const isActive = activeWell?.well_name === w.well_name;
            const distKm = getDistanceKm(w);
            const isInsideRadius = distKm <= radiusKm;
            const offset = getLabelOffset(w.well_name);

            return (
              <g
                key={w.well_name}
                className="cursor-pointer transition-all"
                onMouseEnter={() => setHoveredWell(w)}
                onMouseLeave={() => setHoveredWell(null)}
                onClick={() => onSelectWell(w)}
              >
                {/* Distance Connector Line to Active Well */}
                {activeWell && !isActive && isInsideRadius && (
                  <line
                    x1={activePos.x}
                    y1={activePos.y}
                    x2={pos.x}
                    y2={pos.y}
                    stroke="#E58A13"
                    strokeWidth="1.2"
                    strokeDasharray="3 3"
                    opacity="0.8"
                  />
                )}

                {/* Pin Shape */}
                {isActive ? (
                  <g>
                    {/* Pulsing reticle */}
                    <circle cx={pos.x} cy={pos.y} r="14" fill="#184E3A" opacity="0.18" className="animate-ping" />
                    <circle cx={pos.x} cy={pos.y} r="8" fill="#184E3A" stroke="#FFFFFF" strokeWidth="2" />
                    <circle cx={pos.x} cy={pos.y} r="3" fill="#E58A13" />
                  </g>
                ) : isInsideRadius ? (
                  <g>
                    <circle cx={pos.x} cy={pos.y} r="6" fill="#E58A13" stroke="#FFFFFF" strokeWidth="1.5" />
                    <circle cx={pos.x} cy={pos.y} r="2" fill="#184E3A" />
                  </g>
                ) : (
                  <circle cx={pos.x} cy={pos.y} r="4" fill="#64748B" stroke="#FFFFFF" strokeWidth="1.2" />
                )}

                {/* Well Name Tag with Staggered Offsets */}
                <text
                  x={pos.x + offset.dx}
                  y={pos.y + offset.dy}
                  fontSize={isActive ? "8.5" : "7.5"}
                  fontWeight={isActive ? "800" : isInsideRadius ? "700" : "500"}
                  fill={isActive ? "#184E3A" : isInsideRadius ? "#1E242B" : "#64748B"}
                  textAnchor={offset.anchor}
                >
                  {w.well_name === "SYN-NHK-05"
                    ? "SYN-NHK-05 (ACTIVE)"
                    : w.well_name === "SYN-NHK-01"
                    ? "SYN-NHK-01 (0.4km · STUCK)"
                    : w.well_name.replace("SYN-", "")}
                  {isInsideRadius && !isActive && w.well_name !== "SYN-NHK-01" && (
                    <tspan dx="2" fill="#E58A13" fontSize="6.5" fontWeight="bold">
                      [{distKm.toFixed(1)}k]
                    </tspan>
                  )}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Hovered Well Floating Tooltip */}
        {hoveredWell && (
          <div className="absolute top-3 left-3 bg-[#1E242B]/95 text-white backdrop-blur px-3 py-2 rounded-lg border border-slate-700 shadow-xl text-xs z-20 pointer-events-none animate-fadeIn">
            <div className="flex items-center justify-between gap-3">
              <span className="font-bold text-amber-400">{hoveredWell.well_name}</span>
              <span className="text-[10px] text-gray-300 bg-slate-800 px-1.5 py-0.2 rounded font-mono">
                {hoveredWell.field_name}
              </span>
            </div>
            <div className="text-[10px] text-gray-300 mt-1 space-y-0.5 font-mono">
              <div>Dist from Rig: <span className="text-emerald-400 font-bold">{getDistanceKm(hoveredWell).toFixed(2)} km</span></div>
              <div>Coordinates: {hoveredWell.surface_lat.toFixed(3)}°N, {hoveredWell.surface_lon.toFixed(3)}°E</div>
              {hoveredWell.well_name === "SYN-NHK-01" && (
                <div className="text-red-400 font-bold mt-1">⚠️ 38.5h Stuck Pipe in Upper Tipam</div>
              )}
            </div>
          </div>
        )}

        {/* Legend Overlay */}
        <div className="absolute bottom-3 left-3 bg-white/95 backdrop-blur px-2 py-1.5 rounded border border-slate-200 text-[9.5px] space-y-1 shadow-sm">
          <div className="flex items-center gap-1.5 font-bold text-[#184E3A]">
            <span className="w-2.5 h-2.5 rounded-full bg-[#184E3A] border border-white"></span>
            <span>Active Rig (SYN-NHK-05)</span>
          </div>
          <div className="flex items-center gap-1.5 font-semibold text-[#E58A13]">
            <span className="w-2.5 h-2.5 rounded-full bg-[#E58A13] border border-white"></span>
            <span>Offset Well (&lt;{radiusKm.toFixed(0)} km)</span>
          </div>
          <div className="flex items-center gap-1.5 text-gray-500">
            <span className="w-2 h-2 rounded-full bg-[#64748B]"></span>
            <span>Regional Well</span>
          </div>
        </div>
      </div>

      {/* Selected Well Summary Bar */}
      <div className="px-3 py-1.5 bg-white border-t border-[#E2E8F0] flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <MapPin className="w-3.5 h-3.5 text-[#184E3A]" />
          <div>
            <strong className="text-[#1E242B]">
              {hoveredWell?.well_name || activeWell?.well_name}
            </strong>
            <span className="text-gray-500 ml-2 text-[11px]">
              Field: {hoveredWell?.field_name || activeWell?.field_name} · TD:{" "}
              {hoveredWell?.total_depth_md_m || hoveredWell?.total_depth_m || activeWell?.total_depth_m || 4500}m
            </span>
          </div>
        </div>
        <div className="text-[10.5px] font-mono text-[#E58A13] font-bold">
          LAT: {(hoveredWell?.surface_lat || activeWell?.surface_lat || 27.28).toFixed(3)}°N · LON:{" "}
          {(hoveredWell?.surface_lon || activeWell?.surface_lon || 95.34).toFixed(3)}°E
        </div>
      </div>
    </div>
  );
};
