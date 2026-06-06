"""
Copy this file to env_config.py and fill in your real values.
DO NOT commit env_config.py to source control.

    cp config/env_config.example.py config/env_config.py
"""

# ── API Base URLs ─────────────────────────────────────────────────────────────
GET_API_BASE_URL      = "http://localhost:5001"
POST_API_BASE_URL     = "http://localhost:5002"
ENVELOPE_API_BASE_URL = "http://localhost:5003"        # or your real envelope API URL

# ── OAuth Token ───────────────────────────────────────────────────────────────
TOKEN_URL     = "http://localhost:5004/oauth/token"    # or your real token endpoint
CLIENT_ID     = "your-client-id"
CLIENT_SECRET = "your-client-secret"
AUDIENCE      = "https://api.example.com"              # optional — remove if not needed

# ── Auth ──────────────────────────────────────────────────────────────────────
AUTH_TOKEN = "test-token-123"                          # used by users API (non-OAuth)

# ── Endpoints ─────────────────────────────────────────────────────────────────
ENDPOINTS = {
    "get_all_users":  "/users",
    "get_user_by_id": "/users/{id}",
    "create_user":    "/users",
    "get_envelope":   "/clients/{clientId}/envelopes/{envelopeNumber}",
}

# ── Extra Headers (beyond Authorization) ─────────────────────────────────────
EXTRA_HEADERS = {
    # "x-api-key":   "your-api-key",
    # "x-tenant-id": "your-tenant",
    # "Accept":      "application/json",
}

# ── DB Config ─────────────────────────────────────────────────────────────────
DB_CONFIG = {
    "server":   "your-server.database.windows.net",
    "database": "your-database-name",
    "username": "your-azure-username",
    "password": "your-azure-password",
    "driver":   "ODBC Driver 18 for SQL Server",
}
USERS_TABLE = "dbo.Users"
