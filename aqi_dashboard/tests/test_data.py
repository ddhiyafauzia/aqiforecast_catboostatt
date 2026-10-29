import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from aqi import data


class CategorizeTest(unittest.TestCase):
    def test_boundaries(self):
        cases = {0: "GOOD", 50: "GOOD", 50.1: "MODERATE", 100: "MODERATE", 150: "UNHEALTHY",
                 200: "VERY UNHEALTHY", 200.1: "HAZARDOUS", 287: "HAZARDOUS"}
        for value, expected in cases.items():
            self.assertEqual(data.categorize_pm25(value), expected, value)

    def test_nan_is_no_data(self):
        self.assertEqual(data.categorize_pm25(np.nan), data.NO_DATA)


class StandardizeTest(unittest.TestCase):
    def setUp(self):
        self.raw = pd.DataFrame({
            "Tanggal": ["2024-03-05 14:00", "2024-03-05 15:00", "bad-date"],
            "pm_duakomalima": [10.0, 20.0, 30.0], "PM_SEPULUH": [1.0, 2.0, 3.0]})

    def test_renames_and_derives_time_columns(self):
        out = data.standardize_columns(self.raw)
        self.assertEqual(len(out), 2)
        self.assertIn("PM2.5", out.columns)
        self.assertEqual(out["hour"].tolist(), [14, 15])
        self.assertEqual(out["month_day"].iloc[0], "03-05")

    def test_missing_date_raises(self):
        with self.assertRaises(KeyError):
            data.standardize_columns(pd.DataFrame({"x": [1]}))

    def test_does_not_mutate_input(self):
        before = self.raw.copy()
        data.standardize_columns(self.raw)
        pd.testing.assert_frame_equal(self.raw, before)


class ProfileTest(unittest.TestCase):
    def setUp(self):
        raw = pd.DataFrame({
            "date": pd.to_datetime(["2023-01-01 01:00", "2023-01-01 02:00", "2024-01-01 01:00"]),
            "PM2.5": [10.0, 30.0, 50.0]})
        self.long = data.to_long(data.standardize_columns(raw), ["PM2.5", "missing"])

    def test_to_long_ignores_unknown_columns(self):
        self.assertEqual(set(self.long["parameter"]), {"PM2.5"})

    def test_to_long_empty_when_nothing_matches(self):
        frame = pd.DataFrame({c: [] for c in data.TIME_COLUMNS})
        self.assertTrue(data.to_long(frame, ["x"]).empty)

    def test_annual_profile_is_averaged_and_sorted(self):
        profile = data.annual_profile(self.long, "PM2.5")
        self.assertEqual(profile["value"].tolist(), [20.0, 50.0])
        self.assertEqual(profile["year"].tolist(), [2023, 2024])

    def test_hourly_profile_groups_by_hour_and_year(self):
        self.assertEqual(len(data.hourly_profile(self.long, ["PM2.5"])), 3)

    def test_find_peak(self):
        date, value = data.find_peak(self.long)
        self.assertEqual(value, 50.0)
        self.assertEqual(date.year, 2024)

    def test_find_peak_all_nan_returns_none(self):
        frame = pd.DataFrame({"date": [pd.Timestamp("2024-01-01")], "value": [np.nan]})
        self.assertIsNone(data.find_peak(frame))


class CategoricalTest(unittest.TestCase):
    def test_builds_ordered_category_and_station_labels(self):
        df = pd.DataFrame({"PM2.5": [10, 80, 250, np.nan], "station": ["DKI1", "DKI2", "DKI5", "DKI1"]})
        out = data.prepare_categorical(df)
        self.assertEqual(len(out), 3)
        self.assertEqual(list(out["Category"].cat.categories), ["GOOD", "MODERATE", "HAZARDOUS"])
        self.assertIn("DKI1 - Bundaran HI", set(out["station"].astype(str)))


class LoadersTest(unittest.TestCase):
    def test_load_aqi_parses_dates(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "aqi.csv"
            path.write_text("tanggal,pm_duakomalima\n2024-01-01,12\n")
            self.assertTrue(pd.api.types.is_datetime64_any_dtype(data.load_aqi(path)["tanggal"]))

    def test_load_meteorology_merges_files_and_fills_numeric(self):
        with tempfile.TemporaryDirectory() as tmp:
            for i, temp in enumerate(["30", ""]):
                Path(tmp, f"m{i}.csv").write_text(
                    f"DATE,LATITUDE,LONGITUDE,TEMPERATURE,junk\n2024-01-0{i+1},-6.2,106.8,{temp},x\n")
            out = data.load_meteorology(Path(tmp))
            self.assertEqual(len(out), 2)
            self.assertNotIn("junk", out.columns)
            self.assertFalse(out["temperature"].isna().any())

    def test_load_meteorology_empty_folder_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                data.load_meteorology(Path(tmp))


class LocateFileTest(unittest.TestCase):
    def test_finds_file_in_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "aqi_meteo.csv").write_text("x")
            self.assertEqual(data.locate_file("aqi_meteo.csv", [Path(tmp)]), Path(tmp, "aqi_meteo.csv"))

    def test_finds_file_in_data_subfolder(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "data").mkdir()
            Path(tmp, "data", "aqi_meteo.csv").write_text("x")
            self.assertIsNotNone(data.locate_file("aqi_meteo.csv", [Path(tmp)]))

    def test_tolerates_hidden_double_extension_and_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "AQI_Meteo.csv.csv").write_text("x")
            self.assertEqual(data.locate_file("aqi_meteo.csv", [Path(tmp)]).name, "AQI_Meteo.csv.csv")

    def test_returns_none_when_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(data.locate_file("aqi_meteo.csv", [Path(tmp)]))
