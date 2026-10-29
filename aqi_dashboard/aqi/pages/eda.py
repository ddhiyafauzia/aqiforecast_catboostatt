"""Exploratory data analysis: schema, numerical and categorical distributions."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from aqi.config import NUMERICAL_FEATURES
from aqi.content import AQI_ROWS, AQI_SCHEMA, METEO_ROWS, METEO_SCHEMA
from aqi.data import prepare_categorical
from aqi.services import get_aqi_data
from aqi.ui import metric_row, nav, page_header, show_plot, show_table


def render_eda() -> None:
    page_header("search", "Exploratory Data Analysis", "Schema, distributions and categories")
    section = nav(["Data Type Analysis", "Numerical Data", "Categorical Data"], key="eda_nav")
    if section == "Data Type Analysis":
        _data_types()
        return

    df = get_aqi_data()
    if df.empty:
        return
    (_numerical if section == "Numerical Data" else _categorical)(df)


def _data_types() -> None:
    total = AQI_ROWS + METEO_ROWS
    metric_row([("AQI rows", f"{AQI_ROWS:,}"), ("Meteorology rows", f"{METEO_ROWS:,}"),
                ("Total processed rows", f"{total:,}", "Hourly AQI measurements + meteorological variables")])
    st.write("")
    left, right = st.columns(2)
    with left:
        st.markdown("##### Air Quality Index")
        show_table(pd.DataFrame(AQI_SCHEMA, columns=["Column", "Dtype"]), height=420)
    with right:
        st.markdown("##### Meteorology (Climatology)")
        show_table(pd.DataFrame(METEO_SCHEMA, columns=["Column", "Dtype"]), height=420)


def _numerical(df: pd.DataFrame) -> None:
    options = [c for c in NUMERICAL_FEATURES if c in df.columns]
    default = [c for c in ("PM2.5", "PM10") if c in options]
    selected = st.multiselect("Numerical features", options, default=default)
    if not selected:
        st.info("Select at least one feature to see its distribution.")
        return

    for left, right in zip(selected[::2], selected[1::2] + [None]):
        columns = st.columns(2)
        for column, feature in zip(columns, (left, right)):
            if feature is None:
                continue
            with column:
                fig = px.histogram(df, x=feature, nbins=30, marginal="box",
                                   title=f"Distribution: {feature}")
                fig.update_traces(marker_line_color="white", marker_line_width=0.6, selector=dict(type="histogram"))
                show_plot(fig, height=380)

    st.subheader("Descriptive statistics")
    show_table(df[selected].describe().T.round(3).reset_index(names="feature"))


def _categorical(df: pd.DataFrame) -> None:
    if "PM2.5" not in df.columns and "Category" not in df.columns:
        st.warning("The dataset has neither a `Category` nor a `PM2.5` column.")
        return
    prepared = prepare_categorical(df)
    options = [c for c in ("station", "Category") if c in prepared.columns]
    selected = st.multiselect("Categorical features", options, default=["Category"] if "Category" in options else options[:1])
    if not selected:
        st.info("Select at least one feature.")
        return

    for column, feature in zip(st.columns(min(len(selected), 2)), selected):
        counts = prepared[feature].value_counts(sort=False).rename_axis(feature).reset_index(name="count")
        with column:
            show_plot(px.bar(counts, x=feature, y="count", text="count", title=f"Distribution: {feature}"), height=400)
