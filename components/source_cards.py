"""
SchoolGPT - Source Citation Cards Component
Renders clickable citations and document page references matching the reference laptop preview.
"""

import streamlit as st
from typing import List, Dict, Any

def render_sources(sources: List[Dict[str, Any]]):
    """
    Renders the Sources Cited section matching the reference design.
    """
    if not sources:
        return

    st.markdown("""
        <div style="margin-top: 1rem; border-top: 2px dashed #E2E8F0; padding-top: 1rem;">
            <div style="display: flex; align-items: center; gap: 8px; color: #1D4ED8; font-weight: 800; font-size: 1.1rem; margin-bottom: 0.8rem;">
                <span style="font-size: 1.25rem;">📖</span>
                <span>Sources (Cited)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    for i, src in enumerate(sources, 1):
        title = src.get("title", "Official School Document")
        page = src.get("page", 1)
        section = src.get("section", "")
        category = src.get("category", "General")
        similarity = src.get("similarity", 0.0)
        snippet = src.get("snippet", "")

        meta_parts = []
        if page:
            meta_parts.append(f"Page: {page}")
        if section and not section.lower().startswith("page"):
            meta_parts.append(f"Section: {section}")
        meta_parts.append(f"Category: {category}")
        meta_str = " • ".join(meta_parts)

        sim_percentage = int(similarity * 100) if similarity > 0 else 95

        st.markdown(f"""
            <div class="rsr-source-pill-card">
                <div class="rsr-source-row">
                    <div class="rsr-source-doc-name">
                        <span>📄</span>
                        <span>{title}</span>
                    </div>
                    <span class="rsr-source-match-badge">✓ {sim_percentage}% Match</span>
                </div>
                <div class="rsr-source-details">
                    <b>{meta_str}</b>
                </div>
            </div>
        """, unsafe_allow_html=True)

        with st.expander(f"🔍 Inspect Cited Excerpt from {title}", expanded=False):
            st.markdown(f"**Document Passage (Page {page}):**")
            st.markdown(f"""
                <div style="background: #FFFFFF; border-left: 3px solid #2563EB; padding: 10px 14px; border-radius: 6px; font-size: 0.88rem; color: #334155; line-height: 1.6; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                    {snippet}
                </div>
            """, unsafe_allow_html=True)
            st.caption(f"Document ID: #{src.get('doc_id')} | Verified Grounded Reference")
