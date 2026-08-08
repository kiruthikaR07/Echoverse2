import { Candidate, CurriculumItem, Message, InterviewResponseData } from "./types";

export async function fetchCandidates(): Promise<Candidate[]> {
  const res = await fetch("/api/candidates");
  if (!res.ok) throw new Error("Failed to load candidates");
  return await res.json();
}

export async function fetchCurriculum(): Promise<CurriculumItem[]> {
  const res = await fetch("/api/curriculum");
  if (!res.ok) throw new Error("Failed to load curriculum");
  return await res.json();
}

export async function sendInterviewTurn(
  sessionId: string,
  candidate: Candidate,
  messages: Message[]
): Promise<InterviewResponseData> {
  const res = await fetch("/api/interview", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      sessionId,
      candidate,
      messages: messages.map(m => ({ role: m.role, content: m.content })),
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.error || errorData.detail || "Failed to process interview turn");
  }

  return await res.json();
}
