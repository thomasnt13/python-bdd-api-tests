"""
Azure SQL Server connection configuration — EXAMPLE FILE.
Copy this file to db_config.py and fill in your real credentials.
DO NOT commit db_config.py to source control.
"""

DB_CONFIG = {
    "server":   "your-server.database.windows.net",
    "database": "your-database-name",
    "username": "your-azure-username",
    "password": "your-azure-password",
    "driver":   "ODBC Driver 18 for SQL Server",
}

# Table names
USERS_TABLE = "dbo.Users"
