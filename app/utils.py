"""
Visualization and UI Utility Engine for the Employee Productivity Dashboard.
Includes custom CSS injections, executive-grade Plotly charts, Seaborn figures, and layout helpers.
"""

from typing import Dict, Any, List, Optional
import io
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns


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
            "paper_bgcolor": "#122118",
            "plot_bgcolor": "#12311F",
            "text_color": "#F2F8F3",
            "grid_color": "rgba(255,255,255,0.10)",
            "axis_color": "#CFE1D4",
            "legend_bg": "rgba(18,33,24,0.90)",
        }
    return {
        "template": "plotly_white",
        "paper_bgcolor": "#ffffff",
        "plot_bgcolor": "#ffffff",
        "text_color": "#17231B",
        "grid_color": "rgba(21,128,61,0.12)",
        "axis_color": "#526357",
        "legend_bg": "rgba(255,255,255,0.96)",
    }


def get_custom_css() -> str:
    """
    Returns the premium white-and-green enterprise theme for the dashboard.
    """
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

        * { font-family: 'Plus Jakarta Sans', sans-serif; }

        :root {
            --bg: #FFFFFF;
            --bg-alt: #F7FAF7;
            --panel: #FFFFFF;
            --panel-alt: #F7FAF7;
            --border: #DCE7DE;
            --text: #17231B;
            --muted: #526357;
            --accent: #15803D;
            --accent-dark: #166534;
            --accent-soft: #EAF5EC;
            --accent-light: #DCFCE7;
            --hover: #EAF5EC;
            --shadow: rgba(21, 128, 61, 0.08);
        }

        html[data-theme="dark"], body[data-theme="dark"] {
            --bg: #0E1A13;
            --bg-alt: #122118;
            --panel: #12311F;
            --panel-alt: #163C28;
            --border: #2B5541;
            --text: #F2F8F3;
            --muted: #CFE1D4;
            --accent: #4ADE80;
            --accent-dark: #22C55E;
            --accent-soft: rgba(74, 222, 128, 0.12);
            --accent-light: rgba(74, 222, 128, 0.16);
            --hover: rgba(74, 222, 128, 0.08);
            --shadow: rgba(0, 0, 0, 0.30);
        }

        [data-testid="stAppViewContainer"], .stApp {
            background: var(--bg) !important;
            color: var(--text) !important;
        }

        .block-container {
            padding-top: 0.8rem !important;
            padding-bottom: 2rem !important;
        }

        .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
        .stDataFrameContainer, .stDataFrame, .stTable, .stMetric, .stMetricValue, .stMetricDelta,
        .stTextInput, .stSelectbox, .stMultiSelect, .stNumberInput, .stRadio, .stCheckbox, .stSlider,
        .stTabs, .stExpander, .stDownloadButton, .stButton, .stCaption, label,
        [data-testid="stHorizontalBlock"], [data-testid="stVerticalBlock"] {
            color: var(--text) !important;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--panel) 0%, var(--panel-alt) 100%) !important;
            border-right: 1px solid var(--border) !important;
            color: var(--text) !important;
            box-shadow: 2px 0 18px var(--shadow);
        }

        [data-testid="stSidebar"] * {
            color: var(--text) !important;
        }

        [data-testid="stSidebarNav"] a {
            border-radius: 10px;
            margin: 0.14rem 0.15rem;
            padding: 0.68rem 0.8rem;
            transition: all 0.2s ease;
            color: var(--text) !important;
            background: transparent !important;
            border: 1px solid transparent !important;
            font-weight: 600;
        }

        [data-testid="stSidebarNav"] a:hover {
            background: var(--hover) !important;
            border-color: var(--border) !important;
            transform: translateX(2px);
        }

        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: linear-gradient(90deg, var(--accent-soft), rgba(255,255,255,0.02)) !important;
            border: 1px solid rgba(21,128,61,0.25) !important;
            color: var(--text) !important;
            font-weight: 700;
        }

        .executive-header {
            background: linear-gradient(135deg, #FFFFFF 0%, #F7FAF7 100%);
            border-radius: 14px;
            padding: 24px 28px;
            color: var(--text) !important;
            margin-bottom: 20px;
            box-shadow: 0 10px 20px -12px var(--shadow);
            border: 1px solid var(--border);
        }

        html[data-theme="dark"] .executive-header,
        body[data-theme="dark"] .executive-header {
            background: linear-gradient(135deg, #122118 0%, #163C28 100%) !important;
            border-color: var(--border) !important;
            box-shadow: 0 10px 20px -12px rgba(0, 0, 0, 0.38) !important;
        }

        .header-title {
            font-size: 1.95rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            margin-bottom: 6px;
            color: var(--text);
        }

        .header-subtitle {
            font-size: 0.98rem;
            color: var(--muted);
            max-width: 900px;
            line-height: 1.45;
            margin-bottom: 12px;
        }

        .badge-pill {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-right: 6px;
            background: var(--accent-soft);
            color: var(--accent-dark);
            border: 1px solid rgba(21,128,61,0.18);
        }

        .kpi-card {
            background: var(--panel) !important;
            border-radius: 12px;
            padding: 18px 20px;
            border: 1px solid var(--border);
            box-shadow: 0 6px 18px -14px var(--shadow);
            position: relative;
            overflow: hidden;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            color: var(--text) !important;
        }

        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -16px var(--shadow);
        }

        .kpi-stripe {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
        }

        .stripe-blue { background: #15803D; }
        .stripe-emerald { background: #16A34A; }
        .stripe-purple { background: #4ADE80; }
        .stripe-amber { background: #22C55E; }
        .stripe-rose { background: #65A30D; }

        .kpi-title {
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }

        .kpi-value {
            font-size: 1.85rem;
            font-weight: 800;
            color: var(--text);
            line-height: 1.15;
            margin-bottom: 4px;
        }

        .kpi-caption {
            font-size: 0.78rem;
            color: var(--muted);
        }

        .story-box {
            background: var(--panel);
            border-radius: 10px;
            border-left: 4px solid var(--accent);
            padding: 14px 18px;
            margin-bottom: 16px;
            font-size: 0.9rem;
            color: var(--text);
            line-height: 1.45;
            box-shadow: 0 2px 10px -8px var(--shadow);
        }

        .story-box-amber { border-left-color: #22C55E; background: rgba(34,197,94,0.06); }
        .story-box-emerald { border-left-color: #16A34A; background: rgba(22,163,74,0.06); }

        .action-card {
            background: var(--panel) !important;
            border-radius: 10px;
            border: 1px solid var(--border);
            padding: 14px 16px;
            margin-bottom: 10px;
            box-shadow: 0 6px 14px -16px var(--shadow);
            color: var(--text) !important;
        }

        .badge-status-overload { background: rgba(34,197,94,0.08); color: var(--accent-dark); padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }
        .badge-status-under { background: rgba(34,197,94,0.08); color: var(--accent-dark); padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }
        .badge-status-optimal { background: rgba(34,197,94,0.12); color: var(--accent-dark); padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }
        .badge-status-star { background: rgba(74,222,128,0.12); color: var(--accent-dark); padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }

        div[data-testid="stDataFrame"], div[data-testid="stDataFrameScrollWrap"], .stDataFrameContainer {
            background: var(--panel) !important;
            color: var(--text) !important;
            border: 1px solid var(--border);
            border-radius: 12px;
        }

        table, th, td, .stDataFrame tbody tr, .stDataFrame thead tr {
            color: var(--text) !important;
            background: var(--panel) !important;
        }

        .stTabs [role="tablist"] button {
            color: var(--text) !important;
        }

        .stExpander {
            background: var(--panel) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px;
        }

        .stExpander summary {
            color: var(--text) !important;
        }
    </style>
    """


def create_workforce_quadrant_chart(df: pd.DataFrame) -> go.Figure:
    """
    Creates an executive scatter plot showing Work Hours vs Task Completion with 4 utilization quadrants.
    """
    color_map = {
        'Overloaded': '#166534',
        'Underutilized': '#22C55E',
        'High Performer': '#15803D',
        'Optimal / Balanced': '#4ADE80'
    }

    fig = px.scatter(
        df,
        x='Weekly_Work_Hours',
        y='Task_Completion_Pct',
        color='Workforce_Status',
        color_discrete_map=color_map,
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
        template='plotly_white'
    )

    # Reference lines
    fig.add_vline(x=45, line_dash="dash", line_color="#94A3B8")
    fig.add_vline(x=38, line_dash="dot", line_color="#CBD5E1")
    fig.add_hline(y=80, line_dash="dash", line_color="#94A3B8")

    # Annotations
    fig.add_annotation(x=55, y=55, text="<b>🚨 High Overload Zone</b>", showarrow=False, font=dict(color="#166534", size=10), bgcolor="rgba(220, 252, 231, 0.7)")
    fig.add_annotation(x=33, y=92, text="<b>⚡ Slack / Underutilized</b>", showarrow=False, font=dict(color="#22C55E", size=10), bgcolor="rgba(220, 252, 231, 0.75)")
    fig.add_annotation(x=55, y=95, text="<b>🔥 Strained Stars</b>", showarrow=False, font=dict(color="#15803D", size=10), bgcolor="rgba(234, 245, 236, 0.8)")
    fig.add_annotation(x=41, y=88, text="<b>✅ Optimal Core</b>", showarrow=False, font=dict(color="#166534", size=10), bgcolor="rgba(234, 245, 236, 0.8)")

    theme = _plotly_theme_settings()
    fig.update_layout(
        height=420,
        template=theme["template"],
        paper_bgcolor=theme["paper_bgcolor"],
        plot_bgcolor=theme["plot_bgcolor"],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=theme["text_color"]),
            bgcolor=theme["legend_bg"],
        ),
        margin=dict(l=30, r=30, t=60, b=30),
        font=dict(family="Plus Jakarta Sans, sans-serif", color=theme["text_color"]),
        xaxis=dict(gridcolor=theme["grid_color"], tickfont=dict(color=theme["axis_color"]), title_font=dict(color=theme["axis_color"]), zerolinecolor=theme["grid_color"]),
        yaxis=dict(gridcolor=theme["grid_color"], tickfont=dict(color=theme["axis_color"]), title_font=dict(color=theme["axis_color"]), zerolinecolor=theme["grid_color"]),
    )

    return fig


def create_department_benchmark_bar(dept_df: pd.DataFrame) -> go.Figure:
    """
    Creates a clean horizontal bar chart comparing departmental Task Completion %.
    """
    sorted_df = dept_df.sort_values(by='Avg_Task_Completion_Pct', ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=sorted_df['Department'],
        x=sorted_df['Avg_Task_Completion_Pct'],
        orientation='h',
        marker=dict(
            color=sorted_df['Avg_Task_Completion_Pct'],
            colorscale='Greens',
            line=dict(color='#15803D', width=1)
        ),
        text=sorted_df['Avg_Task_Completion_Pct'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside'
    ))

    theme = _plotly_theme_settings()
    fig.update_layout(
        title={"text": "<b>Avg Task Completion Rate by Department</b>", "font": {"color": theme["text_color"]}},
        template=theme["template"],
        paper_bgcolor=theme["paper_bgcolor"],
        plot_bgcolor=theme["plot_bgcolor"],
        height=350,
        xaxis=dict(range=[0, 110], title="Avg Task Completion Rate (%)", title_font=dict(color=theme["axis_color"]), tickfont=dict(color=theme["axis_color"]), gridcolor=theme["grid_color"], zerolinecolor=theme["grid_color"]),
        yaxis=dict(title="", tickfont=dict(color=theme["axis_color"]), title_font=dict(color=theme["axis_color"]), gridcolor=theme["grid_color"], zerolinecolor=theme["grid_color"]),
        margin=dict(l=30, r=30, t=50, b=30),
        font=dict(family="Plus Jakarta Sans, sans-serif", color=theme["text_color"]),
        legend=dict(font=dict(color=theme["text_color"]))
    )

    return fig


def create_utilization_distribution_pie(df: pd.DataFrame) -> go.Figure:
    """
    Creates an executive donut chart of workforce status proportions.
    """
    counts = df['Workforce_Status'].value_counts().reset_index()
    counts.columns = ['Status', 'Count']

    colors = {
        'Overloaded': '#166534',
        'Underutilized': '#22C55E',
        'High Performer': '#15803D',
        'Optimal / Balanced': '#4ADE80'
    }

    fig = px.pie(
        counts,
        values='Count',
        names='Status',
        hole=0.6,
        color='Status',
        color_discrete_map=colors,
        title="<b>Workforce Allocation Share</b>",
        template='plotly_white'
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    theme = _plotly_theme_settings()
    fig.update_layout(
        height=320,
        template=theme["template"],
        paper_bgcolor=theme["paper_bgcolor"],
        plot_bgcolor=theme["plot_bgcolor"],
        margin=dict(l=15, r=15, t=45, b=15),
        font=dict(family="Plus Jakarta Sans, sans-serif", color=theme["text_color"]),
        legend=dict(font=dict(color=theme["text_color"]))
    )
    return fig


def _green_status_palette() -> dict:
    return {
        'Overloaded': '#166534',
        'Underutilized': '#22C55E',
        'High Performer': '#15803D',
        'Optimal / Balanced': '#4ADE80'
    }


def create_hours_distribution_plot(df: pd.DataFrame) -> go.Figure:
    """
    Plotly distribution plot of weekly work hours.
    """
    fig = px.histogram(
        df,
        x="Weekly_Work_Hours",
        color="Workforce_Status",
        marginal="box",
        nbins=24,
        title="<b>Weekly Work Hours Distribution</b>",
        labels={'Weekly_Work_Hours': 'Weekly Work Hours (hrs/wk)'},
        color_discrete_map=_green_status_palette(),
        template='plotly_white'
    )
    theme = _plotly_theme_settings()
    fig.update_layout(
        height=340,
        template=theme["template"],
        paper_bgcolor=theme["paper_bgcolor"],
        plot_bgcolor=theme["plot_bgcolor"],
        margin=dict(l=30, r=30, t=100, b=30),
        font=dict(family="Plus Jakarta Sans, sans-serif", color=theme["text_color"]),
        title=dict(text="<b>Weekly Work Hours Distribution</b>", x=0.02, xanchor="left", y=0.98, font=dict(color=theme["text_color"])),
        legend=dict(orientation="h", x=0.5, y=1.12, xanchor="center", yanchor="bottom", font=dict(color=theme["text_color"]))
    )
    return fig


def create_completion_distribution_plot(df: pd.DataFrame) -> go.Figure:
    """
    Plotly distribution plot of task completion %.
    """
    fig = px.histogram(
        df,
        x="Task_Completion_Pct",
        color="Workforce_Status",
        marginal="box",
        nbins=24,
        title="<b>Task Completion % Distribution</b>",
        labels={'Task_Completion_Pct': 'Task Completion (%)'},
        color_discrete_map=_green_status_palette(),
        template='plotly_white'
    )
    theme = _plotly_theme_settings()
    fig.update_layout(
        height=340,
        template=theme["template"],
        paper_bgcolor=theme["paper_bgcolor"],
        plot_bgcolor=theme["plot_bgcolor"],
        margin=dict(l=30, r=30, t=100, b=30),
        font=dict(family="Plus Jakarta Sans, sans-serif", color=theme["text_color"]),
        title=dict(text="<b>Task Completion % Distribution</b>", x=0.02, xanchor="left", y=0.98, font=dict(color=theme["text_color"])),
        legend=dict(orientation="h", x=0.5, y=1.12, xanchor="center", yanchor="bottom", font=dict(color=theme["text_color"]))
    )
    return fig


def create_seaborn_distributions(df: pd.DataFrame) -> plt.Figure:
    """
    Static Seaborn Histogram + KDE plots for executive reporting.
    """
    sns.set_theme(style="darkgrid" if _is_dark_theme() else "whitegrid", palette="deep")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    text_color = '#F2F8F3' if _is_dark_theme() else '#17231B'
    axis_color = '#CFE1D4' if _is_dark_theme() else '#526357'
    fig.patch.set_facecolor('#122118' if _is_dark_theme() else '#ffffff')

    # Task Completion
    sns.histplot(
        df['Task_Completion_Pct'],
        kde=True,
        ax=axes[0],
        color="#15803D",
        bins=20,
        line_kws={'linewidth': 2.2}
    )
    axes[0].set_title('Task Completion % Distribution (KDE)', fontsize=11, fontweight='bold', pad=10, color=text_color)
    axes[0].set_xlabel('Task Completion (%)', fontsize=10, color=axis_color)
    axes[0].set_ylabel('Employee Count', fontsize=10, color=axis_color)
    axes[0].tick_params(axis='x', colors=axis_color)
    axes[0].tick_params(axis='y', colors=axis_color)
    axes[0].axvline(df['Task_Completion_Pct'].mean(), color='#166534', linestyle='--', label=f"Mean: {df['Task_Completion_Pct'].mean():.1f}%")
    axes[0].legend(fontsize=9, labelcolor=text_color)

    # Weekly Hours
    sns.histplot(
        df['Weekly_Work_Hours'],
        kde=True,
        ax=axes[1],
        color="#166534",
        bins=20,
        line_kws={'linewidth': 2.2}
    )
    axes[1].set_title('Weekly Work Hours Distribution (KDE)', fontsize=11, fontweight='bold', pad=10, color=text_color)
    axes[1].set_xlabel('Weekly Work Hours (hrs/wk)', fontsize=10, color=axis_color)
    axes[1].set_ylabel('Employee Count', fontsize=10, color=axis_color)
    axes[1].tick_params(axis='x', colors=axis_color)
    axes[1].tick_params(axis='y', colors=axis_color)
    axes[1].axvline(40, color='#15803D', linestyle=':', label='40h Baseline')
    axes[1].axvline(df['Weekly_Work_Hours'].mean(), color='#166534', linestyle='--', label=f"Mean: {df['Weekly_Work_Hours'].mean():.1f}h")
    axes[1].legend(fontsize=9, labelcolor=text_color)

    plt.tight_layout()
    return fig


def create_gauge_indicator(title: str, value: float, max_val: float = 100.0, suffix: str = "%") -> go.Figure:
    """
    Gauge widget for key indicators.
    """
    theme = _plotly_theme_settings()
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 13, 'color': theme['text_color']}},
        number={'suffix': suffix, 'font': {'size': 24, 'color': theme['text_color'], 'family': 'Plus Jakarta Sans'}},
        gauge={
            'axis': {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': theme['axis_color']},
            'bar': {'color': "#15803D"},
            'bgcolor': theme['paper_bgcolor'],
            'borderwidth': 1,
            'bordercolor': theme['axis_color'],
            'steps': [
                {'range': [0, max_val * 0.35], 'color': '#DCFCE7'},
                {'range': [max_val * 0.35, max_val * 0.65], 'color': '#FEF3C7'},
                {'range': [max_val * 0.65, max_val], 'color': '#FEE2E2'}
            ]
        }
    ))
    fig.update_layout(
        height=160,
        margin=dict(l=15, r=15, t=25, b=15),
        paper_bgcolor=theme['paper_bgcolor'],
        plot_bgcolor=theme['plot_bgcolor'],
        font=dict(color=theme['text_color'])
    )
    return fig
