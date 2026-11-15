"""
SchoolGPT - Analytics & Reporting Module
In-depth query intelligence, user engagement, and compliance export.
RSR Technologies
"""

import streamlit as st
from services.analytics_service import analytics_service
from auth.permissions import has_permission

def render_analytics(current_user: dict):
    user_role = current_user.get("role", "School Administrator")

    if not has_permission(user_role, "can_view_analytics"):
        st.error("⛔ Access Denied: Institutional analytics are restricted to Administrators and Principals.")
        return

    st.markdown('<div class="rsr-section-title">📈 Institutional AI Intelligence & Analytics</div>', unsafe_allow_html=True)
    st.caption("Deep telemetry, inquiry trends, role engagement metrics, and resolution logs.")

    summary = analytics_service.get_summary_metrics()

    # KPI Summary Cards in a 4-column row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Inquiries Recorded", summary["total_queries"], "Lifetime Telemetry")
    with col2:
        st.metric("Inquiries Past 7 Days", summary["week_queries"], "Recent Activity")
    with col3:
        st.metric("Inquiries Past 30 Days", summary["month_queries"], "Monthly Volume")
    with col4:
        st.metric("Grounded Resolution Rate", f"{summary['satisfaction_rate']}%", "Strict Grounding")

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Query Volume Trends", "👥 Role Demographics & Topics", "📥 Audit Export"])

    with tab1:
        st.plotly_chart(analytics_service.get_queries_over_time_chart(), use_container_width=True)
        st.plotly_chart(analytics_service.get_category_distribution_chart(), use_container_width=True)

    with tab2:
        c_left, c_right = st.columns([1, 1.2])
        with c_left:
            st.plotly_chart(analytics_service.get_queries_by_role_chart(), use_container_width=True)
        with c_right:
            st.markdown("#### Most Frequently Asked Topics")
            top_qs = analytics_service.get_top_questions(limit=8)
            if top_qs:
                st.dataframe(top_qs, use_container_width=True)
            else:
                st.info("No queries recorded yet.")

    with tab3:
        st.markdown("#### Institutional Compliance & Query Audit Log")
        st.caption("Export historical query activity for institutional audit and review.")

        export_df = analytics_service.get_export_dataframe()
        if not export_df.empty:
            csv_data = export_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Full Institutional Audit Report (CSV)",
                data=csv_data,
                file_name="schoolgpt_compliance_audit_report.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.dataframe(export_df.head(25), use_container_width=True)
        else:
            st.info("No query logs available for export.")
