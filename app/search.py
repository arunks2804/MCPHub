import sqlite3
import json

DB_PATH = "./data/registry.db"


def search_servers(query: str) -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    search_term = f"%{query}%"
    cursor.execute("""
        SELECT * FROM mcp_servers
        WHERE status = 'active'
        AND (
            name LIKE ?
            OR description LIKE ?
            OR tools LIKE ?
            OR category LIKE ?
        )
        ORDER BY name ASC
    """, (search_term, search_term, search_term, search_term))
    results = [_row_to_dict(dict(row)) for row in cursor.fetchall()]
    conn.close()
    return results


def get_all_servers(category: str = None) -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if category and category != "All":
        cursor.execute("SELECT * FROM mcp_servers WHERE status = 'active' AND category = ? ORDER BY name ASC", (category,))
    else:
        cursor.execute("SELECT * FROM mcp_servers WHERE status = 'active' ORDER BY name ASC")
    results = [_row_to_dict(dict(row)) for row in cursor.fetchall()]
    conn.close()
    return results


def get_categories() -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT category, COUNT(*) as count FROM mcp_servers WHERE status = 'active' GROUP BY category ORDER BY count DESC")
    results = [{"category": row[0], "count": row[1]} for row in cursor.fetchall()]
    conn.close()
    return results


def _row_to_dict(row: dict) -> dict:
    try:
        row["tools"] = json.loads(row["tools"])
    except Exception:
        row["tools"] = []
    return row
