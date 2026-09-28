import streamlit as st

from app.backend import compute_department_kpis
from app.page_shared import configure_app, get_filtered_workforce, render_empty_state, render_page_header
from app.utils import create_department_benchmark_bar


configure_app(page_title="Department Analytics")
render_page_header(
    title="Department Benchmarking & Performance Analytics",
    subtitle="Evaluate departmental productivity, attendance adherence, workload intensity, and attrition risk to replicate high-performance team habits.",
    badges=["🏢 Department Benchmarks", "📊 Cross-Team Comparison", "📈 Operational Efficiency"],
)

df_raw, df = get_filtered_workforce()
if df.empty:
    render_empty_state()

dept_df = compute_department_kpis(df)

chart_col, summary_col = st.columns([6, 6])
with chart_col:
    st.plotly_chart(create_department_benchmark_bar(dept_df), use_container_width=True)

with summary_col:
    st.markdown("#### 🌟 Departmental Performance Spotlight")
    if len(dept_df) >= 2:
        top = dept_df.iloc[0]
        bottom = dept_df.iloc[-1]
        st.markdown(
            f"""
            <div class="action-card" style="border-left: 4px solid var(--emerald); margin-bottom: 0.85rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span class="kpi-chip kpi-chip-emerald">🏆 HIGHEST COMPLETION RATE</span>
                    <span style="font-size:0.75rem; color:var(--muted); font-weight:700;">Rank #1</span>
                </div>
                <div style="font-weight:800; font-size:1.15rem; color:var(--text); margin-bottom:6px;">{top['Department']}</div>
                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:0.5rem; font-size:0.85rem; color:var(--text);">
                    <div><span style="color:var(--muted); font-size:0.75rem; display:block;">Avg Completion</span><b>{top['Avg_Task_Completion_Pct']}%</b></div>
                    <div><span style="color:var(--muted); font-size:0.75rem; display:block;">Avg Workload</span><b>{top['Avg_Weekly_Hours']} hrs/wk</b></div>
                    <div><span style="color:var(--muted); font-size:0.75rem; display:block;">Overload Rate</span><b>{top['Overloaded_Pct']}%</b></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="action-card" style="border-left: 4px solid var(--rose); margin-bottom: 0.85rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span class="kpi-chip kpi-chip-rose">⚠️ BOTTLENECK WATCHLIST</span>
                    <span style="font-size:0.75rem; color:var(--muted); font-weight:700;">Needs Support</span>
                </div>
                <div style="font-weight:800; font-size:1.15rem; color:var(--text); margin-bottom:6px;">{bottom['Department']}</div>
                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:0.5rem; font-size:0.85rem; color:var(--text);">
                    <div><span style="color:var(--muted); font-size:0.75rem; display:block;">Avg Completion</span><b>{bottom['Avg_Task_Completion_Pct']}%</b></div>
                    <div><span style="color:var(--muted); font-size:0.75rem; display:block;">Avg Workload</span><b>{bottom['Avg_Weekly_Hours']} hrs/wk</b></div>
                    <div><span style="color:var(--muted); font-size:0.75rem; display:block;">Overload Rate</span><b>{bottom['Overloaded_Pct']}%</b></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Select multiple departments in the sidebar to view comparative highlights.")

st.markdown("---")

st.markdown("### 📋 Comprehensive Department Scorecard")
st.dataframe(
    dept_df.style.format({
        "Avg_Task_Completion_Pct": "{:.1f}%",
        "Avg_Weekly_Hours": "{:.1f}h",
        "Avg_Manager_Rating": "{:.2f}",
        "Avg_Attendance_Pct": "{:.1f}%",
        "Avg_Productivity_Score": "{:.1f}",
        "Avg_Satisfaction": "{:.1f}/10",
        "Avg_Salary_INR": "₹{:,}",
        "Overloaded_Pct": "{:.1f}%",
        "Underutilized_Pct": "{:.1f}%",
        "Attrition_Rate_Pct": "{:.1f}%",
    }),
    use_container_width=True,
    hide_index=True,
)
