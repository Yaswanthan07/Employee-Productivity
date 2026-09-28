import io
from typing import Any, Dict, List, Optional

import pandas as pd

from app.backend import load_and_clean_data

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

REFERENCE_COLUMNS = [
    'Employee_ID',
    'Age',
    'Gender',
    'Department',
    'Job_Role',
    'Education_Level',
    'Total_Experience_Years',
    'Years_at_Company',
    'Monthly_Salary_INR',
    'Weekly_Work_Hours',
    'Overtime_Hours_Weekly',
    'Projects_Handled',
    'Task_Completion_Pct',
    'Attendance_Pct',
    'Manager_Rating',
    'Satisfaction_Score',
    'Burnout_Risk_Level',
    'Work_From_Home_Pct',
    'Training_Hours_Last_Year',
    'Promotion_Last_2Years',
    'Attrition',
]

REQUIRED_COLUMNS = REFERENCE_COLUMNS.copy()
OPTIONAL_COLUMNS: List[str] = []
NUMERIC_COLUMNS = [
    'Age', 'Total_Experience_Years', 'Years_at_Company', 'Monthly_Salary_INR',
    'Weekly_Work_Hours', 'Overtime_Hours_Weekly', 'Projects_Handled',
    'Task_Completion_Pct', 'Attendance_Pct', 'Manager_Rating',
    'Satisfaction_Score', 'Work_From_Home_Pct', 'Training_Hours_Last_Year'
]
PERCENTAGE_COLUMNS = [
    'Task_Completion_Pct', 'Attendance_Pct', 'Work_From_Home_Pct'
]
CATEGORY_COLUMNS = [
    'Gender', 'Department', 'Job_Role', 'Education_Level',
    'Burnout_Risk_Level', 'Attrition', 'Promotion_Last_2Years'
]


def _reference_categories() -> Dict[str, List[str]]:
    ref_df = load_and_clean_data()
    categories: Dict[str, List[str]] = {}
    for col in ['Gender', 'Department', 'Job_Role', 'Education_Level', 'Burnout_Risk_Level', 'Attrition']:
        if col in ref_df.columns:
            categories[col] = sorted({str(v).strip() for v in ref_df[col].dropna().astype(str).unique() if str(v).strip()})
    # Promotion_Last_2Years is stored as Yes/No in the project dataset
    categories['Promotion_Last_2Years'] = ['No', 'Yes']
    return categories


def generate_sample_template() -> pd.DataFrame:
    ref_df = load_and_clean_data()
    categories = _reference_categories()
    department = categories['Department'][0]
    role = ref_df['Job_Role'].dropna().astype(str).unique()[0]
    gender = categories['Gender'][0]
    education = categories['Education_Level'][0]
    burnout = categories['Burnout_Risk_Level'][0]

    sample = {
        'Employee_ID': ['EMP-1001', 'EMP-1002'],
        'Age': [32, 41],
        'Gender': [gender, gender],
        'Department': [department, department],
        'Job_Role': [role, role],
        'Education_Level': [education, education],
        'Total_Experience_Years': [4.2, 9.5],
        'Years_at_Company': [2.5, 6.0],
        'Monthly_Salary_INR': [85000, 120000],
        'Weekly_Work_Hours': [42.5, 47.0],
        'Overtime_Hours_Weekly': [2.5, 7.0],
        'Projects_Handled': [4, 6],
        'Task_Completion_Pct': [88.0, 82.5],
        'Attendance_Pct': [95.0, 91.2],
        'Manager_Rating': [4.3, 3.9],
        'Satisfaction_Score': [7.2, 6.8],
        'Burnout_Risk_Level': [burnout, 'Medium'],
        'Work_From_Home_Pct': [60, 40],
        'Training_Hours_Last_Year': [18, 28],
        'Promotion_Last_2Years': ['No', 'Yes'],
        'Attrition': ['No', 'No'],
    }
    return pd.DataFrame(sample)


def _clean_string_series(series: pd.Series) -> pd.Series:
    return series.map(lambda x: x.strip() if isinstance(x, str) else x)


def _normalize_known_equivalent_label(column_name: str, value: Any) -> Any:
    if value is None or pd.isna(value):
        return value
    text = str(value).strip()
    if not text:
        return value

    normalized = text.strip().replace("  ", " ")
    if column_name == 'Education_Level':
        mapping = {
            'bachelor': 'Bachelor',
            "bachelor's": 'Bachelor',
            'bachelors': 'Bachelor',
            'master': 'Master',
            "master's": 'Master',
            'masters': 'Master',
            'phd': 'PhD',
            'ph.d': 'PhD',
            'diploma': 'Diploma',
        }
        lower = normalized.lower()
        if lower in mapping:
            return mapping[lower]
    return value


def _validate_numeric_column(series: pd.Series, column_name: str) -> tuple[pd.Series, List[str], List[str]]:
    warnings: List[str] = []
    errors: List[str] = []
    converted = pd.to_numeric(series, errors='coerce')
    invalid_mask = series.notna() & converted.isna()
    if invalid_mask.any():
        bad_values = sorted(series[invalid_mask].astype(str).unique().tolist())[:5]
        warnings.append(f"Column '{column_name}' contains non-numeric values that could not be converted: {bad_values}")

    if column_name in ['Age']:
        bad = converted[(converted <= 0) | (converted > 80)]
        if not bad.empty:
            warnings.append(f"Column '{column_name}' has out-of-range values above 80 or <= 0.")
    elif column_name in ['Total_Experience_Years', 'Years_at_Company']:
        bad = converted[(converted < 0) | (converted > 60)]
        if not bad.empty:
            warnings.append(f"Column '{column_name}' has values outside the expected range (0 to 60 years).")
    elif column_name == 'Monthly_Salary_INR':
        bad = converted[(converted <= 0) | (converted > 5000000)]
        if not bad.empty:
            warnings.append(f"Column '{column_name}' has values outside the expected range (positive and under 5,000,000 INR).")
    elif column_name in ['Weekly_Work_Hours', 'Overtime_Hours_Weekly']:
        bad = converted[(converted < 0) | (converted > 120)]
        if not bad.empty:
            warnings.append(f"Column '{column_name}' has values outside the expected range (0 to 120 hours).")
    elif column_name == 'Projects_Handled':
        bad = converted[(converted < 0) | (converted > 50)]
        if not bad.empty:
            warnings.append(f"Column '{column_name}' has values outside the expected range (0 to 50 projects).")
    elif column_name in PERCENTAGE_COLUMNS:
        bad = converted[(converted < 0) | (converted > 100)]
        if not bad.empty:
            warnings.append(f"Column '{column_name}' has percentage values outside the expected 0–100 range.")
    elif column_name == 'Manager_Rating':
        bad = converted[(converted < 0) | (converted > 5)]
        if not bad.empty:
            warnings.append(f"Column '{column_name}' should follow the project scale of 1-5 and contains out-of-range values.")
    elif column_name == 'Satisfaction_Score':
        bad = converted[(converted < 0) | (converted > 10)]
        if not bad.empty:
            warnings.append(f"Column '{column_name}' should follow the project scale of 1-10 and contains out-of-range values.")
    elif column_name in ['Work_From_Home_Pct', 'Training_Hours_Last_Year']:
        if column_name == 'Work_From_Home_Pct':
            bad = converted[(converted < 0) | (converted > 100)]
            if not bad.empty:
                warnings.append(f"Column '{column_name}' has percentage values outside the expected 0–100 range.")
        else:
            bad = converted[(converted < 0)]
            if not bad.empty:
                warnings.append(f"Column '{column_name}' has negative training hours values.")

    if 'Years_at_Company' in series.index and 'Total_Experience_Years' in series.index:
        pass

    return converted, warnings, errors


def validate_uploaded_employee_csv(uploaded_file: Optional[Any]) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        'status': 'Invalid',
        'errors': [],
        'warnings': [],
        'file_summary': {},
        'schema_summary': {},
        'data_quality_summary': {},
        'validated_df': pd.DataFrame(),
        'preview_df': pd.DataFrame(),
        'converted_columns': [],
    }

    if uploaded_file is None:
        report['errors'].append('No file was uploaded.')
        return report

    raw_data = None
    if hasattr(uploaded_file, 'getvalue'):
        try:
            raw_data = uploaded_file.getvalue()
        except Exception:
            raw_data = None
    if raw_data is None:
        try:
            raw_data = uploaded_file.read()
            uploaded_file.seek(0)
        except Exception:
            raw_data = None

    if raw_data is None or len(raw_data) == 0:
        report['errors'].append('The uploaded file is empty.')
        return report

    file_size = getattr(uploaded_file, 'size', None)
    if file_size is None:
        file_size = len(raw_data)
    try:
        file_size = int(file_size)
    except (TypeError, ValueError):
        file_size = len(raw_data)

    if file_size > MAX_FILE_SIZE_BYTES:
        report['errors'].append(f'The uploaded file exceeds the 10 MB limit ({file_size / (1024 * 1024):.1f} MB).')

    try:
        text = raw_data.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw_data.decode('latin-1')

    try:
        df = pd.read_csv(io.StringIO(text))
    except Exception as exc:  # pragma: no cover - defensive branch
        report['errors'].append(f'Unable to parse the CSV file: {exc}')
        return report

    if df.empty:
        report['errors'].append('The uploaded CSV does not contain any data rows.')
        return report

    if df.columns is None or len(df.columns) == 0:
        report['errors'].append('The uploaded CSV does not contain valid column headers.')
        return report

    column_names = [str(col) for col in df.columns]
    if any(col.strip() == '' for col in column_names):
        report['errors'].append('The uploaded CSV contains empty column names.')

    stripped_columns = []
    for col in column_names:
        stripped = col.strip()
        stripped_columns.append(stripped)
        if col != stripped:
            report['warnings'].append(f"Column header '{col}' has leading/trailing whitespace; it was normalized to '{stripped}'.")

    if len(stripped_columns) != len(set(stripped_columns)):
        duplicates = sorted({name for name in set(stripped_columns) if stripped_columns.count(name) > 1})
        report['errors'].append(f"Duplicate column names detected: {duplicates}")

    df.columns = stripped_columns

    missing_required = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    unexpected_columns = [col for col in df.columns if col not in REQUIRED_COLUMNS]

    report['schema_summary'] = {
        'required_columns_found': [col for col in REQUIRED_COLUMNS if col in df.columns],
        'missing_required_columns': missing_required,
        'optional_columns_missing': [],
        'unexpected_columns': unexpected_columns,
    }

    if missing_required:
        report['errors'].append(f"Missing required columns: {missing_required}")

    if unexpected_columns:
        report['warnings'].append(f"Unexpected columns found and kept as warnings: {unexpected_columns}")

    preview_df = df.head(10).copy()
    report['preview_df'] = preview_df

    if 'Employee_ID' in df.columns:
        duplicate_ids = df['Employee_ID'].astype(str).duplicated().sum()
        if duplicate_ids > 0:
            report['warnings'].append(f"{duplicate_ids} duplicate Employee_ID values were found.")

    duplicate_rows = int(df.duplicated().sum())
    if duplicate_rows > 0:
        report['warnings'].append(f"{duplicate_rows} duplicate rows were found.")

    missing_summary = {}
    for col in df.columns:
        non_null = df[col].notna()
        empty_values = df[col].astype(str).str.strip().eq('')
        missing_count = int((~non_null | empty_values).sum())
        if missing_count > 0:
            missing_summary[col] = {
                'missing_count': missing_count,
                'missing_pct': round((missing_count / len(df)) * 100, 2),
            }
    report['data_quality_summary'] = {
        'total_missing_values': int(df.isna().sum().sum() + (df.astype(str).apply(lambda s: s.str.strip().eq('').sum())).sum()),
        'duplicate_rows': duplicate_rows,
        'duplicate_employee_ids': int(df['Employee_ID'].astype(str).duplicated().sum()) if 'Employee_ID' in df.columns else 0,
        'missing_by_column': missing_summary,
    }

    cleaned_df = df.copy()
    converted_columns: List[str] = []
    for col in NUMERIC_COLUMNS:
        if col not in cleaned_df.columns:
            continue
        original_series = cleaned_df[col].copy()
        converted_series, numeric_warnings, numeric_errors = _validate_numeric_column(original_series, col)
        for msg in numeric_warnings:
            report['warnings'].append(msg)
        for msg in numeric_errors:
            report['errors'].append(msg)
        cleaned_df[col] = converted_series
        converted_columns.append(col)

    if 'Years_at_Company' in cleaned_df.columns and 'Total_Experience_Years' in cleaned_df.columns:
        years_bad = cleaned_df['Years_at_Company'] > cleaned_df['Total_Experience_Years']
        if years_bad.any():
            report['warnings'].append('Some employees have Years_at_Company values greater than Total_Experience_Years.')

    for col in CATEGORY_COLUMNS:
        if col not in cleaned_df.columns:
            continue
        cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
        if col in ['Promotion_Last_2Years']:
            valid_values = {'Yes', 'No', 'Y', 'N', 'True', 'False', '1', '0'}
            invalid_mask = ~cleaned_df[col].str.upper().replace({'TRUE': 'True', 'FALSE': 'False', 'YES': 'Yes', 'NO': 'No', 'Y': 'Yes', 'N': 'No', '1': 'Yes', '0': 'No'}).isin({'Yes', 'No'})
            if invalid_mask.any():
                report['warnings'].append(f"Column '{col}' has values outside the expected Yes/No labels: {sorted(cleaned_df.loc[invalid_mask, col].unique().tolist())[:5]}")
        elif col in ['Attrition']:
            valid_values = {'Yes', 'No'}
            invalid_mask = ~cleaned_df[col].str.upper().isin({'YES', 'NO'})
            if invalid_mask.any():
                report['warnings'].append(f"Column '{col}' has unexpected labels outside Yes/No: {sorted(cleaned_df.loc[invalid_mask, col].unique().tolist())[:5]}")
        else:
            ref_cats = _reference_categories().get(col, [])
            if ref_cats:
                values = cleaned_df[col].astype(str).str.strip()
                if col == 'Education_Level':
                    normalized_values = values.map(lambda v: _normalize_known_equivalent_label(col, v))
                    invalid_mask = (~normalized_values.isin(ref_cats)) & (~values.isna()) & (~values.str.strip().eq(''))
                else:
                    invalid_mask = (~values.isin(ref_cats)) & (~values.isna()) & (~values.str.strip().eq(''))
                if invalid_mask.any():
                    report['warnings'].append(f"Column '{col}' has values not present in the project reference categories: {sorted(values[invalid_mask].unique().tolist())[:10]}")

    report['converted_columns'] = converted_columns
    report['validated_df'] = cleaned_df

    file_summary = {
        'file_name': getattr(uploaded_file, 'name', 'uploaded.csv'),
        'rows': int(len(df)),
        'columns': int(len(df.columns)),
        'file_size_bytes': int(file_size),
        'validation_status': 'Pending'
    }
    report['file_summary'] = file_summary

    if report['errors']:
        report['status'] = 'Invalid'
    elif report['warnings']:
        report['status'] = 'Valid with warnings'
    else:
        report['status'] = 'Valid'

    report['file_summary']['validation_status'] = report['status']
    return report
