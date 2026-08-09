# EchoVerse — Adaptive AI Interview Agent

> An AI-powered technical interviewer that conducts personalized, multi-turn interviews based on a candidate's learning journey through an Enterprise AI Engineering cohort.

## 🚀 Overview

EchoVerse is an adaptive AI Interview Agent built for the ABTalks Vibe Code Hackathon.

Instead of presenting candidates with a fixed list of technical questions, EchoVerse analyzes:

- The cohort curriculum
- The candidate's completed missions
- Failed and skipped missions
- Attempts and learning signals
- Previous interview answers

It then creates a personalized interview that dynamically adapts to the candidate's demonstrated understanding.

The interviewer maintains context throughout the conversation, asks intelligent follow-up questions, changes difficulty based on performance, and generates structured feedback at the end.

---

## 🎯 Problem

Learners completing an AI engineering program often understand the systems they built but struggle to explain:

- Why they selected a particular architecture
- Why they chose one technology over another
- How their systems behave under production constraints
- What trade-offs they considered
- How they would debug or improve their implementation

Traditional technical interviews use predefined questions and do not adapt to the candidate's learning journey.

### Our Solution

EchoVerse behaves more like a real technical interviewer.

```text
Candidate Profile
       +
31-Day Curriculum
       ↓
Interview Planner
       ↓
Personalized Interview
       ↓
Candidate Answer
       ↓
Answer Evaluation
       ↓
Adaptive Follow-up
       ↓
Difficulty Adjustment
       ↓
8+ Questions / 4+ Curriculum Days
       ↓
Structured Final Feedback
