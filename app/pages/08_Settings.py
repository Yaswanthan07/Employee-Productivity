import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st

from app.page_shared import configure_app, _api_request, clear_auth_session, password_policy_text

configure_app(page_title="Settings")

st.title("Settings")
st.markdown("Manage account preferences and keep your credentials secure.")

st.subheader("Security")
current_password = st.text_input("Current password", type="password", key="settings_current_password")
new_password = st.text_input("New password", type="password", key="settings_new_password")
if new_password:
    st.markdown(password_policy_text(new_password), unsafe_allow_html=True)
confirm_password = st.text_input("Confirm new password", type="password", key="settings_confirm_password")

if st.button("Change password"):
    if not all([current_password, new_password, confirm_password]):
        st.error("Complete all password fields.")
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
            st.success("Password updated successfully.")
        else:
            st.error((response.json() if response else {}).get("detail", "Unable to change password."))

if st.button("Logout", key="settings_logout"):
    token = st.session_state.get("auth_token")
    if token:
        _api_request("post", "/auth/logout", token=token)
    clear_auth_session()
    st.success("You have been logged out.")
    st.rerun()
