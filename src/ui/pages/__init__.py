from __future__ import annotations

from collections.abc import Callable

from src.ui.context import PortfolioContext
from src.ui.navigation import BANKING_101_PAGE, DOCS_PAGE
from src.ui.pages import (
    ai_governance,
    banking_foundations,
    basel_capital,
    bcbs239,
    climate_risk,
    credit_risk,
    crr3,
    dora,
    executive_overview,
    financial_crime,
    forecasting,
    geopolitical_reverse_stress,
    ifrs9,
    learning_centre,
    liquidity,
    model_risk,
    regulatory_reporting,
    stress_testing,
    xva,
)

PageRenderer = Callable[[PortfolioContext], None]

PAGE_REGISTRY: dict[str, PageRenderer] = {
    "Executive Overview": executive_overview.render_page,
    "Credit Risk": credit_risk.render_page,
    "IFRS 9 ECL": ifrs9.render_page,
    "Basel Capital and IRB": basel_capital.render_page,
    "CRR3 Basel Final Reforms": crr3.render_page,
    "COREP/FINREP Reporting": regulatory_reporting.render_page,
    "Stress Testing": stress_testing.render_page,
    "Geopolitical Reverse Stress": geopolitical_reverse_stress.render_page,
    "Liquidity and Leverage": liquidity.render_page,
    "Fraud and AML": financial_crime.render_page,
    "Forecasting": forecasting.render_page,
    "BCBS 239 Governance": bcbs239.render_page,
    "Model Risk Management": model_risk.render_page,
    "EU AI Act Governance": ai_governance.render_page,
    "DORA Operational Resilience": dora.render_page,
    "ESG Climate Credit Risk": climate_risk.render_page,
    "XVA Counterparty Risk": xva.render_page,
    DOCS_PAGE: learning_centre.render_page,
    BANKING_101_PAGE: banking_foundations.render_page,
}


def get_page_renderer(page_name: str) -> PageRenderer:
    return PAGE_REGISTRY.get(page_name, executive_overview.render_page)
