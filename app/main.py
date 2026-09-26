"""
Landing page for the AI-Driven Employee Productivity & Workforce Allocation Optimization System.
This file serves as the entry point for the multi-page Streamlit portfolio and routes users to each major application page.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st

from app.page_shared import configure_app, render_landing_page


configure_app(page_title="AI Workforce Productivity & Allocation Optimizer")
render_landing_page()
