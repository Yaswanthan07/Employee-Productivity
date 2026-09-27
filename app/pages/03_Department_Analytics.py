import streamlit as st

from app.backend import compute_department_kpis
from app.page_shared import configure_app, get_filtered_workforce, render_empty_state, render_page_header
from app.utils import create_department_benchmark_bar


configure_app(page_title="Department Analytics")
render_page_header(
    title="Department Analytics",
    subtitle="Benchmark departments on productivity, attendance, workload intensity, and employee risk to uncover bottlenecks and replicate high-performance patterns.",
    badges=["🏢 Benchmarked Teams", "📊 Performance Comparison", "📈 Capacity Insights"],
)

df_raw, df = get_filtered_workforce()
if df.empty:
    render_empty_state()

dept_df = compute_department_kpis(df)

chart_col, summary_col = st.columns([6, 4])
with chart_col:
    st.plotly_chart(create_department_benchmark_bar(dept_df), use_container_width=True)
with summary_col:
    st.markdown("#### High & Low Performing Departments")
    if len(dept_df) >= 2:
        top = dept_df.iloc[0]
        bottom = dept_df.iloc[-1]
        st.markdown(
            f"""
            <div class="action-card" style="border-left:4px solid #15803D;">
                <div style="font-size:0.75rem; font-weight:700; color:#15803D; text-transform:uppercase;">🥇 Top department</div>
                <div style="font-weight:800; font-size:1.1rem; color:var(--text);">{top['Department']}</div>
                <div style="font-size:0.85rem; color:var(--muted);">
                    • Task Completion: <b>{top['Avg_Task_Completion_Pct']}%</b><br>
                    • Weekly Hours: <b>{top['Avg_Weekly_Hours']}h</b><br>
                    • Overload Rate: <b>{top['Overloaded_Pct']}%</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="action-card" style="border-left:4px solid #166534;">
                <div style="font-size:0.75rem; font-weight:700; color:#166534; text-transform:uppercase;">⚠️ Lowest productivity</div>
                <div style="font-weight:800; font-size:1.1rem; color:var(--text);">{bottom['Department']}</div>
                <div style="font-size:0.85rem; color:var(--muted);">
                    • Task Completion: <b>{bottom['Avg_Task_Completion_Pct']}%</b><br>
                    • Weekly Hours: <b>{bottom['Avg_Weekly_Hours']}h</b><br>
                    • Overload Rate: <b>{bottom['Overloaded_Pct']}%</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("### Department Scorecard")
with st.expander("🔍 View complete department detail table"):
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
