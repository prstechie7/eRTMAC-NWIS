"use client";

import React, { useEffect, useRef, useState } from "react";
import { Compass, Filter, MapPin, Globe, Info } from "lucide-react";
import { RigWeatherWidget } from "./RigWeatherWidget";
import gsap from "gsap";

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

const MAPTILER_KEY = process.env.NEXT_PUBLIC_MAPTILER_KEY || "o8Qhn3wgKrPhpfkNBiVU";

export const BasinMap: React.FC<BasinMapProps> = ({
  wells, activeWell, radiusKm, setRadiusKm, onSelectWell,
}) => {
  const [hoveredWell, setHoveredWell] = useState<WellPoint | null>(null);
  const [mapStyle, setMapStyle] = useState<"terrain" | "satellite" | "topo">("terrain");
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (cardRef.current) {
      gsap.fromTo(cardRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.6, ease: "power2.out", delay: 0.1 }
      );
    }
  }, []);

  const minLat = 27.12; const maxLat = 27.65;
  const minLon = 94.80; const maxLon = 95.65;
  const svgW = 560; const svgH = 300;

  const project = (lat: number, lon: number) => ({
    x: ((lon - minLon) / (maxLon - minLon)) * (svgW - 80) + 40,
    y: ((maxLat - lat) / (maxLat - minLat)) * (svgH - 60) + 30,
  });

  const kmToPixels = (km: number) =>
    (km / ((maxLon - minLon) * 99.2)) * (svgW - 80);

  const getDistanceKm = (w: WellPoint) => {
    if (!activeWell) return 0;
    const R = 6371;
    const dLat = ((w.surface_lat - activeWell.surface_lat) * Math.PI) / 180;
    const dLon = ((w.surface_lon - activeWell.surface_lon) * Math.PI) / 180;
    const a =
      Math.sin(dLat / 2) ** 2 +
      Math.cos((activeWell.surface_lat * Math.PI) / 180) *
      Math.cos((w.surface_lat * Math.PI) / 180) *
      Math.sin(dLon / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  };

  const getLabelOffset = (name: string) => {
    const map: Record<string, { dx: number; dy: number; anchor: "start" | "end" }> = {
      "SYN-NHK-05": { dx: 10, dy: -10, anchor: "start" },
      "SYN-NHK-01": { dx: 10, dy: 14, anchor: "start" },
      "SYN-NHK-02": { dx: 10, dy: -2, anchor: "start" },
      "SYN-NHK-03": { dx: -10, dy: 14, anchor: "end" },
      "SYN-NHK-04": { dx: 10, dy: 12, anchor: "start" },
    };
    return map[name] || { dx: 8, dy: 4, anchor: "start" as const };
  };

  const activePos = activeWell
    ? project(activeWell.surface_lat, activeWell.surface_lon)
    : { x: 380, y: 200 };
  const radiusPx = kmToPixels(radiusKm);

  // Map background colors per style
  const mapBg = {
    terrain: { bg: "#dfe9f0", grid: "#c5d5e3", field: "#d0e8db" },
    satellite: { bg: "#b8ccd8", grid: "#9eb8c5", field: "#b0d4c0" },
    topo: { bg: "#e6ead8", grid: "#cdd3be", field: "#cde0d0" },
  }[mapStyle];

  return (
    <div ref={cardRef} className="card flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="card-header">
        <div className="flex items-center gap-2.5">
          <div className="icon-chip icon-chip-pine">
            <Compass className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-heading font-bold text-[13px]" style={{ color: "var(--text-primary)" }}>
              Panel 1 · 2D Basin Navigator
            </h3>
            <p className="text-[11px]" style={{ color: "var(--text-muted)" }}>MapTiler · Upper Assam Basin</p>
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          <Globe className="w-3.5 h-3.5" style={{ color: "var(--pine)" }} />
          <span className="text-[11px] font-mono" style={{ color: "var(--text-secondary)" }}>
            Vector/Satellite API
          </span>
          <span className="live-dot" />
        </div>
      </div>

      {/* Control Bar */}
      <div
        className="px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 text-xs"
        style={{ borderBottom: "1px solid var(--border)", background: "var(--surface-2)" }}
      >
        {/* Radius */}
        <div className="flex items-center gap-2.5">
          <Filter className="w-3.5 h-3.5" style={{ color: "var(--amber)" }} />
          <span className="font-semibold" style={{ color: "var(--text-secondary)" }}>Search Radius:</span>
          <span
            className="font-mono font-bold px-2.5 py-0.5 rounded text-xs"
            style={{ background: "var(--pine-pale)", color: "var(--pine)", border: "1px solid #b2d8c8" }}
          >
            {radiusKm.toFixed(1)} km
          </span>
          <input
            type="range" min="1.0" max="15.0" step="0.5" value={radiusKm}
            onChange={(e) => setRadiusKm(parseFloat(e.target.value))}
            className="w-28"
          />
        </div>

        {/* Style Selector */}
        <div
          className="flex items-center gap-1 rounded-lg p-1"
          style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
        >
          {(["terrain", "satellite", "topo"] as const).map((s) => (
            <button
              key={s}
              onClick={() => setMapStyle(s)}
              className="text-[10.5px] font-semibold capitalize px-2.5 py-1 rounded-md transition-all"
              style={{
                background: mapStyle === s ? "var(--pine)" : "transparent",
                color: mapStyle === s ? "white" : "var(--text-secondary)",
              }}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* SVG Map Canvas */}
      <div className="relative p-3 flex-1 flex items-center justify-center" style={{ background: "#f0f5f8" }}>
        <svg
          viewBox={`0 0 ${svgW} ${svgH}`}
          className="w-full h-auto map-canvas"
          style={{ maxHeight: 280 }}
        >
          <defs>
            <pattern id="mapgrid" width="30" height="30" patternUnits="userSpaceOnUse">
              <path d="M 30 0 L 0 0 0 30" fill="none" stroke={mapBg.grid} strokeWidth="0.7" />
            </pattern>
            <radialGradient id="radiusGrd" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#1a5c45" stopOpacity="0.08" />
              <stop offset="70%" stopColor="#1a5c45" stopOpacity="0.05" />
              <stop offset="100%" stopColor="#1a5c45" stopOpacity="0.18" />
            </radialGradient>
          </defs>

          <rect width="100%" height="100%" fill={mapBg.bg} />
          <rect width="100%" height="100%" fill="url(#mapgrid)" />

          {/* Fault line */}
          <path
            d="M 30 190 Q 220 150 530 80"
            fill="none" stroke="#94a3b8" strokeWidth="1.5" strokeDasharray="5 4"
          />
          <text x="180" y="138" fill="#94a3b8" fontSize="8" fontStyle="italic">
            Brahmaputra Regional Alluvial Fault
          </text>

          {/* Field Regions */}
          <rect x="35" y="190" width="110" height="80" rx="8"
            fill="rgba(148,163,184,0.15)" stroke="#94a3b8" strokeWidth="1" />
          <text x="43" y="208" fill="#64748b" fontSize="9" fontWeight="700">MORAN FIELD</text>

          <rect x="318" y="168" width="170" height="120" rx="8"
            fill={`${mapBg.field}88`} stroke="#1a5c45" strokeWidth="1.5" />
          <text x="326" y="185" fill="#1a5c45" fontSize="9" fontWeight="700">NAHORKATIYA FIELD (ACTIVE)</text>

          <rect x="420" y="28" width="128" height="72" rx="8"
            fill="rgba(217,119,6,0.08)" stroke="#d97706" strokeWidth="1.2" />
          <text x="428" y="46" fill="#d97706" fontSize="9" fontWeight="700">BAGHJAN FIELD</text>

          {/* Radius Circle */}
          {activeWell && (
            <g>
              <circle
                cx={activePos.x} cy={activePos.y} r={radiusPx}
                fill="url(#radiusGrd)"
                stroke="#1a5c45"
                strokeWidth="1.5"
                strokeDasharray="5 3"
              />
            </g>
          )}

          {/* Connector Lines */}
          {wells.map((w) => {
            const pos = project(w.surface_lat, w.surface_lon);
            const isActive = activeWell?.well_name === w.well_name;
            const dist = getDistanceKm(w);
            const inside = dist <= radiusKm;
            if (!isActive && inside && activeWell) {
              return (
                <line key={`line-${w.well_name}`}
                  x1={activePos.x} y1={activePos.y} x2={pos.x} y2={pos.y}
                  stroke="#1a5c45" strokeWidth="1" strokeDasharray="3 3" opacity="0.5"
                />
              );
            }
            return null;
          })}

          {/* Well Pins */}
          {wells.map((w) => {
            const pos = project(w.surface_lat, w.surface_lon);
            const isActive = activeWell?.well_name === w.well_name;
            const dist = getDistanceKm(w);
            const inside = dist <= radiusKm;
            const offset = getLabelOffset(w.well_name);

            return (
              <g
                key={w.well_name}
                className="cursor-pointer"
                onMouseEnter={() => setHoveredWell(w)}
                onMouseLeave={() => setHoveredWell(null)}
                onClick={() => onSelectWell(w)}
              >
                {isActive ? (
                  <>
                    <circle cx={pos.x} cy={pos.y} r="16" fill="#1a5c45" opacity="0.12" />
                    <circle cx={pos.x} cy={pos.y} r="9" fill="#1a5c45" stroke="white" strokeWidth="2.5" />
                    <circle cx={pos.x} cy={pos.y} r="3.5" fill="white" />
                  </>
                ) : inside ? (
                  <>
                    <circle cx={pos.x} cy={pos.y} r="6.5" fill="#d97706" stroke="white" strokeWidth="2" />
                    <circle cx={pos.x} cy={pos.y} r="2" fill="white" />
                  </>
                ) : (
                  <circle cx={pos.x} cy={pos.y} r="4" fill="#94a3b8" stroke="white" strokeWidth="1.5" />
                )}

                <text
                  x={pos.x + offset.dx}
                  y={pos.y + offset.dy}
                  fontSize={isActive ? "8.5" : "7.5"}
                  fontWeight={isActive ? "800" : inside ? "700" : "500"}
                  fill={isActive ? "#1a5c45" : inside ? "#0f172a" : "#94a3b8"}
                  textAnchor={offset.anchor}
                  fontFamily="JetBrains Mono, monospace"
                >
                  {w.well_name === "SYN-NHK-05"
                    ? "SYN-NHK-05 (ACTIVE)"
                    : w.well_name === "SYN-NHK-01"
                    ? "NHK-01 (0.4km · STUCK)"
                    : w.well_name.replace("SYN-", "")}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Hover Tooltip */}
        {hoveredWell && (
          <div
            className="absolute top-4 left-4 p-3 rounded-xl shadow-lg z-20 pointer-events-none text-xs"
            style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              boxShadow: "var(--shadow-lg)"
            }}
          >
            <div className="flex items-center gap-2 mb-1.5">
              <span className="font-heading font-bold" style={{ color: "var(--text-primary)" }}>
                {hoveredWell.well_name}
              </span>
              <span className="badge badge-pine">{hoveredWell.field_name}</span>
            </div>
            <div className="font-mono space-y-0.5" style={{ color: "var(--text-secondary)" }}>
              <div>
                Distance:{" "}
                <span className="font-bold" style={{ color: "var(--pine)" }}>
                  {getDistanceKm(hoveredWell).toFixed(2)} km
                </span>
              </div>
              <div>
                {hoveredWell.surface_lat.toFixed(3)}°N, {hoveredWell.surface_lon.toFixed(3)}°E
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Weather Widget */}
      <div className="px-3 py-2.5" style={{ borderTop: "1px solid var(--border)" }}>
        <RigWeatherWidget
          lat={activeWell?.surface_lat || 27.2885}
          lon={activeWell?.surface_lon || 95.3345}
        />
      </div>

      {/* Footer */}
      <div className="card-footer flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <MapPin className="w-3.5 h-3.5" style={{ color: "var(--pine)" }} />
          <span className="font-mono font-bold" style={{ color: "var(--text-primary)" }}>
            {hoveredWell?.well_name || activeWell?.well_name}
          </span>
          <span style={{ color: "var(--text-muted)" }}>
            Field: {hoveredWell?.field_name || activeWell?.field_name} · TD:{" "}
            {hoveredWell?.total_depth_m || activeWell?.total_depth_m || 4500}m
          </span>
        </div>
        <span className="font-mono text-[10px]" style={{ color: "var(--text-muted)" }}>
          © MapTiler · OpenStreetMap contributors
        </span>
      </div>
    </div>
  );
};
