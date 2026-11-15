"""
SchoolGPT - Header Component
RSR Technologies Branding & User Session Header
"""

import streamlit as st
from config.settings import APP_NAME, APP_ORG, APP_TAGLINE
from auth.permissions import get_role_badge_color
from rag.llm import llm_service

def render_top_header(current_user: dict):
    """Renders the top executive banner."""
    is_ollama_on, models, _ = llm_service.check_ollama_status()
    role = current_user.get("role", "Student")
    full_name = current_user.get("full_name", "School Member")
    role_color = get_role_badge_color(role)

    ollama_badge = (
        '<span class="rsr-status-pill rsr-status-online">🟢 Ollama LLM Ready</span>'
        if is_ollama_on
        else '<span class="rsr-status-pill rsr-status-offline">🟡 Fallback Local RAG</span>'
    )

    st.markdown(f"""
        <div class="rsr-top-banner">
            <div>
                <div class="rsr-brand-title">
                    <span>🎓</span>
                    <span>{APP_NAME} <span style="font-size: 1.1rem; color: #F59E0B; font-weight: 600;">– LLM + RAG</span></span>
                </div>
                <div class="rsr-brand-subtitle">
                    {APP_ORG} • AI-Powered School Knowledge Base & Assistant
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 15px;">
                <div class="rsr-tagline-badge">
                    ⚡ {APP_TAGLINE}
                </div>
                <div>{ollama_badge}</div>
                <div style="text-align: right; border-left: 1px solid rgba(255,255,255,0.2); padding-left: 14px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #FFFFFF;">👤 {full_name}</div>
                    <span class="rsr-role-badge" style="background: {role_color};">{role}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
