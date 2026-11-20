import sqlite3

from saps_tracker.classifier import is_drug_bust
from saps_tracker.db import save_incident
from saps_tracker.models import Incident
from saps_tracker.parser import parse_incident


def ingest_statement(
    conn: sqlite3.Connection,
    text: str,
    source: str = "unknown",
) -> Incident | None:
    """Classify, parse, and store a candidate SAPS statement.

    Returns the saved Incident (with database ID) if accepted and new,
    or None if the text is not a drug bust or is a duplicate.
    """
    if not is_drug_bust(text):
        return None

    incident = parse_incident(text, source=source)
    return save_incident(conn, incident)
