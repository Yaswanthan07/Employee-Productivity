"""
Visualization and UI Utility Engine for the Employee Productivity Dashboard.
Includes custom CSS design system, executive-grade Plotly charts, Seaborn figures, and layout helpers.
"""

from typing import Dict, Any, List, Optional
import io
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


STATUS_PALETTE = {
    'Overloaded': '#EF4444',        # High risk / critical workload alert (Rose/Red)
    'Underutilized': '#F59E0B',     # Reallocatable slack capacity (Amber/Gold)
    'High Performer': '#8B5CF6',    # Top output & star performance (Royal Purple)
    'Optimal / Balanced': '#10B981',# Healthy, sustainable baseline (Emerald)
}


def _is_dark_theme() -> bool:
    try:
        return st.get_option("theme.base") == "dark"
    except Exception:
        return False


def _plotly_theme_settings() -> dict:
    is_dark = _is_dark_theme()
    if is_dark:
        return {
            "template": "plotly_dark",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "text_color": "#F8FAFC",
            "grid_color": "rgba(255, 255, 255, 0.08)",
            "axis_color": "#94A3B8",
            "legend_bg": "rgba(17, 24, 39, 0.90)",
            "font_family": "Plus Jakarta Sans, sans-serif",
        }
    return {
        "template": "plotly_white",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "text_color": "#0F172A",
        "grid_color": "rgba(226, 232, 240, 0.8)",
        "axis_color": "#64748B",
        "legend_bg": "rgba(255, 255, 255, 0.94)",
        "font_family": "Plus Jakarta Sans, sans-serif",
    }


def get_custom_css() -> str:
    """
    Returns the comprehensive modern enterprise theme and CSS design tokens.
    """
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        * {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            box-sizing: border-box;
        }

        :root {
            --app-bg: #F8FAFC;
            --app-bg-alt: #F1F5F9;
            --panel: #FFFFFF;
            --panel-alt: #F8FAFC;
            --panel-elevated: #FFFFFF;
            --border: #E2E8F0;
            --border-subtle: #EDF2F7;
            --border-hover: #CBD5E1;
            --text: #0F172A;
            --text-secondary: #334155;
            --muted: #64748B;
            --muted-light: #94A3B8;

            /* Semantic Brand & State Colors */
            --primary: #4F46E5;
            --primary-hover: #4338CA;
            --primary-soft: #EEF2FF;
            --primary-border: #C7D2FE;

            --emerald: #10B981;
            --emerald-soft: #ECFDF5;
            --emerald-border: #A7F3D0;
            --emerald-dark: #047857;

            --rose: #EF4444;
            --rose-soft: #FEF2F2;
            --rose-border: #FECACA;
            --rose-dark: #B91C1C;

            --amber: #F59E0B;
            --amber-soft: #FFFBEB;
            --amber-border: #FDE68A;
            --amber-dark: #B45309;

            --purple: #8B5CF6;
            --purple-soft: #F5F3FF;
            --purple-border: #DDD6FE;
            --purple-dark: #6D28D9;

            --sky: #0EA5E9;
            --sky-soft: #F0F9FF;
            --sky-border: #BAE6FD;
            --sky-dark: #0369A1;

            --card-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.05), 0 2px 4px -2px rgba(15, 23, 42, 0.05);
            --card-shadow-hover: 0 12px 20px -3px rgba(15, 23, 42, 0.09), 0 4px 6px -4px rgba(15, 23, 42, 0.05);
            --header-shadow: 0 10px 25px -10px rgba(79, 70, 229, 0.08), 0 4px 6px -2px rgba(15, 23, 42, 0.03);
        }

        html[data-theme="dark"], body[data-theme="dark"] {
            --app-bg: #090D16;
            --app-bg-alt: #0F172A;
            --panel: #111827;
            --panel-alt: #162032;
            --panel-elevated: #1E293B;
            --border: #2D3748;
            --border-subtle: #1F2937;
            --border-hover: #475569;
            --text: #F8FAFC;
            --text-secondary: #CBD5E1;
            --muted: #94A3B8;
            --muted-light: #64748B;

            --primary: #6366F1;
            --primary-hover: #4F46E5;
            --primary-soft: rgba(99, 102, 241, 0.15);
            --primary-border: rgba(99, 102, 241, 0.35);

            --emerald: #34D399;
            --emerald-soft: rgba(16, 185, 129, 0.15);
            --emerald-border: rgba(16, 185, 129, 0.35);
            --emerald-dark: #10B981;

            --rose: #F87171;
            --rose-soft: rgba(239, 68, 68, 0.15);
            --rose-border: rgba(239, 68, 68, 0.35);
            --rose-dark: #EF4444;

            --amber: #FBBF24;
            --amber-soft: rgba(245, 158, 11, 0.15);
            --amber-border: rgba(245, 158, 11, 0.35);
            --amber-dark: #F59E0B;

            --purple: #A78BFA;
            --purple-soft: rgba(139, 92, 246, 0.15);
            --purple-border: rgba(139, 92, 246, 0.35);
            --purple-dark: #8B5CF6;

            --sky: #38BDF8;
            --sky-soft: rgba(14, 165, 233, 0.15);
            --sky-border: rgba(14, 165, 233, 0.35);
            --sky-dark: #0EA5E9;

            --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.2);
            --card-shadow-hover: 0 12px 24px -4px rgba(0, 0, 0, 0.45);
            --header-shadow: 0 10px 25px -10px rgba(0, 0, 0, 0.5);
        }

        /* Top-level Streamlit Layout */
        [data-testid="stAppViewContainer"], .stApp {
            background-color: var(--app-bg) !important;
            color: var(--text) !important;
        }

        .block-container {
            padding-top: 4.8rem !important;
            padding-bottom: 3rem !important;
            max-width: 1440px !important;
        }

        /* Streamlit Native Header & Top Navbar */
        [data-testid="stHeader"] {
            background: var(--panel) !important;
            border-bottom: 1px solid var(--border) !important;
            box-shadow: 0 2px 10px -2px rgba(15, 23, 42, 0.06) !important;
            backdrop-filter: blur(12px) !important;
            z-index: 999990 !important;
        }

        /* Top Bar Navigation Items Styling */
        [data-testid="stHeader"] nav {
            gap: 0.25rem !important;
            align-items: center !important;
        }

        [data-testid="stHeader"] nav a,
        [data-testid="stHeader"] nav button,
        [data-testid="stHeader"] [data-testid="stPageLink-NavLink"],
        [data-testid="stHeader"] ul li a {
            font-weight: 600 !important;
            font-size: 0.86rem !important;
            border-radius: 8px !important;
            padding: 0.38rem 0.75rem !important;
            transition: all 0.15s ease-in-out !important;
            color: var(--text-secondary) !important;
            text-decoration: none !important;
            border: 1px solid transparent !important;
        }

        [data-testid="stHeader"] nav a:hover,
        [data-testid="stHeader"] nav button:hover,
        [data-testid="stHeader"] [data-testid="stPageLink-NavLink"]:hover,
        [data-testid="stHeader"] ul li a:hover {
            background: var(--app-bg-alt) !important;
            color: var(--primary) !important;
            border-color: var(--border) !important;
        }

        [data-testid="stHeader"] nav a[aria-current="page"],
        [data-testid="stHeader"] [data-testid="stPageLink-NavLink"][aria-current="page"],
        [data-testid="stHeader"] ul li a[aria-current="page"] {
            background: var(--primary-soft) !important;
            color: var(--primary) !important;
            border-color: var(--primary-border) !important;
            font-weight: 700 !important;
        }

        button[title="Deploy"],
        [data-testid="stHeader"] button[title*="Deploy"],
        [data-testid="stHeader"] [aria-label*="Deploy"] {
            display: none !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            background: var(--panel) !important;
            border-right: 1px solid var(--border) !important;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {
            color: var(--text) !important;
        }

        [data-testid="stSidebarNav"] {
            padding-top: 1rem !important;
        }

        [data-testid="stSidebarNav"] span {
            font-size: 0.88rem !important;
            font-weight: 600 !important;
        }

        [data-testid="stSidebarNav"] a {
            border-radius: 10px !important;
            margin: 0.15rem 0.4rem !important;
            padding: 0.55rem 0.85rem !important;
            transition: all 0.15s ease !important;
            border: 1px solid transparent !important;
        }

        [data-testid="stSidebarNav"] a:hover {
            background: var(--app-bg-alt) !important;
            border-color: var(--border) !important;
        }

        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: var(--primary-soft) !important;
            border-color: var(--primary-border) !important;
            color: var(--primary) !important;
            font-weight: 700 !important;
        }

        /* Form Inputs & Controls */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        .stNumberInput > div > div > input {
            background: var(--panel) !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
            color: var(--text) !important;
            font-size: 0.9rem !important;
            transition: all 0.2s ease !important;
        }

        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div:focus-within,
        .stMultiSelect > div > div:focus-within,
        .stNumberInput > div > div > input:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px var(--primary-soft) !important;
        }

        /* Executive Header */
        .page-header {
            background: linear-gradient(135deg, var(--panel) 0%, var(--panel-alt) 100%);
            border-radius: 16px;
            padding: 1.5rem 1.75rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border);
            box-shadow: var(--header-shadow);
            position: relative;
            overflow: hidden;
        }

        .page-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary) 0%, var(--emerald) 50%, var(--purple) 100%);
        }

        .page-header-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .page-title {
            font-size: clamp(1.5rem, 2.2vw, 2.2rem);
            font-weight: 800;
            letter-spacing: -0.03em;
            color: var(--text);
            margin: 0 0 0.4rem 0;
            line-height: 1.2;
        }

        .page-subtitle {
            color: var(--muted);
            font-size: 0.95rem;
            line-height: 1.55;
            max-width: 980px;
            margin-bottom: 0.85rem;
        }

        .tenant-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            background: var(--panel-elevated);
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 0.35rem 0.85rem;
            font-size: 0.78rem;
            font-weight: 600;
            color: var(--text-secondary);
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }

        .tenant-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--emerald);
        }

        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-top: 0.5rem;
        }

        .badge-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            background: var(--primary-soft);
            color: var(--primary);
            border: 1px solid var(--primary-border);
            padding: 0.3rem 0.7rem;
            border-radius: 999px;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.01em;
        }

        /* KPI Cards System */
        .kpi-card {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            background: var(--panel) !important;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.2rem 1.25rem;
            box-shadow: var(--card-shadow);
            position: relative;
            overflow: hidden;
            min-height: 128px;
            height: 100%;
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }

        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--card-shadow-hover);
        }

        .kpi-stripe {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            border-radius: 999px 999px 0 0;
        }

        .stripe-blue { background: linear-gradient(90deg, #3B82F6, #60A5FA); }
        .stripe-indigo { background: linear-gradient(90deg, #6366F1, #818CF8); }
        .stripe-emerald { background: linear-gradient(90deg, #10B981, #34D399); }
        .stripe-amber { background: linear-gradient(90deg, #F59E0B, #FBBF24); }
        .stripe-rose, .stripe-red { background: linear-gradient(90deg, #EF4444, #F87171); }
        .stripe-purple { background: linear-gradient(90deg, #8B5CF6, #A78BFA); }
        .stripe-sky { background: linear-gradient(90deg, #0EA5E9, #38BDF8); }

        .kpi-header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.4rem;
        }

        .kpi-title {
            font-size: 0.76rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--muted);
        }

        .kpi-chip {
            font-size: 0.7rem;
            font-weight: 700;
            padding: 0.18rem 0.5rem;
            border-radius: 6px;
        }

        .kpi-chip-rose { background: var(--rose-soft); color: var(--rose-dark); border: 1px solid var(--rose-border); }
        .kpi-chip-amber { background: var(--amber-soft); color: var(--amber-dark); border: 1px solid var(--amber-border); }
        .kpi-chip-emerald { background: var(--emerald-soft); color: var(--emerald-dark); border: 1px solid var(--emerald-border); }
        .kpi-chip-purple { background: var(--purple-soft); color: var(--purple-dark); border: 1px solid var(--purple-border); }
        .kpi-chip-blue { background: var(--primary-soft); color: var(--primary); border: 1px solid var(--primary-border); }

        .kpi-value {
            font-size: clamp(1.6rem, 2.2vw, 2.1rem);
            font-weight: 800;
            color: var(--text);
            line-height: 1.15;
            margin: 0.3rem 0;
            letter-spacing: -0.02em;
        }

        .kpi-caption {
            font-size: 0.78rem;
            color: var(--muted);
            line-height: 1.4;
            margin-top: auto;
        }

        /* Story / Callout Boxes */
        .story-box {
            background: var(--panel);
            border: 1px solid var(--border);
            border-left: 4px solid var(--primary);
            border-radius: 12px;
            padding: 1rem 1.25rem;
            color: var(--text);
            margin: 1.25rem 0;
            box-shadow: var(--card-shadow);
            font-size: 0.92rem;
            line-height: 1.6;
        }

        .story-box-amber { border-left-color: var(--amber); background: var(--amber-soft); }
        .story-box-emerald { border-left-color: var(--emerald); background: var(--emerald-soft); }
        .story-box-rose { border-left-color: var(--rose); background: var(--rose-soft); }

        /* Action Cards */
        .action-card {
            background: var(--panel) !important;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.1rem 1.25rem;
            box-shadow: var(--card-shadow);
            margin-bottom: 0.85rem;
            transition: all 0.18s ease;
        }

        .action-card:hover {
            box-shadow: var(--card-shadow-hover);
            border-color: var(--border-hover);
        }

        /* Analytical Card Container */
        .chart-card {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.25rem;
            box-shadow: var(--card-shadow);
            margin-bottom: 1.25rem;
        }

        .chart-card-header {
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 0.75rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        /* Streamlit Dataframe Overrides */
        [data-testid="stDataFrame"], [data-testid="stTable"] {
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            background: var(--panel) !important;
        }

        /* Tabs Polish */
        .stTabs [role="tablist"] {
            gap: 0.5rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.25rem;
            margin-bottom: 1rem;
        }

        .stTabs [role="tab"] {
            padding: 0.55rem 1.1rem !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            border-radius: 8px 8px 0 0 !important;
            color: var(--muted) !important;
            background: transparent !important;
            border: none !important;
            transition: all 0.15s ease !important;
        }

        .stTabs [role="tab"][aria-selected="true"] {
            color: var(--primary) !important;
            font-weight: 700 !important;
            border-bottom: 2px solid var(--primary) !important;
        }

        /* Button Styling */
        .stButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            padding: 0.45rem 1.1rem !important;
            transition: all 0.15s ease !important;
            border: 1px solid var(--border) !important;
        }

        .stButton > button:hover {
            border-color: var(--primary) !important;
            color: var(--primary) !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
        }

        /* Primary Button */
        .stButton > button[kind="primary"] {
            background: var(--primary) !important;
            color: #FFFFFF !important;
            border: 1px solid var(--primary) !important;
        }

        .stButton > button[kind="primary"]:hover {
            background: var(--primary-hover) !important;
            box-shadow: 0 4px 12px var(--primary-soft) !important;
        }

        /* Expander */
        .stExpander {
            background: var(--panel) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            margin-bottom: 1rem !important;
        }

        .stExpander summary {
            font-weight: 600 !important;
            color: var(--text) !important;
            padding: 0.75rem 1rem !important;
        }
    </style>
    """


def create_workforce_quadrant_chart(df: pd.DataFrame) -> go.Figure:
    """
    Creates an executive scatter plot showing Work Hours vs Task Completion with 4 utilization quadrants.
    """
    theme = _plotly_theme_settings()

    fig = px.scatter(
        df,
        x='Weekly_Work_Hours',
        y='Task_Completion_Pct',
        color='Workforce_Status',
        color_discrete_map=STATUS_PALETTE,
        size='Projects_Handled',
        size_max=12,
        hover_name='Employee_ID',
        hover_data={
            'Department': True,
            'Job_Role': True,
            'Weekly_Work_Hours': ':.1f',
            'Task_Completion_Pct': ':.1f',
            'Manager_Rating': ':.1f',
            'Workforce_Status': True
        },
        title="<b>Workforce Utilization Matrix (Workload vs. Output)</b>",
        labels={
            'Weekly_Work_Hours': 'Weekly Work Hours (hrs/wk)',
            'Task_Completion_Pct': 'Task Completion (%)',
            'Workforce_Status': 'Status'
        },
        template=theme["template"]
    )

    # Clean benchmark reference lines
    fig.add_vline(x=45, line_dash="dash", line_color="#EF4444", line_width=1.2)
    fig.add_vline(x=38, line_dash="dot", line_color="#F59E0B", line_width=1.2)
    fig.add_hline(y=80, line_dash="dash", line_color="#10B981", line_width=1.2)

    # Modern translucent quadrant callouts
    fig.add_annotation(
        x=55, y=55,
        text="<b>🚨 Overload Risk Zone</b>",
        showarrow=False,
        font=dict(color="#DC2626", size=10, family=theme["font_family"]),
        bgcolor="rgba(254, 226, 226, 0.85)",
        bordercolor="#FECACA",
        borderwidth=1,
        borderpad=4
    )
    fig.add_annotation(
        x=33, y=92,
        text="<b>⚡ Slack / Reallocatable</b>",
        showarrow=False,
        font=dict(color="#B45309", size=10, family=theme["font_family"]),
        bgcolor="rgba(254, 243, 199, 0.85)",
        bordercolor="#FDE68A",
        borderwidth=1,
        borderpad=4
    )
    fig.add_annotation(
        x=55, y=95,
        text="<b>⭐ Strained Stars</b>",
        showarrow=False,
        font=dict(color="#6D28D9", size=10, family=theme["font_family"]),
        bgcolor="rgba(237, 233, 254, 0.85)",
        bordercolor="#DDD6FE",
        borderwidth=1,
        borderpad=4
    )
    fig.add_annotation(
        x=41, y=88,
        text="<b>✅ Balanced Core</b>",
        showarrow=False,
        font=dict(color="#047857", size=10, family=theme["font_family"]),
        bgcolor="rgba(209, 250, 229, 0.85)",
        bordercolor="#A7F3D0",
        borderwidth=1,
        borderpad=4
    )

    fig.update_layout(
        height=380,
        template=theme["template"],
        paper_bgcolor=theme["paper_bgcolor"],
        plot_bgcolor=theme["plot_bgcolor"],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=theme["text_color"], size=10, family=theme["font_family"]),
            bgcolor=theme["legend_bg"],
        ),
        margin=dict(l=35, r=30, t=65, b=35),
        font=dict(family=theme["font_family"], color=theme["text_color"]),
        xaxis=dict(
            gridcolor=theme["grid_color"],
            tickfont=dict(color=theme["axis_color"]),
            title_font=dict(color=theme["axis_color"]),
            zerolinecolor=theme["grid_color"]
        ),
        yaxis=dict(
            gridcolor=theme["grid_color"],
            tickfont=dict(color=theme["axis_color"]),
            title_font=dict(color=theme["axis_color"]),
            zerolinecolor=theme["grid_color"]
        ),
    )

    return fig


def create_department_benchmark_bar(dept_df: pd.DataFrame) -> go.Figure:
    """
    Creates a clean horizontal bar chart comparing departmental Task Completion %.
    """
    sorted_df = dept_df.sort_values(by='Avg_Task_Completion_Pct', ascending=True)
    theme = _plotly_theme_settings()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=sorted_df['Department'],
        x=sorted_df['Avg_Task_Completion_Pct'],
        orientation='h',
        marker=dict(
            color=sorted_df['Avg_Task_Completion_Pct'],
            colorscale=[[0.0, '#F59E0B'], [0.5, '#6366F1'], [1.0, '#10B981']],
            line=dict(color='rgba(255,255,255,0.6)', width=1)
        ),
        text=sorted_df['Avg_Task_Completion_Pct'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside',
        cliponaxis=False
    ))

    # Add 80% Benchmark Reference Line
    fig.add_vline(x=80.0, line_dash="dash", line_color="#10B981", line_width=1.5,
                  annotation_text="Target: 80%", annotation_position="top right",
                  annotation_font=dict(color="#10B981", size=10, family=theme["font_family"]))

    fig.update_layout(
        title={"text": "<b>Avg Task Completion Rate by Department</b>", "font": {"color": theme["text_color"], "family": theme["font_family"]}},
        template=theme["template"],
        paper_bgcolor=theme["paper_bgcolor"],
        plot_bgcolor=theme["plot_bgcolor"],
        height=380,
        xaxis=dict(
            range=[0, 105],
            title="Avg Task Completion Rate (%)",
            title_font=dict(color=theme["axis_color"]),
            tickfont=dict(color=theme["axis_color"]),
            gridcolor=theme["grid_color"],
            zerolinecolor=theme["grid_color"]
        ),
        yaxis=dict(
            title="",
            tickfont=dict(color=theme["text_color"], size=11, family=theme["font_family"]),
            gridcolor=theme["grid_color"]
        ),
        margin=dict(l=35, r=40, t=55, b=35),
        font=dict(family=theme["font_family"], color=theme["text_color"]),
    )

    return fig


def create_utilization_distribution_pie(df: pd.DataFrame) -> go.Figure:
    """
    Creates an executive donut chart of workforce status proportions.
    """
    counts = df['Workforce_Status'].value_counts().reset_index()
    counts.columns = ['Status', 'Count']
    theme = _plotly_theme_settings()

    fig = px.pie(
        counts,
        values='Count',
        names='Status',
        hole=0.62,
        color='Status',
        color_discrete_map=STATUS_PALETTE,
        title="<b>Workforce Allocation Share</b>",
        template=theme["template"]
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )

    fig.update_layout(
        height=380,
        template=theme["template"],
        paper_bgcolor=theme["paper_bgcolor"],
        plot_bgcolor=theme["plot_bgcolor"],
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family=theme["font_family"], color=theme["text_color"]),
        legend=dict(
            font=dict(color=theme["text_color"], size=10, family=theme["font_family"]),
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        )
    )
    return fig


def _green_status_palette() -> dict:
    """Legacy compatibility helper."""
    return STATUS_PALETTE


def create_hours_distribution_plot(df: pd.DataFrame) -> go.Figure:
    """
    Plotly distribution plot of weekly work hours.
    """
    theme = _plotly_theme_settings()
    fig = px.histogram(
        df,
        x="Weekly_Work_Hours",
        color="Workforce_Status",
        marginal="box",
        nbins=24,
        title="<b>Weekly Work Hours Distribution</b>",
        labels={'Weekly_Work_Hours': 'Weekly Work Hours (hrs/wk)'},
        color_discrete_map=STATUS_PALETTE,
        template=theme["template"]
    )

    fig.add_vline(x=40.0, line_dash="dash", line_color="#3B82F6", line_width=1.5,
                  annotation_text="40h Baseline", annotation_position="top left",
                  annotation_font=dict(color="#3B82F6", size=10))

    fig.update_layout(
        height=360,
        template=theme["template"],
        paper_bgcolor=theme["paper_bgcolor"],
        plot_bgcolor=theme["plot_bgcolor"],
        margin=dict(l=35, r=30, t=90, b=35),
        font=dict(family=theme["font_family"], color=theme["text_color"]),
        title=dict(text="<b>Weekly Work Hours Distribution</b>", x=0.02, xanchor="left", y=0.98, font=dict(color=theme["text_color"])),
        legend=dict(orientation="h", x=0.5, y=1.14, xanchor="center", yanchor="bottom", font=dict(color=theme["text_color"]))
    )
    return fig


def create_completion_distribution_plot(df: pd.DataFrame) -> go.Figure:
    """
    Plotly distribution plot of task completion %.
    """
    theme = _plotly_theme_settings()
    fig = px.histogram(
        df,
        x="Task_Completion_Pct",
        color="Workforce_Status",
        marginal="box",
        nbins=24,
        title="<b>Task Completion % Distribution</b>",
        labels={'Task_Completion_Pct': 'Task Completion (%)'},
        color_discrete_map=STATUS_PALETTE,
        template=theme["template"]
    )

    fig.add_vline(x=80.0, line_dash="dash", line_color="#10B981", line_width=1.5,
                  annotation_text="80% Target", annotation_position="top left",
                  annotation_font=dict(color="#10B981", size=10))

    fig.update_layout(
        height=360,
        template=theme["template"],
        paper_bgcolor=theme["paper_bgcolor"],
        plot_bgcolor=theme["plot_bgcolor"],
        margin=dict(l=35, r=30, t=90, b=35),
        font=dict(family=theme["font_family"], color=theme["text_color"]),
        title=dict(text="<b>Task Completion % Distribution</b>", x=0.02, xanchor="left", y=0.98, font=dict(color=theme["text_color"])),
        legend=dict(orientation="h", x=0.5, y=1.14, xanchor="center", yanchor="bottom", font=dict(color=theme["text_color"]))
    )
    return fig


def create_seaborn_distributions(df: pd.DataFrame) -> plt.Figure:
    """
    Static Seaborn Histogram + KDE plots for executive reporting.
    """
    is_dark = _is_dark_theme()
    sns.set_theme(style="darkgrid" if is_dark else "whitegrid", palette="deep")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    text_color = '#F8FAFC' if is_dark else '#0F172A'
    axis_color = '#94A3B8' if is_dark else '#64748B'
    fig.patch.set_facecolor('#111827' if is_dark else '#FFFFFF')

    # Task Completion
    sns.histplot(
        df['Task_Completion_Pct'],
        kde=True,
        ax=axes[0],
        color="#10B981",
        bins=20,
        line_kws={'linewidth': 2.2}
    )
    axes[0].set_title('Task Completion % Distribution (KDE)', fontsize=11, fontweight='bold', pad=10, color=text_color)
    axes[0].set_xlabel('Task Completion (%)', fontsize=10, color=axis_color)
    axes[0].set_ylabel('Employee Count', fontsize=10, color=axis_color)
    axes[0].tick_params(axis='x', colors=axis_color)
    axes[0].tick_params(axis='y', colors=axis_color)
    axes[0].axvline(df['Task_Completion_Pct'].mean(), color='#059669', linestyle='--', label=f"Mean: {df['Task_Completion_Pct'].mean():.1f}%")
    axes[0].legend(fontsize=9, labelcolor=text_color)

    # Weekly Hours
    sns.histplot(
        df['Weekly_Work_Hours'],
        kde=True,
        ax=axes[1],
        color="#6366F1",
        bins=20,
        line_kws={'linewidth': 2.2}
    )
    axes[1].set_title('Weekly Work Hours Distribution (KDE)', fontsize=11, fontweight='bold', pad=10, color=text_color)
    axes[1].set_xlabel('Weekly Work Hours (hrs/wk)', fontsize=10, color=axis_color)
    axes[1].set_ylabel('Employee Count', fontsize=10, color=axis_color)
    axes[1].tick_params(axis='x', colors=axis_color)
    axes[1].tick_params(axis='y', colors=axis_color)
    axes[1].axvline(40, color='#3B82F6', linestyle=':', label='40h Standard')
    axes[1].axvline(df['Weekly_Work_Hours'].mean(), color='#4F46E5', linestyle='--', label=f"Mean: {df['Weekly_Work_Hours'].mean():.1f}h")
    axes[1].legend(fontsize=9, labelcolor=text_color)

    plt.tight_layout()
    return fig


def create_gauge_indicator(title: str, value: float, max_val: float = 100.0, suffix: str = "%") -> go.Figure:
    """
    Modern Gauge widget with clear gradient zones.
    """
    theme = _plotly_theme_settings()
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': f"<b>{title}</b>", 'font': {'size': 14, 'color': theme['text_color'], 'family': theme['font_family']}},
        number={'suffix': suffix, 'font': {'size': 28, 'color': theme['text_color'], 'family': theme['font_family']}},
        gauge={
            'axis': {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': theme['axis_color']},
            'bar': {'color': "#6366F1", 'thickness': 0.28},
            'bgcolor': 'rgba(0,0,0,0)',
            'borderwidth': 1,
            'bordercolor': theme['axis_color'],
            'steps': [
                {'range': [0, max_val * 0.35], 'color': '#ECFDF5'},
                {'range': [max_val * 0.35, max_val * 0.65], 'color': '#FFFBEB'},
                {'range': [max_val * 0.65, max_val], 'color': '#FEF2F2'}
            ]
        }
    ))
    fig.update_layout(
        height=180,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor=theme['paper_bgcolor'],
        plot_bgcolor=theme['plot_bgcolor'],
        font=dict(color=theme['text_color'], family=theme['font_family'])
    )
    return fig
