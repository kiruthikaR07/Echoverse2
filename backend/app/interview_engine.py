"""
Interview Engine - Deterministic Python Controller.
Enforces interview invariants:
- Minimum 8 questions
- Minimum 4 distinct curriculum days
- Session state continuity
- Max 1 follow-up per topic
- Difficulty adaptation (1-5)
- Automated transition to final feedback generation
"""

import json
import os
import sys
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from backend.app.candidate_analyzer import analyze_candidate
    from backend.app.gemini_service import (
        plan_interview,
        generate_question,
        evaluate_answer,
        generate_followup,
        generate_final_feedback
    )
except ImportError:
    from app.candidate_analyzer import analyze_candidate
    from app.gemini_service import (
        plan_interview,
        generate_question,
        evaluate_answer,
        generate_followup,
        generate_final_feedback
    )

# Load Curriculum & Candidates Data
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def _load_json(filename: str) -> List[Dict[str, Any]]:
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

CURRICULUM = _load_json("curriculum.json")
CANDIDATES = _load_json("candidates.json")

# In-memory session store: session_id -> state dict
SESSIONS: Dict[str, Dict[str, Any]] = {}

def get_candidates() -> List[Dict[str, Any]]:
    """Returns candidate list."""
    return CANDIDATES

def get_curriculum() -> List[Dict[str, Any]]:
    """Returns cohort curriculum."""
    return CURRICULUM

def process_interview_turn(
    session_id: str,
    candidate_data: Dict[str, Any],
    messages: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Main interview state machine turn handler.
    """
    curr_map = {item["day"]: item for item in CURRICULUM}
    
    # 1. INITIALIZE NEW SESSION if not exists
    if session_id not in SESSIONS:
        analyzer_res = analyze_candidate(candidate_data, CURRICULUM)
        plan = plan_interview(candidate_data, CURRICULUM)
        
        selected_day_nums = plan.get("selected_days", [1, 4, 8, 12])
        # Ensure at least 4 distinct days planned
        if len(selected_day_nums) < 4:
            all_days = [c["day"] for c in CURRICULUM]
            for d in all_days:
                if d not in selected_day_nums:
                    selected_day_nums.append(d)
                if len(selected_day_nums) >= 4:
                    break
                    
        starting_diff = plan.get("starting_difficulty", 3)
        starting_diff = max(1, min(5, starting_diff))
        
        first_day_num = selected_day_nums[0]
        first_day_obj = curr_map.get(first_day_num, CURRICULUM[0])
        
        # Generate initial question
        q_data = generate_question(
            candidate_profile=candidate_data,
            current_day=first_day_obj,
            history=[],
            last_eval=None,
            difficulty=starting_diff
        )
        
        state = {
            "session_id": session_id,
            "candidate": candidate_data,
            "analysis": analyzer_res,
            "plan": plan,
            "selected_days": selected_day_nums,
            "covered_days": [first_day_obj["day"]],
            "current_day": first_day_obj,
            "current_difficulty": starting_diff,
            "question_count": 1,
            "followups_on_current_topic": 0,
            "history": [
                {
                    "question": q_data.get("question", f"Welcome. Let's discuss {first_day_obj['title']}."),
                    "answer": "",
                    "day": first_day_obj["day"],
                    "difficulty": starting_diff,
                    "topic": q_data.get("topic", first_day_obj["title"])
                }
            ],
            "evaluations": [],
            "strengths": [],
            "gaps": [],
            "done": False,
            "feedback": None
        }
        
        SESSIONS[session_id] = state
        return {
            "sessionId": session_id,
            "message": state["history"][0]["question"],
            "done": False,
            "feedback": None
        }
        
    # 2. CONTINUING EXISTING SESSION
    state = SESSIONS[session_id]
    
    if state["done"]:
        return {
            "sessionId": session_id,
            "message": "Interview completed.",
            "done": True,
            "feedback": state["feedback"]
        }
        
    # Extract candidate's latest answer
    candidate_answer = ""
    if messages:
        candidate_answer = messages[-1].get("content", "").strip()
        
    current_q_entry = state["history"][-1]
    current_q_entry["answer"] = candidate_answer
    
    # Evaluate the answer
    eval_res = evaluate_answer(
        current_day=state["current_day"],
        question=current_q_entry["question"],
        candidate_answer=candidate_answer,
        history=state["history"]
    )
    
    state["evaluations"].append(eval_res)
    state["strengths"].extend(eval_res.get("strengths", []))
    state["gaps"].extend(eval_res.get("gaps", []))
    
    recommended_action = eval_res.get("recommended_action", "new_topic")
    
    # 3. CHECK TERMINATION CONDITION: min 8 questions AND min 4 covered days
    has_min_questions = state["question_count"] >= 8
    has_min_days = len(state["covered_days"]) >= 4
    
    if has_min_questions and has_min_days and (recommended_action != "follow_up" or state["question_count"] >= 10):
        # Generate final feedback & conclude
        fb = generate_final_feedback(
            candidate_profile=state["candidate"],
            history=state["history"],
            evaluations=state["evaluations"],
            covered_days=state["covered_days"]
        )
        state["done"] = True
        state["feedback"] = fb
        
        return {
            "sessionId": session_id,
            "message": "Thank you for completing the Enterprise AI Engineering technical interview! Here is your structured performance feedback report.",
            "done": True,
            "feedback": fb
        }
        
    # 4. CONTROLLER DECISION LOGIC: Follow-up vs Next Question
    if recommended_action == "follow_up" and state["followups_on_current_topic"] < 1:
        # Ask targeted follow-up question
        followup_q = generate_followup(
            question=current_q_entry["question"],
            candidate_answer=candidate_answer,
            evaluation=eval_res,
            current_day=state["current_day"],
            history=state["history"]
        )
        
        state["question_count"] += 1
        state["followups_on_current_topic"] += 1
        
        state["history"].append({
            "question": followup_q,
            "answer": "",
            "day": state["current_day"]["day"],
            "difficulty": state["current_difficulty"],
            "topic": f"{state['current_day']['title']} (Follow-up)"
        })
        
        return {
            "sessionId": session_id,
            "message": followup_q,
            "done": False,
            "feedback": None
        }
    else:
        # Move to next topic / adapt difficulty
        state["followups_on_current_topic"] = 0
        
        # Difficulty adaptation
        if recommended_action == "increase_difficulty":
            state["current_difficulty"] = min(5, state["current_difficulty"] + 1)
        elif recommended_action == "decrease_difficulty":
            state["current_difficulty"] = max(1, state["current_difficulty"] - 1)
            
        # Select next curriculum day
        covered_set = set(state["covered_days"])
        next_day_num = None
        
        # Priority 1: Ensure we cover 4 distinct days before question 8
        if len(covered_set) < 4:
            for d in state["selected_days"]:
                if d not in covered_set:
                    next_day_num = d
                    break
            if not next_day_num:
                for c in CURRICULUM:
                    if c["day"] not in covered_set:
                        next_day_num = c["day"]
                        break
                        
        # Priority 2: Pick next unvisited or cycle selected
        if not next_day_num:
            for d in state["selected_days"]:
                if d != state["current_day"]["day"]:
                    next_day_num = d
                    break
            if not next_day_num:
                next_day_num = (state["current_day"]["day"] % len(CURRICULUM)) + 1
                
        next_day_obj = curr_map.get(next_day_num, CURRICULUM[0])
        state["current_day"] = next_day_obj
        
        if next_day_obj["day"] not in state["covered_days"]:
            state["covered_days"].append(next_day_obj["day"])
            
        # Generate question for next day
        q_data = generate_question(
            candidate_profile=state["candidate"],
            current_day=next_day_obj,
            history=state["history"],
            last_eval=eval_res,
            difficulty=state["current_difficulty"]
        )
        
        state["question_count"] += 1
        state["history"].append({
            "question": q_data.get("question", f"Regarding {next_day_obj['title']}..."),
            "answer": "",
            "day": next_day_obj["day"],
            "difficulty": state["current_difficulty"],
            "topic": q_data.get("topic", next_day_obj["title"])
        })
        
        return {
            "sessionId": session_id,
            "message": state["history"][-1]["question"],
            "done": False,
            "feedback": None
        }
