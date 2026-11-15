"""
SchoolGPT - Sidebar Navigation Component
Faithfully structured after RSR Technologies visual guidelines and laptop mockup.
"""

import streamlit as st
from auth.permissions import has_permission, get_role_badge_color
from config.settings import APP_ORG

def render_sidebar(current_user: dict) -> str:
    """
    Renders the navigation menu and returns the selected route.
    """
    user_role = current_user.get("role", "Student")
    full_name = current_user.get("full_name", "School Member")
    username = current_user.get("username", "user")
    initial = (full_name[0] if full_name else "U").upper()
    role_color = get_role_badge_color(user_role)

    with st.sidebar:
        # Organization Header
        st.markdown(f"""
            <div class="rsr-sidebar-header">
                <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                    <span style="font-size: 1.6rem;">🎓</span>
                    <span class="rsr-sidebar-logo-text"><span style="color: #60A5FA;">RSR</span> TECH</span>
                </div>
                <div class="rsr-sidebar-tagline">
                    AI For Education • SchoolGPT
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Primary Action Button: "Ask a Question" (Matches Laptop Mockup in Reference Photo!)
        if st.button("✨ Ask SchoolGPT", key="btn_primary_ask", help="Open Conversational AI Assistant", use_container_width=True):
            st.session_state["current_page"] = "chat"
            st.rerun()

        st.markdown('<div class="rsr-nav-section-title">NAVIGATION MENU</div>', unsafe_allow_html=True)

        # Build accessible navigation options based on permissions
        nav_options = []

        if has_permission(user_role, "can_view_dashboard"):
            nav_options.append(("📊 Dashboard", "dashboard"))
        else:
            # Student/Parent personalized portal view
            nav_options.append(("🏠 My Portal", "dashboard"))

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

        nav_options.append(("⚙️ Settings", "settings"))

        labels = [item[0] for item in nav_options]
        keys = [item[1] for item in nav_options]

        current_nav = st.session_state.get("current_page", "chat")
        default_index = keys.index(current_nav) if current_nav in keys else 0

        selected_label = st.radio(
            "Main Navigation",
            options=labels,
            index=default_index,
            label_visibility="collapsed"
        )

        selected_key = keys[labels.index(selected_label)]
        st.session_state["current_page"] = selected_key

        st.markdown('<div class="rsr-nav-section-title">LANGUAGE PREFERENCE</div>', unsafe_allow_html=True)

        # Multilingual Selector
        lang_choice = st.selectbox(
            "Language Selector",
            options=["🇬🇧 English", "🇮🇳 Kannada (ಕನ್ನಡ)", "🇮🇳 Hindi (हिन्दी)"],
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

        # Micro User Card & Logout
        st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 12px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 34px; height: 34px; border-radius: 50%; background: linear-gradient(135deg, #2563EB, #7C3AED); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.85rem; color: #FFF;">
                        {initial}
                    </div>
                    <div style="line-height: 1.2; overflow: hidden;">
                        <div style="font-size: 0.82rem; font-weight: 700; color: #FFF; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{full_name}</div>
                        <span style="font-size: 0.68rem; font-weight: 700; color: #CBD5E1; background: {role_color}; padding: 1px 6px; border-radius: 4px; display: inline-block; margin-top: 2px;">
                            {user_role}
                        </span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Sign Out", key="btn_logout_sidebar", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.markdown(f"""
            <div style="font-size: 0.68rem; color: #64748B; text-align: center; margin-top: 1rem; line-height: 1.4;">
                SchoolGPT v2.5 Enterprise<br>
                © 2026 {APP_ORG}
            </div>
        """, unsafe_allow_html=True)

    return selected_key
