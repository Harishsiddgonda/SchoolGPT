"""
SchoolGPT - Knowledge Base Repository Module
Allows users to browse, search, and preview institutional documentation.
RSR Technologies
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from database.models import get_accessible_documents
from config.settings import DOCUMENT_CATEGORIES
from rag.document_loader import load_document

def render_knowledge_base(current_user: dict):
    user_role = current_user.get("role", "Student")

    st.markdown('<div class="rsr-section-title">📚 Official School Knowledge Repository</div>', unsafe_allow_html=True)
    st.caption(f"Search, filter, and inspect verified policy documents accessible to role: **{user_role}**")

    # Filter Bar
    f_col1, f_col2, f_col3, f_col4 = st.columns([2.2, 1.2, 1, 1])

    with f_col1:
        search_query = st.text_input("🔍 Search Knowledge Base", placeholder="Search by document title or content keywords...")

    with f_col2:
        category_options = ["All Categories"] + DOCUMENT_CATEGORIES
        selected_category = st.selectbox("Category Filter", options=category_options)

    with f_col3:
        academic_years = ["All Years", "2024-2025", "2023-2024"]
        selected_year = st.selectbox("Academic Year", options=academic_years)

    with f_col4:
        view_mode = st.radio("Display View", options=["Cards", "Table"], horizontal=True)

    # Fetch documents with RBAC
    docs = get_accessible_documents(user_role)

    # Filter docs
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
        st.warning("No documents match your filter criteria or role permissions.")
        return

    if view_mode == "Table":
        table_data = []
        for d in filtered_docs:
            table_data.append({
                "Document Title": d["title"],
                "Category": d["category"],
                "Format": d.get("file_type", "pdf").upper(),
                "Year": d.get("academic_year", "2024-2025"),
                "Chunks": d.get("chunk_count", 0),
                "Status": "INDEXED",
                "Uploaded Date": d.get("upload_date", "N/A")[:10]
            })
        st.dataframe(pd.DataFrame(table_data), use_container_width=True)

    else:
        # Cards View
        grid_cols = st.columns(2)
        for idx, doc in enumerate(filtered_docs):
            with grid_cols[idx % 2]:
                with st.container():
                    st.markdown(f"""
                        <div style="background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; padding: 1.2rem; margin-bottom: 1rem; box-shadow: 0 2px 6px rgba(0,0,0,0.04); height: 100%;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="font-size: 1.5rem;">📄</span>
                                    <div>
                                        <div style="font-size: 1.05rem; font-weight: 700; color: #1D4ED8;">
                                            {doc['title']}
                                        </div>
                                        <div style="font-size: 0.78rem; color: #64748B;">
                                            Category: <b>{doc['category']}</b> • Year: <b>{doc.get('academic_year', '2024-2025')}</b>
                                        </div>
                                    </div>
                                </div>
                                <span style="background: #DCFCE7; color: #15803D; font-size: 0.72rem; font-weight: 700; padding: 3px 8px; border-radius: 12px;">
                                    ✓ INDEXED
                                </span>
                            </div>
                            <div style="font-size: 0.84rem; color: #334155; margin: 10px 0; line-height: 1.45;">
                                {doc.get('description') or 'Official institutional document.'}
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #F1F5F9; padding-top: 8px; font-size: 0.75rem; color: #94A3B8;">
                                <span>Format: <b>{doc.get('file_type', 'pdf').upper()}</b> ({doc.get('chunk_count', 0)} chunks)</span>
                                <span>Roles: <i>{', '.join(doc.get('allowed_roles_list', []))}</i></span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    with st.expander(f"📖 Inspect {doc['title']}", expanded=False):
                        p = Path(doc["file_path"])
                        if p.exists():
                            pages, _, _ = load_document(p)
                            if pages:
                                st.markdown(f"**Total Pages Preserved:** {len(pages)}")
                                for pg in pages[:3]:
                                    st.markdown(f"**--- Page {pg.page_number} ({pg.section}) ---**")
                                    st.text(pg.text[:500] + ("..." if len(pg.text) > 500 else ""))
                        else:
                            st.warning("File is stored virtually in ChromaDB index.")
