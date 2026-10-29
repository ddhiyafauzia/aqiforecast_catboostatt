import base64
import html
import importlib.util
import io
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from aqi import assets, config, hero, theme

PNG_1PX = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")


class AssetsTest(unittest.TestCase):
    def test_svg_fallbacks_exist_and_are_valid_xml(self):
        for name in ("ush_emblem.svg", "hero_skyline.svg"):
            path = assets.ASSETS_DIR / name
            self.assertTrue(path.exists(), name)
            self.assertTrue(ET.parse(path).getroot().tag.endswith("svg"), name)

    def test_data_uri_is_base64_svg_and_cached(self):
        uri = assets.data_uri("ush_emblem.svg")
        self.assertTrue(uri.startswith("data:image/svg+xml;base64,"))
        self.assertIs(assets.data_uri("ush_emblem.svg"), uri)

    def test_missing_asset_raises(self):
        with self.assertRaises(FileNotFoundError):
            assets.data_uri("nope.svg")

    def test_find_image_is_case_and_extension_agnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "JKTLogo.PNG").write_bytes(PNG_1PX)
            self.assertEqual(assets.find_image(Path(tmp), "jktlogo").name, "JKTLogo.PNG")
            self.assertIsNone(assets.find_image(Path(tmp), "intellogo"))

    def test_brand_logos_keep_order_and_fall_back_to_emblem_for_ush(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("intellogo.png", "jktlogo.png"):
                (Path(tmp) / name).write_bytes(PNG_1PX)
            logos = assets.brand_logos(Path(tmp))
        self.assertEqual([alt for alt, _ in logos], [config.BRAND_LOGOS[0][0], config.BRAND_LOGOS[1][0],
                                                      config.BRAND_LOGOS[2][0]])
        self.assertTrue(logos[0][1].startswith("data:image/png"))
        self.assertTrue(logos[1][1].startswith("data:image/svg+xml"))

    def test_brand_logos_without_any_file_still_shows_university_emblem(self):
        with tempfile.TemporaryDirectory() as tmp:
            logos = assets.brand_logos(Path(tmp))
        self.assertEqual(len(logos), 1)

    def test_photo_missing_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(assets.photo_data_uri(Path(tmp), "jktimage"))

    @unittest.skipUnless(importlib.util.find_spec("PIL"), "Pillow not installed")
    def test_photo_is_downscaled_and_compressed(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            Image.new("RGB", (3200, 1600), (30, 80, 160)).save(Path(tmp) / "jktimage.jpeg")
            uri = assets.photo_data_uri(Path(tmp), "jktimage", max_width=1600)
        self.assertTrue(uri.startswith("data:image/jpeg;base64,"))
        width = Image.open(io.BytesIO(base64.b64decode(uri.split(",", 1)[1]))).width
        self.assertEqual(width, 1600)


class HeroTest(unittest.TestCase):
    def setUp(self):
        self.html = hero.build_hero_html(photo_uri=None, logos=())

    def test_contains_counters_for_dataset_sizes(self):
        self.assertIn('data-count="6966"', self.html)
        self.assertIn('data-count="99231"', self.html)

    def test_has_one_chip_per_aqi_category(self):
        self.assertEqual(self.html.count('class="chip'), 5)

    def test_respects_reduced_motion_and_is_self_contained(self):
        self.assertIn("prefers-reduced-motion", self.html)
        self.assertNotIn("http://", self.html.replace("http://www.w3.org", ""))

    def test_falls_back_to_skyline_without_photo(self):
        self.assertIn('class="sky"', self.html)
        self.assertNotIn('class="photo"', self.html)

    def test_uses_photo_and_logos_when_given(self):
        page = hero.build_hero_html(photo_uri="data:image/jpeg;base64,AAAA",
                                    logos=[("Intel", "data:image/png;base64,BBBB"),
                                           ("Universitas Sugeng Hartono", "data:image/png;base64,CCCC")])
        self.assertIn('class="photo"', page)
        self.assertNotIn('class="sky"', page)
        self.assertEqual(page.count('class="logo"'), 2)
        self.assertIn('alt="Intel"', page)


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

    def test_brand_block_lists_the_four_lines_in_order(self):
        text = html.unescape(theme.brand_html([("Intel", "data:image/png;base64,AAAA")]))
        lines = ["AI for Workforce Intel", "Fauzia Dhiyaa' Farros", "Universitas Sugeng Hartono",
                 "© 2026 Fauzia Dhiyaa' Farros"]
        positions = [text.index(line) for line in lines]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('alt="Intel"', text)

    def test_footer_text_uses_config(self):
        text = html.unescape(theme.footer_html())
        self.assertIn(config.copyright_line(), text)
        self.assertIn(config.UNIVERSITY, text)
