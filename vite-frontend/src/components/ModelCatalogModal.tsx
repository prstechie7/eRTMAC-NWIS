import React from "react";
import { X, CheckCircle2, ShieldCheck, Cpu, Activity, Award } from "lucide-react";

interface ModelCatalogModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ModelCatalogModal: React.FC<ModelCatalogModalProps> = ({
  isOpen,
  onClose,
}) => {
  if (!isOpen) return null;

  const models = [
    { priority: "P0", model: "Extra Trees Classifier", task: "Stuck-pipe prediction", benchmark: "100% test / 96.6% AUC", fit: "97%", status: "Active Primary" },
    { priority: "P0", model: "XGBoost Classifier", task: "Stuck-pipe prediction", benchmark: "~92.0% accuracy / 95.8% AUC", fit: "95%", status: "Active Ensemble" },
    { priority: "P0", model: "Extra Trees Classifier", task: "Lost-circulation prediction", benchmark: "99.0% test, F1 0.90", fit: "95%", status: "Active Primary" },
    { priority: "P0", model: "XGBoost Classifier", task: "Lost-circulation prediction", benchmark: "82.27% accuracy", fit: "93%", status: "Active Ensemble" },
    { priority: "P0", model: "Support Vector Machine (SVM)", task: "Kick/influx detection", benchmark: "96.8% accuracy", fit: "93%", status: "Active Primary" },
    { priority: "P0", model: "Random Forest Classifier", task: "Activity-aware kick detection", benchmark: "89.58% accuracy", fit: "90%", status: "Active Ensemble" },
    { priority: "P0", model: "XGBoost Regressor", task: "ROP prediction", benchmark: "R² ≈ 0.98", fit: "94%", status: "Active Regressor" },
    { priority: "P0", model: "XGBoost Regressor", task: "Torque prediction", benchmark: "R² ≈ 0.9235", fit: "94%", status: "Active Regressor" },
    { priority: "P0", model: "XGBoost Regressor", task: "Drag prediction", benchmark: "R² ≈ 0.9762", fit: "91%", status: "Active Regressor" },
    { priority: "P0", model: "Random Forest Classifier", task: "Stick-slip severity", benchmark: "90% accuracy, F1 0.91", fit: "91%", status: "Active" },
    { priority: "P1", model: "Random Forest Classifier", task: "Lithology / formation", benchmark: "75–85% FORCE dataset", fit: "85%", status: "Active" },
    { priority: "P0", model: "Isolation Forest", task: "Unsupervised sensor anomaly", benchmark: "Real-time out-of-bounds", fit: "92%", status: "Active Watchdog" },
    { priority: "P0", model: "CUSUM Change-Point Detector", task: "Step-change onset (pit/pressure)", benchmark: "Sub-second onset alarm", fit: "96%", status: "Active Watchdog" },
    { priority: "P0", model: "Dynamic Time Warping (DTW)", task: "Historical well offset alignment", benchmark: "Multi-channel alignment", fit: "98%", status: "Active Matcher" },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden">
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-forest-900 text-emerald-400 flex items-center justify-center font-bold">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-extrabold text-slate-900">
                OIL 14-Model Enterprise ML Stack & Benchmarks
              </h2>
              <p className="text-xs text-slate-500 font-medium">
                Production models calibrated for Assam-Arakan & Indian Basins
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-2xl transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body / Table */}
        <div className="p-6 overflow-y-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider">
                <th className="pb-3 pl-2">Priority</th>
                <th className="pb-3">ML Model</th>
                <th className="pb-3">NWIS Operational Use</th>
                <th className="pb-3">Published Benchmark</th>
                <th className="pb-3">Fit</th>
                <th className="pb-3 pr-2 text-right">Engine State</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {models.map((m, idx) => (
                <tr key={idx} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3 pl-2">
                    <span
                      className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded ${
                        m.priority === "P0"
                          ? "bg-rose-50 text-rose-700 border border-rose-200"
                          : "bg-amber-50 text-amber-700 border border-amber-200"
                      }`}
                    >
                      {m.priority}
                    </span>
                  </td>
                  <td className="py-3 font-semibold text-slate-900 font-mono text-[11px]">
                    {m.model}
                  </td>
                  <td className="py-3 text-slate-600">{m.task}</td>
                  <td className="py-3 text-slate-700 font-mono text-[11px]">{m.benchmark}</td>
                  <td className="py-3 font-mono font-bold text-emerald-700">{m.fit}</td>
                  <td className="py-3 pr-2 text-right">
                    <span className="inline-flex items-center gap-1 text-[10px] font-mono font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                      {m.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Modal Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-medium">
          <span>Safety Standard: API 53 / ISO 13624-1 Compliant</span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold hover:bg-slate-800 transition-all"
          >
            Close Catalog
          </button>
        </div>
      </div>
    </div>
  );
};
