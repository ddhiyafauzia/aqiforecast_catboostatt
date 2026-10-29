import unittest
import xml.etree.ElementTree as ET

from aqi import assets, config, hero, theme


class AssetsTest(unittest.TestCase):
    def test_svg_assets_exist_and_are_valid_xml(self):
        for name in ("logo.svg", "ush_emblem.svg", "hero_skyline.svg"):
            path = assets.ASSETS_DIR / name
            self.assertTrue(path.exists(), name)
            self.assertTrue(ET.parse(path).getroot().tag.endswith("svg"), name)

    def test_data_uri_is_base64_svg_and_cached(self):
        uri = assets.data_uri("logo.svg")
        self.assertTrue(uri.startswith("data:image/svg+xml;base64,"))
        self.assertIs(assets.data_uri("logo.svg"), uri)

    def test_missing_asset_raises(self):
        with self.assertRaises(FileNotFoundError):
            assets.data_uri("nope.svg")

    def test_university_logo_falls_back_to_emblem(self):
        self.assertTrue(assets.university_logo_uri().startswith("data:image/"))


class HeroTest(unittest.TestCase):
    def setUp(self):
        self.html = hero.build_hero_html()

    def test_contains_counters_for_dataset_sizes(self):
        self.assertIn('data-count="6966"', self.html)
        self.assertIn('data-count="99231"', self.html)

    def test_has_one_chip_per_aqi_category(self):
        self.assertEqual(self.html.count('class="chip'), 5)

    def test_respects_reduced_motion_and_is_self_contained(self):
        self.assertIn("prefers-reduced-motion", self.html)
        self.assertNotIn("http://", self.html.replace("http://www.w3.org", ""))

    def test_embeds_skyline_inline(self):
        self.assertIn("<svg", self.html)


class ThemeTest(unittest.TestCase):
    def test_palette_values_are_hex(self):
        for key, value in theme.PALETTE.items():
            self.assertRegex(value, r"^#[0-9A-Fa-f]{6}$", key)

    def test_css_is_mobile_first_and_animated(self):
        css = theme.build_css()
        for needle in ("@media (max-width: 640px)", "@keyframes", "prefers-reduced-motion", "--primary"):
            self.assertIn(needle, css)

    def test_old_teal_amber_palette_is_gone(self):
        blob = (theme.build_css() + "".join(theme.COLORWAY)).lower()
        for old in ("#0f766e", "#f59e0b"):
            self.assertNotIn(old, blob)

    def test_plotly_layout_uses_palette(self):
        layout = theme.plotly_layout(400)
        self.assertEqual(layout["height"], 400)
        self.assertEqual(list(layout["colorway"]), list(theme.COLORWAY))

    def test_footer_text_uses_config(self):
        self.assertIn(config.copyright_line(), theme.footer_html())
