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
    if "page_picker" not in st.session_state:
        st.session_state.page_picker = st.session_state.page if st.session_state.page in MAIN_PAGES else "Executive Overview"
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "Standard View"
    if "scenario" not in st.session_state:
        st.session_state.scenario = "Baseline"


def set_page(page_name: str) -> None:
    st.session_state.page = page_name
    if page_name in MAIN_PAGES:
        st.session_state.page_picker = page_name


def set_page_from_picker() -> None:
    set_page(st.session_state.page_picker)


def set_view_mode(mode: str) -> None:
    st.session_state.view_mode = mode


def set_scenario(scenario_name: str) -> None:
    st.session_state.scenario = scenario_name


def _sidebar_state_button(label: str, active: bool, key: str, on_click, args: tuple[str, ...]) -> None:
    prefix = "Selected: " if active else ""
    st.button(
        f"{prefix}{label}",
        key=key,
        use_container_width=True,
        type="primary" if active else "secondary",
        on_click=on_click,
        args=args,
    )


def render_sidebar() -> tuple[str, float, float, str]:
    st.sidebar.markdown("### European Banking Risk & Governance Lab")
    st.sidebar.caption("Scenario controls, learning mode and navigation")
    st.sidebar.caption(PORTFOLIO_DISCLAIMER)
    initialize_navigation()

    st.sidebar.markdown("#### View mode")
    view_columns = st.sidebar.columns(2)
    with view_columns[0]:
        _sidebar_state_button(
            "Standard",
            st.session_state.view_mode == "Standard View",
            "view_mode_standard",
            set_view_mode,
            ("Standard View",),
        )
    with view_columns[1]:
        _sidebar_state_button(
            "Learning",
            st.session_state.view_mode == "Learning View",
            "view_mode_learning",
            set_view_mode,
            ("Learning View",),
        )
    st.sidebar.caption(f"Current view: {st.session_state.view_mode}")
    st.sidebar.caption("Learning View keeps formulas, assumptions and interview prompts visible where pages support them.")

    st.sidebar.markdown("#### Navigation")
    if st.session_state.page in MAIN_PAGES and st.session_state.page_picker != st.session_state.page:
        st.session_state.page_picker = st.session_state.page
    picker_index = MAIN_PAGES.index(st.session_state.page_picker) if st.session_state.page_picker in MAIN_PAGES else 0
    st.sidebar.selectbox(
        "Select page",
        MAIN_PAGES,
        index=picker_index,
        key="page_picker",
        on_change=set_page_from_picker,
    )
    st.sidebar.caption("Use this single page selector for the main app pages.")

    st.sidebar.divider()
    pd_shock = st.sidebar.slider("Portfolio PD shock", -20, 100, 0, 5) / 100
    lgd_shock = st.sidebar.slider("Portfolio LGD shock", -20, 80, 0, 5) / 100
    st.sidebar.markdown("#### Scenario")
    scenario_columns = st.sidebar.columns(len(SCENARIOS))
    for column, scenario_name in zip(scenario_columns, SCENARIOS):
        with column:
            _sidebar_state_button(
                scenario_name,
                st.session_state.scenario == scenario_name,
                f"scenario_{scenario_name}",
                set_scenario,
                (scenario_name,),
            )
    st.sidebar.divider()
    if st.sidebar.button(DOCS_PAGE):
        set_page(DOCS_PAGE)
    if st.sidebar.button(BANKING_101_PAGE):
        set_page(BANKING_101_PAGE)
    st.sidebar.caption(f"Current page: {st.session_state.page}")
    return st.session_state.page, pd_shock, lgd_shock, st.session_state.scenario
