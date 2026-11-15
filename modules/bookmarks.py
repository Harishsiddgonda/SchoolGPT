"""
SchoolGPT - Bookmarks Module
Personal repository of bookmarked answers and citations.
RSR Technologies
"""

import streamlit as st
from database.models import get_user_bookmarks, delete_bookmark

def render_bookmarks(current_user: dict):
    user_id = current_user.get("id")

    st.markdown('<div class="rsr-section-title">🔖 Saved SchoolGPT Answers</div>', unsafe_allow_html=True)
    st.caption("Access your bookmarked answers, policy excerpts, and citations.")

    bookmarks = get_user_bookmarks(user_id=user_id)

    if not bookmarks:
        st.info("You don't have any saved bookmarks yet. Click '🔖 Bookmark' under any answer in **Ask SchoolGPT** to save it here.")
        return

    # Category Filter
    categories = list(set([b.get("category", "General") for b in bookmarks]))
    selected_cat = st.selectbox("Category Filter", options=["All"] + categories)

    filtered_bms = bookmarks
    if selected_cat != "All":
        filtered_bms = [b for b in bookmarks if b.get("category") == selected_cat]

    for bm in filtered_bms:
        with st.container():
            st.markdown(f"""
                <div style="background: #FFFFFF; border-radius: 12px; border-left: 4px solid #7C3AED; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; padding: 1.2rem; margin-bottom: 0.8rem; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A;">
                            📌 {bm['question']}
                        </div>
                        <span style="font-size: 0.75rem; background: #EDE9FE; color: #6D28D9; font-weight: 700; padding: 3px 8px; border-radius: 6px;">
                            {bm.get('category', 'Saved Answer')}
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            with st.expander(f"View Answer & Citations: {bm['question'][:60]}...", expanded=True):
                st.markdown(bm["answer"])

                if bm.get("sources"):
                    st.markdown("**Original Citations:**")
                    for s in bm["sources"]:
                        st.caption(f"• 📄 {s.get('title')} (Page {s.get('page')}, {s.get('section')})")

                st.caption(f"Bookmarked on: {bm.get('created_at', 'N/A')[:16]}")

                b_col1, b_col2 = st.columns([1, 4])
                with b_col1:
                    if st.button("❌ Remove", key=f"del_bm_{bm['id']}"):
                        delete_bookmark(bm["id"], user_id)
                        st.rerun()
                with b_col2:
                    if st.button("💬 Ask Follow-up", key=f"ask_bm_{bm['id']}"):
                        st.session_state["active_question"] = bm["question"]
                        st.session_state["current_page"] = "chat"
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
