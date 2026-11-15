"""
SchoolGPT - My Queries & History Module
Isolated user query telemetry, inspection, and management.
RSR Technologies
"""

import streamlit as st
from database.models import get_user_query_history, delete_query_history_item, clear_user_query_history
from components.source_cards import render_sources

def render_query_history(current_user: dict):
    user_id = current_user.get("id")

    st.markdown("## 🕒 My Query History")
    st.caption("Review your past interactions, grounded responses, and cited references.")

    queries = get_user_query_history(user_id=user_id, limit=50)

    if not queries:
        st.info("You haven't asked any questions yet. Head over to **Ask SchoolGPT** to get started!")
        return

    # Header controls
    c1, c2 = st.columns([3, 1])
    with c1:
        search_kw = st.text_input("Filter your past queries", placeholder="Search queries...")
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear All History", type="secondary"):
            clear_user_query_history(user_id)
            st.success("Query history cleared.")
            st.rerun()

    # Filter
    display_list = queries
    if search_kw:
        sk = search_kw.lower()
        display_list = [q for q in queries if sk in q["query_text"].lower() or sk in q["answer_text"].lower()]

    st.markdown(f"**Showing {len(display_list)} recorded questions:**")

    for q in display_list:
        with st.expander(f"❓ {q['query_text']} — ({q['created_at']})", expanded=False):
            st.markdown(f"**Answer:**")
            st.markdown(q["answer_text"])

            if q.get("sources"):
                st.markdown("**Referenced Sources:**")
                for s in q["sources"]:
                    st.caption(f"• {s.get('title')} (Page {s.get('page')}, {s.get('section')})")

            st.caption(f"Language: {q.get('language', 'en').upper()} | Response Time: {q.get('response_time_sec', 0.0)}s")

            if st.button("Delete this entry", key=f"del_q_{q['id']}"):
                delete_query_history_item(q["id"], user_id)
                st.rerun()
