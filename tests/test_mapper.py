from saps_tracker.geocoder import get_coordinates
from saps_tracker.mapper import build_bust_map
from saps_tracker.models import Incident


def test_geocoder_resolves_kzn_towns():
    assert get_coordinates("Magudu") == (-27.5333, 31.65)
    assert get_coordinates("margate") == (-30.8636, 30.3703)
    assert get_coordinates("Unknown Village") is None


def test_build_bust_map_embeds_supply_photo_and_totals(tmp_path):
    tiny_png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00"
        b"\x00\x04\x00\x01\xf6\x178U\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    photo_file = tmp_path / "magudu_bales.png"
    photo_file.write_bytes(tiny_png)

    incidents = [
        Incident(
            id=1,
            raw_text="THREE SUSPECTS ARRESTED WITH R3 MILLION WORTH OF DAGGA IN MAGUDU.",
            source="whatsapp",
            location="Magudu",
            drug_type="dagga",
            suspect_count=3,
            estimated_value_zar=3_000_000.0,
            image_path=str(photo_file),
            status="approved",
        ),
        Incident(
            id=2,
            raw_text="TEENAGER ARRESTED WITH DRUGS WORTH OVER R8 MILLION IN MARGATE.",
            source="x",
            location="Margate",
            drug_type="drugs",
            suspect_count=1,
            estimated_value_zar=8_000_000.0,
            status="approved",
        ),
    ]

    map_file = tmp_path / "bust_map.html"
    result_path = build_bust_map(incidents, output_path=map_file)

    assert result_path.is_file()
    html_output = result_path.read_text(encoding="utf-8")
    assert "Magudu" in html_output
    assert "Margate" in html_output
    assert "R11,000,000" in html_output
    assert "data:image/png;base64," in html_output
