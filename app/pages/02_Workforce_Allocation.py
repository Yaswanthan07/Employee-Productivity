import streamlit as st

from app.backend import compute_top_level_kpis, generate_allocation_recommendations
from app.page_shared import configure_app, get_filtered_workforce, render_empty_state, render_kpi_card, render_page_header
from app.utils import create_utilization_distribution_pie, create_workforce_quadrant_chart


configure_app(page_title="Workforce Allocation")
render_page_header(
    title="Workforce Allocation & Capacity Balancing",
    subtitle="Diagnose overload bottlenecks, unlock latent capacity, and execute targeted reallocation playbooks that balance team workload without sacrificing output.",
    badges=["⚖️ Capacity Equilibrium", "🚨 Overload Mitigation", "🎯 Reallocation Playbooks"],
)

df_raw, df = get_filtered_workforce()
if df.empty:
    render_empty_state()

kpis = compute_top_level_kpis(df)
recommendations = generate_allocation_recommendations(df)

# Capacity Pulse Grid (Balanced 4 Columns)
st.markdown("#### ⚡ Capacity Distribution Summary")
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card(
        "Overloaded Staff",
        f"{kpis['overloaded_count']}",
        f"{kpis['overloaded_pct']}% of active workforce",
        stripe="stripe-rose",
        chip="🚨 Overload",
        chip_theme="rose",
    )
with col2:
    render_kpi_card(
        "Underutilized Staff",
        f"{kpis['underutilized_count']}",
        f"{kpis['underutilized_pct']}% available bandwidth",
        stripe="stripe-amber",
        chip="⚡ Reallocatable",
        chip_theme="amber",
    )
with col3:
    render_kpi_card(
        "High Performers",
        f"{kpis['high_performers_count']}",
        f"{kpis['high_performers_pct']}% key strategic talent",
        stripe="stripe-purple",
        chip="⭐ Key Talent",
        chip_theme="purple",
    )
with col4:
    optimal_count = len(df[df["Workforce_Status"] == "Optimal / Balanced"])
    optimal_pct = round((optimal_count / len(df) * 100), 1) if len(df) > 0 else 0
    render_kpi_card(
        "Balanced Core",
        f"{optimal_count}",
        f"{optimal_pct}% sustainable capacity",
        stripe="stripe-emerald",
        chip="✅ Healthy",
        chip_theme="emerald",
    )

st.markdown("---")

# Equal-height visual charts row
chart_left, chart_right = st.columns([5, 5])
with chart_left:
    st.plotly_chart(create_utilization_distribution_pie(df), use_container_width=True)
with chart_right:
    st.plotly_chart(create_workforce_quadrant_chart(df), use_container_width=True)

# Strategic Reallocation Recommendations
st.markdown("### 🎯 Priority Reallocation Action Playbooks")
if recommendations:
    rec_cols = st.columns(2)
    for idx, rec in enumerate(recommendations[:4]):
        col = rec_cols[idx % 2]
        with col:
            is_high = rec["priority"] == "HIGH"
            border_accent = "var(--rose)" if is_high else "var(--primary)"
            badge_class = "kpi-chip-rose" if is_high else "kpi-chip-blue"
            st.markdown(
                f"""
                <div class="action-card" style="border-left: 4px solid {border_accent}; min-height: 140px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <span class="kpi-chip {badge_class}">{rec['priority']} PRIORITY • {rec['type']}</span>
                        <span style="font-size:0.78rem; color:var(--muted); font-weight:700;">🏢 {rec['department']}</span>
                    </div>
                    <div style="font-weight:800; font-size:1.02rem; color:var(--text); margin-bottom:6px;">{rec['title']}</div>
                    <div style="font-size:0.86rem; color:var(--muted); line-height:1.5; margin-bottom:8px;">{rec['description']}</div>
                    <div style="font-size:0.84rem; font-weight:700; color:var(--primary);">👉 Recommended Action: <span style="font-weight:500; color:var(--text);">{rec['action_item']}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
else:
    st.success("✅ Workforce load is optimally balanced across all selected departments and roles.")

st.markdown("---")

# Tabular Action Lists
st.markdown("### 📋 Targeted Workforce Cohorts")
ov_tab, un_tab = st.tabs(["🚨 Overloaded Employees Requiring Load Relief", "⚡ Underutilized Employees Ready for Assignment"])
with ov_tab:
    top_ov = df[df["Workforce_Status"] == "Overloaded"][
        ["Employee_ID", "Department", "Job_Role", "Weekly_Work_Hours", "Overtime_Hours_Weekly", "Task_Completion_Pct", "Burnout_Risk_Level"]
    ].sort_values(by="Weekly_Work_Hours", ascending=False).head(10)
    if not top_ov.empty:
        st.dataframe(
            top_ov.style.format({
                "Weekly_Work_Hours": "{:.1f}h",
                "Overtime_Hours_Weekly": "{:.1f}h",
                "Task_Completion_Pct": "{:.1f}%",
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No overloaded employees identified in the active filter criteria.")

with un_tab:
    top_un = df[df["Workforce_Status"] == "Underutilized"][
        ["Employee_ID", "Department", "Job_Role", "Weekly_Work_Hours", "Projects_Handled", "Task_Completion_Pct", "Satisfaction_Score"]
    ].sort_values(by="Weekly_Work_Hours", ascending=True).head(10)
    if not top_un.empty:
        st.dataframe(
            top_un.style.format({
                "Weekly_Work_Hours": "{:.1f}h",
                "Task_Completion_Pct": "{:.1f}%",
                "Satisfaction_Score": "{:.1f}/10",
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No underutilized employees identified in the active filter criteria.")
