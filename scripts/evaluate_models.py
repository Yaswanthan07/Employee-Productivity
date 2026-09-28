import json
import os
import sys
import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    precision_recall_fscore_support,
    classification_report,
)
from sklearn.model_selection import train_test_split

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.backend import load_and_clean_data


def _safe_dict(values):
    return {k: round(float(v), 6) for k, v in values.items()}


def evaluate_attrition():
    df = load_and_clean_data()

    feature_cols_num = [
        'Age', 'Total_Experience_Years', 'Years_at_Company', 'Monthly_Salary_INR',
        'Weekly_Work_Hours', 'Overtime_Hours_Weekly', 'Projects_Handled',
        'Task_Completion_Pct', 'Attendance_Pct', 'Manager_Rating',
        'Satisfaction_Score', 'Work_From_Home_Pct', 'Training_Hours_Last_Year'
    ]
    feature_cols_cat = [
        'Department', 'Education_Level', 'Burnout_Risk_Level',
        'Promotion_Last_2Years', 'Gender'
    ]
    X = df[feature_cols_num + feature_cols_cat]
    y = (df['Attrition'] == 'Yes').astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model_bundle = joblib.load(os.path.join(ROOT, 'app', 'saved_models', 'attrition_model.joblib'))
    pipeline = model_bundle['pipeline']
    pred = pipeline.predict(X_test)
    prob = pipeline.predict_proba(X_test)[:, 1]

    metrics = {
        'accuracy': accuracy_score(y_test, pred),
        'precision': precision_score(y_test, pred, zero_division=0),
        'recall': recall_score(y_test, pred, zero_division=0),
        'f1_score': f1_score(y_test, pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, prob),
    }

    cm = confusion_matrix(y_test, pred, labels=[0, 1])
    report = classification_report(y_test, pred, target_names=['No', 'Yes'], digits=4, zero_division=0)

    return {
        'split': {
            'train_rows': len(X_train),
            'test_rows': len(X_test),
            'seed': 42,
            'test_fraction': 0.25,
            'target_label': 'Attrition == Yes (binary)'
        },
        'features': {
            'numeric': feature_cols_num,
            'categorical': feature_cols_cat,
        },
        'metrics': _safe_dict(metrics),
        'confusion_matrix': cm.tolist(),
        'classification_report': report,
    }


def evaluate_productivity():
    df = load_and_clean_data()

    def get_tier(score):
        if score >= 85.0:
            return 'High'
        elif score >= 70.0:
            return 'Moderate'
        else:
            return 'Needs Improvement'

    num_cols = [
        'Age', 'Total_Experience_Years', 'Years_at_Company', 'Weekly_Work_Hours',
        'Overtime_Hours_Weekly', 'Projects_Handled', 'Attendance_Pct',
        'Satisfaction_Score', 'Training_Hours_Last_Year', 'Work_From_Home_Pct'
    ]
    cat_cols = ['Department', 'Education_Level', 'Gender', 'Burnout_Risk_Level']
    X = df[num_cols + cat_cols]
    y = df['Productivity_Score'].apply(get_tier)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model_bundle = joblib.load(os.path.join(ROOT, 'app', 'saved_models', 'productivity_model.joblib'))
    pipeline = model_bundle['pipeline']
    pred = pipeline.predict(X_test)
    prob = pipeline.predict_proba(X_test)
    classes = list(pipeline.classes_)

    metrics = {
        'accuracy': accuracy_score(y_test, pred),
        'precision_macro': precision_score(y_test, pred, average='macro', zero_division=0),
        'recall_macro': recall_score(y_test, pred, average='macro', zero_division=0),
        'f1_macro': f1_score(y_test, pred, average='macro', zero_division=0),
        'precision_weighted': precision_score(y_test, pred, average='weighted', zero_division=0),
        'recall_weighted': recall_score(y_test, pred, average='weighted', zero_division=0),
        'f1_weighted': f1_score(y_test, pred, average='weighted', zero_division=0),
        'roc_auc_macro_ovr': roc_auc_score(y_test, prob, multi_class='ovr', average='macro'),
    }

    labels = classes
    cm = confusion_matrix(y_test, pred, labels=labels)
    report = classification_report(y_test, pred, labels=labels, digits=4, zero_division=0)
    per_class = precision_recall_fscore_support(y_test, pred, labels=labels, zero_division=0)
    per_class_dict = {}
    for cls, p, r, f, s in zip(labels, *per_class):
        per_class_dict[cls] = {
            'precision': round(float(p), 6),
            'recall': round(float(r), 6),
            'f1_score': round(float(f), 6),
            'support': int(s),
        }

    return {
        'split': {
            'train_rows': len(X_train),
            'test_rows': len(X_test),
            'seed': 42,
            'test_fraction': 0.25,
            'target_label': 'Productivity_Score tier derived as High / Moderate / Needs Improvement'
        },
        'features': {
            'numeric': num_cols,
            'categorical': cat_cols,
            'derived_target': 'Productivity_Score -> High >= 85, Moderate >= 70, else Needs Improvement'
        },
        'classes': classes,
        'metrics': _safe_dict(metrics),
        'confusion_matrix': cm.tolist(),
        'classification_report': report,
        'per_class_metrics': per_class_dict,
    }


if __name__ == '__main__':
    attr = evaluate_attrition()
    prod = evaluate_productivity()

    print('=== ATTRITION MODEL ===')
    print(json.dumps(attr, indent=2))
    print('\n=== PRODUCTIVITY MODEL ===')
    print(json.dumps(prod, indent=2))
