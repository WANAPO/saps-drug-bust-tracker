import re

from saps_tracker.classifier import DRUG_KEYWORDS
from saps_tracker.models import Incident

MULTIPLIERS = {
    "k": 1_000.0,
    "thousand": 1_000.0,
    "m": 1_000_000.0,
    "million": 1_000_000.0,
    "b": 1_000_000_000.0,
    "billion": 1_000_000_000.0,
}

WORD_NUMBERS = {
    "one": 1,
    "a": 1,
    "an": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}

KNOWN_LOCATIONS = (
    # KwaZulu-Natal focus
    "Margate",
    "Magudu",
    "Port Shepstone",
    "Ulundi",
    "Empangeni",
    "Richards Bay",
    "Durban",
    "Pietermaritzburg",
    "Newcastle",
    "Ladysmith",
    "Umhlanga",
    "Verulam",
    "Phoenix",
    "Chatsworth",
    "Pinetown",
    "Amanzimtoti",
    "Tongaat",
    "KwaDukuza",
    "Stanger",
    "Vryheid",
    "Pongola",
    "Eshowe",
    "Kokstad",
    "Ixopo",
    "Estcourt",
    # Major national metros
    "Johannesburg",
    "Pretoria",
    "Cape Town",
    "Gqeberha",
    "East London",
    "Bloemfontein",
    "Polokwane",
    "Mbombela",
    "Kimberley",
    "Mahikeng",
)

RAND_PATTERN = re.compile(
    r"\bR\s*(\d[\d\s,]*(?:\.\d+)?)\s*(thousand|million|billion|k|m|b)?\b",
    re.IGNORECASE,
)

# Matches e.g. "3 suspects", "three suspects", "two occupants"
PLURAL_SUSPECT_PATTERN = re.compile(
    r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+"
    r"(?:suspects|occupants|men|women|individuals|persons)\b",
    re.IGNORECASE,
)

# Matches singular arrests like "an 18-year-old boy", "a 30-year-old man", "the driver"
SINGULAR_SUSPECT_PATTERN = re.compile(
    r"\b(?:an?\s+(?:\d+-year-old\s+)?(?:suspect|man|woman|boy|girl|driver|foreign national)"
    r"|the\s+(?:suspect|driver))\b",
    re.IGNORECASE,
)

# Strips leading provincial media-desk dateline like "DURBAN: 17 November 2026 –"
DATELINE_PATTERN = re.compile(
    r"^[A-Z\s-]+:\s*\d{1,2}\s+[A-Za-z]+\s+\d{4}\s*[–—-]\s*",
    re.MULTILINE,
)


def extract_drug_type(text: str) -> str | None:
    """Return the matching drug keyword in normalized form, or None."""
    if not text or not text.strip():
        return None

    normalized = text.lower()
    ordered_keywords = sorted(DRUG_KEYWORDS, key=len, reverse=True)
    for keyword in ordered_keywords:
        if re.search(rf"\b{re.escape(keyword)}\b", normalized):
            return keyword
    return None


def extract_value_zar(text: str) -> float | None:
    """Extract the largest Rand value mentioned in the text as a float in ZAR."""
    if not text or not text.strip():
        return None

    values: list[float] = []
    for match in RAND_PATTERN.finditer(text):
        raw_number, suffix = match.groups()
        cleaned_number = re.sub(r"[\s,]+", "", raw_number)
        try:
            amount = float(cleaned_number)
        except ValueError:
            continue

        if suffix:
            amount *= MULTIPLIERS[suffix.lower()]

        values.append(amount)

    return max(values) if values else None


def extract_suspect_count(text: str) -> int | None:
    """Extract the number of suspects arrested, avoiding age numbers."""
    if not text or not text.strip():
        return None

    plural_match = PLURAL_SUSPECT_PATTERN.search(text)
    if plural_match:
        token = plural_match.group(1).lower()
        return int(token) if token.isdigit() else WORD_NUMBERS.get(token)

    if SINGULAR_SUSPECT_PATTERN.search(text):
        return 1

    return None


def extract_location(text: str) -> str | None:
    """Extract the first known town/area outside the media-desk dateline."""
    if not text or not text.strip():
        return None

    body = DATELINE_PATTERN.sub("", text)
    for place in KNOWN_LOCATIONS:
        if re.search(rf"\b{re.escape(place)}\b", body, re.IGNORECASE):
            return place
    return None


def parse_incident(text: str, source: str = "unknown") -> Incident:
    """Build a structured Incident from a raw SAPS statement."""
    return Incident(
        raw_text=text,
        source=source,
        location=extract_location(text),
        drug_type=extract_drug_type(text),
        suspect_count=extract_suspect_count(text),
        estimated_value_zar=extract_value_zar(text),
    )
