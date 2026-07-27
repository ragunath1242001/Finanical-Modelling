from __future__ import annotations

from src.ui.banking_101 import render_banking_101
from src.ui.context import PortfolioContext


def render_page(ctx: PortfolioContext) -> None:
    render_banking_101()


