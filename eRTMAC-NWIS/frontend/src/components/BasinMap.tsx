"use client";

import React, { useState } from "react";
import { Compass, Filter, MapPin, AlertTriangle, Layers, Info } from "lucide-react";

export interface WellPoint {
  well_id: string;
  well_name: string;
  field_name: string;
  surface_lat: number;
  surface_lon: number;
  kb_elevation_m: number;
  total_depth_m: number;
  status: string;
  recorded_hazards_count?: number;
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
  const [selectedPin, setSelectedPin] = useState<WellPoint | null>(null);

  // Map Bounds for Upper Assam Basin
  // Lat: 27.15 to 27.65 (Moran to Baghjan)
  // Lon: 94.85 to 95.45
  const minLat = 27.15;
  const maxLat = 27.65;
  const minLon = 94.85;
  const maxLon = 95.45;

  const mapWidth = 520;
  const mapHeight = 360;

  // Project lat/lon to SVG canvas coordinates
  const project = (lat: number, lon: number) => {
    const x = ((lon - minLon) / (maxLon - minLon)) * (mapWidth - 60) + 30;
    const y = ((maxLat - lat) / (maxLat - minLat)) * (mapHeight - 60) + 30;
    return { x, y };
  };

  // Convert km radius to SVG pixels at 27.3°N latitude
  // 1 deg lat ~ 111 km, 1 deg lon ~ 99 km
  const kmToPixels = (km: number) => {
    const totalKmX = (maxLon - minLon) * 99; // approx 59.4 km
    return (km / totalKmX) * (mapWidth - 60);
  };

  const activePos = activeWell ? project(activeWell.surface_lat, activeWell.surface_lon) : { x: 340, y: 220 };
  const radiusPx = kmToPixels(radiusKm);

  // Haversine calculation for display
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

  return (
    <div className="bg-white rounded-lg border border-[#E2E8F0] shadow-sm overflow-hidden flex flex-col h-full">
      {/* Header Bar */}
      <div className="bg-[#F8F9FA] px-4 py-2.5 border-b border-[#E2E8F0] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#184E3A]"></div>
          <span className="font-bold text-xs uppercase tracking-wider text-[#184E3A]">
            Panel 1 · 2D Basin Navigator & Spatial Radius
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="text-gray-500 font-medium">Upper Assam Structural Corridor</span>
        </div>
      </div>

      {/* Control Bar: Radius Slider */}
      <div className="px-4 py-2 bg-slate-50 border-b border-[#E2E8F0] flex items-center justify-between gap-4 text-xs">
        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-[#E58A13]" />
          <span className="font-semibold text-gray-700">Offset Search Radius:</span>
          <span className="font-mono font-bold text-[#184E3A] bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
            {radiusKm.toFixed(1)} km
          </span>
        </div>
        <input
          type="range"
          min="1.0"
          max="15.0"
          step="0.5"
          value={radiusKm}
          onChange={(e) => setRadiusKm(parseFloat(e.target.value))}
          className="w-40 h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#184E3A]"
        />
      </div>

      {/* Map SVG Canvas */}
      <div className="relative p-2 bg-[#F1F5F9] flex-1 flex items-center justify-center min-h-[300px]">
        <svg
          viewBox={`0 0 ${mapWidth} ${mapHeight}`}
          className="w-full h-auto max-h-[360px] bg-[#FFFFFF] rounded border border-slate-200 shadow-inner"
        >
          {/* Subtle Grid Lines */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#F1F5F9" strokeWidth="1" />
            </pattern>
            {/* Pulsing Target Marker */}
            <radialGradient id="radiusGradient" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#E58A13" stopOpacity="0.18" />
              <stop offset="85%" stopColor="#E58A13" stopOpacity="0.08" />
              <stop offset="100%" stopColor="#E58A13" stopOpacity="0.35" />
            </radialGradient>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />

          {/* Regional Geographic Labels */}
          <text x="70" y="270" fill="#94A3B8" fontSize="10" fontWeight="bold" letterSpacing="1">
            MORAN FIELD
          </text>
          <text x="320" y="270" fill="#94A3B8" fontSize="10" fontWeight="bold" letterSpacing="1">
            NAHORKATIYA FIELD
          </text>
          <text x="360" y="70" fill="#94A3B8" fontSize="10" fontWeight="bold" letterSpacing="1">
            BAGHJAN FIELD
          </text>
          <path
            d="M 50 180 Q 220 150 480 120"
            fill="none"
            stroke="#CBD5E1"
            strokeWidth="2"
            strokeDasharray="4 4"
          />
          <text x="230" y="140" fill="#64748B" fontSize="9" fontStyle="italic">
            Brahmaputra Regional Alluvial Fault Line
          </text>

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
                r={radiusPx + 3}
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

            return (
              <g
                key={w.well_name}
                className="cursor-pointer transition-all hover:scale-110"
                onClick={() => {
                  setSelectedPin(w);
                  onSelectWell(w);
                }}
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
                    opacity="0.75"
                  />
                )}

                {/* Pin Circle */}
                {isActive ? (
                  <g>
                    <circle cx={pos.x} cy={pos.y} r="9" fill="#184E3A" stroke="#FFFFFF" strokeWidth="2.5" />
                    <circle cx={pos.x} cy={pos.y} r="4" fill="#E58A13" />
                  </g>
                ) : isInsideRadius ? (
                  <g>
                    <circle cx={pos.x} cy={pos.y} r="6.5" fill="#E58A13" stroke="#FFFFFF" strokeWidth="2" />
                    <circle cx={pos.x} cy={pos.y} r="2.5" fill="#184E3A" />
                  </g>
                ) : (
                  <circle cx={pos.x} cy={pos.y} r="4.5" fill="#64748B" stroke="#FFFFFF" strokeWidth="1.5" />
                )}

                {/* Well Name Tag */}
                <text
                  x={pos.x + 8}
                  y={pos.y + 3}
                  fontSize="9.5"
                  fontWeight={isActive ? "800" : isInsideRadius ? "700" : "500"}
                  fill={isActive ? "#184E3A" : isInsideRadius ? "#1E242B" : "#64748B"}
                >
                  {w.well_name}
                  {isInsideRadius && !isActive && (
                    <tspan dx="4" fill="#E58A13" fontSize="8.5" fontWeight="bold">
                      ({distKm.toFixed(2)} km)
                    </tspan>
                  )}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Legend Overlay */}
        <div className="absolute bottom-3 left-4 bg-white/95 backdrop-blur px-2.5 py-1.5 rounded border border-slate-200 text-[10px] space-y-1 shadow-sm">
          <div className="flex items-center gap-1.5 font-bold text-gray-700">
            <span className="w-2.5 h-2.5 rounded-full bg-[#184E3A] border border-white"></span>
            <span>Active Rig (SYN-NHK-05)</span>
          </div>
          <div className="flex items-center gap-1.5 text-gray-600">
            <span className="w-2.5 h-2.5 rounded-full bg-[#E58A13] border border-white"></span>
            <span>Offset Well (&lt;{radiusKm} km)</span>
          </div>
          <div className="flex items-center gap-1.5 text-gray-500">
            <span className="w-2 h-2 rounded-full bg-[#64748B]"></span>
            <span>Distant Field Well</span>
          </div>
        </div>
      </div>

      {/* Selected Well Summary Bar */}
      <div className="p-3 bg-white border-t border-[#E2E8F0] flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-[#184E3A]" />
          <div>
            <span className="font-bold text-[#1E242B]">
              {selectedPin ? selectedPin.well_name : activeWell?.well_name || "Select Well"}
            </span>
            <span className="text-gray-500 ml-2">
              Field: {selectedPin?.field_name || activeWell?.field_name} · TD:{" "}
              {selectedPin?.total_depth_m || activeWell?.total_depth_m}m MD
            </span>
          </div>
        </div>
        <div className="text-[11px] font-mono text-[#E58A13] font-bold">
          LAT: {selectedPin?.surface_lat || activeWell?.surface_lat}°N · LON:{" "}
          {selectedPin?.surface_lon || activeWell?.surface_lon}°E
        </div>
      </div>
    </div>
  );
};
