TOOL_DESIGN_PROMPT = """
You are an MCP server architect. Design MCP tools for the given API.

Return ONLY valid JSON, no markdown, no explanation:
{
  "tools": [
    {
      "name": "snake_case_tool_name",
      "description": "What this tool does in one sentence",
      "parameters": [
        {
          "name": "param_name",
          "type": "string",
          "description": "What this parameter is",
          "required": true
        }
      ],
      "api_endpoint": "/path/to/endpoint/{param}",
      "http_method": "GET",
      "response_description": "What this tool returns"
    }
  ]
}

Rules:
- Tool names must be snake_case
- Design 3-6 tools based on the description
- Make tools atomic — one action per tool
- Parameters should match real REST API patterns
- Include path parameters, query parameters as needed
"""

CODE_GENERATION_PROMPT = """
You are an expert Python MCP server developer.
Generate a complete, working MCP server using the official MCP Python SDK.

Return ONLY valid JSON where keys are file paths and values are complete file contents.
No markdown. No explanation. Just the JSON.

{
  "server.py": "complete server code",
  "config.py": "complete config code",
  "tools/tool_name.py": "complete tool code",
  ".env.example": "env template",
  "requirements.txt": "dependencies",
  "README.md": "setup instructions"
}

Rules:
- Use: from mcp.server import Server, from mcp.types import Tool, TextContent
- Read API key: import os; api_key = os.environ.get("API_KEY_ENV_NAME")
- Use httpx for all HTTP calls: import httpx
- Never hardcode credentials
- Include proper error handling with try/except
- config.py must use python-dotenv: from dotenv import load_dotenv
- .env.example must show all required env vars with placeholder values
- README.md must include: installation, env setup, how to run, how to connect to Claude Desktop and Cursor
- requirements.txt must include: mcp, httpx, python-dotenv
"""
