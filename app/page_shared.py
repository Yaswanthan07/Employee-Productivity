import os
import sys

import requests
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.backend import filter_data, load_and_clean_data
from app.utils import get_custom_css

API_BASE_URL = os.getenv("EMPLOYEE_PRODUCTIVITY_API_URL", "http://localhost:8000")

PAGE_NAV_ITEMS = [
    {"title": "Executive Overview", "path": "app/pages/01_Executive_Overview.py", "icon": "📊"},
    {"title": "Workforce Allocation", "path": "app/pages/02_Workforce_Allocation.py", "icon": "⚖️"},
    {"title": "Department Analytics", "path": "app/pages/03_Department_Analytics.py", "icon": "📈"},
    {"title": "Workload & Performance Analytics", "path": "app/pages/04_Workload_&_Performance_Analytics.py", "icon": "📉"},
    {"title": "Talent Risk & AI Predictions", "path": "app/pages/05_Talent_Risk_&_AI_Predictions.py", "icon": "🤖"},
    {"title": "Employee Data Explorer", "path": "app/pages/06_Employee_Data_Explorer.py", "icon": "🧾"},
]


@st.cache_data(ttl=3600)
def get_dataset():
    return load_and_clean_data()


COOKIE_NAME = "employee_productivity_auth_token"


def set_browser_cookie(name: str, value: str, days: int = 7) -> None:
    if not value:
        return
    secure_flag = "true" if os.getenv("APP_ENV", "development").lower() == "production" else "false"
    components.html(
        f"""
        <script>
            const secure = {secure_flag};
            const cookieValue = "{value}";
            document.cookie = "{name}=" + cookieValue + "; path=/; max-age={days * 86400}; SameSite=Lax" + (secure ? "; Secure" : "");
        </script>
        """,
        height=0,
    )


def clear_browser_cookie(name: str) -> None:
    components.html(
        f"""
        <script>
            document.cookie = "{name}=; path=/; max-age=0; SameSite=Lax";
        </script>
        """,
        height=0,
    )


def get_browser_cookie(name: str):
    script = """
    <script>
        function getCookie(name) {
            const match = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/([.$?*|{}()[\\]\\/+^])/g, '\\$1') + '=([^;]*)'));
            return match ? decodeURIComponent(match[1]) : '';
        }
        try { Streamlit.setComponentValue(getCookie('__COOKIE_NAME__')); } catch (e) {}
    </script>
    """.replace("__COOKIE_NAME__", name)
    cookie_value = components.html(script, height=0)
    return cookie_value or None


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
    rendered = "<ul style='margin:0.25rem 0 0 1rem; color: var(--muted);'>"
    for label, ok in checks.items():
        rendered += f"<li style='color:{'#15803D' if ok else '#526357'}'>{label}: {'✓' if ok else '•'}</li>"
    rendered += "</ul>"
    return rendered


def _api_request(method: str, path: str, payload: dict | None = None, token: str | None = None):
    url = f"{API_BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.request(method=method.upper(), url=url, json=payload, headers=headers, timeout=10)
        return response
    except requests.RequestException:
        return None


def ensure_authenticated_session() -> tuple[bool, dict | None]:
    token = st.session_state.get("auth_token") or get_browser_cookie(COOKIE_NAME)
    if not token:
        clear_auth_session()
        return False, None

    st.session_state["auth_token"] = token
    response = _api_request("get", "/auth/me", token=token)
    if response is None or response.status_code != 200:
        clear_auth_session()
        return False, None

    profile = response.json()
    st.session_state["auth_user"] = profile.get("full_name")
    st.session_state["user_email"] = profile.get("email")
    st.session_state["company_id"] = profile.get("company_id")
    st.session_state["company_name"] = profile.get("company_name")
    st.session_state["user_role"] = profile.get("role")
    set_browser_cookie(COOKIE_NAME, token)
    return True, profile


def render_auth_screen() -> None:
    st.set_page_config(
        page_title="Company Access",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    st.markdown(
        """
        <style>
            .auth-shell {
                max-width: 720px;
                margin: 2rem auto;
                background: var(--panel, #FFFFFF);
                border: 1px solid var(--border, #DCE7DE);
                border-radius: 18px;
                padding: 1.5rem;
                box-shadow: 0 20px 30px -28px rgba(21, 128, 61, 0.28);
            }
            .auth-header {
                font-size: clamp(1.7rem, 3vw, 2.5rem);
                font-weight: 800;
                letter-spacing: -0.03em;
                margin-bottom: 0.5rem;
                color: var(--text, #17231B);
            }
            .auth-subtitle {
                color: var(--muted, #526357);
                margin-bottom: 1.25rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="auth-shell">
            <div class="auth-header">Company Access</div>
            <div class="auth-subtitle">Secure sign-in for your workforce intelligence workspace.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, register_tab = st.tabs(["Login", "Register Company"])

    with login_tab:
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Work email", placeholder="hr@company.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in")
            if submitted:
                if not email or not password:
                    st.error("Email and password are required.")
                else:
                    response = _api_request("post", "/auth/login", {"email": email, "password": password})
                    if response is None:
                        st.error("Authentication service is unavailable. Start the FastAPI backend first.")
                    elif response.status_code == 200:
                        data = response.json()
                        st.session_state["auth_token"] = data["token"]
                        st.session_state["auth_user"] = data["full_name"]
                        st.session_state["user_email"] = data.get("email")
                        st.session_state["company_id"] = data["company_id"]
                        st.session_state["company_name"] = data.get("company_name", "Company")
                        st.session_state["user_role"] = data.get("role", "HR")
                        set_browser_cookie(COOKIE_NAME, data["token"])
                        st.success("Login successful. Redirecting to the dashboard...")
                        st.rerun()
                    else:
                        st.error(response.json().get("detail", "Invalid email or password."))

    with register_tab:
        with st.form("register_form", clear_on_submit=False):
            company_name = st.text_input("Company name")
            full_name = st.text_input("HR user full name")
            email = st.text_input("Work email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            if password:
                st.markdown(password_policy_text(password), unsafe_allow_html=True)
            submitted = st.form_submit_button("Create company account")
            if submitted:
                if not all([company_name, full_name, email, password, confirm_password]):
                    st.error("All fields are required.")
                else:
                    response = _api_request(
                        "post",
                        "/auth/register",
                        {
                            "company_name": company_name,
                            "full_name": full_name,
                            "email": email,
                            "password": password,
                            "confirm_password": confirm_password,
                        },
                    )
                    if response is None:
                        st.error("Authentication service is unavailable. Start the FastAPI backend first.")
                    elif response.status_code in (200, 201):
                        st.success("Company registered successfully. You can now log in.")
                    else:
                        st.error(response.json().get("detail", "Registration failed."))


def _account_widget_key(name: str, page_title: str | None = None) -> str:
    suffix = (page_title or "app").strip().lower()
    suffix = "".join(ch if ch.isalnum() else "_" for ch in suffix).strip("_") or "app"
    return f"account_{suffix}_{name}"


def render_account_menu() -> None:
    with st.columns([8, 1])[1]:
        with st.popover("⋮", use_container_width=True):
            if st.button("👤 Profile", use_container_width=True):
                st.session_state["account_view"] = "profile"
            if st.button("⚙️ Settings", use_container_width=True):
                st.session_state["account_view"] = "settings"
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                token = st.session_state.get('auth_token')
                if token:
                    _api_request('post', '/auth/logout', token=token)
                clear_auth_session()
                st.session_state.pop("account_view", None)
                st.success('You have been logged out.')
                st.rerun()


def render_account_view(page_title: str | None = None) -> None:
    view = st.session_state.get("account_view")
    if not view:
        return

    profile_key = _account_widget_key("profile_name", page_title)
    current_password_key = _account_widget_key("current_password", page_title)
    new_password_key = _account_widget_key("new_password", page_title)
    confirm_password_key = _account_widget_key("confirm_password", page_title)

    if view == "profile":
        st.markdown("### Profile")
        st.write(f"**Name:** {st.session_state.get('auth_user', 'User')}")
        st.write(f"**Company:** {st.session_state.get('company_name', 'Company')}")
        st.write(f"**Email:** {st.session_state.get('user_email', 'Unknown')}")
        profile_name = st.text_input("Full name", value=st.session_state.get('auth_user', ''), key=profile_key)
        if st.button("Save profile"):
            token = st.session_state.get('auth_token')
            response = _api_request('put', '/auth/profile', {'full_name': profile_name}, token=token)
            if response and response.status_code == 200:
                st.session_state['auth_user'] = response.json()['full_name']
                st.success('Profile updated successfully.')
            else:
                st.error((response.json() if response else {}).get('detail', 'Unable to update profile.'))
    elif view == "settings":
        st.markdown("### Settings")
        st.caption('Security & account settings')
        current_password = st.text_input('Current password', type='password', key=current_password_key)
        new_password = st.text_input('New password', type='password', key=new_password_key)
        if new_password:
            st.markdown(password_policy_text(new_password), unsafe_allow_html=True)
        confirm_password = st.text_input('Confirm new password', type='password', key=confirm_password_key)
        if st.button('Change password'):
            if not all([current_password, new_password, confirm_password]):
                st.error('Complete all password fields.')
            else:
                token = st.session_state.get('auth_token')
                response = _api_request('put', '/auth/password', {
                    'current_password': current_password,
                    'new_password': new_password,
                    'confirm_password': confirm_password,
                }, token=token)
                if response and response.status_code == 200:
                    st.success('Password updated successfully.')
                else:
                    st.error((response.json() if response else {}).get('detail', 'Unable to change password.'))


def configure_app(page_title: str = "AI Workforce Productivity & Allocation Optimizer") -> None:
    st.set_page_config(
        page_title=page_title,
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    auth_ok, _ = ensure_authenticated_session()
    if not auth_ok:
        render_auth_screen()
        st.stop()

    st.markdown(get_custom_css(), unsafe_allow_html=True)
    render_account_menu()
    render_account_view(page_title=page_title)

    st.markdown(
        """
        <style>
            [data-testid="stHeader"] {
                background: transparent !important;
                box-shadow: none !important;
            }
            nav[data-testid="stPageNavigation"] {
                display: flex !important;
                flex-wrap: nowrap !important;
                white-space: nowrap !important;
                overflow-x: visible !important;
                gap: 0.25rem !important;
                align-items: center !important;
                justify-content: flex-start !important;
                background: rgba(255, 255, 255, 0.96) !important;
                border: 1px solid rgba(21, 128, 61, 0.18) !important;
                border-radius: 12px !important;
                padding: 0.2rem 0.4rem !important;
                margin: 0.1rem 0 0.8rem 0 !important;
                box-shadow: 0 10px 24px -20px rgba(21, 128, 61, 0.35);
            }
            nav[data-testid="stPageNavigation"] a {
                color: #17231B !important;
                background: transparent !important;
                border-radius: 8px !important;
                padding: 0.42rem 0.6rem !important;
                font-size: 0.73rem !important;
                font-weight: 600 !important;
                line-height: 1.2 !important;
                border: 1px solid transparent !important;
                min-width: max-content !important;
                flex-shrink: 0 !important;
                text-decoration: none !important;
            }
            nav[data-testid="stPageNavigation"] a:hover {
                background: rgba(21, 128, 61, 0.08) !important;
                border-color: rgba(21, 128, 61, 0.16) !important;
            }
            nav[data-testid="stPageNavigation"] a[aria-current="page"] {
                background: linear-gradient(180deg, rgba(21, 128, 61, 0.12), rgba(21, 128, 61, 0.04)) !important;
                border: 1px solid rgba(21, 128, 61, 0.26) !important;
                color: #17231B !important;
            }
            html[data-theme="dark"] nav[data-testid="stPageNavigation"],
            body[data-theme="dark"] nav[data-testid="stPageNavigation"] {
                background: rgba(18, 33, 24, 0.96) !important;
                border-color: rgba(74, 222, 128, 0.22) !important;
                box-shadow: 0 10px 24px -20px rgba(0, 0, 0, 0.42) !important;
            }
            html[data-theme="dark"] nav[data-testid="stPageNavigation"] a,
            body[data-theme="dark"] nav[data-testid="stPageNavigation"] a {
                color: #F2F8F3 !important;
            }
            html[data-theme="dark"] nav[data-testid="stPageNavigation"] a:hover,
            body[data-theme="dark"] nav[data-testid="stPageNavigation"] a:hover {
                background: rgba(74, 222, 128, 0.08) !important;
                border-color: rgba(74, 222, 128, 0.18) !important;
            }
            html[data-theme="dark"] nav[data-testid="stPageNavigation"] a[aria-current="page"],
            body[data-theme="dark"] nav[data-testid="stPageNavigation"] a[aria-current="page"] {
                background: linear-gradient(180deg, rgba(74, 222, 128, 0.14), rgba(74, 222, 128, 0.04)) !important;
                border-color: rgba(74, 222, 128, 0.22) !important;
                color: #F2F8F3 !important;
            }
            button[title="Deploy"],
            [data-testid="stHeader"] button[title*="Deploy"],
            [data-testid="stHeader"] [aria-label*="Deploy"] {
                display: none !important;
            }
            :root {
                --app-bg: #FFFFFF;
                --app-bg-2: #F7FAF7;
                --panel: #FFFFFF;
                --panel-2: #F7FAF7;
                --panel-3: #F7FAF7;
                --border: #DCE7DE;
                --border-soft: rgba(21, 128, 61, 0.12);
                --text: #17231B;
                --muted: #526357;
                --accent: #15803D;
                --accent-dark: #166534;
                --accent-soft: #EAF5EC;
                --sidebar-bg: #FFFFFF;
                --sidebar-bg-2: #F7FAF7;
                --topnav-bg: rgba(255,255,255,0.96);
                --topnav-border: rgba(21, 128, 61, 0.18);
            }
            html[data-theme="dark"], body[data-theme="dark"] {
                --app-bg: #0E1A13;
                --app-bg-2: #122118;
                --panel: #12311F;
                --panel-2: #163C28;
                --panel-3: #183D2B;
                --border: #2B5541;
                --border-soft: rgba(74, 222, 128, 0.18);
                --text: #F2F8F3;
                --muted: #CFE1D4;
                --accent: #4ADE80;
                --accent-dark: #22C55E;
                --accent-soft: rgba(74, 222, 128, 0.12);
                --sidebar-bg: #122118;
                --sidebar-bg-2: #163C28;
                --topnav-bg: rgba(18, 33, 24, 0.96);
                --topnav-border: rgba(74, 222, 128, 0.20);
            }
            .premium-shell { padding-bottom: 2rem; }
            .page-header {
                background: linear-gradient(135deg, #FFFFFF 0%, #F7FAF7 100%);
                border-radius: 18px;
                padding: 1.5rem 1.5rem 1.1rem 1.5rem;
                color: var(--text);
                box-shadow: 0 18px 30px -18px rgba(21, 128, 61, 0.25);
                margin-bottom: 1.25rem;
                border: 1px solid var(--border);
            }
            html[data-theme="dark"] .page-header,
            body[data-theme="dark"] .page-header {
                background: linear-gradient(135deg, #122118 0%, #163C28 100%) !important;
                border-color: var(--border) !important;
                box-shadow: 0 18px 30px -18px rgba(0, 0, 0, 0.38) !important;
            }
            .page-title {
                font-size: clamp(1.6rem, 2vw, 2.4rem);
                font-weight: 800;
                letter-spacing: -0.03em;
                margin-bottom: 0.4rem;
                color: var(--text);
            }
            .page-subtitle {
                color: var(--muted);
                font-size: 0.97rem;
                line-height: 1.6;
                max-width: 1100px;
            }
            .badge-row { margin-top: 0.9rem; }
            .badge-pill {
                display: inline-block;
                background: var(--accent-soft);
                color: var(--accent-dark, var(--accent));
                border: 1px solid var(--border);
                padding: 0.45rem 0.75rem;
                border-radius: 999px;
                font-size: 0.72rem;
                font-weight: 700;
                margin-right: 0.5rem;
                margin-bottom: 0.4rem;
            }
            .section-shell {
                background: var(--accent-soft);
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 1rem 1rem 0.5rem;
                margin-bottom: 1rem;
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, var(--sidebar-bg) 0%, var(--sidebar-bg-2) 100%) !important;
                border-right: 1px solid var(--border) !important;
                color: var(--text) !important;
                transition: width 0.25s ease, min-width 0.25s ease, opacity 0.25s ease, padding 0.25s ease;
            }
            [data-testid="stSidebar"] .stTextInput > div,
            [data-testid="stSidebar"] .stMultiSelect > div,
            [data-testid="stSidebar"] .stSelectbox > div,
            [data-testid="stSidebar"] .stNumberInput > div {
                background: var(--panel);
                border: 1px solid var(--border);
                border-radius: 10px;
            }
            [data-testid="stSidebar"] input,
            [data-testid="stSidebar"] span,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] .stMarkdown {
                color: var(--text) !important;
            }
            [data-testid="stSidebar"] .stCaption {
                color: var(--muted) !important;
            }
            .sidebar-toggle-wrap {
                display: flex;
                justify-content: flex-start;
                margin: 0 0 0.85rem 0;
            }
            .sidebar-toggle-btn {
                border: 1px solid rgba(21,128,61,0.20);
                background: var(--accent-soft);
                color: var(--text);
                border-radius: 8px;
                padding: 0.35rem 0.5rem;
                font-size: 0.95rem;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .sidebar-toggle-btn:hover {
                background: rgba(21, 128, 61, 0.08);
            }
            body[data-sidebar-collapsed="true"] [data-testid="stSidebar"] {
                width: 0px !important;
                min-width: 0px !important;
                max-width: 0px !important;
                padding: 0 !important;
                overflow: hidden !important;
                opacity: 0 !important;
                border: none !important;
            }
            body[data-sidebar-collapsed="true"] [data-testid="stSidebar"] > div {
                display: none !important;
            }
            body[data-sidebar-collapsed="true"] [data-testid="stAppViewContainer"] {
                margin-left: 0 !important;
            }
            .kpi-card {
                position: relative;
                background: var(--panel, #FFFFFF) !important;
                border: 1px solid var(--border, #DCE7DE);
                border-radius: 18px;
                padding: 1rem 1rem 0.9rem;
                box-shadow: 0 18px 30px -24px rgba(21, 128, 61, 0.25);
                height: 100%;
                overflow: hidden;
                color: var(--text, #17231B) !important;
            }
            .kpi-stripe { height: 6px; width: 100%; border-radius: 999px; margin-bottom: 0.9rem; }
            .stripe-blue { background: linear-gradient(90deg, #15803D, #4ADE80); }
            .stripe-purple { background: linear-gradient(90deg, #166534, #86EFAC); }
            .stripe-emerald { background: linear-gradient(90deg, #166534, #4ADE80); }
            .stripe-amber { background: linear-gradient(90deg, #22C55E, #BBF7D0); }
            .stripe-red { background: linear-gradient(90deg, #15803D, #86EFAC); }
            .kpi-title {
                font-size: 0.8rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: var(--muted, #526357);
            }
            .kpi-value {
                font-size: clamp(1.5rem, 2.2vw, 2.1rem);
                font-weight: 800;
                color: var(--text, #17231B);
                line-height: 1.15;
                margin: 0.5rem 0;
            }
            .kpi-caption {
                font-size: 0.76rem;
                color: var(--muted, #526357);
            }
            .story-box {
                background: var(--panel, #FFFFFF);
                border-left: 4px solid var(--accent, #15803D);
                border-radius: 14px;
                padding: 0.8rem 1rem;
                color: var(--text, #17231B);
                margin-bottom: 1rem;
                box-shadow: 0 2px 10px -8px rgba(21,128,61,0.08);
            }
            .story-box-amber { background: rgba(34, 197, 94, 0.06); border-left-color: #22C55E; }
            .story-box-emerald { background: rgba(22, 163, 74, 0.06); border-left-color: #16A34A; }
            .action-card {
                background: var(--panel, #FFFFFF) !important;
                border: 1px solid var(--border, #DCE7DE);
                border-radius: 14px;
                padding: 0.85rem 0.9rem;
                box-shadow: 0 14px 28px -26px rgba(21, 128, 61, 0.24);
                margin-bottom: 0.75rem;
                color: var(--text, #17231B) !important;
            }
            .feature-grid > div { padding: 0.3rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str, badges=None) -> None:
    badge_items = badges or []
    rendered_badges = "".join(f'<span class="badge-pill">{badge}</span>' for badge in badge_items)
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-title">{title}</div>
            <div class="page-subtitle">{subtitle}</div>
            <div class="badge-row">{rendered_badges}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(title: str, value: str, caption: str, stripe: str = "stripe-blue") -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-stripe {stripe}"></div>
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(message: str = "No employee records match the active filter criteria.") -> None:
    st.warning(message)
    st.stop()


def render_landing_page() -> None:
    st.markdown(
        """
        <div class="page-header">
            <div class="page-title">⚡ AI-Driven Workforce Allocation & Productivity Optimizer</div>
            <div class="page-subtitle">
                Executive decision intelligence platform for employee productivity analysis, workload balancing,
                capability benchmarking, talent risk detection, and strategic workforce reallocation.
            </div>
            <div class="badge-row">
                <span class="badge-pill">🤖 ML Predictive Engine</span>
                <span class="badge-pill">⚖️ Workforce Balancer</span>
                <span class="badge-pill">📊 Executive Dashboard</span>
                <span class="badge-pill">🎯 SDG 8 & 9</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-shell">
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem;">
                <div class="action-card">
                    <div style="font-size:0.72rem; font-weight:700; color:#15803D; text-transform:uppercase;">Overview</div>
                    <div style="font-weight:800; font-size:1.1rem; color:var(--text); margin:0.3rem 0;">Executive health</div>
                    <div style="color:var(--muted);">Monitor productivity, workload, attendance, and strategic signals across the workforce.</div>
                </div>
                <div class="action-card">
                    <div style="font-size:0.72rem; font-weight:700; color:#166534; text-transform:uppercase;">Allocation</div>
                    <div style="font-weight:800; font-size:1.1rem; color:var(--text); margin:0.3rem 0;">Rebalance capacity</div>
                    <div style="color:var(--muted);">Flag overworked teams and surface underused talent ready for reallocation.</div>
                </div>
                <div class="action-card">
                    <div style="font-size:0.72rem; font-weight:700; color:#15803D; text-transform:uppercase;">Risk</div>
                    <div style="font-weight:800; font-size:1.1rem; color:var(--text); margin:0.3rem 0;">AI talent risk</div>
                    <div style="color:var(--muted);">Assess attrition signals, burnout pressure, and productivity forecast scenarios.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Navigation")
    st.info("Use the sidebar to move between the six premium pages: Executive Overview, Workforce Allocation, Department Analytics, Workload & Performance Analytics, Talent Risk & AI Predictions, and Employee Data Explorer.")


def get_filtered_workforce():
    df_raw = get_dataset()

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
        st.markdown(
            """
            <div class="sidebar-toggle-wrap">
                <button class="sidebar-toggle-btn" id="sidebar-toggle-btn" aria-label="Toggle sidebar">⟨</button>
            </div>
            <script>
                const btn = document.getElementById('sidebar-toggle-btn');
                const setCollapsed = (collapsed) => {
                    document.body.setAttribute('data-sidebar-collapsed', collapsed ? 'true' : 'false');
                    if (btn) {
                        btn.textContent = collapsed ? '⟩' : '⟨';
                        btn.setAttribute('aria-label', collapsed ? 'Expand sidebar' : 'Collapse sidebar');
                    }
                };
                if (btn && !window.__sidebarToggleBound) {
                    btn.addEventListener('click', function() {
                        const collapsed = document.body.getAttribute('data-sidebar-collapsed') === 'true';
                        setCollapsed(!collapsed);
                    });
                    window.__sidebarToggleBound = true;
                }
            </script>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("### ⚡ Workforce Navigator")
        st.caption("AI-powered HR intelligence platform for productivity analysis and workload balancing.")
        st.markdown("---")
        st.markdown("#### 🔍 Filter Workforce")

        st.session_state.search_query = st.text_input(
            "🔎 Search by ID, Role, Dept",
            value=st.session_state.search_query,
            placeholder="e.g. EMP-1015, Tech Lead...",
        )

        all_departments = sorted(df_raw["Department"].unique().tolist())
        st.session_state.selected_departments = st.multiselect(
            "🏢 Department",
            options=all_departments,
            default=st.session_state.selected_departments,
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
        )

        all_tiers = [
            "Junior (0-3 yrs)",
            "Mid-Level (3-7 yrs)",
            "Senior (7-12 yrs)",
            "Lead / Principal (12+ yrs)",
        ]
        st.session_state.selected_exp_tiers = st.multiselect(
            "📈 Experience Band",
            options=all_tiers,
            default=st.session_state.selected_exp_tiers,
        )

        st.session_state.selected_burnout = st.multiselect(
            "🔥 Burnout Risk",
            options=["Low", "Medium", "High"],
            default=st.session_state.selected_burnout,
        )

        st.markdown("---")
        st.markdown("#### 💡 How to use this workspace")
        st.markdown(
            """
            1. Scan top KPIs to gauge workforce health.
            2. Review allocation and risk signals across teams.
            3. Drill into departments and individual employees.
            4. Export clean or AI-enriched datasets for planning.
            """
        )

        st.caption(f"📊 Active Filtered Cohort: **{len(df_raw):,}** total employees in DB.")

    df = filter_data(
        df=df_raw,
        departments=st.session_state.selected_departments,
        roles=st.session_state.selected_roles,
        experience_tier=st.session_state.selected_exp_tiers,
        burnout_levels=st.session_state.selected_burnout,
        search_query=st.session_state.search_query,
    )
    return df_raw, df
