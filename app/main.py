"""Entry point for the AI-Driven Employee Productivity & Workforce Allocation Optimization System."""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st

from app.page_shared import configure_app


configure_app(page_title="AI Workforce Productivity & Allocation Optimizer")

base_dir = BASE_DIR
pages = [
    st.Page(os.path.join(base_dir, "app", "pages", "01_Executive_Overview.py"), title="Executive Overview", icon=":material/insights:"),
    st.Page(os.path.join(base_dir, "app", "pages", "02_Workforce_Allocation.py"), title="Workforce Allocation", icon=":material/compare_arrows:"),
    st.Page(os.path.join(base_dir, "app", "pages", "03_Department_Analytics.py"), title="Department Analytics", icon=":material/analytics:"),
    st.Page(os.path.join(base_dir, "app", "pages", "04_Workload_&_Performance_Analytics.py"), title="Workload & Performance Analytics", icon=":material/bar_chart:"),
    st.Page(os.path.join(base_dir, "app", "pages", "05_Talent_Risk_&_AI_Predictions.py"), title="Talent Risk & AI Predictions", icon=":material/auto_awesome:"),
    st.Page(os.path.join(base_dir, "app", "pages", "06_Employee_Data_Explorer.py"), title="Employee Data Explorer", icon=":material/table_rows:"),
]

navigation = st.navigation(pages, position="top")
navigation.run()
