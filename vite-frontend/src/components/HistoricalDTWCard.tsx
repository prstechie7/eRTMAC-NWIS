import React from "react";
import { GitCompare, MoreHorizontal, ArrowRight, ShieldCheck, CheckCircle2, AlertOctagon } from "lucide-react";

export interface DTWRecord {
  wellId: string;
  field: string;
  formation: string;
  similarity: number;
  historicalIncident: string;
  incidentDepth: string;
  remedyAction: string;
  nptHours: number;
  status: "stuck" | "loss" | "kick" | "safe";
}

interface HistoricalDTWCardProps {
  onSelectWell?: (wellId: string) => void;
}

export const HistoricalDTWCard: React.FC<HistoricalDTWCardProps> = ({
  onSelectWell,
}) => {
  const records: DTWRecord[] = [
    {
      wellId: "NHK-014",
      field: "Duliajan Block (Assam-Arakan)",
      formation: "Barail Coal-Shale",
      similarity: 98.4,
      historicalIncident: "Mechanical Stuck Pipe",
      incidentDepth: "2,420.0 m (6.5m deeper)",
      remedyAction: "Jarred free with 180 klbf overpull + 1.28 SG mud sweep",
      nptHours: 14.5,
      status: "stuck",
    },
    {
      wellId: "NHK-019",
      field: "Nahorkatiya Block",
      formation: "Upper Tipam Sandstone",
      similarity: 89.2,
      historicalIncident: "Partial Lost Circulation",
      incidentDepth: "2,385.0 m",
      remedyAction: "Pill 40 bbls Nutplug LCM + Reduced SPM by 25%",
      nptHours: 6.0,
      status: "loss",
    },
    {
      wellId: "NHK-021",
      field: "Moran Field",
      formation: "Girujan Clay",
      similarity: 76.5,
      historicalIncident: "Tight Hole / Swelling Shale",
      incidentDepth: "1,940.0 m",
      remedyAction: "Back-reamed with 6% KCl mud + Glycol inhibitor",
      nptHours: 4.2,
      status: "safe",
    },
    {
      wellId: "NHK-007",
      field: "Duliajan West",
      formation: "Barail Formation",
      similarity: 64.1,
      historicalIncident: "Minor Gas Influx (Kick)",
      incidentDepth: "2,408.0 m",
      remedyAction: "Shut-in & Engineer's Method circulation (1.32 SG)",
      nptHours: 8.5,
      status: "kick",
    },
  ];

  return (
    <div className="luxury-card rounded-3xl p-6 bg-white border border-slate-200/90 flex flex-col justify-between">
      {/* ── Table Header (Shopeers Style) ── */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <span>Historical Offset Well Alignments</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold">
              DYNAMIC TIME WARPING (DTW)
            </span>
          </h3>
          <p className="text-[11px] text-slate-400 font-medium">
            Multi-sensor trajectory matching against historical drilling events in Duliajan
          </p>
        </div>

        <button className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-xl transition-all">
          <MoreHorizontal className="w-4 h-4" />
        </button>
      </div>

      {/* ── Clean Table View ── */}
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-slate-100 text-[10px] font-bold text-slate-400 uppercase tracking-wider font-mono">
              <th className="pb-3 pl-2">Offset Well</th>
              <th className="pb-3">Formation</th>
              <th className="pb-3">DTW Match</th>
              <th className="pb-3">Historical Incident</th>
              <th className="pb-3">Field Advisory</th>
              <th className="pb-3 pr-2 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100/80 text-xs">
            {records.map((rec) => {
              const isTopMatch = rec.similarity > 95;
              return (
                <tr
                  key={rec.wellId}
                  className={`hover:bg-slate-50/80 transition-colors group ${
                    isTopMatch ? "bg-rose-50/20" : ""
                  }`}
                >
                  {/* Well ID */}
                  <td className="py-3.5 pl-2">
                    <div className="flex items-center gap-2.5">
                      <div
                        className={`w-7 h-7 rounded-xl flex items-center justify-center font-mono font-bold text-xs ${
                          rec.status === "stuck"
                            ? "bg-rose-100 text-rose-700"
                            : rec.status === "loss"
                            ? "bg-amber-100 text-amber-700"
                            : rec.status === "kick"
                            ? "bg-purple-100 text-purple-700"
                            : "bg-emerald-100 text-emerald-700"
                        }`}
                      >
                        {rec.wellId.substring(4)}
                      </div>
                      <div>
                        <div className="font-bold text-slate-900 font-mono flex items-center gap-1.5">
                          <span>{rec.wellId}</span>
                          {isTopMatch && (
                            <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-rose-100 text-rose-700 font-bold">
                              TOP MATCH
                            </span>
                          )}
                        </div>
                        <div className="text-[10px] text-slate-400">{rec.field}</div>
                      </div>
                    </div>
                  </td>

                  {/* Formation */}
                  <td className="py-3.5">
                    <span className="font-medium text-slate-700">{rec.formation}</span>
                  </td>

                  {/* DTW Similarity with mini progress bar */}
                  <td className="py-3.5">
                    <div className="w-28">
                      <div className="flex items-center justify-between text-[11px] font-mono font-bold mb-1">
                        <span className={rec.similarity > 90 ? "text-rose-600" : "text-slate-700"}>
                          {rec.similarity}%
                        </span>
                      </div>
                      <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            rec.similarity > 90
                              ? "bg-rose-500"
                              : rec.similarity > 80
                              ? "bg-amber-500"
                              : "bg-emerald-500"
                          }`}
                          style={{ width: `${rec.similarity}%` }}
                        />
                      </div>
                    </div>
                  </td>

                  {/* Historical Incident */}
                  <td className="py-3.5">
                    <div className="font-semibold text-slate-900">{rec.historicalIncident}</div>
                    <div className="text-[10px] text-slate-400 font-mono">{rec.incidentDepth}</div>
                  </td>

                  {/* Field Advisory */}
                  <td className="py-3.5 max-w-xs">
                    <div className="text-[11px] text-slate-600 line-clamp-1 group-hover:line-clamp-none transition-all">
                      {rec.remedyAction}
                    </div>
                  </td>

                  {/* Action */}
                  <td className="py-3.5 pr-2 text-right">
                    <button
                      onClick={() => onSelectWell?.(rec.wellId)}
                      className="px-2.5 py-1 text-[11px] font-semibold text-slate-700 hover:text-emerald-700 bg-slate-100 hover:bg-emerald-50 rounded-xl transition-all border border-slate-200/80 inline-flex items-center gap-1"
                    >
                      <span>Overlay</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
