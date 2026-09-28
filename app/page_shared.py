import io
import os
import sys

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.backend import filter_data, load_and_clean_data, prepare_dataset_for_dashboard
from app.utils import get_custom_css

API_BASE_URL = os.getenv("EMPLOYEE_PRODUCTIVITY_API_URL", "http://localhost:8000")


@st.cache_data(ttl=3600)
def get_dataset():
    return load_and_clean_data()


def reset_active_dataset() -> None:
    for key in ["uploaded_employee_df", "sidebar_csv_validation", "dataset_source"]:
        st.session_state.pop(key, None)
    st.session_state["dataset_source"] = "default"


def get_active_dataset() -> pd.DataFrame:
    uploaded_df = st.session_state.get("uploaded_employee_df")
    if uploaded_df is not None and not pd.DataFrame(uploaded_df).empty:
        st.session_state["dataset_source"] = "uploaded"
        return prepare_dataset_for_dashboard(pd.DataFrame(uploaded_df))

    st.session_state["dataset_source"] = "default"
    return get_dataset()


COOKIE_NAME = "employee_productivity_auth_token"


def set_browser_cookie(name: str, value: str, days: int = 7) -> None:
    pass


def clear_browser_cookie(name: str) -> None:
    pass


def get_browser_cookie(name: str) -> None:
    return None


def clear_auth_session() -> None:
    for key in ["auth_token", "auth_user", "user_email", "company_id", "company_name", "user_role"]:
        if key in st.session_state:
            del st.session_state[key]
    clear_browser_cookie(COOKIE_NAME)


def password_policy_text(password: str):
    if not password:
        return ""
    checks = {
        "Minimum 8 characters": len(password) >= 8,
        "One uppercase letter": any(c.isupper() for c in password),
        "One lowercase letter": any(c.islower() for c in password),
        "One special character": any(not c.isalnum() for c in password),
    }
    rendered = "<ul style='margin:0.35rem 0 0 1rem; color: var(--muted); font-size:0.82rem;'>"
    for label, ok in checks.items():
        color = "var(--emerald)" if ok else "var(--muted)"
        icon = "✓" if ok else "•"
        rendered += f"<li style='color:{color}; font-weight:{'600' if ok else '400'}'>{label}: {icon}</li>"
    rendered += "</ul>"
    return rendered


def _api_request(method: str, path: str, payload: dict | None = None, token: str | None = None):
    url = f"{API_BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.request(method=method.upper(), url=url, json=payload, headers=headers, timeout=5)
        return response
    except requests.RequestException:
        return None


def login_user_action(email: str, password: str) -> tuple[bool, str]:
    if not email or not password:
        return False, "Work email and password are required."

    # 1. Try FastAPI REST endpoint
    response = _api_request("post", "/auth/login", {"email": email, "password": password})
    if response is not None and response.status_code == 200:
        data = response.json()
        st.session_state["auth_token"] = data["token"]
        st.session_state["auth_user"] = data["full_name"]
        st.session_state["user_email"] = data.get("email")
        st.session_state["company_id"] = data["company_id"]
        st.session_state["company_name"] = data.get("company_name", "Company")
        st.session_state["user_role"] = data.get("role", "HR")
        set_browser_cookie(COOKIE_NAME, data["token"])
        return True, "Login successful."

    # 2. Resilient local fallback directly against database
    try:
        from app.auth_service import login_user
        data = login_user(email, password)
        st.session_state["auth_token"] = data["token"]
        st.session_state["auth_user"] = data["full_name"]
        st.session_state["user_email"] = data.get("email")
        st.session_state["company_id"] = data["company_id"]
        st.session_state["company_name"] = data.get("company_name", "Company")
        st.session_state["user_role"] = data.get("role", "HR")
        set_browser_cookie(COOKIE_NAME, data["token"])
        return True, "Login successful."
    except Exception as exc:
        err_msg = str(exc)
        if response is not None and response.status_code != 200:
            err_msg = response.json().get("detail", err_msg)
        return False, err_msg


def validate_uploaded_csv_backend(uploaded_file) -> dict | None:
    if uploaded_file is None:
        return None

    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "text/csv")}
        response = requests.post(f"{API_BASE_URL}/upload/validate", files=files, timeout=20)
        if response is None:
            return {"success": False, "status": "invalid", "message": "Backend unavailable. Start the FastAPI API server first."}
        try:
            body = response.json()
        except ValueError:
            body = {"success": False, "status": "invalid", "message": "Unexpected backend response."}
        if response.status_code != 200:
            body.setdefault("success", False)
            body.setdefault("status", "invalid")
            body.setdefault("message", "Validation failed.")
        return body
    except requests.RequestException as exc:
        return {"success": False, "status": "invalid", "message": f"API request failed: {str(exc)}"}


def ensure_authenticated_session() -> tuple[bool, dict | None]:
    token = st.session_state.get("auth_token")
    if not token or not isinstance(token, str) or not str(token).strip():
        clear_auth_session()
        return False, None

    token = str(token).strip()
    st.session_state["auth_token"] = token
    response = _api_request("get", "/auth/me", token=token)
    if response is not None and response.status_code == 200:
        profile = response.json()
    else:
        # Fallback to local auth database verification
        from app.auth_service import get_session_context, get_user_profile
        sess = get_session_context(token)
        if not sess:
            clear_auth_session()
            return False, None
        profile = get_user_profile(sess["user_id"])
        if not profile:
            clear_auth_session()
            return False, None

    st.session_state["auth_user"] = profile.get("full_name")
    st.session_state["user_email"] = profile.get("email")
    st.session_state["company_id"] = profile.get("company_id")
    st.session_state["company_name"] = profile.get("company_name")
    st.session_state["user_role"] = profile.get("role")
    set_browser_cookie(COOKIE_NAME, token)
    return True, profile


def render_auth_screen() -> None:
    st.markdown(get_custom_css(), unsafe_allow_html=True)

    # Centered container styling
    st.markdown(
        """
        <style>
            .auth-hero-card {
                background: var(--panel);
                border: 1px solid var(--border);
                border-radius: 20px;
                padding: 2.2rem 2.5rem 1.8rem;
                box-shadow: 0 20px 45px -15px rgba(15, 23, 42, 0.12);
                position: relative;
                overflow: hidden;
                margin-top: 1.5rem;
                margin-bottom: 1.5rem;
            }
            .auth-hero-card::before {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0;
                height: 5px;
                background: linear-gradient(90deg, #4F46E5 0%, #10B981 50%, #8B5CF6 100%);
            }
            .auth-title-row {
                display: flex;
                align-items: center;
                gap: 0.9rem;
                margin-bottom: 0.8rem;
            }
            .auth-icon-badge {
                width: 48px;
                height: 48px;
                background: var(--primary-soft);
                color: var(--primary);
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                border: 1px solid var(--primary-border);
                box-shadow: 0 4px 10px rgba(79, 70, 229, 0.15);
            }
            .auth-title {
                font-size: 1.6rem;
                font-weight: 800;
                color: var(--text);
                letter-spacing: -0.03em;
                line-height: 1.2;
            }
            .auth-tagline {
                font-size: 0.8rem;
                color: var(--muted);
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.06em;
            }
            .auth-desc {
                font-size: 0.93rem;
                color: var(--muted);
                line-height: 1.55;
                margin-bottom: 1.2rem;
            }
            .auth-cred-box {
                background: var(--primary-soft);
                border: 1px solid var(--primary-border);
                border-radius: 12px;
                padding: 0.75rem 1rem;
                margin-bottom: 1.2rem;
                font-size: 0.85rem;
                color: var(--text);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    _, col_center, _ = st.columns([1, 2.2, 1])
    with col_center:
        st.markdown(
            """
            <div class="auth-hero-card">
                <div class="auth-title-row">
                    <div class="auth-icon-badge">⚡</div>
                    <div>
                        <div class="auth-title">Workforce Intelligence</div>
                        <div class="auth-tagline">Productivity & Allocation Optimizer</div>
                    </div>
                </div>
                <div class="auth-desc">
                    Executive decision portal for delivery benchmarking, capacity rebalancing, burnout alerts, and AI-powered attrition forecasting.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["🔐 Sign In to Workspace", "🏢 Register New Organization"])

        with tab_login:
            st.markdown(
                """
                <div class="auth-cred-box">
                    <div style="font-weight:700; color:var(--primary); margin-bottom:2px;">🔑 Verified Login Credentials Ready</div>
                    <div style="color:var(--text); font-size:0.82rem;">
                        Work Email: <b>yaswanthanbrcs225@gmail.com</b><br>
                        Password: <b>Rmkec@123.</b> (or <b>Rmkec@123</b>)
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("portal_login_form"):
                email_val = st.text_input(
                    "Work Email",
                    value="yaswanthanbrcs225@gmail.com",
                    placeholder="name@company.com",
                )
                pass_val = st.text_input(
                    "Password",
                    value="Rmkec@123.",
                    type="password",
                    placeholder="Enter password",
                )
                submit_login = st.form_submit_button("🚀 Sign In to Workspace", use_container_width=True, type="primary")

                if submit_login:
                    success, message = login_user_action(email_val, pass_val)
                    if success:
                        st.success("✅ Authentication successful. Loading workspace...")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

        with tab_register:
            with st.form("portal_register_form"):
                new_org = st.text_input("Organization Name", placeholder="e.g. Acme Corporation")
                new_admin = st.text_input("Administrator Name", placeholder="e.g. Jane Doe")
                new_email = st.text_input("Work Email", placeholder="e.g. admin@acme.com")
                new_pwd = st.text_input("Password", type="password", placeholder="Min. 8 characters")
                new_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")

                if new_pwd:
                    st.markdown(password_policy_text(new_pwd), unsafe_allow_html=True)

                submit_reg = st.form_submit_button("Create Enterprise Workspace", use_container_width=True, type="primary")
                if submit_reg:
                    if not all([new_org, new_admin, new_email, new_pwd, new_confirm]):
                        st.error("All registration fields are required.")
                    else:
                        reg_res = _api_request(
                            "post",
                            "/auth/register",
                            {
                                "company_name": new_org,
                                "full_name": new_admin,
                                "email": new_email,
                                "password": new_pwd,
                                "confirm_password": new_confirm,
                            },
                        )
                        if reg_res is not None and reg_res.status_code in (200, 201):
                            st.success("✅ Organization created! Switch to the 'Sign In' tab to log in.")
                        else:
                            detail = reg_res.json().get("detail", "Registration failed.") if reg_res else "Auth service unavailable."
                            st.error(f"❌ {detail}")


def configure_app(page_title: str = "Workforce Intelligence") -> None:
    # Injects the consolidated enterprise CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)

    auth_ok, _ = ensure_authenticated_session()
    if not auth_ok:
        st.rerun()


def render_page_header(title: str, subtitle: str, badges=None) -> None:
    badge_items = badges or []
    rendered_badges = "".join(f'<span class="badge-pill">{badge}</span>' for badge in badge_items)

    company = st.session_state.get("company_name", "R.M.K. Engineering College")
    user = st.session_state.get("auth_user", "Yaswanthan B R")
    role = st.session_state.get("user_role", "HR Admin")

    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-header-top">
                <div>
                    <h1 class="page-title">{title}</h1>
                    <div class="page-subtitle">{subtitle}</div>
                </div>
                <div class="tenant-pill">
                    <span class="tenant-dot"></span>
                    <span>🏢 <b>{company}</b></span>
                    <span style="opacity:0.4;">|</span>
                    <span>👤 {user} <span style="font-size:0.7rem; color:var(--primary); font-weight:700;">({role})</span></span>
                </div>
            </div>
            <div class="badge-row">{rendered_badges}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    title: str,
    value: str,
    caption: str,
    stripe: str = "stripe-blue",
    chip: str = "",
    chip_theme: str = "",
    *args,
    **kwargs,
) -> None:
    chip_val = chip or kwargs.get("chip", "")
    theme_val = chip_theme or kwargs.get("chip_theme", "")
    chip_html = ""
    if chip_val:
        theme_class = f"kpi-chip-{theme_val}" if theme_val else "kpi-chip-blue"
        chip_html = f'<span class="kpi-chip {theme_class}">{chip_val}</span>'

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-stripe {stripe}"></div>
            <div class="kpi-header-row">
                <div class="kpi-title">{title}</div>
                {chip_html}
            </div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(message: str = "No employee records match the active filter criteria.") -> None:
    st.warning(f"⚠️ {message}")
    st.stop()


def get_filtered_workforce():
    df_raw = get_active_dataset()

    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "selected_departments" not in st.session_state:
        st.session_state.selected_departments = []
    if "selected_roles" not in st.session_state:
        st.session_state.selected_roles = []
    if "selected_exp_tiers" not in st.session_state:
        st.session_state.selected_exp_tiers = []
    if "selected_burnout" not in st.session_state:
        st.session_state.selected_burnout = []

    with st.sidebar:
        company = st.session_state.get("company_name", "R.M.K. Engineering College")
        user = st.session_state.get("auth_user", "Yaswanthan B R")
        email = st.session_state.get("user_email", "yaswanthanbrcs225@gmail.com")
        role = st.session_state.get("user_role", "HR Admin")

        # 1. Organization & User Badge Card at TOP of Sidebar
        st.markdown(
            f"""
            <div style="background:var(--app-bg-alt); border:1px solid var(--border); border-radius:14px; padding:0.9rem 1rem; margin-bottom:0.6rem; box-shadow:var(--card-shadow);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;">
                    <span style="font-size:0.68rem; font-weight:700; text-transform:uppercase; color:var(--muted); letter-spacing:0.06em;">ACTIVE WORKSPACE</span>
                    <span style="font-size:0.68rem; background:var(--primary-soft); color:var(--primary); font-weight:700; padding:0.12rem 0.5rem; border-radius:999px;">{role}</span>
                </div>
                <div style="font-size:1.05rem; font-weight:800; color:var(--text); line-height:1.25; margin-bottom:0.25rem;">🏢 {company}</div>
                <div style="font-size:0.83rem; font-weight:600; color:var(--text);">👤 {user}</div>
                <div style="font-size:0.75rem; color:var(--muted);">{email}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 2. Prominent Quick Sign Out button right under the profile card!
        if st.button("🚪 Sign Out", use_container_width=True, key="sidebar_quick_logout_btn"):
            token = st.session_state.get("auth_token")
            if token:
                _api_request("post", "/auth/logout", token=token)
            clear_auth_session()
            st.success("Signed out successfully.")
            st.rerun()

        st.markdown("---")

        # 3. Direct, unmissable filter panel
        st.markdown("#### 🔍 Filter Workforce Cohort")

        st.session_state.search_query = st.text_input(
            "🔎 Search ID, Role, Dept",
            value=st.session_state.search_query,
            placeholder="e.g. EMP-1015, Tech Lead...",
        )

        all_departments = sorted(df_raw["Department"].unique().tolist())
        st.session_state.selected_departments = st.multiselect(
            "🏢 Department",
            options=all_departments,
            default=st.session_state.selected_departments,
            placeholder="All Departments",
        )

        if st.session_state.selected_departments:
            available_roles = sorted(
                df_raw[df_raw["Department"].isin(st.session_state.selected_departments)]["Job_Role"].unique().tolist()
            )
        else:
            available_roles = sorted(df_raw["Job_Role"].unique().tolist())

        st.session_state.selected_roles = st.multiselect(
            "💼 Job Role",
            options=available_roles,
            default=st.session_state.selected_roles,
            placeholder="All Roles",
        )

        all_tiers = [
            "Junior (0-3 yrs)",
            "Mid-Level (3-7 yrs)",
            "Senior (7-12 yrs)",
            "Lead / Principal (12+ yrs)",
        ]
        st.session_state.selected_exp_tiers = st.multiselect(
            "📈 Experience Tier",
            options=all_tiers,
            default=st.session_state.selected_exp_tiers,
            placeholder="All Tiers",
        )

        st.session_state.selected_burnout = st.multiselect(
            "🔥 Burnout Risk",
            options=["Low", "Medium", "High"],
            default=st.session_state.selected_burnout,
            placeholder="All Risk Levels",
        )

        if any([
            st.session_state.search_query,
            st.session_state.selected_departments,
            st.session_state.selected_roles,
            st.session_state.selected_exp_tiers,
            st.session_state.selected_burnout,
        ]):
            if st.button("✕ Reset All Filters", use_container_width=True):
                st.session_state.search_query = ""
                st.session_state.selected_departments = []
                st.session_state.selected_roles = []
                st.session_state.selected_exp_tiers = []
                st.session_state.selected_burnout = []
                st.rerun()

        # 4. Upload Custom CSV Data
        with st.expander("📁 Upload Custom Workforce Dataset", expanded=False):
            st.caption("Upload session CSV dataset to analyze custom workforce records.")

            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type=["csv"],
                key="sidebar_csv_uploader",
                label_visibility="collapsed",
            )

            val_col1, val_col2 = st.columns(2)
            with val_col1:
                validate_clicked = st.button("Validate", use_container_width=True, type="primary")
            with val_col2:
                if st.button("Reset", use_container_width=True, key="clear_sidebar_csv"):
                    st.session_state.pop("sidebar_csv_uploader", None)
                    st.session_state.pop("sidebar_csv_validation", None)
                    st.session_state.pop("uploaded_employee_df", None)
                    reset_active_dataset()
                    st.rerun()

            if validate_clicked and uploaded_file is not None:
                validation_report = validate_uploaded_csv_backend(uploaded_file)
                st.session_state["sidebar_csv_validation"] = validation_report

                if validation_report and validation_report.get("success"):
                    try:
                        raw_df = pd.read_csv(io.BytesIO(uploaded_file.getvalue()))
                        st.session_state["uploaded_employee_df"] = prepare_dataset_for_dashboard(raw_df)
                        st.session_state["dataset_source"] = "uploaded"
                    except Exception:
                        st.session_state["uploaded_employee_df"] = None
                        st.session_state["dataset_source"] = "default"
                else:
                    st.session_state["uploaded_employee_df"] = None
                    st.session_state["dataset_source"] = "default"

            validation_report = st.session_state.get("sidebar_csv_validation")
            if validation_report:
                status = validation_report.get("status", "invalid")
                status_label = status.replace("_", " ").title()
                if validation_report.get("success"):
                    st.success(f"Status: {status_label}")
                else:
                    st.error(f"Status: {status_label}")

                message = validation_report.get("message")
                if message:
                    st.caption(message)

    df = filter_data(
        df=df_raw,
        departments=st.session_state.selected_departments,
        roles=st.session_state.selected_roles,
        experience_tier=st.session_state.selected_exp_tiers,
        burnout_levels=st.session_state.selected_burnout,
        search_query=st.session_state.search_query,
    )
    return df_raw, df
