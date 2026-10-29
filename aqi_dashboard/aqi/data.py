"""Loading, cleaning and reshaping of the AQI and meteorology datasets (pure pandas, no UI)."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Tuple

import numpy as np
import pandas as pd

from aqi.config import METEO_COLUMNS_TO_KEEP, STATION_LABELS

NO_DATA = "NO DATA"
EXCLUDED_CATEGORIES = {NO_DATA, "TIDAK ADA DATA"}
CATEGORY_ORDER = ("GOOD", "MODERATE", "UNHEALTHY", "VERY UNHEALTHY", "HAZARDOUS")
_CATEGORY_THRESHOLDS = ((50, "GOOD"), (100, "MODERATE"), (150, "UNHEALTHY"), (200, "VERY UNHEALTHY"))

TIME_COLUMNS = ["date", "year", "month", "month_day", "hour"]

AQI_RENAME_MAP = {
    "pm_sepuluh": "PM10", "pm_duakomalima": "PM2.5", "pm_10": "PM10",
    "pm25": "PM2.5", "pm2.5": "PM2.5", "pm10": "PM10", "so2": "SO2",
    "co": "CO", "o3": "O3", "no2": "NO2",
    "parameter_pencemar_kritis": "Critical", "kategori": "Category",
    "lokasi_spku": "Station", "tanggal": "date", "stasiun": "Station",
}


def load_aqi(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["tanggal"])


def load_meteorology(folder: Path) -> pd.DataFrame:
    files = sorted(Path(folder).glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in '{folder}'")

    frames = []
    for file in files:
        frame = pd.read_csv(file, low_memory=False)
        frame.columns = frame.columns.str.lower()
        frames.append(frame)
    df = pd.concat(frames, ignore_index=True)

    df = df[[c for c in METEO_COLUMNS_TO_KEEP if c in df.columns]].copy()
    if "date" not in df.columns:
        raise ValueError("Meteorology files must contain a 'date' column")

    required = [c for c in ("latitude", "longitude", "date") if c in df.columns]
    df = df.dropna(subset=required)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    numeric = df.select_dtypes(include="number").columns
    df[numeric] = df[numeric].fillna(df[numeric].median())
    return df.reset_index(drop=True)


def categorize_pm25(value: float) -> str:
    if pd.isna(value):
        return NO_DATA
    for upper, label in _CATEGORY_THRESHOLDS:
        if value <= upper:
            return label
    return "HAZARDOUS"


def find_column(df: pd.DataFrame, name: str) -> Optional[str]:
    for column in df.columns:
        if str(column).lower() == name.lower():
            return column
    return None


def prepare_categorical(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    if "Category" not in out.columns:
        out["Category"] = out["PM2.5"].apply(categorize_pm25)
    out["Category"] = out["Category"].astype(str).str.upper().str.strip()
    out = out[~out["Category"].isin(EXCLUDED_CATEGORIES)].copy()
    present = [c for c in CATEGORY_ORDER if c in set(out["Category"])]
    extra = sorted(set(out["Category"]) - set(present))
    out["Category"] = pd.Categorical(out["Category"], categories=present + extra, ordered=True)

    station_col = find_column(out, "station")
    if station_col is not None:
        out = out.rename(columns={station_col: "station"})
        out["station"] = out["station"].astype(str).str.strip().map(lambda s: STATION_LABELS.get(s, s))
        out["station"] = pd.Categorical(out["station"], categories=list(STATION_LABELS.values()), ordered=True)
    return out


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = out.columns.str.lower()
    out = out.rename(columns=AQI_RENAME_MAP)
    out = out.loc[:, ~out.columns.duplicated()]
    if "date" not in out.columns:
        raise KeyError("Expected a 'date' (or 'tanggal') column")

    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out = out.dropna(subset=["date"]).copy()
    out["year"] = out["date"].dt.year
    out["month"] = out["date"].dt.month
    out["month_day"] = out["date"].dt.strftime("%m-%d")
    out["hour"] = out["date"].dt.hour
    return out


def to_long(df: pd.DataFrame, value_vars: Iterable[str], value_name: str = "value") -> pd.DataFrame:
    valid = [v for v in value_vars if v in df.columns]
    if not valid:
        return pd.DataFrame(columns=TIME_COLUMNS + ["parameter", value_name])
    return df.melt(id_vars=TIME_COLUMNS, value_vars=valid, var_name="parameter", value_name=value_name)


def annual_profile(long_df: pd.DataFrame, parameter: str) -> pd.DataFrame:
    subset = long_df[long_df["parameter"] == parameter]
    profile = subset.groupby(["year", "month_day"], as_index=False)["value"].mean()
    profile["plot_date"] = pd.to_datetime("2000-" + profile["month_day"], format="%Y-%m-%d")
    return profile.sort_values(["year", "plot_date"]).reset_index(drop=True)


def hourly_profile(long_df: pd.DataFrame, parameters: Iterable[str]) -> pd.DataFrame:
    subset = long_df[long_df["parameter"].isin(list(parameters))]
    return subset.groupby(["hour", "year", "parameter"], as_index=False)["value"].mean()


def find_peak(df: pd.DataFrame, value_col: str = "value") -> Optional[Tuple[pd.Timestamp, float]]:
    valid = df.dropna(subset=[value_col])
    if valid.empty:
        return None
    row = valid.iloc[valid[value_col].to_numpy().argmax()]
    return row["date"], float(row[value_col])
