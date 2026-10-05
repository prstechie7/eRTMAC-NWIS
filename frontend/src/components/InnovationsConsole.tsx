"use client";

import React, { useState, useEffect } from "react";
import { 
  Activity, DollarSign, Map as MapIcon, FileText, Bot, AlertTriangle, 
  RefreshCw, TrendingDown, Clock, ShieldAlert, Cpu, CheckCircle2, AlertOctagon,
  MessageSquare
} from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, ReferenceLine } from "recharts";

interface InnovationsConsoleProps {
  currentDepthMd: number;
}

export const InnovationsConsole: React.FC<InnovationsConsoleProps> = ({ currentDepthMd }) => {
  const [data, setData] = useState<any>(null);
  const [ddr, setDdr] = useState<any>(null);
  const [heatmap, setHeatmap] = useState<any>(null);
  const [copilotQuery, setCopilotQuery] = useState("");
  const [copilotResponse, setCopilotResponse] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [copilotLoading, setCopilotLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // 1. Fetch main innovations dashboard (A2, A7, etc)
        const dashRes = await fetch(`http://localhost:8000/api/v1/innovations/dashboard?depth_md_m=${currentDepthMd}`);
        const dashData = await dashRes.json();
        
        // 2. Fetch Auto DDR (A13)
        const ddrRes = await fetch(`http://localhost:8000/api/v1/innovations/generate-ddr?depth_end_m=${currentDepthMd}`);
        const ddrData = await ddrRes.json();

        // 3. Fetch Hazard Heatmap (A8)
        const heatRes = await fetch(`http://localhost:8000/api/v1/innovations/hazard-heatmap`);
        const heatData = await heatRes.json();

        setData(dashData);
        setDdr(ddrData);
        setHeatmap(heatData);
      } catch (e) {
        console.error("Failed to load innovations", e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [currentDepthMd]);

  const handleCopilotSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!copilotQuery.trim()) return;
    
    setCopilotLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/innovations/copilot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: copilotQuery, depth_md_m: currentDepthMd })
      });
      const data = await res.json();
      setCopilotResponse(data);
    } catch (e) {
      console.error(e);
    } finally {
      setCopilotLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px] text-slate-500">
        <RefreshCw className="w-8 h-8 animate-spin text-emerald-500 mb-4" />
        <p>Loading Deepmind Top 5 Innovations...</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-[1720px] mx-auto pb-20">
      
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <Cpu className="w-6 h-6 text-emerald-600" />
            Top 5 Drilling Innovations (SIH26121)
          </h2>
          <p className="text-slate-500 mt-1">Real-time intelligent decision support for {data?.formation}</p>
        </div>
        <div className="bg-emerald-50 text-emerald-700 px-4 py-2 rounded-lg font-mono text-sm font-semibold border border-emerald-200">
          MD: {currentDepthMd.toFixed(1)}m | TVD: {data?.depth_tvd_m.toFixed(1)}m
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* 1. NPT Cost Quantification (A7) */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 col-span-1 flex flex-col">
          <div className="flex items-center gap-2 mb-4 text-rose-700">
            <DollarSign className="w-5 h-5" />
            <h3 className="font-bold text-slate-800">Financial NPT Exposure (A7)</h3>
          </div>
          <div className="bg-rose-50 border border-rose-100 rounded-lg p-4 mb-4">
            <p className="text-sm text-rose-600 font-semibold mb-1">P50 Expected Cost</p>
            <p className="text-3xl font-black text-rose-700">
              {data?.npt_cost?.financial_exposure?.p50_expected}
            </p>
            <p className="text-xs text-rose-500 mt-2 uppercase tracking-wide font-mono">
              Hazard: {data?.npt_cost?.hazard_type}
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-50 rounded p-3 border border-slate-100">
              <p className="text-xs text-slate-500">P10 Optimistic</p>
              <p className="text-sm font-bold text-slate-700">{data?.npt_cost?.financial_exposure?.p10_optimistic}</p>
            </div>
            <div className="bg-slate-50 rounded p-3 border border-slate-100">
              <p className="text-xs text-slate-500">P90 Worst Case</p>
              <p className="text-sm font-bold text-slate-700">{data?.npt_cost?.financial_exposure?.p90_worst_case}</p>
            </div>
          </div>
          <p className="text-xs text-slate-500 mt-4 leading-relaxed">
            {data?.npt_cost?.summary}
          </p>
        </div>

        {/* 2. D-Exponent Pore Pressure (A2) */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 col-span-1 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2 text-indigo-700">
              <Activity className="w-5 h-5" />
              <h3 className="font-bold text-slate-800">D-Exponent Pore Pressure (A2)</h3>
            </div>
            <div className={`px-3 py-1 rounded-full text-xs font-bold ${
              data?.pore_pressure?.alert ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'
            }`}>
              {data?.pore_pressure?.pp_status}
            </div>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="border border-slate-100 rounded-lg p-3 bg-slate-50">
              <p className="text-xs text-slate-500">Predicted PP</p>
              <p className="text-xl font-bold text-slate-800">{data?.pore_pressure?.pp_predicted_sg.toFixed(3)} SG</p>
            </div>
            <div className="border border-slate-100 rounded-lg p-3 bg-slate-50">
              <p className="text-xs text-slate-500">Current MW</p>
              <p className="text-xl font-bold text-indigo-700">{data?.pore_pressure?.mud_weight_sg.toFixed(2)} SG</p>
            </div>
            <div className="border border-slate-100 rounded-lg p-3 bg-slate-50">
              <p className="text-xs text-slate-500">Kick Margin</p>
              <p className={`text-xl font-bold ${data?.pore_pressure?.kick_margin_sg < 0.05 ? 'text-rose-600' : 'text-emerald-600'}`}>
                {data?.pore_pressure?.kick_margin_sg.toFixed(3)} SG
              </p>
            </div>
            <div className="border border-slate-100 rounded-lg p-3 bg-slate-50">
              <p className="text-xs text-slate-500">D-Exponent</p>
              <p className="text-xl font-bold text-slate-700">{data?.pore_pressure?.d_exponent_raw.toFixed(2)}</p>
            </div>
          </div>

          <div className="bg-indigo-50 border border-indigo-100 rounded-lg p-4 flex gap-3 items-start">
            <AlertTriangle className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-indigo-900">Recommendation</p>
              <p className="text-sm text-indigo-700 mt-1">{data?.pore_pressure?.recommended_action}</p>
            </div>
          </div>
        </div>

      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* 3. Multi-Agent Copilot (A12) */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 flex flex-col h-[500px]">
          <div className="flex items-center gap-2 mb-4 text-purple-700">
            <Bot className="w-5 h-5" />
            <h3 className="font-bold text-slate-800">Multi-Agent Copilot (A12)</h3>
          </div>
          
          <div className="flex-1 bg-slate-50 border border-slate-200 rounded-lg p-4 overflow-y-auto mb-4 flex flex-col gap-4">
            {copilotResponse ? (
              <div className="space-y-4">
                <div className="bg-white border border-slate-200 p-3 rounded-lg rounded-tr-none self-end max-w-[80%] ml-auto">
                  <p className="text-sm text-slate-700">{copilotResponse.query}</p>
                </div>
                
                {/* Reasoning Steps */}
                <div className="space-y-2">
                  <p className="text-xs font-semibold text-slate-500 uppercase">Agent Reasoning</p>
                  {copilotResponse.reasoning_steps.map((step: any, i: number) => (
                    <div key={i} className="flex gap-2 items-start text-xs text-slate-600 bg-slate-100 p-2 rounded border border-slate-200">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 mt-0.5 flex-shrink-0" />
                      <p><span className="font-semibold">{step.agent}:</span> {step.output}</p>
                    </div>
                  ))}
                </div>

                {/* Synthesis */}
                <div className="bg-purple-50 border border-purple-200 p-4 rounded-lg rounded-tl-none self-start max-w-[95%] shadow-sm">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-4 h-4 text-purple-600" />
                    <span className="text-xs font-bold text-purple-800 uppercase">Copilot Synthesis</span>
                  </div>
                  <p className="text-sm text-purple-900 leading-relaxed font-medium">
                    {copilotResponse.synthesis}
                  </p>
                  {copilotResponse.alert && (
                    <div className="mt-3 inline-flex items-center gap-1.5 bg-rose-100 text-rose-700 px-2 py-1 rounded text-xs font-bold">
                      <AlertOctagon className="w-3.5 h-3.5" /> High Risk Detected
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-slate-400">
                <MessageSquare className="w-10 h-10 mb-3 opacity-20" />
                <p className="text-sm">Ask the drilling copilot for recommendations...</p>
                <div className="flex gap-2 mt-4">
                  <button onClick={() => setCopilotQuery("What is the stuck pipe risk?")} className="text-[10px] bg-slate-200 hover:bg-slate-300 text-slate-600 px-2 py-1 rounded-full">Stuck pipe risk?</button>
                  <button onClick={() => setCopilotQuery("Is the mud weight safe?")} className="text-[10px] bg-slate-200 hover:bg-slate-300 text-slate-600 px-2 py-1 rounded-full">Mud weight safe?</button>
                </div>
              </div>
            )}
          </div>

          <form onSubmit={handleCopilotSubmit} className="flex gap-2">
            <input 
              type="text" 
              value={copilotQuery}
              onChange={e => setCopilotQuery(e.target.value)}
              placeholder="E.g., Should I pull out of hole now?"
              className="flex-1 border border-slate-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
            />
            <button 
              type="submit"
              disabled={copilotLoading}
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50 flex items-center justify-center min-w-[80px]"
            >
              {copilotLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : "Ask"}
            </button>
          </form>
        </div>

        {/* 4 & 5. DDR (A13) & Hazard Heatmap (A8) */}
        <div className="space-y-6 flex flex-col h-[500px]">
          
          {/* Auto DDR */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 flex-1 overflow-hidden flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-sky-700">
                <FileText className="w-5 h-5" />
                <h3 className="font-bold text-slate-800">Auto DDR Generator (A13)</h3>
              </div>
              <button className="text-xs bg-sky-50 text-sky-700 font-bold px-3 py-1 rounded border border-sky-200 hover:bg-sky-100">
                Download PDF
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
              {ddr && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-2 text-xs border-b border-slate-100 pb-3">
                    <div><span className="text-slate-500">Report Date:</span> <span className="font-bold">{ddr.report.header.report_date}</span></div>
                    <div><span className="text-slate-500">Well:</span> <span className="font-bold">{ddr.report.header.well_name}</span></div>
                    <div><span className="text-slate-500">Footage:</span> <span className="font-bold">{ddr.report.header.footage_drilled_m} m</span></div>
                    <div><span className="text-slate-500">Rig:</span> <span className="font-bold">{ddr.report.header.rig_name}</span></div>
                  </div>
                  
                  <div>
                    <h4 className="text-xs font-bold text-slate-700 uppercase mb-2">Drill Ahead Summary</h4>
                    <p className="text-sm text-slate-600 bg-slate-50 p-3 rounded border border-slate-100">
                      Drilled {ddr.report.drill_ahead_summary.formation_drilled} at avg ROP of {ddr.report.drill_ahead_summary.avg_rop_mhr} m/hr. 
                      Parameters maintained at {ddr.report.drill_ahead_summary.avg_wob_klbs} kLbs WOB, {ddr.report.drill_ahead_summary.avg_rpm} RPM.
                    </p>
                  </div>

                  <div>
                    <h4 className="text-xs font-bold text-slate-700 uppercase mb-2">Look-Ahead Advisory</h4>
                    <p className="text-sm text-amber-700 bg-amber-50 p-3 rounded border border-amber-200">
                      {ddr.report.lookahead_advisory.hazard_warning}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Hazard Heatmap (A8) Preview */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 h-[200px] flex flex-col relative overflow-hidden group cursor-pointer">
            <div className="flex items-center gap-2 mb-2 relative z-10">
              <MapIcon className="w-5 h-5 text-emerald-600" />
              <h3 className="font-bold text-slate-800">Basin Hazard Heatmap (A8)</h3>
            </div>
            <p className="text-xs text-slate-500 mb-3 relative z-10">
              {heatmap?.total_incidents_mapped} historical incidents mapped across {heatmap?.formations_analyzed} formations in Nahorkatiya.
            </p>
            
            {/* Visual mock of map */}
            <div className="absolute -bottom-8 -right-8 w-64 h-64 bg-emerald-100/50 rounded-full blur-3xl group-hover:bg-emerald-200/50 transition-colors" />
            <div className="absolute top-10 left-10 w-32 h-32 bg-amber-100/50 rounded-full blur-2xl group-hover:bg-amber-200/50 transition-colors" />
            
            <div className="mt-auto relative z-10 flex gap-2">
              <span className="text-xs font-bold bg-white/80 backdrop-blur border border-slate-200 px-2 py-1 rounded shadow-sm">Differential Sticking (High)</span>
              <span className="text-xs font-bold bg-white/80 backdrop-blur border border-slate-200 px-2 py-1 rounded shadow-sm">Gas Kicks (Med)</span>
            </div>
          </div>

        </div>
      </div>

    </div>
  );
};
