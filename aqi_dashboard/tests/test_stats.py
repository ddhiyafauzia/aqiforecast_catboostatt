import unittest

import numpy as np
import pandas as pd

from aqi import stats


def make_pivot(seed=0, windows=6, models=("A", "B", "C", "D")):
    rng = np.random.default_rng(seed)
    base = np.arange(len(models), dtype=float)
    return pd.DataFrame(base + rng.normal(0, 0.05, (windows, len(models))), columns=list(models))


class StatsTest(unittest.TestCase):
    def test_complete_cases_drops_incomplete_models(self):
        p = make_pivot()
        p.loc[0, "D"] = np.nan
        complete, excluded = stats.complete_cases(p)
        self.assertEqual(excluded, ["D"])
        self.assertNotIn("D", complete.columns)

    def test_pairwise_matrix_is_symmetric_with_unit_diagonal(self):
        m = stats.pairwise_ttest_matrix(make_pivot())
        self.assertTrue(np.allclose(np.diag(m), 1.0))
        np.testing.assert_allclose(m.to_numpy(), m.to_numpy().T, equal_nan=True)

    def test_pairwise_skips_pairs_with_too_few_windows(self):
        p = make_pivot()
        p.loc[2:, "D"] = np.nan
        self.assertTrue(np.isnan(stats.pairwise_ttest_matrix(p).loc["A", "D"]))

    def test_friedman_detects_consistent_ordering(self):
        result = stats.friedman_test(make_pivot())
        self.assertTrue(result.is_significant())
        self.assertEqual((result.n_windows, result.n_models), (6, 4))

    def test_friedman_validates_design(self):
        with self.assertRaises(ValueError):
            stats.friedman_test(make_pivot(models=("A", "B")))
        bad = make_pivot()
        bad.iloc[0, 0] = np.nan
        with self.assertRaises(ValueError):
            stats.friedman_test(bad)

    def test_mean_ranks_sorted_best_first(self):
        ranks = stats.mean_ranks(make_pivot())
        self.assertEqual(ranks.index[0], "A")
        self.assertEqual(ranks.iloc[0], 1.0)

    def test_nemenyi_is_symmetric_and_bounded(self):
        m = stats.nemenyi_matrix(make_pivot()).to_numpy()
        self.assertTrue(((m >= 0) & (m <= 1)).all())
        np.testing.assert_allclose(m, m.T)
        self.assertTrue(np.allclose(np.diag(m), 1.0))

    def test_nemenyi_matches_demsar_critical_difference(self):
        k, n = 3, 10
        cd = 2.343 * np.sqrt(k * (k + 1) / (6 * n))
        self.assertAlmostEqual(stats.nemenyi_p_value(cd, k, n), 0.05, places=2)
