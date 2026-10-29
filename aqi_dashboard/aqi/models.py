"""Benchmark results of the forecasting models and helpers to summarise them."""
from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

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


def leaderboard_bars(results: pd.DataFrame, metric: str, floor: float = 1e-3) -> pd.DataFrame:
    """Mean ``metric`` per model (best first) with a log-scaled bar ``width`` in 0-100."""
    mean = results.groupby("model")[metric].mean().sort_values().rename("value").reset_index()
    logs = np.log10(mean["value"].clip(lower=floor))
    span = max(logs.max() - np.log10(floor), 1e-9)
    mean["width"] = ((logs - np.log10(floor)) / span * 100).round(1)
    return mean
