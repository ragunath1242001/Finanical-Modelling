from __future__ import annotations

import pandas as pd

from src.config import DATA_DIR
from src.data.generate_synthetic_data import main as generate_data


def _read_or_generate(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    if not path.exists():
        generate_data()
    return pd.read_csv(path)


def load_customers() -> pd.DataFrame:
    return _read_or_generate("customers.csv")


def load_loans() -> pd.DataFrame:
    return _read_or_generate("loans.csv")


def load_transactions() -> pd.DataFrame:
    return _read_or_generate("transactions.csv")


def load_financials() -> pd.DataFrame:
    return _read_or_generate("financials.csv")
