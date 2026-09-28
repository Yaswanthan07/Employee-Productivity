import pandas as pd

from app.backend import prepare_dataset_for_dashboard
from app.page_shared import get_active_dataset, reset_active_dataset


def test_prepare_dataset_for_dashboard_adds_derived_metrics():
    df = pd.DataFrame([
        {
            'Employee_ID': 'EMP-9001',
            'Age': 32,
            'Gender': 'Male',
            'Department': 'Technology',
            'Job_Role': 'Software Engineer',
            'Education_Level': 'Bachelor',
            'Total_Experience_Years': 5.0,
            'Years_at_Company': 3.0,
            'Monthly_Salary_INR': 90000,
            'Weekly_Work_Hours': 42.5,
            'Overtime_Hours_Weekly': 2.5,
            'Projects_Handled': 4,
            'Task_Completion_Pct': 88.0,
            'Attendance_Pct': 94.0,
            'Manager_Rating': 4.4,
            'Satisfaction_Score': 7.3,
            'Burnout_Risk_Level': 'Low',
            'Work_From_Home_Pct': 40,
            'Training_Hours_Last_Year': 18,
            'Promotion_Last_2Years': 'No',
            'Attrition': 'No',
        }
    ])

    prepared = prepare_dataset_for_dashboard(df)

    assert 'Productivity_Score' in prepared.columns
    assert 'Workload_Index' in prepared.columns
    assert 'Workforce_Status' in prepared.columns
    assert 'Experience_Tier' in prepared.columns
    assert len(prepared) == 1


def test_get_active_dataset_uses_uploaded_dataframe_when_present():
    uploaded = pd.DataFrame([
        {
            'Employee_ID': 'EMP-1001',
            'Age': 35,
            'Gender': 'Male',
            'Department': 'Technology',
            'Job_Role': 'Software Engineer',
            'Education_Level': 'Bachelor',
            'Total_Experience_Years': 5.0,
            'Years_at_Company': 3.0,
            'Monthly_Salary_INR': 90000,
            'Weekly_Work_Hours': 42.5,
            'Overtime_Hours_Weekly': 2.0,
            'Projects_Handled': 4,
            'Task_Completion_Pct': 88.0,
            'Attendance_Pct': 94.0,
            'Manager_Rating': 4.4,
            'Satisfaction_Score': 7.3,
            'Burnout_Risk_Level': 'Low',
            'Work_From_Home_Pct': 40,
            'Training_Hours_Last_Year': 18,
            'Promotion_Last_2Years': 'No',
            'Attrition': 'No',
        }
    ])

    import streamlit as st
    st.session_state.pop('uploaded_employee_df', None)
    st.session_state['uploaded_employee_df'] = uploaded

    active = get_active_dataset()
    assert len(active) == 1
    assert 'Productivity_Score' in active.columns

    reset_active_dataset()
    assert 'uploaded_employee_df' not in st.session_state
