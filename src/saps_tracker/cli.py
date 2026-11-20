import argparse
from pathlib import Path

from saps_tracker.db import get_connection, list_incidents, update_status
from saps_tracker.pipeline import ingest_statement


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="saps-tracker",
        description="SAPS Drug Bust Tracker ingestion and editorial review CLI.",
    )
    parser.add_argument(
        "--db",
        default="data/saps_tracker.db",
        help="Path to SQLite database file (default: data/saps_tracker.db)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ingest
    ingest_cmd = subparsers.add_parser("ingest", help="Ingest a SAPS statement")
    ingest_cmd.add_argument("--source", default="manual", help="Source channel (e.g. whatsapp, x)")
    group = ingest_cmd.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Raw statement text")
    group.add_argument("--file", type=Path, help="Path to a text file containing the statement")

    # list
    list_cmd = subparsers.add_parser("list", help="List stored incidents")
    list_cmd.add_argument(
        "--status",
        choices=["pending_review", "approved", "rejected"],
        default=None,
        help="Filter incidents by editorial status",
    )

    # approve / reject
    approve_cmd = subparsers.add_parser("approve", help="Approve an incident for publishing")
    approve_cmd.add_argument("id", type=int, help="Incident ID")

    reject_cmd = subparsers.add_parser("reject", help="Reject an incident")
    reject_cmd.add_argument("id", type=int, help="Incident ID")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    conn = get_connection(args.db)

    if args.command == "ingest":
        raw_text = args.file.read_text(encoding="utf-8") if args.file else args.text
        saved = ingest_statement(conn, raw_text, source=args.source)
        if saved is None:
            print("Ignored (not a drug bust or already recorded).")
        else:
            value_str = (
                f"R{saved.estimated_value_zar:,.0f}"
                if saved.estimated_value_zar is not None
                else "N/A"
            )
            print(
                f"Saved #{saved.id} [{saved.status}] | "
                f"Location: {saved.location or 'Unknown'} | "
                f"Drug: {saved.drug_type or 'Unknown'} | "
                f"Suspects: {saved.suspect_count or 'N/A'} | "
                f"Value: {value_str}"
            )
        return 0

    if args.command == "list":
        incidents = list_incidents(conn, status=args.status)
        if not incidents:
            print("No incidents found.")
            return 0
        for inc in incidents:
            value_str = (
                f"R{inc.estimated_value_zar:,.0f}"
                if inc.estimated_value_zar is not None
                else "N/A"
            )
            print(
                f"#{inc.id} [{inc.status}] ({inc.source}) | "
                f"{inc.location or 'Unknown'} | {inc.drug_type or 'Unknown'} | "
                f"Suspects: {inc.suspect_count or 'N/A'} | Value: {value_str}"
            )
        return 0

    if args.command in {"approve", "reject"}:
        target_status = "approved" if args.command == "approve" else "rejected"
        updated = update_status(conn, args.id, target_status)
        if updated:
            print(f"Incident #{args.id} marked as {target_status}.")
            return 0
        print(f"Incident #{args.id} not found.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
