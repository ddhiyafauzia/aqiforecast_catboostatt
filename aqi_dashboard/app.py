"""Entry point:  streamlit run app.py"""
import streamlit as st

from aqi.config import APP_TITLE, PROJECT_TITLE

st.set_page_config(page_title=f"{APP_TITLE} · {PROJECT_TITLE}", page_icon="🌿", layout="wide",
                   initial_sidebar_state="auto")

from aqi.pages import PAGES  # noqa: E402  (must come after set_page_config)
from aqi.ui import footer, inject_css, nav, sidebar_brand  # noqa: E402


def main() -> None:
    inject_css()
    with st.sidebar:
        sidebar_brand()
        selected = nav([p.label for p in PAGES], key="main_nav", sidebar=True)
    next(p for p in PAGES if p.label == selected).render()
    footer()


main()
