"""
SchoolGPT - Analytics & Reporting Module
In-depth query intelligence, user engagement, and data export.
RSR Technologies
"""

import streamlit as st
from services.analytics_service import analytics_service
from auth.permissions import has_permission

def render_analytics(current_user: dict):
    user_role = current_user.get("role", "School Administrator")

    if not has_permission(user_role, "can_view_analytics"):
        st.error("⛔ Access Denied: You do not have permission to view institutional analytics.")
        return

    st.markdown("## 📈 SchoolGPT Query Intelligence & Analytics")
    st.caption("Comprehensive analysis of inquiry volume, resolution rates, and user patterns.")

    summary = analytics_service.get_summary_metrics()

    # KPI Summary Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Inquiries", summary["total_queries"])
    with col2:
        st.metric("Past 7 Days", summary["week_queries"])
    with col3:
        st.metric("Past 30 Days", summary["month_queries"])
    with col4:
        st.metric("Grounded Resolution Rate", f"{summary['satisfaction_rate']}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # Plotly Visualizations
    tab1, tab2, tab3 = st.tabs(["📊 Usage Trends", "👥 Role Demographics", "📥 Export & Raw Data"])

    with tab1:
        st.plotly_chart(analytics_service.get_queries_over_time_chart(), use_container_width=True)
        st.plotly_chart(analytics_service.get_category_distribution_chart(), use_container_width=True)

    with tab2:
        st.plotly_chart(analytics_service.get_queries_by_role_chart(), use_container_width=True)

        st.markdown("### 🏆 Top Frequency School Queries")
        top_qs = analytics_service.get_top_questions(limit=10)
        if top_qs:
            st.dataframe(top_qs, use_container_width=True)
        else:
            st.info("No queries recorded yet.")

    with tab3:
        st.markdown("### Export Institutional Query Logs")
        st.caption("Download complete historical question-answering records for compliance and review.")

        export_df = analytics_service.get_export_dataframe()
        if not export_df.empty:
            csv_data = export_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Queries CSV Report",
                data=csv_data,
                file_name="schoolgpt_query_intelligence_report.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.dataframe(export_df.head(20), use_container_width=True)
        else:
            st.info("No query logs available to export.")
