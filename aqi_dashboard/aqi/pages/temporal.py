"""Temporal analysis: annual, hourly and peak trends."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from aqi.config import METEO_FEATURES, POLLUTANTS
from aqi.data import annual_profile, find_peak, hourly_profile, standardize_columns, to_long
from aqi.services import get_aqi_data, get_meteorology_data
from aqi.ui import nav, page_header, show_plot


_TRENDS = ["Annual Trend", "Hourly Trend", "Peak Trend"]


def render_temporal() -> None:
    page_header("clock", "Temporal Analysis", "Air quality & meteorology over time")
    source = nav(["AQI Trends", "Meteorology Trends"], key="temporal_source")

    if source == "AQI Trends":
        raw, params, default, key = get_aqi_data(), POLLUTANTS, ["PM2.5", "PM10"], "aqi"
    else:
        raw, params, default, key = get_meteorology_data(), METEO_FEATURES, ["dew_point_temperature", "relative_humidity"], "meteo"
    if raw.empty:
        return

    long = to_long(standardize_columns(raw), params)
    available = [p for p in params if p in set(long["parameter"])]
    if not available:
        st.warning("None of the expected parameters were found in this dataset.")
        return

    trend = nav(_TRENDS, key=f"{key}_trend")
    selected = st.multiselect("Parameters", available, default=[p for p in default if p in available], key=f"{key}_params")
    if not selected:
        st.info("Select at least one parameter.")
        return

    {"Annual Trend": _annual, "Hourly Trend": _hourly, "Peak Trend": _peak}[trend](long, selected)


def _annual(long: pd.DataFrame, parameters) -> None:
    for parameter in parameters:
        profile = annual_profile(long, parameter)
        profile["year"] = profile["year"].astype(str)
        fig = px.line(profile, x="plot_date", y="value", color="year", title=f"Annual trend of {parameter}",
                      labels={"plot_date": "", "value": parameter, "year": "Year"})
        fig.update_xaxes(tickformat="%b", dtick="M1")
        show_plot(fig, height=420)


def _hourly(long: pd.DataFrame, parameters) -> None:
    hourly = hourly_profile(long, parameters)
    hourly["year"] = hourly["year"].astype(str)
    fig = px.line(hourly, x="hour", y="value", color="year", facet_col="parameter", facet_col_wrap=2,
                  markers=True, title="Hourly trend (mean by hour of day)",
                  labels={"hour": "Hour", "value": "Value", "year": "Year"})
    fig.update_yaxes(matches=None, showticklabels=True)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    show_plot(fig, height=max(420, 320 * -(-len(parameters) // 2)))


def _peak(long: pd.DataFrame, parameters) -> None:
    for parameter in parameters:
        subset = long[long["parameter"] == parameter]
        peak = find_peak(subset)
        if peak is None:
            st.warning(f"No valid values for {parameter}.")
            continue
        date, value = peak
        fig = go.Figure()
        fig.add_trace(go.Scattergl(x=subset["date"], y=subset["value"], mode="lines", name=parameter,
                                   line=dict(width=1, color="#94A3B8")))
        fig.add_trace(go.Scatter(x=[date], y=[value], mode="markers", name=f"Peak {value:.1f} on {date.date()}",
                                 marker=dict(size=12, color="#DC2626", line=dict(width=2, color="white"))))
        fig.update_layout(title=f"Peak trend of {parameter}", yaxis_title=parameter)
        show_plot(fig, height=420)
