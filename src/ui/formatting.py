"""Shared display formatting helpers."""

from __future__ import annotations

from datetime import date, datetime
from math import isnan
from numbers import Number


def _missing(value: object) -> bool:
    return value is None or (isinstance(value, float) and isnan(value))


def format_currency(value: float | int | None, symbol: str = "EUR", decimals: int = 0) -> str:
    if _missing(value):
        return "Not available"
    prefix = f"{symbol} " if symbol and len(symbol) > 1 else symbol
    sign = "-" if float(value) < 0 else ""
    return f"{sign}{prefix}{abs(float(value)):,.{decimals}f}"


def format_percent(value: float | int | None, decimals: int = 2) -> str:
    if _missing(value):
        return "Not available"
    return f"{float(value):.{decimals}%}"


def format_ratio(value: float | int | None, decimals: int = 2) -> str:
    if _missing(value):
        return "Not available"
    return f"{float(value):,.{decimals}f}x"


def format_bps(value: float | int | None, decimals: int = 0) -> str:
    if _missing(value):
        return "Not available"
    return f"{float(value):,.{decimals}f} bps"


def format_count(value: Number | None) -> str:
    if _missing(value):
        return "Not available"
    return f"{int(value):,}"


def format_date(value: date | datetime | str | None) -> str:
    if _missing(value):
        return "Not available"
    if isinstance(value, str):
        value = datetime.fromisoformat(value).date()
    if isinstance(value, datetime):
        value = value.date()
    return value.strftime("%d %b %Y")
