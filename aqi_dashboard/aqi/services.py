"""Cached data access for the Streamlit app (the only data module that depends on Streamlit)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from aqi.config import DATA_FILE, METEO_DIR
from aqi.data import load_aqi, load_meteorology


@st.cache_data(show_spinner="Loading AQI dataset…")
def _cached_aqi() -> pd.DataFrame:
    return load_aqi(DATA_FILE)


@st.cache_data(show_spinner="Loading meteorology files…")
def _cached_meteorology() -> pd.DataFrame:
    return load_meteorology(METEO_DIR)


def get_aqi_data() -> pd.DataFrame:
    try:
        return _cached_aqi()
    except FileNotFoundError:
        st.error(f"File `{DATA_FILE.name}` not found. Put it in the same folder as `app.py`.")
        return pd.DataFrame()


def get_meteorology_data() -> pd.DataFrame:
    try:
        return _cached_meteorology()
    except FileNotFoundError:
        st.error(f"No CSV files found in the `{METEO_DIR.name}/` folder.")
        return pd.DataFrame()
