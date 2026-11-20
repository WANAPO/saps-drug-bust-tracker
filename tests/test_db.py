import pytest

from saps_tracker.db import get_connection, list_incidents, save_incident, update_status
from saps_tracker.parser import parse_incident


def test_save_and_list_incidents_in_memory():
    conn = get_connection(":memory:")
    inc = parse_incident(
        "THREE SUSPECTS ARRESTED WITH R3 MILLION WORTH OF DAGGA IN MAGUDU.",
        source="saps_whatsapp",
    )

    saved = save_incident(conn, inc)
    assert saved is not None
    assert saved.id == 1

    pending = list_incidents(conn, status="pending_review")
    assert len(pending) == 1
    assert pending[0].location == "Magudu"
    assert pending[0].estimated_value_zar == 3_000_000.0


def test_rejects_duplicate_incidents():
    conn = get_connection(":memory:")
    text = "THREE SUSPECTS ARRESTED WITH R3 MILLION WORTH OF DAGGA IN MAGUDU."

    first = save_incident(conn, parse_incident(text, source="whatsapp"))
    duplicate = save_incident(conn, parse_incident(f"  {text}  ", source="x"))

    assert first is not None
    assert duplicate is None
    assert len(list_incidents(conn)) == 1


def test_update_status_editorial_gate():
    conn = get_connection(":memory:")
    saved = save_incident(
        conn,
        parse_incident("Suspect arrested with dagga in Margate.", source="whatsapp"),
    )
    assert saved is not None and saved.id is not None

    assert update_status(conn, saved.id, "approved") is True
    assert len(list_incidents(conn, status="pending_review")) == 0
    assert len(list_incidents(conn, status="approved")) == 1

    with pytest.raises(ValueError):
        update_status(conn, saved.id, "published")
