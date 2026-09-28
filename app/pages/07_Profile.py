import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st

from app.page_shared import _api_request, clear_auth_session, configure_app, render_page_header

configure_app(page_title="Company Profile")
render_page_header(
    title="Company Profile & Organization Details",
    subtitle="Manage your enterprise workspace identity, primary administrator details, and tenant account preferences.",
    badges=["🏢 Enterprise Profile", "👤 Administrator Details", "🔒 Verified Tenant"],
)

left_col, right_col = st.columns([6, 6])

with left_col:
    st.markdown("#### 🏢 Workspace Overview")
    company_name = st.session_state.get("company_name", "Acme Enterprise")
    user_email = st.session_state.get("user_email", "hr@company.com")
    user_role = st.session_state.get("user_role", "HR Administrator")
    auth_user = st.session_state.get("auth_user", "Admin User")

    st.markdown(
        f"""
        <div class="action-card" style="border-left: 4px solid var(--primary);">
            <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:var(--muted); margin-bottom:4px;">Organization</div>
            <div style="font-size:1.3rem; font-weight:800; color:var(--text); margin-bottom:12px;">🏢 {company_name}</div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem; font-size:0.88rem; color:var(--text);">
                <div><span style="color:var(--muted); font-size:0.75rem; display:block;">Registered Admin</span><b>{auth_user}</b></div>
                <div><span style="color:var(--muted); font-size:0.75rem; display:block;">Admin Role</span><b>{user_role}</b></div>
                <div style="grid-column: span 2;"><span style="color:var(--muted); font-size:0.75rem; display:block;">Associated Work Email</span><b>{user_email}</b></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_col:
    st.markdown("#### ✏️ Update Profile Details")
    with st.form("profile_form"):
        profile_name = st.text_input(
            "Administrator Full Name",
            value=st.session_state.get("auth_user", ""),
            placeholder="e.g. Jane Doe",
        )
        submitted = st.form_submit_button("Save Changes", use_container_width=True, type="primary")
        if submitted:
            token = st.session_state.get("auth_token")
            response = _api_request("put", "/auth/profile", {"full_name": profile_name}, token=token)
            if response and response.status_code == 200:
                st.session_state["auth_user"] = response.json()["full_name"]
                st.success("✅ Profile updated successfully.")
                st.rerun()
            else:
                st.error((response.json() if response else {}).get("detail", "Unable to update profile."))

st.markdown("---")
st.markdown("#### 🚪 Session Management")
if st.button("Sign Out of Workspace", key="profile_logout_btn"):
    token = st.session_state.get("auth_token")
    if token:
        _api_request("post", "/auth/logout", token=token)
    clear_auth_session()
    st.success("You have been signed out.")
    st.rerun()
