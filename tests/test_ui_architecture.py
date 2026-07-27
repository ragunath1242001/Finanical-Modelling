from __future__ import annotations

import importlib

from streamlit.testing.v1 import AppTest

from src.risk.stress_testing import SCENARIOS
from src.ui.context import build_portfolio_context, load_app_data
from src.ui.navigation import BANKING_101_PAGE, DOCS_PAGE, MAIN_PAGES
from src.ui.pages import PAGE_REGISTRY, get_page_renderer
from src.ui.pages import executive_overview


def test_page_registry_covers_navigation_pages() -> None:
    expected_pages = [*MAIN_PAGES, DOCS_PAGE, BANKING_101_PAGE]

    assert list(PAGE_REGISTRY) == expected_pages
    assert len(PAGE_REGISTRY) == len(set(PAGE_REGISTRY))


def test_invalid_page_selection_falls_back_to_overview() -> None:
    assert get_page_renderer("Unknown Page") is executive_overview.render_page


def test_sidebar_shortcut_navigation_updates_current_page() -> None:
    at = AppTest.from_file("app.py")
    at.run(timeout=30)
    assert not at.exception

    shortcut = next(button for button in at.button if button.label == "Credit Risk")
    shortcut.click()
    at.run(timeout=30)

    assert not at.exception
    assert at.session_state["page"] == "Credit Risk"
    assert at.session_state["page_select"] == "Credit Risk"


def test_page_modules_are_importable() -> None:
    modules = {
        renderer.__module__
        for renderer in PAGE_REGISTRY.values()
    }

    for module_name in modules:
        module = importlib.import_module(module_name)
        assert callable(module.render_page)


def test_portfolio_context_creation_uses_shared_data() -> None:
    data = load_app_data()
    context = build_portfolio_context(data, 0.0, 0.0, "Baseline")

    assert len(context.data.customers) > 0
    assert len(context.data.loans_raw) > 0
    assert len(context.loans) == len(context.data.loans_raw)
    assert context.portfolio_ead > 0
    assert context.base_rwa > 0
    assert 0 <= context.quality_score <= 100


def test_context_supports_all_sidebar_scenarios() -> None:
    data = load_app_data()

    for scenario_name in SCENARIOS:
        context = build_portfolio_context(data, 0.0, 0.0, scenario_name)
        assert context.stressed["stressed_ecl"] >= 0


def test_portfolio_shocks_change_expected_loss() -> None:
    data = load_app_data()
    baseline = build_portfolio_context(data, 0.0, 0.0, "Baseline")
    shocked = build_portfolio_context(data, 0.25, 0.10, "Baseline")

    assert shocked.portfolio_ecl > baseline.portfolio_ecl
