# Logistiq Shipment Tracker MCP Server

This is a proof-of-concept (POC) MCP (Model Context Protocol) server for Logistiq order tracking, designed specifically for integration with Voiceflow text-to-speech.

## Known Limitations

This is explicitly a POC, not a production-ready service, and has the following deliberate limitations:

- **Single global in-process session**: The auth state is kept in-memory and shared across all requests. This is NOT multi-tenant safe.
- **No caching, no retry/backoff**: There is no caching of tracking data to avoid staleness, and only one reactive re-login retry is implemented on 401/403 errors.
- **No structured logging**: There is no structured logging pipeline or PII redaction.
- **No disambiguation logic**: Assumes the AWB provided is clean and exact; there is no logic for scenarios where a user has multiple shipments.
- **Dev/test credentials only**: Credentials are read from environment variables, not a secure secrets manager.
- **No database or persistence**: Tracking data is fetched live on every call.
- **No background jobs**: There are no token refresh schedulers or cron tasks.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your credentials manually.

## Running

Start the server:
```bash
python server.py
```
By default, it listens on port 8000. Expose it via ngrok for Voiceflow testing:
```bash
ngrok http 8000
```

## Supported Python versions
This project requires Python >=3.10,<3.14 (constrained by the `mcp` SDK's
current PyPI wheel availability, not by anything in this codebase).
Python 3.14 will fail at `pip install` — use pyenv/venv to select 3.11 or 3.12.
