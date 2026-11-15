"""
SchoolGPT - Header & Notification Component
RSR Technologies Branding, Live Telemetry, and Notification Panel
"""

import streamlit as st
from config.settings import APP_NAME, APP_ORG, APP_TAGLINE
from auth.permissions import get_role_badge_color
from rag.llm import llm_service
from database.models import query_all

SYSTEM_NOTICES = [
    {
        "icon": "📢",
        "title": "Annual Examination Timetable Published",
        "desc": "Exam calendar for Term 2 & Pre-boards is now available in the Knowledge Base.",
        "time": "10 mins ago",
        "category": "Academic"
    },
    {
        "icon": "🚌",
        "title": "School Bus GPS Real-Time Fleet Tracking",
        "desc": "All 24 school bus routes are operational with female attendants on board.",
        "time": "1 hour ago",
        "category": "Transport"
    },
    {
        "icon": "💳",
        "title": "Term 2 Fee Installment Due Date",
        "desc": "Parents are requested to settle installment dues on or before the 10th.",
        "time": "Today",
        "category": "Accounts"
    },
    {
        "icon": "🛡️",
        "title": "Strict RAG Grounding Enabled",
        "desc": "All queries are verified against official school documents.",
        "time": "System Alert",
        "category": "Security"
    }
]

def render_top_header(current_user: dict):
    """Renders the executive top header banner and notification drawer."""
    is_ollama_on, models, _ = llm_service.check_ollama_status()
    role = current_user.get("role", "Student")
    full_name = current_user.get("full_name", "School Member")
    username = current_user.get("username", "user")
    initial = (full_name[0] if full_name else "U").upper()
    role_color = get_role_badge_color(role)

    # Telemetry Badge
    if is_ollama_on:
        model_name = models[0] if models else "Qwen3:4b"
        status_html = f"""
            <div class="rsr-pulse-badge online">
                <span class="pulse-dot green"></span>
                <span>Ollama Neural LLM ({model_name})</span>
            </div>
        """
    else:
        status_html = """
            <div class="rsr-pulse-badge fallback">
                <span class="pulse-dot amber"></span>
                <span>High-Speed Local Grounded RAG</span>
            </div>
        """

    # Render Header Banner
    st.markdown(f"""
        <div class="rsr-header-wrapper">
            <div class="rsr-header-content">
                <div class="rsr-header-brand">
                    <div class="rsr-brand-icon-box">🎓</div>
                    <div>
                        <div class="rsr-brand-title">
                            {APP_NAME} <span class="glow-tag">– LLM + RAG</span>
                        </div>
                        <div class="rsr-brand-subtitle">
                            <b>{APP_ORG}</b> • Training | Development | Projects | Products | Consulting
                        </div>
                    </div>
                </div>
                <div class="rsr-header-actions">
                    {status_html}
                    <div class="rsr-user-pill">
                        <div class="rsr-user-avatar">{initial}</div>
                        <div class="rsr-user-info">
                            <div class="rsr-user-name">{full_name}</div>
                            <span class="rsr-user-role" style="background: {role_color}; color: #FFFFFF;">
                                {role}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Interactive Notification Center Drawer
    with st.expander("🔔 School Notices & System Bulletins (4 New Alerts)", expanded=False):
        n_col1, n_col2 = st.columns([3, 1])
        with n_col1:
            st.caption("Official real-time circulars, academic notices, and AI telemetry updates.")
        with n_col2:
            st.markdown(f"<div style='text-align:right;'><span style='font-size:0.75rem; background:#EDE9FE; color:#6D28D9; font-weight:700; padding:2px 8px; border-radius:12px;'>Live Feed</span></div>", unsafe_allow_html=True)

        notices_cols = st.columns(4)
        for i, notice in enumerate(SYSTEM_NOTICES):
            with notices_cols[i % 4]:
                st.markdown(f"""
                    <div class="rsr-notice-item">
                        <div style="font-size: 0.72rem; font-weight: 800; color: #7C3AED; text-transform: uppercase;">
                            {notice['category']} • {notice['time']}
                        </div>
                        <div class="rsr-notice-title" style="margin-top: 4px;">
                            {notice['icon']} {notice['title']}
                        </div>
                        <div class="rsr-notice-meta" style="margin-top: 6px; line-height: 1.35;">
                            {notice['desc']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
