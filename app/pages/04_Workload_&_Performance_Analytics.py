import streamlit as st
import numpy as np

from app.page_shared import configure_app, get_filtered_workforce, render_empty_state, render_kpi_card, render_page_header
from app.utils import create_completion_distribution_plot, create_hours_distribution_plot, create_seaborn_distributions


configure_app(page_title="Workload & Performance Analytics")
render_page_header(
    title="Workload & Performance Analytics",
    subtitle="Examine workload intensity curves and task completion variance across personnel to isolate operational drag and systemic overtime.",
    badges=["📈 Distribution Curves", "⏱️ Workload Spread", "📊 Variance Diagnostics"],
)

df_raw, df = get_filtered_workforce()
if df.empty:
    render_empty_state()

# Summary Metrics Row
avg_hours = round(df["Weekly_Work_Hours"].mean(), 1)
std_hours = round(df["Weekly_Work_Hours"].std(), 1)
avg_completion = round(df["Task_Completion_Pct"].mean(), 1)
overtime_pct = round((df["Weekly_Work_Hours"] > 40.0).mean() * 100, 1)

st.markdown("#### 📊 Cohort Distribution Summary")
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card(
        "Avg Weekly Hours",
        f"{avg_hours}h",
        f"Std Dev: ±{std_hours} hrs/wk",
        stripe="stripe-sky",
        chip="Workload",
        chip_theme="blue",
    )
with c2:
    render_kpi_card(
        "Overtime Exposure",
        f"{overtime_pct}%",
        "Staff working > 40 hrs/wk",
        stripe="stripe-amber",
        chip="Overtime",
        chip_theme="amber",
    )
with c3:
    render_kpi_card(
        "Avg Task Completion",
        f"{avg_completion}%",
        "Target Baseline: ≥ 80.0%",
        stripe="stripe-emerald",
        chip="Output",
        chip_theme="emerald",
    )
with c4:
    completion_std = round(df["Task_Completion_Pct"].std(), 1)
    render_kpi_card(
        "Completion Variance",
        f"±{completion_std}%",
        "Output dispersion indicator",
        stripe="stripe-purple",
        chip="Consistency",
        chip_theme="purple",
    )

st.markdown("---")

tab_interactive, tab_statistical = st.tabs(["📊 Interactive Plotly Analytics", "📉 Statistical Seaborn KDE Density"])

with tab_interactive:
    left, right = st.columns(2)
    with left:
        st.plotly_chart(create_hours_distribution_plot(df), use_container_width=True)
    with right:
        st.plotly_chart(create_completion_distribution_plot(df), use_container_width=True)

with tab_statistical:
    fig = create_seaborn_distributions(df)
    st.pyplot(fig)

st.markdown(
    """
    <div class="story-box">
        <strong>Strategic Advisory:</strong> A pronounced right skew in weekly work hours indicates concentrated overtime dependencies where a subset of the workforce absorbs disproportionate project load. When high work hours coincide with stagnant or decreasing task completion, it signals cognitive fatigue and operational drag. We recommend implementing workload caps at 45 hrs/week and redistributing tickets to teams with slack capacity.
    </div>
    """,
    unsafe_allow_html=True,
)
