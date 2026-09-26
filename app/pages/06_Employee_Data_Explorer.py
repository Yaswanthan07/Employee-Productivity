import streamlit as st

from app.ml_models import score_batch_workforce
from app.page_shared import configure_app, get_filtered_workforce, render_empty_state, render_page_header


configure_app(page_title="Employee Data Explorer")
render_page_header(
    title="Employee Data Explorer",
    subtitle="Search, filter, inspect, and export workforce records for executive planning, Power BI reporting, and deeper operational analysis.",
    badges=["📂 Data Explorer", "🔎 Advanced Filters", "📤 CSV Export"],
)

df_raw, df = get_filtered_workforce()
if df.empty:
    render_empty_state()

scored = score_batch_workforce(df)
show_cols = [
    'Employee_ID', 'Department', 'Job_Role', 'Total_Experience_Years',
    'Monthly_Salary_INR', 'Weekly_Work_Hours', 'Task_Completion_Pct',
    'Attendance_Pct', 'Manager_Rating', 'Workforce_Status',
    'AI_Attrition_Risk_Pct', 'AI_Risk_Category', 'AI_Predicted_Productivity_Tier'
]

st.markdown("### Workforce Records")
st.dataframe(scored[show_cols], use_container_width=True, height=420, hide_index=True)

exp1, exp2 = st.columns(2)
with exp1:
    clean_csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📄 Download cleaned CSV dataset",
        data=clean_csv,
        file_name="employee_productivity_clean.csv",
        mime="text/csv",
    )
with exp2:
    powerbi_csv = scored.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📊 Download AI-enriched Power BI CSV",
        data=powerbi_csv,
        file_name="employee_productivity_powerbi_enriched.csv",
        mime="text/csv",
    )
