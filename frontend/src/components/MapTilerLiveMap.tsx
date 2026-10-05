"use client";

import React, { useEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";
import { Navigation, Filter, Layers, Crosshair, Search, MapPin, Compass } from "lucide-react";

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

interface MapTilerMapProps {
  wells: WellPoint[];
  activeWell: WellPoint | null;
  radiusKm: number;
  setRadiusKm: (r: number) => void;
  onSelectWell: (w: WellPoint) => void;
}

const MAPTILER_KEY = process.env.NEXT_PUBLIC_MAPTILER_KEY || "o8Qhn3wgKrPhpfkNBiVU";

const TILE_STYLES: Record<string, { url: string; label: string; icon: string; attribution: string }> = {
  hybrid: {
    url: `https://api.maptiler.com/maps/hybrid/{z}/{x}/{y}.jpg?key=${MAPTILER_KEY}`,
    label: "Hybrid Satellite",
    icon: "🛰️",
    attribution: `© <a href="https://www.maptiler.com/copyright/" target="_blank">MapTiler</a> © <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors</a>`
  },
  satellite: {
    url: `https://api.maptiler.com/maps/satellite/{z}/{x}/{y}.jpg?key=${MAPTILER_KEY}`,
    label: "Pure Satellite",
    icon: "🌍",
    attribution: `© <a href="https://www.maptiler.com/copyright/" target="_blank">MapTiler</a>`
  },
  topo: {
    url: `https://api.maptiler.com/maps/topo-v2/{z}/{x}/{y}.png?key=${MAPTILER_KEY}`,
    label: "Topographic",
    icon: "⛰️",
    attribution: `© <a href="https://www.maptiler.com/copyright/" target="_blank">MapTiler</a> © <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors</a>`
  },
  streets: {
    url: `https://api.maptiler.com/maps/streets-v2/{z}/{x}/{y}.png?key=${MAPTILER_KEY}`,
    label: "Streets",
    icon: "🛣️",
    attribution: `© <a href="https://www.maptiler.com/copyright/" target="_blank">MapTiler</a> © <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors</a>`
  },
};

// Inner component running exclusively on client with Leaflet
const LeafletMapInner: React.FC<MapTilerMapProps & { tileStyle: string }> = ({
  wells, activeWell, radiusKm, onSelectWell, tileStyle,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const leafletMapRef = useRef<any>(null);
  const tileLayerRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const circleRef = useRef<any>(null);

  const getDistKm = (w: WellPoint) => {
    if (!activeWell) return 0;
    const R = 6371;
    const dLat = ((w.surface_lat - activeWell.surface_lat) * Math.PI) / 180;
    const dLon = ((w.surface_lon - activeWell.surface_lon) * Math.PI) / 180;
    const a = Math.sin(dLat / 2) ** 2 + Math.cos((activeWell.surface_lat * Math.PI) / 180) * Math.cos((w.surface_lat * Math.PI) / 180) * Math.sin(dLon / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  };

  useEffect(() => {
    if (!mapContainerRef.current || leafletMapRef.current) return;

    let isMounted = true;

    import("leaflet").then((L) => {
      if (!isMounted || !mapContainerRef.current) return;

      // Fix Leaflet's default icon paths
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      });

      const center = activeWell
        ? [activeWell.surface_lat, activeWell.surface_lon] as [number, number]
        : [27.2885, 95.3345] as [number, number];

      const map = L.map(mapContainerRef.current, {
        center,
        zoom: 12,
        zoomControl: false,
        attributionControl: true,
      });

      // Zoom control in bottom right
      L.control.zoom({ position: "bottomright" }).addTo(map);
      L.control.scale({ imperial: false, position: "bottomleft" }).addTo(map);

      // MapTiler tile layer (512px tile with -1 zoomOffset for high-res retina)
      const currentStyle = TILE_STYLES[tileStyle] || TILE_STYLES.hybrid;
      const tileLayer = L.tileLayer(currentStyle.url, {
        attribution: currentStyle.attribution,
        maxZoom: 19,
        tileSize: 512,
        zoomOffset: -1,
      }).addTo(map);

      tileLayerRef.current = tileLayer;
      leafletMapRef.current = map;

      // Invalidate size to ensure full tile coverage
      setTimeout(() => {
        if (map) map.invalidateSize();
      }, 150);
      setTimeout(() => {
        if (map) map.invalidateSize();
      }, 500);

      renderMarkersAndRadius(L, map);
    });

    const handleResize = () => {
      if (leafletMapRef.current) {
        leafletMapRef.current.invalidateSize();
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      isMounted = false;
      window.removeEventListener("resize", handleResize);
      if (leafletMapRef.current) {
        leafletMapRef.current.remove();
        leafletMapRef.current = null;
        markersRef.current = [];
        circleRef.current = null;
        tileLayerRef.current = null;
      }
    };
  }, []);

  // Update markers/circle when wells, active well, or radius change
  useEffect(() => {
    if (!leafletMapRef.current) return;
    import("leaflet").then((L) => {
      renderMarkersAndRadius(L, leafletMapRef.current!);
    });
  }, [wells, activeWell?.well_name, radiusKm]);

  // Swap tile layer when style changes
  useEffect(() => {
    if (!leafletMapRef.current || !tileLayerRef.current) return;
    import("leaflet").then((L) => {
      tileLayerRef.current.remove();
      const currentStyle = TILE_STYLES[tileStyle] || TILE_STYLES.hybrid;
      tileLayerRef.current = L.tileLayer(currentStyle.url, {
        attribution: currentStyle.attribution,
        maxZoom: 19,
        tileSize: 512,
        zoomOffset: -1,
      }).addTo(leafletMapRef.current!);
    });
  }, [tileStyle]);

  // Pan to active well when selection changes
  useEffect(() => {
    if (!leafletMapRef.current || !activeWell) return;
    leafletMapRef.current.flyTo(
      [activeWell.surface_lat, activeWell.surface_lon],
      12.5,
      { duration: 1.0 }
    );
  }, [activeWell?.well_name]);

  const renderMarkersAndRadius = (L: any, map: any) => {
    // Clear existing markers & circle
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];
    if (circleRef.current) {
      circleRef.current.remove();
      circleRef.current = null;
    }

    // Draw offset radius circle around active drilling well
    if (activeWell) {
      circleRef.current = L.circle(
        [activeWell.surface_lat, activeWell.surface_lon],
        {
          radius: radiusKm * 1000,
          color: "#059669",
          fillColor: "#10b981",
          fillOpacity: 0.08,
          weight: 2,
          dashArray: "6, 6",
        }
      ).addTo(map);
    }

    // Add well markers
    wells.forEach((w) => {
      const isActive = activeWell?.well_name === w.well_name;
      const dist = getDistKm(w);
      const inRadius = activeWell ? dist <= radiusKm : true;
      const isDrilling = w.status === "DRILLING";

      const fieldColor =
        w.field_name === "Nahorkatiya"
          ? (isDrilling ? "#059669" : "#d97706")
          : w.field_name === "Moran"
          ? "#2563eb"
          : "#7c3aed";

      // Rich SVG icons
      const size = isActive ? 34 : inRadius ? 22 : 16;
      let iconHtml = "";

      if (isActive) {
        // Active rig: animated pulsing radar ring + drilling derrick symbol
        iconHtml = `
          <div style="position:relative;width:${size}px;height:${size}px;display:flex;align-items:center;justify-content:center;">
            <div style="position:absolute;inset:-6px;border-radius:50%;background:rgba(5,150,105,0.25);animation:ping 2s cubic-bezier(0,0,0.2,1) infinite;"></div>
            <div style="position:absolute;inset:0;border-radius:50%;background:#059669;box-shadow:0 0 14px rgba(5,150,105,0.8);border:2.5px solid #ffffff;display:flex;align-items:center;justify-content:center;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2v20M5 22h14M8 12h8M7 7h10M6 17h12"/>
              </svg>
            </div>
          </div>
        `;
      } else {
        // Offset well pin: color-coded dot with clean border
        iconHtml = `
          <div style="width:${size}px;height:${size}px;border-radius:50%;background:${fieldColor};border:2px solid white;box-shadow:0 2px 6px rgba(15,23,42,0.35);display:flex;align-items:center;justify-content:center;">
            <div style="width:${Math.max(4, size - 12)}px;height:${Math.max(4, size - 12)}px;border-radius:50%;background:white;opacity:0.9;"></div>
          </div>
        `;
      }

      const icon = L.divIcon({
        html: iconHtml,
        className: "ertmac-map-icon",
        iconSize: [size, size],
        iconAnchor: [size / 2, size / 2],
        popupAnchor: [0, -(size / 2 + 6)],
      });

      const popupHtml = `
        <div style="font-family:Inter,-apple-system,BlinkMacSystemFont,sans-serif;min-width:210px;padding:4px 2px;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid #e2e8f0;">
            <div style="width:12px;height:12px;border-radius:50%;background:${fieldColor};box-shadow:0 0 6px ${fieldColor}88;"></div>
            <div style="font-weight:800;font-size:14px;color:#0f172a;letter-spacing:-0.01em;">${w.well_name}</div>
            ${isDrilling ? `<span style="background:#ecfdf5;color:#059669;border:1px solid #a7f3d0;font-size:9px;font-weight:700;padding:2px 7px;border-radius:12px;margin-left:auto;">● DRILLING</span>` : ""}
          </div>
          <table style="width:100%;font-size:11.5px;border-collapse:collapse;line-height:1.6;">
            <tr><td style="color:#64748b;padding:2px 10px 2px 0;">Field</td><td style="color:#0f172a;font-weight:600;">${w.field_name}</td></tr>
            <tr><td style="color:#64748b;padding:2px 10px 2px 0;">Status</td><td style="color:#0f172a;font-weight:600;">${w.status}</td></tr>
            <tr><td style="color:#64748b;padding:2px 10px 2px 0;">Total Depth</td><td style="color:#0f172a;font-weight:700;font-family:monospace;">${w.total_depth_m || "—"} m</td></tr>
            <tr><td style="color:#64748b;padding:2px 10px 2px 0;">KB Elevation</td><td style="color:#0f172a;font-weight:600;font-family:monospace;">${w.kb_elevation_m || "—"} m</td></tr>
            ${activeWell ? `<tr><td style="color:#64748b;padding:2px 10px 2px 0;">Distance</td><td style="color:#059669;font-weight:800;font-family:monospace;">${dist.toFixed(2)} km</td></tr>` : ""}
            <tr><td style="color:#64748b;padding:2px 10px 2px 0;">Coords</td><td style="color:#0f172a;font-family:monospace;font-size:10px;">${w.surface_lat.toFixed(4)}°N, ${w.surface_lon.toFixed(4)}°E</td></tr>
          </table>
          <button
            onclick="window.__ertmacSelectWell && window.__ertmacSelectWell('${w.well_name}')"
            style="margin-top:10px;width:100%;padding:7px 10px;background:${isActive ? "#059669" : "#0f172a"};color:white;border:none;border-radius:8px;font-weight:700;font-size:11.5px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;transition:background 0.15s ease;"
          >
            ${isActive ? "✓ Currently Active Rig" : "▶ Set as Active Rig"}
          </button>
        </div>
      `;

      const marker = L.marker([w.surface_lat, w.surface_lon], { icon })
        .addTo(map)
        .bindPopup(popupHtml, {
          maxWidth: 240,
          className: "ertmac-leaflet-popup",
        });

      marker.on("click", () => {
        onSelectWell(w);
      });

      markersRef.current.push(marker);
    });

    // Global callback for popup button
    (window as any).__ertmacSelectWell = (name: string) => {
      const w = wells.find((x) => x.well_name === name);
      if (w) onSelectWell(w);
    };
  };

  return (
    <div
      ref={mapContainerRef}
      className="w-full h-full min-h-[480px]"
      style={{ zIndex: 1 }}
    />
  );
};

// Client-only dynamic loader
const LeafletMapDynamic = dynamic(
  () => Promise.resolve(LeafletMapInner),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full min-h-[480px] flex flex-col items-center justify-center bg-slate-100">
        <div className="w-10 h-10 rounded-full mb-3 animate-spin border-4 border-slate-300 border-t-emerald-600" />
        <p className="text-sm font-semibold text-slate-700">Loading MapTiler Hybrid Satellite…</p>
        <p className="text-[11px] font-mono text-slate-500 mt-1">Calibrated for Upper Assam Petroleum Province</p>
      </div>
    ),
  }
);

export const MapTilerLiveMap: React.FC<MapTilerMapProps> = ({
  wells, activeWell, radiusKm, setRadiusKm, onSelectWell,
}) => {
  const [tileStyle, setTileStyle] = useState("hybrid");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredWells = searchQuery
    ? wells.filter(
        (w) =>
          w.well_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          w.field_name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : wells;

  return (
    <div className="card flex flex-col overflow-hidden shadow-lg border border-slate-200" style={{ minHeight: 600 }}>
      {/* ─── Control Bar ─── */}
      <div className="px-4 py-3 bg-white border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
        {/* Left: Title & Stats */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700 shadow-sm flex-shrink-0">
            <Navigation className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-heading font-bold text-sm text-slate-900">
                2D Basin Spatial Navigator · Upper Assam Province
              </h3>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                MAPTILER SATELLITE
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Real-time offset intelligence · {wells.length} wells monitored · {radiusKm} km advisory radius
            </p>
          </div>
        </div>

        {/* Right: Controls */}
        <div className="flex items-center flex-wrap gap-2">
          {/* Quick Search */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Find well / field…"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="text-xs pl-8 pr-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white w-36 lg:w-44 transition-all"
            />
          </div>

          {/* Map Layer Switcher */}
          <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200">
            {Object.entries(TILE_STYLES).map(([id, s]) => (
              <button
                key={id}
                onClick={() => setTileStyle(id)}
                title={s.label}
                className={`flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-md transition-all ${
                  tileStyle === id
                    ? "bg-white text-emerald-800 shadow-xs font-bold"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <span>{s.icon}</span>
                <span className="hidden md:inline">{s.label.split(" ")[0]}</span>
              </button>
            ))}
          </div>

          {/* Radius Selector */}
          <div className="flex items-center gap-2 px-2.5 py-1 bg-slate-50 rounded-lg border border-slate-200">
            <Filter className="w-3.5 h-3.5 text-slate-500" />
            <span className="text-xs font-mono font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-100">
              {radiusKm.toFixed(1)} km
            </span>
            <input
              type="range"
              min="1"
              max="20"
              step="0.5"
              value={radiusKm}
              onChange={(e) => setRadiusKm(parseFloat(e.target.value))}
              className="w-20 accent-emerald-600 cursor-pointer"
            />
          </div>
        </div>
      </div>

      {/* ─── Map Container ─── */}
      <div className="relative flex-1 bg-slate-200" style={{ minHeight: 520 }}>
        <LeafletMapDynamic
          wells={filteredWells}
          activeWell={activeWell}
          radiusKm={radiusKm}
          setRadiusKm={setRadiusKm}
          onSelectWell={onSelectWell}
          tileStyle={tileStyle}
        />

        {/* Well Field Legend Overlay */}
        <div
          className="absolute top-4 left-4 z-[999] px-3.5 py-3 rounded-xl text-xs bg-white/95 backdrop-blur-md border border-slate-200/90 shadow-xl pointer-events-auto"
          style={{ maxWidth: 220 }}
        >
          <div className="font-heading font-bold text-xs text-slate-900 mb-2 flex items-center justify-between">
            <span>Well Legend</span>
            <span className="text-[10px] font-mono text-slate-500 font-normal">Assam Arc</span>
          </div>
          <div className="space-y-1.5">
            {[
              {
                color: "#059669",
                label: "Active Rig (Drilling)",
                count: wells.filter((w) => w.status === "DRILLING").length,
                isPulsing: true,
              },
              {
                color: "#d97706",
                label: "Nahorkatiya Field",
                count: wells.filter((w) => w.field_name === "Nahorkatiya" && w.status !== "DRILLING").length,
              },
              {
                color: "#2563eb",
                label: "Moran Field",
                count: wells.filter((w) => w.field_name === "Moran").length,
              },
              {
                color: "#7c3aed",
                label: "Baghjan Field",
                count: wells.filter((w) => w.field_name === "Baghjan").length,
              },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between gap-3 text-[11px]">
                <div className="flex items-center gap-2">
                  <div
                    className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                    style={{
                      background: item.color,
                      boxShadow: item.isPulsing ? `0 0 6px ${item.color}` : "none",
                    }}
                  />
                  <span className="text-slate-700 font-medium">{item.label}</span>
                </div>
                <span className="font-mono font-bold text-slate-900">{item.count}</span>
              </div>
            ))}
          </div>

          <div className="mt-2.5 pt-2 border-t border-slate-200 flex items-center justify-between text-[10.5px] text-slate-500">
            <div className="flex items-center gap-1.5">
              <div className="w-3.5 border-t-2 border-dashed border-emerald-600" />
              <span>Offset Zone</span>
            </div>
            <span className="font-mono font-bold text-emerald-700">{radiusKm} km</span>
          </div>
        </div>

        {/* Map Key & Provenance Tag */}
        <div
          className="absolute bottom-3 left-3 z-[999] px-2.5 py-1 rounded-md text-[10px] font-mono bg-white/90 backdrop-blur-xs border border-slate-200 text-slate-600 shadow-xs"
        >
          MapTiler Hybrid Satellite · SPE-197489-MS Calibrated
        </div>
      </div>

      {/* ─── Footer Status ─── */}
      <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-4 font-mono text-xs">
          <div className="flex items-center gap-1.5">
            <span className="text-slate-500">Active Rig:</span>
            <span className="font-bold text-emerald-800 bg-emerald-100/60 px-1.5 py-0.5 rounded border border-emerald-200">
              {activeWell?.well_name || "SYN-NHK-05"}
            </span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-slate-500">Field:</span>
            <span className="font-bold text-slate-800">{activeWell?.field_name || "Nahorkatiya"}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-slate-500">Target TD:</span>
            <span className="font-bold text-slate-800">{activeWell?.total_depth_m || 3150}m</span>
          </div>
          <div className="hidden sm:flex items-center gap-1">
            <span className="text-slate-500">Coords:</span>
            <span className="font-bold text-slate-800">
              {activeWell?.surface_lat?.toFixed(4)}°N, {activeWell?.surface_lon?.toFixed(4)}°E
            </span>
          </div>
        </div>

        <div className="text-[11px] text-slate-500 flex items-center gap-2">
          <span>Map tiles © MapTiler</span>
          <span>·</span>
          <span>© OpenStreetMap contributors</span>
        </div>
      </div>
    </div>
  );
};
