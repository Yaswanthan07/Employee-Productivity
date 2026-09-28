import streamlit as st

from app.ml_models import score_batch_workforce
from app.page_shared import configure_app, get_filtered_workforce, render_empty_state, render_kpi_card, render_page_header


configure_app(page_title="Employee Data Explorer")
render_page_header(
    title="Employee Intelligence & Data Explorer",
    subtitle="Inspect, filter, drill down, and export individual employee records enriched with ML attrition forecasts and productivity classifications.",
    badges=["📂 Data Explorer", "🔎 Granular Records", "📤 Export Pipelines"],
)

df_raw, df = get_filtered_workforce()
if df.empty:
    render_empty_state()

scored = score_batch_workforce(df)

# Quick Cohort Summary Cards
st.markdown("#### 📊 Filtered Cohort Overview")
k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi_card(
        "Active Employee Records",
        f"{len(df):,}",
        f"{round(len(df)/len(df_raw)*100, 1)}% of total company records",
        stripe="stripe-indigo",
        chip="Records",
        chip_theme="blue",
    )
with k2:
    avg_salary = int(df["Monthly_Salary_INR"].mean())
    render_kpi_card(
        "Avg Monthly Salary",
        f"₹{avg_salary:,}",
        "Active cohort payroll baseline",
        stripe="stripe-emerald",
        chip="Payroll",
        chip_theme="emerald",
    )
with k3:
    avg_task = round(df["Task_Completion_Pct"].mean(), 1)
    render_kpi_card(
        "Avg Task Completion",
        f"{avg_task}%",
        "Target Baseline: ≥ 80.0%",
        stripe="stripe-sky",
        chip="Output",
        chip_theme="blue",
    )
with k4:
    high_risk_count = len(scored[scored["AI_Risk_Category"] == "High"])
    render_kpi_card(
        "High Risk Count",
        f"{high_risk_count}",
        f"{round(high_risk_count/len(df)*100, 1) if len(df) else 0}% flagged by AI model",
        stripe="stripe-rose",
        chip="Risk Alert",
        chip_theme="rose",
    )

st.markdown("---")

show_cols = [
    'Employee_ID', 'Department', 'Job_Role', 'Total_Experience_Years',
    'Monthly_Salary_INR', 'Weekly_Work_Hours', 'Task_Completion_Pct',
    'Attendance_Pct', 'Manager_Rating', 'Workforce_Status',
    'AI_Attrition_Risk_Pct', 'AI_Risk_Category', 'AI_Predicted_Productivity_Tier'
]

st.markdown("### 📋 Enriched Employee Records")
st.dataframe(
    scored[show_cols].style.format({
        "Monthly_Salary_INR": "₹{:,}",
        "Weekly_Work_Hours": "{:.1f}h",
        "Task_Completion_Pct": "{:.1f}%",
        "Attendance_Pct": "{:.1f}%",
        "Manager_Rating": "{:.2f}",
        "AI_Attrition_Risk_Pct": "{:.1f}%",
    }),
    use_container_width=True,
    height=440,
    hide_index=True,
)

st.markdown("---")

st.markdown("### 📤 Export Dataset for Reporting")
exp1, exp2 = st.columns(2)
with exp1:
    st.markdown(
        """
        <div class="action-card">
            <div style="font-weight:700; font-size:0.95rem; margin-bottom:4px;">📄 Cleaned Cohort Dataset</div>
            <div style="font-size:0.84rem; color:var(--muted); margin-bottom:12px;">Standard normalized employee records suitable for internal HR reporting and Excel dashboards.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    clean_csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Cleaned CSV",
        data=clean_csv,
        file_name="employee_productivity_clean.csv",
        mime="text/csv",
        use_container_width=True,
    )
with exp2:
    st.markdown(
        """
        <div class="action-card">
            <div style="font-weight:700; font-size:0.95rem; margin-bottom:4px;">📊 AI-Enriched Power BI Dataset</div>
            <div style="font-size:0.84rem; color:var(--muted); margin-bottom:12px;">Includes ML attrition probabilities, risk tiers, and predicted productivity classifications.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    powerbi_csv = scored.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download AI-Enriched CSV",
        data=powerbi_csv,
        file_name="employee_productivity_powerbi_enriched.csv",
        mime="text/csv",
        use_container_width=True,
        type="primary",
    )
