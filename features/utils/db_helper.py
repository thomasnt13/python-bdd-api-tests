"""DB helper — Azure AD Password authentication with SQL Server via pyodbc."""
import pyodbc


def get_connection(db_config: dict):
    """Return a pyodbc connection using Azure AD password auth."""
    conn_str = (
        f"Driver={{{db_config['driver']}}};"
        f"Server={db_config['server']};"
        f"Database={db_config['database']};"
        f"UID={db_config['username']};"
        f"PWD={db_config['password']};"
        "Authentication=ActiveDirectoryPassword;"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )
    return pyodbc.connect(conn_str, timeout=10)


def fetch_envelope(db_config: dict, table: str, client_id, envelope_number) -> dict | None:
    """
    Fetch one envelope row from the DB.
    Returns a dict of column→value, or None if not found.
    Adjust column names (client_id, envelope_number) to match your actual schema.
    """
    query = f"""
        SELECT *
        FROM {table}
        WHERE client_id = ? AND envelope_number = ?
    """
    with get_connection(db_config) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (int(client_id), int(envelope_number)))
        row = cursor.fetchone()
        if row is None:
            return None
        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))
