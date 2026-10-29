"""References."""
from __future__ import annotations

import streamlit as st

from aqi.content import REFERENCES
from aqi.ui import page_header


def render_references() -> None:
    page_header("book", "References", f"{len(REFERENCES)} sources")
    for number, reference in enumerate(REFERENCES, start=1):
        st.markdown(f"**[{number}]** {reference}")
