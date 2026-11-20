import hashlib
import sqlite3
from pathlib import Path

from saps_tracker.models import Incident

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash TEXT NOT NULL UNIQUE,
    raw_text TEXT NOT NULL,
    source TEXT NOT NULL,
    location TEXT,
    drug_type TEXT,
    suspect_count INTEGER,
    estimated_value_zar REAL,
    image_path TEXT,
    status TEXT NOT NULL DEFAULT 'pending_review',
    created_at TEXT NOT NULL
);
"""

VALID_STATUSES = {"pending_review", "approved", "rejected"}


def compute_content_hash(raw_text: str) -> str:
    """Return a deterministic SHA-256 hash for whitespace-normalized text."""
    normalized = " ".join(raw_text.split()).lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _ensure_migrations(conn: sqlite3.Connection) -> None:
    """Safely add newer columns to existing SQLite databases."""
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(incidents)").fetchall()}
    if "image_path" not in columns:
        conn.execute("ALTER TABLE incidents ADD COLUMN image_path TEXT")
        conn.commit()


def get_connection(db_path: str | Path = "data/saps_tracker.db") -> sqlite3.Connection:
    """Open a SQLite connection and ensure the incidents schema exists."""
    if str(db_path) != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    _ensure_migrations(conn)
    conn.commit()
    return conn


def save_incident(conn: sqlite3.Connection, incident: Incident) -> Incident | None:
    """Insert an Incident into SQLite. Return None if a duplicate already exists."""
    content_hash = compute_content_hash(incident.raw_text)
    try:
        cursor = conn.execute(
            """
            INSERT INTO incidents (
                content_hash,
                raw_text,
                source,
                location,
                drug_type,
                suspect_count,
                estimated_value_zar,
                image_path,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                content_hash,
                incident.raw_text,
                incident.source,
                incident.location,
                incident.drug_type,
                incident.suspect_count,
                incident.estimated_value_zar,
                incident.image_path,
                incident.status,
                incident.created_at,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return None

    incident.id = cursor.lastrowid
    return incident


def list_incidents(
    conn: sqlite3.Connection,
    status: str | None = None,
) -> list[Incident]:
    """Return stored incidents, optionally filtered by editorial review status."""
    if status is not None:
        rows = conn.execute(
            "SELECT * FROM incidents WHERE status = ? ORDER BY id ASC",
            (status,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM incidents ORDER BY id ASC").fetchall()

    return [
        Incident(
            id=row["id"],
            raw_text=row["raw_text"],
            source=row["source"],
            location=row["location"],
            drug_type=row["drug_type"],
            suspect_count=row["suspect_count"],
            estimated_value_zar=row["estimated_value_zar"],
            image_path=row["image_path"],
            status=row["status"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


def update_status(conn: sqlite3.Connection, incident_id: int, status: str) -> bool:
    """Update the editorial review status of an incident. Return True if updated."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status!r}. Expected one of {sorted(VALID_STATUSES)}.")

    cursor = conn.execute(
        "UPDATE incidents SET status = ? WHERE id = ?",
        (status, incident_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def attach_image(conn: sqlite3.Connection, incident_id: int, image_path: str) -> bool:
    """Attach a seizure/supply photo path to an existing incident."""
    cursor = conn.execute(
        "UPDATE incidents SET image_path = ? WHERE id = ?",
        (image_path, incident_id),
    )
    conn.commit()
    return cursor.rowcount > 0
