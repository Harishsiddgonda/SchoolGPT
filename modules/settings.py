"""
SchoolGPT - Settings & System Configuration Module
RSR Technologies
"""

import streamlit as st
from config.settings import (
    OLLAMA_BASE_URL,
    OLLAMA_LLM_MODEL,
    OLLAMA_EMBED_MODEL,
    CHUNK_SIZE,
    TOP_K_RESULTS,
    SIMILARITY_THRESHOLD
)
from database.models import get_all_settings, set_setting, log_activity
from rag.llm import llm_service
from rag.embeddings import embedding_service
from rag.vector_store import vector_store
from auth.authentication import change_password

def render_settings(current_user: dict):
    user_id = current_user.get("id")
    user_role = current_user.get("role", "Student")
    is_admin = user_role in ("Super Admin", "School Administrator")

    st.markdown("## ⚙️ SchoolGPT Settings & Configuration")
    st.caption("Manage AI model endpoints, vector repository parameters, and personal profile.")

    tabs = ["👤 Profile & Security"]
    if is_admin:
        tabs.extend(["🤖 AI & Ollama Configuration", "🏫 School Metadata", "🗄️ Vector Database Health"])

    tab_objs = st.tabs(tabs)

    # Tab 1: Profile & Password
    with tab_objs[0]:
        st.markdown("#### Personal Security Settings")
        st.info(f"Signed in as **{current_user.get('full_name')}** (`@{current_user.get('username')}`) with role **{user_role}**")

        with st.form("change_pwd_form"):
            curr_pwd = st.text_input("Current Password", type="password")
            new_pwd = st.text_input("New Password", type="password")
            confirm_pwd = st.text_input("Confirm New Password", type="password")
            submit_pwd = st.form_submit_button("Update Password")

        if submit_pwd:
            if new_pwd != confirm_pwd:
                st.error("New passwords do not match.")
            else:
                ok, msg = change_password(user_id, curr_pwd, new_pwd)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    # Tab 2: AI & Ollama (Admin only)
    if is_admin and len(tab_objs) > 1:
        with tab_objs[1]:
            st.markdown("#### Ollama LLM & Embeddings Diagnostic")

            is_online, installed_models, status_msg = llm_service.check_ollama_status()

            if is_online:
                st.success(f"🟢 **Ollama Connected** at `{OLLAMA_BASE_URL}`")
                st.markdown(f"**Available Local Models:** `{', '.join(installed_models) if installed_models else 'None downloaded yet'}`")
            else:
                st.warning(f"🟡 **Ollama Status:** {status_msg}")
                st.markdown("""
                    <div style="background: #FFFBEB; border: 1px solid #FCD34D; padding: 12px; border-radius: 8px; font-size: 0.85rem; color: #92400E;">
                        <b>How to start Ollama on Windows:</b><br>
                        1. Open PowerShell or Command Prompt.<br>
                        2. Run: <code>ollama serve</code><br>
                        3. In another terminal, pull the recommended model: <code>ollama run qwen3:4b</code> (or <code>ollama run llama3.2:3b</code>)<br>
                        4. Pull the embedding model: <code>ollama pull nomic-embed-text-v2-moe</code><br>
                        <i>SchoolGPT will automatically use the active models once available. In the meantime, SchoolGPT's built-in local grounded engine and deterministic vectorizer are fully operational!</i>
                    </div>
                """, unsafe_allow_html=True)

            embed_status = embedding_service.get_status_info()
            st.markdown(f"**Active Embedding Engine:** `{embed_status['engine']}` (Dimension: {embed_status['dimension']})")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### RAG Hyperparameters")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.number_input("Chunk Size (Characters)", value=CHUNK_SIZE, disabled=True)
            with c2:
                st.number_input("Top-K Retrieved Chunks", value=TOP_K_RESULTS, disabled=True)
            with c3:
                st.number_input("Minimum Similarity Threshold", value=SIMILARITY_THRESHOLD, disabled=True)

    # Tab 3: School Info (Admin only)
    if is_admin and len(tab_objs) > 2:
        with tab_objs[2]:
            st.markdown("#### Institution Profile")
            settings = get_all_settings()

            with st.form("school_info_form"):
                s_name = st.text_input("School Name", value=settings.get("school_name", "RSR International Academy"))
                s_year = st.text_input("Active Academic Year", value=settings.get("academic_year", "2024-2025"))
                s_email = st.text_input("Official Email", value=settings.get("contact_email", "support@rsrtechnologies.co.in"))
                s_phone = st.text_input("Official Phone", value=settings.get("contact_phone", "+91 99453 21367 / +91 77605 94868"))
                s_web = st.text_input("Website", value=settings.get("website", "www.rsrtechnologies.co.in"))
                save_info = st.form_submit_button("Save Institutional Info")

            if save_info:
                set_setting("school_name", s_name)
                set_setting("academic_year", s_year)
                set_setting("contact_email", s_email)
                set_setting("contact_phone", s_phone)
                set_setting("website", s_web)
                log_activity(user_id, "SETTINGS_UPDATED", "Updated institutional profile settings")
                st.success("School information saved successfully.")

    # Tab 4: Vector DB Health (Admin only)
    if is_admin and len(tab_objs) > 3:
        with tab_objs[3]:
            st.markdown("#### ChromaDB Knowledge Vector Index")
            vec_count = vector_store.count()
            st.metric("Total Indexed Vectors in ChromaDB", vec_count)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("⚠️ **Danger Zone: Reset Vector Index**")
            st.caption("Clearing the vector database will purge all indexed embeddings. Uploaded files will remain in storage and can be re-indexed.")
            if st.button("🗑️ Reset All Vector Embeddings", type="secondary"):
                vector_store.reset_collection()
                log_activity(user_id, "CHROMA_RESET", "Vector collection cleared by administrator")
                st.warning("ChromaDB vector collection has been reset.")
                st.rerun()
