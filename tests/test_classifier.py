from saps_tracker.classifier import is_drug_bust


def test_detects_drug_bust_with_arrest_and_seizure():
    statement = "THREE SUSPECTS ARRESTED WITH R3 MILLION WORTH OF DAGGA IN MAGUDU."
    assert is_drug_bust(statement) is True


def test_ignores_non_drug_arrest():
    statement = "TWO SUSPECTS ARRESTED FOR POSSESSION OF UNLICENSED FIREARM."
    assert is_drug_bust(statement) is False


def test_ignores_drug_mention_without_enforcement_action():
    statement = "Community workshop held today to discuss dagga awareness."
    assert is_drug_bust(statement) is False


def test_handles_empty_or_whitespace_input():
    assert is_drug_bust("") is False
    assert is_drug_bust("   \n\t  ") is False
