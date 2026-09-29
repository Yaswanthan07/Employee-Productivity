"""Entry point for the AI-Driven Employee Productivity & Workforce Allocation Optimization System."""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import importlib

for mod_name in ["app.utils", "app.page_shared", "app.backend", "app.ml_models"]:
    if mod_name in sys.modules:
        try:
            importlib.reload(sys.modules[mod_name])
        except Exception:
            pass

import streamlit as st

from app.page_shared import ensure_authenticated_session, get_custom_css, render_auth_screen

st.set_page_config(
    page_title="Workforce Intelligence • AI Optimization Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(get_custom_css(), unsafe_allow_html=True)

auth_ok, _ = ensure_authenticated_session()
if not auth_ok:
    render_auth_screen()
    st.stop()

base_dir = BASE_DIR
pages = [
    st.Page(
        os.path.join(base_dir, "app", "pages", "01_Executive_Overview.py"),
        title="Executive Overview",
        icon=":material/dashboard:",
        url_path="",
        default=True,
    ),
    st.Page(
        os.path.join(base_dir, "app", "pages", "02_Workforce_Allocation.py"),
        title="Workforce Allocation",
        icon=":material/tune:",
        url_path="Workforce_Allocation",
    ),
    st.Page(
        os.path.join(base_dir, "app", "pages", "03_Department_Analytics.py"),
        title="Department Analytics",
        icon=":material/domain:",
        url_path="Department_Analytics",
    ),
    st.Page(
        os.path.join(base_dir, "app", "pages", "04_Workload_&_Performance_Analytics.py"),
        title="Workload & Performance",
        icon=":material/query_stats:",
        url_path="Workload_&_Performance_Analytics",
    ),
    st.Page(
        os.path.join(base_dir, "app", "pages", "05_Talent_Risk_&_AI_Predictions.py"),
        title="Talent Risk & AI Predictions",
        icon=":material/psychology:",
        url_path="Talent_Risk_&_AI_Predictions",
    ),
    st.Page(
        os.path.join(base_dir, "app", "pages", "06_Employee_Data_Explorer.py"),
        title="Employee Data Explorer",
        icon=":material/table_chart:",
        url_path="Employee_Data_Explorer",
    ),
    st.Page(
        os.path.join(base_dir, "app", "pages", "07_Profile.py"),
        title="Company Profile",
        icon=":material/badge:",
        url_path="Profile",
    ),
    st.Page(
        os.path.join(base_dir, "app", "pages", "08_Settings.py"),
        title="Security Settings",
        icon=":material/shield:",
        url_path="Settings",
    ),
]

navigation = st.navigation(pages, position="top")
navigation.run()
