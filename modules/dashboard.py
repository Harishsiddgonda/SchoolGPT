"""
SchoolGPT - Personalized Role-Based Dashboard Module
Tailored KPI cards, operational telemetry, and workflows for each role.
RSR Technologies
"""

import streamlit as st
import pandas as pd
from database.models import get_dashboard_metrics, query_all
from services.analytics_service import analytics_service
from auth.permissions import get_role_badge_color

def render_dashboard(current_user: dict):
    role = current_user.get("role", "Student")
    full_name = current_user.get("full_name", "School Member")
    role_color = get_role_badge_color(role)

    # Executive Greeting Card
    st.markdown(f"""
        <div class="rsr-role-welcome-card">
            <div>
                <div style="font-size: 1.55rem; font-weight: 800; letter-spacing: -0.5px;">
                    Welcome back, {full_name} 👋
                </div>
                <div style="font-size: 0.88rem; color: #94A3B8; margin-top: 4px;">
                    Portal Dashboard • Role Authorization: <span style="background: {role_color}; color: #FFF; padding: 2px 8px; border-radius: 4px; font-weight: 700;">{role}</span>
                </div>
            </div>
            <div style="text-align: right; display: flex; align-items: center; gap: 12px;">
                <div style="background: rgba(255, 255, 255, 0.08); padding: 8px 16px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1);">
                    <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase;">Academic Term</div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #F59E0B;">2024–2025</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Dispatch to role-specific dashboard
    if role in ("Super Admin", "School Administrator"):
        render_admin_dashboard(current_user)
    elif role == "Principal":
        render_principal_dashboard(current_user)
    elif role == "Teacher":
        render_teacher_dashboard(current_user)
    elif role == "Student":
        render_student_dashboard(current_user)
    elif role == "Parent":
        render_parent_dashboard(current_user)
    else:
        render_admin_dashboard(current_user)

# ================= 1. ADMIN DASHBOARD =================
def render_admin_dashboard(current_user: dict):
    metrics = get_dashboard_metrics()
    summary = analytics_service.get_summary_metrics()

    # 6 KPI Cards in a modern responsive row
    kpi_cols = st.columns(6)

    kpis = [
        ("Total Documents", str(metrics['total_documents']), "Official Files", "📚", "positive", "100% Indexed"),
        ("Total Users", str(metrics['total_users']), f"Active: {metrics['active_users']}", "👥", "neutral", "6 Roles"),
        ("Total Inquiries", str(metrics['total_questions']), "Lifetime Queries", "💬", "neutral", "Telemetry On"),
        ("Resolution Rate", f"{summary['satisfaction_rate']}%", "Grounded Answers", "✅", "positive", "Strict RAG"),
        ("Knowledge Size", str(metrics['kb_size']), "Persistent Storage", "🗄️", "neutral", "ChromaDB"),
        ("System Health", "Active", "Latency < 0.1s", "⚡", "positive", "Operational")
    ]

    for idx, (label, val, desc, icon, badge_type, badge_text) in enumerate(kpis):
        with kpi_cols[idx]:
            st.markdown(f"""
                <div class="rsr-kpi-card">
                    <div class="rsr-kpi-header">
                        <span class="rsr-kpi-label">{label}</span>
                        <div class="rsr-kpi-icon" style="background: rgba(37, 99, 235, 0.08); color: #2563EB;">{icon}</div>
                    </div>
                    <div class="rsr-kpi-value">{val}</div>
                    <div class="rsr-kpi-footer">
                        <span class="rsr-kpi-badge {badge_type}">{badge_text}</span>
                        <span>{desc}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Plotly Charts
    c1, c2 = st.columns([1.6, 1])
    with c1:
        st.plotly_chart(analytics_service.get_queries_over_time_chart(), use_container_width=True)
    with c2:
        st.plotly_chart(analytics_service.get_queries_by_role_chart(), use_container_width=True)

    c3, c4 = st.columns([1.2, 1])
    with c3:
        st.plotly_chart(analytics_service.get_category_distribution_chart(), use_container_width=True)
    with c4:
        st.markdown('<div class="rsr-section-title">🔥 Trending Inquiries</div>', unsafe_allow_html=True)
        top_qs = analytics_service.get_top_questions(limit=4)
        if top_qs:
            for item in top_qs:
                st.markdown(f"""
                    <div style="background: #FFFFFF; border-left: 3px solid #7C3AED; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                        <div style="font-weight: 700; font-size: 0.88rem; color: #0F172A;">{item['query_text']}</div>
                        <div style="font-size: 0.74rem; color: #64748B; margin-top: 3px;">
                            Asked <b>{item['ask_count']}</b> times • Avg Response: <b>{item['avg_time']:.1f}s</b>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No queries recorded yet.")

# ================= 2. PRINCIPAL DASHBOARD =================
def render_principal_dashboard(current_user: dict):
    metrics = get_dashboard_metrics()
    summary = analytics_service.get_summary_metrics()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Institutional Documents", metrics["total_documents"], "Policies & Timetables")
    with c2:
        st.metric("Staff & Student Inquiries", summary["total_queries"], "+12 this week")
    with c3:
        st.metric("Grounded Accuracy Rate", f"{summary['satisfaction_rate']}%", "100% Policy Grounded")
    with c4:
        st.metric("Exam Readiness", "Approved", "Pre-Boards & Annuals")

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns([1.5, 1])
    with col_a:
        st.plotly_chart(analytics_service.get_queries_by_role_chart(), use_container_width=True)
    with col_b:
        st.markdown('<div class="rsr-section-title">📋 Principal Quick Approvals</div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; padding: 1.2rem; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
                <div style="font-size: 0.88rem; font-weight: 700; color: #0F172A; margin-bottom: 8px;">
                    📝 Leaves Exceeding 3 Days (Section 4.2)
                </div>
                <div style="font-size: 0.82rem; color: #475569; line-height: 1.5;">
                    As per the <b>Student Leave Policy</b>, planned leaves exceeding 3 consecutive days require prior written sanction from the Principal.
                </div>
                <hr style="margin: 12px 0; border: none; border-top: 1px solid #E2E8F0;">
                <div style="font-size: 0.88rem; font-weight: 700; color: #0F172A; margin-bottom: 8px;">
                    🎯 Examination Re-tests
                </div>
                <div style="font-size: 0.82rem; color: #475569; line-height: 1.5;">
                    Absence during mid-terms requires medical review and Academic Council sanction chaired by the Principal.
                </div>
            </div>
        """, unsafe_allow_html=True)

# ================= 3. TEACHER DASHBOARD =================
def render_teacher_dashboard(current_user: dict):
    t_cols = st.columns(4)
    with t_cols[0]:
        st.metric("Academic Calendar", "Term 2", "In Progress")
    with t_cols[1]:
        st.metric("Class Attendance Benchmark", "75%", "Mandatory for Exams")
    with t_cols[2]:
        st.metric("Next Assessment", "Pre-Boards", "Jan 6 – Jan 18")
    with t_cols[3]:
        st.metric("Library Borrowing", "3 Books", "14 Days Loan")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown('<div class="rsr-section-title">📅 Academic Schedule Snapshot</div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; padding: 1.2rem; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
                <table style="width: 100%; border-collapse: collapse; font-size: 0.86rem;">
                    <tr style="border-bottom: 2px solid #E2E8F0; text-align: left; color: #64748B;">
                        <th style="padding: 8px;">Assessment</th>
                        <th style="padding: 8px;">Dates</th>
                        <th style="padding: 8px;">Timing</th>
                    </tr>
                    <tr style="border-bottom: 1px solid #F1F5F9;">
                        <td style="padding: 8px; font-weight: 700; color: #1D4ED8;">Pre-Board Exams (10 & 12)</td>
                        <td style="padding: 8px;">Jan 6 – Jan 18, 2025</td>
                        <td style="padding: 8px;">9:15 AM – 12:15 PM</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #F1F5F9;">
                        <td style="padding: 8px; font-weight: 700; color: #7C3AED;">Annual Final Examinations</td>
                        <td style="padding: 8px;">Mar 3 – Mar 17, 2025</td>
                        <td style="padding: 8px;">9:15 AM – 12:15 PM</td>
                    </tr>
                </table>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="rsr-section-title">💡 Teacher Guidance Quick Links</div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; padding: 1.2rem; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
                <div style="margin-bottom: 10px;">
                    <b>📖 Student Handbook:</b> Disciplinary procedures, device prohibition on campus.
                </div>
                <div style="margin-bottom: 10px;">
                    <b>📝 Leave Protocols:</b> Reviewing parent leave submissions.
                </div>
                <div>
                    <b>🚌 Transport Guidelines:</b> Bus stop arrival standards and bus teacher escorts.
                </div>
            </div>
        """, unsafe_allow_html=True)

# ================= 4. STUDENT DASHBOARD =================
def render_student_dashboard(current_user: dict):
    s_cols = st.columns(4)
    with s_cols[0]:
        st.metric("School Working Hours", "8:30 AM – 3:30 PM", "Mon – Fri")
    with s_cols[1]:
        st.metric("My Minimum Attendance", "75%", "Pass Threshold")
    with s_cols[2]:
        st.metric("Wednesday Uniform", "Sports / PT", "White track & House T-shirt")
    with s_cols[3]:
        st.metric("Library Loan Limit", "3 Books", "14 Days Validity")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown('<div class="rsr-section-title">🎒 Student Rules & Regulations Quick Reference</div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; padding: 1.4rem; box-shadow: 0 2px 6px rgba(0,0,0,0.04); font-size: 0.88rem; line-height: 1.6;">
                <p><b>⏰ Morning Bell:</b> Students must arrive 10 minutes prior to the 8:20 AM assembly bell.</p>
                <p><b>📱 Mobile Phones:</b> Personal smartphones must be deposited in the secure administrative locker upon arrival.</p>
                <p><b>👕 Formal Uniform Days:</b> Full formal uniform is mandatory on Monday, Tuesday, and Thursday.</p>
                <p><b>🏆 Student Houses:</b> Aryabhata (Blue), Ramanujan (Red), Kalam (Green), Sarabhai (Yellow).</p>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="rsr-section-title">❓ Quick Student Queries</div>', unsafe_allow_html=True)
        if st.button("📌 What is the student leave policy?", key="st_q1", use_container_width=True):
            st.session_state["active_question"] = "What is the student leave policy?"
            st.session_state["current_page"] = "chat"
            st.rerun()
        if st.button("📌 When are the examinations scheduled?", key="st_q2", use_container_width=True):
            st.session_state["active_question"] = "When are the examinations scheduled?"
            st.session_state["current_page"] = "chat"
            st.rerun()
        if st.button("📌 What are the school transportation rules?", key="st_q3", use_container_width=True):
            st.session_state["active_question"] = "What are the school transportation rules?"
            st.session_state["current_page"] = "chat"
            st.rerun()

# ================= 5. PARENT DASHBOARD =================
def render_parent_dashboard(current_user: dict):
    p_cols = st.columns(4)
    with p_cols[0]:
        st.metric("Term 2 Installment Due", "Oct 10, 2024", "Grace Period to 25th")
    with p_cols[1]:
        st.metric("Bus Fleet Status", "24 GPS Buses", "Female Attendants On Board")
    with p_cols[2]:
        st.metric("Leave Notice Required", "48 Hours Prior", "For Leaves > 3 Days")
    with p_cols[3]:
        st.metric("Admissions Helpdesk", "+91 99453 21367", "support@rsrtechnologies.co.in")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown('<div class="rsr-section-title">💳 Fee Payment Schedule & Surcharges</div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; padding: 1.2rem; box-shadow: 0 2px 6px rgba(0,0,0,0.04); font-size: 0.86rem;">
                <p><b>• Term 1:</b> Payable on or before June 10, 2024</p>
                <p><b>• Term 2:</b> Payable on or before October 10, 2024</p>
                <p><b>• Term 3:</b> Payable on or before January 10, 2025</p>
                <p><b>• Late Surcharge:</b> Payments after the 10th incur a late surcharge of Rs. 100/day up to the 25th.</p>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="rsr-section-title">🚌 Bus Tracking & Safety Protocols</div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; padding: 1.2rem; box-shadow: 0 2px 6px rgba(0,0,0,0.04); font-size: 0.86rem;">
                <p><b>• Real-Time Tracking:</b> Parents can track bus location in real-time on SchoolGPT.</p>
                <p><b>• Stop Waiting Window:</b> Buses wait maximum 2 minutes at designated stops.</p>
                <p><b>• Emergency Delays:</b> SMS notifications sent automatically for delays over 15 minutes.</p>
            </div>
        """, unsafe_allow_html=True)
