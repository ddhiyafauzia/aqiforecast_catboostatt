"""Spatial analysis: station map and spatiotemporal correlation matrix."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from aqi.config import AQI_STATIONS, METEO_STATIONS, NUMERICAL_FEATURES
from aqi.content import CORRELATION_NOTES
from aqi.services import get_aqi_data
from aqi.theme import HEATMAP_SCALE
from aqi.ui import nav, page_header, show_plot

# Plotly >= 5.24 renamed Scattermapbox -> Scattermap; support both.
_USE_NEW_MAP = hasattr(go, "Scattermap")
_SCATTER_MAP = go.Scattermap if _USE_NEW_MAP else go.Scattermapbox
_MAP_KEY = "map" if _USE_NEW_MAP else "mapbox"


def render_spatial() -> None:
    page_header("map", "Spatial Analysis", "AQI & meteorological stations across Jakarta")
    section = nav(["Spatial Map", "Spatiotemporal Correlation Matrix"], key="spatial_nav")
    (_map if section == "Spatial Map" else _correlation)()


def _station_trace(stations, *, label, unit, colorscale, size, bar_x, text_color, position):
    frame = pd.DataFrame(stations)
    return _SCATTER_MAP(
        lat=frame["lat"], lon=frame["lon"], mode="markers+text",
        text=frame.apply(lambda r: f"{r['name']}<br>{label}: {r['peak']}{unit}", axis=1),
        textposition=position, textfont=dict(size=12, color=text_color),
        marker=dict(size=size, color=frame["peak"], colorscale=colorscale,
                    cmin=frame["peak"].min(), cmax=frame["peak"].max(), showscale=True,
                    colorbar=dict(title=label, x=bar_x, thickness=16)),
        name=f"{label} stations", hoverinfo="text",
    )


def _map() -> None:
    st.subheader("Spatial AQI & meteorological distribution")
    fig = go.Figure()
    fig.add_trace(_station_trace(AQI_STATIONS, label="AQI", unit="", colorscale="RdYlGn_r", size=20,
                                 bar_x=0.88, text_color="black", position="top right"))
    fig.add_trace(_station_trace(METEO_STATIONS, label="Temp", unit="°C", colorscale="Blues", size=16,
                                 bar_x=1.02, text_color="darkblue", position="bottom right"))
    fig.update_layout(**{f"{_MAP_KEY}_style": "carto-positron", f"{_MAP_KEY}_zoom": 10.5,
                         f"{_MAP_KEY}_center": {"lat": -6.2, "lon": 106.82}},
                      margin=dict(r=0, t=10, l=0, b=0),
                      legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5))
    show_plot(fig, height=720)


def _correlation() -> None:
    df = get_aqi_data()
    if df.empty:
        return
    columns = [c for c in NUMERICAL_FEATURES if c in df.columns]
    if len(columns) < 2:
        st.warning("Not enough numerical columns to compute correlations.")
        return

    corr = df[columns].corr(method="pearson")
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale=HEATMAP_SCALE, zmin=-1, zmax=1,
                    aspect="auto", title="Spatiotemporal correlation matrix (Pearson)")
    fig.update_xaxes(tickangle=45, showgrid=False)
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_layout(dragmode="zoom", modebar_add=["zoom", "pan", "resetScale2d"],
                      modebar_remove=["lasso2d", "select2d"])
    show_plot(fig, height=700)

    with st.expander("Interpretation notes", expanded=True):
        st.markdown(CORRELATION_NOTES)
