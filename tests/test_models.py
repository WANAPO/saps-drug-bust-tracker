from saps_tracker.models import Incident


def test_incident_defaults():
    inc = Incident(raw_text="Suspect arrested with dagga.")
    assert inc.raw_text == "Suspect arrested with dagga."
    assert inc.source == "unknown"
    assert inc.status == "pending_review"
    assert inc.suspect_count is None
    assert inc.id is None
    assert inc.created_at
