"""
Handles authentication against the Logistiq auth service.
Auth model: session-cookie based (Django-style). Login returns Set-Cookie headers
containing `sessionid` and `csrftoken`. We cache these in memory and attach them
to every tracking API call.

POC decisions (no fixed values were available from the API team):
- Session TTL: no documented value. Using a conservative 25-minute soft TTL —
  force re-login after that window — PLUS reactive re-login on any 401/403 from
  the tracking API.
- CSRF: not sent. The tracking call is a GET request; Django's default CSRF
  middleware does not enforce CSRF tokens on GET, only on state-changing requests.
  Revisit only if the API starts returning 403 with a CSRF-specific error body.

Single in-memory session for the whole process — fine for a single-tenant POC.
NOT safe for multi-user/multi-tenant production use.
"""
import os
import time
from typing import Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

AUTH_URL = os.getenv(
    "LOGISTIQ_AUTH_URL",
    "https://logistiqauth-dev.logistiq.me/auth/api/v1/accounts/login",
)
EMAIL = os.getenv("LOGISTIQ_EMAIL")
PASSWORD = os.getenv("LOGISTIQ_PASSWORD")
SESSION_SOFT_TTL_SECONDS = 25 * 60

class SessionManager:
    def __init__(self):
        self._cookies: Optional[httpx.Cookies] = None
        self._logged_in_at: float = 0.0

    def _login(self) -> httpx.Cookies:
        if not EMAIL or not PASSWORD:
            raise RuntimeError(
                "LOGISTIQ_EMAIL / LOGISTIQ_PASSWORD are not set. "
                "Set them as environment variables — see .env.example."
            )
        resp = httpx.post(
            AUTH_URL,
            json={"email": EMAIL, "password": PASSWORD},
            headers={"Content-Type": "application/json"},
            timeout=10.0,
        )
        resp.raise_for_status()
        self._cookies = resp.cookies
        self._logged_in_at = time.monotonic()
        return self._cookies

    def get_cookies(self) -> httpx.Cookies:
        expired = (
            self._cookies is None
            or (time.monotonic() - self._logged_in_at) > SESSION_SOFT_TTL_SECONDS
        )
        if expired:
            self._login()
        return self._cookies

    def invalidate(self) -> None:
        """Call after a 401/403 from a downstream API to force re-login."""
        self._cookies = None

session_manager = SessionManager()
