"""
Data generation script for the HR Analytics Dataset (India).
Generates a realistic, comprehensive dataset modeling Indian corporate enterprises
with complete metrics for employee productivity, attendance, workload, burnout risk, and attrition.
"""

import numpy as np
import pandas as pd
import os

def generate_hr_dataset(n_samples: int = 1500, random_state: int = 42) -> pd.DataFrame:
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
        
        # Demographics
        gender = np.random.choice(['Male', 'Female', 'Other'], p=[0.58, 0.40, 0.02])
        age = int(np.clip(np.random.normal(32, 6.5), 21, 58))
        
        # Education
        if dept in ['Technology', 'R&D']:
            edu = np.random.choice(['Bachelor', 'Master', 'PhD', 'Diploma'], p=[0.55, 0.35, 0.08, 0.02])
        elif dept == 'Finance':
            edu = np.random.choice(['Bachelor', 'Master', 'PhD', 'Diploma'], p=[0.40, 0.52, 0.03, 0.05])
        else:
            edu = np.random.choice(['Bachelor', 'Master', 'PhD', 'Diploma'], p=[0.65, 0.28, 0.02, 0.05])
            
        # Experience
        max_exp = max(0, age - 21)
        total_exp = round(float(np.clip(np.random.exponential(scale=5.5), 0.5, max_exp)), 1)
        years_at_company = round(float(np.clip(np.random.uniform(0.2, min(total_exp, 15.0)), 0.2, total_exp)), 1)
        
        # Base salary (INR per month) based on role, dept, experience
        base_factor = {
            'Technology': 65000, 'Finance': 58000, 'Sales': 50000,
            'Human Resources': 45000, 'Operations': 42000, 'Marketing': 48000,
            'R&D': 72000, 'Customer Support': 35000
        }[dept]
        
        salary = int(base_factor + (total_exp * 14500) + np.random.normal(0, 8000))
        if 'Lead' in role or 'Manager' in role or 'Architect' in role or 'Director' in role:
            salary = int(salary * 1.35)
        salary = max(28000, salary)
        
        # Work patterns
        # Some employees work high hours, creating overload
        is_overworked_profile = np.random.rand() < 0.22
        is_slack_profile = (not is_overworked_profile) and (np.random.rand() < 0.16)
        
        if is_overworked_profile:
            weekly_hours = round(float(np.random.uniform(49.0, 68.0)), 1)
            overtime_hours = round(float(weekly_hours - 40.0), 1)
            projects_handled = int(np.random.randint(5, 12))
            satisfaction = round(float(np.clip(np.random.normal(4.2, 1.8), 1.0, 7.5)), 1)
            burnout_score = np.random.choice(['Medium', 'High'], p=[0.25, 0.75])
            task_completion = round(float(np.clip(np.random.normal(74.0, 14.0), 42.0, 96.0)), 1)
        elif is_slack_profile:
            weekly_hours = round(float(np.random.uniform(28.0, 37.5)), 1)
            overtime_hours = 0.0
            projects_handled = int(np.random.randint(1, 3))
            satisfaction = round(float(np.clip(np.random.normal(7.5, 1.5), 4.0, 9.8)), 1)
            burnout_score = 'Low'
            task_completion = round(float(np.clip(np.random.normal(82.0, 10.0), 60.0, 100.0)), 1)
        else:
            weekly_hours = round(float(np.clip(np.random.normal(42.5, 4.0), 38.0, 48.0)), 1)
            overtime_hours = round(float(max(0.0, weekly_hours - 40.0)), 1)
            projects_handled = int(np.random.randint(2, 6))
            satisfaction = round(float(np.clip(np.random.normal(6.8, 1.6), 2.5, 10.0)), 1)
            burnout_score = np.random.choice(['Low', 'Medium', 'High'], p=[0.70, 0.24, 0.06])
            task_completion = round(float(np.clip(np.random.normal(86.0, 8.5), 55.0, 100.0)), 1)
            
        # Attendance %
        attendance = round(float(np.clip(np.random.normal(92.5, 5.0) - (0.5 if burnout_score == 'High' else 0), 72.0, 99.8)), 1)
        
        # Manager Rating (1.0 to 5.0)
        # correlated with task completion, attendance, and slight manager bias
        rating_calc = (task_completion / 100.0 * 3.0) + (attendance / 100.0 * 1.5) + np.random.normal(0, 0.35)
        manager_rating = round(float(np.clip(rating_calc, 1.0, 5.0)), 1)
        
        # Work from home %
        wfh_pct = int(np.random.choice([0, 20, 40, 50, 60, 80, 100], p=[0.15, 0.10, 0.15, 0.20, 0.20, 0.10, 0.10]))
        
        # Training hours
        training_hours = int(np.clip(np.random.normal(24, 12), 4, 64))
        
        # Promotion in last 2 years
        promotion_prob = 0.12 if years_at_company < 2 else (0.28 if manager_rating >= 4.0 else 0.08)
        promotion = 'Yes' if np.random.rand() < promotion_prob else 'No'
        
        # Attrition logic (Higher when: burnout High, satisfaction low, overtime high, no promotion, low rating)
        attrition_prob = 0.05
        if burnout_score == 'High':
            attrition_prob += 0.28
        if satisfaction < 4.5:
            attrition_prob += 0.22
        if overtime_hours > 10:
            attrition_prob += 0.18
        if promotion == 'No' and years_at_company > 3:
            attrition_prob += 0.10
        if manager_rating < 2.5:
            attrition_prob += 0.15
        if salary < base_factor * 1.1 and total_exp > 4:
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
            'Burnout_Risk_Level': burnout_score,
            'Work_From_Home_Pct': wfh_pct,
            'Training_Hours_Last_Year': training_hours,
            'Promotion_Last_2Years': promotion,
            'Attrition': attrition
        })
        
    df = pd.DataFrame(records)
    return df

if __name__ == '__main__':
    output_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, 'hr_analytics_india.csv')
    df = generate_hr_dataset(1500)
    df.to_csv(csv_path, index=False)
    print(f"Generated {len(df)} records at: {csv_path}")
