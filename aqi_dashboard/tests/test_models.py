import unittest

from aqi import content, models


class ModelsTest(unittest.TestCase):
    def setUp(self):
        self.results = models.build_model_results()

    def test_shape_and_columns(self):
        self.assertEqual(list(self.results.columns), models.COLUMNS)
        self.assertEqual(len(self.results), 36)

    def test_summary_sorted_by_rmse_and_catboost_leads(self):
        summary = models.summarize_models(self.results)
        self.assertTrue(summary["RMSE"].is_monotonic_increasing)
        self.assertEqual(summary.iloc[0]["model"], "CatBoost")

    def test_prediction_samples_filters_model_and_window(self):
        window = int(self.results["window"].iloc[0])
        out = models.prediction_samples(self.results, ["CatBoost"], window)
        self.assertTrue((out["model"] == "CatBoost").all())
        self.assertTrue((out["window"] == window).all())

    def test_every_model_has_an_insight_text(self):
        self.assertEqual(set(self.results["model"]), set(content.MODEL_INSIGHTS))

    def test_leaderboard_bars_are_normalised(self):
        bars = models.leaderboard_bars(self.results, "RMSE")
        self.assertEqual(bars["model"].iloc[0], "CatBoost")
        self.assertTrue(bars["width"].between(0, 100).all())
        self.assertTrue(bars["width"].is_monotonic_increasing)
