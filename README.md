# MCPHub

Build MCP servers from any API using AI.
Discover MCP servers built by others.
Self-hosted. Open source. MIT license.

## What it does

**Build** — Describe what tools you need from any API in plain English.
MCPHub generates a complete, working MCP server in seconds.
Download the code. Run it anywhere.

**Discover** — Search MCP servers by what you need, not just keywords.
Semantic search finds the right tool even if you don't know its name.

## Quick Start

### 1. Install Ollama
```bash
# Download from https://ollama.com
ollama pull mistral
ollama pull nomic-embed-text
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Start MCPHub
```bash
uvicorn app.main:app --reload --port 8002
```

### 4. Open the UI
```bash
open frontend/index.html
```

## Self Hosted

MCPHub runs entirely on your own infrastructure.
API keys never leave your environment.
Deploy on any VM, laptop, or on-premise server.

## Deployment Models

- Self hosted — free, open source, MIT license
- Cloud hosted — coming soon

## Connect generated MCP to Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "your-mcp-name": {
      "command": "python",
      "args": ["/path/to/generated/server.py"]
    }
  }
}
```

## Connect to Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "your-mcp-name": {
      "command": "python",
      "args": ["/path/to/generated/server.py"]
    }
  }
}
```

## Stack

- Backend: FastAPI + Python
- Frontend: Single HTML file, dark theme, vanilla JS
- Search: ChromaDB + Ollama nomic-embed-text embeddings
- LLM: Pluggable — Ollama, Claude, OpenAI, Gemini, Mistral, Groq
- Database: SQLite
