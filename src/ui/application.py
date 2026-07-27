"""Streamlit application shell for the banking risk lab."""

from __future__ import annotations

import streamlit as st

from src.config import APP_NAME, APP_TAGLINE
from src.risk.stress_testing import SCENARIOS
from src.ui.components import render_app_header
from src.ui.context import build_portfolio_context, load_app_data
from src.ui.navigation import render_sidebar
from src.ui.pages import get_page_renderer
from src.ui.style import configure_plotly_defaults, inject_custom_style


def render_application() -> None:
    st.set_page_config(page_title=APP_NAME, layout="wide")
    inject_custom_style()
    configure_plotly_defaults()

    app_data = load_app_data()
    page, pd_shock, lgd_shock, scenario = render_sidebar()
    if scenario not in SCENARIOS:
        st.warning("Unknown scenario selected. Falling back to Baseline.")
        scenario = "Baseline"

    context = build_portfolio_context(app_data, pd_shock, lgd_shock, scenario)
    render_app_header(APP_NAME, APP_TAGLINE)

    renderer = get_page_renderer(page)
    try:
        renderer(context)
    except Exception as exc:
        st.error(f"The page '{page}' could not be rendered.")
        st.exception(exc)


render_application()
