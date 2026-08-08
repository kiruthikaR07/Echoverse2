import React, { useState, useEffect } from "react";
import { Candidate, CurriculumItem, Message, FeedbackReportData } from "./types";
import { fetchCandidates, fetchCurriculum, sendInterviewTurn } from "./api";
import { CandidateSelector } from "./components/CandidateSelector";
import { ProgressHeader } from "./components/ProgressHeader";
import { InterviewChat } from "./components/InterviewChat";
import { FeedbackReport } from "./components/FeedbackReport";
import { Bot, Sparkles, AlertCircle, RefreshCw } from "lucide-react";

export default function App() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [curriculum, setCurriculum] = useState<CurriculumItem[]>([]);
  const [activeCandidate, setActiveCandidate] = useState<Candidate | null>(null);
  const [sessionId, setSessionId] = useState<string>("");

  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isStarted, setIsStarted] = useState<boolean>(false);
  const [isComplete, setIsComplete] = useState<boolean>(false);
  const [feedback, setFeedback] = useState<FeedbackReportData | null>(null);

  const [questionCount, setQuestionCount] = useState<number>(0);
  const [coveredDays, setCoveredDays] = useState<number[]>([]);
  const [currentDifficulty, setCurrentDifficulty] = useState<number>(3);
  const [currentTopic, setCurrentTopic] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  // Load candidate and curriculum data
  useEffect(() => {
    async function loadData() {
      try {
        const [cands, curr] = await Promise.all([fetchCandidates(), fetchCurriculum()]);
        setCandidates(cands);
        setCurriculum(curr);
      } catch (err: any) {
        console.error("Failed to initialize app data:", err);
        setError("Failed to connect to backend server. Make sure server is running.");
      }
    }
    loadData();
  }, []);

  // Handle starting a new interview session
  const handleStartInterview = async (candidate: Candidate) => {
    setIsLoading(true);
    setError(null);
    setActiveCandidate(candidate);

    const newSessionId = `session_${candidate.id}_${Date.now()}`;
    setSessionId(newSessionId);

    try {
      // First API turn: empty messages initializes Interview Planner + Question Generator
      const res = await sendInterviewTurn(newSessionId, candidate, []);

      const firstMessage: Message = {
        role: "assistant",
        content: res.message,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        topic: "Interview Initialization",
        day: 1,
        difficulty: 3,
      };

      setMessages([firstMessage]);
      setQuestionCount(1);
      setCoveredDays([1]);
      setCurrentDifficulty(3);
      setCurrentTopic("Cohort Assessment Start");
      setIsStarted(true);
      setIsComplete(res.done);
      if (res.done && res.feedback) {
        setFeedback(res.feedback);
      }
    } catch (err: any) {
      console.error("Interview turn error:", err);
      setError(err.message || "Failed to start interview turn.");
    } finally {
      setIsLoading(false);
    }
  };

  // Handle candidate answer submission
  const handleSendMessage = async (userAnswer: string) => {
    if (!activeCandidate || !sessionId || isLoading) return;

    const userMsg: Message = {
      role: "user",
      content: userAnswer,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setIsLoading(true);
    setError(null);

    try {
      const res = await sendInterviewTurn(sessionId, activeCandidate, updatedMessages);

      if (res.done && res.feedback) {
        setIsComplete(true);
        setFeedback(res.feedback);
        const doneMsg: Message = {
          role: "assistant",
          content: res.message,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        };
        setMessages((prev) => [...prev, doneMsg]);
      } else {
        const assistantMsg: Message = {
          role: "assistant",
          content: res.message,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        };

        setMessages((prev) => [...prev, assistantMsg]);
        setQuestionCount((prev) => prev + 1);

        // Dynamically track distinct curriculum days covered based on message count
        setCoveredDays((prev) => {
          if (prev.length < 4 && (questionCount + 1) % 2 === 0) {
            return [...prev, prev.length + 1];
          }
          return prev;
        });

        // Adapt difficulty display
        if (questionCount > 3) {
          setCurrentDifficulty((prev) => Math.min(5, Math.max(1, prev)));
        }
      }
    } catch (err: any) {
      console.error("Turn submission error:", err);
      setError(err.message || "Error communicating with interview engine.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRestart = () => {
    setIsStarted(false);
    setIsComplete(false);
    setFeedback(null);
    setMessages([]);
    setQuestionCount(0);
    setCoveredDays([]);
    setSessionId("");
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans flex flex-col">
      {/* Global Top Bar */}
      <nav className="bg-slate-900 text-white border-b border-slate-800 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3 cursor-pointer" onClick={handleRestart}>
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-xs">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-sm tracking-tight flex items-center gap-1.5">
              Enterprise AI Interviewer <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            </h1>
            <p className="text-[10px] text-slate-400">31-Day Cohort Technical Assessor</p>
          </div>
        </div>

        {isStarted && (
          <button
            onClick={handleRestart}
            className="text-xs text-slate-300 hover:text-white flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Restart Session
          </button>
        )}
      </nav>

      {/* Error Alert Toast */}
      {error && (
        <div className="bg-rose-50 border-b border-rose-200 text-rose-800 px-6 py-3 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError(null)} className="font-bold hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Main View Router */}
      <main className="flex-1">
        {!isStarted ? (
          /* View 1: Candidate Selection */
          <CandidateSelector
            candidates={candidates}
            curriculum={curriculum}
            onSelectCandidate={handleStartInterview}
            isLoading={isLoading}
          />
        ) : isComplete && feedback && activeCandidate ? (
          /* View 3: Complete Feedback Report */
          <FeedbackReport
            feedback={feedback}
            candidate={activeCandidate}
            onRestart={handleRestart}
          />
        ) : activeCandidate ? (
          /* View 2: Live Technical Interview */
          <div className="flex flex-col h-full">
            <ProgressHeader
              candidate={activeCandidate}
              questionCount={questionCount}
              coveredDaysCount={coveredDays.length}
              difficulty={currentDifficulty}
              currentTopic={currentTopic}
              sessionId={sessionId}
            />
            <InterviewChat
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              candidate={activeCandidate}
              isComplete={isComplete}
            />
          </div>
        ) : null}
      </main>
    </div>
  );
}
