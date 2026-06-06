"""
Environment configuration — EXAMPLE FILE.
Copy this to env_config.py and fill in your real values.
DO NOT commit env_config.py to source control.
"""

# ── API Base URLs ─────────────────────────────────────────────────────────────
GET_API_BASE_URL  = "http://localhost:5001"   # e.g. "https://api.yourapp.com"
POST_API_BASE_URL = "http://localhost:5002"   # e.g. "https://api.yourapp.com"

# ── Auth ──────────────────────────────────────────────────────────────────────
AUTH_TOKEN = "test-token-123"                 # e.g. "your-real-bearer-token"

# ── Endpoints ─────────────────────────────────────────────────────────────────
ENDPOINTS = {
    "get_all_users":  "/users",
    "get_user_by_id": "/users/{id}",
    "create_user":    "/users",
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
