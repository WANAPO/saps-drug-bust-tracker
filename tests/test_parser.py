from saps_tracker.parser import (
    extract_drug_type,
    extract_location,
    extract_suspect_count,
    extract_value_zar,
    parse_incident,
)

MARGATE_RELEASE = """OFFICE OF THE PROVINCIAL COMMISSIONER: KWAZULU-NATAL
TEENAGER ARRESTED WITH DRUGS WORTH OVER R8 MILLION
DURBAN: 17 November 2026 – Police in KwaZulu-Natal have arrested an 18-year-old boy
for possession and dealing in drugs on Marine Drive in Margate on Tuesday, 16 November 2026.
During the operation police recovered a substantial quantity of drugs with an estimated
street value of over R8 million. He is due to appear before Port Shepstone Magistrates Court."""

MAGUDU_RELEASE = """OFFICE OF THE PROVINCIAL COMMISSIONER: KWAZULU-NATAL
THREE SUSPECTS ARRESTED WITH R3 MILLION WORTH OF DAGGA IN MAGUDU
DURBAN: 19 November 2026 – Police in Magudu, together with officers from Ulundi K9 Unit,
conducted an intelligence-driven operation that resulted in the arrest of three suspects
aged between 35 and 40 years old and the recovery of 47 bales of compressed dagga with an
estimated street value of almost R3 million in two separate incidents."""


def test_extracts_drug_type():
    assert extract_drug_type(MARGATE_RELEASE) == "drugs"
    assert extract_drug_type(MAGUDU_RELEASE) == "dagga"


def test_extracts_value_zar():
    assert extract_value_zar(MARGATE_RELEASE) == 8_000_000.0
    assert extract_value_zar(MAGUDU_RELEASE) == 3_000_000.0
    assert extract_value_zar("Further recovery worth R800 000.") == 800_000.0


def test_extracts_suspect_count_without_confusing_ages():
    assert extract_suspect_count(MARGATE_RELEASE) == 1
    assert extract_suspect_count(MAGUDU_RELEASE) == 3
    assert extract_suspect_count("12 suspects apprehended with tik.") == 12


def test_extracts_incident_location_ignoring_dateline():
    assert extract_location(MARGATE_RELEASE) == "Margate"
    assert extract_location(MAGUDU_RELEASE) == "Magudu"


def test_parse_incident_full():
    inc = parse_incident(MAGUDU_RELEASE, source="saps_whatsapp")
    assert inc.source == "saps_whatsapp"
    assert inc.location == "Magudu"
    assert inc.drug_type == "dagga"
    assert inc.suspect_count == 3
    assert inc.estimated_value_zar == 3_000_000.0
    assert inc.status == "pending_review"
