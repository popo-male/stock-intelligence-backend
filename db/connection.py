import sqlite3

from core.settings import settings


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DB_PATH)
    # Return dict-like objects instead of tuples.
    conn.row_factory = sqlite3.Row
    return conn
