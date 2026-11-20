from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Incident:
    """Structured representation of a candidate SAPS drug bust."""

    raw_text: str
    source: str = "unknown"
    location: str | None = None
    drug_type: str | None = None
    suspect_count: int | None = None
    estimated_value_zar: float | None = None
    status: str = "pending_review"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    id: int | None = None
