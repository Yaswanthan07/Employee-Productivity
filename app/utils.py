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


def get_custom_css() -> str:
    """
    Returns executive-grade UI styles, modern cards, and readable typography.
    """
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        
        * {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        [data-testid="stSidebarNav"] {
            padding-top: 1rem;
        }

        [data-testid="stSidebarNav"] a {
            border-radius: 12px;
            margin: 0.15rem 0.25rem;
            padding: 0.65rem 0.8rem;
            transition: all 0.2s ease;
            color: #0F172A;
        }

        [data-testid="stSidebarNav"] a:hover {
            background: rgba(59, 130, 246, 0.08);
            transform: translateX(2px);
        }

        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: linear-gradient(90deg, rgba(14, 165, 233, 0.12), rgba(59, 130, 246, 0.08));
            border: 1px solid rgba(59, 130, 246, 0.20);
            box-shadow: 0 10px 25px -18px rgba(14, 165, 233, 0.65);
            font-weight: 700;
        }

        /* Top Executive Header */
        .executive-header {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 60%, #0369A1 100%);
            border-radius: 14px;
            padding: 24px 28px;
            color: #FFFFFF;
            margin-bottom: 20px;
            box-shadow: 0 10px 20px -5px rgba(15, 23, 42, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        .header-title {
            font-size: 1.95rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            margin-bottom: 6px;
            color: #FFFFFF;
        }
        
        .header-subtitle {
            font-size: 0.98rem;
            color: #CBD5E1;
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
        }
        .badge-cyan { background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.3); }
        .badge-emerald { background: rgba(52, 211, 153, 0.15); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.3); }
        .badge-purple { background: rgba(192, 132, 252, 0.15); color: #C084FC; border: 1px solid rgba(192, 132, 252, 0.3); }

        /* KPI Metric Cards */
        .kpi-card {
            background: #FFFFFF;
            border-radius: 12px;
            padding: 18px 20px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
            position: relative;
            overflow: hidden;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.06);
        }
        .kpi-stripe {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
        }
        .stripe-blue { background: #0284C7; }
        .stripe-emerald { background: #059669; }
        .stripe-purple { background: #7C3AED; }
        .stripe-amber { background: #D97706; }
        .stripe-rose { background: #E11D48; }

        .kpi-title {
            font-size: 0.8rem;
            font-weight: 700;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }
        .kpi-value {
            font-size: 1.85rem;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.15;
            margin-bottom: 4px;
        }
        .kpi-caption {
            font-size: 0.78rem;
            color: #64748B;
        }

        /* Story & Takeaway Callout Boxes */
        .story-box {
            background: #F8FAFC;
            border-radius: 10px;
            border-left: 4px solid #0284C7;
            padding: 14px 18px;
            margin-bottom: 16px;
            font-size: 0.9rem;
            color: #334155;
            line-height: 1.45;
        }
        .story-box-amber { border-left-color: #F59E0B; background: #FFFDF5; }
        .story-box-emerald { border-left-color: #10B981; background: #F6FEF9; }
        
        .action-card {
            background: #FFFFFF;
            border-radius: 10px;
            border: 1px solid #E2E8F0;
            padding: 14px 16px;
            margin-bottom: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }

        /* Status Pills */
        .badge-status-overload { background: #FEE2E2; color: #DC2626; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }
        .badge-status-under { background: #FEF3C7; color: #D97706; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }
        .badge-status-optimal { background: #DCFCE7; color: #16A34A; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }
        .badge-status-star { background: #EDE9FE; color: #7C3AED; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }
    </style>
    """


def create_workforce_quadrant_chart(df: pd.DataFrame) -> go.Figure:
    """
    Creates an executive scatter plot showing Work Hours vs Task Completion with 4 utilization quadrants.
    """
    color_map = {
        'Overloaded': '#EF4444',
        'Underutilized': '#F59E0B',
        'High Performer': '#8B5CF6',
        'Optimal / Balanced': '#10B981'
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
    fig.add_annotation(x=55, y=55, text="<b>🚨 High Overload Zone</b>", showarrow=False, font=dict(color="#EF4444", size=10), bgcolor="rgba(254, 226, 226, 0.7)")
    fig.add_annotation(x=33, y=92, text="<b>⚡ Slack / Underutilized</b>", showarrow=False, font=dict(color="#D97706", size=10), bgcolor="rgba(254, 243, 199, 0.7)")
    fig.add_annotation(x=55, y=95, text="<b>🔥 Strained Stars</b>", showarrow=False, font=dict(color="#7C3AED", size=10), bgcolor="rgba(237, 233, 254, 0.7)")
    fig.add_annotation(x=41, y=88, text="<b>✅ Optimal Core</b>", showarrow=False, font=dict(color="#16A34A", size=10), bgcolor="rgba(220, 252, 231, 0.7)")

    fig.update_layout(
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=30, r=30, t=60, b=30),
        font=dict(family="Plus Jakarta Sans, sans-serif")
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
            colorscale='Blues',
            line=dict(color='#0284C7', width=1)
        ),
        text=sorted_df['Avg_Task_Completion_Pct'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside'
    ))

    fig.update_layout(
        title="<b>Avg Task Completion Rate by Department</b>",
        template='plotly_white',
        height=350,
        xaxis=dict(range=[0, 110], title="Avg Task Completion Rate (%)"),
        yaxis=dict(title=""),
        margin=dict(l=30, r=30, t=50, b=30),
        font=dict(family="Plus Jakarta Sans, sans-serif")
    )

    return fig


def create_utilization_distribution_pie(df: pd.DataFrame) -> go.Figure:
    """
    Creates an executive donut chart of workforce status proportions.
    """
    counts = df['Workforce_Status'].value_counts().reset_index()
    counts.columns = ['Status', 'Count']

    colors = {
        'Overloaded': '#EF4444',
        'Underutilized': '#F59E0B',
        'High Performer': '#8B5CF6',
        'Optimal / Balanced': '#10B981'
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
    fig.update_layout(
        height=320,
        margin=dict(l=15, r=15, t=45, b=15),
        font=dict(family="Plus Jakarta Sans, sans-serif")
    )
    return fig


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
        color_discrete_map={
            'Overloaded': '#EF4444',
            'Underutilized': '#F59E0B',
            'High Performer': '#8B5CF6',
            'Optimal / Balanced': '#10B981'
        },
        template='plotly_white'
    )
    fig.update_layout(
        height=340,
        margin=dict(l=30, r=30, t=50, b=30),
        font=dict(family="Plus Jakarta Sans, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
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
        color_discrete_map={
            'Overloaded': '#EF4444',
            'Underutilized': '#F59E0B',
            'High Performer': '#8B5CF6',
            'Optimal / Balanced': '#10B981'
        },
        template='plotly_white'
    )
    fig.update_layout(
        height=340,
        margin=dict(l=30, r=30, t=50, b=30),
        font=dict(family="Plus Jakarta Sans, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def create_seaborn_distributions(df: pd.DataFrame) -> plt.Figure:
    """
    Static Seaborn Histogram + KDE plots for executive reporting.
    """
    sns.set_theme(style="whitegrid", palette="deep")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    # Task Completion
    sns.histplot(
        df['Task_Completion_Pct'],
        kde=True,
        ax=axes[0],
        color="#0284C7",
        bins=20,
        line_kws={'linewidth': 2.2}
    )
    axes[0].set_title('Task Completion % Distribution (KDE)', fontsize=11, fontweight='bold', pad=10)
    axes[0].set_xlabel('Task Completion (%)', fontsize=10)
    axes[0].set_ylabel('Employee Count', fontsize=10)
    axes[0].axvline(df['Task_Completion_Pct'].mean(), color='#DC2626', linestyle='--', label=f"Mean: {df['Task_Completion_Pct'].mean():.1f}%")
    axes[0].legend(fontsize=9)

    # Weekly Hours
    sns.histplot(
        df['Weekly_Work_Hours'],
        kde=True,
        ax=axes[1],
        color="#7C3AED",
        bins=20,
        line_kws={'linewidth': 2.2}
    )
    axes[1].set_title('Weekly Work Hours Distribution (KDE)', fontsize=11, fontweight='bold', pad=10)
    axes[1].set_xlabel('Weekly Work Hours (hrs/wk)', fontsize=10)
    axes[1].set_ylabel('Employee Count', fontsize=10)
    axes[1].axvline(40, color='#16A34A', linestyle=':', label='40h Baseline')
    axes[1].axvline(df['Weekly_Work_Hours'].mean(), color='#DC2626', linestyle='--', label=f"Mean: {df['Weekly_Work_Hours'].mean():.1f}h")
    axes[1].legend(fontsize=9)

    plt.tight_layout()
    return fig


def create_gauge_indicator(title: str, value: float, max_val: float = 100.0, suffix: str = "%") -> go.Figure:
    """
    Gauge widget for key indicators.
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 13, 'color': '#334155'}},
        number={'suffix': suffix, 'font': {'size': 24, 'color': '#0F172A', 'family': 'Plus Jakarta Sans'}},
        gauge={
            'axis': {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': "#CBD5E1"},
            'bar': {'color': "#0284C7"},
            'bgcolor': "#F1F5F9",
            'borderwidth': 1,
            'bordercolor': "#E2E8F0",
            'steps': [
                {'range': [0, max_val * 0.35], 'color': '#DCFCE7'},
                {'range': [max_val * 0.35, max_val * 0.65], 'color': '#FEF3C7'},
                {'range': [max_val * 0.65, max_val], 'color': '#FEE2E2'}
            ]
        }
    ))
    fig.update_layout(height=160, margin=dict(l=15, r=15, t=25, b=15))
    return fig
