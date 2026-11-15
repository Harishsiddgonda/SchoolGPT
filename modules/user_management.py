"""
SchoolGPT - User Management Module
Role assignment, account activation, credential management.
RSR Technologies
"""

import streamlit as st
from config.settings import ROLES
from services.user_service import user_service
from auth.authentication import register_user, reset_user_password_by_admin
from auth.permissions import has_permission, get_role_badge_color

def render_user_management(current_user: dict):
    admin_id = current_user.get("id")
    admin_role = current_user.get("role", "School Administrator")

    if not has_permission(admin_role, "can_manage_users"):
        st.error("⛔ Access Denied: Administrator privileges required.")
        return

    st.markdown('<div class="rsr-section-title">👥 Institutional User & Role Administration</div>', unsafe_allow_html=True)
    st.caption("Manage student, parent, teacher, and administrative accounts with granular role-based access control.")

    tab1, tab2 = st.tabs(["📋 Registered Accounts Directory", "➕ Provision New User Account"])

    with tab1:
        users = user_service.list_users()
        st.markdown(f"**Total Registered Accounts: {len(users)}**")

        for u in users:
            with st.container():
                role_col = get_role_badge_color(u["role"])
                status_str = "🟢 Active" if u.get("is_active") else "🔴 Inactive"
                initial = (u["full_name"][0] if u["full_name"] else "U").upper()

                col1, col2, col3, col4 = st.columns([2.8, 1.4, 1.4, 1.8])

                with col1:
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #1D4ED8, #7C3AED); display: flex; align-items: center; justify-content: center; color: #FFF; font-weight: 800; font-size: 0.9rem;">
                                {initial}
                            </div>
                            <div>
                                <div style="font-weight: 700; font-size: 0.92rem; color: #0F172A;">{u['full_name']}</div>
                                <div style="font-size: 0.76rem; color: #64748B;">@{u['username']} • {u['email']}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                        <div style="margin-top: 4px;">
                            <span style="background: {role_col}; color: white; padding: 3px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 700;">
                                {u['role']}
                            </span>
                            <div style="font-size: 0.74rem; color: #64748B; margin-top: 4px;">{status_str}</div>
                        </div>
                    """, unsafe_allow_html=True)

                with col3:
                    new_role = st.selectbox(
                        "Change Role",
                        options=ROLES,
                        index=ROLES.index(u["role"]) if u["role"] in ROLES else 0,
                        key=f"role_sel_{u['id']}",
                        label_visibility="collapsed"
                    )
                    if new_role != u["role"]:
                        if st.button("Update Role", key=f"btn_role_{u['id']}"):
                            user_service.change_role(u["id"], new_role, admin_id)
                            st.success(f"Updated {u['username']} to {new_role}")
                            st.rerun()

                with col4:
                    b_col1, b_col2 = st.columns(2)
                    with b_col1:
                        btn_txt = "Deactivate" if u.get("is_active") else "Activate"
                        if st.button(btn_txt, key=f"toggle_{u['id']}", use_container_width=True):
                            user_service.toggle_user_status(u["id"], bool(u.get("is_active")), admin_id)
                            st.rerun()
                    with b_col2:
                        if u["id"] != admin_id:
                            if st.button("Delete", key=f"del_user_{u['id']}", type="secondary", use_container_width=True):
                                user_service.remove_user(u["id"], admin_id)
                                st.rerun()

                with st.expander(f"🔑 Reset Credentials for @{u['username']}", expanded=False):
                    new_pwd = st.text_input("New Temporary Password", type="password", key=f"newpwd_{u['id']}")
                    if st.button("Confirm Password Reset", key=f"btn_reset_{u['id']}"):
                        if len(new_pwd) >= 6:
                            reset_user_password_by_admin(admin_id, u["id"], new_pwd)
                            st.success(f"Password reset for @{u['username']}.")
                        else:
                            st.error("Password must be at least 6 characters.")

                st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    with tab2:
        st.markdown("#### Provision New Account")
        with st.form("create_user_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                new_username = st.text_input("Username *", placeholder="e.g. john_teacher")
                new_email = st.text_input("Email Address *", placeholder="e.g. john@rsracademy.edu")
                new_fullname = st.text_input("Full Name *", placeholder="e.g. John Doe")

            with col_b:
                new_role = st.selectbox("Assigned Role *", options=ROLES)
                new_password = st.text_input("Temporary Password *", type="password", placeholder="Minimum 6 characters")

            submit_create = st.form_submit_button("➕ Provision Account", use_container_width=True)

        if submit_create:
            ok, msg = register_user(
                username=new_username,
                email=new_email,
                full_name=new_fullname,
                role=new_role,
                password=new_password,
                creator_id=admin_id
            )
            if ok:
                st.success(f"✅ {msg}")
                st.rerun()
            else:
                st.error(f"❌ {msg}")
