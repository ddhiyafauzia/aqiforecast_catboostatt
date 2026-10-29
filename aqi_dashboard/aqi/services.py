"""Cached data access for the Streamlit app (the only data module that depends on Streamlit)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from pathlib import Path

from aqi.config import BASE_DIR, DATA_FILE, METEO_DIR
from aqi.data import load_aqi, load_meteorology, locate_file


@st.cache_data(show_spinner="Loading AQI dataset…")
def _cached_aqi() -> pd.DataFrame:
    path = locate_file(DATA_FILE.name, [BASE_DIR, Path.cwd()])
    if path is None:
        raise FileNotFoundError(DATA_FILE.name)
    return load_aqi(path)


@st.cache_data(show_spinner="Loading meteorology files…")
def _cached_meteorology() -> pd.DataFrame:
    return load_meteorology(METEO_DIR)


def get_aqi_data() -> pd.DataFrame:
    try:
        return _cached_aqi()
    except FileNotFoundError:
        st.error(f"File `{DATA_FILE.name}` not found. Looked in `{BASE_DIR}` and `{BASE_DIR / 'data'}`.")
        return pd.DataFrame()


def get_meteorology_data() -> pd.DataFrame:
    try:
        return _cached_meteorology()
    except FileNotFoundError:
        st.error(f"No CSV files found in the `{METEO_DIR.name}/` folder.")
        return pd.DataFrame()
