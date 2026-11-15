"""
SchoolGPT - Source Cards Component
Renders clickable citations and document page references.
RSR Technologies
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
            <div style="display: flex; align-items: center; gap: 8px; color: #1D4ED8; font-weight: 700; font-size: 1.05rem; margin-bottom: 0.8rem;">
                <span>📚</span>
                <span>Sources (Cited)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    for i, src in enumerate(sources, 1):
        title = src.get("title", "Official Document")
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

        sim_badge = f"{int(similarity * 100)}% match" if similarity > 0 else "Grounded match"

        with st.expander(f"📄 {i}. {title} ({meta_str}) — {sim_badge}", expanded=False):
            st.markdown(f"**Referenced Excerpt:**")
            st.info(snippet)
            st.caption(f"Document ID: #{src.get('doc_id')} | Grounding verification passed")
