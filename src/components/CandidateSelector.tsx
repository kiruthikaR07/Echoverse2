import React, { useState } from "react";
import { Candidate, CurriculumItem } from "../types";
import { User, CheckCircle, AlertTriangle, HelpCircle, ArrowRight, BookOpen, Cpu, Sparkles } from "lucide-react";

interface CandidateSelectorProps {
  candidates: Candidate[];
  curriculum: CurriculumItem[];
  onSelectCandidate: (candidate: Candidate) => void;
  isLoading: boolean;
}

export const CandidateSelector: React.FC<CandidateSelectorProps> = ({
  candidates,
  curriculum,
  onSelectCandidate,
  isLoading,
}) => {
  const [selectedId, setSelectedId] = useState<string>(candidates[0]?.id || "");
  const [isCustomMode, setIsCustomMode] = useState<boolean>(false);
  const [customCandidate, setCustomCandidate] = useState<Partial<Candidate>>({
    id: `custom_${Date.now()}`,
    name: "Taylor Vance",
    role: "MLOps Engineer",
    experience: "3 years Kubernetes & PyTorch",
    completed_missions: [1, 4, 8],
    skipped_missions: [12],
    failed_missions: [20],
    attempts: { "1": 1, "4": 1, "8": 2, "20": 2 },
    learning_signals: {
      strengths: ["Clean container architecture", "FastAPI web services"],
      gaps: ["Needs practice on LoRA VRAM memory estimation"],
    },
  });

  const activeCandidate = isCustomMode
    ? (customCandidate as Candidate)
    : candidates.find((c) => c.id === selectedId) || candidates[0];

  const handleStart = () => {
    if (activeCandidate) {
      onSelectCandidate(activeCandidate);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-8">
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-white relative overflow-hidden shadow-xl">
        <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
          <Cpu className="w-64 h-64 text-indigo-400" />
        </div>
        <div className="relative z-10 space-y-3 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs font-semibold tracking-wide uppercase">
            <Sparkles className="w-3.5 h-3.5" /> 31-Day Cohort Assessor
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-slate-50">
            Adaptive AI Interviewer
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Conduct realistic multi-turn technical interviews for Enterprise AI Engineers. The AI interviewer adapts difficulty, explores strengths, probes knowledge gaps, and covers at least 4 curriculum days over 8+ questions.
          </p>
        </div>
      </div>

      {/* Candidate Selection Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
            <User className="w-5 h-5 text-indigo-600" /> Select Cohort Candidate
          </h2>
          <button
            onClick={() => setIsCustomMode(!isCustomMode)}
            className="text-xs font-medium text-indigo-600 hover:text-indigo-800 underline transition-colors"
          >
            {isCustomMode ? "← Choose Existing Candidate" : "+ Add Custom Candidate"}
          </button>
        </div>

        {!isCustomMode ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {candidates.map((cand) => {
              const isSelected = cand.id === selectedId;
              return (
                <div
                  key={cand.id}
                  onClick={() => setSelectedId(cand.id)}
                  className={`cursor-pointer rounded-xl p-5 border transition-all duration-200 ${
                    isSelected
                      ? "border-indigo-600 bg-indigo-50/50 shadow-md ring-2 ring-indigo-600/20"
                      : "border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="w-10 h-10 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">
                      {cand.name.split(" ").map((n) => n[0]).join("")}
                    </div>
                    {isSelected && (
                      <span className="w-2.5 h-2.5 rounded-full bg-indigo-600 animate-pulse" />
                    )}
                  </div>

                  <div className="mt-4 space-y-1">
                    <h3 className="font-semibold text-slate-900 text-base">{cand.name}</h3>
                    <p className="text-xs text-indigo-600 font-medium">{cand.role}</p>
                    <p className="text-xs text-slate-500 line-clamp-2 mt-1">{cand.experience}</p>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600">
                    <span className="flex items-center gap-1 text-emerald-600 font-medium">
                      <CheckCircle className="w-3.5 h-3.5" /> {cand.completed_missions.length} Missions
                    </span>
                    <span className="flex items-center gap-1 text-amber-600">
                      <HelpCircle className="w-3.5 h-3.5" /> {cand.skipped_missions.length} Skipped
                    </span>
                    <span className="flex items-center gap-1 text-rose-600">
                      <AlertTriangle className="w-3.5 h-3.5" /> {cand.failed_missions.length} Failed
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          /* Custom Candidate Form */
          <div className="bg-white border border-slate-200 rounded-xl p-6 space-y-4 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-900">Custom Candidate Profile</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Full Name</label>
                <input
                  type="text"
                  value={customCandidate.name}
                  onChange={(e) => setCustomCandidate({ ...customCandidate, name: e.target.value })}
                  className="w-full text-sm border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Role / Background</label>
                <input
                  type="text"
                  value={customCandidate.role}
                  onChange={(e) => setCustomCandidate({ ...customCandidate, role: e.target.value })}
                  className="w-full text-sm border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Profile Details & Learning History */}
      {activeCandidate && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-6 shadow-sm">
          <div className="border-b border-slate-100 pb-4">
            <h3 className="text-lg font-bold text-slate-900">{activeCandidate.name}</h3>
            <p className="text-xs text-slate-500">{activeCandidate.role} • {activeCandidate.experience}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Mission Records */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                <BookOpen className="w-4 h-4 text-indigo-600" /> Cohort Mission History
              </h4>
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-emerald-50/60 border border-emerald-100 text-emerald-800">
                  <span className="font-medium">Completed Missions:</span>
                  <span>Days {activeCandidate.completed_missions.join(", ") || "None"}</span>
                </div>
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-amber-50/60 border border-amber-100 text-amber-800">
                  <span className="font-medium">Skipped Missions (Unassessed):</span>
                  <span>Days {activeCandidate.skipped_missions.join(", ") || "None"}</span>
                </div>
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-rose-50/60 border border-rose-100 text-rose-800">
                  <span className="font-medium">Failed Missions (Targeted Probe):</span>
                  <span>Days {activeCandidate.failed_missions.join(", ") || "None"}</span>
                </div>
              </div>
            </div>

            {/* Learning Signals */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-indigo-600" /> Pre-Interview Learning Signals
              </h4>
              <div className="space-y-2 text-xs">
                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
                  <span className="font-semibold text-slate-700 block">Demonstrated Strengths:</span>
                  <ul className="list-disc list-inside text-slate-600 space-y-0.5">
                    {activeCandidate.learning_signals.strengths.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
                  <span className="font-semibold text-slate-700 block">Knowledge Gaps to Probe:</span>
                  <ul className="list-disc list-inside text-slate-600 space-y-0.5">
                    {activeCandidate.learning_signals.gaps.map((g, i) => (
                      <li key={i}>{g}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Action Footer */}
          <div className="pt-4 border-t border-slate-100 flex items-center justify-end">
            <button
              onClick={handleStart}
              disabled={isLoading}
              className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white font-medium text-sm rounded-xl shadow-sm transition-all flex items-center gap-2"
            >
              {isLoading ? "Initializing Engine..." : "Start Technical Interview"}
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
