import argparse
from pathlib import Path

from saps_tracker.db import attach_image, get_connection, list_incidents, update_status
from saps_tracker.mapper import build_bust_map
from saps_tracker.pipeline import ingest_statement


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="saps-tracker",
        description="SAPS Drug Bust Tracker ingestion, review, and mapping CLI.",
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
    ingest_cmd.add_argument("--image", default=None, help="Optional path to seizure/supply image")
    group = ingest_cmd.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Raw statement text")
    group.add_argument("--file", type=Path, help="Path to a text file containing the statement")

    # attach-image
    img_cmd = subparsers.add_parser("attach-image", help="Attach a supply photo to an incident")
    img_cmd.add_argument("id", type=int, help="Incident ID")
    img_cmd.add_argument("image_path", help="Path to the seizure/supply image file")

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

    # build-map
    map_cmd = subparsers.add_parser("build-map", help="Generate interactive HTML map")
    map_cmd.add_argument(
        "--output",
        default="output/saps_bust_map.html",
        help="Output HTML file path (default: output/saps_bust_map.html)",
    )
    map_cmd.add_argument(
        "--include-pending",
        action="store_true",
        help="Include pending_review incidents in addition to approved ones",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    conn = get_connection(args.db)

    if args.command == "ingest":
        raw_text = args.file.read_text(encoding="utf-8") if args.file else args.text
        saved = ingest_statement(conn, raw_text, source=args.source, image_path=args.image)
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

    if args.command == "attach-image":
        if attach_image(conn, args.id, args.image_path):
            print(f"Attached image to incident #{args.id}.")
            return 0
        print(f"Incident #{args.id} not found.")
        return 1

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
            photo_tag = " [photo]" if inc.image_path else ""
            print(
                f"#{inc.id} [{inc.status}] ({inc.source}) | "
                f"{inc.location or 'Unknown'} | {inc.drug_type or 'Unknown'} | "
                f"Suspects: {inc.suspect_count or 'N/A'} | Value: {value_str}{photo_tag}"
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

    if args.command == "build-map":
        incidents = (
            list_incidents(conn)
            if args.include_pending
            else list_incidents(conn, status="approved")
        )
        out_path = build_bust_map(incidents, output_path=args.output)
        print(f"Generated interactive map at {out_path} ({len(incidents)} incidents).")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
