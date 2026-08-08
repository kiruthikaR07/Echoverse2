import React from "react";
import { Candidate } from "../types";
import { Target, Layers, Gauge, User, ShieldCheck } from "lucide-react";

interface ProgressHeaderProps {
  candidate: Candidate;
  questionCount: number;
  coveredDaysCount: number;
  difficulty: number;
  currentTopic?: string;
  sessionId: string;
}

export const ProgressHeader: React.FC<ProgressHeaderProps> = ({
  candidate,
  questionCount,
  coveredDaysCount,
  difficulty,
  currentTopic,
  sessionId,
}) => {
  // Goal: minimum 8 questions, minimum 4 covered days
  const minQuestions = 8;
  const minDays = 4;

  const qProgress = Math.min(100, Math.round((questionCount / minQuestions) * 100));
  const dayProgress = Math.min(100, Math.round((coveredDaysCount / minDays) * 100));

  const getDifficultyColor = (diff: number) => {
    switch (diff) {
      case 1:
        return "bg-emerald-100 text-emerald-800 border-emerald-200";
      case 2:
        return "bg-teal-100 text-teal-800 border-teal-200";
      case 3:
        return "bg-indigo-100 text-indigo-800 border-indigo-200";
      case 4:
        return "bg-amber-100 text-amber-800 border-amber-200";
      case 5:
        return "bg-rose-100 text-rose-800 border-rose-200";
      default:
        return "bg-indigo-100 text-indigo-800 border-indigo-200";
    }
  };

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
      <div className="max-w-6xl mx-auto px-4 py-3">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          
          {/* Candidate & Session Info */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-sm shadow-xs">
              {candidate.name.split(" ").map((n) => n[0]).join("")}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-semibold text-slate-900 text-sm">{candidate.name}</h2>
                <span className="text-xs text-slate-400 font-mono">#{sessionId.slice(-6)}</span>
              </div>
              <p className="text-xs text-slate-500 line-clamp-1">
                {currentTopic ? `Current Topic: ${currentTopic}` : candidate.role}
              </p>
            </div>
          </div>

          {/* Telemetry Metrics */}
          <div className="flex items-center gap-6 w-full sm:w-auto justify-between sm:justify-end">
            
            {/* Metric 1: Question Count */}
            <div className="space-y-1 text-left sm:text-right">
              <div className="flex items-center gap-1.5 text-xs text-slate-600 font-medium">
                <Target className="w-3.5 h-3.5 text-indigo-600" />
                <span>Questions: <strong className="text-slate-900">{questionCount}</strong> / {minQuestions}+</span>
              </div>
              <div className="w-28 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-indigo-600 rounded-full transition-all duration-300"
                  style={{ width: `${qProgress}%` }}
                />
              </div>
            </div>

            {/* Metric 2: Curriculum Days Covered */}
            <div className="space-y-1 text-left sm:text-right">
              <div className="flex items-center gap-1.5 text-xs text-slate-600 font-medium">
                <Layers className="w-3.5 h-3.5 text-teal-600" />
                <span>Days Covered: <strong className="text-slate-900">{coveredDaysCount}</strong> / {minDays}+</span>
              </div>
              <div className="w-28 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-teal-600 rounded-full transition-all duration-300"
                  style={{ width: `${dayProgress}%` }}
                />
              </div>
            </div>

            {/* Metric 3: Adapted Difficulty Badge */}
            <div className="flex items-center gap-1.5">
              <div
                className={`px-2.5 py-1 rounded-full border text-xs font-bold flex items-center gap-1 ${getDifficultyColor(
                  difficulty
                )}`}
              >
                <Gauge className="w-3.5 h-3.5" />
                <span>Level {difficulty}/5</span>
              </div>
            </div>

          </div>

        </div>
      </div>
    </header>
  );
};
