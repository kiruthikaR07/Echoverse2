export interface LearningSignals {
  strengths: string[];
  gaps: string[];
}

export interface Candidate {
  id: string;
  name: string;
  role: string;
  experience: string;
  completed_missions: number[];
  skipped_missions: number[];
  failed_missions: number[];
  attempts: Record<string, number>;
  learning_signals: LearningSignals;
}

export interface CurriculumItem {
  day: number;
  title: string;
  type: string;
  tools: string[];
  learning_objectives: string[];
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  topic?: string;
  day?: number;
  difficulty?: number;
}

export interface FeedbackReportData {
  summary: string;
  strengths: string[];
  gaps: string[];
  next: string[];
}

export interface InterviewResponseData {
  sessionId: string;
  message: string;
  done: boolean;
  feedback: FeedbackReportData | null;
}
