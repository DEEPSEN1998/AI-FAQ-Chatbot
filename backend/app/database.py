"""Small SQLite repository for lead capture.

SQLite is appropriate for one-container deployments and keeps lead data out of
the vector database. Move this module to PostgreSQL when running multiple app
replicas or when the lead volume outgrows a single disk.
"""

import sqlite3
from datetime import datetime, timezone

from backend.app.config import DATA_DIR, SQLITE_PATH
from backend.app.models import LeadCreate


def _connect() -> sqlite3.Connection:
    """Open a short-lived connection; this is safe for FastAPI worker threads."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(SQLITE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Create the lead table and its time-based reporting index if missing."""
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                company TEXT,
                message TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute("CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at)")


def create_lead(lead: LeadCreate) -> int:
    """Insert one validated lead using parameterized SQL and return its ID."""
    created_at = datetime.now(timezone.utc).isoformat()
    with _connect() as connection:
        cursor = connection.execute(
            "INSERT INTO leads (name, email, company, message, created_at) VALUES (?, ?, ?, ?, ?)",
            (lead.name.strip(), str(lead.email).lower(), _clean_optional(lead.company), _clean_optional(lead.message), created_at),
        )
        return int(cursor.lastrowid)


def _clean_optional(value: str | None) -> str | None:
    """Normalize optional browser form fields before storing them."""
    return value.strip() if value and value.strip() else None
