"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Sparkles, Send, Bot, User, ShieldAlert, BookOpen, Clock,
  CheckCircle2, AlertTriangle, ArrowRight, CornerDownLeft, RotateCcw
} from "lucide-react";

interface QuerySuggestion {
  category: string;
  query: string;
  context: string;
}

interface CitedEvidence {
  well_name: string;
  event_type: string;
  formation_name: string;
  depth_start_m: number;
  depth_end_m: number;
  npt_hours: number;
  root_cause: string;
  mitigation_action: string;
  source_document: string;
  surface_distance_m?: number;
  tsd_difference_m?: number;
}

interface SearchResponse {
  query: string;
  answer: string;
  model: string;
  grounded_on: string;
  matching_events_count: number;
  cited_evidence: CitedEvidence[];
  suggested_followups: string[];
  engineer_review_required: boolean;
  autonomous_control: boolean;
}

interface ChatMessage {
  id: string;
  sender: "user" | "ai";
  text: string;
  timestamp: string;
  model?: string;
  citedEvidence?: CitedEvidence[];
  suggestedFollowups?: string[];
}

export const GroundedAIAssistant: React.FC<{ activeDepthMd?: number }> = ({
  activeDepthMd = 2410.0,
}) => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<QuerySuggestion[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Fetch Suggestions on mount
  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/intelligence/query-suggestions`)
      .then((res) => res.json())
      .then((data: QuerySuggestion[]) => {
        setSuggestions(data);
      })
      .catch((err) => console.error("Error fetching suggestions:", err));

    // Initial greeting message
    setMessages([
      {
        id: "msg-0",
        sender: "ai",
        text: `**Welcome to eRTMAC-NWIS Grounded AI Assistant (Powered by Google Gemini 2.5 Flash)**\n\nI specialize in retrieving verified historical drilling evidence, offset-well hazards, and documented mitigation procedures from the National Data Repository (NDR) and Oil India Limited daily drilling archives.\n\n*All responses are strictly grounded in structured offset data. Select a suggestion below or type your inquiry.*`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        model: "gemini-2.5-flash",
      },
    ]);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (questionText?: string) => {
    const q = (questionText || query).trim();
    if (!q || loading) return;

    const userMsg: ChatMessage = {
      id: `usr-${Date.now()}`,
      sender: "user",
      text: q,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setQuery("");
    setLoading(true);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/intelligence/grounded-search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: q,
          bit_depth_md: activeDepthMd,
          formation: "Upper Tipam Sandstone",
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to get answer`);
      const data: SearchResponse = await res.json();

      const aiMsg: ChatMessage = {
        id: `ai-${Date.now()}`,
        sender: "ai",
        text: data.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        model: data.model,
        citedEvidence: data.cited_evidence,
        suggestedFollowups: data.suggested_followups,
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      const errMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        sender: "ai",
        text: `⚠️ Error retrieving evidence: ${err.message || "Failed to communicate with service."}`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  function json_stringify(obj: any) {
    return JSON.stringify(obj);
  }

  return (
    <div className="space-y-6">
      {/* ── Top Header Banner ── */}
      <div className="bg-gradient-to-r from-purple-950 via-slate-900 to-indigo-950 text-white rounded-2xl p-6 border border-purple-800/40 shadow-xl">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5 mb-2">
              <span className="bg-purple-500/25 text-purple-300 border border-purple-500/40 px-3 py-1 rounded-full text-xs font-mono font-bold flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                REQUIREMENT 27 · GROUNDED NATURAL-LANGUAGE SEARCH
              </span>
              <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 px-2.5 py-0.5 rounded-full text-xs font-mono font-bold">
                GOOGLE GEMINI 2.5 FLASH ACTIVE
              </span>
            </div>
            <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-3">
              <span>🤖 Grounded Natural-Language Evidence Assistant</span>
            </h1>
            <p className="text-slate-200 text-xs mt-1 max-w-3xl leading-relaxed">
              Domain-constrained decision support assistant. Cites exact historical offset wells (e.g. NHK-014, NHK-019),
              documented NPT hours, root causes, and Daily Drilling Report (DDR) sources. Never invents unsupported equipment instructions.
            </p>
          </div>

          <div className="flex items-center gap-2 font-mono text-xs text-purple-200 bg-purple-900/40 p-3 rounded-xl border border-purple-700/50">
            <ShieldAlert className="w-4 h-4 text-purple-400 flex-shrink-0" />
            <span>engineer_review_required = true</span>
          </div>
        </div>
      </div>

      {/* ── Prompt Suggestions Bar ── */}
      <div className="card p-5 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-600" />
            <span>Curated Drilling Engineering Suggestions (Click to Ask)</span>
          </div>
          <span className="text-[11px] font-mono text-slate-500">1-Click Quick Prompts</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(s.query)}
              disabled={loading}
              className="text-left p-3 rounded-xl border border-slate-200 bg-slate-50 hover:bg-purple-50/60 hover:border-purple-300 transition-all group flex flex-col justify-between"
            >
              <div className="flex items-start justify-between gap-1 mb-1">
                <span className="text-[10px] font-mono font-bold uppercase text-purple-700 bg-purple-100/60 px-2 py-0.5 rounded border border-purple-200">
                  {s.category}
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-purple-600 group-hover:translate-x-0.5 transition-all" />
              </div>
              <div className="text-xs font-semibold text-slate-800 group-hover:text-purple-900 leading-snug">
                "{s.query}"
              </div>
              <div className="text-[10px] text-slate-500 mt-1 font-mono">
                Context: {s.context}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* ── Main Chat Conversation ── */}
      <div className="card bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden flex flex-col" style={{ minHeight: 480 }}>
        {/* Messages Stream */}
        <div className="flex-1 p-5 space-y-4 overflow-y-auto max-h-[560px] bg-slate-50/40">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-4xl ${msg.sender === "user" ? "ml-auto flex-row-reverse" : ""}`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 text-white ${
                  msg.sender === "user" ? "bg-slate-800" : "bg-purple-700 shadow-md"
                }`}
              >
                {msg.sender === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Message Bubble */}
              <div
                className={`rounded-2xl p-4 text-xs space-y-3 ${
                  msg.sender === "user"
                    ? "bg-slate-800 text-white rounded-tr-none shadow-sm"
                    : "bg-white text-slate-800 border border-slate-200/80 rounded-tl-none shadow-sm"
                }`}
              >
                {/* Header info */}
                <div className="flex items-center justify-between gap-4 border-b border-slate-100 pb-2">
                  <span className={`font-bold text-[11px] ${msg.sender === "user" ? "text-slate-300" : "text-purple-800 font-mono"}`}>
                    {msg.sender === "user" ? "Drilling Engineer" : `eRTMAC-NWIS (${msg.model || "Gemini 2.5 Flash"})`}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">{msg.timestamp}</span>
                </div>

                {/* Body Text (rendered markdown) */}
                <div className="leading-relaxed whitespace-pre-wrap font-sans text-xs">
                  {msg.text}
                </div>

                {/* Cited Evidence Cards if available */}
                {msg.citedEvidence && msg.citedEvidence.length > 0 && (
                  <div className="pt-3 border-t border-slate-100 space-y-2">
                    <div className="text-[10px] font-mono font-bold uppercase text-purple-700 flex items-center gap-1.5">
                      <BookOpen className="w-3.5 h-3.5" />
                      <span>Cited Offset Evidence Sources ({msg.citedEvidence.length} Events)</span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {msg.citedEvidence.map((evt, idx) => (
                        <div key={idx} className="p-3 bg-purple-50/50 rounded-xl border border-purple-200/70 text-[11px] space-y-1">
                          <div className="flex items-center justify-between font-mono font-bold">
                            <span className="text-purple-900">{evt.well_name}</span>
                            <span className="text-rose-700">{evt.event_type}</span>
                          </div>
                          <div className="text-slate-600">
                            {evt.formation_name} ({evt.depth_start_m}–{evt.depth_end_m} m)
                          </div>
                          <div className="text-slate-500 font-mono text-[10px]">
                            NPT: <strong>{evt.npt_hours} hrs</strong> · Source: <code className="bg-white px-1 rounded">{evt.source_document}</code>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Follow-up suggestions */}
                {msg.suggestedFollowups && msg.suggestedFollowups.length > 0 && (
                  <div className="pt-2 flex flex-wrap gap-1.5">
                    <span className="text-[10px] font-mono text-slate-400 self-center">Follow-up:</span>
                    {msg.suggestedFollowups.map((f, i) => (
                      <button
                        key={i}
                        onClick={() => handleSend(f)}
                        className="text-[10px] px-2 py-0.5 rounded-lg bg-slate-100 hover:bg-purple-100 text-slate-700 hover:text-purple-900 transition-colors border border-slate-200"
                      >
                        {f}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-3 max-w-xl">
              <div className="w-8 h-8 rounded-xl bg-purple-700 flex items-center justify-center text-white flex-shrink-0 animate-pulse">
                <Bot className="w-4 h-4" />
              </div>
              <div className="rounded-2xl p-4 bg-white border border-slate-200 rounded-tl-none shadow-sm text-xs font-mono text-slate-500 flex items-center gap-2">
                <div className="w-3.5 h-3.5 border-2 border-purple-600 border-t-transparent rounded-full animate-spin" />
                <span>Consulting Gemini 2.5 Flash with Grounded NWIS Evidence…</span>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-slate-200 bg-white">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask natural language question (e.g. Show previous stuck-pipe events near current bit)..."
              disabled={loading}
              className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-purple-500 text-xs font-sans"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-5 py-2.5 rounded-xl bg-purple-700 hover:bg-purple-600 text-white font-bold text-xs shadow-md transition-all flex items-center gap-2 disabled:opacity-50"
            >
              <span>Ask Evidence AI</span>
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 mt-2">
            <span>Powered by Google Gemini 2.5 Flash · Strictly Grounded in NWIS Offset DB</span>
            <span>Bit Depth: {activeDepthMd.toFixed(1)} m</span>
          </div>
        </div>
      </div>
    </div>
  );
};
