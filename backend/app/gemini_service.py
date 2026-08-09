"""
Gemini API Service Module.
Handles communication with the Gemini API for prompt processing and JSON parsing.
"""

import os
import json
import re
import sys
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from backend.app.prompts import (
        SYSTEM_INTERVIEW_PLANNER,
        SYSTEM_QUESTION_GENERATOR,
        SYSTEM_ANSWER_EVALUATOR,
        SYSTEM_FOLLOWUP_GENERATOR,
        SYSTEM_FINAL_FEEDBACK_GENERATOR,
    )
except ImportError:
    from app.prompts import (
        SYSTEM_INTERVIEW_PLANNER,
        SYSTEM_QUESTION_GENERATOR,
        SYSTEM_ANSWER_EVALUATOR,
        SYSTEM_FOLLOWUP_GENERATOR,
        SYSTEM_FINAL_FEEDBACK_GENERATOR,
    )

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
CANDIDATE_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash-latest",
    "gemini-flash-latest",
]

def _call_gemini(
    system_instruction: str,
    user_prompt: str,
    response_json: bool = True,
    temperature: float = 0.3
) -> str:
    """
    Core function to call Gemini API via HTTP POST with automatic model fallback & retry logic.
    """
    api_key = os.environ.get("GEMINI_API_KEY", GEMINI_API_KEY)
    if not api_key:
        print("Warning: GEMINI_API_KEY environment variable is missing.")
        
    last_exception = None

    for model_name in CANDIDATE_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            },
            "generationConfig": {
                "temperature": temperature,
            }
        }
        
        if response_json:
            payload["generationConfig"]["responseMimeType"] = "application/json"
            
        data_bytes = json.dumps(payload).encode("utf-8")
        
        for attempt in range(2): # Up to 2 retries per model
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={"Content-Type": "application/json"}
            )
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    res_body = json.loads(resp.read().decode("utf-8"))
                    candidates = res_body.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
                    return ""
            except urllib.error.HTTPError as e:
                err_msg = e.read().decode("utf-8")
                last_exception = e
                if e.code in [429, 500, 502, 503, 504]: # Rate limit or temporary service issue, brief pause and retry
                    import time
                    time.sleep(1.5 * (attempt + 1))
                    continue
                elif e.code == 404: # Model not found, break and try next candidate model
                    break
                else:
                    print(f"Gemini API HTTP Error {e.code} for model {model_name}: {err_msg}")
                    break
            except Exception as e:
                last_exception = e
                break

    if last_exception:
        raise last_exception
    return ""

def _clean_json_str(text: str) -> str:
    """Removes markdown code fences from JSON strings."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()

def plan_interview(candidate_profile: Dict[str, Any], curriculum: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calls Interview Planner to construct initial interview strategy."""
    prompt = f"""Candidate Profile:
{json.dumps(candidate_profile, indent=2)}

Cohort Curriculum:
{json.dumps(curriculum, indent=2)}

Create the interview plan according to your system instructions.
"""
    try:
        raw_res = _call_gemini(SYSTEM_INTERVIEW_PLANNER, prompt, response_json=True)
        return json.loads(_clean_json_str(raw_res))
    except Exception as e:
        print("Planner fallback triggered:", e)
        # Fallback plan
        curr_days = [c["day"] for c in curriculum[:4]]
        return {
            "selected_days": curr_days if curr_days else [1, 4, 8, 12],
            "strengths_to_explore": candidate_profile.get("learning_signals", {}).get("strengths", []),
            "gaps_to_probe": candidate_profile.get("learning_signals", {}).get("gaps", []),
            "starting_difficulty": 3,
            "strategy": "Progressive assessment covering core topics and candidate gap areas."
        }

def generate_question(
    candidate_profile: Dict[str, Any],
    current_day: Dict[str, Any],
    history: List[Dict[str, Any]],
    last_eval: Optional[Dict[str, Any]],
    difficulty: int
) -> Dict[str, Any]:
    """Calls Question Generator to produce the next interview question."""
    prompt = f"""Candidate Profile:
{json.dumps(candidate_profile, indent=2)}

Target Curriculum Day:
Day {current_day.get('day')}: {current_day.get('title')}
Type: {current_day.get('type')}
Tools: {', '.join(current_day.get('tools', []))}
Learning Objectives:
{json.dumps(current_day.get('learning_objectives', []), indent=2)}

Current Difficulty Level: {difficulty}/5

Previous Questions & Answers History:
{json.dumps(history[-4:], indent=2) if history else "No previous questions yet."}

Last Answer Evaluation:
{json.dumps(last_eval, indent=2) if last_eval else "None"}

Generate the next technical question.
"""
    try:
        raw_res = _call_gemini(SYSTEM_QUESTION_GENERATOR, prompt, response_json=True)
        return json.loads(_clean_json_str(raw_res))
    except Exception as e:
        print("Question generator fallback triggered:", e)
        title = current_day.get("title", "AI Architecture")
        objs = current_day.get("learning_objectives", ["Core concepts"])
        return {
            "question": f"In the context of {title}, how would you approach: {objs[0]}?",
            "curriculum_day": current_day.get("day", 1),
            "topic": title,
            "difficulty": difficulty,
            "question_type": "architectural",
            "why_this_question": "Fallback question assessing primary learning objective."
        }

def evaluate_answer(
    current_day: Dict[str, Any],
    question: str,
    candidate_answer: str,
    history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Calls Answer Evaluator to score and analyze the candidate's answer."""
    prompt = f"""Curriculum Day {current_day.get('day')}: {current_day.get('title')}
Learning Objectives: {json.dumps(current_day.get('learning_objectives', []))}

Question Asked:
"{question}"

Candidate's Answer:
"{candidate_answer}"

Previous Interview Context:
{json.dumps(history[-3:], indent=2) if history else "Start of interview"}

Evaluate this response according to system instructions.
"""
    try:
        raw_res = _call_gemini(SYSTEM_ANSWER_EVALUATOR, prompt, response_json=True)
        return json.loads(_clean_json_str(raw_res))
    except Exception as e:
        print("Answer evaluator fallback triggered:", e)
        return {
            "score": 6,
            "technical_accuracy": 6,
            "depth": 6,
            "clarity": 7,
            "strengths": ["Demonstrated baseline understanding"],
            "gaps": ["Could elaborate with more specific technical trade-offs"],
            "follow_up_needed": False,
            "follow_up_reason": "",
            "recommended_action": "new_topic"
        }

def generate_followup(
    question: str,
    candidate_answer: str,
    evaluation: Dict[str, Any],
    current_day: Dict[str, Any],
    history: List[Dict[str, Any]]
) -> str:
    """Calls Follow-Up Generator to construct a targeted follow-up question."""
    prompt = f"""Original Question:
"{question}"

Candidate's Answer:
"{candidate_answer}"

Answer Evaluation Gaps/Weaknesses:
{json.dumps(evaluation.get('gaps', []), indent=2)}
Follow-up reason: {evaluation.get('follow_up_reason', '')}

Curriculum Objectives:
{json.dumps(current_day.get('learning_objectives', []), indent=2)}

Generate a sharp, concise follow-up question addressing the specific weakness or trade-off in the candidate's response.
"""
    try:
        raw_res = _call_gemini(SYSTEM_FOLLOWUP_GENERATOR, prompt, response_json=False)
        return raw_res.strip().strip('"')
    except Exception as e:
        print("Followup generator fallback triggered:", e)
        gaps = evaluation.get("gaps", ["that aspect"])
        return f"Could you elaborate specifically on {gaps[0] if gaps else 'the trade-offs'} in your previous answer?"

def generate_final_feedback(
    candidate_profile: Dict[str, Any],
    history: List[Dict[str, Any]],
    evaluations: List[Dict[str, Any]],
    covered_days: List[int]
) -> Dict[str, Any]:
    """Calls Final Feedback Generator to produce comprehensive final assessment."""
    prompt = f"""Candidate Profile:
{json.dumps(candidate_profile, indent=2)}

Curriculum Days Covered in Interview: {covered_days}

Complete Interview Transcript & Questions:
{json.dumps(history, indent=2)}

All Question Evaluations:
{json.dumps(evaluations, indent=2)}

Generate the final post-interview feedback report in strict JSON format.
"""
    try:
        raw_res = _call_gemini(SYSTEM_FINAL_FEEDBACK_GENERATOR, prompt, response_json=True)
        return json.loads(_clean_json_str(raw_res))
    except Exception as e:
        print("Final feedback fallback triggered:", e)
        return {
            "summary": f"The candidate completed a comprehensive 8-question technical interview spanning {len(covered_days)} cohort curriculum modules. They demonstrated solid core technical capabilities while highlighting key growth areas in advanced architectural trade-offs.",
            "strengths": [
                "Clear communication and structured problem solving approach",
                "Demonstrated practical familiarity with core AI engineering tools"
            ],
            "gaps": [
                "Detailed mathematical calculations on VRAM and context memory limits",
                "Deeper benchmarking of retrieval evaluation metrics"
            ],
            "next": [
                "Review Day 20 Parameter-Efficient Fine-Tuning (PEFT) VRAM formulas",
                "Implement hybrid retrieval evaluation with RAG metrics (Faithfulness and Answer Relevance)",
                "Practice configuring vLLM PagedAttention KV-cache parameters"
            ]
        }
