import os
import httpx
from dotenv import load_dotenv

load_dotenv()

from mcp.server.fastmcp import FastMCP
from tracking import fetch_tracking
from formatter import format_status_for_voice

port = int(os.getenv("PORT", "8000"))

mcp = FastMCP("logistiq-shipment-tracker", host="0.0.0.0", port=port)


@mcp.tool()
def get_shipment_status(cpawb: str) -> str:
    """
    Get the current status of a shipment given its tracking number
    (CPAWB / waybill, e.g. "MACMSASAF000005030").

    Returns a short, spoken-friendly summary covering shipment status,
    last known location, and expected delivery date — suitable for
    direct text-to-speech playback.
    """
    cpawb = cpawb.strip()

    try:
        raw = fetch_tracking(cpawb)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return (
                f"I couldn't find any shipment with tracking number {cpawb}. "
                "Please double check the number and try again."
            )
        return (
            "Sorry, I'm having trouble reaching the tracking system right now. "
            "Please try again in a moment."
        )
    except httpx.TimeoutException:
        return "The tracking system is taking too long to respond. Please try again shortly."
    except Exception:
        return "Sorry, something went wrong while checking your shipment status."

    return format_status_for_voice(raw)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
