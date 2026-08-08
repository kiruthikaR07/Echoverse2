/**
 * API Service for Adaptive AI Interviewer Frontend
 */

export async function fetchCandidates() {
  const res = await fetch("/api/candidates");
  if (!res.ok) throw new Error("Failed to load candidates");
  return await res.json();
}

export async function fetchCurriculum() {
  const res = await fetch("/api/curriculum");
  if (!res.ok) throw new Error("Failed to load curriculum");
  return await res.json();
}

export async function sendInterviewTurn(sessionId, candidate, messages) {
  const res = await fetch("/api/interview", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      sessionId,
      candidate,
      messages,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.error || errorData.detail || "Failed to process interview turn");
  }

  return await res.json();
}
