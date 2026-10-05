"use client";

import React, { useEffect, useRef, useState } from "react";
import { Layers, Crosshair, ZoomIn, ZoomOut, Compass, MapPin } from "lucide-react";

export interface MapPoint {
  id: string;
  name: string;
  type: "WELL" | "BASIN";
  lat: number;
  lon: number;
  operator: string;
  distanceKm: number;
  field?: string;
  basin?: string;
  depthM?: number;
  status?: string;
}

interface IndianProximityMapProps {
  userLat: number;
  userLon: number;
  radiusKm: number;
  points: MapPoint[];
  onSelectPoint?: (pt: MapPoint) => void;
  selectedPointId?: string | null;
}

const MAPTILER_KEY = process.env.NEXT_PUBLIC_MAPTILER_KEY || "o8Qhn3wgKrPhpfkNBiVU";

const TILE_STYLES: Record<string, { url: string; label: string; icon: string }> = {
  hybrid: {
    url: `https://api.maptiler.com/maps/hybrid/{z}/{x}/{y}.jpg?key=${MAPTILER_KEY}`,
    label: "Hybrid Satellite",
    icon: "🛰️",
  },
  satellite: {
    url: `https://api.maptiler.com/maps/satellite/{z}/{x}/{y}.jpg?key=${MAPTILER_KEY}`,
    label: "Pure Satellite",
    icon: "🌍",
  },
  topo: {
    url: `https://api.maptiler.com/maps/topo-v2/{z}/{x}/{y}.png?key=${MAPTILER_KEY}`,
    label: "Topographic",
    icon: "⛰️",
  },
  streets: {
    url: `https://api.maptiler.com/maps/streets-v2/{z}/{x}/{y}.png?key=${MAPTILER_KEY}`,
    label: "Streets",
    icon: "🛣️",
  },
};

export const IndianProximityMap: React.FC<IndianProximityMapProps> = ({
  userLat,
  userLon,
  radiusKm,
  points,
  onSelectPoint,
  selectedPointId,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const leafletMapRef = useRef<any>(null);
  const tileLayerRef = useRef<any>(null);
  const userMarkerRef = useRef<any>(null);
  const circleRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);

  const [tileStyle, setTileStyle] = useState<string>("hybrid");
  const [mapReady, setMapReady] = useState<boolean>(false);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current || leafletMapRef.current) return;

    let isMounted = true;

    import("leaflet").then((L) => {
      if (!isMounted || !mapContainerRef.current) return;

      // Fix default icons
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      });

      const map = L.map(mapContainerRef.current, {
        center: [userLat, userLon],
        zoom: 7,
        zoomControl: false,
        attributionControl: true,
      });

      leafletMapRef.current = map;

      // Initial Tile Layer
      tileLayerRef.current = L.tileLayer(TILE_STYLES[tileStyle].url, {
        maxZoom: 19,
        attribution: `© <a href="https://www.maptiler.com/copyright/" target="_blank">MapTiler</a> © <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>`,
      }).addTo(map);

      // Custom User Marker Icon
      const userHtml = `
        <div style="position:relative;display:flex;align-items:center;justify-content:center;width:40px;height:40px;">
          <div style="position:absolute;width:40px;height:40px;border-radius:50%;background:#06b6d4;opacity:0.6;animation:ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>
          <div style="width:24px;height:24px;border-radius:50%;background:#0891b2;border:3px solid #ffffff;box-shadow:0 4px 10px rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;color:#ffffff;font-size:12px;font-weight:bold;">📍</div>
        </div>
      `;
      const userIcon = L.divIcon({
        className: "custom-user-marker",
        html: userHtml,
        iconSize: [40, 40],
        iconAnchor: [20, 20],
      });

      userMarkerRef.current = L.marker([userLat, userLon], { icon: userIcon, zIndexOffset: 1000 })
        .addTo(map)
        .bindPopup(`
          <div style="font-family:system-ui,sans-serif;font-size:12px;padding:4px;">
            <div style="font-weight:800;color:#0891b2;margin-bottom:2px;">📍 YOUR LOCATION</div>
            <div style="font-family:monospace;font-size:11px;color:#334155;">${userLat.toFixed(4)}° N, ${userLon.toFixed(4)}° E</div>
            <div style="margin-top:4px;font-size:10px;color:#64748b;">Center of active proximity scan</div>
          </div>
        `);

      // Proximity Range Circle
      circleRef.current = L.circle([userLat, userLon], {
        radius: radiusKm * 1000,
        color: "#10b981",
        fillColor: "#10b981",
        fillOpacity: 0.12,
        weight: 2,
        dashArray: "6, 8",
      }).addTo(map);

      setMapReady(true);
    });

    return () => {
      isMounted = false;
      if (leafletMapRef.current) {
        leafletMapRef.current.remove();
        leafletMapRef.current = null;
      }
    };
  }, []);

  // Update Tile Style
  useEffect(() => {
    if (!leafletMapRef.current || !tileLayerRef.current) return;
    tileLayerRef.current.setUrl(TILE_STYLES[tileStyle].url);
  }, [tileStyle]);

  // Update User Marker, Circle, and Point Markers
  useEffect(() => {
    if (!leafletMapRef.current || !mapReady) return;

    import("leaflet").then((L) => {
      const map = leafletMapRef.current;
      if (!map) return;

      // Update User Marker Position
      if (userMarkerRef.current) {
        userMarkerRef.current.setLatLng([userLat, userLon]);
        userMarkerRef.current.setPopupContent(`
          <div style="font-family:system-ui,sans-serif;font-size:12px;padding:4px;">
            <div style="font-weight:800;color:#0891b2;margin-bottom:2px;">📍 YOUR LOCATION</div>
            <div style="font-family:monospace;font-size:11px;color:#334155;">${userLat.toFixed(4)}° N, ${userLon.toFixed(4)}° E</div>
            <div style="margin-top:4px;font-size:10px;color:#64748b;">Search Radius: ${radiusKm} km</div>
          </div>
        `);
      }

      // Update Circle
      if (circleRef.current) {
        circleRef.current.setLatLng([userLat, userLon]);
        circleRef.current.setRadius(radiusKm * 1000);
      }

      // Clear existing markers
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];

      // Add Point Markers
      points.forEach((pt) => {
        const inRange = pt.distanceKm <= radiusKm;
        const isSelected = selectedPointId === pt.id;

        let iconHtml = "";
        if (pt.type === "BASIN") {
          // Basin Icon
          iconHtml = `
            <div style="position:relative;display:flex;align-items:center;justify-content:center;width:32px;height:32px;">
              ${isSelected ? '<div style="position:absolute;width:40px;height:40px;border-radius:50%;background:#f59e0b;opacity:0.4;animation:pulse 1s infinite;"></div>' : ""}
              <div style="width:26px;height:26px;border-radius:50%;background:${inRange ? "#d97706" : "#64748b"};border:2px solid #ffffff;box-shadow:0 3px 8px rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;color:#ffffff;font-size:11px;font-weight:bold;">🛢️</div>
            </div>
          `;
        } else {
          // Well Icon
          const bgCol = inRange ? (isSelected ? "#059669" : "#10b981") : "#94a3b8";
          iconHtml = `
            <div style="position:relative;display:flex;align-items:center;justify-content:center;width:28px;height:28px;">
              ${inRange && isSelected ? '<div style="position:absolute;width:34px;height:34px;border-radius:50%;background:#10b981;opacity:0.5;animation:pulse 1s infinite;"></div>' : ""}
              <div style="width:20px;height:20px;border-radius:50%;background:${bgCol};border:2px solid #ffffff;box-shadow:0 2px 6px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;color:#ffffff;font-size:10px;font-weight:bold;">
                ${inRange ? "★" : "•"}
              </div>
            </div>
          `;
        }

        const icon = L.divIcon({
          className: "custom-pt-marker",
          html: iconHtml,
          iconSize: [32, 32],
          iconAnchor: [16, 16],
        });

        const marker = L.marker([pt.lat, pt.lon], { icon })
          .addTo(map)
          .bindPopup(`
            <div style="font-family:system-ui,sans-serif;font-size:12px;padding:6px;min-width:180px;">
              <div style="display:flex;align-items:center;justify-content:between;gap:6px;margin-bottom:4px;">
                <span style="font-weight:800;color:#0f172a;font-size:13px;">${pt.name}</span>
                <span style="font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px;background:${inRange ? "#ecfdf5;color:#059669;border:1px solid #a7f3d0" : "#f1f5f9;color:#64748b"};">
                  ${inRange ? "IN RANGE" : "OUTSIDE"}
                </span>
              </div>
              <div style="color:#64748b;font-size:11px;margin-bottom:2px;">
                ${pt.type === "WELL" ? `${pt.field || ""} · ${pt.operator}` : `${pt.operator}`}
              </div>
              <div style="font-family:monospace;font-weight:700;color:${inRange ? "#059669" : "#475569"};font-size:12px;margin:4px 0;">
                📍 ${pt.distanceKm.toFixed(1)} km from you
              </div>
              ${pt.depthM ? `<div style="font-size:10px;color:#475569;">Total Depth: <strong>${pt.depthM} m</strong></div>` : ""}
              ${pt.status ? `<div style="font-size:10px;color:#475569;">Status: <strong>${pt.status}</strong></div>` : ""}
            </div>
          `);

        marker.on("click", () => {
          if (onSelectPoint) onSelectPoint(pt);
        });

        markersRef.current.push(marker);
      });
    });
  }, [userLat, userLon, radiusKm, points, selectedPointId, mapReady]);

  // Center on user location
  const handleCenterOnUser = () => {
    if (!leafletMapRef.current) return;
    leafletMapRef.current.setView([userLat, userLon], 8, { animate: true });
  };

  // Fit bounds to circle and points
  const handleFitCircle = () => {
    if (!leafletMapRef.current || !circleRef.current) return;
    const bounds = circleRef.current.getBounds();
    leafletMapRef.current.fitBounds(bounds, { padding: [40, 40], animate: true });
  };

  return (
    <div className="relative w-full rounded-2xl overflow-hidden border border-slate-300 shadow-md bg-slate-900" style={{ height: 500 }}>
      {/* Map Canvas */}
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* Floating Style Selector */}
      <div className="absolute top-4 left-4 z-[400] flex items-center gap-1.5 bg-slate-900/90 backdrop-blur-md p-1.5 rounded-xl border border-slate-700 shadow-lg">
        {Object.entries(TILE_STYLES).map(([key, style]) => (
          <button
            key={key}
            onClick={() => setTileStyle(key)}
            className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
              tileStyle === key
                ? "bg-emerald-600 text-white shadow-sm"
                : "text-slate-300 hover:text-white hover:bg-slate-800"
            }`}
          >
            <span>{style.icon}</span>
            <span className="hidden sm:inline">{style.label}</span>
          </button>
        ))}
      </div>

      {/* Floating View Controls */}
      <div className="absolute top-4 right-4 z-[400] flex flex-col gap-2">
        <button
          onClick={handleCenterOnUser}
          title="Center on Your GPS Location"
          className="p-2.5 bg-slate-900/90 backdrop-blur-md rounded-xl border border-slate-700 text-cyan-400 hover:text-cyan-300 hover:bg-slate-800 shadow-lg transition-all flex items-center justify-center"
        >
          <Crosshair className="w-4 h-4" />
        </button>
        <button
          onClick={handleFitCircle}
          title="Fit View to Search Range Circle"
          className="p-2.5 bg-slate-900/90 backdrop-blur-md rounded-xl border border-slate-700 text-emerald-400 hover:text-emerald-300 hover:bg-slate-800 shadow-lg transition-all flex items-center justify-center"
        >
          <Compass className="w-4 h-4" />
        </button>
      </div>

      {/* Floating Map Legend */}
      <div className="absolute bottom-4 left-4 z-[400] bg-slate-900/90 backdrop-blur-md p-2.5 px-3 rounded-xl border border-slate-700 shadow-lg text-[11px] font-mono text-slate-300 flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-cyan-500 border border-white inline-block"></span>
          <span>Your GPS Position</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full border border-emerald-400 border-dashed bg-emerald-500/20 inline-block"></span>
          <span>{radiusKm} km Scan Radius</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"></span>
          <span>Wells in Range</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-slate-400 inline-block"></span>
          <span>Wells Outside</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-[10px]">🛢️</span>
          <span>Category-I Basin</span>
        </div>
      </div>
    </div>
  );
};
