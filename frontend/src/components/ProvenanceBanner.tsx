"use client";

import React from "react";
import { Info } from "lucide-react";

export const ProvenanceBanner: React.FC = () => (
  <div
    className="flex flex-wrap items-center justify-between gap-2 px-5 py-2 text-[10.5px]"
    style={{ background: "#fffbeb", borderBottom: "1px solid #fde68a" }}
  >
    <div className="flex items-center gap-2">
      <Info className="w-3 h-3 flex-shrink-0" style={{ color: "#d97706" }} />
      <span
        className="font-mono font-black uppercase tracking-wider text-[9px] px-1.5 py-0.5 rounded"
        style={{ background: "#fef3c7", color: "#d97706", border: "1px solid #fde68a" }}
      >
        DEMO
      </span>
      <span style={{ color: "#92400e" }}>
        Public/Synthetic Data only — No confidential Oil India operational data is used.
      </span>
    </div>
    <div className="flex items-center gap-1.5">
      {[
        { label: "PUBLIC DATA", bg: "#eff6ff", c: "#1d4ed8", b: "#bfdbfe" },
        { label: "SYNTHETIC DATA", bg: "#f5f3ff", c: "#6d28d9", b: "#ddd6fe" },
        { label: "OIL INTERNAL (WITSML API REQUIRED)", bg: "#ecfdf5", c: "#065f46", b: "#a7f3d0" },
      ].map((t) => (
        <span
          key={t.label}
          className="font-mono font-bold text-[9px] px-2 py-0.5 rounded"
          style={{ background: t.bg, color: t.c, border: `1px solid ${t.b}` }}
        >
          {t.label}
        </span>
      ))}
    </div>
  </div>
);
