"""
Machine Learning Layer for Employee Productivity & Workforce Allocation Optimization.
Provides:
1. Attrition Risk Predictor (Classification Pipeline + Explainability)
2. Productivity & Performance Tier Classifier
3. Workforce Reallocation Matching Algorithm
4. Risk Summary Generator for Executive HR Dashboards
"""

from typing import Dict, List, Tuple, Any, Optional
import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

# Ensure both project root and app directory are in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.dirname(os.path.abspath(__file__))
for p in [BASE_DIR, APP_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from backend import load_and_clean_data
except ImportError:
    from app.backend import load_and_clean_data

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_models")
os.makedirs(MODEL_DIR, exist_ok=True)

ATTRITION_MODEL_FILE = os.path.join(MODEL_DIR, "attrition_model.joblib")
PRODUCTIVITY_MODEL_FILE = os.path.join(MODEL_DIR, "productivity_model.joblib")


class AttritionRiskModel:
    """
    Predicts employee attrition risk probability and extracts top risk drivers.
    """
    def __init__(self):
        self.pipeline: Optional[Pipeline] = None
        self.metrics: Dict[str, Any] = {}
        self.feature_names: List[str] = []
        self.feature_importances: Dict[str, float] = {}

    def train(self, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        if df is None:
            df = load_and_clean_data()

        target_col = 'Attrition'
        y = (df[target_col] == 'Yes').astype(int)

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

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), feature_cols_num),
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), feature_cols_cat)
            ]
        )

        clf = RandomForestClassifier(
            n_estimators=120,
            max_depth=8,
            min_samples_split=5,
            class_weight='balanced',
            random_state=42
        )

        self.pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', clf)
        ])

        self.pipeline.fit(X_train, y_train)

        # Evaluation
        y_pred = self.pipeline.predict(X_test)
        y_prob = self.pipeline.predict_proba(X_test)[:, 1]

        self.metrics = {
            'accuracy': round(accuracy_score(y_test, y_pred) * 100, 2),
            'precision': round(precision_score(y_test, y_pred, zero_division=0) * 100, 2),
            'recall': round(recall_score(y_test, y_pred, zero_division=0) * 100, 2),
            'f1_score': round(f1_score(y_test, y_pred, zero_division=0) * 100, 2),
            'roc_auc': round(roc_auc_score(y_test, y_prob) * 100, 2),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'test_sample_count': len(y_test)
        }

        # Extract Feature Importances
        cat_encoder = self.pipeline.named_steps['preprocessor'].named_transformers_['cat']
        cat_features = cat_encoder.get_feature_names_out(feature_cols_cat)
        all_features = feature_cols_num + list(cat_features)
        importances = self.pipeline.named_steps['classifier'].feature_importances_

        feat_imp = dict(sorted(zip(all_features, importances), key=lambda x: x[1], reverse=True)[:10])
        self.feature_importances = {k: round(float(v) * 100, 2) for k, v in feat_imp.items()}

        # Save model
        try:
            joblib.dump({
                'pipeline': self.pipeline,
                'metrics': self.metrics,
                'feature_importances': self.feature_importances
            }, ATTRITION_MODEL_FILE)
        except Exception:
            pass

        return self.metrics

    def load(self) -> bool:
        if os.path.exists(ATTRITION_MODEL_FILE):
            try:
                data = joblib.load(ATTRITION_MODEL_FILE)
                self.pipeline = data['pipeline']
                self.metrics = data['metrics']
                self.feature_importances = data['feature_importances']
                return True
            except Exception:
                return False
        return False

    def predict(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        if self.pipeline is None:
            if not self.load():
                self.train()

        input_df = pd.DataFrame([input_dict])
        prob = float(self.pipeline.predict_proba(input_df)[0, 1])
        prediction = int(prob >= 0.50)

        risk_level = "High" if prob >= 0.65 else ("Medium" if prob >= 0.35 else "Low")

        drivers = []
        if input_dict.get('Burnout_Risk_Level') == 'High':
            drivers.append("High Burnout Risk indicator flagged")
        if input_dict.get('Satisfaction_Score', 10) < 5.0:
            drivers.append(f"Low Job Satisfaction ({input_dict.get('Satisfaction_Score')}/10)")
        if input_dict.get('Overtime_Hours_Weekly', 0) > 8:
            drivers.append(f"Heavy Overtime ({input_dict.get('Overtime_Hours_Weekly')} hrs/wk)")
        if input_dict.get('Weekly_Work_Hours', 40) >= 50:
            drivers.append(f"Excessive Weekly Workload ({input_dict.get('Weekly_Work_Hours')} hrs/wk)")
        if input_dict.get('Promotion_Last_2Years') == 'No' and input_dict.get('Years_at_Company', 0) >= 3:
            drivers.append("Stagnant career growth (No promotion in 2+ years)")
        if input_dict.get('Manager_Rating', 5) < 3.0:
            drivers.append(f"Low Manager Rating ({input_dict.get('Manager_Rating')}/5.0)")

        if not drivers:
            drivers.append("Stable workload and positive satisfaction indicators.")

        return {
            'attrition_prediction': 'Yes' if prediction == 1 else 'No',
            'attrition_probability_pct': round(prob * 100, 1),
            'risk_level': risk_level,
            'top_risk_drivers': drivers
        }


class ProductivityTierModel:
    """
    Classifies employee productivity tier into High Performer, Core Performer, or At-Risk.
    """
    def __init__(self):
        self.pipeline: Optional[Pipeline] = None
        self.metrics: Dict[str, Any] = {}

    def train(self, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        if df is None:
            df = load_and_clean_data()

        def get_tier(score):
            if score >= 85.0:
                return 'High'
            elif score >= 70.0:
                return 'Moderate'
            else:
                return 'Needs Improvement'

        y = df['Productivity_Score'].apply(get_tier)

        num_cols = [
            'Age', 'Total_Experience_Years', 'Years_at_Company', 'Weekly_Work_Hours',
            'Overtime_Hours_Weekly', 'Projects_Handled', 'Attendance_Pct',
            'Satisfaction_Score', 'Training_Hours_Last_Year', 'Work_From_Home_Pct'
        ]
        cat_cols = ['Department', 'Education_Level', 'Gender', 'Burnout_Risk_Level']

        X = df[num_cols + cat_cols]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), num_cols),
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_cols)
            ]
        )

        clf = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.08,
            max_depth=5,
            random_state=42
        )

        self.pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', clf)
        ])

        self.pipeline.fit(X_train, y_train)

        y_pred = self.pipeline.predict(X_test)

        self.metrics = {
            'accuracy': round(accuracy_score(y_test, y_pred) * 100, 2),
            'precision_macro': round(precision_score(y_test, y_pred, average='macro', zero_division=0) * 100, 2),
            'recall_macro': round(recall_score(y_test, y_pred, average='macro', zero_division=0) * 100, 2),
            'f1_macro': round(f1_score(y_test, y_pred, average='macro', zero_division=0) * 100, 2),
            'classes': list(self.pipeline.classes_)
        }

        try:
            joblib.dump({
                'pipeline': self.pipeline,
                'metrics': self.metrics
            }, PRODUCTIVITY_MODEL_FILE)
        except Exception:
            pass

        return self.metrics

    def load(self) -> bool:
        if os.path.exists(PRODUCTIVITY_MODEL_FILE):
            try:
                data = joblib.load(PRODUCTIVITY_MODEL_FILE)
                self.pipeline = data['pipeline']
                self.metrics = data['metrics']
                return True
            except Exception:
                return False
        return False

    def predict(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        if self.pipeline is None:
            if not self.load():
                self.train()

        input_df = pd.DataFrame([input_dict])
        pred_class = self.pipeline.predict(input_df)[0]
        probs = self.pipeline.predict_proba(input_df)[0]
        prob_dict = {
            cls_name: round(float(p) * 100, 1)
            for cls_name, p in zip(self.pipeline.classes_, probs)
        }

        recommendations = {
            'High': "Eligible for leadership mentorship, critical task leadership, and retention equity.",
            'Moderate': "Maintain consistent workload; provide targeted technical upskilling to reach High tier.",
            'Needs Improvement': "Schedule performance coaching, rebalance project allocations, and assess attendance/burnout root causes."
        }

        return {
            'predicted_tier': pred_class,
            'tier_probabilities': prob_dict,
            'strategic_guidance': recommendations.get(pred_class, "Standard performance review.")
        }


# Global singleton instances
_attrition_model = AttritionRiskModel()
_productivity_model = ProductivityTierModel()


def get_attrition_model() -> AttritionRiskModel:
    global _attrition_model
    if _attrition_model.pipeline is None:
        if not _attrition_model.load():
            _attrition_model.train()
    return _attrition_model


def get_productivity_model() -> ProductivityTierModel:
    global _productivity_model
    if _productivity_model.pipeline is None:
        if not _productivity_model.load():
            _productivity_model.train()
    return _productivity_model


def score_batch_workforce(df: pd.DataFrame) -> pd.DataFrame:
    """
    Appends AI Attrition Risk Probability and Predicted Productivity Tier to an entire dataframe.
    """
    if df.empty:
        return df

    df_copy = df.copy()
    att_model = get_attrition_model()
    prod_model = get_productivity_model()

    try:
        att_probs = att_model.pipeline.predict_proba(df_copy)[:, 1]
        df_copy['AI_Attrition_Risk_Pct'] = np.round(att_probs * 100, 1)
        df_copy['AI_Risk_Category'] = pd.cut(
            df_copy['AI_Attrition_Risk_Pct'],
            bins=[-1, 35, 65, 101],
            labels=['Low Risk', 'Medium Risk', 'High Risk']
        )
    except Exception:
        df_copy['AI_Attrition_Risk_Pct'] = 15.0
        df_copy['AI_Risk_Category'] = 'Low Risk'

    try:
        prod_tiers = prod_model.pipeline.predict(df_copy)
        df_copy['AI_Predicted_Productivity_Tier'] = prod_tiers
    except Exception:
        df_copy['AI_Predicted_Productivity_Tier'] = 'Moderate'

    return df_copy


def get_risk_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generates an executive talent risk summary with risk percentages and a sample of top high-risk employees.
    """
    if df.empty:
        return {
            'high_risk_pct': 0.0,
            'medium_risk_pct': 0.0,
            'low_risk_pct': 0.0,
            'high_risk_count': 0,
            'sample_high_risk_df': pd.DataFrame()
        }

    scored_df = score_batch_workforce(df)
    total = len(scored_df)

    high_risk_df = scored_df[scored_df['AI_Risk_Category'] == 'High Risk']
    med_risk_df = scored_df[scored_df['AI_Risk_Category'] == 'Medium Risk']
    low_risk_df = scored_df[scored_df['AI_Risk_Category'] == 'Low Risk']

    sample_table = high_risk_df[[
        'Employee_ID', 'Department', 'Job_Role', 'Weekly_Work_Hours',
        'Overtime_Hours_Weekly', 'Satisfaction_Score', 'Burnout_Risk_Level',
        'AI_Attrition_Risk_Pct'
    ]].sort_values(by='AI_Attrition_Risk_Pct', ascending=False).head(5)

    return {
        'high_risk_count': len(high_risk_df),
        'high_risk_pct': round((len(high_risk_df) / total) * 100.0, 1),
        'medium_risk_pct': round((len(med_risk_df) / total) * 100.0, 1),
        'low_risk_pct': round((len(low_risk_df) / total) * 100.0, 1),
        'sample_high_risk_df': sample_table
    }
