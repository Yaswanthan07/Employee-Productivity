"""
Backend Data & KPI Engine for Employee Productivity & Workforce Allocation Optimization.
Handles data ingestion, preprocessing, KPI calculation, workforce status classification,
and data-driven resource reallocation recommendations.
"""

from typing import Dict, List, Optional, Tuple, Any
import os
import sys
import pandas as pd
import numpy as np

# Path configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.dirname(os.path.abspath(__file__))
for p in [BASE_DIR, APP_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

DATA_PATH = os.path.join(BASE_DIR, "data", "hr_analytics_india.csv")


def generate_synthetic_data(n_samples: int = 1500, random_state: int = 42) -> pd.DataFrame:
    """
    Generates a realistic synthetic Indian Enterprise HR dataset if data is missing or incomplete.
    """
    np.random.seed(random_state)

    departments_roles = {
        'Technology': [
            'Software Engineer', 'Senior Developer', 'Data Scientist',
            'DevOps Engineer', 'QA Automation Engineer', 'Tech Lead', 'Cloud Architect'
        ],
        'Finance': [
            'Financial Analyst', 'Chartered Accountant', 'Risk Manager',
            'Payroll Specialist', 'Investment Analyst'
        ],
        'Sales': [
            'Sales Executive', 'Account Executive', 'Regional Sales Manager',
            'Business Development Associate', 'Enterprise Sales Lead'
        ],
        'Human Resources': [
            'HR Executive', 'Technical Recruiter', 'HR Business Partner',
            'Talent Development Lead', 'Compensation & Benefits Specialist'
        ],
        'Operations': [
            'Operations Associate', 'Supply Chain Analyst', 'Process Improvement Manager',
            'Logistics Coordinator', 'Operations Director'
        ],
        'Marketing': [
            'Digital Marketing Specialist', 'Content Strategist', 'Growth Marketing Manager',
            'Brand Manager', 'SEO Specialist'
        ],
        'R&D': [
            'Research Scientist', 'AI/ML Research Engineer', 'Product Designer',
            'Innovation Lead'
        ],
        'Customer Support': [
            'Customer Support Specialist', 'Technical Support Engineer',
            'Customer Success Manager', 'Support Team Lead'
        ]
    }

    dept_weights = [0.28, 0.12, 0.16, 0.08, 0.14, 0.09, 0.07, 0.06]
    departments = list(departments_roles.keys())
    records = []

    for i in range(1, n_samples + 1):
        emp_id = f"EMP-{1000 + i}"
        dept = np.random.choice(departments, p=dept_weights)
        role = np.random.choice(departments_roles[dept])
        gender = np.random.choice(['Male', 'Female', 'Other'], p=[0.57, 0.41, 0.02])
        age = int(np.clip(np.random.normal(32, 6.5), 21, 58))

        if dept in ['Technology', 'R&D']:
            edu = np.random.choice(['Bachelor', 'Master', 'PhD', 'Diploma'], p=[0.55, 0.35, 0.08, 0.02])
        elif dept == 'Finance':
            edu = np.random.choice(['Bachelor', 'Master', 'PhD', 'Diploma'], p=[0.40, 0.52, 0.03, 0.05])
        else:
            edu = np.random.choice(['Bachelor', 'Master', 'PhD', 'Diploma'], p=[0.65, 0.28, 0.02, 0.05])

        max_exp = max(0.5, age - 21)
        total_exp = round(float(np.clip(np.random.exponential(scale=5.5), 0.5, max_exp)), 1)
        years_at_company = round(float(np.clip(np.random.uniform(0.2, min(total_exp, 15.0)), 0.2, total_exp)), 1)

        base_salaries = {
            'Technology': 65000, 'Finance': 58000, 'Sales': 50000,
            'Human Resources': 45000, 'Operations': 42000, 'Marketing': 48000,
            'R&D': 72000, 'Customer Support': 35000
        }
        base_sal = base_salaries[dept]
        salary = int(base_sal + (total_exp * 14500) + np.random.normal(0, 7500))
        if any(w in role for w in ['Lead', 'Manager', 'Architect', 'Director']):
            salary = int(salary * 1.35)
        salary = max(28000, salary)

        is_overworked = np.random.rand() < 0.22
        is_slack = (not is_overworked) and (np.random.rand() < 0.16)

        if is_overworked:
            weekly_hours = round(float(np.random.uniform(49.0, 68.0)), 1)
            overtime_hours = round(float(weekly_hours - 40.0), 1)
            projects_handled = int(np.random.randint(5, 12))
            satisfaction = round(float(np.clip(np.random.normal(4.2, 1.8), 1.0, 7.5)), 1)
            burnout_risk = np.random.choice(['Medium', 'High'], p=[0.25, 0.75])
            task_completion = round(float(np.clip(np.random.normal(74.0, 14.0), 42.0, 96.0)), 1)
        elif is_slack:
            weekly_hours = round(float(np.random.uniform(28.0, 37.5)), 1)
            overtime_hours = 0.0
            projects_handled = int(np.random.randint(1, 3))
            satisfaction = round(float(np.clip(np.random.normal(7.6, 1.4), 4.0, 9.8)), 1)
            burnout_risk = 'Low'
            task_completion = round(float(np.clip(np.random.normal(83.0, 9.5), 62.0, 100.0)), 1)
        else:
            weekly_hours = round(float(np.clip(np.random.normal(42.5, 3.8), 38.0, 48.0)), 1)
            overtime_hours = round(float(max(0.0, weekly_hours - 40.0)), 1)
            projects_handled = int(np.random.randint(2, 6))
            satisfaction = round(float(np.clip(np.random.normal(6.9, 1.5), 2.5, 10.0)), 1)
            burnout_risk = np.random.choice(['Low', 'Medium', 'High'], p=[0.72, 0.22, 0.06])
            task_completion = round(float(np.clip(np.random.normal(86.5, 8.0), 55.0, 100.0)), 1)

        attendance = round(float(np.clip(np.random.normal(92.8, 4.8) - (1.2 if burnout_risk == 'High' else 0), 72.0, 99.8)), 1)
        rating_calc = (task_completion / 100.0 * 3.0) + (attendance / 100.0 * 1.5) + np.random.normal(0, 0.3)
        manager_rating = round(float(np.clip(rating_calc, 1.0, 5.0)), 1)

        wfh_pct = int(np.random.choice([0, 20, 40, 50, 60, 80, 100], p=[0.15, 0.10, 0.15, 0.20, 0.20, 0.10, 0.10]))
        training_hours = int(np.clip(np.random.normal(24, 12), 4, 64))

        promotion_prob = 0.10 if years_at_company < 2 else (0.28 if manager_rating >= 4.0 else 0.08)
        promotion = 'Yes' if np.random.rand() < promotion_prob else 'No'

        attrition_prob = 0.05
        if burnout_risk == 'High':
            attrition_prob += 0.28
        if satisfaction < 4.5:
            attrition_prob += 0.22
        if overtime_hours > 10:
            attrition_prob += 0.18
        if promotion == 'No' and years_at_company > 3:
            attrition_prob += 0.10
        if manager_rating < 2.5:
            attrition_prob += 0.15
        if salary < base_sal * 1.1 and total_exp > 4:
            attrition_prob += 0.12

        attrition_prob = float(np.clip(attrition_prob, 0.02, 0.88))
        attrition = 'Yes' if np.random.rand() < attrition_prob else 'No'

        records.append({
            'Employee_ID': emp_id,
            'Age': age,
            'Gender': gender,
            'Department': dept,
            'Job_Role': role,
            'Education_Level': edu,
            'Total_Experience_Years': total_exp,
            'Years_at_Company': years_at_company,
            'Monthly_Salary_INR': salary,
            'Weekly_Work_Hours': weekly_hours,
            'Overtime_Hours_Weekly': overtime_hours,
            'Projects_Handled': projects_handled,
            'Task_Completion_Pct': task_completion,
            'Attendance_Pct': attendance,
            'Manager_Rating': manager_rating,
            'Satisfaction_Score': satisfaction,
            'Burnout_Risk_Level': burnout_risk,
            'Work_From_Home_Pct': wfh_pct,
            'Training_Hours_Last_Year': training_hours,
            'Promotion_Last_2Years': promotion,
            'Attrition': attrition
        })

    return pd.DataFrame(records)


def load_and_clean_data(file_path: Optional[str] = None) -> pd.DataFrame:
    """
    Loads HR dataset, cleans columns, handles nulls, and derives core workforce KPIs.
    Guarantees at least 1500 records by generating synthetic data if CSV is minimal.
    """
    target_path = file_path or DATA_PATH

    if os.path.exists(target_path):
        try:
            df = pd.read_csv(target_path)
            if len(df) < 200:
                df = generate_synthetic_data(1500)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                df.to_csv(target_path, index=False)
        except Exception:
            df = generate_synthetic_data(1500)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            df.to_csv(target_path, index=False)
    else:
        df = generate_synthetic_data(1500)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        df.to_csv(target_path, index=False)

    return prepare_dataset_for_dashboard(df)


def prepare_dataset_for_dashboard(df: Optional[pd.DataFrame]) -> pd.DataFrame:
    """Normalizes and enriches any employee dataset so all dashboard pages operate on the same schema."""
    if df is None:
        return pd.DataFrame()

    work_df = df.copy()
    if work_df.empty:
        return work_df

    work_df.columns = [str(col).strip() for col in work_df.columns]

    required_cols = [
        'Employee_ID', 'Age', 'Gender', 'Department', 'Job_Role', 'Education_Level',
        'Total_Experience_Years', 'Years_at_Company', 'Monthly_Salary_INR',
        'Weekly_Work_Hours', 'Overtime_Hours_Weekly', 'Projects_Handled',
        'Task_Completion_Pct', 'Attendance_Pct', 'Manager_Rating', 'Satisfaction_Score',
        'Burnout_Risk_Level', 'Work_From_Home_Pct', 'Training_Hours_Last_Year',
        'Promotion_Last_2Years', 'Attrition'
    ]

    for col in required_cols:
        if col not in work_df.columns:
            work_df[col] = pd.NA

    numeric_cols = [
        'Age', 'Total_Experience_Years', 'Years_at_Company', 'Monthly_Salary_INR',
        'Weekly_Work_Hours', 'Overtime_Hours_Weekly', 'Projects_Handled',
        'Task_Completion_Pct', 'Attendance_Pct', 'Manager_Rating',
        'Satisfaction_Score', 'Work_From_Home_Pct', 'Training_Hours_Last_Year'
    ]
    for col in numeric_cols:
        if col in work_df.columns:
            work_df[col] = pd.to_numeric(work_df[col], errors='coerce')
            if not work_df[col].dropna().empty:
                work_df[col] = work_df[col].fillna(work_df[col].median())
            else:
                work_df[col] = work_df[col].fillna(0)

    cat_cols = ['Department', 'Job_Role', 'Education_Level', 'Gender', 'Burnout_Risk_Level', 'Promotion_Last_2Years', 'Attrition']
    for col in cat_cols:
        if col in work_df.columns:
            work_df[col] = work_df[col].fillna('Unknown').astype(str).str.strip()

    work_df['Productivity_Score'] = (
        (work_df['Task_Completion_Pct'] * 0.45) +
        ((work_df['Manager_Rating'] / 5.0 * 100.0) * 0.35) +
        (work_df['Attendance_Pct'] * 0.20)
    ).round(1)

    work_df['Workload_Index'] = (
        (work_df['Weekly_Work_Hours'] / 40.0 * 0.45) +
        (work_df['Projects_Handled'] / 4.0 * 0.30) +
        (work_df['Overtime_Hours_Weekly'] / 5.0 * 0.25)
    ).round(2)

    def classify_status(row):
        is_overloaded = (row['Weekly_Work_Hours'] >= 48.0) or (row['Overtime_Hours_Weekly'] >= 10.0) or (row['Weekly_Work_Hours'] > 44.0 and row['Task_Completion_Pct'] < 75.0)
        is_underutilized = (row['Weekly_Work_Hours'] < 38.0) and (row['Projects_Handled'] <= 2) and (row['Task_Completion_Pct'] >= 75.0)
        is_star = (row['Productivity_Score'] >= 85.0) and (row['Manager_Rating'] >= 4.2) and (row['Weekly_Work_Hours'] <= 46.0)

        if is_overloaded:
            return 'Overloaded'
        elif is_underutilized:
            return 'Underutilized'
        elif is_star:
            return 'High Performer'
        return 'Optimal / Balanced'

    work_df['Workforce_Status'] = work_df.apply(classify_status, axis=1)

    def get_exp_tier(exp):
        if pd.isna(exp):
            return 'Junior (0-3 yrs)'
        if exp < 3.0:
            return 'Junior (0-3 yrs)'
        if exp < 7.0:
            return 'Mid-Level (3-7 yrs)'
        if exp < 12.0:
            return 'Senior (7-12 yrs)'
        return 'Lead / Principal (12+ yrs)'

    work_df['Experience_Tier'] = work_df['Total_Experience_Years'].apply(get_exp_tier)

    return work_df


def compute_top_level_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes summary executive KPIs across the active workforce slice.
    """
    if df.empty:
        return {
            'total_employees': 0, 'avg_task_completion': 0.0,
            'avg_weekly_hours': 0.0, 'avg_manager_rating': 0.0,
            'avg_attendance': 0.0, 'avg_satisfaction': 0.0,
            'avg_productivity_score': 0.0, 'attrition_rate': 0.0,
            'overloaded_count': 0, 'overloaded_pct': 0.0,
            'underutilized_count': 0, 'underutilized_pct': 0.0,
            'high_performers_count': 0, 'high_performers_pct': 0.0,
            'burnout_high_count': 0, 'burnout_high_pct': 0.0
        }

    total = len(df)
    overloaded = (df['Workforce_Status'] == 'Overloaded').sum()
    underutilized = (df['Workforce_Status'] == 'Underutilized').sum()
    high_perf = (df['Workforce_Status'] == 'High Performer').sum()
    burnout_high = (df['Burnout_Risk_Level'] == 'High').sum()
    attrited = (df['Attrition'] == 'Yes').sum()

    return {
        'total_employees': total,
        'avg_task_completion': round(float(df['Task_Completion_Pct'].mean()), 1),
        'avg_weekly_hours': round(float(df['Weekly_Work_Hours'].mean()), 1),
        'avg_manager_rating': round(float(df['Manager_Rating'].mean()), 2),
        'avg_attendance': round(float(df['Attendance_Pct'].mean()), 1),
        'avg_satisfaction': round(float(df['Satisfaction_Score'].mean()), 1),
        'avg_productivity_score': round(float(df['Productivity_Score'].mean()), 1),
        'attrition_rate': round(float((attrited / total) * 100.0), 1),
        'overloaded_count': int(overloaded),
        'overloaded_pct': round(float((overloaded / total) * 100.0), 1),
        'underutilized_count': int(underutilized),
        'underutilized_pct': round(float((underutilized / total) * 100.0), 1),
        'high_performers_count': int(high_perf),
        'high_performers_pct': round(float((high_perf / total) * 100.0), 1),
        'burnout_high_count': int(burnout_high),
        'burnout_high_pct': round(float((burnout_high / total) * 100.0), 1)
    }


def compute_department_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes department-level benchmarking metrics.
    """
    if df.empty:
        return pd.DataFrame()

    records = []
    for dept, group in df.groupby('Department'):
        total = len(group)
        overloaded = (group['Workforce_Status'] == 'Overloaded').sum()
        underutilized = (group['Workforce_Status'] == 'Underutilized').sum()
        attrition_count = (group['Attrition'] == 'Yes').sum()

        records.append({
            'Department': dept,
            'Headcount': total,
            'Avg_Task_Completion_Pct': round(group['Task_Completion_Pct'].mean(), 1),
            'Avg_Weekly_Hours': round(group['Weekly_Work_Hours'].mean(), 1),
            'Avg_Manager_Rating': round(group['Manager_Rating'].mean(), 2),
            'Avg_Attendance_Pct': round(group['Attendance_Pct'].mean(), 1),
            'Avg_Productivity_Score': round(group['Productivity_Score'].mean(), 1),
            'Avg_Satisfaction': round(group['Satisfaction_Score'].mean(), 1),
            'Avg_Salary_INR': int(group['Monthly_Salary_INR'].mean()),
            'Overloaded_Count': int(overloaded),
            'Overloaded_Pct': round((overloaded / total) * 100.0, 1),
            'Underutilized_Count': int(underutilized),
            'Underutilized_Pct': round((underutilized / total) * 100.0, 1),
            'Attrition_Rate_Pct': round((attrition_count / total) * 100.0, 1)
        })

    result = pd.DataFrame(records).sort_values(by='Avg_Productivity_Score', ascending=False)
    return result


def compute_role_kpis(df: pd.DataFrame, department: Optional[str] = None) -> pd.DataFrame:
    """
    Computes job role-level metrics, optionally filtered by a specific department.
    """
    sub_df = df if department is None or department == "All" else df[df['Department'] == department]
    if sub_df.empty:
        return pd.DataFrame()

    records = []
    for (dept, role), group in sub_df.groupby(['Department', 'Job_Role']):
        total = len(group)
        overloaded = (group['Workforce_Status'] == 'Overloaded').sum()
        underutilized = (group['Workforce_Status'] == 'Underutilized').sum()

        records.append({
            'Department': dept,
            'Job_Role': role,
            'Headcount': total,
            'Avg_Task_Completion': round(group['Task_Completion_Pct'].mean(), 1),
            'Avg_Weekly_Hours': round(group['Weekly_Work_Hours'].mean(), 1),
            'Avg_Manager_Rating': round(group['Manager_Rating'].mean(), 2),
            'Avg_Productivity_Score': round(group['Productivity_Score'].mean(), 1),
            'Overloaded_Pct': round((overloaded / total) * 100.0, 1),
            'Underutilized_Pct': round((underutilized / total) * 100.0, 1),
            'Avg_Salary_INR': int(group['Monthly_Salary_INR'].mean())
        })

    return pd.DataFrame(records).sort_values(by='Avg_Productivity_Score', ascending=False)


def generate_allocation_recommendations(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Generates algorithmic workforce allocation and rebalancing strategies based on
    cross-department load variance and individual utilization patterns.
    """
    if df.empty:
        return []

    dept_stats = compute_department_kpis(df)
    recommendations = []

    # Strategy 1: Identify heavily overloaded departments
    overloaded_depts = dept_stats[dept_stats['Overloaded_Pct'] >= 20.0]
    underutilized_depts = dept_stats[dept_stats['Underutilized_Pct'] >= 15.0]

    for _, ov_row in overloaded_depts.iterrows():
        dept_name = ov_row['Department']
        ov_count = ov_row['Overloaded_Count']
        ov_pct = ov_row['Overloaded_Pct']

        matching_surplus = underutilized_depts[underutilized_depts['Department'] != dept_name]
        partner_dept = matching_surplus.iloc[0]['Department'] if not matching_surplus.empty else "Operations Pool"

        recommendations.append({
            'type': 'Workload Balancing',
            'priority': 'HIGH' if ov_pct > 25.0 else 'MEDIUM',
            'title': f"Shift Project Modules from {dept_name}",
            'department': dept_name,
            'description': (
                f"{dept_name} has {ov_count} employees ({ov_pct}%) classified as Overloaded "
                f"(avg {ov_row['Avg_Weekly_Hours']} hrs/wk). Offload secondary support tasks to {partner_dept} "
                f"and enforce overtime caps."
            ),
            'action_item': f"Reassign ~{max(2, int(ov_count * 0.4))} project deliverables to {partner_dept} or contractor support."
        })

    # Strategy 2: Upskilling & Capacity Uplift for Underutilized Cohorts
    for _, un_row in underutilized_depts.iterrows():
        dept_name = un_row['Department']
        un_count = un_row['Underutilized_Count']
        un_pct = un_row['Underutilized_Pct']

        recommendations.append({
            'type': 'Capacity Utilization',
            'priority': 'MEDIUM',
            'title': f"Upskill & Absorb Workload in {dept_name}",
            'department': dept_name,
            'description': (
                f"{dept_name} has a {un_pct}% underutilization rate (avg {un_row['Avg_Weekly_Hours']} hrs/wk). "
                f"Staff show strong task completion ({un_row['Avg_Task_Completion_Pct']}%) with available bandwidth."
            ),
            'action_item': f"Enroll {un_count} team members into cross-functional technical workflows to absorb excess corporate projects."
        })

    # Strategy 3: Burnout & Attrition Risk Intervention
    high_burnout_dept = dept_stats[dept_stats['Attrition_Rate_Pct'] > 18.0]
    for _, ab_row in high_burnout_dept.iterrows():
        dept_name = ab_row['Department']
        recommendations.append({
            'type': 'Retention & Wellness',
            'priority': 'HIGH',
            'title': f"Proactive Retention Check-In for {dept_name}",
            'department': dept_name,
            'description': (
                f"Attrition in {dept_name} is at {ab_row['Attrition_Rate_Pct']}%, with satisfaction averaging {ab_row['Avg_Satisfaction']}/10. "
            ),
            'action_item': "Initiate 1-on-1 manager check-ins, mandate wellness recovery days, and conduct compensation benchmarking."
        })

    return recommendations


def filter_data(
    df: pd.DataFrame,
    departments: Optional[List[str]] = None,
    roles: Optional[List[str]] = None,
    experience_tier: Optional[List[str]] = None,
    genders: Optional[List[str]] = None,
    workforce_statuses: Optional[List[str]] = None,
    burnout_levels: Optional[List[str]] = None,
    search_query: Optional[str] = None
) -> pd.DataFrame:
    """
    Applies multi-attribute slicing and filtering to dataset.
    """
    filtered = df.copy()

    if departments and "All" not in departments and len(departments) > 0:
        filtered = filtered[filtered['Department'].isin(departments)]

    if roles and "All" not in roles and len(roles) > 0:
        filtered = filtered[filtered['Job_Role'].isin(roles)]

    if experience_tier and "All" not in experience_tier and len(experience_tier) > 0:
        filtered = filtered[filtered['Experience_Tier'].isin(experience_tier)]

    if genders and "All" not in genders and len(genders) > 0:
        filtered = filtered[filtered['Gender'].isin(genders)]

    if workforce_statuses and "All" not in workforce_statuses and len(workforce_statuses) > 0:
        filtered = filtered[filtered['Workforce_Status'].isin(workforce_statuses)]

    if burnout_levels and "All" not in burnout_levels and len(burnout_levels) > 0:
        filtered = filtered[filtered['Burnout_Risk_Level'].isin(burnout_levels)]

    if search_query:
        q = search_query.strip().lower()
        filtered = filtered[
            filtered['Employee_ID'].str.lower().str.contains(q, na=False) |
            filtered['Job_Role'].str.lower().str.contains(q, na=False) |
            filtered['Department'].str.lower().str.contains(q, na=False)
        ]

    return filtered
