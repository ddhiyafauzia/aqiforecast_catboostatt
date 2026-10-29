"""Page registry: the order here is the order of the sidebar menu."""
from __future__ import annotations

from collections import namedtuple

from aqi.pages.eda import render_eda
from aqi.pages.home import render_home
from aqi.pages.modeling import render_modeling
from aqi.pages.references import render_references
from aqi.pages.spatial import render_spatial
from aqi.pages.stat_test import render_stat_test
from aqi.pages.temporal import render_temporal

Page = namedtuple("Page", "label render")
PAGES = (
    Page("Home", render_home),
    Page("Exploratory Data Analysis (EDA)", render_eda),
    Page("Temporal Analysis", render_temporal),
    Page("Spatial Analysis", render_spatial),
    Page("Modeling & Evaluation", render_modeling),
    Page("Statistical Test", render_stat_test),
    Page("References", render_references),
)
