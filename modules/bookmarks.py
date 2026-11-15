"""
SchoolGPT - Bookmarks Module
Personal repository of bookmarked answers and citations.
RSR Technologies
"""

import streamlit as st
from database.models import get_user_bookmarks, delete_bookmark

def render_bookmarks(current_user: dict):
    user_id = current_user.get("id")

    st.markdown("## 🔖 Saved Bookmarks")
    st.caption("Access your saved answers, policy excerpts, and citations.")

    bookmarks = get_user_bookmarks(user_id=user_id)

    if not bookmarks:
        st.info("You don't have any saved bookmarks. Click '🔖 Bookmark' under any answer in **Ask SchoolGPT** to save it here.")
        return

    # Category Filter
    categories = list(set([b.get("category", "General") for b in bookmarks]))
    selected_cat = st.selectbox("Filter by Category", options=["All"] + categories)

    filtered_bms = bookmarks
    if selected_cat != "All":
        filtered_bms = [b for b in bookmarks if b.get("category") == selected_cat]

    for bm in filtered_bms:
        with st.container():
            st.markdown(f"""
                <div style="background: #FFFFFF; border-radius: 10px; border-left: 4px solid #7C3AED; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; padding: 1.2rem; margin-bottom: 0.8rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A;">
                            📌 {bm['question']}
                        </div>
                        <span style="font-size: 0.75rem; background: #EDE9FE; color: #6D28D9; font-weight: 700; padding: 3px 8px; border-radius: 8px;">
                            {bm.get('category', 'Saved Answer')}
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            with st.expander(f"View Saved Answer & Citations", expanded=True):
                st.markdown(bm["answer"])

                if bm.get("sources"):
                    st.markdown("**Original Citations:**")
                    for s in bm["sources"]:
                        st.caption(f"• 📄 {s.get('title')} (Page {s.get('page')}, {s.get('section')})")

                st.caption(f"Bookmarked on: {bm.get('created_at', 'N/A')}")

                if st.button("❌ Remove Bookmark", key=f"del_bm_{bm['id']}"):
                    delete_bookmark(bm["id"], user_id)
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
