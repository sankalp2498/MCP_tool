"""
Client for the Logistiq order tracking API.
On 401/403 we assume the session expired or was revoked, force a re-login,
and retry exactly once. A second failure surfaces as a real error — we do
not retry indefinitely.
"""
import os
import httpx
from auth import session_manager

TRACKING_URL = os.getenv(
    "LOGISTIQ_TRACKING_URL",
    "https://logistiqhawk-dev.logistiq.me/allocation/api/v1/tracking/order-details",
)

def fetch_tracking(cpawb: str) -> dict:
    """
    Fetch raw tracking data for a given AWB / CPAWB.
    Raises httpx.HTTPStatusError for non-2xx responses (after the single
    re-login retry), so callers can distinguish "not found" (404) from
    "system unavailable" (5xx / timeout).
    """
    cookies = session_manager.get_cookies()
    params = {"alpha_awb": cpawb}
    resp = httpx.get(
        TRACKING_URL,
        params=params,
        cookies=cookies,
        headers={"accept": "*/*"},
        timeout=10.0,
    )
    if resp.status_code in (401, 403):
        session_manager.invalidate()
        cookies = session_manager.get_cookies()
        resp = httpx.get(
            TRACKING_URL,
            params=params,
            cookies=cookies,
            headers={"accept": "*/*"},
            timeout=10.0,
        )
    resp.raise_for_status()
    return resp.json()
