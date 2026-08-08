"""
Candidate Analyzer Module.
Extracts candidate learning signals, mission completion records, and identifies
potential strengths and gaps without assuming skipped missions mean a lack of knowledge.
"""

from typing import Dict, Any, List

def analyze_candidate(candidate: Dict[str, Any], curriculum: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyzes candidate profile against cohort curriculum.
    """
    completed_ids = set(candidate.get("completed_missions", []))
    skipped_ids = set(candidate.get("skipped_missions", []))
    failed_ids = set(candidate.get("failed_missions", []))
    attempts = candidate.get("attempts", {})
    learning_signals = candidate.get("learning_signals", {})
    
    # Map curriculum days
    curr_by_day = {item["day"]: item for item in curriculum}
    
    completed_topics = [curr_by_day[d]["title"] for d in completed_ids if d in curr_by_day]
    skipped_topics = [curr_by_day[d]["title"] for d in skipped_ids if d in curr_by_day]
    failed_topics = [curr_by_day[d]["title"] for d in failed_ids if d in curr_by_day]
    
    # Identify initial strengths: single-attempt completions + explicit signals
    strengths = list(learning_signals.get("strengths", []))
    for day_str, count in attempts.items():
        day_int = int(day_str) if str(day_str).isdigit() else 0
        if day_int in completed_ids and count == 1 and day_int in curr_by_day:
            topic = f"Solid mastery on Day {day_int}: {curr_by_day[day_int]['title']}"
            if topic not in strengths:
                strengths.append(topic)
                
    # Identify gaps to probe: failed missions + multi-attempt missions + explicit signals
    gaps_to_probe = list(learning_signals.get("gaps", []))
    for day_int in failed_ids:
        if day_int in curr_by_day:
            gap_note = f"Failed mission on Day {day_int} ({curr_by_day[day_int]['title']})"
            if gap_note not in gaps_to_probe:
                gaps_to_probe.append(gap_note)
                
    for day_str, count in attempts.items():
        day_int = int(day_str) if str(day_str).isdigit() else 0
        if count > 1 and day_int in curr_by_day:
            gap_note = f"Took {count} attempts on Day {day_int} ({curr_by_day[day_int]['title']})"
            if gap_note not in gaps_to_probe:
                gaps_to_probe.append(gap_note)
                
    return {
        "name": candidate.get("name", "Candidate"),
        "role": candidate.get("role", "AI Engineer Candidate"),
        "experience": candidate.get("experience", ""),
        "completed_count": len(completed_ids),
        "skipped_count": len(skipped_ids),
        "failed_count": len(failed_ids),
        "completed_topics": completed_topics,
        "skipped_topics": skipped_topics,
        "failed_topics": failed_topics,
        "initial_strengths": strengths,
        "gaps_to_probe": gaps_to_probe,
        "note": "Skipped missions indicate unassessed areas, NOT lack of knowledge."
    }
