from __future__ import annotations

import re
from pathlib import Path

from src.config import APP_NAME, PORTFOLIO_DISCLAIMER
from src.ui.formatting import format_bps, format_count, format_currency, format_date, format_percent, format_ratio
from src.ui.navigation import MAIN_PAGES, NAVIGATION_GROUPS
from src.ui.pages import PAGE_REGISTRY


ROOT = Path(__file__).resolve().parents[1]


def test_project_identity_and_disclaimer_are_consistent():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert APP_NAME in readme
    assert "educational portfolio demonstration" in readme
    assert "production banking system" in readme
    assert PORTFOLIO_DISCLAIMER.startswith("This is an independent educational portfolio project")


def test_readme_required_sections_exist():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    required = [
        "## Demo",
        "## Executive Overview",
        "## Key Capabilities",
        "## End-To-End Use Cases",
        "## Architecture",
        "## Repository Structure",
        "## Methodology And Assumptions",
        "## Testing",
        "## Technology Stack",
        "## Synthetic Data Statement",
        "## Limitations",
        "## Interview Value",
        "## Deployment",
        "## Licence",
    ]
    for section in required:
        assert section in readme


def test_required_phase6_documents_exist():
    required = [
        "docs/glossary.md",
        "docs/formulas.md",
        "docs/model_cards.md",
        "docs/data_dictionary.md",
        "docs/architecture.md",
        "docs/end_to_end_walkthroughs.md",
        "docs/interview_guide.md",
        "docs/portfolio_talking_points.md",
        "docs/cv_linkedin_examples.md",
        "docs/deployment.md",
        "docs/final_quality_report.md",
        "docs/future_roadmap.md",
        "docs/screenshots_checklist.md",
    ]
    for relative in required:
        assert (ROOT / relative).exists(), relative


def test_markdown_local_links_point_to_existing_files():
    markdown_files = [ROOT / "README.md", *ROOT.glob("docs/**/*.md")]
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    missing = []
    for file in markdown_files:
        text = file.read_text(encoding="utf-8")
        for target in pattern.findall(text):
            if target.startswith(("http://", "https://", "mailto:")) or target.startswith("#"):
                continue
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            if not (file.parent / clean).resolve().exists():
                missing.append(f"{file.relative_to(ROOT)} -> {target}")
    assert missing == []


def test_screenshot_references_are_truthful():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for image in re.findall(r"!\[[^\]]+\]\(([^)]+)\)", readme):
        assert (ROOT / image).exists(), image
    checklist = (ROOT / "docs/screenshots_checklist.md").read_text(encoding="utf-8")
    assert "Recommended final screenshots to capture" in checklist


def test_navigation_groups_cover_main_pages_without_duplicates():
    grouped = [page for pages in NAVIGATION_GROUPS.values() for page in pages]
    assert set(grouped) == set(MAIN_PAGES)
    assert len(grouped) == len(set(grouped))
    assert "Executive Overview" in NAVIGATION_GROUPS["Overview"]


def test_page_registry_contains_all_pages():
    assert len(PAGE_REGISTRY) == 19
    assert set(MAIN_PAGES).issubset(PAGE_REGISTRY)
    assert len(PAGE_REGISTRY) == len(set(PAGE_REGISTRY))


def test_formatting_utilities_handle_common_values():
    assert format_currency(1234.5) == "EUR 1,234"
    assert format_currency(-1234.5, symbol="£") == "-£1,234"
    assert format_percent(0.1234, 1) == "12.3%"
    assert format_ratio(1.234, 2) == "1.23x"
    assert format_bps(125) == "125 bps"
    assert format_count(12345) == "12,345"
    assert format_date("2026-07-27") == "27 Jul 2026"
    assert format_currency(None) == "Not available"


def test_model_cards_have_required_card_fields():
    text = (ROOT / "docs/model_cards.md").read_text(encoding="utf-8")
    for heading in ["Credit PD Model", "IFRS 9 Scenario ECL Engine", "Core Risk Engines", "Phase 5 Model-Risk Card", "Fraud Classifier", "Forecasting Baseline"]:
        assert f"## {heading}" in text
    for field in ["Purpose", "Inputs", "Output", "Method", "Limitations", "Monitoring"]:
        assert f"- {field}:" in text
