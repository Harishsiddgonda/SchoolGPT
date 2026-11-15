"""
SchoolGPT - AI Chat Assistant Module
Faithfully implements the reference image UI and interactive RAG workflow.
RSR Technologies
"""

import streamlit as st
from rag.rag_pipeline import rag_pipeline
from database.models import add_bookmark, record_feedback

SUGGESTED_QUESTIONS = [
    "What is the student leave policy?",
    "What is the school admission procedure and required documents?",
    "What is the fee payment deadline and late fine structure?",
    "What are the school working hours and attendance requirement?",
    "When are the examinations scheduled for this academic year?",
    "What are the school transportation and bus safety rules?"
]

def render_chat(current_user: dict):
    user_id = current_user.get("id")
    user_role = current_user.get("role", "Student")
    lang = st.session_state.get("selected_lang", "en")

    st.markdown("""
        <div style="background: #FFFFFF; border-radius: 12px; padding: 1.2rem 1.5rem; border: 1px solid #E2E8F0; margin-bottom: 1.2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="font-size: 2.2rem; background: #EEF2FF; padding: 6px 12px; border-radius: 10px;">🏫</div>
                    <div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #0F172A;">
                            SchoolGPT <span style="font-size: 0.95rem; color: #7C3AED; font-weight: 600;">Assistant</span>
                        </div>
                        <div style="font-size: 0.84rem; color: #64748B;">
                            Official School Knowledge Base • Powered by LLM + RAG
                        </div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 0.78rem; background: #F1F5F9; padding: 4px 10px; border-radius: 6px; color: #475569; font-weight: 600;">
                        Role Access: <b>{user_role}</b>
                    </span>
                </div>
            </div>
        </div>
    """.format(user_role=user_role), unsafe_allow_html=True)

    # Initialize chat state
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "active_question" not in st.session_state:
        st.session_state["active_question"] = ""

    # Suggested Questions Pills
    st.markdown("<p style='font-size: 0.82rem; font-weight: 700; color: #475569; margin-bottom: 6px;'>💡 Quick School Inquiries:</p>", unsafe_allow_html=True)
    suggest_cols = st.columns(3)
    for idx, q_text in enumerate(SUGGESTED_QUESTIONS):
        with suggest_cols[idx % 3]:
            if st.button(f"📌 {q_text}", key=f"sug_{idx}", use_container_width=True):
                st.session_state["active_question"] = q_text

    st.markdown("<br>", unsafe_allow_html=True)

    # Question Input Bar with Ask button
    with st.form("ask_form", clear_on_submit=False):
        input_col1, input_col2 = st.columns([4.2, 0.8])
        with input_col1:
            user_input = st.text_input(
                "School Question",
                value=st.session_state.get("active_question", ""),
                placeholder="Ask any question about school policies, fees, leave, exams, or transport...",
                label_visibility="collapsed"
            )
        with input_col2:
            submitted = st.form_submit_button("Ask 🚀", use_container_width=True)

    # Process Query
    if submitted and user_input.strip():
        st.session_state["active_question"] = user_input.strip()
        with st.spinner("🔍 Searching authorized school documents and generating verified answer..."):
            result = rag_pipeline.query(
                question=user_input.strip(),
                user_role=user_role,
                user_id=user_id,
                language=lang
            )

        # Append to active session history
        st.session_state["chat_history"].insert(0, {
            "question": user_input.strip(),
            "answer": result["answer"],
            "sources": result["sources"],
            "model": result["model"],
            "response_time": result["response_time"],
            "query_id": result["query_id"]
        })

    # Render Latest or Selected Q&A
    if st.session_state["chat_history"]:
        latest = st.session_state["chat_history"][0]

        # Layout replica: Left for Answer, Right for Sources
        ans_col, src_col = st.columns([1.5, 1])

        with ans_col:
            st.markdown(f"""
                <div class="rsr-answer-container">
                    <div class="rsr-answer-header">
                        <span>✅</span>
                        <span>Answer</span>
                    </div>
                    <div style="font-size: 0.84rem; color: #64748B; margin-bottom: 0.8rem;">
                        <b>Question:</b> {latest['question']}
                    </div>
                    <div class="rsr-answer-body">
            """, unsafe_allow_html=True)

            st.markdown(latest["answer"])

            st.markdown(f"""
                    </div>
                    <div style="margin-top: 1rem; padding-top: 0.8rem; border-top: 1px solid #E2E8F0; display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem; color: #64748B;">
                        <span>Engine: <b>{latest['model']}</b></span>
                        <span>Response time: <b>{latest['response_time']}s</b></span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Interactive action buttons
            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 1])
            with btn_col1:
                if st.button("🔖 Bookmark", key="btn_bookmark"):
                    add_bookmark(
                        user_id=user_id,
                        question=latest["question"],
                        answer=latest["answer"],
                        category="Saved Answer",
                        sources=latest["sources"],
                        query_history_id=latest["query_id"]
                    )
                    st.success("Bookmarked!")

            with btn_col2:
                if st.button("👍 Helpful", key="btn_helpful"):
                    if latest.get("query_id"):
                        record_feedback(latest["query_id"], user_id, 1, "Helpful")
                        st.toast("Thank you for your feedback!")

            with btn_col3:
                if st.button("👎 Unhelpful", key="btn_unhelpful"):
                    if latest.get("query_id"):
                        record_feedback(latest["query_id"], user_id, -1, "Needs Improvement")
                        st.toast("Feedback recorded!")

            with btn_col4:
                if st.button("🗑️ Clear", key="btn_clear"):
                    st.session_state["chat_history"] = []
                    st.rerun()

        with src_col:
            st.markdown("""
                <div class="rsr-answer-container">
                    <div style="display: flex; align-items: center; gap: 8px; color: #1D4ED8; font-size: 1.15rem; font-weight: 700; margin-bottom: 0.8rem; border-bottom: 2px solid #E2E8F0; padding-bottom: 0.6rem;">
                        <span>📖</span>
                        <span>Sources (Cited)</span>
                    </div>
            """, unsafe_allow_html=True)

            if not latest["sources"]:
                st.markdown("""
                    <div style="color: #64748B; font-size: 0.85rem; padding: 1rem 0;">
                        <i>No specific documents cited for this inquiry (insufficient information policy enforced).</i>
                    </div>
                """, unsafe_allow_html=True)
            else:
                for src in latest["sources"]:
                    title = src.get("title", "Document")
                    page = src.get("page", 1)
                    section = src.get("section", "")
                    sim = src.get("similarity", 0.0)

                    page_info = f"Page {page}" if page else ""
                    if section and not section.lower().startswith("page"):
                        page_info += f", Section: {section}"

                    st.markdown(f"""
                        <div class="rsr-source-card">
                            <div class="rsr-source-title">
                                <span>📄 {title}</span>
                                <span style="font-size: 0.72rem; color: #059669; font-weight: 600;">{int(sim * 100)}% match</span>
                            </div>
                            <div class="rsr-source-meta">{page_info}</div>
                        </div>
                    """, unsafe_allow_html=True)

                    with st.expander(f"View excerpt from {title}", expanded=False):
                        st.caption(src.get("snippet", ""))

            st.markdown("</div>", unsafe_allow_html=True)

    else:
        # Initial Welcome State
        st.info("👋 Welcome to **SchoolGPT**! Enter any question above or choose a suggested inquiry to see grounded AI answers with citations.")
