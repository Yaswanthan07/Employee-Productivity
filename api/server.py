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

from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

try:
    from app.auth_service import (
        register_company,
        login_user,
        logout_session,
        get_session_context,
        get_user_profile,
    )
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
    from auth_service import (
        register_company,
        login_user,
        logout_session,
        get_session_context,
        get_user_profile,
        update_user_profile,
        change_user_password,
    )
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

security = HTTPBearer(auto_error=False)

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
class CompanyRegistrationInput(BaseModel):
    company_name: str = Field(..., min_length=2, description="Company name")
    full_name: str = Field(..., min_length=2, description="HR user full name")
    email: str = Field(..., description="Work email")
    password: str = Field(..., min_length=8, description="Password")
    confirm_password: str = Field(..., min_length=8, description="Confirm password")


class LoginInput(BaseModel):
    email: str = Field(..., description="Email")
    password: str = Field(..., description="Password")


class ProfileUpdateInput(BaseModel):
    full_name: str = Field(..., min_length=2, description="Updated full name")


class PasswordChangeInput(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., min_length=8, description="Confirm new password")


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


def get_current_session(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    session = get_session_context(credentials.credentials)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return session


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


@app.post("/auth/register", tags=["Authentication"])
def register_user(payload: CompanyRegistrationInput):
    try:
        result = register_company(
            company_name=payload.company_name,
            full_name=payload.full_name,
            email=payload.email,
            password=payload.password,
            confirm_password=payload.confirm_password,
        )
        return {
            "message": "Company registered successfully.",
            **result,
        }
    except ValueError as exc:
        msg = str(exc)
        status_code = status.HTTP_409_CONFLICT if "already" in msg.lower() or "exists" in msg.lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=msg)


@app.post("/auth/login", tags=["Authentication"])
def login_user_endpoint(payload: LoginInput):
    try:
        session = login_user(email=payload.email, password=payload.password)
        return {
            "message": "Login successful.",
            **session,
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@app.post("/auth/logout", tags=["Authentication"])
def logout_user_endpoint(current_user: Dict[str, Any] = Depends(get_current_session)):
    success = logout_session(current_user["session_id"])
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to log out the current session.")
    return {"message": "Logged out successfully."}


@app.get("/auth/me", tags=["Authentication"])
def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_session)):
    profile = get_user_profile(current_user["user_id"])
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found.")
    return {
        "user_id": profile["user_id"],
        "company_id": profile["company_id"],
        "company_name": profile["company_name"],
        "full_name": profile["full_name"],
        "email": profile["email"],
        "role": profile["role"],
        "status": profile["status"],
    }


@app.put("/auth/profile", tags=["Authentication"])
def update_profile(payload: ProfileUpdateInput, current_user: Dict[str, Any] = Depends(get_current_session)):
    try:
        result = update_user_profile(current_user["user_id"], full_name=payload.full_name)
        return {"message": "Profile updated successfully.", **result}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@app.put("/auth/password", tags=["Authentication"])
def change_password(payload: PasswordChangeInput, current_user: Dict[str, Any] = Depends(get_current_session)):
    try:
        change_user_password(
            current_user["user_id"],
            current_password=payload.current_password,
            new_password=payload.new_password,
            confirm_password=payload.confirm_password,
        )
        return {"message": "Password updated successfully."}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@app.get("/kpis", tags=["KPIs & Analytics"])
def get_overall_kpis(
    current_user: Dict[str, Any] = Depends(get_current_session),
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
def get_department_kpis(current_user: Dict[str, Any] = Depends(get_current_session)):
    """
    Returns department-level benchmarking metrics.
    """
    df = load_and_clean_data()
    dept_df = compute_department_kpis(df)
    return dept_df.to_dict(orient="records")


@app.get("/workforce/allocation", tags=["Workforce Allocation"])
def get_workforce_allocation(current_user: Dict[str, Any] = Depends(get_current_session)):
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
def get_allocation_recommendations(current_user: Dict[str, Any] = Depends(get_current_session)):
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
def predict_attrition(payload: EmployeeFeatureInput, current_user: Dict[str, Any] = Depends(get_current_session)):
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
def predict_productivity(payload: EmployeeFeatureInput, current_user: Dict[str, Any] = Depends(get_current_session)):
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
