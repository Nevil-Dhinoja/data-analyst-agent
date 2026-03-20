import streamlit as st
import os
import glob
from app.agent import analyse
from app.pdf_export import generate_pdf

st.set_page_config(
    page_title="Data Analyst Agent",
    page_icon="📊",
    layout="wide"
)

st.title("Autonomous Data Analyst Agent")
st.caption("Give it a goal — it writes SQL, runs Python, builds charts and exports a PDF report.")

MULTI_GOALS = [
    "What are the top 5 cities by total revenue?",
    "Which product category generates the most revenue? Show a pie chart.",
    "Show monthly revenue trend for the last 12 months and forecast next 3 months.",
    "Segment customers by RFM score and identify Champions vs At Risk customers.",
    "Show the order funnel — how many orders are delivered vs cancelled vs returned?"
]

SINGLE_GOALS = [
    "Find correlations between customer age, product rating, quantity and revenue",
    "Which payment method is most popular by city?",
    "Find the top 5 best-selling products by quantity sold",
    "What age group buys the most Electronics?",
    "Find customers who spent more than 50000 total",
    "Which product category has the highest return rate?",
    "Show revenue breakdown by gender and city"
]

with st.sidebar:
    st.markdown("### Single analysis")
    for g in SINGLE_GOALS:
        if st.button(g, use_container_width=True):
            st.session_state.goal = g

    st.divider()
    st.markdown("### Full business report")
    st.caption("Runs 5 analyses automatically and bundles into one PDF")
    run_full = st.button("Run Full Report", type="primary",
                         use_container_width=True)

if "history" not in st.session_state:
    st.session_state.history = []
if "goal" not in st.session_state:
    st.session_state.goal = ""

goal = st.text_area(
    "Enter your analysis goal:",
    value=st.session_state.goal,
    height=80,
    placeholder="e.g. Segment customers by RFM and find who is At Risk of churning"
)

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    run = st.button("Run Analysis", type="primary")
with col2:
    if st.button("Clear all"):
        st.session_state.history = []
        for f in glob.glob("outputs/*.png"):
            os.remove(f)
        st.rerun()

# Single analysis
if run and goal.strip():
    with st.spinner("Agent is thinking, querying and charting..."):
        report = analyse(goal.strip())
    charts = sorted(glob.glob("outputs/*.png"),
                    key=os.path.getmtime, reverse=True)[:3]
    st.session_state.history.append({
        "goal": goal.strip(),
        "report": report,
        "charts": charts
    })
    st.session_state.goal = ""
    st.rerun()

# Full business report
if run_full:
    all_charts = []
    all_reports = []
    progress = st.progress(0, text="Starting full report...")

    for i, g in enumerate(MULTI_GOALS):
        progress.progress((i) / len(MULTI_GOALS),
                          text=f"Running: {g[:60]}...")
        with st.spinner(f"Analysis {i+1}/5: {g[:50]}..."):
            report = analyse(g)
            charts = sorted(glob.glob("outputs/*.png"),
                            key=os.path.getmtime, reverse=True)[:2]
            all_reports.append(f"## Goal {i+1}: {g}\n\n{report}")
            all_charts.extend(charts)
            st.session_state.history.append({
                "goal": g,
                "report": report,
                "charts": charts
            })

    progress.progress(1.0, text="Generating PDF...")
    combined = "\n\n---\n\n".join(all_reports)
    pdf_path = generate_pdf("Full Business Report", combined,
                            list(dict.fromkeys(all_charts)))
    progress.empty()

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="Download Full Report PDF",
            data=f,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf"
        )
    st.rerun()

# Display history
for item in reversed(st.session_state.history):
    with st.expander(f"{item['goal']}", expanded=True):
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown(item["report"])

            # PDF download for single analysis
            if st.button("Export as PDF", key=f"pdf_{item['goal'][:20]}"):
                pdf_path = generate_pdf(
                    item["goal"], item["report"], item["charts"]
                )
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="Download PDF",
                        data=f,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf",
                        key=f"dl_{item['goal'][:20]}"
                    )
        with col2:
            if item["charts"]:
                for chart in item["charts"]:
                    if os.path.exists(chart):
                        st.image(chart, use_container_width=True)
            else:
                st.info("No charts for this analysis.")