LOCATION_COORDS: dict[str, tuple[float, float]] = {
    # KwaZulu-Natal
    "Margate": (-30.8636, 30.3703),
    "Magudu": (-27.5333, 31.6500),
    "Port Shepstone": (-30.7414, 30.4547),
    "Ulundi": (-28.3352, 31.4162),
    "Empangeni": (-28.7620, 31.8933),
    "Richards Bay": (-28.7807, 32.0383),
    "Durban": (-29.8587, 31.0218),
    "Pietermaritzburg": (-29.6006, 30.3794),
    "Newcastle": (-27.7580, 29.9318),
    "Ladysmith": (-28.5597, 29.7808),
    "Umhlanga": (-29.7253, 31.0858),
    "Verulam": (-29.6436, 31.0492),
    "Phoenix": (-29.7069, 31.0114),
    "Chatsworth": (-29.9144, 30.8889),
    "Pinetown": (-29.8167, 30.8500),
    "Amanzimtoti": (-30.0500, 30.8833),
    "Tongaat": (-29.5750, 31.1236),
    "KwaDukuza": (-29.3282, 31.2895),
    "Stanger": (-29.3282, 31.2895),
    "Vryheid": (-27.7695, 30.7917),
    "Pongola": (-27.3833, 31.6167),
    "Eshowe": (-28.8865, 31.4699),
    "Kokstad": (-30.5472, 29.4241),
    "Ixopo": (-30.1564, 30.0642),
    "Estcourt": (-29.0046, 29.8716),
    # National metros
    "Johannesburg": (-26.2041, 28.0473),
    "Pretoria": (-25.7479, 28.2293),
    "Cape Town": (-33.9249, 18.4241),
    "Gqeberha": (-33.9608, 25.6022),
    "East London": (-33.0292, 27.8546),
    "Bloemfontein": (-29.0852, 26.1596),
    "Polokwane": (-23.9045, 29.4689),
    "Mbombela": (-25.4753, 30.9694),
    "Kimberley": (-28.7282, 24.7499),
    "Mahikeng": (-25.8560, 25.6403),
}


def get_coordinates(location: str | None) -> tuple[float, float] | None:
    """Return (lat, lon) for a known South African location, case-insensitively."""
    if not location:
        return None
    for name, coords in LOCATION_COORDS.items():
        if name.lower() == location.strip().lower():
            return coords
    return None
