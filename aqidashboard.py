from __future__ import annotations

import html
import warnings
from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import scikit_posthocs as sp
import streamlit as st
from scipy.stats import friedmanchisquare, ttest_rel
from streamlit_option_menu import option_menu


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "aqi_meteo.csv"
METEO_DIR = BASE_DIR / "meteorology"


APP_TITLE = "Spatiotemporal AQI Forecasting Dashboard"
PROJECT_TITLE = "AI for Workforce Intel"
AUTHOR = "Fauzia Dhiyaa' Farros"
UNIVERSITY = "Universitas Sugeng Hartono"
COPYRIGHT_YEAR = 2025

LOGO_FILES = ("university_logo.png", "jktlogo.png")
HERO_IMAGE = "jktimage.jpeg"


POLLUTANTS = ("PM2.5", "PM10", "SO2", "CO", "O3", "NO2")
METEO_FEATURES = (
    "temperature", "dew_point_temperature", "relative_humidity",
    "wind_speed", "wind_direction", "precipitation_24_hour",
    "sea_level_pressure", "visibility",
)
NUMERICAL_FEATURES = POLLUTANTS + METEO_FEATURES

METEO_COLUMNS_TO_KEEP = (
    "station", "station_name", "date", "latitude", "longitude", "elevation",
    "temperature", "dew_point_temperature", "relative_humidity", "wind_speed",
    "wind_direction", "precipitation", "precipitation_24_hour",
    "sea_level_pressure", "visibility",
)


STATION_LABELS = {
    "DKI1": "DKI1 - Bundaran HI",
    "DKI2": "DKI2 - Kelapa Gading",
    "DKI3": "DKI3 - Jagakarsa",
    "DKI4": "DKI4 - Lubang Buaya",
    "DKI5": "DKI5 - Kebon Jeruk",
}

AQI_STATIONS = (
    {"id": "DKI1", "name": "Bundaran HI", "area": "Central Jakarta", "lat": -6.193, "lon": 106.820, "peak": 150},
    {"id": "DKI2", "name": "Kelapa Gading", "area": "North Jakarta", "lat": -6.152, "lon": 106.905, "peak": 287},
    {"id": "DKI3", "name": "Jagakarsa", "area": "South Jakarta", "lat": -6.336, "lon": 106.823, "peak": 120},
    {"id": "DKI4", "name": "Lubang Buaya", "area": "East Jakarta", "lat": -6.289, "lon": 106.903, "peak": 191},
    {"id": "DKI5", "name": "Kebon Jeruk", "area": "West Jakarta", "lat": -6.196, "lon": 106.769, "peak": 65},
)

METEO_STATIONS = (
    {"id": "IDI0000WIHH", "name": "Halim Perdanakusuma", "area": "East Jakarta", "lat": -6.266, "lon": 106.891, "peak": 29.5},
    {"id": "IDU096749-1", "name": "Soekarno Hatta", "area": "Banten", "lat": -6.125, "lon": 106.655, "peak": 31.2},
    {"id": "IDU096745-1", "name": "Jakarta Observatory", "area": "Central Jakarta", "lat": -6.174, "lon": 106.827, "peak": 28.7},
    {"id": "IDU096741-1", "name": "Tanjung Priok", "area": "North Jakarta", "lat": -6.104, "lon": 106.879, "peak": 30.1},
)


st.set_page_config(page_title=f"{APP_TITLE} · AI for Workforce Intel", page_icon="🌍", layout="wide")


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


MIN_PAIRS_FOR_TTEST = 3


@dataclass(frozen=True)
class FriedmanResult:
    statistic: float
    p_value: float
    n_windows: int
    n_models: int

    def is_significant(self, alpha: float = 0.05) -> bool:
        return self.p_value < alpha


def metric_pivot(results: pd.DataFrame, metric: str) -> pd.DataFrame:
    return results.pivot_table(index="window", columns="model", values=metric, aggfunc="mean")


def complete_cases(pivot: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    complete = pivot.dropna(axis=1, how="any")
    excluded = [c for c in pivot.columns if c not in complete.columns]
    return complete, excluded


def pairwise_ttest_matrix(pivot: pd.DataFrame, min_pairs: int = MIN_PAIRS_FOR_TTEST) -> pd.DataFrame:
    models = list(pivot.columns)
    matrix = pd.DataFrame(np.nan, index=models, columns=models)
    for i, a in enumerate(models):
        matrix.loc[a, a] = 1.0
        for b in models[i + 1:]:
            pair = pivot[[a, b]].dropna()
            if len(pair) < min_pairs:
                continue
            with warnings.catch_warnings(), np.errstate(all="ignore"):
                warnings.simplefilter("ignore")
                _, p_value = ttest_rel(pair[a], pair[b])
            matrix.loc[a, b] = matrix.loc[b, a] = p_value
    return matrix


def _validate_block_design(pivot: pd.DataFrame) -> None:
    if pivot.isna().any().any():
        raise ValueError("Pivot contains missing values; run complete_cases() first")
    if pivot.shape[1] < 3:
        raise ValueError("Friedman test needs at least 3 models")
    if pivot.shape[0] < 2:
        raise ValueError("Friedman test needs at least 2 windows")


def friedman_test(pivot: pd.DataFrame) -> FriedmanResult:
    _validate_block_design(pivot)
    statistic, p_value = friedmanchisquare(*[pivot[c].to_numpy() for c in pivot.columns])
    return FriedmanResult(float(statistic), float(p_value), pivot.shape[0], pivot.shape[1])


def nemenyi_matrix(pivot: pd.DataFrame) -> pd.DataFrame:
    _validate_block_design(pivot)
    matrix = sp.posthoc_nemenyi_friedman(pivot.to_numpy())
    matrix.index = pivot.columns
    matrix.columns = pivot.columns
    return matrix


def mean_ranks(pivot: pd.DataFrame) -> pd.Series:
    return pivot.rank(axis=1).mean().sort_values()


TRUE_AQI = 113.0
SAMPLE_COLUMNS = ["Sample 1", "Sample 2", "Sample 3"]
METRICS = ("RMSE", "MAE", "MAPE", "train_time")
COLUMNS = ["model", "window", "RMSE", "MAPE", "MAE", "train_time", "True", *SAMPLE_COLUMNS]


_RECORDS = {
    "LightGBM Attention": [
        (1, 0.048, 0.03, 0.038, 68.30, 112.931, 112.979, 112.930),
        (8, 0.480, 0.41, 0.463, 111.16, 112.628, 112.613, 112.603),
        (12, 0.304, 0.24, 0.271, 140.97, 113.350, 113.345, 113.342),
        (24, 0.242, 0.19, 0.217, 173.08, 112.735, 112.730, 112.728),
        (48, 0.208, 0.11, 0.128, 323.14, 112.870, 112.876, 112.868),
    ],
    "Linear Regression": [
        (1, 0.544, 0.39, 0.437, 0.05, 112.254, 113.841, 112.544),
        (8, 0.045, 0.03, 0.037, 1.84, 113.007, 113.001, 113.001),
        (12, 0.028, 0.02, 0.023, 3.05, 113.011, 113.004, 113.005),
        (24, 0.023, 0.02, 0.019, 2.43, 113.019, 113.020, 113.021),
        (48, 0.004, 0.00, 0.003, 5.96, 113.003, 113.004, 113.002),
    ],
    "Lasso Regression": [
        (1, 0.542, 0.39, 0.435, 1.09, 112.266, 113.840, 112.553),
        (8, 0.041, 0.03, 0.034, 20.30, 113.014, 113.010, 113.011),
        (12, 0.023, 0.02, 0.019, 69.21, 113.017, 113.013, 113.016),
        (24, 0.017, 0.01, 0.014, 428.67, 113.022, 113.021, 113.024),
        (48, 0.002, 0.00, 0.001, 1178.66, 113.002, 113.001, 113.002),
    ],
    "FNN": [
        (1, 0.533, 0.36, 0.412, 30.47, 112.569, 112.795, 112.917),
        (8, 0.804, 0.51, 0.577, 23.99, 113.289, 112.866, 112.403),
        (12, 1.076, 0.71, 0.802, 19.44, 112.756, 113.686, 114.296),
        (24, 1.251, 1.02, 1.148, 42.14, 114.171, 114.084, 113.950),
        (48, 0.881, 0.57, 0.649, 49.70, 112.245, 113.072, 112.576),
    ],
    "CNN–LSTM": [
        (8, 2.666, 2.36, 2.666, 234.01, 110.334, 110.334, 110.334),
        (12, 3.260, 2.89, 3.260, 89.96, 109.740, 109.740, 109.740),
        (24, 3.547, 3.14, 3.547, 127.58, 109.453, 109.453, 109.453),
        (48, 2.633, 2.33, 2.633, 1088.12, 110.367, 110.367, 110.367),
    ],
    "GRU–LSTM": [
        (1, 0.092, 0.03, 0.033, 47.26, 113.012, 113.011, 113.018),
        (8, 0.204, 0.15, 0.174, 326.60, 113.261, 113.261, 113.261),
        (12, 0.217, 0.15, 0.166, 524.57, 112.963, 112.963, 112.963),
        (24, 0.208, 0.18, 0.207, 1119.12, 113.231, 113.231, 113.231),
        (48, 0.043, 0.04, 0.040, 1907.34, 112.958, 112.958, 112.958),
    ],
    "CatBoost": [
        (1, 0.010, 0.01, 0.007, 20.84, 113.010, 113.013, 113.011),
        (8, 0.005, 0.00, 0.003, 41.76, 113.010, 113.011, 113.012),
        (12, 0.004, 0.00, 0.003, 46.89, 113.004, 113.008, 113.004),
        (24, 0.005, 0.00, 0.004, 90.82, 113.009, 113.007, 113.011),
        (48, 0.002, 0.00, 0.002, 175.96, 113.001, 112.999, 112.999),
    ],
    "Transformer": [
        (1, 0.094, 0.07, 0.081, 90.14, 112.938, 112.975, 112.940),
        (8, 0.040, 0.02, 0.022, 125.01, 113.017, 113.011, 113.012),
    ],
}


def build_model_results() -> pd.DataFrame:
    rows = []
    for model, records in _RECORDS.items():
        for window, rmse, mape, mae, seconds, s1, s2, s3 in records:
            rows.append([model, window, rmse, mape, mae, seconds, TRUE_AQI, s1, s2, s3])
    return pd.DataFrame(rows, columns=COLUMNS)


def summarize_models(results: pd.DataFrame) -> pd.DataFrame:
    return (
        results.groupby("model")
        .agg(windows=("window", "nunique"), RMSE=("RMSE", "mean"), MAE=("MAE", "mean"),
             MAPE=("MAPE", "mean"), train_time=("train_time", "mean"))
        .sort_values("RMSE")
        .reset_index()
    )


def prediction_samples(results: pd.DataFrame, models: Iterable[str], window: int) -> pd.DataFrame:
    mask = results["model"].isin(list(models)) & (results["window"] == window)
    return results.loc[mask, ["model", "window", "True", *SAMPLE_COLUMNS]].reset_index(drop=True)


INTRODUCTION = """
In densely populated urban areas like DKI Jakarta, air pollution—especially fine particulate matter
(PM2.5)—poses serious health risks, contributing to bronchitis, asthma, heart disease, stroke, and
even death [1]. The interplay of multiple pollutants, weather variability, traffic emissions, and
industrial activities complicates air quality dynamics [2], [13], prompting recent research to treat
pollution as a spatiotemporal problem rather than isolated measurements [3], [14]. This approach captures
both temporal patterns (e.g., hourly or daily changes) and spatial relationships across monitoring stations.

Traditional statistical methods often fail to model these complex, nonlinear patterns, whereas machine
learning models like Categorical Boosting handle high-dimensional structured data efficiently using
histogram-based binning and a leaf-wise growth strategy [4], [15]. However, Categorical Boosting alone may
not effectively prioritize temporal or environmental features unless explicitly guided. To address this,
attention mechanisms—originally from natural language processing—are now applied in time series forecasting
to emphasize critical features such as sudden weather shifts or pollution spikes [5], [6], [16], [17], [18].
Combining Categorical Boosting with attention improves interpretability and predictive accuracy
[6], [9], [10], [19], [20], though many models remain limited to low-resolution data or single-station
inputs [7], [21].

This study proposes a hybrid attention–Categorical Boosting framework to model multivariate spatiotemporal
correlations of PM2.5 in DKI Jakarta, using hourly climate data from five satellite-derived sources and
pollutant data (PM2.5, PM10, NO₂, SO₂, CO, O₃) from five ground stations (2020–2024). An attention mechanism
is applied after preprocessing and temporal segmentation to highlight key variables at each timestep,
followed by Categorical Boosting to model nonlinear interactions. The method enhances interpretability and
forecasting performance, offering insights for data-driven policymaking and urban air quality management.
"""

HOME_FACTS = (
    ("AQI stations", "5", "Jakarta Environmental Agency"),
    ("Meteorological stations", "4", "NOAA hourly network"),
    ("Pollutants", "6", "PM2.5 · PM10 · SO₂ · CO · O₃ · NO₂"),
    ("Study period", "2020–2024", "Hourly resolution"),
)

WHO_REFERENCE = (
    ("PM2.5", "< 5 μg/m³ (annual)"),
    ("PM10", "< 15 μg/m³ (annual)"),
    ("SO₂", "< 40 μg/m³ (10-min)"),
    ("CO", "< 4 mg/m³ (daily)"),
    ("O₃", "< 100 μg/m³ (8-hour)"),
    ("NO₂", "< 10 μg/m³ (annual)"),
    ("Max", "Depends on pollutant type"),
    ("Category", "Good"),
    ("temperature", "20–25 °C"),
    ("dew_point_temperature", "Depends on air temperature"),
    ("relative_humidity", "40–60%"),
    ("wind_speed", "0–15 m/s"),
    ("wind_direction", "None"),
    ("precipitation", "Seasonal dependent"),
    ("precipitation_24_hour", "Seasonal dependent"),
)

DATASET_AQI = """
The dataset comprises the **Air Pollution Standard Index (ISPU)** collected from **five Air Quality
Monitoring Stations** operated by the Jakarta Environmental Agency.

📂 Public data: [Jakarta Smart City Portal](https://satudata.jakarta.go.id/)
"""

DATASET_METEO = """
The dataset also includes **hourly meteorological data** from NOAA (temperature, precipitation, humidity,
latitude/longitude and elevation), collected from four meteorological stations.

📂 Public data: [Global Historical Climatology Network – Hourly](https://www.ncei.noaa.gov/access/search/data-search/global-historical-climatology-network-hourly)
"""

BUSINESS_UNDERSTANDING = """
This research provides accurate assessments of PM2.5 levels across urban areas, supporting strategies to
control pollution from industry and transportation. By integrating pollutant concentrations with climate
conditions that often exceed WHO-recommended limits, the system can capture both rapid fluctuations and
long-term seasonal patterns.
"""

BUSINESS_PILLARS = (
    ("🚛 Emission Management",
     "Local governments can temporarily restrict heavy trucks or industrial activities when high pollution "
     "levels are predicted."),
    ("🩺 Public Health Advisory",
     "Early alerts when PM2.5 is expected to exceed 5 μg/m³ (annual guideline) can reduce hospital visits for "
     "respiratory problems by 3–5% and save Jakarta Rp 50–100 billion in healthcare costs each year [3]."),
    ("🏙️ Sustainable Urban Planning",
     "Long-term predictions guide low-emission zones, green spaces, and the relocation of sensitive facilities."),
)

BUSINESS_CLOSING = (
    "By linking **spatiotemporal correlations between pollutants and weather elements**, this approach enhances "
    "prediction accuracy and strengthens decision-making for **fast-response systems** in Jakarta's most "
    "vulnerable areas."
)

AQI_SCHEMA = (
    ("periode_data", "int64"), ("tanggal", "datetime64[ns]"), ("PM10", "float64"), ("SO2", "float64"),
    ("CO", "float64"), ("O3", "float64"), ("NO2", "float64"), ("Max", "float64"), ("Critical", "object"),
    ("Category", "object"), ("Station", "object"), ("PM2.5", "float64"), ("sulfur_dioksida", "float64"),
    ("karbon_monoksida", "float64"), ("ozon", "float64"), ("nitrogen_dioksida", "float64"), ("bulan", "float64"),
)
AQI_ROWS = 6966

METEO_SCHEMA = (
    ("station_name", "object"), ("date", "datetime64[ns]"), ("latitude", "float64"), ("longitude", "float64"),
    ("elevation", "float64"), ("temperature", "float64"), ("dew_point_temperature", "float64"),
    ("relative_humidity", "float64"), ("wind_speed", "float64"), ("wind_direction", "float64"),
    ("precipitation", "float64"), ("precipitation_24_hour", "float64"), ("sea_level_pressure", "float64"),
    ("visibility", "float64"),
)
METEO_ROWS = 99231

CORRELATION_NOTES = """
- **Positive correlation (r > 0)** → the value tends to **increase** as the other parameter increases.
- **Negative correlation (r < 0)** → the value tends to **decrease** as the other parameter increases.

**A. Inter-pollutant (AQI vs AQI)**
- **PM2.5 – PM10 (r = 0.69):** strong positive — shared sources such as vehicular emissions, combustion and dust.
- **CO – O₃ (r = 0.38):** moderate positive — CO acts as a precursor in ozone formation.
- **CO – NO₂ (r = 0.32):** moderate — both originate from combustion and traffic.
- **PM2.5 – NO₂ (r = 0.25):** weak to moderate — urban and industrial activity.
- **PM10 – NO₂ (r = 0.23):** weak to moderate — mixed particulate sources.

**B. Inter-meteorological**
- **Temperature – Relative humidity (r = –0.89):** very strong negative — warmer air holds relatively less moisture.
- **Dew point – Relative humidity (r = 0.62):** strong positive — both reflect moisture content.
- **Temperature – Wind speed (r = 0.45):** moderate positive — warm air enhances convective movement.
- **Pressure – Sea-level pressure (r ≈ 0.40–0.50):** moderate — stable atmospheric pressure relationships.

**C. Pollutant–meteorology**
- **CO – Temperature (r = 0.32):** CO rises with temperature (enhanced photochemical reactions).
- **PM2.5 – Visibility (r = 0.25):** fine particles scatter light and reduce visibility.
- **PM10 – Visibility (r = 0.23):** coarse particles show a similar effect.
- **SO₂ – Visibility (r = 0.18):** slight reduction due to aerosol formation.
- **PM10 – Temperature (r = 0.17):** weak positive — possible dust resuspension in warmer conditions.

*Stronger correlations (|r| > 0.6) indicate direct or inverse environmental relationships; weaker ones suggest
indirect or complex interactions.*
"""

MODEL_INSIGHTS = {
    "LightGBM Attention": """
- **Overview:** Hybrid tree-based model enhanced with attention and adaptive weighting.
- **Strengths:** High interpretability, low error (RMSE < 0.5 for all windows) and stable across time steps.
- **Weaknesses:** Slightly higher training time than linear models.
- **Inference:** Predictions stay very close to the true AQI (≈113), showing strong generalization.
- **Best use:** Short- to mid-range forecasting with high accuracy and explainability.
""",
    "Linear Regression": """
- **Overview:** Baseline model for comparison.
- **Strengths:** Fastest training; very stable across window lengths.
- **Weaknesses:** Limited in capturing complex temporal or non-linear dependencies.
- **Performance:** RMSE decreases with longer windows, showing smoother trend learning.
- **Best use:** Quick baselines or limited computational power.
""",
    "Lasso Regression": """
- **Overview:** Linear model with L1 regularization to prevent overfitting.
- **Strengths:** Slightly better stability and sparsity control than plain linear regression.
- **Weaknesses:** Still limited in learning temporal sequences; training time grows quickly with window length.
- **Performance:** Excellent at longer windows (RMSE ≈ 0.002 at 48 h).
- **Best use:** Feature selection or simple AQI estimation pipelines.
""",
    "FNN": """
- **Overview:** Simple deep learning model without temporal memory.
- **Strengths:** Models non-linear dependencies better than linear models.
- **Weaknesses:** Struggles with long-term sequence dependencies.
- **Performance:** Error rises at longer windows, indicating loss of temporal understanding.
- **Best use:** Small-scale AQI patterns or non-sequential data.
""",
    "CNN–LSTM": """
- **Overview:** CNN for feature extraction combined with LSTM for temporal learning.
- **Strengths:** Able to capture spatiotemporal correlations in AQI data.
- **Weaknesses:** High training time and less stable on small datasets.
- **Performance:** RMSE stays high (> 2.5) across all windows; may need tuning or regularization.
- **Best use:** Large, multi-station AQI datasets with spatial variability.
""",
    "GRU–LSTM": """
- **Overview:** Hybrid sequential model combining GRU efficiency and LSTM accuracy.
- **Strengths:** Learns temporal dependencies effectively.
- **Weaknesses:** Computationally heavy and slow to train on long windows.
- **Performance:** RMSE 0.04–0.22; best at 1 h and 48 h windows.
- **Best use:** Medium-term AQI fluctuations with complex temporal dependencies.
""",
    "CatBoost": """
- **Overview:** Gradient boosting optimized for categorical and numerical data.
- **Strengths:** Near-perfect accuracy (RMSE ≤ 0.010 for all windows) with fast training.
- **Weaknesses:** May overfit if the dataset is too small.
- **Performance:** Most stable and efficient among all models.
- **Best use:** Tabular AQI forecasting and real-time deployment.
""",
    "Transformer": """
- **Overview:** Sequence-to-sequence model based on self-attention.
- **Strengths:** Captures long-range dependencies effectively.
- **Weaknesses:** Needs large datasets and tuning; only 1 h and 8 h windows were evaluated.
- **Performance:** RMSE < 0.1 on both evaluated windows.
- **Best use:** Advanced forecasting and large-scale AQI prediction pipelines.
""",
}

FINDINGS = (
    ("🏆 Best overall", "CatBoost", "Lowest RMSE and fast convergence."),
    ("⚖️ Most balanced", "LightGBM Attention", "Good trade-off between accuracy and efficiency."),
    ("📏 Strong baselines", "Linear · Lasso", "Highly efficient with acceptable accuracy."),
    ("🔁 Best sequential", "GRU–LSTM", "Effective in medium-range forecasting."),
    ("🧠 Most advanced", "Transformer", "Strong potential for long-range dependencies."),
    ("🛠️ Needs work", "CNN–LSTM", "Unstable on small datasets."),
)

METRIC_DEFINITIONS = (
    ("RMSE", "Root Mean Squared Error — lower means higher accuracy."),
    ("MAE", "Mean Absolute Error — average absolute difference between prediction and truth."),
    ("MAPE", "Mean Absolute Percentage Error — error as a percentage of actual values."),
    ("train_time", "Total training time in seconds — a proxy for computational cost."),
)

REFERENCES = (
    "Zhang, B., Chen, W., Li, M., Guo, X., Zheng, Z., and Yang, R., “MGAtt-LSTM: A multi-scale spatial correlation prediction model of PM2.5 concentration based on multi-graph attention,” *Environmental Modelling & Software*, vol. 179, p. 106095, 2024.",
    "Ye, Y., Cao, Y., Dong, Y., and Yan, H., “A graph neural network and Transformer-based model for PM2.5 prediction through spatiotemporal correlation,” *Environmental Modelling and Software*, vol. 191, p. 106501, 2025.",
    "Borah, J., Kumar, S., Nadzir, M. S. M., Cayetano, M. G., Ghayvat, H., Majumdar, S., and Kumar, N., “AiCareBreath: IoT-Enabled Location-Invariant Novel Unified Model for Predicting Air Pollutants to Avoid Related Respiratory Disease,” *IEEE Internet of Things Journal*, vol. 11, no. 8, pp. 14625–14633, 2024.",
    "Iskandaryan, D., Ramos, F., and Trilles, S., “A set of deep learning algorithms for air quality prediction applications,” *Software Impacts*, vol. 16, p. 100365, 2023.",
    "Doush, I. A., Sultan, K., Alsaber, A., Alkandari, D., and Abdullah, A., “Enhanced Jaya optimization for improving multilayer perceptron neural network in urban air quality prediction,” *Journal of Intelligent Systems*, vol. 33, no. 1, pp. 1–32, 2024.",
    "Gond, A. K., Jamal, A., and Verma, T., “Developing a machine learning model using satellite data to predict the Air Quality Index (AQI) over Korba Coalfield, Chhattisgarh (India),” *Atmospheric Pollution Research*, vol. 16, no. 2, Article 102398, 2025.",
    "Kunjir, G. M., Tikle, S., Das, S., Karim, M., Roy, S. K., and Chatterjee, U., “Assessing particulate matter (PM2.5) concentrations and variability across Maharashtra using satellite data and machine learning techniques,” *Discover Sustainability*, vol. 6, no. 1, Article 10823, 2025.",
    "Li, R., Hu, Y., Xu, Z., Shao, X., and Huo, Y., “Predicting the complex variation characteristics of equipment heat dissipation in office buildings via CNN-LSTM-ATT, multiple regression, and similar day models,” *Building and Environment*, vol. 280, p. 113051, 2025.",
    "Shih, D. H., Chung, F. I., Wu, T. W., Wang, B. H., and Shih, M. H., “Advanced Trans-BiGRU-QA fusion model for atmospheric mercury prediction,” *Mathematics*, vol. 12, no. 22, Article 3547, 2024.",
    "Wang, S.-J., Huang, B.-J., and Hu, M.-H., “A deep learning-based air quality index prediction model using LSTM and reference stations: A real application in Taiwan,” in *Proc. 33rd Int. Telecommun. Netw. Appl. Conf. (ITNAC)*, Melbourne, Australia, 2023, pp. 204–209.",
    "Shen, J., Liu, Q., and Feng, X., “Hourly PM2.5 concentration prediction for dry bulk port clusters considering spatiotemporal correlation: A novel deep learning blending ensemble model,” *Journal of Environmental Management*, vol. 337, p. 117795, 2024.",
    "Zhang, J., and Li, S., “Air quality index forecast in Beijing based on CNN-LSTM multi-model,” *Chemosphere*, vol. 308, p. 136180, 2022.",
    "Santiko, I., Soeprobowati, T. R., Surarso, B., and Tahyudin, I., “Campus websites' information quality measurement model and potential students' interest prediction,” *TEM Journal*, vol. 14, no. 2, pp. 1845–1859, 2025.",
    "Wicaksana, H. S., Kusumaningrum, R., and Gernowo, R., “Determining community happiness index with transformers and attention-based deep learning,” *IAES International Journal of Artificial Intelligence*, vol. 13, no. 2, pp. 1753–1761, 2024.",
    "Triyono, L., Gernowo, R., and Prayitno, “MoNetViT: an efficient fusion of CNN and transformer technologies for visual navigation assistance with multi query attention,” *Frontiers in Computer Science*, vol. 7, 1510252, 2025.",
    "Koesuma, S., et al., “Tropical cyclone-related extreme rainfall and its impact under solar radiation management (SRM) in eastern Indonesia region,” in *EGU General Assembly*, Vienna, Austria, Apr. 2024, EGU24-20960.",
    "Koesuma, S., et al., “Analysis of extreme rainfall of tropical cyclone using solar radiation management and ERA5 data in eastern Indonesia,” *Geographia Technica*, vol. 20, no. 1, pp. 298–312, 2025.",
    "Hakim, D. K., Gernowo, R., and Nirwansyah, A. W., “Flood prediction with time series data mining: Systematic review,” *Natural Hazards Research*, vol. 4, no. 2, pp. 194–220, 2023.",
    "Usman, C. D., Widodo, A. P., Adi, K., and Gernowo, R., “Rainfall prediction model in Semarang city using machine learning,” *Indonesian Journal of Electrical Engineering and Computer Science*, vol. 30, no. 2, pp. 1224, 2023.",
    "Gernowo, R., Purbasari, A., Widada, S., and Purboyo, W., “Combination of flood models with weather research and forecast based on extreme rainfall for hazard mitigations,” *Journal of Physics: Conference Series*, vol. 1524, no. 1, 012144, 2020.",
    "Santiko, I., et al., “Traditional-enhance-mobile-ubiquitous-smart: Model innovation in higher education learning style classification using multidimensional and machine learning methods,” *Journal of Applied Data Science*, vol. 6, no. 1, pp. 753–772, 2025.",
    "Utomo, A. P., Purwanto, P., and Surarso, B., “Latest algorithms in machine and deep learning methods to predict retention rates and dropout in higher education: A literature review,” *E3S Web of Conferences*, vol. 448, 02034, 2023.",
    "Zhou, Y., Chen, H., Li, J., Wu, Y., Wu, J., and Chen, L., “ST-Attn: Spatial-temporal attention for crowd flow prediction,” in *Proc. IEEE Int. Conf. Data Mining Workshops (ICDMW)*, Nov. 2019, pp. 609–614.",
)


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


PALETTE = {
    "primary": "#0F766E", "primary-soft": "#CCFBF1", "accent": "#F59E0B",
    "ink": "#0F172A", "muted": "#64748B", "surface": "#FFFFFF",
    "bg": "#F8FAFC", "border": "#E2E8F0",
}
COLORWAY = ["#0F766E", "#F59E0B", "#2563EB", "#DB2777", "#7C3AED", "#EA580C", "#0891B2", "#65A30D"]
HEATMAP_SCALE = "RdBu"

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, .stApp, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1280px; }
#MainMenu, footer { visibility: hidden; }

[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border); }
[data-testid="stSidebar"] .block-container { padding-top: 1rem; }

.page-header { display:flex; align-items:center; gap:.9rem; margin-bottom:1.1rem; }
.page-header .icon { font-size:1.8rem; background:var(--primary-soft); border-radius:14px;
                     width:3rem; height:3rem; display:flex; align-items:center; justify-content:center; }
.page-header h1 { font-size:1.65rem; font-weight:700; margin:0; color:var(--ink); line-height:1.2; }
.page-header p  { margin:.15rem 0 0; color:var(--muted); font-size:.95rem; }

.hero { background: linear-gradient(135deg, #0F766E 0%, #115E59 55%, #134E4A 100%);
        color:#fff; border-radius:18px; padding:1.6rem 1.8rem; margin-bottom:1.2rem; }
.hero h2 { color:#fff; font-size:1.35rem; font-weight:700; margin:0 0 .4rem; }
.hero p  { color:#CCFBF1; margin:0; font-size:.95rem; }

.card { background:var(--surface); border:1px solid var(--border); border-radius:14px;
        padding:1rem 1.2rem; height:100%; box-shadow:0 1px 2px rgba(15,23,42,.04); }
.card h4 { margin:0 0 .35rem; font-size:1rem; color:var(--ink); }
.card p, .card .small { margin:0; color:var(--muted); font-size:.9rem; line-height:1.5; }
.card .tag { color:var(--primary); font-weight:600; font-size:1.05rem; margin-bottom:.15rem; }

[data-testid="stMetric"] { background:var(--surface); border:1px solid var(--border);
        border-radius:14px; padding:.9rem 1.1rem; box-shadow:0 1px 2px rgba(15,23,42,.04); }
[data-testid="stMetricLabel"] { color:var(--muted); }
[data-testid="stMetricValue"] { color:var(--ink); font-weight:700; }

.brand { text-align:center; padding:.6rem .4rem .2rem; }
.brand .project { font-weight:700; font-size:1.05rem; color:var(--primary); }
.brand .author  { font-weight:600; font-size:.9rem; color:var(--ink); margin-top:.35rem; }
.brand .meta    { font-size:.8rem; color:var(--muted); }

.app-footer { text-align:center; color:var(--muted); font-size:.8rem;
              border-top:1px solid var(--border); margin-top:2.5rem; padding-top:1rem; }

.stTabs [data-baseweb="tab"] { font-weight:600; }
[data-testid="stExpander"] { border-radius:12px; border:1px solid var(--border); background:var(--surface); }
"""


def inject_css() -> None:
    variables = ":root{" + ";".join(f"--{k}:{v}" for k, v in PALETTE.items()) + "}"
    st.markdown(f"<style>{variables}{_CSS}</style>", unsafe_allow_html=True)


def style_figure(fig: go.Figure, height: int | None = None) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        colorway=COLORWAY,
        font=dict(family="Inter, sans-serif", color=PALETTE["ink"]),
        title_font=dict(size=17),
        margin=dict(l=20, r=20, t=60, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=""),
        hoverlabel=dict(font_family="Inter, sans-serif"),
    )
    fig.update_xaxes(gridcolor=PALETTE["border"], zeroline=False)
    fig.update_yaxes(gridcolor=PALETTE["border"], zeroline=False)
    if height:
        fig.update_layout(height=height)
    return fig


_NAV_COMMON = {
    "container": {"padding": "0!important", "background-color": "transparent"},
    "icon": {"color": PALETTE["muted"], "font-size": "16px"},
    "nav-link": {"color": PALETTE["ink"], "font-size": "14px", "font-weight": "500",
                 "margin": "3px 0", "border-radius": "10px", "--hover-color": PALETTE["primary-soft"]},
    "nav-link-selected": {"background-color": PALETTE["primary"], "color": "#FFFFFF", "font-weight": "600"},
}
_SIDEBAR_NAV = {**_NAV_COMMON, "nav-link": {**_NAV_COMMON["nav-link"], "text-align": "left"}}
_TOPBAR_NAV = {**_NAV_COMMON, "nav-link": {**_NAV_COMMON["nav-link"], "text-align": "center", "margin": "3px"},
               "container": {"padding": "4px!important", "background-color": PALETTE["surface"],
                             "border": f"1px solid {PALETTE['border']}", "border-radius": "14px"}}


def nav(options: Sequence[str], icons: Sequence[str], key: str, sidebar: bool = False) -> str:
    return option_menu(
        None, list(options), icons=list(icons), key=key, default_index=0,
        orientation="vertical" if sidebar else "horizontal",
        styles=_SIDEBAR_NAV if sidebar else _TOPBAR_NAV,
    )


def page_header(icon: str, title: str, subtitle: str = "") -> None:
    sub = f"<p>{html.escape(subtitle)}</p>" if subtitle else ""
    st.markdown(
        f'<div class="page-header"><div class="icon">{icon}</div>'
        f"<div><h1>{html.escape(title)}</h1>{sub}</div></div>",
        unsafe_allow_html=True,
    )


def hero(title: str, text: str) -> None:
    st.markdown(f'<div class="hero"><h2>{html.escape(title)}</h2><p>{html.escape(text)}</p></div>',
                unsafe_allow_html=True)


def card(title: str, body: str, tag: str = "") -> None:
    tag_html = f'<div class="tag">{html.escape(tag)}</div>' if tag else ""
    st.markdown(f'<div class="card">{tag_html}<h4>{html.escape(title)}</h4><p>{html.escape(body)}</p></div>',
                unsafe_allow_html=True)


def card_row(items: Sequence[tuple]) -> None:
    columns = st.columns(len(items))
    for column, item in zip(columns, items):
        with column:
            card(*item)


def metric_row(items: Sequence[tuple]) -> None:
    for column, (label, value, *rest) in zip(st.columns(len(items)), items):
        column.metric(label, value, help=rest[0] if rest else None)


def show_plot(fig: go.Figure, height: int | None = None) -> None:
    fig = style_figure(fig, height)
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def show_table(df: pd.DataFrame, **kwargs) -> None:
    kwargs.setdefault("hide_index", True)
    try:
        st.dataframe(df, width="stretch", **kwargs)
    except TypeError:
        st.dataframe(df, use_container_width=True, **kwargs)


def sidebar_brand() -> None:
    logos = [BASE_DIR / name for name in LOGO_FILES if (BASE_DIR / name).exists()]
    if logos:
        for column, logo in zip(st.columns(len(logos)), logos):
            column.image(str(logo), width=90)
    st.markdown(
        f'<div class="brand"><div class="project">{html.escape(PROJECT_TITLE)}</div>'
        f'<div class="author">{html.escape(AUTHOR)}</div>'
        f'<div class="meta">{html.escape(UNIVERSITY)}<br>© {COPYRIGHT_YEAR}</div></div>',
        unsafe_allow_html=True,
    )
    st.divider()


def footer() -> None:
    st.markdown(
        f'<div class="app-footer">{html.escape(PROJECT_TITLE)} · {html.escape(AUTHOR)} · '
        f"{html.escape(UNIVERSITY)} · © {COPYRIGHT_YEAR}</div>",
        unsafe_allow_html=True,
    )


def render_home() -> None:
    page_header("🏠", "Home", "Spatiotemporal AQI modeling for DKI Jakarta")
    section = nav(["Introduction", "Dataset", "Business Understanding"],
                  ["book", "database", "briefcase"], key="home_nav")
    {"Introduction": _introduction, "Dataset": _dataset, "Business Understanding": _business}[section]()


def _introduction() -> None:
    hero("Spatiotemporal Air Quality Index (AQI) Modeling in DKI Jakarta",
         "Categorical Boosting with an Attention Mechanism")
    card_row([(label, detail, value) for label, value, detail in HOME_FACTS])
    st.write("")

    image = BASE_DIR / HERO_IMAGE
    if image.exists():
        st.image(str(image), caption="View of Jakarta City, DKI Jakarta")

    st.markdown(INTRODUCTION)

    st.subheader("WHO reference values")
    show_table(pd.DataFrame(WHO_REFERENCE, columns=["Parameter", "WHO Reference Value"]))


def _station_table(stations, value_label: str) -> pd.DataFrame:
    return pd.DataFrame(
        [(s["id"], s["name"], s["area"], s["lat"], s["lon"]) for s in stations],
        columns=["ID", "Station", "Area", "Latitude", "Longitude"],
    )


def _dataset() -> None:
    st.subheader("Air Pollution Standard Index (ISPU)")
    st.markdown(DATASET_AQI)
    show_table(_station_table(AQI_STATIONS, "AQI"))

    st.subheader("Global Historical Climatology Network — Hourly (NOAA)")
    st.markdown(DATASET_METEO)
    show_table(_station_table(METEO_STATIONS, "Temp"))


def _business() -> None:
    st.subheader("Business Understanding")
    st.markdown(BUSINESS_UNDERSTANDING)
    card_row([(title, body) for title, body in BUSINESS_PILLARS])
    st.write("")
    st.info(BUSINESS_CLOSING)


def render_eda() -> None:
    page_header("📂", "Exploratory Data Analysis", "Schema, distributions and categories")
    section = nav(["Data Type Analysis", "Numerical Data", "Categorical Data"],
                  ["gear", "123", "grid"], key="eda_nav")
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
        st.markdown("##### 🟢 Air Quality Index")
        show_table(pd.DataFrame(AQI_SCHEMA, columns=["Column", "Dtype"]), height=420)
    with right:
        st.markdown("##### 🔵 Meteorology (Climatology)")
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


_TRENDS = ["Annual Trend", "Hourly Trend", "Peak Trend"]
_TREND_ICONS = ["calendar", "clock", "star"]


def render_temporal() -> None:
    page_header("📊", "Temporal Analysis", "Air quality & meteorology over time")
    source = nav(["AQI Trends", "Meteorology Trends"], ["activity", "cloud"], key="temporal_source")

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

    trend = nav(_TRENDS, _TREND_ICONS, key=f"{key}_trend")
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


def render_spatial() -> None:
    page_header("🗺️", "Spatial Analysis", "AQI & meteorological stations across Jakarta")
    section = nav(["Spatial Map", "Spatiotemporal Correlation Matrix"], ["map", "link"], key="spatial_nav")
    (_map if section == "Spatial Map" else _correlation)()


def _station_trace(stations, *, label, unit, colorscale, size, bar_x, text_color, position) -> go.Scattermapbox:
    frame = pd.DataFrame(stations)
    return go.Scattermapbox(
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
    fig.update_layout(mapbox_style="carto-positron", mapbox_zoom=10.5,
                      mapbox_center={"lat": -6.2, "lon": 106.82}, margin=dict(r=0, t=10, l=0, b=0),
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

    with st.expander("🧭 Interpretation notes", expanded=True):
        st.markdown(CORRELATION_NOTES)


_FORMATS = {
    "RMSE": st.column_config.NumberColumn("RMSE", format="%.4f"),
    "MAE": st.column_config.NumberColumn("MAE", format="%.4f"),
    "MAPE": st.column_config.NumberColumn("MAPE", format="%.3f"),
    "train_time": st.column_config.NumberColumn("Train time (s)", format="%.1f"),
}


def render_modeling() -> None:
    results = build_model_results()
    summary = summarize_models(results)
    page_header("📶", "Modeling & Evaluation", "Performance of prediction models across window lengths")

    best, fastest = summary.iloc[0], summary.sort_values("train_time").iloc[0]
    metric_row([
        ("Best model (mean RMSE)", best["model"], "Lowest mean RMSE over the windows evaluated"),
        ("Mean RMSE", f"{best['RMSE']:.4f}"),
        ("Fastest to train", fastest["model"], f"{fastest['train_time']:.2f} s on average"),
        ("Models evaluated", str(len(summary))),
    ])
    st.write("")

    overview, compare, samples, insights = st.tabs(
        ["🏁 Overview", "📈 Compare models", "🎯 Actual vs predicted", "🧠 Insights"])
    with overview:
        _overview(results, summary)
    with compare:
        _compare(results)
    with samples:
        _samples(results)
    with insights:
        _insights()


def _overview(results, summary) -> None:
    st.markdown("##### Leaderboard (mean over evaluated windows)")
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
        with st.expander(f"🧩 {name}"):
            st.markdown(text)

    st.markdown("##### Summary of findings")
    card_row([(title, body, tag) for title, tag, body in FINDINGS[:3]])
    st.write("")
    card_row([(title, body, tag) for title, tag, body in FINDINGS[3:]])

    st.markdown("##### Metric definitions")
    for name, text in METRIC_DEFINITIONS:
        st.markdown(f"- **{name}:** {text}")


_METRICS = ("RMSE", "MAE", "MAPE")


def _heatmap(matrix: pd.DataFrame, title: str, scale: str):
    fig = px.imshow(matrix, text_auto=".3f", color_continuous_scale=scale, zmin=0, zmax=1, aspect="auto",
                    title=title, labels=dict(color="p-value"))
    fig.update_xaxes(tickangle=40)
    return fig


def render_stat_test() -> None:
    page_header("📑", "Statistical Test", "Is the difference between models statistically significant?")
    results = build_model_results()

    tab_t, tab_f = st.tabs(["🔹 Paired t-test", "🔹 Friedman + Nemenyi"])
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
        st.success("✅ Significant difference between models (p < 0.05)")
    else:
        st.info("ℹ️ No significant difference detected between models (p ≥ 0.05)")

    ranks = mean_ranks(pivot).rename("mean rank").reset_index()
    show_plot(px.bar(ranks, x="model", y="mean rank", text_auto=".2f",
                     title=f"Mean rank per model ({metric}, lower is better)"), height=360)
    show_plot(_heatmap(nemenyi, f"Post-hoc Nemenyi p-values ({metric})", "YlGnBu"), height=560)


def render_references() -> None:
    page_header("📚", "References", f"{len(REFERENCES)} sources")
    for number, reference in enumerate(REFERENCES, start=1):
        st.markdown(f"**[{number}]** {reference}")


Page = namedtuple("Page", "label icon render")
PAGES = (
    Page("Home", "house", render_home),
    Page("Exploratory Data Analysis (EDA)", "search", render_eda),
    Page("Temporal Analysis", "clock", render_temporal),
    Page("Spatial Analysis", "map", render_spatial),
    Page("Modeling & Evaluation", "cpu", render_modeling),
    Page("Statistical Test", "bar-chart", render_stat_test),
    Page("References", "book", render_references),
)


def main() -> None:
    inject_css()
    with st.sidebar:
        sidebar_brand()
        selected = nav([p.label for p in PAGES], [p.icon for p in PAGES], key="main_nav", sidebar=True)
    next(p for p in PAGES if p.label == selected).render()
    footer()


main()