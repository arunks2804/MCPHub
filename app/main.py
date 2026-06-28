import json
import os
import httpx

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from app import registry
from app.search import search_servers, get_all_servers, get_categories
from app.builder import generate_mcp_server
from app.tester import test_tool, test_all_tools

app = FastAPI(title="MCPHub", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./generated", exist_ok=True)
    registry.init_db()


# ─── Models ───────────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    name: str
    description: str
    api_base_url: str
    api_key_env_name: str
    tools_description: str
    category: str = "Custom"
    provider: str = "ollama"
    model: str = "mistral"
    api_key: str = ""


class RegisterRequest(BaseModel):
    name: str
    description: str
    api_base_url: str
    api_key_env_name: str
    tools: list
    category: str = "Custom"
    source: str = "registered"


class TestToolRequest(BaseModel):
    server_id: str
    tool_name: str
    parameters: dict = {}
    api_key: str


class TestAllRequest(BaseModel):
    server_id: str
    api_key: str
    sample_params: dict = {}


class AddToRegistryRequest(BaseModel):
    server_id: str


# ─── Registry endpoints ────────────────────────────────────────────────────────

@app.get("/servers")
def list_servers(category: Optional[str] = Query(default=None)):
    return registry.list_servers(category)


@app.get("/servers/{server_id}")
def get_server(server_id: str):
    server = registry.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@app.post("/servers/register")
def register_server(req: RegisterRequest):
    import uuid
    server_id = str(uuid.uuid4())
    return registry.save_server(
        server_id=server_id,
        name=req.name,
        description=req.description,
        api_base_url=req.api_base_url,
        api_key_env_name=req.api_key_env_name,
        tools=req.tools,
        category=req.category,
        source=req.source,
    )


@app.delete("/servers/{server_id}")
def delete_server(server_id: str):
    deleted = registry.delete_server(server_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Server not found")
    return {"deleted": True}


@app.get("/categories")
async def categories():
    return get_categories()


@app.get("/search")
async def search(q: str = "", category: str = "All"):
    if q:
        results = search_servers(q)
    else:
        results = get_all_servers(category)
    return {"results": results, "count": len(results)}


# ─── Builder endpoints ─────────────────────────────────────────────────────────

@app.post("/builder/generate")
async def builder_generate(req: GenerateRequest):
    result = await generate_mcp_server(
        name=req.name,
        description=req.description,
        api_base_url=req.api_base_url,
        api_key_env_name=req.api_key_env_name,
        tools_description=req.tools_description,
        category=req.category,
        provider=req.provider,
        model=req.model,
        api_key=req.api_key,
    )
    return result


@app.get("/builder/download/{server_id}")
def builder_download(server_id: str):
    zip_path = os.path.join("generated", f"{server_id}.zip")
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(zip_path, media_type="application/zip", filename=f"{server_id}.zip")


@app.post("/builder/add-to-registry")
def builder_add_to_registry(req: AddToRegistryRequest):
    zip_path = os.path.join("generated", f"{req.server_id}.zip")
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="Generated server not found")

    meta_path = os.path.join("generated", req.server_id, "_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
        return registry.save_server(
            server_id=req.server_id,
            name=meta["name"],
            description=meta["description"],
            api_base_url=meta["api_base_url"],
            api_key_env_name=meta["api_key_env_name"],
            tools=meta["tools"],
            category=meta["category"],
            source="built",
        )
    raise HTTPException(status_code=404, detail="Metadata not found — generate the server first")


@app.post("/builder/test-tool")
async def builder_test_tool(req: TestToolRequest):
    return await test_tool(req.server_id, req.tool_name, req.parameters, req.api_key)


@app.post("/builder/test-all")
async def builder_test_all(req: TestAllRequest):
    return await test_all_tools(req.server_id, req.api_key, req.sample_params)


# ─── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    ollama_ok = False
    ollama_models = []
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get("http://localhost:11434/api/tags")
            if resp.status_code == 200:
                ollama_ok = True
                ollama_models = [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        pass

    return {
        "status": "ok",
        "ollama": {"available": ollama_ok, "models": ollama_models},
    }
