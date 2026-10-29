"""Static configuration: paths, branding, schema and station metadata."""
from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "aqi_meteo.csv"
METEO_DIR = BASE_DIR / "meteorology"


APP_TITLE = "Spatiotemporal AQI Forecasting Dashboard"
PROJECT_TITLE = "AI for Workforce Intel"
AUTHOR = "Fauzia Dhiyaa' Farros"
UNIVERSITY = "Universitas Sugeng Hartono"
COPYRIGHT_YEAR = 2026

LOGO_DIR = BASE_DIR / "assets" / "logo"
BRAND_LOGOS = (  # (alt text, file stem) in display order; any image extension is accepted
    ("Intel", "intellogo"),
    ("Universitas Sugeng Hartono", "ushlogo"),
    ("Pemerintah Provinsi DKI Jakarta", "jktlogo"),
)
HERO_PHOTO_STEM = "jktimage"


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



def copyright_line() -> str:
    return f"© {COPYRIGHT_YEAR} {AUTHOR}"


# Indonesian ISPU / PM2.5 categories, used by the interactive AQI explorer.
AQI_CATEGORIES = (
    {"key": "GOOD", "label": "Good", "range": "0 – 50", "color": "#22A06B",
     "advice": "Air quality is satisfactory and poses little or no risk to health."},
    {"key": "MODERATE", "label": "Moderate", "range": "51 – 100", "color": "#E8B100",
     "advice": "Acceptable for most people; unusually sensitive individuals may feel minor effects."},
    {"key": "UNHEALTHY", "label": "Unhealthy", "range": "101 – 150", "color": "#F97316",
     "advice": "Sensitive groups may experience health effects. Limit prolonged outdoor exertion."},
    {"key": "VERY UNHEALTHY", "label": "Very Unhealthy", "range": "151 – 200", "color": "#DC2626",
     "advice": "Everyone may begin to feel health effects. Reduce outdoor activity and wear a mask."},
    {"key": "HAZARDOUS", "label": "Hazardous", "range": "200+", "color": "#9333EA",
     "advice": "Health alert: serious risk for the whole population. Stay indoors with clean air."},
)
