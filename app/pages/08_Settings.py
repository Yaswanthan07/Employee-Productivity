import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st

from app.page_shared import _api_request, clear_auth_session, configure_app, password_policy_text, render_page_header

configure_app(page_title="Security Settings")
render_page_header(
    title="Security & Account Settings",
    subtitle="Configure enterprise authentication security, update administrator credentials, and maintain access governance standards.",
    badges=["🔒 Enterprise Security", "🔑 Access Governance", "🛡️ Compliance Ready"],
)

left_col, right_col = st.columns([6, 6])

with left_col:
    st.markdown("#### 🔑 Update Security Password")
    with st.form("settings_password_form"):
        current_password = st.text_input("Current Password", type="password", placeholder="••••••••")
        new_password = st.text_input("New Password", type="password", placeholder="Min. 8 characters")
        if new_password:
            st.markdown(password_policy_text(new_password), unsafe_allow_html=True)
        confirm_password = st.text_input("Confirm New Password", type="password", placeholder="Re-enter new password")

        submitted = st.form_submit_button("Update Password", use_container_width=True, type="primary")
        if submitted:
            if not all([current_password, new_password, confirm_password]):
                st.error("Please complete all password fields.")
            else:
                token = st.session_state.get("auth_token")
                response = _api_request(
                    "put",
                    "/auth/password",
                    {
                        "current_password": current_password,
                        "new_password": new_password,
                        "confirm_password": confirm_password,
                    },
                    token=token,
                )
                if response and response.status_code == 200:
                    st.success("✅ Password updated successfully.")
                else:
                    st.error((response.json() if response else {}).get("detail", "Unable to change password."))

with right_col:
    st.markdown("#### 🛡️ Security Governance Guidelines")
    st.markdown(
        """
        <div class="action-card" style="border-left: 4px solid var(--emerald);">
            <div style="font-weight:700; font-size:0.95rem; margin-bottom:6px;">Enterprise Password Policy</div>
            <ul style="margin:0 0 0.5rem 1.2rem; font-size:0.86rem; color:var(--muted); line-height:1.6;">
                <li>Passwords must contain at least 8 characters.</li>
                <li>At least one uppercase and one lowercase letter are required.</li>
                <li>At least one non-alphanumeric special character is mandatory.</li>
                <li>Avoid reusing prior passwords across multiple rotations.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown("#### 🚪 Session Termination")
if st.button("Sign Out of All Sessions", key="settings_logout_btn"):
    token = st.session_state.get("auth_token")
    if token:
        _api_request("post", "/auth/logout", token=token)
    clear_auth_session()
    st.success("You have been signed out.")
    st.rerun()
