# ⚡ AI-Driven Employee Productivity & Workforce Allocation Optimization System

An executive-grade, end-to-end Machine Learning and Decision Intelligence platform designed to analyze employee productivity, detect workforce workload imbalances (overloaded vs. underutilized), benchmark cross-departmental efficiency, predict attrition and burnout risks, and orchestrate algorithmic workforce reallocation strategies.

---

## 🌟 Context, Problem Statement & SDG Alignment

Modern human resource management often grapples with uneven workload distributions, undetected employee burnout, lagging performance reviews, and unexpected talent attrition. This product equips HR managers, business unit leads, and enterprise planners with real-time, data-driven decision intelligence designed for high-level executive decision-making.

### Alignment with UN Sustainable Development Goals (SDGs)
- **SDG 8: Decent Work & Economic Growth (Target 8.5 & 8.8)**: Promotes balanced working hours, monitors overtime, reduces occupational burnout, fosters safe and healthy working environments, and unlocks individual potential through equitable workload distribution.
- **SDG 9: Industry, Innovation & Infrastructure (Target 9.5)**: Enhances corporate digital infrastructure by applying modern AI/ML predictive analytics to automate talent optimization and increase operational efficiency.

---

## 🏛️ System Architecture

```
employee-productivity-dashboard/
├── data/
│   ├── generate_data.py          # Synthetic dataset generator for Indian enterprise HR data
│   └── hr_analytics_india.csv    # Primary dataset (1,500+ employee records)
├── app/
│   ├── __init__.py
│   ├── backend.py                # Data loading, cleaning, validation & KPI computation engine
│   ├── ml_models.py              # ML pipelines (Attrition Risk Predictor, Productivity Classifier, Risk Summary)
│   ├── utils.py                  # Custom executive UI CSS, Plotly & Seaborn visual engines
│   └── main.py                   # Executive-ready Streamlit dashboard with narrative storytelling
├── api/
│   ├── __init__.py
│   └── server.py                 # Production-ready FastAPI REST service with Pydantic models
├── notebooks/
│   └── exploratory_analysis.ipynb# Jupyter notebook for deep EDA and model diagnostics
├── requirements.txt              # Complete Python dependency manifest
└── README.md                     # Comprehensive system documentation
```

---

## 📊 Executive Dashboard Hierarchy & Storytelling

The Streamlit dashboard ([`app/main.py`](file:///d:/Workspace/projects/Employee%20Productivity/app/main.py)) is structured for a **30-second executive scan**, moving from high-level business health to tactical allocation actions:

```
┌────────────────────────────────────────────────────────────────────────┐
│  ⚡ Top Executive Header: Product Title, Badges & Enterprise Scope     │
├────────────────────────────────────────────────────────────────────────┤
│  1. 📊 Key Performance Indicators (4 Top Business Metric Cards)       │
│     Avg Task Completion (%) | Avg Weekly Hours | Avg Rating | Attend % │
├────────────────────────────────────────────────────────────────────────┤
│  2. ⚖️ Workforce Allocation Insights (Overloaded vs. Underutilized)    │
│     Donut Breakdown + 4-Quadrant Matrix + Top Reallocation Actions     │
│     + Compact Top 5 Overloaded & Top 5 Underutilized Profile Lists     │
├────────────────────────────────────────────────────────────────────────┤
│  3. 🏢 Productivity by Department                                     │
│     Benchmarking Bar Chart + Top & Bottom Department Summary Cards     │
├────────────────────────────────────────────────────────────────────────┤
│  4. 📈 Workload & Performance Distributions                            │
│     Side-by-Side Distribution Histograms + Static Seaborn KDE Curves   │
├────────────────────────────────────────────────────────────────────────┤
│  5. 🤖 Talent Risk Overview & AI Predictive Engine                    │
│     Risk Tiers (% High/Med/Low) + Top 5 Attrition Candidates           │
│     + Interactive Single-Employee What-If Scenario Simulator          │
├────────────────────────────────────────────────────────────────────────┤
│  6. 📁 Advanced Data Explorer & Power BI Export (Collapsible)          │
│     Searchable raw data view kept out of executive flow + CSV Exports  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Domain | Technology / Library |
| :--- | :--- |
| **Language** | Python 3.9+ |
| **Data Processing** | Pandas, NumPy |
| **Machine Learning** | Scikit-Learn (Pipelines, RandomForest, GradientBoosting) |
| **Interactive Visualizations** | Plotly Express & Plotly Graph Objects |
| **Statistical Visualizations**| Seaborn, Matplotlib |
| **Frontend Application** | Streamlit (Executive UX layout) |
| **REST API Layer** | FastAPI, Uvicorn, Pydantic |
| **Notebook & Analytics** | Jupyter Notebook (IPython) |

---

## 🚀 Getting Started

### 1. Environment Setup

Clone the repository and create an isolated Python virtual environment:

```bash
# Navigate to project directory
cd employee-productivity-dashboard

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (cmd):
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

---

### 2. Running the Executive Streamlit Dashboard

Launch the polished web application:

```bash
streamlit run app/main.py
```
Open your browser and navigate to `http://localhost:8501`.

---

### 3. Running the FastAPI REST Backend (Optional)

Start the production API server:

```bash
uvicorn api.server:app --reload --port 8000
```
- API Documentation (Swagger UI): `http://localhost:8000/docs`
- Interactive OpenAPI Redoc: `http://localhost:8000/redoc`

#### Available API Endpoints:
- `GET /` — System health and endpoint catalog
- `GET /kpis` — Overall executive workforce KPIs (supports `?department=` and `?burnout=` query parameters)
- `GET /kpis/department` — Department-level aggregated metrics
- `GET /workforce/allocation` — Utilization counts and percentages
- `GET /workforce/recommendations` — AI reallocation recommendations list
- `POST /predict/attrition` — Predicts employee attrition probability and risk drivers
- `POST /predict/productivity` — Predicts productivity tier and strategic guidance

---

### 4. Running the Exploratory Data Analysis (EDA) Notebook

Launch JupyterLab or VS Code notebook viewer:

```bash
jupyter notebook notebooks/exploratory_analysis.ipynb
```

---

## 📈 Data Dictionary & Metric Formulations

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `Employee_ID` | String | Unique identifier (e.g., `EMP-1001`) |
| `Department` | Categorical | Technology, Finance, Sales, Human Resources, Operations, Marketing, R&D, Customer Support |
| `Job_Role` | Categorical | Specialized role within the department |
| `Total_Experience_Years` | Float | Cumulative work experience in years |
| `Monthly_Salary_INR` | Integer | Base monthly compensation in Indian Rupees (₹) |
| `Weekly_Work_Hours` | Float | Average hours worked per week |
| `Overtime_Hours_Weekly` | Float | Hours worked beyond standard 40 hrs/wk |
| `Task_Completion_Pct` | Float | Percentage of assigned deliverables completed on time |
| `Attendance_Pct` | Float | Punctuality and attendance adherence percentage |
| `Manager_Rating` | Float | Performance score (1.0 to 5.0) |
| `Satisfaction_Score` | Float | Self-reported job satisfaction (1.0 to 10.0) |
| `Burnout_Risk_Level` | Categorical | `Low`, `Medium`, `High` based on workload and sentiment |
| `Workforce_Status` | Categorical | Derived: `Overloaded`, `Underutilized`, `High Performer`, `Optimal / Balanced` |
| `Productivity_Score` | Float (0-100) | `(Task_Completion_Pct * 0.45) + (Manager_Rating * 20 * 0.35) + (Attendance_Pct * 0.20)` |

---

## 💡 Practical Business Takeaways for HR Leaders

1. **Preemptive Burnout Prevention**: Flag employees averaging >48 weekly hours before burnout translates to resignation or productivity collapse.
2. **Data-Driven Resource Allocation**: Reallocate secondary project deliverables from overloaded technical departments to high-capacity cohorts (e.g. Operations / Marketing).
3. **Equitable Recognition**: Identify hidden high-performers sustaining excellent productivity without unnecessary overtime.
4. **Targeted Capacity Upskilling**: Deploy training programs specifically to underutilized segments to expand organizational throughput.
