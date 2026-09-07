"""
FastAPI Backend Server for AI-Driven Employee Productivity & Workforce Allocation Optimization System.
Provides RESTful endpoints for enterprise KPI retrieval, departmental analytics,
machine learning inference, and algorithmic workforce reallocation recommendations.
"""

from typing import Dict, List, Any, Optional
import os
import sys

# Ensure parent directory and app directory are in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(BASE_DIR, "app")
for p in [BASE_DIR, APP_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
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
        get_productivity_model
    )
except ImportError:
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
        get_productivity_model
    )

# Initialize FastAPI App
app = FastAPI(
    title="Employee Productivity & Workforce Allocation Optimization API",
    description="Enterprise REST API for AI-powered workforce analytics, attrition prediction, and capacity optimization.",
    version="1.0.0"
)

# Enable CORS for external frontend or Power BI connector integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------
class EmployeeFeatureInput(BaseModel):
    Age: int = Field(default=30, ge=18, le=70, description="Employee Age")
    Gender: str = Field(default="Male", description="Gender (Male, Female, Other)")
    Department: str = Field(default="Technology", description="Department name")
    Education_Level: str = Field(default="Bachelor", description="Education Level (Bachelor, Master, PhD, Diploma)")
    Total_Experience_Years: float = Field(default=5.0, ge=0.0, le=45.0, description="Total work experience in years")
    Years_at_Company: float = Field(default=2.5, ge=0.0, le=35.0, description="Tenure at company in years")
    Monthly_Salary_INR: float = Field(default=95000.0, ge=15000.0, description="Monthly salary in INR")
    Weekly_Work_Hours: float = Field(default=45.0, ge=10.0, le=90.0, description="Average weekly work hours")
    Overtime_Hours_Weekly: float = Field(default=5.0, ge=0.0, le=50.0, description="Weekly overtime hours")
    Projects_Handled: int = Field(default=4, ge=1, le=20, description="Active projects handled")
    Task_Completion_Pct: float = Field(default=85.0, ge=0.0, le=100.0, description="Task completion rate (%)")
    Attendance_Pct: float = Field(default=94.0, ge=0.0, le=100.0, description="Attendance rate (%)")
    Manager_Rating: float = Field(default=3.8, ge=1.0, le=5.0, description="Manager rating score (1.0 to 5.0)")
    Satisfaction_Score: float = Field(default=7.0, ge=1.0, le=10.0, description="Job satisfaction score (1.0 to 10.0)")
    Burnout_Risk_Level: str = Field(default="Low", description="Burnout risk level (Low, Medium, High)")
    Work_From_Home_Pct: float = Field(default=40.0, ge=0.0, le=100.0, description="Work from home percentage")
    Training_Hours_Last_Year: float = Field(default=24.0, ge=0.0, le=200.0, description="Training hours completed")
    Promotion_Last_2Years: str = Field(default="No", description="Promoted in last 2 years (Yes / No)")


class AttritionPredictionResponse(BaseModel):
    attrition_prediction: str
    attrition_probability_pct: float
    risk_level: str
    top_risk_drivers: List[str]


class ProductivityPredictionResponse(BaseModel):
    predicted_tier: str
    tier_probabilities: Dict[str, float]
    strategic_guidance: str


# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------
@app.get("/", tags=["Health & Metadata"])
def get_root():
    return {
        "system": "AI-Driven Employee Productivity & Workforce Allocation Optimization System",
        "status": "online",
        "version": "1.0.0",
        "endpoints": [
            "/kpis",
            "/kpis/department",
            "/workforce/allocation",
            "/workforce/recommendations",
            "/predict/attrition",
            "/predict/productivity"
        ]
    }


@app.get("/health", tags=["Health & Metadata"])
def health_check():
    return {"status": "healthy", "service": "productivity-engine-api"}


@app.get("/kpis", tags=["KPIs & Analytics"])
def get_overall_kpis(
    department: Optional[str] = Query(None, description="Filter by department (optional)"),
    burnout: Optional[str] = Query(None, description="Filter by burnout risk (optional)")
):
    """
    Returns executive top-level workforce KPIs.
    """
    df = load_and_clean_data()
    depts = [department] if department else None
    burnouts = [burnout] if burnout else None

    filtered = filter_data(df, departments=depts, burnout_levels=burnouts)
    kpis = compute_top_level_kpis(filtered)
    return kpis


@app.get("/kpis/department", tags=["KPIs & Analytics"])
def get_department_kpis():
    """
    Returns department-level benchmarking metrics.
    """
    df = load_and_clean_data()
    dept_df = compute_department_kpis(df)
    return dept_df.to_dict(orient="records")


@app.get("/workforce/allocation", tags=["Workforce Allocation"])
def get_workforce_allocation():
    """
    Returns breakdown of overloaded, underutilized, high-performer, and balanced workforce counts.
    """
    df = load_and_clean_data()
    counts = df['Workforce_Status'].value_counts().to_dict()
    total = len(df)
    percentages = {k: round((v / total) * 100.0, 1) for k, v in counts.items()}

    return {
        "total_headcount": total,
        "counts": counts,
        "percentages": percentages
    }


@app.get("/workforce/recommendations", tags=["Workforce Allocation"])
def get_allocation_recommendations():
    """
    Returns data-driven workforce reallocation strategies and priority action items.
    """
    df = load_and_clean_data()
    recommendations = generate_allocation_recommendations(df)
    return {
        "count": len(recommendations),
        "recommendations": recommendations
    }


@app.post("/predict/attrition", response_model=AttritionPredictionResponse, tags=["Machine Learning"])
def predict_attrition(payload: EmployeeFeatureInput):
    """
    Predicts employee attrition risk probability, risk category, and key contributing drivers.
    """
    try:
        model = get_attrition_model()
        data_dict = payload.model_dump()
        result = model.predict(data_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/predict/productivity", response_model=ProductivityPredictionResponse, tags=["Machine Learning"])
def predict_productivity(payload: EmployeeFeatureInput):
    """
    Predicts employee productivity tier and provides strategic HR guidance.
    """
    try:
        model = get_productivity_model()
        data_dict = payload.model_dump()
        result = model.predict(data_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)
