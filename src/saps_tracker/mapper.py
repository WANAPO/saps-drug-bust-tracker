import base64
import html
import mimetypes
from pathlib import Path

import folium

from saps_tracker.geocoder import get_coordinates
from saps_tracker.models import Incident

KZN_CENTER = (-28.85, 30.85)


def _encode_image_data_uri(image_path: str | None) -> str | None:
    """Read a local image file and return a base64 data URI, or None if missing."""
    if not image_path:
        return None
    path = Path(image_path)
    if not path.is_file():
        return None

    mime_type, _ = mimetypes.guess_type(path.name)
    if not mime_type or not mime_type.startswith("image/"):
        mime_type = "image/jpeg"

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _build_popup_html(incident: Incident) -> str:
    """Render an HTML popup card with optional seizure/supply photo."""
    location = html.escape(incident.location or "Unknown Location")
    drug = html.escape((incident.drug_type or "Unspecified").upper())
    source = html.escape(incident.source)
    suspects = str(incident.suspect_count) if incident.suspect_count is not None else "N/A"
    value_str = (
        f"R{incident.estimated_value_zar:,.0f}"
        if incident.estimated_value_zar is not None
        else "Undisclosed"
    )
    excerpt = html.escape(incident.raw_text.strip()[:260])
    if len(incident.raw_text.strip()) > 260:
        excerpt += "..."

    image_html = ""
    data_uri = _encode_image_data_uri(incident.image_path)
    if data_uri:
        image_html = (
            f'<div style="margin:8px 0;">'
            f'<img src="{data_uri}" alt="Seized supplies in {location}" '
            f'style="width:100%;max-height:180px;object-fit:cover;border-radius:6px;'
            f'border:1px solid #ddd;" />'
            f"</div>"
        )

    return f"""
    <div style="font-family:system-ui,-apple-system,sans-serif;width:270px;line-height:1.4;">
        <div style="background:#0b2545;color:#fff;padding:6px 10px;border-radius:6px 6px 0 0;
                    font-weight:700;font-size:13px;">
            {location} — {drug}
        </div>
        <div style="padding:8px 10px;border:1px solid #d9e2ec;border-top:none;
                    border-radius:0 0 6px 6px;background:#fff;">
            {image_html}
            <div style="font-size:12px;color:#102a43;margin-bottom:6px;">
                <strong>Est. Value:</strong> {value_str}<br/>
                <strong>Suspects Arrested:</strong> {suspects}<br/>
                <strong>Source:</strong> {source}
            </div>
            <p style="font-size:11px;color:#486581;margin:0;">{excerpt}</p>
        </div>
    </div>
    """


def build_bust_map(
    incidents: list[Incident],
    output_path: str | Path = "output/saps_bust_map.html",
) -> Path:
    """Generate an interactive Folium HTML map of geocoded incidents."""
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    fmap = folium.Map(
        location=KZN_CENTER,
        zoom_start=7,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri",
    )

    plotted_count = 0
    total_value = 0.0
    total_suspects = 0

    for idx, incident in enumerate(incidents):
        coords = get_coordinates(incident.location)
        if coords is None:
            continue

        # Slight deterministic offset if multiple busts occur in the exact same town
        lat = coords[0] + (idx * 0.004)
        lon = coords[1] + (idx * 0.004)

        value = incident.estimated_value_zar or 0.0
        total_value += value
        total_suspects += incident.suspect_count or 0
        plotted_count += 1

        marker_color = "red" if value >= 1_000_000 else "orange" if value > 0 else "blue"
        tooltip = f"{incident.location}: {incident.drug_type or 'Drugs'} (Click for details)"

        popup = folium.Popup(_build_popup_html(incident), max_width=300)
        folium.Marker(
            location=(lat, lon),
            tooltip=tooltip,
            popup=popup,
            icon=folium.Icon(color=marker_color, icon="info-sign"),
        ).add_to(fmap)

    banner_html = f"""
    <div style="position:fixed;top:12px;left:55px;z-index:9999;background:#0b2545;color:#fff;
                padding:10px 14px;border-radius:8px;font-family:system-ui,sans-serif;
                box-shadow:0 2px 8px rgba(0,0,0,0.25);font-size:12px;">
        <div style="font-weight:700;font-size:14px;margin-bottom:2px;">
            SAPS Drug Bust Tracker
        </div>
        <div>
            <strong>{plotted_count}</strong> Mapped Busts &bull;
            <strong>{total_suspects}</strong> Suspects &bull;
            <strong>R{total_value:,.0f}</strong> Est. Value
        </div>
    </div>
    """
    fmap.get_root().html.add_child(folium.Element(banner_html))
    fmap.save(str(out_file))
    return out_file
