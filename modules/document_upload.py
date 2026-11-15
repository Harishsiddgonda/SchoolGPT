"""
SchoolGPT - Document Upload & Management Module
Enables authorized school staff to upload, parse, chunk,
embed and manage school documents.
RSR Technologies
"""

import streamlit as st
from config.settings import DOCUMENT_CATEGORIES, ROLES
from services.document_service import document_service
from database.models import get_all_documents
from auth.permissions import has_permission

def render_document_upload(current_user: dict):
    user_id = current_user.get("id")
    user_role = current_user.get("role", "School Administrator")

    if not has_permission(user_role, "can_upload_docs"):
        st.error("⛔ Access Denied: You do not have permission to upload school documents.")
        return

    st.markdown("## 📤 Document Upload & Ingestion")
    st.caption("Upload official school documents (PDF, DOCX, TXT) to expand the AI Knowledge Base.")

    tab1, tab2 = st.tabs(["➕ Upload New Document", "📋 Manage Uploaded Documents"])

    with tab1:
        with st.form("upload_doc_form", clear_on_submit=False):
            st.markdown("#### Document Metadata & Access Control")

            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Document Title *", placeholder="e.g. Student Handbook 2024-2025")
                category = st.selectbox("Document Category *", options=DOCUMENT_CATEGORIES)
                academic_year = st.selectbox("Academic Year *", options=["2024-2025", "2025-2026", "2023-2024"])

            with col2:
                description = st.text_area("Description / Notes", placeholder="Brief description of the document contents...", height=95)
                allowed_roles = st.multiselect(
                    "Allowed User Roles (Role-Based Access Control) *",
                    options=ROLES,
                    default=ROLES,
                    help="Only users with these roles will be able to search and retrieve from this document."
                )

            st.markdown("#### Select Document File")
            uploaded_file = st.file_uploader(
                "Choose PDF, Word (DOCX), or Text (TXT) file",
                type=["pdf", "docx", "txt"],
                help="Maximum allowed file size: 50 MB"
            )

            submit_upload = st.form_submit_button("🚀 Upload & Index into SchoolGPT", use_container_width=True)

        if submit_upload:
            if not uploaded_file:
                st.error("Please select a file to upload.")
            elif not title.strip():
                st.error("Please provide a document title.")
            elif not allowed_roles:
                st.error("Please select at least one authorized role.")
            else:
                with st.spinner(f"Ingesting '{uploaded_file.name}' into vector database..."):
                    file_bytes = uploaded_file.read()
                    success, msg, doc_id = document_service.process_and_index_document(
                        file_bytes=file_bytes,
                        filename=uploaded_file.name,
                        title=title.strip(),
                        category=category,
                        academic_year=academic_year,
                        description=description.strip(),
                        allowed_roles=allowed_roles,
                        uploaded_by_user_id=user_id
                    )

                if success:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ Upload Failed: {msg}")

    with tab2:
        st.markdown("#### Indexed Knowledge Documents")
        all_docs = get_all_documents()

        if not all_docs:
            st.info("No documents uploaded yet. Use the upload tab above to add documents.")
            return

        for doc in all_docs:
            with st.container():
                d_col1, d_col2, d_col3 = st.columns([3, 1, 1.2])

                with d_col1:
                    st.markdown(f"**📄 {doc['title']}** (`{doc['filename']}`)")
                    st.caption(f"Category: {doc['category']} | Chunks: {doc.get('chunk_count', 0)} | Uploaded: {doc.get('upload_date', 'N/A')}")
                    st.caption(f"Allowed: {', '.join(doc.get('allowed_roles_list', []))}")

                with d_col2:
                    if st.button("🔄 Re-index", key=f"reindex_{doc['id']}"):
                        with st.spinner(f"Re-indexing {doc['title']}..."):
                            re_ok, re_msg = document_service.reindex_document(doc["id"], user_id=user_id)
                        if re_ok:
                            st.success(re_msg)
                            st.rerun()
                        else:
                            st.error(re_msg)

                with d_col3:
                    if has_permission(user_role, "can_delete_docs"):
                        if st.button("🗑️ Delete", key=f"del_{doc['id']}", type="secondary"):
                            with st.spinner(f"Deleting {doc['title']} and removing vectors..."):
                                del_ok, del_msg = document_service.delete_document(doc["id"], user_id=user_id)
                            if del_ok:
                                st.success(del_msg)
                                st.rerun()
                            else:
                                st.error(del_msg)
                    else:
                        st.caption("Delete restricted to Admins")

                st.markdown("---")
