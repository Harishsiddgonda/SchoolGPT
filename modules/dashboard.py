"""
SchoolGPT - Dashboard Module
Executive KPI Cards and Operational Visualizations
RSR Technologies
"""

import streamlit as st
from database.models import get_dashboard_metrics
from services.analytics_service import analytics_service

def render_dashboard(current_user: dict):
    st.markdown("## 📊 SchoolGPT Executive Dashboard")
    st.caption("Real-time telemetry, knowledge repository health, and usage metrics.")

    metrics = get_dashboard_metrics()
    summary = analytics_service.get_summary_metrics()

    # Metric Cards in Row
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown(f"""
            <div class="rsr-metric-card">
                <div class="rsr-metric-label">Total Documents</div>
                <div class="rsr-metric-value">{metrics['total_documents']}</div>
                <div class="rsr-metric-desc">Official files</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="rsr-metric-card">
                <div class="rsr-metric-label">Total Users</div>
                <div class="rsr-metric-value">{metrics['total_users']}</div>
                <div class="rsr-metric-desc">Active: {metrics['active_users']}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="rsr-metric-card">
                <div class="rsr-metric-label">Total Questions</div>
                <div class="rsr-metric-value">{metrics['total_questions']}</div>
                <div class="rsr-metric-desc">Lifetime queries</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="rsr-metric-card">
                <div class="rsr-metric-label">Questions Answered</div>
                <div class="rsr-metric-value" style="color: #059669;">{metrics['questions_answered']}</div>
                <div class="rsr-metric-desc">{summary['satisfaction_rate']}% resolution</div>
            </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
            <div class="rsr-metric-card">
                <div class="rsr-metric-label">Knowledge Size</div>
                <div class="rsr-metric-value" style="color: #2563EB;">{metrics['kb_size']}</div>
                <div class="rsr-metric-desc">Indexed storage</div>
            </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
            <div class="rsr-metric-card">
                <div class="rsr-metric-label">Active Users</div>
                <div class="rsr-metric-value" style="color: #7C3AED;">{metrics['active_users']}</div>
                <div class="rsr-metric-desc">Authorized accounts</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row
    chart_col1, chart_col2 = st.columns([1.5, 1])

    with chart_col1:
        st.plotly_chart(analytics_service.get_queries_over_time_chart(), use_container_width=True)

    with chart_col2:
        st.plotly_chart(analytics_service.get_queries_by_role_chart(), use_container_width=True)

    chart_col3, chart_col4 = st.columns([1.2, 1])

    with chart_col3:
        st.plotly_chart(analytics_service.get_category_distribution_chart(), use_container_width=True)

    with chart_col4:
        st.markdown("### 🔥 Frequently Asked Inquiries")
        top_qs = analytics_service.get_top_questions(limit=5)
        if not top_qs:
            st.info("No query telemetry recorded yet. Ask a question to begin!")
        else:
            for item in top_qs:
                st.markdown(f"""
                    <div style="background: #FFFFFF; border-left: 3px solid #7C3AED; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="font-weight: 600; font-size: 0.88rem; color: #0F172A;">{item['query_text']}</div>
                        <div style="font-size: 0.75rem; color: #64748B; margin-top: 2px;">
                            Asked <b>{item['ask_count']}</b> times • Avg response: <b>{item['avg_time']:.1f}s</b>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
