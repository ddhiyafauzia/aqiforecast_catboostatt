"""Reusable Streamlit components. Every piece of HTML is escaped before it is injected."""
from __future__ import annotations

import html
from typing import Sequence

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from aqi import assets, hero, theme
from aqi.config import AUTHOR, BASE_DIR, PROJECT_TITLE, UNIVERSITY, copyright_line


def inject_css() -> None:
    st.markdown(f"<style>{theme.build_css()}</style>", unsafe_allow_html=True)


def nav(options: Sequence[str], key: str, sidebar: bool = False) -> str:
    return st.radio("Navigation", list(options), key=key, horizontal=not sidebar, label_visibility="collapsed")


def page_header(icon: str, title: str, subtitle: str = "") -> None:
    sub = f"<p>{html.escape(subtitle)}</p>" if subtitle else ""
    svg = (f'<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.9" '
           f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{theme.ICONS[icon]}</svg>')
    st.markdown(f'<div class="page-header"><div class="icon">{svg}</div>'
                f"<div><h1>{html.escape(title)}</h1>{sub}</div></div>", unsafe_allow_html=True)


def card(title: str, body: str, tag: str = "") -> None:
    tag_html = f'<div class="tag">{html.escape(tag)}</div>' if tag else ""
    st.markdown(f'<div class="card">{tag_html}<h4>{html.escape(title)}</h4><p>{html.escape(body)}</p></div>',
                unsafe_allow_html=True)


def card_row(items: Sequence[tuple]) -> None:
    for column, item in zip(st.columns(len(items)), items):
        with column:
            card(*item)


def metric_row(items: Sequence[tuple]) -> None:
    for column, (label, value, *rest) in zip(st.columns(len(items)), items):
        column.metric(label, value, help=rest[0] if rest else None)


def leaderboard(bars: pd.DataFrame, title: str, unit: str = "") -> None:
    rows = "".join(
        f'<div class="lb-row"><div class="lb-head"><span>{html.escape(str(r.model))}</span>'
        f"<span>{r.value:.4g}{unit}</span></div>"
        f'<div class="lb-track"><div class="lb-fill" style="width:{r.width}%"></div></div></div>'
        for r in bars.itertuples())
    st.markdown(f'<div class="lb"><h4>{html.escape(title)}</h4>{rows}</div>', unsafe_allow_html=True)


def show_plot(fig, height: int | None = None) -> None:
    fig.update_layout(**theme.plotly_layout(height))
    fig.update_xaxes(gridcolor=theme.PALETTE["border"], zeroline=False)
    fig.update_yaxes(gridcolor=theme.PALETTE["border"], zeroline=False)
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:  # older Streamlit
        st.plotly_chart(fig, use_container_width=True)


def show_table(df: pd.DataFrame, **kwargs) -> None:
    kwargs.setdefault("hide_index", True)
    try:
        st.dataframe(df, width="stretch", **kwargs)
    except TypeError:
        st.dataframe(df, use_container_width=True, **kwargs)


def interactive_hero() -> None:
    components.html(hero.build_hero_html(), height=760, scrolling=False)


def sidebar_brand() -> None:
    logos = [assets.data_uri("logo.svg"), assets.university_logo_uri()]
    jkt = BASE_DIR / "jktlogo.png"
    if jkt.exists():
        logos.append(assets.file_data_uri(jkt))
    imgs = "".join(f'<img src="{uri}" alt="">' for uri in logos)
    st.markdown(
        f'<div class="brand"><div class="logos">{imgs}</div>'
        f'<div class="project">{html.escape(PROJECT_TITLE)}</div><div class="author">{html.escape(AUTHOR)}</div>'
        f'<div class="meta">{html.escape(UNIVERSITY)}<br>{html.escape(copyright_line())}</div></div>',
        unsafe_allow_html=True)
    st.divider()


def footer() -> None:
    st.markdown(theme.footer_html(), unsafe_allow_html=True)
