"""Statistical tests: paired t-test, Friedman and Nemenyi post-hoc."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from aqi.models import build_model_results
from aqi.stats import (MIN_PAIRS_FOR_TTEST, complete_cases, friedman_test, mean_ranks, metric_pivot,
                       nemenyi_matrix, pairwise_ttest_matrix)
from aqi.ui import metric_row, page_header, show_plot


_METRICS = ("RMSE", "MAE", "MAPE")


def _heatmap(matrix: pd.DataFrame, title: str, scale: str):
    fig = px.imshow(matrix, text_auto=".3f", color_continuous_scale=scale, zmin=0, zmax=1, aspect="auto",
                    title=title, labels=dict(color="p-value"))
    fig.update_xaxes(tickangle=40)
    return fig


def render_stat_test() -> None:
    page_header("chart", "Statistical Test", "Is the difference between models statistically significant?")
    results = build_model_results()

    tab_t, tab_f = st.tabs(["Paired t-test", "Friedman + Nemenyi"])
    with tab_t:
        _pairwise(results)
    with tab_f:
        _friedman(results)
    st.caption("p-values < 0.05 indicate statistically significant differences between model pairs.")


def _pairwise(results: pd.DataFrame) -> None:
    st.caption(f"Windows are paired by length; pairs with fewer than {MIN_PAIRS_FOR_TTEST} shared windows "
               "(e.g. Transformer) are left blank.")
    metric = st.radio("Metric", _METRICS, horizontal=True, key="ttest_metric")
    matrix = pairwise_ttest_matrix(metric_pivot(results, metric))
    show_plot(_heatmap(matrix, f"Pairwise t-test p-values ({metric})", "RdYlGn"), height=560)


def _friedman(results: pd.DataFrame) -> None:
    metric = st.selectbox("Metric", _METRICS, key="friedman_metric")
    pivot, excluded = complete_cases(metric_pivot(results, metric))
    if excluded:
        st.info("Excluded (missing results for some windows): " + ", ".join(excluded))

    try:
        result = friedman_test(pivot)
        nemenyi = nemenyi_matrix(pivot)
    except ValueError as error:
        st.warning(str(error))
        return

    metric_row([("Friedman χ²", f"{result.statistic:.3f}"), ("p-value", f"{result.p_value:.4g}"),
                ("Windows × models", f"{result.n_windows} × {result.n_models}")])
    if result.is_significant():
        st.success("Significant difference between models (p < 0.05)")
    else:
        st.info("No significant difference detected between models (p ≥ 0.05)")

    ranks = mean_ranks(pivot).rename("mean rank").reset_index()
    show_plot(px.bar(ranks, x="model", y="mean rank", text_auto=".2f",
                     title=f"Mean rank per model ({metric}, lower is better)"), height=360)
    show_plot(_heatmap(nemenyi, f"Post-hoc Nemenyi p-values ({metric})", "YlGnBu"), height=560)
