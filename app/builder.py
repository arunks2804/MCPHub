import json
import os
import uuid
import zipfile

from app.llm_provider import call_llm
from app.prompts import TOOL_DESIGN_PROMPT, CODE_GENERATION_PROMPT


async def generate_mcp_server(
    name: str,
    description: str,
    api_base_url: str,
    api_key_env_name: str,
    tools_description: str,
    category: str,
    provider: str,
    model: str,
    api_key: str,
) -> dict:
    server_id = str(uuid.uuid4())

    # Step 1 — Design tools
    tool_design_user = f"API Base URL: {api_base_url}\n\nDescription: {tools_description}"
    tool_design_raw = await call_llm(provider, model, api_key, TOOL_DESIGN_PROMPT, tool_design_user)

    try:
        tool_design = json.loads(tool_design_raw)
        tools = tool_design.get("tools", [])
    except json.JSONDecodeError:
        tools = []

    # Step 2 — Generate code
    code_gen_user = (
        f"Server Name: {name}\n"
        f"Description: {description}\n"
        f"API Base URL: {api_base_url}\n"
        f"API Key Environment Variable: {api_key_env_name}\n\n"
        f"Tools to implement:\n{json.dumps(tools, indent=2)}"
    )
    code_raw = await call_llm(provider, model, api_key, CODE_GENERATION_PROMPT, code_gen_user)

    try:
        files = json.loads(code_raw)
    except json.JSONDecodeError:
        files = {
            "server.py": f"# Generated MCP server for {name}\n# Could not parse LLM response\n",
            "requirements.txt": "mcp\nhttpx\npython-dotenv\n",
            ".env.example": f"{api_key_env_name}=your_key_here\n",
            "README.md": f"# {name}\n\nGenerated MCP server.\n",
        }

    # Step 3 — Write files and create zip
    server_dir = os.path.join("generated", server_id)
    os.makedirs(server_dir, exist_ok=True)

    for filename, content in files.items():
        filepath = os.path.join(server_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(content)

    zip_path = os.path.join("generated", f"{server_id}.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        for filename in files.keys():
            full_path = os.path.join(server_dir, filename)
            if os.path.exists(full_path):
                zf.write(full_path, filename)

    return {
        "server_id": server_id,
        "name": name,
        "description": description,
        "api_base_url": api_base_url,
        "api_key_env_name": api_key_env_name,
        "category": category,
        "tools": tools,
        "files": files,
        "zip_path": zip_path,
    }
