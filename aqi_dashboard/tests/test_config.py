import unittest

from aqi import config


class ConfigTest(unittest.TestCase):
    def test_copyright_year_is_2026(self):
        self.assertEqual(config.COPYRIGHT_YEAR, 2026)

    def test_copyright_line_credits_author_and_university(self):
        self.assertEqual(
            config.copyright_line(),
            "© 2026 Fauzia Dhiyaa' Farros - Universitas Sugeng Hartono",
        )

    def test_station_inventory(self):
        self.assertEqual(len(config.AQI_STATIONS), 5)
        self.assertEqual(len(config.METEO_STATIONS), 4)

    def test_station_ids_are_unique(self):
        ids = [s["id"] for s in config.AQI_STATIONS + config.METEO_STATIONS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_stations_are_inside_jakarta_bounds(self):
        for s in config.AQI_STATIONS + config.METEO_STATIONS:
            self.assertTrue(-6.5 < s["lat"] < -6.0, s)
            self.assertTrue(106.6 < s["lon"] < 107.0, s)

    def test_every_aqi_station_has_a_label(self):
        self.assertEqual({s["id"] for s in config.AQI_STATIONS}, set(config.STATION_LABELS))
