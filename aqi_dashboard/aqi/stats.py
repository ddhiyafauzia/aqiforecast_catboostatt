"""Statistical comparison of forecasting models: paired t-test, Friedman and Nemenyi post-hoc."""
from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, studentized_range, ttest_rel

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



def mean_ranks(pivot: pd.DataFrame) -> pd.Series:
    """Mean rank per model across windows (1 = best), sorted best first."""
    return pivot.rank(axis=1).mean().sort_values()


def nemenyi_p_value(rank_gap: float, k: int, n: int) -> float:
    """Two-sided Nemenyi p-value for a mean-rank gap among ``k`` models over ``n`` blocks."""
    q = rank_gap / np.sqrt(k * (k + 1) / (6.0 * n))
    return float(studentized_range.sf(q * np.sqrt(2.0), k, np.inf))


def nemenyi_matrix(pivot: pd.DataFrame) -> pd.DataFrame:
    """Pairwise Nemenyi post-hoc p-values (same result as scikit-posthocs, without the dependency)."""
    _validate_block_design(pivot)
    n, k = pivot.shape
    ranks = pivot.rank(axis=1).mean()
    matrix = pd.DataFrame(1.0, index=pivot.columns, columns=pivot.columns)
    for i, a in enumerate(pivot.columns):
        for b in pivot.columns[i + 1:]:
            matrix.loc[a, b] = matrix.loc[b, a] = nemenyi_p_value(abs(ranks[a] - ranks[b]), k, n)
    return matrix
