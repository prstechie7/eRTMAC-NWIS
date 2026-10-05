import React, { useState, useEffect } from "react";
import gsap from "gsap";
import { Sidebar, type ViewTab } from "./components/Sidebar";
import { TopBar } from "./components/TopBar";
import { MetricCards } from "./components/MetricCards";
import { LiveWellboreMapCard } from "./components/LiveWellboreMapCard";
import { RadialGaugeCard } from "./components/RadialGaugeCard";
import { HistoricalDTWCard } from "./components/HistoricalDTWCard";
import { IntelligenceStationCard } from "./components/IntelligenceStationCard";
import { IndianBasinsMapCard } from "./components/IndianBasinsMapCard";
import { ModelCatalogModal } from "./components/ModelCatalogModal";
import { Sparkles, ShieldAlert, ArrowUpRight, Activity } from "lucide-react";

export function App() {
  const [activeTab, setActiveTab] = useState<ViewTab>("dashboard");
  const [isCatalogOpen, setIsCatalogOpen] = useState(false);
  const [currentDepth, setCurrentDepth] = useState(2413.5);
  const [rop, setRop] = useState(14.2);
  const [stuckRisk, setStuckRisk] = useState(83.5);
  const [notification, setNotification] = useState<string | null>(null);

  // GSAP Entrance Animations
  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from(".forest-hero-card", {
        scale: 0.96,
        opacity: 0,
        duration: 0.8,
        ease: "power3.out",
      });

      gsap.from(".luxury-card", {
        y: 20,
        opacity: 0,
        duration: 0.6,
        stagger: 0.06,
        ease: "power2.out",
      });
    });

    return () => ctx.revert();
  }, [activeTab]);

  // Subtle telemetry pulse
  useEffect(() => {
    const interval = setInterval(() => {
      // Micro-telemetry drift simulation
      setCurrentDepth((prev) => +(prev + 0.02).toFixed(2));
      setRop((prev) => +(14.2 + (Math.random() * 0.4 - 0.2)).toFixed(1));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleActionToast = (msg: string) => {
    setNotification(msg);
    setTimeout(() => setNotification(null), 3500);
  };

  return (
    <div className="flex bg-[#F4F6F8] min-h-screen text-slate-800 font-sans antialiased selection:bg-emerald-500 selection:text-white">
      {/* ── Left Sidebar (Donezo / Shopeers Style) ── */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={(tab) => {
          setActiveTab(tab);
          handleActionToast(`Switched view to ${tab.toUpperCase().replace("-", " ")}`);
        }}
        activeWellName="NHK-062 (Duliajan)"
      />

      {/* ── Main Content Area ── */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Bar with Search & Ticker */}
        <TopBar
          activeWellName="NHK-062 · Duliajan Block"
          depthMd={currentDepth}
          ropValue={rop}
          stuckRisk={stuckRisk}
          onOpenModelCatalog={() => setIsCatalogOpen(true)}
          onOpenAddScenario={() =>
            handleActionToast("Scenario simulation module launched: NHK-062 sidetrack")
          }
        />

        {/* Dynamic Toast Notification */}
        {notification && (
          <div className="fixed bottom-6 right-6 z-50 bg-slate-900 text-white px-4 py-2.5 rounded-2xl shadow-2xl flex items-center gap-2.5 text-xs font-semibold animate-in slide-in-from-bottom-3 duration-200">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>{notification}</span>
          </div>
        )}

        {/* ── Main Dashboard Body ── */}
        <main className="p-8 space-y-7 max-w-7xl mx-auto w-full">
          {/* Welcome Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                  {activeTab === "dashboard" && "Real-Time Drilling Intelligence"}
                  {activeTab === "ml-station" && "14-Model Enterprise ML Reasoning"}
                  {activeTab === "3d-wellbore" && "Live Field Wellbore Proximity Map"}
                  {activeTab === "ai-assistant" && "Gemini 2.5 Flash Grounded AI Evidence"}
                  {activeTab === "indian-basins" && "Indian Basins & NDR Proximity Scanner"}
                  {activeTab === "real-data" && "Live WITSML Sensor Telemetry Hub"}
                  {activeTab === "telemetry" && "1Hz Mud Logging Stream Analysis"}
                  {activeTab === "doghouse" && "Doghouse Touchscreen Interface"}
                </h1>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold">
                  RIG D-42
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium mt-1">
                Oil India Limited · Real-Time Near Wellbore Intelligence System (eRTMAC-NWIS)
              </p>
            </div>

            {/* Quick Action Badges */}
            <div className="flex items-center gap-2 text-xs">
              <button
                onClick={() => setIsCatalogOpen(true)}
                className="px-3.5 py-1.5 bg-white border border-slate-200/90 hover:bg-slate-50 rounded-xl text-slate-700 font-semibold shadow-xs transition-all flex items-center gap-1.5"
              >
                <Sparkles className="w-3.5 h-3.5 text-purple-600" />
                <span>14 ML Models</span>
              </button>

              <button
                onClick={() =>
                  handleActionToast("DTW trajectory synchronization complete with NHK-014")
                }
                className="px-3.5 py-1.5 bg-emerald-50 border border-emerald-200 hover:bg-emerald-100/70 rounded-xl text-emerald-800 font-bold transition-all flex items-center gap-1.5"
              >
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span>NHK-014 Aligned (98.4%)</span>
              </button>
            </div>
          </div>

          {/* ── Section 1: Hero Metric Cards Row (Donezo / Shopeers Style) ── */}
          <MetricCards
            stuckRisk={stuckRisk}
            dtwTopWell="NHK-014"
            dtwSimilarity={98.4}
            ropDeviation={-33.0}
            activeWellsCount={24}
            onSelectCard={(id) => handleActionToast(`Selected metric card: ${id}`)}
          />

          {/* ── Section 2: Core Visual Section (Live Map + Donezo Radial Gauge) ── */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
            {/* Left 7 Columns: Live Interactive Map (MapLibre + MapTiler Satellite/Streets) */}
            <div className="lg:col-span-7 h-[460px]">
              <LiveWellboreMapCard
                currentDepthMd={currentDepth}
                onSelectWell={(well) =>
                  handleActionToast(`Inspecting offset well ${well.name} (${well.distanceKm.toFixed(1)} km)`)
                }
              />
            </div>

            {/* Right 5 Columns: Donezo-Style Segmented Radial Gauge */}
            <div className="lg:col-span-5 h-[460px]">
              <RadialGaugeCard
                riskPercentage={stuckRisk}
                consensusScore={97.0}
                primaryMechanism="Mechanical Sticking · Barail Coal-Shale"
                onExploreRemedy={() => {
                  setActiveTab("ai-assistant");
                  handleActionToast("Navigating to AI Evidence mitigation plan");
                }}
              />
            </div>
          </div>

          {/* ── Section 3: Intelligence & Historical Alignment Row ── */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left 6 Columns: Shopeers-style DTW Historical Offset Table */}
            <div className="lg:col-span-6">
              <HistoricalDTWCard
                onSelectWell={(wellId) =>
                  handleActionToast(`Overlaying trajectory & logs for ${wellId}`)
                }
              />
            </div>

            {/* Right 6 Columns: NWIS Intelligence Station & AI Reasoning */}
            <div className="lg:col-span-6">
              <IntelligenceStationCard />
            </div>
          </div>

          {/* ── Section 4: Indian Basin & Offset Proximity Scanner ── */}
          <IndianBasinsMapCard
            onSelectWell={(well) =>
              handleActionToast(`Selected well ${well.name} (${well.distanceKm.toFixed(1)} km)`)
            }
          />
        </main>
      </div>

      {/* ── 14 ML Model Catalog Modal ── */}
      <ModelCatalogModal
        isOpen={isCatalogOpen}
        onClose={() => setIsCatalogOpen(false)}
      />
    </div>
  );
}
export default App;
