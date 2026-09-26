import streamlit as st

from app.backend import compute_top_level_kpis
from app.page_shared import configure_app, get_filtered_workforce, render_empty_state, render_kpi_card, render_page_header


configure_app(page_title="Executive Overview")
render_page_header(
    title="Executive Overview",
    subtitle="A premium, 30-second health scan of delivery efficiency, workload balance, managerial sentiment, and people risk across the current workforce slice.",
    badges=["📊 KPI Command Center", "⚡ Workforce Pulse", "🤖 AI Risk Lens"],
)

df_raw, df = get_filtered_workforce()
if df.empty:
    render_empty_state()

kpis = compute_top_level_kpis(df)

st.markdown('<div class="section-shell">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card("Avg Task Completion", f"{kpis['avg_task_completion']}%", "🎯 Benchmark: ≥ 80.0%", "stripe-blue")
with col2:
    render_kpi_card("Avg Weekly Hours", f"{kpis['avg_weekly_hours']}h", "⏱️ Baseline: 40–45 hrs", "stripe-purple")
with col3:
    render_kpi_card("Avg Manager Rating", f"{kpis['avg_manager_rating']}/5.0", "⭐ Target: ≥ 3.8 / 5.0", "stripe-emerald")
with col4:
    render_kpi_card("Avg Attendance Rate", f"{kpis['avg_attendance']}%", "📅 Adherence target: ≥ 90%", "stripe-amber")
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("🚨 Overloaded Staff", f"{kpis['overloaded_count']}", f"{kpis['overloaded_pct']}% of slice", delta_color="inverse")
with m2:
    st.metric("⚡ Underutilized Staff", f"{kpis['underutilized_count']}", f"{kpis['underutilized_pct']}% capacity", delta_color="off")
with m3:
    st.metric("🌟 High Performers", f"{kpis['high_performers_count']}", f"{kpis['high_performers_pct']}% stars", delta_color="normal")
with m4:
    st.metric("🔥 Burnout High", f"{kpis['burnout_high_count']}", f"{kpis['burnout_high_pct']}% flagged", delta_color="inverse")

st.markdown("### Executive Signal Summary")
st.markdown(
    f"""
    <div class="story-box">
        <strong>Current workforce condition:</strong> The active cohort is operating at <b>{kpis['avg_task_completion']}%</b> average completion, <b>{kpis['avg_weekly_hours']} hrs/week</b> workload exposure, and <b>{kpis['attrition_rate']}%</b> attrition rate. The organization is showing a healthy balance when workload remains within the target range, but the most material risk remains in overburdened teams with elevated burnout indicators.
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(f"Filtered employees: {len(df):,} / {len(df_raw):,} total records")
