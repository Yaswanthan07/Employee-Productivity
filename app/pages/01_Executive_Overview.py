import streamlit as st

from app.backend import compute_department_kpis, compute_top_level_kpis
from app.page_shared import configure_app, get_filtered_workforce, render_empty_state, render_kpi_card, render_page_header
from app.utils import create_department_benchmark_bar, create_utilization_distribution_pie


configure_app(page_title="Executive Overview")
render_page_header(
    title="Executive Overview",
    subtitle="Enterprise 360° health scan: delivery efficiency, workload balance, managerial sentiment, and talent risk across the active workforce cohort.",
    badges=["📊 KPI Command Center", "⚡ Workforce Pulse", "🤖 Predictive AI Lens"],
)

df_raw, df = get_filtered_workforce()
if df.empty:
    render_empty_state()

kpis = compute_top_level_kpis(df)

# Operational & Productivity Benchmarks
st.markdown("#### 🎯 Delivery & Productivity Benchmarks")
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card(
        "Avg Task Completion",
        f"{kpis['avg_task_completion']}%",
        "Target Benchmark: ≥ 80.0%",
        stripe="stripe-indigo",
        chip="Output",
        chip_theme="blue",
    )
with col2:
    render_kpi_card(
        "Avg Weekly Hours",
        f"{kpis['avg_weekly_hours']}h",
        "Sustainable Standard: 40–45 hrs",
        stripe="stripe-sky",
        chip="Workload",
        chip_theme="blue",
    )
with col3:
    render_kpi_card(
        "Avg Manager Rating",
        f"{kpis['avg_manager_rating']}/5.0",
        "Target: ≥ 3.8 / 5.0",
        stripe="stripe-emerald",
        chip="Sentiment",
        chip_theme="emerald",
    )
with col4:
    render_kpi_card(
        "Avg Attendance Rate",
        f"{kpis['avg_attendance']}%",
        "Adherence Target: ≥ 90.0%",
        stripe="stripe-emerald",
        chip="Reliability",
        chip_theme="emerald",
    )

st.write("")

# Workforce Health & Capacity Allocation
st.markdown("#### ⚖️ Capacity Health & Talent Risk Exposure")
m1, m2, m3, m4 = st.columns(4)
with m1:
    render_kpi_card(
        "Overloaded Staff",
        f"{kpis['overloaded_count']}",
        f"{kpis['overloaded_pct']}% of active cohort (>45 hrs/wk)",
        stripe="stripe-rose",
        chip="🚨 Overload",
        chip_theme="rose",
    )
with m2:
    render_kpi_card(
        "Underutilized Staff",
        f"{kpis['underutilized_count']}",
        f"{kpis['underutilized_pct']}% available for reallocation",
        stripe="stripe-amber",
        chip="⚡ Slack Capacity",
        chip_theme="amber",
    )
with m3:
    render_kpi_card(
        "High Performers",
        f"{kpis['high_performers_count']}",
        f"{kpis['high_performers_pct']}% top rating & high completion",
        stripe="stripe-purple",
        chip="⭐ Key Talent",
        chip_theme="purple",
    )
with m4:
    render_kpi_card(
        "Elevated Burnout",
        f"{kpis['burnout_high_count']}",
        f"{kpis['burnout_high_pct']}% flagged for intervention",
        stripe="stripe-rose",
        chip="🔥 High Risk",
        chip_theme="rose",
    )

st.markdown("---")

# Analytical Visual Cards
chart_left, chart_right = st.columns(2)
with chart_left:
    st.plotly_chart(create_utilization_distribution_pie(df), use_container_width=True)
with chart_right:
    dept_df = compute_department_kpis(df)
    st.plotly_chart(create_department_benchmark_bar(dept_df), use_container_width=True)

# Executive Callout
st.markdown(
    f"""
    <div class="story-box">
        <strong>Executive Advisory:</strong> Active workforce slice of <b>{len(df):,}</b> employees is operating at an average <b>{kpis['avg_task_completion']}%</b> task completion with <b>{kpis['avg_weekly_hours']} hrs/week</b> average commitment. Currently, <b>{kpis['overloaded_count']} employees ({kpis['overloaded_pct']}%)</b> are in the critical overload zone, while <b>{kpis['underutilized_count']} employees ({kpis['underutilized_pct']}%)</b> represent reallocatable capacity. Rebalancing tasks from overloaded teams into underutilized personnel is projected to mitigate burnout while elevating output.
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(f"Showing {len(df):,} of {len(df_raw):,} total workforce records in active slice.")
