"""
SchoolGPT – LLM + RAG
AI-Powered School Knowledge Base & Assistant
Organization: RSR Technologies
Tagline: Smart • Reliable • Instant Answers
"""

import streamlit as st
from pathlib import Path
import sys

# Setup root path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Streamlit Page Config
st.set_page_config(
    page_title="SchoolGPT – LLM + RAG | RSR Technologies",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS Stylesheet
def load_css():
    css_path = BASE_DIR / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

from database.db import init_db
from database.models import get_all_users, get_user_by_username
from auth.authentication import authenticate_user
from components.header import render_top_header
from components.sidebar import render_sidebar

# Import functional modules
from modules.dashboard import render_dashboard
from modules.chat import render_chat
from modules.knowledge_base import render_knowledge_base
from modules.document_upload import render_document_upload
from modules.query_history import render_query_history
from modules.bookmarks import render_bookmarks
from modules.analytics import render_analytics
from modules.user_management import render_user_management
from modules.settings import render_settings

# Initialize Database on first run
init_db()

# Auto-seed demo users & documents on fresh deployment (e.g. Streamlit Community Cloud)
try:
    if len(get_all_users()) == 0:
        from scripts.seed_demo_data import seed
        seed()
except Exception:
    pass

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "chat"
if "selected_lang" not in st.session_state:
    st.session_state["selected_lang"] = "en"

# ================= LOGIN VIEW =================
def render_login_view():
    st.markdown("""
        <div style="text-align: center; margin: 1.5rem 0 2rem 0;">
            <div style="display: inline-flex; align-items: center; gap: 12px; background: linear-gradient(135deg, #060B1E 0%, #0B132B 50%, #1D4ED8 100%); color: #FFFFFF; padding: 12px 28px; border-radius: 40px; box-shadow: 0 8px 24px rgba(11, 19, 43, 0.25); border: 1px solid rgba(255,255,255,0.15);">
                <span style="font-size: 2rem;">🎓</span>
                <span style="font-size: 1.6rem; font-weight: 800; letter-spacing: -0.5px;">SchoolGPT <span style="color: #F59E0B;">– LLM + RAG</span></span>
            </div>
            <div style="font-size: 0.95rem; font-weight: 800; color: #DC2626; margin-top: 14px; text-transform: uppercase; letter-spacing: 1.5px;">
                RSR TECHNOLOGIES • SMART • RELIABLE • INSTANT ANSWERS
            </div>
            <div style="font-size: 0.85rem; color: #64748B; margin-top: 4px;">
                AI-Powered School Knowledge Base & Role-Grounded Education Assistant
            </div>
        </div>
    """, unsafe_allow_html=True)

    login_col1, login_col2, login_col3 = st.columns([1, 1.5, 1])

    with login_col2:
        st.markdown("""
            <div style="background: #FFFFFF; border-radius: 16px; border: 1px solid #E2E8F0; padding: 2.2rem; box-shadow: 0 12px 30px rgba(0,0,0,0.06);">
                <div style="font-size: 1.25rem; font-weight: 800; color: #0F172A; margin-bottom: 0.3rem;">
                    🔐 Portal Authentication
                </div>
                <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 1.4rem;">
                    Sign in with your institutional credentials to access role-authorized documents.
                </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username_input = st.text_input("Username or Email", placeholder="e.g. admin or student_aarav")
            password_input = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_login = st.form_submit_button("Sign In to SchoolGPT 🚀", use_container_width=True)

        if submit_login:
            if not username_input or not password_input:
                st.error("Please enter both username and password.")
            else:
                user, err = authenticate_user(username_input, password_input)
                if user:
                    st.session_state["authenticated"] = True
                    st.session_state["current_user"] = user
                    st.session_state["current_page"] = "chat"
                    st.rerun()
                else:
                    st.error(f"❌ {err}")

        st.markdown("</div>", unsafe_allow_html=True)

        # Quick Demo Role Picker
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("⚡ 1-Click Quick Demo Sign-In (Test All 6 Roles)", expanded=True):
            st.caption("Click any persona below to test role-based access control and retrieval immediately:")

            demo_accounts = [
                ("👑 Super Admin", "admin", "AdminPassword123!", "#7C3AED"),
                ("🏫 School Admin", "school_admin", "SchoolAdmin123!", "#1D4ED8"),
                ("🎓 Principal", "principal", "Principal123!", "#0284C7"),
                ("👩‍🏫 Teacher (Sharma)", "teacher_sharma", "Teacher123!", "#059669"),
                ("🎒 Student (Aarav)", "student_aarav", "Student123!", "#D97706"),
                ("👨‍👩‍👧 Parent (Priya)", "parent_priya", "Parent123!", "#DC2626")
            ]

            d_cols = st.columns(2)
            for idx, (label, uname, pwd, color) in enumerate(demo_accounts):
                with d_cols[idx % 2]:
                    if st.button(label, key=f"quick_demo_{uname}", use_container_width=True):
                        user, _ = authenticate_user(uname, pwd)
                        if user:
                            st.session_state["authenticated"] = True
                            st.session_state["current_user"] = user
                            st.session_state["current_page"] = "chat"
                            st.rerun()

        # Footer Contact Information matching reference banner
        st.markdown("""
            <div style="text-align: center; margin-top: 1.5rem; font-size: 0.78rem; color: #64748B; line-height: 1.6;">
                <b>RSR TECHNOLOGIES</b> • www.rsrtechnologies.co.in<br>
                📞 +91 99453 21367 &nbsp;|&nbsp; 📞 +91 77605 94868
            </div>
        """, unsafe_allow_html=True)

# ================= AUTHENTICATED VIEW =================
def render_authenticated_view():
    current_user = st.session_state["current_user"]

    # Top header banner
    render_top_header(current_user)

    # Sidebar navigation
    selected_page = render_sidebar(current_user)

    # Route Dispatcher
    if selected_page == "dashboard":
        render_dashboard(current_user)
    elif selected_page == "chat":
        render_chat(current_user)
    elif selected_page == "knowledge_base":
        render_knowledge_base(current_user)
    elif selected_page == "upload":
        render_document_upload(current_user)
    elif selected_page == "queries":
        render_query_history(current_user)
    elif selected_page == "bookmarks":
        render_bookmarks(current_user)
    elif selected_page == "analytics":
        render_analytics(current_user)
    elif selected_page == "users":
        render_user_management(current_user)
    elif selected_page == "settings":
        render_settings(current_user)
    else:
        render_chat(current_user)

# Main Application Entry
def main():
    if not st.session_state.get("authenticated") or not st.session_state.get("current_user"):
        render_login_view()
    else:
        render_authenticated_view()

if __name__ == "__main__":
    main()
