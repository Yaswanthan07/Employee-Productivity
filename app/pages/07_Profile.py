import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st

from app.page_shared import configure_app, _api_request, clear_auth_session

configure_app(page_title="Profile")

st.title("Profile")
st.markdown("Manage your company profile and account details.")

profile_name = st.text_input(
    "Full name",
    value=st.session_state.get("auth_user", ""),
    key="profile_page_name",
)

st.write(f"**Company:** {st.session_state.get('company_name', 'Company')}")
st.write(f"**Registered email:** {st.session_state.get('user_email', 'Unknown')}")

if st.button("Save profile"):
    token = st.session_state.get("auth_token")
    response = _api_request("put", "/auth/profile", {"full_name": profile_name}, token=token)
    if response and response.status_code == 200:
        st.session_state["auth_user"] = response.json()["full_name"]
        st.success("Profile updated successfully.")
    else:
        st.error((response.json() if response else {}).get("detail", "Unable to update profile."))

if st.button("Logout", key="profile_logout"):
    token = st.session_state.get("auth_token")
    if token:
        _api_request("post", "/auth/logout", token=token)
    clear_auth_session()
    st.success("You have been logged out.")
    st.rerun()
