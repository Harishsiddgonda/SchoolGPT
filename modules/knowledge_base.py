"""
SchoolGPT - Knowledge Base Repository Module
Allows users to browse and search accessible school documentation.
RSR Technologies
"""

import streamlit as st
from database.models import get_accessible_documents
from config.settings import DOCUMENT_CATEGORIES

def render_knowledge_base(current_user: dict):
    user_role = current_user.get("role", "Student")

    st.markdown("## 📚 School Knowledge Base")
    st.caption(f"Explore official policy documents and circulars accessible to: **{user_role}**")

    # Filter & Search Bar
    f_col1, f_col2, f_col3 = st.columns([2, 1.2, 1.2])

    with f_col1:
        search_query = st.text_input("🔍 Search documents by title or topic", placeholder="e.g. Leave, Transport, Fees...")

    with f_col2:
        category_options = ["All Categories"] + DOCUMENT_CATEGORIES
        selected_category = st.selectbox("Category Filter", options=category_options)

    with f_col3:
        academic_years = ["All Years", "2024-2025", "2023-2024"]
        selected_year = st.selectbox("Academic Year", options=academic_years)

    # Fetch documents with role enforcement
    docs = get_accessible_documents(user_role)

    # Apply filters
    filtered_docs = []
    for d in docs:
        if search_query:
            sq = search_query.lower()
            if sq not in d["title"].lower() and sq not in (d.get("description") or "").lower():
                continue
        if selected_category != "All Categories" and d["category"] != selected_category:
            continue
        if selected_year != "All Years" and d.get("academic_year") != selected_year:
            continue
        filtered_docs.append(d)

    st.markdown(f"**Found {len(filtered_docs)} accessible documents:**")

    if not filtered_docs:
        st.warning("No documents found matching your filter criteria or role permissions.")
        return

    # Render document cards
    for doc in filtered_docs:
        with st.container():
            st.markdown(f"""
                <div style="background: #FFFFFF; border-radius: 10px; border: 1px solid #E2E8F0; padding: 1.2rem; margin-bottom: 0.8rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <div style="font-size: 1.15rem; font-weight: 700; color: #1D4ED8;">
                                📄 {doc['title']}
                            </div>
                            <div style="font-size: 0.82rem; color: #64748B; margin-top: 4px;">
                                <b>Category:</b> {doc['category']} &nbsp;|&nbsp; 
                                <b>Year:</b> {doc.get('academic_year', '2024-2025')} &nbsp;|&nbsp; 
                                <b>Format:</b> {doc.get('file_type', 'pdf').upper()} &nbsp;|&nbsp; 
                                <b>Chunks:</b> {doc.get('chunk_count', 0)}
                            </div>
                        </div>
                        <div>
                            <span style="background: #DCFCE7; color: #15803D; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 12px;">
                                ✓ INDEXED & READY
                            </span>
                        </div>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.88rem; color: #334155;">
                        {doc.get('description') or 'Official school documentation.'}
                    </div>
                    <div style="margin-top: 10px; font-size: 0.75rem; color: #94A3B8;">
                        Allowed Roles: <i>{', '.join(doc.get('allowed_roles_list', []))}</i>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            with st.expander(f"📖 Preview content of {doc['title']}", expanded=False):
                try:
                    from rag.document_loader import load_document
                    from pathlib import Path
                    p = Path(doc["file_path"])
                    if p.exists():
                        pages, _, _ = load_document(p)
                        if pages:
                            st.markdown(f"**Document Page Count:** {len(pages)} pages")
                            for page in pages[:3]:
                                st.markdown(f"**--- Page {page.page_number} ({page.section}) ---**")
                                st.text(page.text[:600] + ("..." if len(page.text) > 600 else ""))
                        else:
                            st.info("No preview text available.")
                    else:
                        st.warning("Original document file is not found on disk.")
                except Exception as e:
                    st.error(f"Error reading preview: {str(e)}")
