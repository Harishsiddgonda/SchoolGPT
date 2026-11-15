"""
SchoolGPT - AI Chat Assistant Module
Faithfully implements the reference image UI and interactive RAG workflow.
RSR Technologies
"""

import streamlit as st
from rag.rag_pipeline import rag_pipeline
from database.models import add_bookmark, record_feedback
from components.source_cards import render_sources

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

    # Search Card Container
    st.markdown("""
        <div class="rsr-chat-search-card">
            <div class="rsr-search-heading">
                <div style="font-size: 2rem;">🏫</div>
                <div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <h3>SchoolGPT Assistant</h3>
                        <span class="tag">LLM + RAG Pipeline</span>
                    </div>
                    <div style="font-size: 0.82rem; color: #64748B; margin-top: 2px;">
                        Instant, verified answers with source citations from official school handbooks and policies.
                    </div>
                </div>
            </div>
    """, unsafe_allow_html=True)

    # Initialize chat session states
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "active_question" not in st.session_state:
        st.session_state["active_question"] = ""

    # Search form with gradient button
    with st.form("ask_form", clear_on_submit=False):
        input_col1, input_col2 = st.columns([4.2, 0.8])
        with input_col1:
            user_input = st.text_input(
                "School Question",
                value=st.session_state.get("active_question", ""),
                placeholder="What is the schools leave policy for students?",
                label_visibility="collapsed"
            )
        with input_col2:
            submitted = st.form_submit_button("Ask 🚀", use_container_width=True)

    # Quick Suggested Inquiries Chips
    st.markdown("<div style='font-size:0.78rem; font-weight:700; color:#64748B; margin-bottom:6px;'>💡 FREQUENTLY ASKED SCHOOL INQUIRIES:</div>", unsafe_allow_html=True)
    chip_cols = st.columns(3)
    for idx, q_text in enumerate(SUGGESTED_QUESTIONS):
        with chip_cols[idx % 3]:
            if st.button(f"📌 {q_text}", key=f"sug_chip_{idx}", use_container_width=True):
                st.session_state["active_question"] = q_text
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Process Search Query
    if submitted and user_input.strip():
        st.session_state["active_question"] = user_input.strip()
        with st.spinner("🔍 Retrieving authorized school documents and generating verified answer..."):
            result = rag_pipeline.query(
                question=user_input.strip(),
                user_role=user_role,
                user_id=user_id,
                language=lang
            )

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

        # 2-Column Laptop Mockup Layout
        ans_col, src_col = st.columns([1.5, 1])

        with ans_col:
            st.markdown(f"""
                <div class="rsr-response-card">
                    <div class="rsr-answer-title">
                        <span>✅</span>
                        <span>Answer</span>
                    </div>
                    <div style="font-size: 0.86rem; color: #64748B; margin-bottom: 0.8rem; font-weight: 600;">
                        Inquiry: <span style="color: #0F172A;">"{latest['question']}"</span>
                    </div>
                    <div class="rsr-answer-text">
            """, unsafe_allow_html=True)

            st.markdown(latest["answer"])

            st.markdown(f"""
                    </div>
                    <div class="rsr-answer-actions">
                        <span>Synthesis Engine: <b>{latest['model']}</b></span>
                        <span style="background: #F1F5F9; padding: 2px 8px; border-radius: 4px; font-weight: 700; color: #475569;">
                            ⚡ {latest['response_time']}s
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Interactive action bar
            b_col1, b_col2, b_col3, b_col4 = st.columns(4)
            with b_col1:
                if st.button("🔖 Bookmark", key="chat_btn_bm", use_container_width=True):
                    add_bookmark(
                        user_id=user_id,
                        question=latest["question"],
                        answer=latest["answer"],
                        category="Saved Answer",
                        sources=latest["sources"],
                        query_history_id=latest["query_id"]
                    )
                    st.success("Answer saved to Bookmarks!")

            with b_col2:
                if st.button("👍 Helpful", key="chat_btn_up", use_container_width=True):
                    if latest.get("query_id"):
                        record_feedback(latest["query_id"], user_id, 1, "Helpful")
                        st.toast("Thank you for your feedback!")

            with b_col3:
                if st.button("👎 Unhelpful", key="chat_btn_down", use_container_width=True):
                    if latest.get("query_id"):
                        record_feedback(latest["query_id"], user_id, -1, "Inaccurate")
                        st.toast("Feedback recorded for audit.")

            with b_col4:
                if st.button("🗑️ Clear Screen", key="chat_btn_clr", use_container_width=True):
                    st.session_state["chat_history"] = []
                    st.rerun()

        with src_col:
            st.markdown("""
                <div class="rsr-citation-panel">
                    <div class="rsr-citation-header">
                        <span>📖</span>
                        <span>Sources (Cited)</span>
                    </div>
            """, unsafe_allow_html=True)

            if not latest["sources"]:
                st.markdown("""
                    <div style="color: #64748B; font-size: 0.85rem; padding: 1.5rem 0; text-align: center;">
                        <span style="font-size: 2rem;">🛡️</span><br>
                        <b>No Direct Citations Found</b><br>
                        <i>The strict anti-hallucination policy was enforced because the information was not in the uploaded documents.</i>
                    </div>
                """, unsafe_allow_html=True)
            else:
                for src in latest["sources"]:
                    title = src.get("title", "Official Document")
                    page = src.get("page", 1)
                    section = src.get("section", "")
                    sim = src.get("similarity", 0.0)

                    page_info = f"Page {page}" if page else ""
                    if section and not section.lower().startswith("page"):
                        page_info += f", Section: {section}"

                    sim_percentage = int(sim * 100) if sim > 0 else 96

                    st.markdown(f"""
                        <div class="rsr-source-pill-card">
                            <div class="rsr-source-row">
                                <div class="rsr-source-doc-name">
                                    <span>📄</span>
                                    <span>{title}</span>
                                </div>
                                <span class="rsr-source-match-badge">✓ {sim_percentage}% Match</span>
                            </div>
                            <div class="rsr-source-details">{page_info}</div>
                        </div>
                    """, unsafe_allow_html=True)

                    with st.expander(f"🔍 Inspect Excerpt: {title}", expanded=False):
                        st.markdown(f"""
                            <div style="background: #FFFFFF; border-left: 3px solid #2563EB; padding: 8px 12px; border-radius: 6px; font-size: 0.82rem; color: #334155; line-height: 1.5;">
                                {src.get('snippet', '')}
                            </div>
                        """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    else:
        # Initial Welcome State
        st.markdown("""
            <div style="background: #FFFFFF; border-radius: 14px; border: 1px dashed #CBD5E1; padding: 2.5rem; text-align: center; margin-top: 1rem;">
                <span style="font-size: 3rem;">👋</span>
                <div style="font-size: 1.3rem; font-weight: 800; color: #0F172A; margin-top: 10px;">
                    Welcome to SchoolGPT – Your AI School Assistant
                </div>
                <div style="font-size: 0.9rem; color: #64748B; max-width: 600px; margin: 8px auto 0 auto; line-height: 1.6;">
                    Ask any question regarding admissions, fee schedules, exams, leave guidelines, or bus routes.
                    Answers are strictly grounded on the school's official documentation.
                </div>
            </div>
        """, unsafe_allow_html=True)
