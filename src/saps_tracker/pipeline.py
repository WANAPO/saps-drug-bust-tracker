import sqlite3

from saps_tracker.classifier import is_drug_bust
from saps_tracker.db import save_incident
from saps_tracker.models import Incident
from saps_tracker.parser import parse_incident


def ingest_statement(
    conn: sqlite3.Connection,
    text: str,
    source: str = "unknown",
    image_path: str | None = None,
) -> Incident | None:
    """Classify, parse, and store a candidate SAPS statement."""
    if not is_drug_bust(text):
        return None

    incident = parse_incident(text, source=source)
    incident.image_path = image_path
    return save_incident(conn, incident)
