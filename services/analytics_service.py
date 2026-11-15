"""
SchoolGPT - Analytics & Reporting Service
Interactive Plotly visualizations and metrics aggregation.
RSR Technologies
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
from database.db import query_all, query_one
from config.settings import THEME_COLORS

class AnalyticsService:
    def get_summary_metrics(self) -> Dict[str, Any]:
        """Calculates key operational figures."""
        total_queries = query_one("SELECT COUNT(*) as c FROM query_history")["c"] or 0
        today_queries = query_one("SELECT COUNT(*) as c FROM query_history WHERE date(created_at) = date('now')")["c"] or 0
        week_queries = query_one("SELECT COUNT(*) as c FROM query_history WHERE created_at >= date('now', '-7 days')")["c"] or 0
        month_queries = query_one("SELECT COUNT(*) as c FROM query_history WHERE created_at >= date('now', '-30 days')")["c"] or 0
        
        answered_queries = query_one("""
            SELECT COUNT(*) as c FROM query_history 
            WHERE answer_text NOT LIKE '%could not find reliable information%'
            AND answer_text NOT LIKE '%ವಿಶ್ವಾಸಾರ್ಹ ಮಾಹಿತಿ ಕಂಡುಬಂದಿಲ್ಲ%'
            AND answer_text NOT LIKE '%विश्वसनीय जानकारी नहीं मिली%'
        """)["c"] or 0

        unanswered = total_queries - answered_queries
        satisfaction_rate = round((answered_queries / total_queries * 100), 1) if total_queries > 0 else 100.0

        return {
            "total_queries": total_queries,
            "today_queries": today_queries,
            "week_queries": week_queries,
            "month_queries": month_queries,
            "answered_queries": answered_queries,
            "unanswered_queries": unanswered,
            "satisfaction_rate": satisfaction_rate
        }

    def get_queries_over_time_chart(self) -> go.Figure:
        """Daily query trend chart."""
        rows = query_all("""
            SELECT date(created_at) as query_date, COUNT(*) as query_count 
            FROM query_history 
            GROUP BY date(created_at) 
            ORDER BY query_date ASC 
            LIMIT 30
        """)
        if not rows:
            df = pd.DataFrame({"query_date": [pd.Timestamp.now().strftime("%Y-%m-%d")], "query_count": [0]})
        else:
            df = pd.DataFrame(rows)

        fig = px.area(
            df,
            x="query_date",
            y="query_count",
            title="Daily Query Volume (Last 30 Days)",
            labels={"query_date": "Date", "query_count": "Number of Queries"},
            color_discrete_sequence=[THEME_COLORS["royal_blue"]]
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(248,250,252,1)",
            font=dict(family="Inter, sans-serif"),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return fig

    def get_queries_by_role_chart(self) -> go.Figure:
        """Query distribution by user role."""
        rows = query_all("""
            SELECT u.role, COUNT(q.id) as query_count 
            FROM query_history q
            JOIN users u ON q.user_id = u.id
            GROUP BY u.role
        """)
        if not rows:
            df = pd.DataFrame({"role": ["Student", "Parent", "Teacher"], "query_count": [1, 1, 1]})
        else:
            df = pd.DataFrame(rows)

        fig = px.pie(
            df,
            values="query_count",
            names="role",
            title="Queries by User Role",
            hole=0.45,
            color_discrete_sequence=[
                THEME_COLORS["royal_blue"],
                THEME_COLORS["purple_gradient_start"],
                "#0284C7",
                "#10B981",
                "#F59E0B",
                "#EF4444"
            ]
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return fig

    def get_category_distribution_chart(self) -> go.Figure:
        """Documents by category chart."""
        rows = query_all("""
            SELECT category, COUNT(*) as doc_count, SUM(chunk_count) as total_chunks
            FROM documents
            GROUP BY category
            ORDER BY doc_count DESC
        """)
        if not rows:
            df = pd.DataFrame({"category": ["General"], "doc_count": [0], "total_chunks": [0]})
        else:
            df = pd.DataFrame(rows)

        fig = px.bar(
            df,
            x="category",
            y="doc_count",
            title="Knowledge Base Documents by Category",
            labels={"category": "Category", "doc_count": "Document Count"},
            color="doc_count",
            color_continuous_scale="Purples"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(248,250,252,1)",
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_tickangle=-30
        )
        return fig

    def get_top_questions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Most frequently asked or recent questions."""
        return query_all("""
            SELECT query_text, COUNT(*) as ask_count, MAX(created_at) as last_asked, AVG(response_time_sec) as avg_time
            FROM query_history
            GROUP BY query_text
            ORDER BY ask_count DESC, last_asked DESC
            LIMIT ?
        """, (limit,))

    def get_export_dataframe(self) -> pd.DataFrame:
        """Returns complete query history as DataFrame for CSV export."""
        rows = query_all("""
            SELECT 
                q.id,
                u.username,
                u.role,
                q.query_text,
                q.answer_text,
                q.language,
                q.response_time_sec,
                q.created_at
            FROM query_history q
            LEFT JOIN users u ON q.user_id = u.id
            ORDER BY q.created_at DESC
        """)
        return pd.DataFrame(rows)

analytics_service = AnalyticsService()
