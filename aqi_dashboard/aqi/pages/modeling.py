"""Modeling and evaluation: leaderboard, model comparison, predictions and insights."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from aqi.content import FINDINGS, METRIC_DEFINITIONS, MODEL_INSIGHTS
from aqi.models import (METRICS, SAMPLE_COLUMNS, TRUE_AQI, build_model_results, leaderboard_bars,
                        prediction_samples, summarize_models)
from aqi.ui import card_row, leaderboard, metric_row, page_header, show_plot, show_table


_FORMATS = {
    "RMSE": st.column_config.NumberColumn("RMSE", format="%.4f"),
    "MAE": st.column_config.NumberColumn("MAE", format="%.4f"),
    "MAPE": st.column_config.NumberColumn("MAPE", format="%.3f"),
    "train_time": st.column_config.NumberColumn("Train time (s)", format="%.1f"),
}


def render_modeling() -> None:
    results = build_model_results()
    summary = summarize_models(results)
    page_header("cpu", "Modeling & Evaluation", "Performance of prediction models across window lengths")

    best, fastest = summary.iloc[0], summary.sort_values("train_time").iloc[0]
    metric_row([
        ("Best model (mean RMSE)", best["model"], "Lowest mean RMSE over the windows evaluated"),
        ("Mean RMSE", f"{best['RMSE']:.4f}"),
        ("Fastest to train", fastest["model"], f"{fastest['train_time']:.2f} s on average"),
        ("Models evaluated", str(len(summary))),
    ])
    st.write("")

    overview, compare, samples, insights = st.tabs(
        ["Overview", "Compare models", "Actual vs predicted", "Insights"])
    with overview:
        _overview(results, summary)
    with compare:
        _compare(results)
    with samples:
        _samples(results)
    with insights:
        _insights()


def _animated_leaderboard(results):
    """RMSE per model that animates across window lengths (press Play)."""
    frame = results.sort_values("window")
    fig = px.bar(frame, x="model", y="RMSE", color="model", animation_frame="window",
                 range_y=[0, frame["RMSE"].max() * 1.1],
                 title="RMSE by model across window lengths (press Play)",
                 labels={"RMSE": "RMSE", "model": "", "window": "Window (h)"})
    fig.update_layout(showlegend=False)
    for button in fig.layout.updatemenus[0].buttons:
        button.args[1]["frame"]["duration"] = 800
        button.args[1]["transition"]["duration"] = 500
    return fig


def _overview(results, summary) -> None:
    leaderboard(leaderboard_bars(results, "RMSE"), "Leaderboard · mean RMSE (log scale, lower is better)")
    show_plot(_animated_leaderboard(results), height=460)
    st.markdown("##### Leaderboard table (mean over evaluated windows)")
    show_table(summary.rename(columns={"model": "Model", "windows": "Windows"}),
               column_config=_FORMATS)
    with st.expander("Full results (every model × window)"):
        show_table(results.drop(columns=["True"]), column_config=_FORMATS)


def _compare(results) -> None:
    left, right = st.columns(2)
    models = left.multiselect("Models", sorted(results["model"].unique()), default=["LightGBM Attention"],
                              help="Select one or more models to compare.")
    metric = right.selectbox("Metric", METRICS, help="Metric to visualize.")
    if not models:
        st.warning("Please select at least one model.")
        return
    filtered = results[results["model"].isin(models)]
    fig = px.line(filtered, x="window", y=metric, color="model", markers=True,
                  title=f"{metric} vs window length",
                  labels={"window": "Window length (h)", metric: metric, "model": "Model"})
    fig.update_xaxes(type="category")
    show_plot(fig, height=460)


def _samples(results) -> None:
    left, right = st.columns(2)
    models = left.multiselect("Models to compare", sorted(results["model"].unique()),
                              default=["LightGBM Attention", "CatBoost"], key="sample_models")
    window = right.selectbox("Window length (h)", sorted(results["window"].unique()), key="sample_window")
    chosen = prediction_samples(results, models, window)

    missing = sorted(set(models) - set(chosen["model"]))
    if missing:
        st.info(f"No {window} h result for: {', '.join(missing)}.")
    if chosen.empty:
        st.warning("No data for the selected model(s) and window.")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=SAMPLE_COLUMNS, y=[TRUE_AQI] * 3, mode="lines+markers",
                             name=f"Actual (AQI = {TRUE_AQI:.0f})",
                             line=dict(color="#F59E0B", width=3, dash="dot")))
    for _, row in chosen.iterrows():
        fig.add_trace(go.Scatter(x=SAMPLE_COLUMNS, y=[row[c] for c in SAMPLE_COLUMNS], mode="lines+markers",
                                 name=f"{row['model']} ({window} h)"))
    fig.update_layout(title=f"Actual vs predicted AQI — {window} h window",
                      xaxis_title="Sample", yaxis_title="AQI")
    show_plot(fig, height=460)
    show_table(chosen)


def _insights() -> None:
    st.markdown("##### Model-by-model analysis")
    for name, text in MODEL_INSIGHTS.items():
        with st.expander(f"{name}"):
            st.markdown(text)

    st.markdown("##### Summary of findings")
    card_row([(title, body, tag) for title, tag, body in FINDINGS[:3]])
    st.write("")
    card_row([(title, body, tag) for title, tag, body in FINDINGS[3:]])

    st.markdown("##### Metric definitions")
    for name, text in METRIC_DEFINITIONS:
        st.markdown(f"- **{name}:** {text}")
