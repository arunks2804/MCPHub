import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional


DB_PATH = "./data/registry.db"

SEED_SERVERS = [
    {
        "name": "GitHub MCP",
        "description": "Manage GitHub repos, issues, PRs, commits and code search",
        "api_base_url": "https://api.github.com",
        "api_key_env_name": "GITHUB_TOKEN",
        "tools": [
            {"name": "create_issue", "description": "Create a new GitHub issue"},
            {"name": "search_code", "description": "Search code across repositories"},
            {"name": "get_repo", "description": "Get repository details"},
            {"name": "create_pr", "description": "Create a pull request"},
            {"name": "list_commits", "description": "List commits for a repository"},
        ],
        "category": "Code",
        "source": "registered",
    },
    {
        "name": "Slack MCP",
        "description": "Send messages, read channels, manage Slack workspace",
        "api_base_url": "https://slack.com/api",
        "api_key_env_name": "SLACK_BOT_TOKEN",
        "tools": [
            {"name": "send_message", "description": "Send a message to a channel"},
            {"name": "list_channels", "description": "List all channels"},
            {"name": "get_messages", "description": "Get messages from a channel"},
            {"name": "create_channel", "description": "Create a new channel"},
        ],
        "category": "Communication",
        "source": "registered",
    },
    {
        "name": "PostgreSQL MCP",
        "description": "Query PostgreSQL databases, list tables, describe schema",
        "api_base_url": "postgresql://",
        "api_key_env_name": "DATABASE_URL",
        "tools": [
            {"name": "query", "description": "Execute a SQL query"},
            {"name": "list_tables", "description": "List all tables in database"},
            {"name": "describe_table", "description": "Get column details for a table"},
            {"name": "execute", "description": "Execute a SQL statement"},
        ],
        "category": "Data",
        "source": "registered",
    },
    {
        "name": "Jira MCP",
        "description": "Create and manage Jira issues, sprints, and projects",
        "api_base_url": "https://your-domain.atlassian.net",
        "api_key_env_name": "JIRA_API_TOKEN",
        "tools": [
            {"name": "create_issue", "description": "Create a new Jira issue"},
            {"name": "update_issue", "description": "Update an existing issue"},
            {"name": "list_sprints", "description": "List all sprints for a project"},
            {"name": "get_project", "description": "Get project details"},
        ],
        "category": "Productivity",
        "source": "registered",
    },
    {
        "name": "Notion MCP",
        "description": "Read and write Notion pages and databases",
        "api_base_url": "https://api.notion.com",
        "api_key_env_name": "NOTION_API_KEY",
        "tools": [
            {"name": "get_page", "description": "Get a Notion page by ID"},
            {"name": "create_page", "description": "Create a new page"},
            {"name": "update_page", "description": "Update page content"},
            {"name": "query_database", "description": "Query a Notion database"},
        ],
        "category": "Productivity",
        "source": "registered",
    },
    {
        "name": "Salesforce MCP",
        "description": "Query and update Salesforce CRM records, leads, opportunities",
        "api_base_url": "https://login.salesforce.com",
        "api_key_env_name": "SALESFORCE_ACCESS_TOKEN",
        "tools": [
            {"name": "query_records", "description": "Query Salesforce records using SOQL"},
            {"name": "create_record", "description": "Create a new record"},
            {"name": "update_record", "description": "Update an existing record"},
            {"name": "get_opportunity", "description": "Get opportunity details"},
        ],
        "category": "CRM",
        "source": "registered",
    },
    {
        "name": "Workday MCP",
        "description": "Access HR data, employee records, leave balances, org chart",
        "api_base_url": "https://wd2-impl-services1.workday.com",
        "api_key_env_name": "WORKDAY_ACCESS_TOKEN",
        "tools": [
            {"name": "get_employee", "description": "Get employee details by ID"},
            {"name": "check_leave_balance", "description": "Check leave balance for employee"},
            {"name": "get_org_chart", "description": "Get org chart for a department"},
            {"name": "list_positions", "description": "List open positions"},
        ],
        "category": "HR",
        "source": "registered",
    },
    {
        "name": "Snowflake MCP",
        "description": "Query Snowflake data warehouse, list databases and schemas",
        "api_base_url": "https://account.snowflakecomputing.com",
        "api_key_env_name": "SNOWFLAKE_PASSWORD",
        "tools": [
            {"name": "execute_query", "description": "Execute a SQL query"},
            {"name": "list_databases", "description": "List all databases"},
            {"name": "list_schemas", "description": "List schemas in a database"},
            {"name": "describe_table", "description": "Describe a table structure"},
        ],
        "category": "Data",
        "source": "registered",
    },
]


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mcp_servers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            api_base_url TEXT,
            api_key_env_name TEXT,
            auth_type TEXT DEFAULT 'api_key',
            tools TEXT NOT NULL,
            category TEXT,
            created_at TEXT,
            source TEXT DEFAULT 'built',
            status TEXT DEFAULT 'active'
        )
    """)
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM mcp_servers").fetchone()[0]
    if count == 0:
        _seed(conn)
    conn.close()


def _seed(conn):
    for server in SEED_SERVERS:
        server_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO mcp_servers (id, name, description, api_base_url, api_key_env_name, tools, category, created_at, source) VALUES (?,?,?,?,?,?,?,?,?)",
            (
                server_id,
                server["name"],
                server["description"],
                server["api_base_url"],
                server["api_key_env_name"],
                json.dumps(server["tools"]),
                server["category"],
                datetime.now(timezone.utc).isoformat(),
                server["source"],
            ),
        )
    conn.commit()


def list_servers(category: Optional[str] = None) -> list:
    conn = get_conn()
    if category:
        rows = conn.execute("SELECT * FROM mcp_servers WHERE category=? AND status='active' ORDER BY created_at DESC", (category,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM mcp_servers WHERE status='active' ORDER BY created_at DESC").fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_server(server_id: str) -> Optional[dict]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM mcp_servers WHERE id=?", (server_id,)).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def save_server(server_id: str, name: str, description: str, api_base_url: str, api_key_env_name: str, tools: list, category: str, source: str = "built") -> dict:
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO mcp_servers (id, name, description, api_base_url, api_key_env_name, tools, category, created_at, source) VALUES (?,?,?,?,?,?,?,?,?)",
        (server_id, name, description, api_base_url, api_key_env_name, json.dumps(tools), category, datetime.now(timezone.utc).isoformat(), source),
    )
    conn.commit()
    conn.close()
    return get_server(server_id)


def delete_server(server_id: str) -> bool:
    conn = get_conn()
    result = conn.execute("DELETE FROM mcp_servers WHERE id=?", (server_id,))
    conn.commit()
    conn.close()
    return result.rowcount > 0


def get_categories() -> list:
    conn = get_conn()
    rows = conn.execute("SELECT category, COUNT(*) as count FROM mcp_servers WHERE status='active' GROUP BY category ORDER BY count DESC").fetchall()
    conn.close()
    return [{"category": r["category"], "count": r["count"]} for r in rows]


def keyword_search(query: str) -> list:
    conn = get_conn()
    like = f"%{query}%"
    rows = conn.execute(
        "SELECT * FROM mcp_servers WHERE status='active' AND (name LIKE ? OR description LIKE ? OR tools LIKE ?) ORDER BY created_at DESC",
        (like, like, like),
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_servers_by_ids(ids: list) -> list:
    if not ids:
        return []
    conn = get_conn()
    placeholders = ",".join("?" * len(ids))
    rows = conn.execute(f"SELECT * FROM mcp_servers WHERE id IN ({placeholders}) AND status='active'", ids).fetchall()
    conn.close()
    id_order = {sid: i for i, sid in enumerate(ids)}
    result = [_row_to_dict(r) for r in rows]
    result.sort(key=lambda s: id_order.get(s["id"], 999))
    return result


def _row_to_dict(row) -> dict:
    d = dict(row)
    try:
        d["tools"] = json.loads(d["tools"])
    except Exception:
        d["tools"] = []
    return d
