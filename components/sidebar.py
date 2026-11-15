"""
SchoolGPT - Sidebar Navigation Component
RSR Technologies
"""

import streamlit as st
from auth.permissions import has_permission

def render_sidebar(current_user: dict) -> str:
    """
    Renders the navigation menu and returns the selected route.
    """
    user_role = current_user.get("role", "Student")

    with st.sidebar:
        # Organization Branding
        st.markdown("""
            <div style="text-align: center; padding: 0.5rem 0 1.2rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 1.8rem; font-weight: 900; letter-spacing: -1px; color: #FFFFFF;">
                    <span style="color: #60A5FA;">RSR</span> TECH
                </div>
                <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px;">
                    School Knowledge AI
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Build accessible navigation options based on permissions
        nav_options = []

        if has_permission(user_role, "can_view_dashboard"):
            nav_options.append(("📊 Dashboard", "dashboard"))

        nav_options.append(("💬 Ask SchoolGPT", "chat"))
        nav_options.append(("📚 Knowledge Base", "knowledge_base"))

        if has_permission(user_role, "can_upload_docs"):
            nav_options.append(("📤 Upload Documents", "upload"))

        nav_options.append(("🕒 My Queries", "queries"))
        nav_options.append(("🔖 Bookmarks", "bookmarks"))

        if has_permission(user_role, "can_view_analytics"):
            nav_options.append(("📈 Analytics", "analytics"))

        if has_permission(user_role, "can_manage_users"):
            nav_options.append(("👥 User Management", "users"))

        if has_permission(user_role, "can_edit_settings") or user_role in ("Super Admin", "School Administrator"):
            nav_options.append(("⚙️ Settings", "settings"))

        # Render menu buttons or radio
        labels = [item[0] for item in nav_options]
        keys = [item[1] for item in nav_options]

        current_nav = st.session_state.get("current_page", keys[0] if keys else "chat")
        default_index = keys.index(current_nav) if current_nav in keys else 0

        selected_label = st.radio(
            "Navigation Menu",
            options=labels,
            index=default_index,
            label_visibility="collapsed"
        )

        selected_key = keys[labels.index(selected_label)]
        st.session_state["current_page"] = selected_key

        st.markdown("---")

        # Language Selector
        st.markdown("<p style='font-size:0.8rem; color:#CBD5E1; margin-bottom:4px;'>🌐 Language / ಭಾಷೆ / भाषा</p>", unsafe_allow_html=True)
        lang_choice = st.selectbox(
            "Language",
            options=["English", "Kannada (ಕನ್ನಡ)", "Hindi (हिन्दी)"],
            index=0 if st.session_state.get("selected_lang", "en") == "en" else (1 if st.session_state.get("selected_lang") == "kn" else 2),
            label_visibility="collapsed"
        )
        if "Kannada" in lang_choice:
            st.session_state["selected_lang"] = "kn"
        elif "Hindi" in lang_choice:
            st.session_state["selected_lang"] = "hi"
        else:
            st.session_state["selected_lang"] = "en"

        st.markdown("<br>", unsafe_allow_html=True)

        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        # Footer info
        st.markdown("""
            <div style="font-size: 0.7rem; color: #64748B; text-align: center; margin-top: 1.5rem;">
                SchoolGPT v2.0<br>© 2026 RSR Technologies
            </div>
        """, unsafe_allow_html=True)

    return selected_key
