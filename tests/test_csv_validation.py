import io

from fastapi.testclient import TestClient

from api.server import app
from app.csv_validation import validate_uploaded_employee_csv


def _csv_bytes(data: str) -> io.BytesIO:
    return io.BytesIO(data.encode('utf-8'))


def test_valid_csv_passes_validation():
    payload = '''Employee_ID,Age,Gender,Department,Job_Role,Education_Level,Total_Experience_Years,Years_at_Company,Monthly_Salary_INR,Weekly_Work_Hours,Overtime_Hours_Weekly,Projects_Handled,Task_Completion_Pct,Attendance_Pct,Manager_Rating,Satisfaction_Score,Burnout_Risk_Level,Work_From_Home_Pct,Training_Hours_Last_Year,Promotion_Last_2Years,Attrition
EMP-1001,35,Male,Technology,Software Engineer,Bachelor,5.0,3.0,90000,42.5,2.0,4,88.0,94.0,4.4,7.3,Low,40,18,No,No
EMP-1002,29,Female,Finance,Financial Analyst,Master,3.0,2.0,78000,41.0,1.0,3,80.0,92.0,4.1,6.8,Medium,35,12,Yes,No
'''
    result = validate_uploaded_employee_csv(_csv_bytes(payload))
    assert result['status'] in {'Valid', 'Valid with warnings'}
    assert result['errors'] == []


def test_missing_required_columns_is_flagged():
    payload = '''Employee_ID,Age,Gender,Department,Job_Role
EMP-1001,35,Male,Technology,Software Engineer
'''
    result = validate_uploaded_employee_csv(_csv_bytes(payload))
    assert result['status'] == 'Invalid'
    assert any('Missing required columns' in e for e in result['errors'])


def test_invalid_numeric_values_are_reported():
    payload = '''Employee_ID,Age,Gender,Department,Job_Role,Education_Level,Total_Experience_Years,Years_at_Company,Monthly_Salary_INR,Weekly_Work_Hours,Overtime_Hours_Weekly,Projects_Handled,Task_Completion_Pct,Attendance_Pct,Manager_Rating,Satisfaction_Score,Burnout_Risk_Level,Work_From_Home_Pct,Training_Hours_Last_Year,Promotion_Last_2Years,Attrition
EMP-1001,abc,Male,Technology,Software Engineer,Bachelor,5.0,3.0,90000,42.5,2.0,4,88.0,94.0,4.4,7.3,Low,40,18,No,No
'''
    result = validate_uploaded_employee_csv(_csv_bytes(payload))
    assert any('non-numeric values' in w.lower() for w in result['warnings'])


def test_duplicate_employee_ids_are_warnings():
    payload = '''Employee_ID,Age,Gender,Department,Job_Role,Education_Level,Total_Experience_Years,Years_at_Company,Monthly_Salary_INR,Weekly_Work_Hours,Overtime_Hours_Weekly,Projects_Handled,Task_Completion_Pct,Attendance_Pct,Manager_Rating,Satisfaction_Score,Burnout_Risk_Level,Work_From_Home_Pct,Training_Hours_Last_Year,Promotion_Last_2Years,Attrition
EMP-1001,35,Male,Technology,Software Engineer,Bachelor,5.0,3.0,90000,42.5,2.0,4,88.0,94.0,4.4,7.3,Low,40,18,No,No
EMP-1001,29,Female,Finance,Financial Analyst,Master,3.0,2.0,78000,41.0,1.0,3,80.0,92.0,4.1,6.8,Medium,35,12,Yes,No
'''
    result = validate_uploaded_employee_csv(_csv_bytes(payload))
    assert any('duplicate employee_id' in w.lower() for w in result['warnings'])


def test_equivalent_education_labels_and_new_roles_are_warning_only():
    payload = '''Employee_ID,Age,Gender,Department,Job_Role,Education_Level,Total_Experience_Years,Years_at_Company,Monthly_Salary_INR,Weekly_Work_Hours,Overtime_Hours_Weekly,Projects_Handled,Task_Completion_Pct,Attendance_Pct,Manager_Rating,Satisfaction_Score,Burnout_Risk_Level,Work_From_Home_Pct,Training_Hours_Last_Year,Promotion_Last_2Years,Attrition
EMP-1001,35,Male,Finance,Accountant,Bachelor's,5.0,3.0,90000,42.5,2.0,4,88.0,94.0,4.4,7.3,Low,40,18,No,No
EMP-1002,29,Female,Technology,Data Analyst,Master's,3.0,2.0,78000,41.0,1.0,3,80.0,92.0,4.1,6.8,Medium,35,12,Yes,No
EMP-1003,31,Male,Technology,QA Engineer,Bachelor,4.0,2.5,92000,43.0,1.0,4,87.0,95.0,4.3,7.5,Low,38,20,No,No
'''
    result = validate_uploaded_employee_csv(_csv_bytes(payload))
    assert result['status'] == 'Valid with warnings'
    assert result['errors'] == []
    warnings_text = '\n'.join(result['warnings'])
    assert 'Accountant' in warnings_text or 'Data Analyst' in warnings_text or 'QA Engineer' in warnings_text
    assert 'Bachelor\'s' not in warnings_text and "Master's" not in warnings_text


def test_upload_validate_endpoint_accepts_valid_csv():
    client = TestClient(app)
    payload = '''Employee_ID,Age,Gender,Department,Job_Role,Education_Level,Total_Experience_Years,Years_at_Company,Monthly_Salary_INR,Weekly_Work_Hours,Overtime_Hours_Weekly,Projects_Handled,Task_Completion_Pct,Attendance_Pct,Manager_Rating,Satisfaction_Score,Burnout_Risk_Level,Work_From_Home_Pct,Training_Hours_Last_Year,Promotion_Last_2Years,Attrition
EMP-1001,35,Male,Technology,Software Engineer,Bachelor,5.0,3.0,90000,42.5,2.0,4,88.0,94.0,4.4,7.3,Low,40,18,No,No
EMP-1002,29,Female,Finance,Financial Analyst,Master,3.0,2.0,78000,41.0,1.0,3,80.0,92.0,4.1,6.8,Medium,35,12,Yes,No
'''
    response = client.post(
        "/upload/validate",
        files={"file": ("employees.csv", payload.encode("utf-8"), "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["file_name"] == "employees.csv"
    assert body["row_count"] == 2
    assert body["column_count"] == 21


def test_upload_validate_endpoint_rejects_missing_columns():
    client = TestClient(app)
    payload = '''Employee_ID,Age,Gender,Department,Job_Role
EMP-1001,35,Male,Technology,Software Engineer
'''
    response = client.post(
        "/upload/validate",
        files={"file": ("bad.csv", payload.encode("utf-8"), "text/csv")},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert "missing required columns" in body["message"].lower()
