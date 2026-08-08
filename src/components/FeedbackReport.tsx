import React from "react";
import { FeedbackReportData, Candidate } from "../types";
import { CheckCircle2, AlertTriangle, Compass, Award, RefreshCw, Printer, Sparkles } from "lucide-react";

interface FeedbackReportProps {
  feedback: FeedbackReportData;
  candidate: Candidate;
  onRestart: () => void;
}

export const FeedbackReport: React.FC<FeedbackReportProps> = ({
  feedback,
  candidate,
  onRestart,
}) => {
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8 my-6">
      {/* Top Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-white space-y-3 relative overflow-hidden shadow-xl">
        <div className="flex items-center justify-between">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-xs font-semibold tracking-wide uppercase">
            <Award className="w-3.5 h-3.5" /> Technical Assessment Complete
          </div>
          <button
            onClick={() => window.print()}
            className="text-xs text-slate-300 hover:text-white flex items-center gap-1.5 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700 transition-colors"
          >
            <Printer className="w-3.5 h-3.5" /> Print Report
          </button>
        </div>

        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-50">
          Evaluation Feedback: {candidate.name}
        </h1>
        <p className="text-slate-300 text-xs sm:text-sm">
          Cohort Candidate Profile: {candidate.role}
        </p>
      </div>

      {/* Summary Card */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-3 shadow-xs">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-600" /> Executive Summary
        </h2>
        <p className="text-sm text-slate-700 leading-relaxed font-sans whitespace-pre-line">
          {feedback.summary}
        </p>
      </div>

      {/* Grid: Strengths & Gaps */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Verified Strengths */}
        <div className="bg-white border border-emerald-200 rounded-2xl p-6 space-y-4 shadow-xs">
          <div className="flex items-center gap-2 text-emerald-800">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            <h3 className="font-bold text-base">Verified Technical Strengths</h3>
          </div>
          <ul className="space-y-2.5 text-xs text-slate-700">
            {feedback.strengths.map((str, idx) => (
              <li key={idx} className="flex items-start gap-2 bg-emerald-50/60 p-2.5 rounded-lg border border-emerald-100">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 mt-1.5 shrink-0" />
                <span>{str}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Identified Gaps */}
        <div className="bg-white border border-rose-200 rounded-2xl p-6 space-y-4 shadow-xs">
          <div className="flex items-center gap-2 text-rose-800">
            <AlertTriangle className="w-5 h-5 text-rose-600" />
            <h3 className="font-bold text-base">Verified Technical Gaps</h3>
          </div>
          <ul className="space-y-2.5 text-xs text-slate-700">
            {feedback.gaps.map((gap, idx) => (
              <li key={idx} className="flex items-start gap-2 bg-rose-50/60 p-2.5 rounded-lg border border-rose-100">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-600 mt-1.5 shrink-0" />
                <span>{gap}</span>
              </li>
            ))}
          </ul>
        </div>

      </div>

      {/* Cohort Progression Action Items */}
      <div className="bg-white border border-indigo-200 rounded-2xl p-6 space-y-4 shadow-xs">
        <div className="flex items-center gap-2 text-indigo-900">
          <Compass className="w-5 h-5 text-indigo-600" />
          <h3 className="font-bold text-base">Actionable Next Steps for Cohort Progression</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-slate-800">
          {feedback.next.map((item, idx) => (
            <div key={idx} className="bg-indigo-50/50 p-3 rounded-xl border border-indigo-100 flex items-start gap-2.5">
              <span className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
                {idx + 1}
              </span>
              <span className="leading-relaxed">{item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer Action */}
      <div className="flex justify-center pt-4">
        <button
          onClick={onRestart}
          className="px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white font-medium text-sm rounded-xl shadow-md transition-all flex items-center gap-2 cursor-pointer"
        >
          <RefreshCw className="w-4 h-4" /> Start New Candidate Interview
        </button>
      </div>
    </div>
  );
};
