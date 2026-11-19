DRUG_KEYWORDS = (
    "dagga",
    "drugs",
    "cocaine",
    "heroin",
    "tik",
    "nyaope",
    "mandrax",
    "cannabis",
    "methamphetamine",
    "narcotics",
    "crystal meth",
)

ACTION_KEYWORDS = (
    "arrest",
    "arrested",
    "seize",
    "seized",
    "bust",
    "apprehended",
    "confiscated",
    "recovered",
)


def is_drug_bust(text: str) -> bool:
    """Return True if the text references both a drug term and a police action."""
    if not text or not text.strip():
        return False

    normalized = text.lower()
    has_drug = any(keyword in normalized for keyword in DRUG_KEYWORDS)
    has_action = any(keyword in normalized for keyword in ACTION_KEYWORDS)
    return has_drug and has_action
