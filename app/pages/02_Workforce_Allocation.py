import streamlit as st

from app.backend import compute_top_level_kpis, generate_allocation_recommendations
from app.page_shared import configure_app, get_filtered_workforce, render_empty_state, render_kpi_card, render_page_header
from app.utils import create_utilization_distribution_pie, create_workforce_quadrant_chart


configure_app(page_title="Workforce Allocation")
render_page_header(
    title="Workforce Allocation",
    subtitle="Diagnose overload, identify underutilized capacity, and surface reallocation strategies that rebalance teams without compromising productivity or employee wellbeing.",
    badges=["⚖️ Capacity Balance", "🚨 Overload Alerts", "🎯 Reallocation Playbooks"],
)

df_raw, df = get_filtered_workforce()
if df.empty:
    render_empty_state()

kpis = compute_top_level_kpis(df)
recommendations = generate_allocation_recommendations(df)

st.markdown('<div class="section-shell">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    render_kpi_card("Overloaded Staff", f"{kpis['overloaded_count']}", f"{kpis['overloaded_pct']}% of active cohort", "stripe-red")
with col2:
    render_kpi_card("Underutilized Staff", f"{kpis['underutilized_count']}", f"{kpis['underutilized_pct']}% available capacity", "stripe-amber")
with col3:
    render_kpi_card("High Performers", f"{kpis['high_performers_count']}", f"{kpis['high_performers_pct']}% stars", "stripe-emerald")
st.markdown('</div>', unsafe_allow_html=True)

left, right = st.columns([5, 5])
with left:
    st.plotly_chart(create_utilization_distribution_pie(df), use_container_width=True)
with right:
    st.plotly_chart(create_workforce_quadrant_chart(df), use_container_width=True)

st.markdown("### Priority Reallocation Strategy")
if recommendations:
    for rec in recommendations[:4]:
        badge_color = "#166534" if rec["priority"] == "HIGH" else "#15803D"
        st.markdown(
            f"""
            <div class="action-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span style="font-size:0.72rem; font-weight:700; color:{badge_color}; text-transform:uppercase;">● {rec['priority']} PRIORITY | {rec['type']}</span>
                    <span style="font-size:0.78rem; color:var(--muted); font-weight:600;">{rec['department']}</span>
                </div>
                <div style="font-weight:700; font-size:0.96rem; color:var(--text); margin-bottom:4px;">{rec['title']}</div>
                <div style="font-size:0.84rem; color:var(--muted); line-height:1.45; margin-bottom:5px;">{rec['description']}</div>
                <div style="font-size:0.8rem; font-weight:600; color:#166534;">👉 Action: {rec['action_item']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.success("✅ Workforce load is evenly balanced across the selected filters.")

st.subheader("Workforce Action Lists")
ov, un = st.tabs(["🚨 Top Overloaded Employees", "⚡ Top Underutilized Employees"])
with ov:
    top_ov = df[df["Workforce_Status"] == "Overloaded"][
        ["Employee_ID", "Department", "Job_Role", "Weekly_Work_Hours", "Overtime_Hours_Weekly", "Task_Completion_Pct", "Burnout_Risk_Level"]
    ].sort_values(by="Weekly_Work_Hours", ascending=False).head(5)
    if not top_ov.empty:
        st.dataframe(top_ov.style.format({"Weekly_Work_Hours": "{:.1f}h", "Overtime_Hours_Weekly": "{:.1f}h", "Task_Completion_Pct": "{:.1f}%"}), use_container_width=True, hide_index=True)
    else:
        st.info("No overloaded employees in the current slice.")
with un:
    top_un = df[df["Workforce_Status"] == "Underutilized"][
        ["Employee_ID", "Department", "Job_Role", "Weekly_Work_Hours", "Projects_Handled", "Task_Completion_Pct", "Satisfaction_Score"]
    ].sort_values(by="Weekly_Work_Hours", ascending=True).head(5)
    if not top_un.empty:
        st.dataframe(top_un.style.format({"Weekly_Work_Hours": "{:.1f}h", "Task_Completion_Pct": "{:.1f}%", "Satisfaction_Score": "{:.1f}/10"}), use_container_width=True, hide_index=True)
    else:
        st.info("No underutilized employees in the current slice.")
