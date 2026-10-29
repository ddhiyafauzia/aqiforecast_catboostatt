"""Home: introduction, dataset description and business understanding."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from aqi.config import AQI_STATIONS, BASE_DIR, HERO_IMAGE, METEO_STATIONS
from aqi.content import (BUSINESS_CLOSING, BUSINESS_PILLARS, BUSINESS_UNDERSTANDING, DATASET_AQI,
                         DATASET_METEO, HOME_FACTS, INTRODUCTION, WHO_REFERENCE)
from aqi.ui import card_row, interactive_hero, nav, page_header, show_table


def render_home() -> None:
    page_header("home", "Home", "Spatiotemporal AQI modeling for DKI Jakarta")
    section = nav(["Introduction", "Dataset", "Business Understanding"], key="home_nav")
    {"Introduction": _introduction, "Dataset": _dataset, "Business Understanding": _business}[section]()


def _introduction() -> None:
    interactive_hero()
    card_row([(label, detail, value) for label, value, detail in HOME_FACTS])
    st.write("")

    photo = BASE_DIR / HERO_IMAGE
    if photo.exists():
        st.image(str(photo), caption="View of Jakarta City, DKI Jakarta")

    st.markdown(INTRODUCTION)

    st.subheader("WHO reference values")
    show_table(pd.DataFrame(WHO_REFERENCE, columns=["Parameter", "WHO Reference Value"]))


def _station_table(stations) -> pd.DataFrame:
    return pd.DataFrame(
        [(s["id"], s["name"], s["area"], s["lat"], s["lon"]) for s in stations],
        columns=["ID", "Station", "Area", "Latitude", "Longitude"],
    )


def _dataset() -> None:
    st.subheader("Air Pollution Standard Index (ISPU)")
    st.markdown(DATASET_AQI)
    show_table(_station_table(AQI_STATIONS))

    st.subheader("Global Historical Climatology Network — Hourly (NOAA)")
    st.markdown(DATASET_METEO)
    show_table(_station_table(METEO_STATIONS))


def _business() -> None:
    st.subheader("Business Understanding")
    st.markdown(BUSINESS_UNDERSTANDING)
    card_row([(title, body) for title, body in BUSINESS_PILLARS])
    st.write("")
    st.info(BUSINESS_CLOSING)
