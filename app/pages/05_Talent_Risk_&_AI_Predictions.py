import streamlit as st

from app.backend import compute_top_level_kpis
from app.ml_models import get_attrition_model, get_productivity_model, get_risk_summary
from app.page_shared import configure_app, get_filtered_workforce, render_empty_state, render_kpi_card, render_page_header
from app.utils import create_gauge_indicator


configure_app(page_title="Talent Risk & AI Predictions")
render_page_header(
    title="Talent Risk & AI Predictions",
    subtitle="Track attrition exposure, burnout pressure, and predictive productivity outcomes with decision-ready signals for HR leadership and manager intervention.",
    badges=["🤖 AI Forecasting", "🚨 Risk Monitoring", "🧠 Scenario Simulation"],
)

df_raw, df = get_filtered_workforce()
if df.empty:
    render_empty_state()

kpis = compute_top_level_kpis(df)
risk_summary = get_risk_summary(df)

st.markdown('<div class="section-shell">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card("High Attrition Risk", f"{risk_summary['high_risk_count']}", f"{risk_summary['high_risk_pct']}% of cohort", "stripe-red")
with col2:
    render_kpi_card("Moderate Risk", f"{risk_summary['medium_risk_pct']}%", "Risk pattern is emerging", "stripe-amber")
with col3:
    render_kpi_card("Low Risk / Stable", f"{risk_summary['low_risk_pct']}%", "Healthy workforce posture", "stripe-emerald")
with col4:
    render_kpi_card("Burnout High", f"{kpis['burnout_high_count']}", f"{kpis['burnout_high_pct']}% flagged", "stripe-purple")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("### Top High-Risk Employees")
if not risk_summary['sample_high_risk_df'].empty:
    st.dataframe(
        risk_summary['sample_high_risk_df'].style.format({
            'Weekly_Work_Hours': '{:.1f}h',
            'Overtime_Hours_Weekly': '{:.1f}h',
            'Satisfaction_Score': '{:.1f}/10',
            'AI_Attrition_Risk_Pct': '{:.1f}%'
        }),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No high-risk employees are present in the current slice.")

with st.expander("🔮 Open interactive what-if scenario simulator"):
    st.caption("Adjust core employee attributes to simulate risk and productivity outcomes in real time.")
    sim_left, sim_right = st.columns([5, 5])

    with sim_left:
        dept_options = sorted(df_raw['Department'].unique().tolist())
        s_dept = st.selectbox("Department", dept_options, index=0)
        s_hours = st.slider("Weekly Work Hours", 25.0, 70.0, 52.0, 0.5)
        s_ot = max(0.0, s_hours - 40.0)
        st.caption(f"Calculated overtime: **{s_ot:.1f} hrs/wk**")
        s_rating = st.slider("Manager Rating (1-5)", 1.0, 5.0, 3.2, 0.1)
        s_sat = st.slider("Satisfaction Score (1-10)", 1.0, 10.0, 4.5, 0.5)
        s_burnout = st.selectbox("Burnout Level", ["Low", "Medium", "High"], index=2)
        s_salary = st.number_input("Monthly Salary (INR)", min_value=25000, max_value=500000, value=95000, step=5000)

    with sim_right:
        payload = {
            'Age': 30,
            'Gender': 'Male',
            'Department': s_dept,
            'Education_Level': 'Bachelor',
            'Total_Experience_Years': 5.0,
            'Years_at_Company': 3.0,
            'Monthly_Salary_INR': s_salary,
            'Weekly_Work_Hours': s_hours,
            'Overtime_Hours_Weekly': s_ot,
            'Projects_Handled': 6,
            'Task_Completion_Pct': 75.0,
            'Attendance_Pct': 92.0,
            'Manager_Rating': s_rating,
            'Satisfaction_Score': s_sat,
            'Burnout_Risk_Level': s_burnout,
            'Work_From_Home_Pct': 40,
            'Training_Hours_Last_Year': 20,
            'Promotion_Last_2Years': 'No'
        }

        att_model = get_attrition_model()
        prod_model = get_productivity_model()
        att_res = att_model.predict(payload)
        prod_res = prod_model.predict(payload)

        st.plotly_chart(create_gauge_indicator("Predicted Attrition Risk", att_res['attrition_probability_pct'], 100.0, "%"), use_container_width=True)
        st.markdown(f"**Predicted Productivity Tier:** `{prod_res['predicted_tier']}`")
        st.markdown(f"**Strategic HR Guidance:** {prod_res['strategic_guidance']}")
