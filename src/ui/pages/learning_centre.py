from __future__ import annotations

from src.ui.context import PortfolioContext
from src.ui.study_guide import render_study_guide


def render_page(ctx: PortfolioContext) -> None:
    render_study_guide(ctx.data.loans_raw, ctx.base_cet1, ctx.base_rwa)


