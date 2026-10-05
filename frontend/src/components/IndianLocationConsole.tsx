"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import {
  Compass, MapPin, Navigation, ShieldAlert, AlertTriangle,
  Layers, CheckCircle2, ChevronRight, Activity, Globe, RefreshCw, Info
} from "lucide-react";
import type { MapPoint } from "./IndianProximityMap";

// Dynamic import for Leaflet map to ensure 100% client-side SSR safety
const IndianProximityMap = dynamic(
  () => import("./IndianProximityMap").then((m) => m.IndianProximityMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full rounded-2xl flex items-center justify-center bg-slate-900 border border-slate-700" style={{ height: 500 }}>
        <div className="text-center text-slate-400 text-xs font-mono">
          <div className="w-8 h-8 rounded-full border-2 border-emerald-500 border-t-transparent animate-spin mx-auto mb-2" />
          Loading Proximity Satellite Map…
        </div>
      </div>
    ),
  }
);

interface StratigraphicUnit {
  formation: string;
  typical_depth_m: string;
  lithology: string;
  drilling_hazard: string;
}

interface BasinIntelligence {
  basin_id: string;
  name: string;
  category: string;
  state: string;
  primary_operator: string;
  distance_km: number;
  geological_era: string;
  lithology_summary: string;
  stratigraphic_column: StratigraphicUnit[];
  regional_hazards: string[];
  typical_pp_gradient_sg: number;
  typical_fg_gradient_sg: number;
  recommended_mw_range_sg: string;
}

interface OffsetWell {
  well_id: string;
  well_name: string;
  field_name: string;
  basin: string;
  state: string;
  operator: string;
  surface_lat: number;
  surface_lon: number;
  kb_elevation_m: number;
  total_depth_md_m: number;
  status: string;
  discovery_year: number;
  distance_km: number;
  provenance_type: string;
  source: string;
}

interface RankedBasin {
  basin_id: string;
  name: string;
  state: string;
  distance_km: number;
  center_lat?: number;
  center_lon?: number;
  primary_operator: string;
}

interface LocationResponse {
  user_location: {
    latitude: number;
    longitude: number;
    within_oil_field_perimeter: boolean;
  };
  nearest_basin: BasinIntelligence;
  nearest_offset_well: OffsetWell;
  nearby_offset_wells: OffsetWell[];
  all_indian_wells_ranked?: OffsetWell[];
  all_indian_basins_ranked: RankedBasin[];
  operational_advisory: string;
  engineer_review_required: boolean;
  provenance_type: string;
}

const INDIAN_PRESETS = [
  { label: "Upper Assam (Nahorkatiya · OIL)", lat: 27.2831, lon: 95.3422, basin: "Assam-Arakan" },
  { label: "Moran Field (OIL)", lat: 27.1855, lon: 94.9312, basin: "Assam-Arakan" },
  { label: "Baghjan Play (OIL)", lat: 27.5812, lon: 95.3522, basin: "Assam-Arakan" },
  { label: "Digboi Heritage (OIL)", lat: 27.3800, lon: 95.6300, basin: "Assam-Arakan" },
  { label: "Barmer / Mangala (Cairn/ONGC)", lat: 25.8200, lon: 71.4200, basin: "Rajasthan" },
  { label: "Cambay / Ankleshwar (ONGC)", lat: 21.6312, lon: 73.0125, basin: "Gujarat" },
  { label: "KG Basin / Ravva (ONGC/RIL)", lat: 16.4800, lon: 82.2500, basin: "Andhra Offshore" },
  { label: "Mumbai High (ONGC)", lat: 19.4200, lon: 71.3300, basin: "Western Offshore" },
  { label: "Cauvery / Narimanam (ONGC)", lat: 10.8200, lon: 79.8400, basin: "Tamil Nadu" },
];

export const IndianLocationConsole: React.FC = () => {
  const [currentLat, setCurrentLat] = useState<number>(27.2831);
  const [currentLon, setCurrentLon] = useState<number>(95.3422);
  const [inputLat, setInputLat] = useState<string>("27.2831");
  const [inputLon, setInputLon] = useState<string>("95.3422");

  const [loading, setLoading] = useState<boolean>(false);
  const [locatingGps, setLocatingGps] = useState<boolean>(false);
  const [locationStatus, setLocationStatus] = useState<string | null>(null);
  const [data, setData] = useState<LocationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Proximity Search Range Radius (in km)
  const [radiusKm, setRadiusKm] = useState<number>(350);
  const [selectedPointId, setSelectedPointId] = useState<string | null>(null);

  const fetchLocationData = async (lat: number, lon: number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/india/locate?lat=${lat}&lon=${lon}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to resolve location`);
      const json: LocationResponse = await res.json();
      setData(json);
      setCurrentLat(lat);
      setCurrentLon(lon);
      setInputLat(lat.toString());
      setInputLon(lon.toString());
    } catch (err: any) {
      setError(err.message || "Failed to contact Indian location service");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLocationData(27.2831, 95.3422);
  }, []);

  const handleDetectGps = () => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser");
      return;
    }
    setLocatingGps(true);
    setLocationStatus("Requesting GPS coordinates from browser...");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = parseFloat(pos.coords.latitude.toFixed(4));
        const lon = parseFloat(pos.coords.longitude.toFixed(4));
        const acc = Math.round(pos.coords.accuracy);
        setLocationStatus(`GPS Locked: ${lat}°N, ${lon}°E (Accuracy ±${acc}m)`);
        setLocatingGps(false);
        fetchLocationData(lat, lon);
      },
      (err) => {
        setLocatingGps(false);
        let msg = "GPS permission denied or unavailable";
        if (err.code === 1) msg = "Location permission denied by user. Select an Indian Basin preset below.";
        else if (err.code === 2) msg = "GPS position unavailable. Select an Indian Basin preset below.";
        else if (err.code === 3) msg = "GPS request timed out. Select an Indian Basin preset below.";
        setError(msg);
        setLocationStatus(null);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
    );
  };

  const handleApplyCustom = (e: React.FormEvent) => {
    e.preventDefault();
    const lat = parseFloat(inputLat);
    const lon = parseFloat(inputLon);
    if (isNaN(lat) || isNaN(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      setError("Please enter valid Latitude (-90 to 90) and Longitude (-180 to 180)");
      return;
    }
    setLocationStatus(`Coordinates set to: ${lat}°N, ${lon}°E`);
    fetchLocationData(lat, lon);
  };

  // Build map points from wells & basins
  const wellsList = data?.all_indian_wells_ranked || data?.nearby_offset_wells || [];
  const basinsList = data?.all_indian_basins_ranked || [];

  const mapPoints: MapPoint[] = [
    // Wells
    ...wellsList.map((w) => ({
      id: w.well_id,
      name: w.well_name,
      type: "WELL" as const,
      lat: w.surface_lat,
      lon: w.surface_lon,
      operator: w.operator,
      distanceKm: w.distance_km,
      field: w.field_name,
      basin: w.basin,
      depthM: w.total_depth_md_m,
      status: w.status,
    })),
    // Basins
    ...basinsList.map((b) => ({
      id: b.basin_id,
      name: b.name,
      type: "BASIN" as const,
      lat: b.center_lat || (b.basin_id.includes("ASSAM") ? 27.35 : b.basin_id.includes("CAMBAY") ? 21.75 : b.basin_id.includes("BARMER") ? 25.85 : b.basin_id.includes("KG") ? 16.5 : b.basin_id.includes("MUMBAI") ? 19.42 : 10.85),
      lon: b.center_lon || (b.basin_id.includes("ASSAM") ? 95.30 : b.basin_id.includes("CAMBAY") ? 72.95 : b.basin_id.includes("BARMER") ? 71.45 : b.basin_id.includes("KG") ? 82.25 : b.basin_id.includes("MUMBAI") ? 71.33 : 79.80),
      operator: b.primary_operator,
      distanceKm: b.distance_km,
    })),
  ];

  const wellsWithinRadius = wellsList.filter((w) => w.distance_km <= radiusKm);
  const basinsWithinRadius = basinsList.filter((b) => b.distance_km <= radiusKm);

  return (
    <div className="space-y-6">
      {/* ── Top Header Banner (High Contrast) ── */}
      <div className="bg-gradient-to-r from-emerald-950 via-slate-900 to-amber-950 text-white rounded-2xl p-6 border border-emerald-800/40 shadow-xl">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5 mb-2">
              <span className="bg-emerald-500/30 text-emerald-300 border border-emerald-500/50 px-3 py-1 rounded-full text-xs font-mono font-bold flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5 text-emerald-400" />
                DGH NDR INDIAN BASINS & RIG LOCATOR
              </span>
              <span className="bg-amber-500/30 text-amber-300 border border-amber-500/50 px-2.5 py-0.5 rounded-full text-xs font-mono font-bold">
                OIL INDIA LIMITED
              </span>
            </div>
            <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-3">
              <span className="text-white drop-shadow-md">🇮🇳 Indian Origin & Location-Aware Drilling Intelligence</span>
            </h1>
            <p className="text-slate-200 text-xs mt-1.5 max-w-3xl leading-relaxed">
              Automatic GPS proximity resolution across Directorate General of Hydrocarbons (DGH) Category-I petroleum basins.
              Retrieves regional stratigraphy, calibrated offset discovery wells, pore pressure regimes, and downhole hazard advisories.
            </p>
          </div>

          {/* GPS Quick Action */}
          <div className="flex items-center gap-2 w-full lg:w-auto">
            <button
              onClick={handleDetectGps}
              disabled={locatingGps}
              className="flex-1 lg:flex-none flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg transition-all border border-emerald-400/50 disabled:opacity-60"
            >
              <Navigation className={`w-4 h-4 ${locatingGps ? "animate-spin text-emerald-200" : ""}`} />
              <span>{locatingGps ? "Detecting GPS..." : "📍 Detect My GPS Location"}</span>
            </button>
          </div>
        </div>

        {/* Location feedback status */}
        {locationStatus && (
          <div className="mt-3 py-2 px-3 rounded-lg bg-emerald-900/80 border border-emerald-400/60 text-emerald-100 text-xs font-mono flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-300 flex-shrink-0" />
            <span>{locationStatus}</span>
          </div>
        )}
        {error && (
          <div className="mt-3 py-2 px-3 rounded-lg bg-rose-950/80 border border-rose-500/60 text-rose-100 text-xs font-mono flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-300 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* ── Preset Indian Petroleum Fields & Coordinate Input ── */}
      <div className="card p-5 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-2">
            <MapPin className="w-4 h-4 text-emerald-600" />
            <span>Quick-Select Indian Petroleum Basins & OIL Operational Plays</span>
          </div>
          <span className="text-[11px] font-mono text-slate-500">DGH Category-I Fields</span>
        </div>

        <div className="flex flex-wrap gap-2">
          {INDIAN_PRESETS.map((preset) => {
            const isSelected = Math.abs(currentLat - preset.lat) < 0.01 && Math.abs(currentLon - preset.lon) < 0.01;
            return (
              <button
                key={preset.label}
                onClick={() => {
                  setLocationStatus(`Selected field: ${preset.label}`);
                  fetchLocationData(preset.lat, preset.lon);
                }}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all border flex items-center gap-1.5 ${
                  isSelected
                    ? "bg-emerald-700 text-white border-emerald-800 shadow-sm font-bold"
                    : "bg-slate-50 text-slate-700 border-slate-200 hover:bg-emerald-50 hover:border-emerald-300"
                }`}
              >
                <span className="text-[10px]">{preset.basin.includes("Assam") ? "🛢️" : "📍"}</span>
                <span>{preset.label}</span>
              </button>
            );
          })}
        </div>

        {/* Custom coordinates form */}
        <form onSubmit={handleApplyCustom} className="pt-2 border-t border-slate-100 flex flex-wrap items-center gap-3">
          <div className="text-xs font-medium text-slate-600">Manual GPS:</div>
          <div className="flex items-center gap-2">
            <label className="text-[11px] font-mono text-slate-500">Lat:</label>
            <input
              type="text"
              value={inputLat}
              onChange={(e) => setInputLat(e.target.value)}
              className="px-2.5 py-1 text-xs font-mono rounded-lg border border-slate-300 w-28 bg-slate-50 focus:bg-white focus:outline-emerald-500"
              placeholder="e.g. 27.2831"
            />
          </div>
          <div className="flex items-center gap-2">
            <label className="text-[11px] font-mono text-slate-500">Lon:</label>
            <input
              type="text"
              value={inputLon}
              onChange={(e) => setInputLon(e.target.value)}
              className="px-2.5 py-1 text-xs font-mono rounded-lg border border-slate-300 w-28 bg-slate-50 focus:bg-white focus:outline-emerald-500"
              placeholder="e.g. 95.3422"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-3.5 py-1 text-xs font-bold rounded-lg bg-slate-800 text-white hover:bg-slate-700 transition-colors disabled:opacity-60"
          >
            Apply Coordinates
          </button>
        </form>
      </div>

      {/* ── Interactive Proximity Map & Range Scanner Card ── */}
      <div className="card p-5 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-emerald-100 border border-emerald-300 flex items-center justify-center text-emerald-800 flex-shrink-0">
              <Compass className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-black text-slate-900 tracking-tight">
                Live Indian Petroleum Proximity Map
              </h3>
              <p className="text-[11px] text-slate-500">
                Interactive MapTiler satellite & terrain view centered at your GPS ({currentLat.toFixed(4)}°N, {currentLon.toFixed(4)}°E)
              </p>
            </div>
          </div>

          {/* Dynamic in-range stats badges */}
          <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
            <span className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span>{wellsWithinRadius.length} Wells within {radiusKm} km</span>
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-amber-50 text-amber-800 border border-amber-200 font-bold flex items-center gap-1.5">
              <span>🛢️ {basinsWithinRadius.length} Basins</span>
            </span>
          </div>
        </div>

        {/* Range Slider & Quick Radius Presets */}
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-700">Scan Radius:</span>
              <span className="text-sm font-mono font-black text-emerald-700 bg-white px-2 py-0.5 rounded border border-emerald-300">
                {radiusKm} km
              </span>
              <span className="text-[11px] text-slate-500">around your coordinates</span>
            </div>

            {/* Quick Presets */}
            <div className="flex flex-wrap items-center gap-1.5 text-xs font-mono">
              <span className="text-[10px] text-slate-400 uppercase font-sans mr-1">Quick Range:</span>
              {[50, 150, 350, 600, 1000, 2500].map((km) => (
                <button
                  key={km}
                  onClick={() => setRadiusKm(km)}
                  className={`px-2 py-0.5 rounded text-[11px] font-bold transition-all border ${
                    radiusKm === km
                      ? "bg-emerald-700 text-white border-emerald-800"
                      : "bg-white text-slate-700 border-slate-200 hover:bg-emerald-50 hover:border-emerald-300"
                  }`}
                >
                  {km >= 2500 ? "All India" : `${km} km`}
                </button>
              ))}
            </div>
          </div>

          {/* Slider input */}
          <input
            type="range"
            min={25}
            max={2500}
            step={25}
            value={radiusKm}
            onChange={(e) => setRadiusKm(parseInt(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-emerald-600"
          />
          <div className="flex justify-between text-[10px] font-mono text-slate-400">
            <span>25 km (Local Field)</span>
            <span>250 km (Sub-basin)</span>
            <span>600 km (Inter-state)</span>
            <span>1200 km (Regional)</span>
            <span>2500 km (Subcontinent)</span>
          </div>
        </div>

        {/* Embedded Live Map */}
        <IndianProximityMap
          userLat={currentLat}
          userLon={currentLon}
          radiusKm={radiusKm}
          points={mapPoints}
          selectedPointId={selectedPointId}
          onSelectPoint={(pt) => setSelectedPointId(pt.id)}
        />

        {/* Filtered Wells Grid inside Selected Radius */}
        <div className="space-y-2 pt-2">
          <div className="text-xs font-bold text-slate-700 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span>DGH NDR Indian Wells Within {radiusKm} km ({wellsWithinRadius.length} Available)</span>
            </span>
            <span className="text-[11px] font-mono text-slate-400">Click well to highlight on map</span>
          </div>

          {wellsWithinRadius.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2.5">
              {wellsWithinRadius.map((w) => {
                const isSelected = selectedPointId === w.well_id;
                return (
                  <button
                    key={w.well_id}
                    onClick={() => setSelectedPointId(w.well_id)}
                    className={`text-left p-3 rounded-xl border transition-all ${
                      isSelected
                        ? "bg-emerald-50 border-emerald-500 shadow-sm"
                        : "bg-slate-50/70 border-slate-200 hover:bg-white hover:border-slate-300"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-1 mb-1">
                      <span className="text-xs font-bold font-mono text-slate-900 truncate">
                        {w.well_name}
                      </span>
                      <span className="text-[10px] font-mono font-bold text-emerald-700 bg-white px-1.5 py-0.2 rounded border border-emerald-200 flex-shrink-0">
                        {w.distance_km} km
                      </span>
                    </div>
                    <div className="text-[10px] text-slate-500 truncate">
                      {w.field_name} · {w.operator}
                    </div>
                    <div className="flex items-center justify-between text-[10px] font-mono text-slate-600 mt-1 pt-1 border-t border-slate-200/60">
                      <span>TD: {w.total_depth_md_m} m</span>
                      <span className="text-emerald-700">{w.status.split("_")[0]}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-4 bg-slate-50 rounded-xl border border-dashed border-slate-300 text-xs text-slate-500">
              No Indian discovery wells within {radiusKm} km. Increase the search radius slider above (e.g. to 350 km or 600 km).
            </div>
          )}
        </div>
      </div>

      {/* ── Main Regional Stratigraphy & Geological Intelligence ── */}
      {data && (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Left Column: Nearest Basin & Operator Intelligence */}
          <div className="xl:col-span-1 space-y-6">
            {/* Primary Basin Card */}
            <div className="card p-5 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-[10px] font-mono font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 inline-block mb-1.5">
                    Nearest Indian Basin ({data.nearest_basin.distance_km} km)
                  </div>
                  <h2 className="text-base font-black text-slate-900 leading-snug">
                    {data.nearest_basin.name}
                  </h2>
                  <div className="text-xs text-slate-500 font-medium">
                    {data.nearest_basin.state}
                  </div>
                </div>

                <span
                  className={`text-[10px] font-mono font-bold px-2 py-1 rounded-full border ${
                    data.user_location.within_oil_field_perimeter
                      ? "bg-emerald-100 text-emerald-800 border-emerald-300"
                      : "bg-sky-100 text-sky-800 border-sky-300"
                  }`}
                >
                  {data.user_location.within_oil_field_perimeter ? "ACTIVE PERIMETER" : "REGIONAL CORRELATION"}
                </span>
              </div>

              {/* Attributes Grid */}
              <div className="grid grid-cols-2 gap-3 text-xs bg-slate-50 p-3.5 rounded-xl border border-slate-100 font-mono">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase block font-sans">Primary Operator</span>
                  <span className="font-bold text-slate-800">{data.nearest_basin.primary_operator}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 uppercase block font-sans">DGH Classification</span>
                  <span className="font-bold text-slate-800">{data.nearest_basin.category.split(" ")[0]}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 uppercase block font-sans">Pore Pressure Baseline</span>
                  <span className="font-bold text-emerald-700">{data.nearest_basin.typical_pp_gradient_sg} SG</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 uppercase block font-sans">Fracture Gradient</span>
                  <span className="font-bold text-rose-700">{data.nearest_basin.typical_fg_gradient_sg} SG</span>
                </div>
                <div className="col-span-2">
                  <span className="text-[10px] text-slate-400 uppercase block font-sans">Safe Mud Weight Window</span>
                  <span className="font-bold text-slate-800">{data.nearest_basin.recommended_mw_range_sg}</span>
                </div>
              </div>

              {/* Lithological Summary */}
              <div className="text-xs text-slate-600 bg-amber-50/60 p-3 rounded-xl border border-amber-200/60">
                <div className="font-bold text-amber-900 mb-1 flex items-center gap-1.5">
                  <Info className="w-3.5 h-3.5 text-amber-700" />
                  <span>Geological Character & Basin Era</span>
                </div>
                <p className="text-[11px] leading-relaxed text-amber-950">
                  <span className="font-semibold text-amber-800">{data.nearest_basin.geological_era}:</span> {data.nearest_basin.lithology_summary}.
                </p>
              </div>

              {/* Regional Hazards list */}
              <div>
                <div className="text-xs font-bold text-slate-800 mb-2 flex items-center gap-1.5">
                  <ShieldAlert className="w-4 h-4 text-rose-600" />
                  <span>Documented Regional Hazards (DGH NDR)</span>
                </div>
                <ul className="space-y-1.5 text-xs">
                  {data.nearest_basin.regional_hazards.map((hz, idx) => (
                    <li key={idx} className="flex items-start gap-2 bg-rose-50/50 p-2 rounded-lg border border-rose-100 text-rose-900 text-[11px]">
                      <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mt-1.5 flex-shrink-0" />
                      <span>{hz}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* All Indian Basins Distance Ranking */}
            <div className="card p-5 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-3">
              <div className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
                <Compass className="w-4 h-4 text-slate-600" />
                <span>Indian Basins Proximity Hierarchy</span>
              </div>
              <div className="divide-y divide-slate-100 text-xs">
                {data.all_indian_basins_ranked.map((b) => (
                  <div key={b.basin_id} className="py-2.5 flex items-center justify-between">
                    <div>
                      <div className="font-semibold text-slate-800">{b.name}</div>
                      <div className="text-[10px] text-slate-500">{b.state} · {b.primary_operator}</div>
                    </div>
                    <span className="font-mono font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded text-[11px] border border-emerald-200">
                      {b.distance_km} km
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column (2 cols): Stratigraphy & Offset Discovery Wells */}
          <div className="xl:col-span-2 space-y-6">
            {/* Operational Advisory Banner */}
            <div className="p-4 rounded-xl bg-slate-900 text-white border border-slate-800 flex items-start gap-3 shadow-md">
              <ShieldAlert className="w-5 h-5 text-amber-400 mt-0.5 flex-shrink-0" />
              <div className="space-y-1">
                <div className="text-xs font-bold text-amber-300 font-mono">
                  OPERATIONAL DRILLING ADVISORY · {data.nearest_basin.primary_operator}
                </div>
                <div className="text-xs text-slate-200 leading-relaxed">
                  {data.operational_advisory}
                </div>
                <div className="text-[10px] font-mono text-emerald-400 pt-1">
                  engineer_review_required = true · autonomous_control = false · DGH National Data Repository
                </div>
              </div>
            </div>

            {/* Regional Stratigraphic Column Table */}
            <div className="card p-5 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Layers className="w-4 h-4 text-emerald-600" />
                  <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                    {data.nearest_basin.name} Stratigraphic Column
                  </h3>
                </div>
                <span className="text-[10px] font-mono text-slate-500 font-bold">
                  {data.nearest_basin.stratigraphic_column.length} Units Logged
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border border-slate-200 rounded-xl overflow-hidden">
                  <thead className="bg-slate-100/80 font-mono text-[11px] text-slate-700">
                    <tr>
                      <th className="py-2.5 px-3 border-b">Formation</th>
                      <th className="py-2.5 px-3 border-b">Depth Interval</th>
                      <th className="py-2.5 px-3 border-b">Lithology</th>
                      <th className="py-2.5 px-3 border-b text-rose-800">Operational Hazard</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-sans">
                    {data.nearest_basin.stratigraphic_column.map((unit, i) => (
                      <tr key={i} className="hover:bg-slate-50/80 transition-colors">
                        <td className="py-2.5 px-3 font-bold text-slate-900 font-mono text-[11px]">
                          {unit.formation}
                        </td>
                        <td className="py-2.5 px-3 font-mono text-[11px] text-slate-600 whitespace-nowrap">
                          {unit.typical_depth_m}
                        </td>
                        <td className="py-2.5 px-3 text-slate-700 text-[11px]">
                          {unit.lithology}
                        </td>
                        <td className="py-2.5 px-3 font-medium text-[11px] text-rose-700 bg-rose-50/30">
                          {unit.drilling_hazard}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Proximity-Ranked Offset Discovery Wells */}
            <div className="card p-5 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Compass className="w-4 h-4 text-emerald-600" />
                  <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                    Nearest Indian Offset Wells (DGH NDR)
                  </h3>
                </div>
                <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  Sorted by Great-Circle Distance
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {data.nearby_offset_wells.map((well) => (
                  <div
                    key={well.well_id}
                    className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-white hover:shadow-md transition-all space-y-2"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="text-xs font-bold text-slate-900 font-mono">{well.well_name}</div>
                        <div className="text-[10px] text-slate-500 font-medium">
                          {well.field_name} · {well.operator}
                        </div>
                      </div>
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300">
                        {well.distance_km} km away
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-2 text-[10px] font-mono pt-1 border-t border-slate-200/60 text-slate-600">
                      <div>
                        <span className="text-slate-400 block font-sans text-[9px]">TOTAL DEPTH</span>
                        <span className="font-bold">{well.total_depth_md_m} m</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block font-sans text-[9px]">DISCOVERY</span>
                        <span className="font-bold">{well.discovery_year}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block font-sans text-[9px]">STATUS</span>
                        <span className="font-bold text-emerald-700">{well.status.split("_")[0]}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
