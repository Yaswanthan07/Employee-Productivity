import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st

from app.backend import filter_data, load_and_clean_data
from app.utils import get_custom_css


@st.cache_data(ttl=3600)
def get_dataset():
    return load_and_clean_data()


def configure_app(page_title: str = "AI Workforce Productivity & Allocation Optimizer") -> None:
    st.set_page_config(
        page_title=page_title,
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    st.markdown(
        """
        <style>
            .premium-shell { padding-bottom: 2rem; }
            .page-header {
                background: linear-gradient(135deg, #0F172A 0%, #1E293B 55%, #0EA5E9 100%);
                border-radius: 18px;
                padding: 1.5rem 1.5rem 1.1rem 1.5rem;
                color: white;
                box-shadow: 0 18px 30px -18px rgba(15, 23, 42, 0.6);
                margin-bottom: 1.25rem;
                border: 1px solid rgba(255,255,255,0.08);
            }
            .page-title {
                font-size: clamp(1.6rem, 2vw, 2.4rem);
                font-weight: 800;
                letter-spacing: -0.03em;
                margin-bottom: 0.4rem;
            }
            .page-subtitle {
                color: rgba(255,255,255,0.85);
                font-size: 0.97rem;
                line-height: 1.6;
                max-width: 1100px;
            }
            .badge-row { margin-top: 0.9rem; }
            .badge-pill {
                display: inline-block;
                background: rgba(255,255,255,0.12);
                color: #F8FAFC;
                border: 1px solid rgba(255,255,255,0.16);
                padding: 0.45rem 0.75rem;
                border-radius: 999px;
                font-size: 0.72rem;
                font-weight: 700;
                margin-right: 0.5rem;
                margin-bottom: 0.4rem;
            }
            .section-shell {
                background: rgba(148, 163, 184, 0.04);
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 18px;
                padding: 1rem 1rem 0.5rem;
                margin-bottom: 1rem;
            }
            .kpi-card {
                position: relative;
                background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
                border: 1px solid rgba(148, 163, 184, 0.15);
                border-radius: 18px;
                padding: 1rem 1rem 0.9rem;
                box-shadow: 0 18px 30px -24px rgba(15, 23, 42, 0.5);
                height: 100%;
                overflow: hidden;
            }
            .kpi-stripe { height: 6px; width: 100%; border-radius: 999px; margin-bottom: 0.9rem; }
            .stripe-blue { background: linear-gradient(90deg, #2563EB, #60A5FA); }
            .stripe-purple { background: linear-gradient(90deg, #7C3AED, #A78BFA); }
            .stripe-emerald { background: linear-gradient(90deg, #059669, #34D399); }
            .stripe-amber { background: linear-gradient(90deg, #F59E0B, #FCD34D); }
            .stripe-red { background: linear-gradient(90deg, #EF4444, #FCA5A5); }
            .kpi-title {
                font-size: 0.8rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #475569;
            }
            .kpi-value {
                font-size: clamp(1.5rem, 2.2vw, 2.1rem);
                font-weight: 800;
                color: #0F172A;
                line-height: 1.15;
                margin: 0.5rem 0;
            }
            .kpi-caption {
                font-size: 0.76rem;
                color: #64748B;
            }
            .story-box {
                background: rgba(14, 165, 233, 0.04);
                border-left: 4px solid #0EA5E9;
                border-radius: 14px;
                padding: 0.8rem 1rem;
                color: #0F172A;
                margin-bottom: 1rem;
            }
            .story-box-amber { background: rgba(245, 158, 11, 0.05); border-left-color: #F59E0B; }
            .story-box-emerald { background: rgba(16, 185, 129, 0.05); border-left-color: #10B981; }
            .action-card {
                background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 14px;
                padding: 0.85rem 0.9rem;
                box-shadow: 0 14px 28px -26px rgba(15, 23, 42, 0.5);
                margin-bottom: 0.75rem;
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
                    <div style="font-size:0.72rem; font-weight:700; color:#2563EB; text-transform:uppercase;">Overview</div>
                    <div style="font-weight:800; font-size:1.1rem; color:#0F172A; margin:0.3rem 0;">Executive health</div>
                    <div style="color:#475569;">Monitor productivity, workload, attendance, and strategic signals across the workforce.</div>
                </div>
                <div class="action-card">
                    <div style="font-size:0.72rem; font-weight:700; color:#7C3AED; text-transform:uppercase;">Allocation</div>
                    <div style="font-weight:800; font-size:1.1rem; color:#0F172A; margin:0.3rem 0;">Rebalance capacity</div>
                    <div style="color:#475569;">Flag overworked teams and surface underused talent ready for reallocation.</div>
                </div>
                <div class="action-card">
                    <div style="font-size:0.72rem; font-weight:700; color:#059669; text-transform:uppercase;">Risk</div>
                    <div style="font-weight:800; font-size:1.1rem; color:#0F172A; margin:0.3rem 0;">AI talent risk</div>
                    <div style="color:#475569;">Assess attrition signals, burnout pressure, and productivity forecast scenarios.</div>
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
