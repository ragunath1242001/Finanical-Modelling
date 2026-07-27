"""Append-only educational audit logging."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config import AUDIT_DB as DEFAULT_AUDIT_DB
from src.governance.models import AuditEvent


AUDIT_DB: Path = DEFAULT_AUDIT_DB


def init_audit() -> None:
    AUDIT_DB.parent.mkdir(parents=True, exist_ok=True)
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
                reason TEXT,
                user_role TEXT DEFAULT '',
                object_type TEXT DEFAULT '',
                object_id TEXT DEFAULT '',
                approval_status TEXT DEFAULT ''
            )
            """
        )
        existing = {row[1] for row in con.execute("PRAGMA table_info(audit_events)").fetchall()}
        for column in ["user_role", "object_type", "object_id", "approval_status"]:
            if column not in existing:
                con.execute(f"ALTER TABLE audit_events ADD COLUMN {column} TEXT DEFAULT ''")


def append_audit_event(event: AuditEvent) -> None:
    init_audit()
    with sqlite3.connect(AUDIT_DB) as con:
        con.execute(
            """
            INSERT INTO audit_events(
                timestamp, actor, module, action, old_value, new_value, reason,
                user_role, object_type, object_id, approval_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.timestamp.isoformat(),
                event.user_role,
                event.module,
                event.action,
                event.previous_value,
                event.new_value,
                event.reason,
                event.user_role,
                event.object_type,
                event.object_id,
                event.approval_status,
            ),
        )


def make_audit_event(
    event_id: str,
    user_role: str,
    module: str,
    object_type: str,
    object_id: str,
    action: str,
    previous_value: str,
    new_value: str,
    reason: str,
    approval_status: str = "",
    timestamp: datetime | None = None,
) -> AuditEvent:
    return AuditEvent(
        event_id=event_id,
        timestamp=timestamp or datetime.now(timezone.utc),
        user_role=user_role,
        module=module,
        object_type=object_type,
        object_id=object_id,
        action=action,
        previous_value=previous_value,
        new_value=new_value,
        reason=reason,
        approval_status=approval_status,
    )


def log_event(actor: str, module: str, action: str, old_value: str = "", new_value: str = "", reason: str = "") -> None:
    append_audit_event(
        make_audit_event(
            event_id="LEGACY",
            user_role=actor,
            module=module,
            object_type="Event",
            object_id=module,
            action=action,
            previous_value=old_value,
            new_value=new_value,
            reason=reason,
        )
    )


def read_events(limit: int = 25, issue_id: str | None = None, role: str | None = None, action: str | None = None) -> pd.DataFrame:
    init_audit()
    query = "SELECT * FROM audit_events"
    filters = []
    params: list[object] = []
    if issue_id:
        filters.append("object_id = ?")
        params.append(issue_id)
    if role:
        filters.append("(user_role = ? OR actor = ?)")
        params.extend([role, role])
    if action:
        filters.append("action = ?")
        params.append(action)
    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY timestamp DESC, id DESC LIMIT ?"
    params.append(limit)
    with sqlite3.connect(AUDIT_DB) as con:
        return pd.read_sql_query(query, con, params=params)


def audit_events_chronological(events: list[AuditEvent]) -> bool:
    return all(left.timestamp <= right.timestamp for left, right in zip(events, events[1:]))


def audit_events_to_frame(events: list[AuditEvent]) -> pd.DataFrame:
    if not events:
        return pd.DataFrame(columns=["event_id", "timestamp", "user_role", "module", "object_type", "object_id", "action"])
    return pd.DataFrame([event.__dict__ for event in events]).sort_values("timestamp")
