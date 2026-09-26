import streamlit as st

from app.page_shared import configure_app, get_filtered_workforce, render_empty_state, render_page_header
from app.utils import create_completion_distribution_plot, create_hours_distribution_plot, create_seaborn_distributions


configure_app(page_title="Workload & Performance Analytics")
render_page_header(
    title="Workload & Performance Analytics",
    subtitle="Examine how task completion and weekly workload vary across employees to detect systemic stress, productivity drag, and workplace imbalance patterns.",
    badges=["📈 Distribution Analysis", "⏱️ Workload Trends", "📊 Performance Signals"],
)

df_raw, df = get_filtered_workforce()
if df.empty:
    render_empty_state()

st.markdown("### Distribution View")
view = st.radio("Choose your analytical lens:", ["Interactive Plotly Distributions", "Static Seaborn KDE Report"], horizontal=True)

if view == "Interactive Plotly Distributions":
    left, right = st.columns(2)
    with left:
        st.plotly_chart(create_hours_distribution_plot(df), use_container_width=True)
    with right:
        st.plotly_chart(create_completion_distribution_plot(df), use_container_width=True)
else:
    fig = create_seaborn_distributions(df)
    st.pyplot(fig)

st.markdown("### What this means")
st.markdown(
    """
    <div class="story-box">
        High variance in weekly work hours often signals uneven task allocation or unsustainable overtime. Similarly, clusters of low task completion rates can reveal deeper operational bottlenecks, role mismatch, or burnout risk requiring intervention.
    </div>
    """,
    unsafe_allow_html=True,
)
