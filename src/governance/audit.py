from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

import pandas as pd

from src.config import AUDIT_DB


def init_audit() -> None:
    with sqlite3.connect(AUDIT_DB) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                actor TEXT NOT NULL,
                module TEXT NOT NULL,
                action TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                reason TEXT
            )
            """
        )


def log_event(actor: str, module: str, action: str, old_value: str = "", new_value: str = "", reason: str = "") -> None:
    init_audit()
    with sqlite3.connect(AUDIT_DB) as con:
        con.execute(
            "INSERT INTO audit_events(timestamp, actor, module, action, old_value, new_value, reason) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), actor, module, action, old_value, new_value, reason),
        )


def read_events(limit: int = 25) -> pd.DataFrame:
    init_audit()
    with sqlite3.connect(AUDIT_DB) as con:
        return pd.read_sql_query("SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", con, params=(limit,))
