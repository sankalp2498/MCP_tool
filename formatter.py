"""
Shapes the raw tracking JSON into a short, spoken-friendly summary.
TTS reading raw JSON field-by-field is an instant credibility killer in a voice
demo. This produces 2-4 short sentences prioritized the way a human would answer
"where's my package" — status first, location/ETA second, never a data dump.
"""
from datetime import datetime
from typing import Optional

def _humanize_timestamp(iso_ts: Optional[str]) -> Optional[str]:
    if not iso_ts:
        return None
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        return dt.strftime("%B %d at %I:%M %p UTC")
    except (ValueError, TypeError):
        return iso_ts

def format_status_for_voice(payload: dict) -> str:
    if not payload.get("status"):
        return "I couldn't find any details for that tracking number."
    data = payload.get("data") or {}
    if not data:
        return "I couldn't find any details for that tracking number."
    
    waybill = data.get("waybill", "your shipment")
    current = data.get("current_status") or {}
    status_label = (current.get("status") or "unknown").replace("_", " ").title()
    scan_location = current.get("scan_location")
    scan_time = _humanize_timestamp(current.get("scan_time"))
    eta = _humanize_timestamp(data.get("expected_delivery_date"))
    source = data.get("source_location")
    destination = data.get("destination_location")
    
    parts = [f"Shipment {waybill} is currently {status_label}."]
    if scan_location:
        parts.append(f"It was last scanned at {scan_location}.")
    elif source and destination:
        parts.append(f"It's moving from {source} to {destination}.")
    if scan_time:
        parts.append(f"Last update was on {scan_time}.")
    if eta:
        parts.append(f"Expected delivery is {eta}.")
    else:
        parts.append("An expected delivery date isn't available yet.")
    return " ".join(parts)
