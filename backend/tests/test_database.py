"""Focused tests for the local lead repository; no NVIDIA call is made."""

from backend.app import database
from backend.app.models import LeadCreate


def test_create_lead_persists_normalized_values(tmp_path, monkeypatch):
    """A submitted lead is stored safely and receives an incremental ID."""
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)
    monkeypatch.setattr(database, "SQLITE_PATH", tmp_path / "app.db")
    database.initialize_database()

    lead_id = database.create_lead(
        LeadCreate(name="  Ada Lovelace ", email="ADA@EXAMPLE.COM", company="  Acme  ", message=" Need a demo ")
    )

    with database._connect() as connection:
        row = connection.execute("SELECT name, email, company, message FROM leads WHERE id = ?", (lead_id,)).fetchone()
    assert dict(row) == {"name": "Ada Lovelace", "email": "ada@example.com", "company": "Acme", "message": "Need a demo"}
