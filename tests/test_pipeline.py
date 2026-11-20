from saps_tracker.cli import main
from saps_tracker.db import get_connection, list_incidents
from saps_tracker.pipeline import ingest_statement


def test_pipeline_filters_parses_and_deduplicates():
    conn = get_connection(":memory:")

    # Non-drug arrest should be ignored
    ignored = ingest_statement(
        conn,
        "TWO SUSPECTS ARRESTED FOR UNLICENSED FIREARM IN DURBAN.",
        source="x",
    )
    assert ignored is None

    # Drug bust should be parsed and saved as pending_review
    statement = "THREE SUSPECTS ARRESTED WITH R3 MILLION WORTH OF DAGGA IN MAGUDU."
    first = ingest_statement(conn, statement, source="whatsapp")
    assert first is not None
    assert first.id == 1
    assert first.location == "Magudu"
    assert first.status == "pending_review"

    # Duplicate repost should be ignored
    duplicate = ingest_statement(conn, statement, source="x")
    assert duplicate is None
    assert len(list_incidents(conn)) == 1


def test_cli_end_to_end_workflow(tmp_path, capsys):
    db_file = tmp_path / "test.db"

    rc = main(
        [
            "--db",
            str(db_file),
            "ingest",
            "--source",
            "whatsapp",
            "--text",
            "TEENAGER ARRESTED WITH DRUGS WORTH OVER R8 MILLION IN MARGATE.",
        ]
    )
    assert rc == 0
    assert "Saved #1 [pending_review]" in capsys.readouterr().out

    rc = main(["--db", str(db_file), "approve", "1"])
    assert rc == 0
    assert "Incident #1 marked as approved." in capsys.readouterr().out

    rc = main(["--db", str(db_file), "list", "--status", "approved"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "#1 [approved]" in out
    assert "Margate" in out
