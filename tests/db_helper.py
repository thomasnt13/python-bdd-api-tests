"""
Database helper — connects to Azure SQL Server via pyodbc
and provides query utilities for DB validation in tests.
"""
import sys
import os
import pyodbc
import allure

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.db_config import DB_CONFIG, USERS_TABLE


DB_NOT_CONFIGURED = (
    "your-server" in DB_CONFIG["server"] or
    "your-azure" in DB_CONFIG["username"]
)


def get_connection():
    """Return a pyodbc connection to Azure SQL Server."""
    if DB_NOT_CONFIGURED:
        raise RuntimeError(
            "DB not configured. Update config/db_config.py with real credentials."
        )
    conn_str = (
        f"DRIVER={{{DB_CONFIG['driver']}}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)


def fetch_user_by_name(name: str) -> dict | None:
    """
    Fetch a user row from the DB by name.
    Returns a dict with keys: id, name, email — or None if not found.
    """
    query = f"SELECT id, name, email FROM {USERS_TABLE} WHERE name = ?"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, name)
        row = cursor.fetchone()
        if row:
            return {"id": row[0], "name": row[1], "email": row[2]}
        return None


def fetch_all_users() -> list[dict]:
    """Fetch all users from the DB."""
    query = f"SELECT id, name, email FROM {USERS_TABLE}"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return [
            {"id": row[0], "name": row[1], "email": row[2]}
            for row in cursor.fetchall()
        ]


def fetch_user_by_id(user_id: int) -> dict | None:
    """Fetch a user row from the DB by ID."""
    query = f"SELECT id, name, email FROM {USERS_TABLE} WHERE id = ?"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, user_id)
        row = cursor.fetchone()
        if row:
            return {"id": row[0], "name": row[1], "email": row[2]}
        return None


def validate_api_vs_db(api_record: dict, db_record: dict):
    """
    Assert that API response fields match DB record.
    Attaches a comparison table to the allure report.
    """
    mismatches = []
    comparison = "Field          | API Value         | DB Value\n"
    comparison += "-" * 55 + "\n"

    for key in ("id", "name", "email"):
        api_val = str(api_record.get(key, ""))
        db_val  = str(db_record.get(key, ""))
        match   = "✅" if api_val == db_val else "❌"
        comparison += f"{key:<15}| {api_val:<18}| {db_val} {match}\n"
        if api_val != db_val:
            mismatches.append(f"'{key}': API='{api_val}' vs DB='{db_val}'")

    allure.attach(comparison, name="API vs DB Comparison", attachment_type=allure.attachment_type.TEXT)

    if mismatches:
        raise AssertionError("API response does not match DB:\n" + "\n".join(mismatches))
