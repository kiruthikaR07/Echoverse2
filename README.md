# EchoVerse — Adaptive AI Interviewer

> An AI-powered technical interviewer that conducts personalized, multi-turn interviews based on a candidate's learning journey through an Enterprise AI Engineering cohort.

## 🏆 Hackathon

Built for the **ABTalks Vibe Code Hackathon**.

### Problem Statement 2 — The Interview Agent

The goal is to build the interviewer, not the interview.

The system evaluates a candidate's understanding of topics covered throughout a 31-day Enterprise AI Engineering cohort and conducts a realistic technical interview that adapts to the candidate's responses.

---

## 🎯 What EchoVerse Does

EchoVerse creates a personalized technical interview using:

- Candidate learning progress
- Completed missions
- Failed or repeated attempts
- Skipped topics
- Learning signals
- 31-day cohort curriculum

Instead of following a fixed questionnaire, the interviewer dynamically decides what to ask next.

### Core capabilities

- Personalized interview planning
- Multi-turn conversation
- Adaptive difficulty
- Intelligent follow-up questions
- Curriculum-aware questioning
- Conversation context
- Technical answer evaluation
- Minimum 8-question interview
- Coverage of at least 4 curriculum days
- Structured final feedback

---

## 🧠 How It Works

```text
                    ┌─────────────────────┐
                    │ Candidate Profile   │
                    └──────────┬──────────┘
                               │
                               │
                    ┌──────────▼──────────┐
                    │ 31-Day Curriculum   │
                    └──────────┬──────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │   Interview Planner     │
                  │                         │
                  │ Selects relevant days   │
                  │ Identifies strengths    │
                  │ Finds areas to probe    │
                  │ Sets difficulty          │
                  └────────────┬────────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │  Question Generator     │
                  └────────────┬────────────┘
                               │
                               ▼
                    ┌───────────────────┐
                    │    Candidate      │
                    │      Answer       │
                    └─────────┬─────────┘
                              │
                              ▼
                  ┌─────────────────────────┐
                  │    Answer Evaluator     │
                  │                         │
                  │ Accuracy                │
                  │ Depth                  │
                  │ Clarity                │
                  │ Knowledge gaps          │
                  └────────────┬────────────┘
                               │
                               ▼
                    ┌───────────────────┐
                    │ Interview Engine  │
                    └─────────┬─────────┘
                              │
                ┌─────────────┼──────────────┐
                │             │              │
                ▼             ▼              ▼
            Follow-up     New Topic     Difficulty
            Question                     Change
                │             │              │
                └─────────────┼──────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  Final Feedback   │
                    │                   │
                    │ Strengths         │
                    │ Gaps              │
                    │ Next Steps        │
                    └───────────────────┘
