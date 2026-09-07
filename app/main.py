"""
AI-Driven Employee Productivity & Workforce Allocation Optimization System
Executive-grade Streamlit Dashboard for Human Resource Managers & Enterprise Leaders.
"""

import os
import sys

# Ensure both project root and app directory are in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.dirname(os.path.abspath(__file__))
for p in [BASE_DIR, APP_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

# Local engine modules
try:
    from backend import (
        load_and_clean_data,
        compute_top_level_kpis,
        compute_department_kpis,
        compute_role_kpis,
        generate_allocation_recommendations,
        filter_data
    )
    from ml_models import (
        get_attrition_model,
        get_productivity_model,
        score_batch_workforce,
        get_risk_summary
    )
    from utils import (
        get_custom_css,
        create_workforce_quadrant_chart,
        create_department_benchmark_bar,
        create_utilization_distribution_pie,
        create_hours_distribution_plot,
        create_completion_distribution_plot,
        create_seaborn_distributions,
        create_gauge_indicator
    )
except ImportError:
    from app.backend import (
        load_and_clean_data,
        compute_top_level_kpis,
        compute_department_kpis,
        compute_role_kpis,
        generate_allocation_recommendations,
        filter_data
    )
    from app.ml_models import (
        get_attrition_model,
        get_productivity_model,
        score_batch_workforce,
        get_risk_summary
    )
    from app.utils import (
        get_custom_css,
        create_workforce_quadrant_chart,
        create_department_benchmark_bar,
        create_utilization_distribution_pie,
        create_hours_distribution_plot,
        create_completion_distribution_plot,
        create_seaborn_distributions,
        create_gauge_indicator
    )

# Page configuration
st.set_page_config(
    page_title="AI Workforce Productivity & Allocation Optimizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject executive custom styling
st.markdown(get_custom_css(), unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def get_dataset():
    return load_and_clean_data()


# Ingest Data
df_raw = get_dataset()

# ---------------------------------------------------------
# Sidebar Controls & Story Guide
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚡ **Workforce Navigator**")
    st.caption("AI-powered HR intelligence platform for productivity analysis and workload balancing.")

    st.markdown("---")
    st.markdown("#### 🔍 **Filter Workforce**")

    # Search query
    search_query = st.text_input("🔎 Search by ID, Role, Dept", placeholder="e.g. EMP-1015, Tech Lead...")

    # Department filter
    all_departments = sorted(df_raw['Department'].unique().tolist())
    selected_departments = st.multiselect(
        "🏢 Department",
        options=all_departments,
        default=[]
    )

    # Role filter (dependent on dept selection)
    if selected_departments:
        available_roles = sorted(df_raw[df_raw['Department'].isin(selected_departments)]['Job_Role'].unique().tolist())
    else:
        available_roles = sorted(df_raw['Job_Role'].unique().tolist())

    selected_roles = st.multiselect(
        "💼 Job Role",
        options=available_roles,
        default=[]
    )

    # Experience Tier
    all_tiers = ['Junior (0-3 yrs)', 'Mid-Level (3-7 yrs)', 'Senior (7-12 yrs)', 'Lead / Principal (12+ yrs)']
    selected_exp_tiers = st.multiselect(
        "📈 Experience Band",
        options=all_tiers,
        default=[]
    )

    # Burnout Risk
    selected_burnout = st.multiselect(
        "🔥 Burnout Risk",
        options=['Low', 'Medium', 'High'],
        default=[]
    )

    st.markdown("---")
    st.markdown("#### 💡 **How to Use This Dashboard**")
    st.markdown("""
    1. **Scan Top KPIs** to evaluate overall delivery adherence and working hours.
    2. **Review Allocation Insights** to detect overloaded and underutilized staff.
    3. **Benchmark Departments** to reallocate project tasks across teams.
    4. **Simulate Scenarios** with the AI engine to prevent employee attrition.
    """)

    st.markdown("---")
    st.caption(f"📊 Active Filtered Cohort: **{len(df_raw):,}** total employees in DB.")

# Apply filters
df = filter_data(
    df=df_raw,
    departments=selected_departments,
    roles=selected_roles,
    experience_tier=selected_exp_tiers,
    burnout_levels=selected_burnout,
    search_query=search_query
)

# ---------------------------------------------------------
# Executive Hero Banner
# ---------------------------------------------------------
st.markdown("""
<div class="executive-header">
    <div class="header-title">⚡ AI-Driven Workforce Allocation & Productivity Optimizer</div>
    <div class="header-subtitle">
        Executive decision intelligence platform analyzing employee productivity, detecting workload imbalances,
        predicting attrition and burnout risks, and orchestrating algorithmic workforce reallocation strategies.
    </div>
    <div>
        <span class="badge-pill badge-cyan">🤖 ML Predictive Engine</span>
        <span class="badge-pill badge-emerald">⚖️ Workload Balancer</span>
        <span class="badge-pill badge-purple">🎯 SDG 8 & 9 Aligned</span>
    </div>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️ No employee records match the active filter criteria. Please reset filters in the sidebar.")
    st.stop()

# Compute Top Level KPIs
kpis = compute_top_level_kpis(df)

# =========================================================
# SECTION 1: Key Performance Indicators
# =========================================================
st.markdown("### 📊 **1. Key Performance Indicators**")
st.markdown("""
<div class="story-box">
    <b>Executive Health Check:</b> These four core metrics measure delivery throughput, working hour sustainability, leadership sentiment, and workforce availability across the organization.
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-stripe stripe-blue"></div>
        <div class="kpi-title">Avg Task Completion</div>
        <div class="kpi-value">{kpis['avg_task_completion']}%</div>
        <div class="kpi-caption">🎯 Benchmark: ≥ 80.0%</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-stripe stripe-purple"></div>
        <div class="kpi-title">Avg Weekly Work Hours</div>
        <div class="kpi-value">{kpis['avg_weekly_hours']} <span style="font-size:1.1rem;color:#64748B;">h/wk</span></div>
        <div class="kpi-caption">⏱️ Standard Baseline: 40.0 - 45.0 hrs</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-stripe stripe-emerald"></div>
        <div class="kpi-title">Avg Manager Rating</div>
        <div class="kpi-value">{kpis['avg_manager_rating']} <span style="font-size:1.1rem;color:#64748B;">/ 5.0</span></div>
        <div class="kpi-caption">⭐ Org Target: ≥ 3.8 / 5.0</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-stripe stripe-amber"></div>
        <div class="kpi-title">Avg Attendance Rate</div>
        <div class="kpi-value">{kpis['avg_attendance']}%</div>
        <div class="kpi-caption">📅 Target Adherence: ≥ 90.0%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# =========================================================
# SECTION 2: Workforce Allocation Insights
# =========================================================
st.markdown("### ⚖️ **2. Workforce Allocation Insights (Overloaded vs. Underutilized)**")
st.markdown("""
<div class="story-box story-box-amber">
    <b>Workforce Imbalance Diagnostics:</b>
    <ul style="margin: 4px 0 0 16px; padding: 0;">
        <li><b>Overloaded (🚨):</b> Working &ge;48 hrs/wk or &gt;10 hrs overtime with strained output or high burnout risk.</li>
        <li><b>Underutilized (⚡):</b> Working &lt;38 hrs/wk with high task completion (&ge;75%) and surplus bandwidth to absorb projects.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

col_alloc_summary, col_alloc_actions = st.columns([5, 5])

with col_alloc_summary:
    st.plotly_chart(create_utilization_distribution_pie(df), use_container_width=True)

    # Quick metric callout cards
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.metric(
            label="🚨 Overloaded Staff",
            value=f"{kpis['overloaded_count']}",
            delta=f"{kpis['overloaded_pct']}% of slice",
            delta_color="inverse"
        )
    with sc2:
        st.metric(
            label="⚡ Underutilized Staff",
            value=f"{kpis['underutilized_count']}",
            delta=f"{kpis['underutilized_pct']}% capacity",
            delta_color="off"
        )
    with sc3:
        st.metric(
            label="🌟 High Performers",
            value=f"{kpis['high_performers_count']}",
            delta=f"{kpis['high_performers_pct']}% stars",
            delta_color="normal"
        )

with col_alloc_actions:
    st.markdown("#### 🎯 **Priority Reallocation Strategy**")
    recommendations = generate_allocation_recommendations(df)

    if recommendations:
        for rec in recommendations[:3]:
            badge_color = "#DC2626" if rec['priority'] == 'HIGH' else "#D97706"
            st.markdown(f"""
            <div class="action-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span style="font-size:0.75rem; font-weight:700; color:{badge_color}; text-transform:uppercase;">● {rec['priority']} PRIORITY | {rec['type']}</span>
                    <span style="font-size:0.78rem; color:#64748B; font-weight:600;">{rec['department']}</span>
                </div>
                <div style="font-weight:700; font-size:0.92rem; color:#0F172A; margin-bottom:4px;">{rec['title']}</div>
                <div style="font-size:0.84rem; color:#475569; line-height:1.4; margin-bottom:6px;">{rec['description']}</div>
                <div style="font-size:0.8rem; font-weight:600; color:#0284C7;">👉 Action: {rec['action_item']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ Workforce load is evenly balanced across the selected department filters!")

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# 4-Quadrant Scatter Matrix
st.plotly_chart(create_workforce_quadrant_chart(df), use_container_width=True)

# Summarized Sample Tables (Top 5 Overloaded & Top 5 Underutilized)
st.markdown("#### 📋 **Workforce Action Lists (Top 5 Profiles Requiring Attention)**")
tab_ov, tab_un = st.tabs(["🚨 Top 5 Overloaded Employees", "⚡ Top 5 Underutilized Employees"])

with tab_ov:
    top_ov = df[df['Workforce_Status'] == 'Overloaded'][[
        'Employee_ID', 'Department', 'Job_Role', 'Weekly_Work_Hours',
        'Overtime_Hours_Weekly', 'Projects_Handled', 'Task_Completion_Pct', 'Burnout_Risk_Level'
    ]].sort_values(by='Weekly_Work_Hours', ascending=False).head(5)

    if not top_ov.empty:
        st.dataframe(
            top_ov.style.format({
                'Weekly_Work_Hours': '{:.1f}h',
                'Overtime_Hours_Weekly': '{:.1f}h',
                'Task_Completion_Pct': '{:.1f}%'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No overloaded employees in this slice.")

with tab_un:
    top_un = df[df['Workforce_Status'] == 'Underutilized'][[
        'Employee_ID', 'Department', 'Job_Role', 'Weekly_Work_Hours',
        'Projects_Handled', 'Task_Completion_Pct', 'Satisfaction_Score'
    ]].sort_values(by='Weekly_Work_Hours', ascending=True).head(5)

    if not top_un.empty:
        st.dataframe(
            top_un.style.format({
                'Weekly_Work_Hours': '{:.1f}h',
                'Task_Completion_Pct': '{:.1f}%',
                'Satisfaction_Score': '{:.1f}/10'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No underutilized employees in this slice.")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# =========================================================
# SECTION 3: Productivity by Department
# =========================================================
st.markdown("### 🏢 **3. Productivity by Department**")
st.markdown("""
<div class="story-box story-box-emerald">
    <b>Benchmarking Takeaway:</b> Identifies departments leading in task completion vs. those operating under high overtime strain. Rebalance capacity between leading and bottleneck departments.
</div>
""", unsafe_allow_html=True)

dept_df = compute_department_kpis(df)

col_dept_chart, col_dept_summary = st.columns([6, 4])

with col_dept_chart:
    st.plotly_chart(create_department_benchmark_bar(dept_df), use_container_width=True)

with col_dept_summary:
    st.markdown("#### 🏆 **Top & Bottom Performing Departments**")
    
    if len(dept_df) >= 2:
        top_dept = dept_df.iloc[0]
        bot_dept = dept_df.iloc[-1]

        st.markdown(f"""
        <div class="action-card" style="border-left: 4px solid #10B981;">
            <div style="font-size:0.75rem; font-weight:700; color:#10B981; text-transform:uppercase;">🥇 HIGHEST PRODUCTIVITY DEPT</div>
            <div style="font-weight:800; font-size:1.1rem; color:#0F172A;">{top_dept['Department']}</div>
            <div style="font-size:0.85rem; color:#475569;">
                • Task Completion: <b>{top_dept['Avg_Task_Completion_Pct']}%</b><br>
                • Avg Weekly Hours: <b>{top_dept['Avg_Weekly_Hours']}h</b><br>
                • Overload Rate: <b>{top_dept['Overloaded_Pct']}%</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="action-card" style="border-left: 4px solid #EF4444;">
            <div style="font-size:0.75rem; font-weight:700; color:#EF4444; text-transform:uppercase;">⚠️ HIGHEST WORKLOAD BOTTLENECK</div>
            <div style="font-weight:800; font-size:1.1rem; color:#0F172A;">{bot_dept['Department']}</div>
            <div style="font-size:0.85rem; color:#475569;">
                • Task Completion: <b>{bot_dept['Avg_Task_Completion_Pct']}%</b><br>
                • Avg Weekly Hours: <b>{bot_dept['Avg_Weekly_Hours']}h</b><br>
                • Overload Rate: <b>{bot_dept['Overloaded_Pct']}%</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.dataframe(dept_df, use_container_width=True)

# Collapsible full departmental scorecard
with st.expander("🔍 View Complete Department Scorecard"):
    st.dataframe(
        dept_df.style.format({
            'Avg_Task_Completion_Pct': '{:.1f}%',
            'Avg_Weekly_Hours': '{:.1f}h',
            'Avg_Manager_Rating': '{:.2f}',
            'Avg_Attendance_Pct': '{:.1f}%',
            'Avg_Productivity_Score': '{:.1f}',
            'Avg_Satisfaction': '{:.1f}/10',
            'Avg_Salary_INR': '₹{:,}',
            'Overloaded_Pct': '{:.1f}%',
            'Underutilized_Pct': '{:.1f}%',
            'Attrition_Rate_Pct': '{:.1f}%'
        }),
        use_container_width=True,
        hide_index=True
    )

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# =========================================================
# SECTION 4: Workload & Performance Distributions
# =========================================================
st.markdown("### 📈 **4. Workload & Performance Distributions**")
st.markdown("""
<div class="story-box">
    <b>Distribution Analysis:</b> Understand the variance in working hours and completion rates across staff tiers to detect systemic overwork or operational slack.
</div>
""", unsafe_allow_html=True)

dist_mode = st.radio("Distribution View:", ["Interactive Plotly Distributions", "Static Seaborn KDE Report"], horizontal=True)

if dist_mode == "Interactive Plotly Distributions":
    d1, d2 = st.columns(2)
    with d1:
        st.plotly_chart(create_hours_distribution_plot(df), use_container_width=True)
    with d2:
        st.plotly_chart(create_completion_distribution_plot(df), use_container_width=True)
else:
    fig_sns = create_seaborn_distributions(df)
    st.pyplot(fig_sns)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# =========================================================
# SECTION 5: Talent Risk & AI Predictive Engine
# =========================================================
st.markdown("### 🤖 **5. Talent Risk Overview & AI Predictive Engine**")
st.markdown("""
<div class="story-box">
    <b>AI Predictive Intelligence:</b> Machine Learning models estimate attrition likelihood and productivity tiers based on workload intensity, overtime, compensation, and manager ratings.
</div>
""", unsafe_allow_html=True)

risk_summary = get_risk_summary(df)

rk1, rk2, rk3, rk4 = st.columns(4)
with rk1:
    st.metric(label="🚨 High Attrition Risk Staff", value=f"{risk_summary['high_risk_count']}", delta=f"{risk_summary['high_risk_pct']}% of cohort", delta_color="inverse")
with rk2:
    st.metric(label="⚠️ Moderate Risk", value=f"{risk_summary['medium_risk_pct']}%", delta_color="off")
with rk3:
    st.metric(label="✅ Low Risk / Stable", value=f"{risk_summary['low_risk_pct']}%", delta_color="normal")
with rk4:
    st.metric(label="🔥 Burnout High Cohort", value=f"{kpis['burnout_high_count']}", delta=f"{kpis['burnout_high_pct']}% flagged", delta_color="inverse")

st.markdown("#### 🚨 **Top 5 High-Risk Employees Requiring Retention Check-In**")
if not risk_summary['sample_high_risk_df'].empty:
    st.dataframe(
        risk_summary['sample_high_risk_df'].style.format({
            'Weekly_Work_Hours': '{:.1f}h',
            'Overtime_Hours_Weekly': '{:.1f}h',
            'Satisfaction_Score': '{:.1f}/10',
            'AI_Attrition_Risk_Pct': '{:.1f}%'
        }),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No high-risk attrition candidates detected in current slice.")

# Interactive What-If Simulator Expander
with st.expander("🔮 Open Interactive Employee What-If Scenario Simulator"):
    st.caption("Adjust employee parameters below to simulate real-time AI attrition risk probability.")
    
    sim_c1, sim_c2 = st.columns([5, 5])
    with sim_c1:
        s_dept = st.selectbox("Department", all_departments, index=0)
        s_hours = st.slider("Weekly Work Hours", 25.0, 70.0, 52.0, 0.5)
        s_ot = max(0.0, s_hours - 40.0)
        st.caption(f"Calculated Overtime: **{s_ot:.1f} hrs/wk**")
        s_rating = st.slider("Manager Rating (1-5)", 1.0, 5.0, 3.2, 0.1)
        s_sat = st.slider("Satisfaction Score (1-10)", 1.0, 10.0, 4.5, 0.5)
        s_burnout = st.selectbox("Burnout Level", ["Low", "Medium", "High"], index=2)
        s_salary = st.number_input("Monthly Salary (INR)", min_value=25000, max_value=500000, value=95000, step=5000)

    with sim_c2:
        payload = {
            'Age': 30, 'Gender': 'Male', 'Department': s_dept, 'Education_Level': 'Bachelor',
            'Total_Experience_Years': 5.0, 'Years_at_Company': 3.0, 'Monthly_Salary_INR': s_salary,
            'Weekly_Work_Hours': s_hours, 'Overtime_Hours_Weekly': s_ot, 'Projects_Handled': 6,
            'Task_Completion_Pct': 75.0, 'Attendance_Pct': 92.0, 'Manager_Rating': s_rating,
            'Satisfaction_Score': s_sat, 'Burnout_Risk_Level': s_burnout, 'Work_From_Home_Pct': 40,
            'Training_Hours_Last_Year': 20, 'Promotion_Last_2Years': 'No'
        }

        att_model = get_attrition_model()
        prod_model = get_productivity_model()

        att_res = att_model.predict(payload)
        prod_res = prod_model.predict(payload)

        st.plotly_chart(create_gauge_indicator("Predicted Attrition Risk", att_res['attrition_probability_pct'], 100.0, "%"), use_container_width=True)
        st.markdown(f"**Predicted Productivity Tier:** `{prod_res['predicted_tier']}`")
        st.markdown(f"**Strategic HR Guidance:** {prod_res['strategic_guidance']}")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# =========================================================
# SECTION 6: Advanced Data Explorer & Power BI Export (Collapsible)
# =========================================================
st.markdown("### 📁 **6. Advanced Data Explorer & Power BI Export**")

with st.expander("📂 Click to Expand Raw Dataset & Power BI Export"):
    st.caption("Inspect filtered employee records or export datasets for Power BI dashboard integration.")
    
    scored_workforce = score_batch_workforce(df)
    
    show_cols = [
        'Employee_ID', 'Department', 'Job_Role', 'Total_Experience_Years',
        'Monthly_Salary_INR', 'Weekly_Work_Hours', 'Task_Completion_Pct',
        'Attendance_Pct', 'Manager_Rating', 'Workforce_Status',
        'AI_Attrition_Risk_Pct', 'AI_Risk_Category', 'AI_Predicted_Productivity_Tier'
    ]
    
    st.dataframe(scored_workforce[show_cols], use_container_width=True, height=350, hide_index=True)
    
    exp1, exp2 = st.columns(2)
    with exp1:
        clean_csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download Cleaned CSV Dataset",
            data=clean_csv,
            file_name="employee_productivity_clean.csv",
            mime="text/csv"
        )
    with exp2:
        powerbi_csv = scored_workforce.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Download AI-Enriched Power BI CSV",
            data=powerbi_csv,
            file_name="employee_productivity_powerbi_enriched.csv",
            mime="text/csv"
        )

# Executive Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#64748B; font-size:0.84rem; padding: 10px;">
    <b>AI-Driven Employee Productivity & Workforce Allocation Optimization System</b> • Enterprise Decision Intelligence
</div>
""", unsafe_allow_html=True)
