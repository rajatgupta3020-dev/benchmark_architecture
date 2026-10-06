from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from benchmark_engine import calculate_metrics, make_benchmark_returns

st.set_page_config(
    page_title="Benchmark Architect | Performance Truth Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Demo data: deterministic, synthetic, educational only.
# -----------------------------

rng = np.random.default_rng(42)
dates = pd.date_range("2023-01-31", periods=36, freq="ME")

market = rng.normal(0.010, 0.035, len(dates))
size = rng.normal(0.002, 0.018, len(dates))
value = rng.normal(0.002, 0.016, len(dates))
quality = rng.normal(0.001, 0.012, len(dates))
noise = rng.normal(0.0, 0.008, (len(dates), 6))

index_returns = pd.DataFrame(
    {
        "Nifty 50": market + noise[:, 0],
        "Nifty 100": 0.95 * market + noise[:, 1],
        "Nifty Midcap 150": 0.72 * market + 0.75 * size + noise[:, 2],
        "Nifty Smallcap 250": 0.55 * market + 1.10 * size + noise[:, 3],
        "Nifty 500 Value 50": 0.88 * market + 0.90 * value + noise[:, 4],
        "Nifty 100 Quality 30": 0.90 * market + 0.80 * quality + noise[:, 5],
    },
    index=dates,
)

# Portfolio is intentionally generated from a hidden benchmark recipe plus manager alpha.
true_weights = {"Nifty 100": 0.50, "Nifty Midcap 150": 0.30, "Nifty 500 Value 50": 0.20}
portfolio_returns = make_benchmark_returns(index_returns, true_weights)
portfolio_returns = portfolio_returns + rng.normal(0.0010, 0.006, len(dates))
portfolio_returns.name = "Apex Growth PMS"

portfolio_info = {
    "Manager": "Apex Growth PMS",
    "Mandate": "Large & Mid Cap with Value Tilt",
    "Assets under management": "₹250 crore (demo)",
    "Current stated benchmark": "Nifty 50",
    "Investment horizon": "Long term",
}

explanation = {
    "R²": "How much of the portfolio's movement is explained by the benchmark. Higher usually means a better statistical fit.",
    "Tracking Error": "How much the portfolio typically moves away from the benchmark. Lower means a closer match.",
    "Information Ratio": "Active return earned for each unit of tracking error. Higher is generally better.",
    "Beta": "How sensitive the portfolio is to benchmark movements. Around 1 means similar market sensitivity.",
    "Alpha": "The part of return left after accounting for benchmark sensitivity in this simplified model.",
}

# -----------------------------
# Session state
# -----------------------------

if "xp" not in st.session_state:
    st.session_state.xp = 0
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "best_score" not in st.session_state:
    st.session_state.best_score = 0

# -----------------------------
# Styling
# -----------------------------

st.markdown(
    """
    <style>
    .main-title {font-size: 2.4rem; font-weight: 750; margin-bottom: 0.1rem;}
    .subtitle {font-size: 1.05rem; color: #666; margin-bottom: 1.2rem;}
    .mission {padding: 1rem 1.1rem; border-radius: 12px; border: 1px solid #ddd; background: #fafafa;}
    .metric-note {font-size: 0.82rem; color: #666; margin-top: -0.4rem;}
    .score-box {padding: 1rem; border-radius: 12px; border: 1px solid #ddd; text-align: center;}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Header
# -----------------------------

st.markdown('<div class="main-title">🎯 Benchmark Architect</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">The Performance Truth Engine · Learn to build a benchmark that measures genuine manager skill.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Your profile")
    player_name = st.text_input("Player name", value="Benchmark Architect")
    st.divider()
    st.metric("XP", st.session_state.xp)
    st.metric("Best score", f"{st.session_state.best_score:,} / 1,000")
    st.metric("Attempts", st.session_state.attempts)
    st.divider()
    st.caption("This MVP uses synthetic Indian market-style data for demonstration. It is not investment advice and does not use live index data.")

# -----------------------------
# Mission
# -----------------------------

st.markdown(
    """
    <div class="mission">
    <b>LEVEL 1 · THE MARKET MATCHER</b><br><br>
    A client says the Apex Growth PMS manager created strong returns against the Nifty 50.
    Your job is to decide whether Nifty 50 is actually a fair benchmark.
    <br><br>
    <b>Your mission:</b> build a custom benchmark that better represents what the manager actually owns and the style they follow.
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

info_cols = st.columns(5)
for col, (label, value) in zip(info_cols, portfolio_info.items()):
    col.metric(label, value)

# -----------------------------
# Baseline benchmark
# -----------------------------

baseline = make_benchmark_returns(index_returns, {"Nifty 50": 1.0})
baseline.name = "Nifty 50"
baseline_metrics = calculate_metrics(portfolio_returns, baseline)

st.subheader("1. First, understand the existing benchmark")
st.write("The current benchmark is Nifty 50. Compare it with the portfolio before changing anything.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("R²", f"{baseline_metrics.r_squared:.2f}")
c2.metric("Tracking error", f"{baseline_metrics.tracking_error:.2%}")
c3.metric("Beta", f"{baseline_metrics.beta:.2f}")
c4.metric("Active return", f"{baseline_metrics.active_return:.2%}")

with st.expander("What do these numbers mean?"):
    for metric_name, text_value in explanation.items():
        st.markdown(f"**{metric_name}:** {text_value}")

# -----------------------------
# Benchmark builder
# -----------------------------

st.subheader("2. Build your custom benchmark")
st.write("Choose up to three index components. The weights are automatically normalized to 100%.")

available = list(index_returns.columns)
component_options = ["None"] + available

c1, c2, c3 = st.columns(3)
with c1:
    comp1 = st.selectbox("Component 1", component_options, index=available.index("Nifty 100") + 1)
    w1 = st.slider("Weight 1", 0, 100, 50, 5, disabled=(comp1 == "None"))
with c2:
    comp2 = st.selectbox("Component 2", component_options, index=available.index("Nifty Midcap 150") + 1)
    w2 = st.slider("Weight 2", 0, 100, 30, 5, disabled=(comp2 == "None"))
with c3:
    comp3 = st.selectbox("Component 3", component_options, index=available.index("Nifty 500 Value 50") + 1)
    w3 = st.slider("Weight 3", 0, 100, 20, 5, disabled=(comp3 == "None"))

raw_weights = {}
for component, weight in [(comp1, w1), (comp2, w2), (comp3, w3)]:
    if component != "None" and weight > 0:
        raw_weights[component] = raw_weights.get(component, 0) + weight

if not raw_weights:
    st.warning("Choose at least one component with a positive weight.")
    st.stop()

weight_total = sum(raw_weights.values())
weights = {k: v / weight_total for k, v in raw_weights.items()}
benchmark_returns = make_benchmark_returns(index_returns, weights)
benchmark_returns.name = "Your Custom Benchmark"
metrics = calculate_metrics(portfolio_returns, benchmark_returns)

st.markdown("**Your normalized benchmark:** " + " · ".join(f"{name}: {weight:.0%}" for name, weight in weights.items()))

# -----------------------------
# Visual comparison
# -----------------------------

st.subheader("3. Watch the benchmark quality change")

chart = go.Figure()
chart.add_trace(go.Scatter(x=dates, y=(1 + portfolio_returns).cumprod(), mode="lines", name="Portfolio"))
chart.add_trace(go.Scatter(x=dates, y=(1 + benchmark_returns).cumprod(), mode="lines", name="Your benchmark"))
chart.update_layout(height=430, margin=dict(l=20, r=20, t=20, b=20), yaxis_title="Growth of ₹1", xaxis_title="", legend=dict(orientation="h"))
st.plotly_chart(chart, use_container_width=True)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("R²", f"{metrics.r_squared:.2f}", f"{metrics.r_squared - baseline_metrics.r_squared:+.2f}")
m2.metric("Tracking error", f"{metrics.tracking_error:.2%}", f"{metrics.tracking_error - baseline_metrics.tracking_error:+.2%}", delta_color="inverse")
m3.metric("Information ratio", f"{metrics.information_ratio:.2f}")
m4.metric("Beta", f"{metrics.beta:.2f}")
m5.metric("Alpha", f"{metrics.alpha:.2%}")

st.write(f"**Benchmark assessment:** {metrics.fit_band}")

# -----------------------------
# Scoring
# -----------------------------

st.subheader("4. Your architect score")
col1, col2 = st.columns([1, 2])
with col1:
    st.markdown('<div class="score-box">', unsafe_allow_html=True)
    st.metric("Score", f"{metrics.score:,} / 1,000")
    st.markdown(f"**{player_name}**")
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.progress(metrics.score / 1000)
    st.write("The MVP score rewards three things: how well the benchmark explains portfolio movement, how closely it tracks the portfolio, and whether its market sensitivity is reasonably aligned.")

if st.button("Submit Mission", type="primary"):
    st.session_state.attempts += 1
    st.session_state.best_score = max(st.session_state.best_score, metrics.score)
    earned = int(round(metrics.score * 0.75))
    st.session_state.xp += earned
    st.success(f"Mission submitted. You earned {earned} XP.")

# -----------------------------
# Explain the result in plain English
# -----------------------------

st.subheader("5. Explain your decision")

if metrics.r_squared >= baseline_metrics.r_squared + 0.10:
    verdict = "Your benchmark explains the portfolio much better than the original Nifty 50 benchmark."
elif metrics.r_squared > baseline_metrics.r_squared:
    verdict = "Your benchmark improves the statistical fit, but the improvement is modest."
else:
    verdict = "Your benchmark does not improve the statistical fit. Try different components or weights."

st.info(
    f"**Plain-English verdict:** {verdict} "
    "Remember: a high score alone does not prove manager skill. A fair benchmark should represent the strategy before we call excess return alpha."
)

with st.expander("See the calculation logic"):
    st.markdown("**R²:** squared correlation between monthly portfolio and benchmark returns in this MVP.")
    st.markdown("**Tracking error:** standard deviation of monthly active returns, annualized by √12.")
    st.markdown("**Information ratio:** annualized active return ÷ annualized tracking error.")
    st.markdown("**Beta:** covariance of portfolio and benchmark ÷ benchmark variance.")
    st.markdown("**Alpha:** simplified annualized regression intercept using portfolio and benchmark monthly returns.")

st.caption("Next build stage: holdings-based style analysis, sector exposure matching, benchmark appropriateness checks, benchmark-gaming cases, and Brinson attribution.")
