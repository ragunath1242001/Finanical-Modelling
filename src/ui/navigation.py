"""Sidebar navigation configuration and controls."""

from __future__ import annotations

import streamlit as st

from src.config import PORTFOLIO_DISCLAIMER
from src.risk.stress_testing import SCENARIOS


DOCS_PAGE = "Documentation & Study Guide"
BANKING_101_PAGE = "Banking 101"

MAIN_PAGES = [
    "Executive Overview",
    "Credit Risk",
    "IFRS 9 ECL",
    "Basel Capital and IRB",
    "CRR3 Basel Final Reforms",
    "COREP/FINREP Reporting",
    "Stress Testing",
    "Geopolitical Reverse Stress",
    "Liquidity and Leverage",
    "Fraud and AML",
    "Forecasting",
    "BCBS 239 Governance",
    "Model Risk Management",
    "EU AI Act Governance",
    "DORA Operational Resilience",
    "ESG Climate Credit Risk",
    "XVA Counterparty Risk",
]

NAVIGATION_GROUPS = {
    "Overview": ["Executive Overview"],
    "Credit and Capital": [
        "Credit Risk",
        "IFRS 9 ECL",
        "Basel Capital and IRB",
        "CRR3 Basel Final Reforms",
        "Stress Testing",
        "Geopolitical Reverse Stress",
        "Liquidity and Leverage",
    ],
    "Reporting and Governance": ["COREP/FINREP Reporting", "BCBS 239 Governance", "Model Risk Management"],
    "Financial Crime and Analytics": ["Fraud and AML", "Forecasting"],
    "Emerging Risk": ["EU AI Act Governance", "DORA Operational Resilience", "ESG Climate Credit Risk", "XVA Counterparty Risk"],
}


def initialize_navigation() -> None:
    if "page" not in st.session_state:
        st.session_state.page = "Executive Overview"
    if "page_select" not in st.session_state:
        st.session_state.page_select = st.session_state.page
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "Standard View"


def set_selected_page() -> None:
    selected = st.session_state.page_select
    if selected in MAIN_PAGES:
        st.session_state.page = selected


def set_page(page_name: str) -> None:
    st.session_state.page = page_name
    if page_name in MAIN_PAGES:
        st.session_state.page_select = page_name


def render_sidebar() -> tuple[str, float, float, str]:
    st.sidebar.markdown("### European Banking Risk & Governance Lab")
    st.sidebar.caption("Scenario controls, learning mode and navigation")
    st.sidebar.caption(PORTFOLIO_DISCLAIMER)
    initialize_navigation()

    st.sidebar.radio("View mode", ["Standard View", "Learning View"], horizontal=False, key="view_mode")
    st.sidebar.caption("Learning View keeps formulas, assumptions and interview prompts visible where pages support them.")

    if st.session_state.page in MAIN_PAGES and st.session_state.page_select != st.session_state.page:
        st.session_state.page_select = st.session_state.page
    selected_index = MAIN_PAGES.index(st.session_state.page_select) if st.session_state.page_select in MAIN_PAGES else 0
    st.sidebar.selectbox(
        "Page",
        MAIN_PAGES,
        index=selected_index,
        key="page_select",
        on_change=set_selected_page,
    )

    with st.sidebar.expander("Page shortcuts", expanded=False):
        for group_name, pages in NAVIGATION_GROUPS.items():
            st.markdown(f"**{group_name}**")
            for page_name in pages:
                st.button(
                    page_name,
                    key=f"nav_shortcut_{page_name}",
                    use_container_width=True,
                    on_click=set_page,
                    args=(page_name,),
                )

    st.sidebar.divider()
    pd_shock = st.sidebar.slider("Portfolio PD shock", -20, 100, 0, 5) / 100
    lgd_shock = st.sidebar.slider("Portfolio LGD shock", -20, 80, 0, 5) / 100
    scenario = st.sidebar.selectbox("Scenario", list(SCENARIOS))
    st.sidebar.divider()
    if st.sidebar.button(DOCS_PAGE):
        set_page(DOCS_PAGE)
    if st.sidebar.button(BANKING_101_PAGE):
        set_page(BANKING_101_PAGE)
    st.sidebar.caption(f"Current page: {st.session_state.page}")
    return st.session_state.page, pd_shock, lgd_shock, scenario
