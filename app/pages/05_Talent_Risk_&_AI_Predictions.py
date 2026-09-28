import streamlit as st

from app.backend import compute_top_level_kpis
from app.ml_models import get_attrition_model, get_productivity_model, get_risk_summary
from app.page_shared import configure_app, get_filtered_workforce, render_empty_state, render_kpi_card, render_page_header
from app.utils import create_gauge_indicator


configure_app(page_title="Talent Risk & AI Predictions")
render_page_header(
    title="Talent Risk Intelligence & AI Predictions",
    subtitle="Detect attrition risks, track employee burnout pressure, and simulate predictive workforce outcomes to guide preemptive HR interventions.",
    badges=["🤖 Machine Learning Core", "🚨 Preemptive Risk Detection", "🔮 What-If Scenario Lab"],
)

df_raw, df = get_filtered_workforce()
if df.empty:
    render_empty_state()

kpis = compute_top_level_kpis(df)
risk_summary = get_risk_summary(df)

# Risk KPIs Grid (4 Balanced Columns)
st.markdown("#### 🚨 Predictive Risk Matrix")
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card(
        "High Attrition Risk",
        f"{risk_summary['high_risk_count']}",
        f"{risk_summary['high_risk_pct']}% of active cohort",
        stripe="stripe-rose",
        chip="🚨 Critical",
        chip_theme="rose",
    )
with col2:
    render_kpi_card(
        "Moderate Attrition Risk",
        f"{risk_summary['medium_risk_pct']}%",
        "Emerging attrition signals",
        stripe="stripe-amber",
        chip="⚠️ Caution",
        chip_theme="amber",
    )
with col3:
    render_kpi_card(
        "Low Risk / Stable",
        f"{risk_summary['low_risk_pct']}%",
        "Healthy retention posture",
        stripe="stripe-emerald",
        chip="✅ Retained",
        chip_theme="emerald",
    )
with col4:
    render_kpi_card(
        "Elevated Burnout",
        f"{kpis['burnout_high_count']}",
        f"{kpis['burnout_high_pct']}% experiencing chronic strain",
        stripe="stripe-rose",
        chip="🔥 Urgent",
        chip_theme="rose",
    )

st.markdown("---")

# High Risk Employee Watchlist
st.markdown("### ⚠️ High-Risk Employee Watchlist")
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
    st.info("No high-risk employee records are present in the current filter selection.")

st.markdown("---")

# Interactive What-If Simulator
st.markdown("### 🔮 Interactive What-If Scenario Simulator")
st.caption("Adjust employee parameters in real time to simulate AI attrition probability and predicted productivity tier.")

sim_card = st.container()
with sim_card:
    sim_left, sim_right = st.columns([5, 5])

    with sim_left:
        dept_options = sorted(df_raw['Department'].unique().tolist())
        s_dept = st.selectbox("Department", dept_options, index=0)
        s_hours = st.slider("Weekly Work Hours", 25.0, 70.0, 50.0, 0.5)
        s_ot = max(0.0, s_hours - 40.0)
        st.caption(f"Calculated weekly overtime: **{s_ot:.1f} hrs/wk**")
        s_rating = st.slider("Manager Performance Rating", 1.0, 5.0, 3.2, 0.1)
        s_sat = st.slider("Employee Satisfaction Score", 1.0, 10.0, 4.5, 0.5)
        s_burnout = st.selectbox("Assessed Burnout Level", ["Low", "Medium", "High"], index=2)
        s_salary = st.number_input("Monthly Compensation (INR)", min_value=25000, max_value=500000, value=95000, step=5000)

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

        risk_pct = att_res['attrition_probability_pct']
        risk_color = "var(--rose)" if risk_pct > 60 else ("var(--amber)" if risk_pct > 35 else "var(--emerald)")

        st.plotly_chart(
            create_gauge_indicator("AI Predicted Attrition Risk", risk_pct, 100.0, "%"),
            use_container_width=True
        )

        st.markdown(
            f"""
            <div class="action-card" style="border-left: 4px solid {risk_color}; margin-top: 0.5rem;">
                <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:var(--muted); margin-bottom:4px;">Productivity Classification</div>
                <div style="font-weight:800; font-size:1.1rem; color:var(--text); margin-bottom:6px;">
                    Predicted Tier: <span style="color:var(--primary);">{prod_res['predicted_tier']}</span>
                </div>
                <div style="font-size:0.86rem; color:var(--muted); line-height:1.5;">
                    <b>Executive Guidance:</b> {prod_res['strategic_guidance']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
