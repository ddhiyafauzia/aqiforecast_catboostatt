"""Boots the real Streamlit app headlessly. Skipped when streamlit is not installed."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "streamlit not installed")
class AppSmokeTest(unittest.TestCase):
    def test_every_page_renders_without_exception(self):
        from streamlit.testing.v1 import AppTest
        from aqi.pages import PAGES

        for page in PAGES:
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
            app.session_state["main_nav"] = page.label
            app.run()
            self.assertFalse(app.exception, f"{page.label}: {app.exception}")
