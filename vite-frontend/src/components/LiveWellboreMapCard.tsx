import React, { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import {
  Navigation, Sliders, MapPin, AlertOctagon,
  Layers, Compass, ExternalLink, ShieldAlert
} from "lucide-react";

export interface WellData {
  id: string;
  name: string;
  field: string;
  lat: number;
  lng: number;
  depth: number;
  distanceKm: number;
  status: "active" | "critical" | "warning" | "safe";
  formation: string;
  dtwSimilarity?: number;
  historicalIncident?: string;
  remedy?: string;
}

interface LiveWellboreMapProps {
  currentDepthMd?: number;
  onSelectWell?: (well: WellData) => void;
}

export const LiveWellboreMapCard: React.FC<LiveWellboreMapProps> = ({
  currentDepthMd = 2413.5,
  onSelectWell,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);
  const circleRef = useRef<L.Circle | null>(null);
  const markersRef = useRef<L.Marker[]>([]);

  const [mapStyle, setMapStyle] = useState<"streets" | "hybrid" | "dark">("streets");
  const [proximityRadiusKm, setProximityRadiusKm] = useState<number>(20);
  const [selectedWell, setSelectedWell] = useState<WellData | null>(null);

  const MAPTILER_KEY = "o8Qhn3wgKrPhpfkNBiVU";
  const RIG_LAT = 27.352;
  const RIG_LNG = 95.319;

  const wellsData: WellData[] = [
    {
      id: "NHK-062",
      name: "Rig D-42 · NHK-062 (Active Rig)",
      field: "Duliajan Block (Assam-Arakan)",
      lat: RIG_LAT,
      lng: RIG_LNG,
      depth: currentDepthMd,
      distanceKm: 0.0,
      status: "active",
      formation: "Barail Coal-Shale",
      dtwSimilarity: 100,
      historicalIncident: "Current Rig · P0 Stuck-Pipe Warning at 2,413.5m",
      remedy: "Increase mud circulation from 550 to 680 gpm immediately",
    },
    {
      id: "NHK-014",
      name: "NHK-014 (Top Offset Match)",
      field: "Duliajan South",
      lat: 27.361,
      lng: 95.328,
      depth: 2850.0,
      distanceKm: 1.4,
      status: "critical",
      formation: "Barail Coal-Shale",
      dtwSimilarity: 98.4,
      historicalIncident: "Stuck Pipe at 2,420 m (6.5m deeper) · 14h NPT",
      remedy: "Overpull 180 klbf + 1.28 SG mud sweep to unseat jar",
    },
    {
      id: "NHK-019",
      name: "NHK-019 (Loss Offset)",
      field: "Nahorkatiya Block",
      lat: 27.291,
      lng: 95.278,
      depth: 2920.0,
      distanceKm: 7.8,
      status: "warning",
      formation: "Upper Tipam Sandstone",
      dtwSimilarity: 89.2,
      historicalIncident: "Lost Circulation at 2,385 m (30 bbl/hr)",
      remedy: "Pill 40 bbls Nutplug LCM + Reduced pump SPM",
    },
    {
      id: "NHK-007",
      name: "NHK-007 (Kick Offset)",
      field: "Duliajan West",
      lat: 27.338,
      lng: 95.301,
      depth: 2600.0,
      distanceKm: 3.2,
      status: "warning",
      formation: "Barail Formation",
      dtwSimilarity: 64.1,
      historicalIncident: "Minor Gas Influx (Kick) at 2,408 m",
      remedy: "Shut-in & Engineer's Method circulation (1.32 SG)",
    },
    {
      id: "NHK-021",
      name: "NHK-021 (Shale Offset)",
      field: "Moran Field",
      lat: 27.189,
      lng: 95.042,
      depth: 2450.0,
      distanceKm: 21.2,
      status: "safe",
      formation: "Girujan Clay",
      dtwSimilarity: 76.5,
      historicalIncident: "Swelling Shale & Tight Hole",
      remedy: "6% KCl mud + Glycol inhibitor",
    },
    {
      id: "JRH-005",
      name: "JRH-005 (Exploration)",
      field: "Jorhat Basin",
      lat: 26.751,
      lng: 94.215,
      depth: 3200.0,
      distanceKm: 42.0,
      status: "safe",
      formation: "Kopili Formation",
      dtwSimilarity: 48.0,
      historicalIncident: "Normal drilling without severe NPT",
      remedy: "Standard drilling program",
    },
  ];

  const getTileUrl = (style: "streets" | "hybrid" | "dark") => {
    switch (style) {
      case "hybrid":
        return `https://api.maptiler.com/maps/hybrid/{z}/{x}/{y}.jpg?key=${MAPTILER_KEY}`;
      case "dark":
        return `https://api.maptiler.com/maps/dataviz-dark/{z}/{x}/{y}.png?key=${MAPTILER_KEY}`;
      case "streets":
      default:
        return `https://api.maptiler.com/maps/streets-v2/{z}/{x}/{y}.png?key=${MAPTILER_KEY}`;
    }
  };

  // Initialize Leaflet Map
  useEffect(() => {
    const container = mapContainerRef.current;
    if (!container) return;

    // Reset container if previously initialized (React StrictMode protection)
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }
    (container as any)._leaflet_id = null;

    // Create Map
    const map = L.map(container, {
      center: [RIG_LAT, RIG_LNG],
      zoom: 12,
      zoomControl: false,
    });

    mapInstanceRef.current = map;

    // Zoom control at bottom right
    L.control.zoom({ position: "bottomright" }).addTo(map);

    // Initial Tile Layer
    const tileLayer = L.tileLayer(getTileUrl(mapStyle), {
      attribution:
        '&copy; <a href="https://www.maptiler.com/">MapTiler</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
      tileSize: 512,
      zoomOffset: -1,
    }).addTo(map);

    tileLayerRef.current = tileLayer;

    // Radius Circle around Active Rig
    const circle = L.circle([RIG_LAT, RIG_LNG], {
      radius: proximityRadiusKm * 1000,
      color: "#059669",
      weight: 2,
      dashArray: "6, 6",
      fillColor: "#10b981",
      fillOpacity: 0.12,
    }).addTo(map);

    circleRef.current = circle;

    // Create HTML Markers
    wellsData.forEach((well) => {
      let iconHtml = "";

      if (well.status === "active") {
        iconHtml = `
          <div style="position: relative; display: flex; align-items: center; justify-content: center; width: 44px; height: 44px; transform: translate(-50%, -50%);">
            <span style="position: absolute; width: 40px; height: 40px; border-radius: 9999px; background-color: #ef4444; opacity: 0.5; animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></span>
            <div style="width: 32px; height: 32px; border-radius: 12px; background-color: #064e3b; border: 2.5px solid #34d399; color: white; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: 800; font-size: 11px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);">
              RIG
            </div>
            <div style="position: absolute; top: -24px; white-space: nowrap; background-color: #0f172a; color: white; font-family: monospace; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 6px; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);">
              ${well.id} · Active
            </div>
          </div>
        `;
      } else {
        const isCritical = well.status === "critical";
        const isWarning = well.status === "warning";
        const bgColor = isCritical ? "#e11d48" : isWarning ? "#d97706" : "#059669";
        const badge = well.dtwSimilarity ? `${well.dtwSimilarity}%` : `${well.distanceKm.toFixed(1)}km`;

        iconHtml = `
          <div style="position: relative; display: flex; flex-direction: column; align-items: center; width: 36px; height: 36px; transform: translate(-50%, -50%); cursor: pointer;">
            <div style="width: 26px; height: 26px; border-radius: 10px; background-color: ${bgColor}; border: 2px solid white; color: white; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: 800; font-size: 10px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25);">
              ${well.id.substring(4)}
            </div>
            <div style="white-space: nowrap; background-color: rgba(255, 255, 255, 0.95); color: #0f172a; font-family: monospace; font-size: 9px; font-weight: 800; padding: 1px 4px; border-radius: 4px; border: 1px solid #cbd5e1; margin-top: 2px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
              ${badge}
            </div>
          </div>
        `;
      }

      const customIcon = L.divIcon({
        html: iconHtml,
        className: "custom-well-marker",
        iconSize: [0, 0],
      });

      const marker = L.marker([well.lat, well.lng], { icon: customIcon }).addTo(map);

      // Popup content
      const popupHtml = `
        <div style="font-family: inherit; padding: 4px; min-width: 190px;">
          <div style="font-weight: 800; font-size: 13px; color: #0f172a; margin-bottom: 2px;">
            ${well.name}
          </div>
          <div style="font-size: 11px; color: #64748b; margin-bottom: 6px;">
            ${well.field} · ${well.formation}
          </div>
          <div style="font-size: 11px; font-family: monospace; margin-bottom: 4px;">
            <strong>Depth:</strong> ${well.depth.toFixed(1)} m | <strong>Dist:</strong> ${well.distanceKm.toFixed(1)} km
          </div>
          ${
            well.dtwSimilarity
              ? `<div style="font-size: 11px; font-family: monospace; color: #4338ca; font-weight: 700; margin-bottom: 4px;">
                  DTW Similarity: ${well.dtwSimilarity}%
                </div>`
              : ""
          }
          <div style="font-size: 10px; color: #dc2626; font-weight: 600; line-height: 1.3; margin-top: 4px; border-top: 1px solid #e2e8f0; padding-top: 4px;">
            ${well.historicalIncident || "Normal offset profile"}
          </div>
        </div>
      `;

      marker.bindPopup(popupHtml, { closeButton: false, offset: [0, -10] });

      marker.on("click", () => {
        setSelectedWell(well);
        onSelectWell?.(well);
        map.flyTo([well.lat, well.lng], 13.5, { duration: 1.2 });
      });

      markersRef.current.push(marker);
    });

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update Tile Layer on Style Switch
  useEffect(() => {
    if (!mapInstanceRef.current || !tileLayerRef.current) return;
    tileLayerRef.current.setUrl(getTileUrl(mapStyle));
  }, [mapStyle]);

  // Update Proximity Radius Circle
  useEffect(() => {
    if (!circleRef.current) return;
    circleRef.current.setRadius(proximityRadiusKm * 1000);
  }, [proximityRadiusKm]);

  const handleRecenter = () => {
    mapInstanceRef.current?.flyTo([RIG_LAT, RIG_LNG], 12, { duration: 1.2 });
  };

  const filteredWellsCount = wellsData.filter((w) => w.distanceKm <= proximityRadiusKm).length;

  return (
    <div className="luxury-card rounded-3xl bg-white border border-slate-200/90 overflow-hidden flex flex-col h-full relative shadow-sm">
      {/* ── Top Floating Overlay Header ── */}
      <div className="absolute top-4 left-4 right-4 z-[1000] flex flex-wrap items-center justify-between gap-3 pointer-events-none">
        {/* Left: Active Rig Status Pill */}
        <div className="bg-white/95 backdrop-blur-md px-3.5 py-2 rounded-2xl border border-slate-200 shadow-md flex items-center gap-3 pointer-events-auto">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <span className="font-mono font-bold text-xs text-slate-800">
              NHK-062 · Duliajan
            </span>
          </div>

          <div className="h-3.5 w-px bg-slate-200" />

          <div className="text-[11px] font-mono text-slate-600">
            <span className="text-slate-400">DEPTH: </span>
            <span className="font-bold text-slate-900">{currentDepthMd.toFixed(1)} m</span>
          </div>

          <div className="h-3.5 w-px bg-slate-200" />

          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-md bg-rose-50 text-rose-600 border border-rose-200">
            BARAIL COAL-SHALE
          </span>
        </div>

        {/* Right: Map Style Switcher & Recenter */}
        <div className="flex items-center gap-2 pointer-events-auto">
          {/* Style Switcher */}
          <div className="bg-white/95 backdrop-blur-md p-1 rounded-2xl border border-slate-200 shadow-md flex items-center gap-1">
            <button
              onClick={() => setMapStyle("streets")}
              className={`px-2.5 py-1 text-[11px] font-semibold rounded-xl transition-all ${
                mapStyle === "streets"
                  ? "bg-slate-900 text-white font-bold shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Streets
            </button>
            <button
              onClick={() => setMapStyle("hybrid")}
              className={`px-2.5 py-1 text-[11px] font-semibold rounded-xl transition-all ${
                mapStyle === "hybrid"
                  ? "bg-slate-900 text-white font-bold shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Satellite
            </button>
            <button
              onClick={() => setMapStyle("dark")}
              className={`px-2.5 py-1 text-[11px] font-semibold rounded-xl transition-all ${
                mapStyle === "dark"
                  ? "bg-slate-900 text-white font-bold shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Dark Tech
            </button>
          </div>

          {/* Recenter Button */}
          <button
            onClick={handleRecenter}
            className="p-2 bg-white/95 backdrop-blur-md hover:bg-slate-100 rounded-2xl border border-slate-200 shadow-md text-slate-700 transition-all active:scale-95"
            title="Recenter to Active Rig"
          >
            <Navigation className="w-4 h-4 text-emerald-600" />
          </button>
        </div>
      </div>

      {/* ── Main Leaflet Container ── */}
      <div className="flex-1 w-full h-full min-h-[380px] relative z-0">
        <div ref={mapContainerRef} className="w-full h-full z-0" />
      </div>

      {/* ── Bottom Proximity & Selection Bar ── */}
      <div className="p-3 bg-white/95 backdrop-blur-md border-t border-slate-200/90 flex flex-wrap items-center justify-between gap-3 z-[1000] relative">
        {/* Proximity Radius Slider */}
        <div className="flex items-center gap-2.5 flex-1 min-w-[260px]">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700 flex-shrink-0">
            <Sliders className="w-3.5 h-3.5 text-emerald-600" />
            <span>Range:</span>
            <span className="font-mono text-emerald-700">{proximityRadiusKm} km</span>
          </div>

          <input
            type="range"
            min="5"
            max="45"
            step="1"
            value={proximityRadiusKm}
            onChange={(e) => setProximityRadiusKm(Number(e.target.value))}
            className="w-full max-w-[130px] accent-emerald-600 h-1.5 bg-slate-200 rounded-lg cursor-pointer"
          />

          <span className="text-[10px] font-mono font-bold text-slate-600 bg-slate-100 px-2 py-0.5 rounded-lg border border-slate-200/80 flex-shrink-0">
            {filteredWellsCount} Wells
          </span>
        </div>

        {/* Selected Well Quick Info Banner or Guide */}
        {selectedWell ? (
          <div className="flex items-center gap-2 bg-slate-50 px-2.5 py-1 rounded-xl border border-slate-200 text-xs">
            <span
              className={`w-2 h-2 rounded-full ${
                selectedWell.status === "critical"
                  ? "bg-rose-500 animate-ping"
                  : selectedWell.status === "warning"
                  ? "bg-amber-500"
                  : "bg-emerald-500"
              }`}
            />
            <span className="font-mono font-bold text-slate-900">{selectedWell.id}</span>
            <span className="text-slate-500 text-[10px]">({selectedWell.distanceKm.toFixed(1)} km)</span>
            {selectedWell.dtwSimilarity && (
              <span className="font-mono font-bold text-indigo-600 bg-indigo-50 px-1.5 py-0.2 rounded text-[10px]">
                DTW {selectedWell.dtwSimilarity}%
              </span>
            )}
            <button
              onClick={() => setSelectedWell(null)}
              className="text-slate-400 hover:text-slate-700 text-[10px] font-semibold ml-1"
            >
              ✕
            </button>
          </div>
        ) : (
          <div className="text-[10px] text-slate-500 flex items-center gap-1.5">
            <MapPin className="w-3 h-3 text-rose-500" />
            <span>Click any offset pin to view logs</span>
          </div>
        )}
      </div>
    </div>
  );
};
