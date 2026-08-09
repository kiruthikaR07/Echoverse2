import os
import sys
import uuid
import json
import streamlit as st

# Ensure project root is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Expose GEMINI_API_KEY from Streamlit secrets if present
try:
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets and not os.environ.get("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

from backend.app.interview_engine import (
    process_interview_turn,
    get_candidates,
    get_curriculum,
    SESSIONS
)

# Page Configuration
st.set_page_config(
    page_title="EchoVerse - Adaptive Enterprise AI Interviewer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Enterprise Tech Look
st.markdown("""
<style>
    .main-header {
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0284c7 0%, #4f46e5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .badge-blue { background-color: #e0f2fe; color: #0369a1; }
    .badge-green { background-color: #dcfce7; color: #15803d; }
    .badge-amber { background-color: #fef3c7; color: #b45309; }
    .badge-rose { background-color: #ffe4e6; color: #be123c; }
    .feedback-card {
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .strength-bg { background-color: #f0fdf4; border: 1px solid #bbf7d0; }
    .gap-bg { background-color: #fffbeb; border: 1px solid #fef08a; }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "candidate" not in st.session_state:
    st.session_state.candidate = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "interview_done" not in st.session_state:
    st.session_state.interview_done = False
if "feedback" not in st.session_state:
    st.session_state.feedback = None


def reset_interview():
    st.session_state.interview_started = False
    st.session_state.session_id = None
    st.session_state.candidate = None
    st.session_state.messages = []
    st.session_state.interview_done = False
    st.session_state.feedback = None


# Load Candidates and Curriculum safely
try:
    candidates = get_candidates()
    curriculum = get_curriculum()
except Exception as e:
    st.error(f"Configuration Error: Unable to load cohort candidate or curriculum data. Details: {e}")
    st.stop()


# Sidebar Navigation & System Information
with st.sidebar:
    st.markdown("### ⚡ EchoVerse AI Engine")
    st.markdown("**Enterprise Technical Interviewer**")
    st.caption("Powered by Gemini & Cohort Analysis")
    
    st.divider()
    
    st.markdown("#### 🎯 Execution Parameters")
    st.markdown("""
    - **Min Questions:** 8+
    - **Min Curriculum Days:** 4+
    - **Adaptation:** Dynamic (Difficulty 1-5)
    - **Follow-ups:** Max 1 per topic
    """)
    
    st.divider()
    
    if st.session_state.interview_started:
        if st.button("🔄 Restart Interview", type="secondary", use_container_width=True):
            reset_interview()
            st.rerun()


# ==============================================================================
# SCREEN 1: LANDING & CANDIDATE SELECTION
# ==============================================================================
if not st.session_state.interview_started:
    st.markdown('<div class="main-header">EchoVerse</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Adaptive Enterprise AI Technical Interviewer</div>', unsafe_allow_html=True)
    
    st.info("An adaptive AI interviewer that evaluates a candidate's technical understanding based on their actual AI cohort learning journey.")
    
    st.markdown("#### 👤 Select Cohort Candidate")
    
    candidate_options = {f"{c['name']} — {c['role']}": c for c in candidates}
    selected_name = st.selectbox(
        "Choose candidate profile to evaluate:",
        options=list(candidate_options.keys())
    )
    selected_candidate = candidate_options[selected_name]
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown(f"### {selected_candidate['name']}")
        st.markdown(f"**Role:** {selected_candidate['role']}")
        st.markdown(f"**Experience:** {selected_candidate['experience']}")
        
        st.markdown("**Completed Cohort Missions:**")
        completed_str = ", ".join([f"Day {d}" for d in selected_candidate.get("completed_missions", [])])
        st.markdown(f"<span class='badge badge-green'>{completed_str}</span>", unsafe_allow_html=True)
        
        skipped_missions = selected_candidate.get("skipped_missions", [])
        if skipped_missions:
            st.markdown("**Skipped Modules:**")
            skipped_str = ", ".join([f"Day {d}" for d in skipped_missions])
            st.markdown(f"<span class='badge badge-amber'>{skipped_str}</span>", unsafe_allow_html=True)
            
        failed_missions = selected_candidate.get("failed_missions", [])
        if failed_missions:
            st.markdown("**Failed Attempts:**")
            failed_str = ", ".join([f"Day {d}" for d in failed_missions])
            st.markdown(f"<span class='badge badge-rose'>{failed_str}</span>", unsafe_allow_html=True)

    with col2:
        st.markdown("#### ⚡ Interview Characteristics")
        st.markdown("""
        - 🎯 **8+ Technical Questions**: In-depth probing
        - 📚 **4+ Curriculum Days**: Broad topic coverage
        - 🔄 **Adaptive Follow-ups**: Targeted evaluation of trade-offs
        - 📊 **Personalized Feedback**: Comprehensive performance summary
        """)
        
        st.markdown("##### Prior Signals:")
        signals = selected_candidate.get("learning_signals", {})
        for str_item in signals.get("strengths", [])[:2]:
            st.markdown(f"✅ *{str_item}*")
        for gap_item in signals.get("gaps", [])[:2]:
            st.markdown(f"⚠️ *{gap_item}*")

    st.divider()
    
    if st.button("🚀 Start Technical Interview", type="primary", use_container_width=True):
        session_id = f"session_{uuid.uuid4().hex[:10]}"
        try:
            with st.spinner("Analyzing candidate profile & generating initial question..."):
                turn_res = process_interview_turn(session_id, selected_candidate, [])
                
            st.session_state.session_id = session_id
            st.session_state.candidate = selected_candidate
            st.session_state.messages = [{"role": "assistant", "content": turn_res["message"]}]
            st.session_state.interview_started = True
            st.session_state.interview_done = turn_res.get("done", False)
            st.session_state.feedback = turn_res.get("feedback")
            st.rerun()
        except Exception as e:
            st.error(f"Unable to start interview session. Error: {e}")


# ==============================================================================
# SCREEN 3: FINAL FEEDBACK DASHBOARD
# ==============================================================================
elif st.session_state.interview_done:
    st.markdown('<div class="main-header">EchoVerse</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Technical Interview Assessment Report</div>', unsafe_allow_html=True)
    
    cand = st.session_state.candidate
    fb = st.session_state.feedback or {}
    
    engine_state = SESSIONS.get(st.session_state.session_id, {})
    covered_days_list = engine_state.get("covered_days", [])
    
    st.success("🎉 Technical Interview Completed!")
    
    # Overview Banner
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Candidate", cand["name"])
    with col_b:
        st.metric("Target Role", cand["role"])
    with col_c:
        st.metric("Modules Covered", f"{len(covered_days_list)} / 8")

    st.divider()
    
    # 1. Overall Assessment
    st.markdown("### 📋 1. Overall Assessment")
    st.info(fb.get("summary", "The candidate completed the technical evaluation across core AI engineering modules."))

    # 2 & 3. Strengths and Gaps Side-by-Side
    col_str, col_gap = st.columns(2)
    
    with col_str:
        st.markdown("### 🟢 2. Technical Strengths")
        strengths = fb.get("strengths", [])
        if strengths:
            for item in strengths:
                st.markdown(f"- **{item}**")
        else:
            st.write("No explicit strengths highlighted.")

    with col_gap:
        st.markdown("### ⚠️ 3. Technical Gaps")
        gaps = fb.get("gaps", [])
        if gaps:
            for item in gaps:
                st.markdown(f"- **{item}**")
        else:
            st.write("No major technical gaps detected.")

    st.divider()

    # 4. Recommended Next Steps
    st.markdown("### 🚀 4. Recommended Next Steps")
    next_steps = fb.get("next") or fb.get("recommended_next_steps") or fb.get("next_steps", [])
    if isinstance(next_steps, list):
        for idx, step in enumerate(next_steps, 1):
            st.markdown(f"{idx}. {step}")
    elif isinstance(next_steps, str):
        st.markdown(next_steps)

    st.divider()

    # 5. Curriculum Areas Evaluated
    st.markdown("### 📚 5. Curriculum Areas Evaluated")
    curr_map = {item["day"]: item for item in curriculum}
    for day_num in covered_days_list:
        day_info = curr_map.get(day_num, {"title": f"Day {day_num}", "tools": []})
        with st.expander(f"Day {day_num}: {day_info['title']}"):
            if "learning_objectives" in day_info:
                st.markdown("**Learning Objectives Tested:**")
                for obj in day_info["learning_objectives"]:
                    st.markdown(f"• {obj}")
            if "tools" in day_info:
                st.markdown("**Relevant Stack/Tools:** " + ", ".join(day_info["tools"]))

    st.divider()
    
    if st.button("🔄 Start New Interview", type="primary", use_container_width=True):
        reset_interview()
        st.rerun()


# ==============================================================================
# SCREEN 2: ACTIVE INTERVIEW CHAT INTERFACE
# ==============================================================================
else:
    engine_state = SESSIONS.get(st.session_state.session_id, {})
    
    q_count = engine_state.get("question_count", len(st.session_state.messages) // 2 + 1)
    covered_days = engine_state.get("covered_days", [1])
    diff = engine_state.get("current_difficulty", 3)
    curr_day = engine_state.get("current_day", {})
    
    # Top Status Bar & Metrics
    st.markdown('<div class="main-header">EchoVerse</div>', unsafe_allow_html=True)
    st.markdown(f"Evaluating **{st.session_state.candidate['name']}** — *{st.session_state.candidate['role']}*")
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Question Progress", f"{q_count} / 8+")
    with m2:
        st.metric("Curriculum Coverage", f"{len(covered_days)} / 4+ days")
    with m3:
        st.metric("Current Difficulty", f"Level {diff} / 5")
    with m4:
        st.metric("Current Topic", f"Day {curr_day.get('day', 1)}")

    st.caption(f"📍 **Focus Area:** {curr_day.get('title', 'AI Engineering Foundations')}")
    st.divider()

    # Render Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if user_answer := st.chat_input("Type your technical answer..."):
        # Append user answer
        st.session_state.messages.append({"role": "user", "content": user_answer})
        
        # Call backend interview engine
        try:
            with st.spinner("Evaluating response & adapting next question..."):
                turn_res = process_interview_turn(
                    st.session_state.session_id,
                    st.session_state.candidate,
                    st.session_state.messages
                )
                
            if turn_res.get("done"):
                st.session_state.interview_done = True
                st.session_state.feedback = turn_res.get("feedback")
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": turn_res.get("message", "")
                })
        except Exception as e:
            st.error("Unable to generate the next interview response. Please try again.")
            
        st.rerun()
