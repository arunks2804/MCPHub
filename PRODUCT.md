# MCPHub — Product Specification

> **One-line pitch:** A developer describes what they need from any API in plain English. MCPHub generates a complete, working MCP server in seconds — and lets them discover servers others have already built.

---

## The Problem

AI agents are only as useful as the tools they can reach.

Every team building with Claude, Cursor, or any MCP-compatible agent hits the same wall: the API they need — their internal Confluence, their Workday HR system, their Snowflake warehouse — doesn't have an MCP server. So they either build one from scratch (a multi-hour exercise involving reading MCP SDK docs, structuring tool definitions, wiring HTTP calls, and packaging for distribution) or they go without, leaving the agent unable to act on the data that matters most.

The people who *know* what tools the agent needs (product managers, data analysts, ops teams) cannot build MCP servers. The people who *can* build them (backend engineers) are busy, and a new MCP server feels too small to prioritise but too unfamiliar to delegate.

The result is a systematic gap between what AI agents could do and what they actually do:

- Teams manually wire agents to APIs instead of using MCP standards.
- The same MCP server for Jira, Notion, or Salesforce gets rebuilt from scratch at every company.
- Generated servers have no standard structure — different tools, different conventions, no reuse.
- There is no central place to find "does an MCP server already exist for X?"
- Security is inconsistent — some servers hardcode credentials, others skip auth entirely.

**The cost:** days of engineering time per API integration, duplicated effort across the industry, and AI agents that can't reach the systems they're supposed to operate.

---

## Who This Is For

### Persona 1 — The AI Engineer / Agent Builder
*"I spend more time building tool integrations than building the agent itself."*

**Profile:** Building AI agents, copilots, or automation workflows with Claude, GPT-4, or open-source models. Knows MCP exists but finds the server setup tedious — especially for internal APIs with no community support. Ships one agent per sprint but spends half the sprint on plumbing.

**Challenges:**
- Writing MCP server boilerplate for every new API is repetitive and time-consuming.
- Internal APIs have no documentation in LLM training data — the model can't help.
- Managing credentials, environment variables, and transport layer correctly every time.
- No way to know if someone has already built the server they need.

---

### Persona 2 — The Platform / DevOps Engineer
*"Three different teams have asked me to build an MCP server for Workday. I've done it twice."*

**Profile:** Owns internal developer tooling. Gets requests from AI teams to expose internal systems as MCP servers. Knows the APIs well but has no time for the MCP SDK learning curve. Would rather publish once to a shared registry than answer the same request repeatedly.

**Challenges:**
- No internal registry to share MCP servers across teams.
- Every server is a one-off — no standard structure for testing, deployment, or documentation.
- Can't easily verify a generated server actually calls the right endpoints.
- No way to let other teams discover what's already been built.

---

### Persona 3 — The Non-Engineer Builder
*"I know exactly what I need the agent to do. I just can't write Python."*

**Profile:** Product manager, data analyst, or operations lead experimenting with AI agents. Has API access to the tools they use daily. Has read the MCP docs. Has no idea what a `Tool` definition or a `TextContent` response looks like in Python.

**Challenges:**
- The only path to an MCP server today is either writing code or filing a ticket.
- Cannot verify that a generated server is correct without running it.
- No way to test individual tools without writing test scripts.
- Documentation for MCP is engineering-first — not accessible to non-coders.

---

### Persona 4 — The Open Source Contributor
*"I built an MCP server for Confluence. I want others to find it."*

**Profile:** Developer who has already built an MCP server for a popular API and wants to share it. Currently has to publish to GitHub and hope people find it. No standard discovery mechanism exists — no npm-style registry for MCP servers.

**Challenges:**
- No dedicated registry for MCP servers — GitHub search is the only option.
- No standard format for listing what tools a server exposes.
- No way to signal quality, maintenance status, or category.
- Contributors who share their servers get no visibility into adoption.

---

## The Proposition

### General
MCPHub is the **build-and-discover platform for MCP servers**. It uses a pluggable LLM to convert plain-English API descriptions into complete, production-ready MCP servers — with proper tool definitions, HTTP wiring, credential handling, and documentation — and it hosts a searchable registry of servers built by the community. Self-hosted, open source, MIT license.

---

### For the AI Engineer / Agent Builder
Describe the tools you need from any API in plain English. MCPHub designs the tool definitions, generates the server code, packages it as a zip, and lets you test each tool against the live API before you deploy. Connect the downloaded server to Claude Desktop or Cursor in two config lines.

### For the Platform / DevOps Engineer
Generate once, publish to the registry, let every team find it. MCPHub gives internal MCP servers the same discoverability as public ones. Register an existing server with its tool list and API details — it becomes searchable across the organisation.

### For the Non-Engineer Builder
No code required to go from idea to working MCP server. Describe the tools in plain English, watch MCPHub build the server step by step, test each tool individually with your real API key, and download a zip that any engineer can run. The API key is used once for testing and never stored.

### For the Open Source Contributor
Register your server in the MCPHub registry with its name, description, API base URL, and tool list. It becomes searchable alongside everything else. Others find your work; you stop answering the same "does an MCP server exist for X?" question.

---

## Features

### 1. Natural Language → MCP Server (Core)
Describe the tools you need from any API in plain English. MCPHub runs in four steps:

1. **Tool Design** — LLM designs 3–6 atomic tool definitions: name, description, parameters, API endpoint, HTTP method.
2. **Code Generation** — LLM generates a complete, runnable MCP server using the official MCP Python SDK.
3. **File Assembly** — Files are written to disk: `server.py`, `config.py`, one file per tool in `tools/`, `.env.example`, `requirements.txt`, `README.md`.
4. **Packaging** — All files zipped and available for download.

Generated servers:
- Use the official MCP Python SDK (`from mcp.server import Server`)
- Read all credentials from environment variables — never hardcoded
- Use `httpx` for HTTP calls
- Include a `README.md` with installation, env setup, and Claude Desktop / Cursor connection instructions

---

### 2. Per-Tool Testing
Test each generated tool against the live API before you deploy. For each tool:
- Fill in the required parameters
- Provide your API key (used once, never stored, never logged)
- Click Run Test
- See the HTTP status code, response body, and latency in milliseconds

A **Test All** button runs every tool sequentially and returns a pass/fail summary. Failed tools show the error response — and a **Fix with AI** button sends the error back to the LLM to regenerate that tool only.

---

### 3. MCP Server Registry
A searchable directory of MCP servers — both built on MCPHub and registered from external sources.

**Search** — SQLite full-text search across server name, description, tool names, tool descriptions, and category. Finds "update a confluence comment" even if the server is called "Confluence MCP."

**Filter** — Category pills: Code, Communication, Data, Productivity, HR, Finance, CRM, Custom.

**Server cards** show:
- Name and description
- Category and source (Built on Hub / Registered)
- All tool names at a glance
- API base URL
- Actions: View Code, Test, Download

**View Code** — opens the generated source files in a syntax-highlighted viewer with per-file tabs and a copy button.

**Test** — opens the test panel for any server in the registry, not just freshly generated ones.

**Download** — downloads the zip directly. For externally registered servers, links to their repository.

---

### 4. Register Existing MCP Servers
Don't want to generate? Already have a server? Register it manually:
- Name, description, API base URL, API key env var, category
- Add tools one by one (name + description)
- Registered servers appear in the registry alongside generated ones
- Searchable immediately

---

### 5. Multi-LLM, Zero Lock-in
Works with any of six LLM providers — selected in the UI, never in a config file:

| Provider | Best For | Cost |
|---|---|---|
| **Ollama** (local) | Development, air-gapped environments, privacy | Free |
| **Claude Sonnet** | Highest quality tool design and code generation | Paid |
| **OpenAI GPT-4o** | General use, broad accuracy | Paid |
| **Gemini** | Long context, large API specs | Free tier / Paid |
| **Mistral** | Fast, EU-hosted option | Paid |
| **Groq** | Lowest latency responses | Paid |

API keys stored only in browser `localStorage` — never sent to any MCPHub server. For Ollama, the model name is a free-text field — type whatever model you have running locally.

---

### 6. Pre-Seeded Registry
MCPHub ships with 8 production-ready registered servers on first run, covering the most common enterprise integrations:

| Server | Category | Tools |
|---|---|---|
| GitHub MCP | Code | create_issue, search_code, get_repo, create_pr, list_commits |
| Slack MCP | Communication | send_message, list_channels, get_messages, create_channel |
| PostgreSQL MCP | Data | query, list_tables, describe_table, execute |
| Jira MCP | Productivity | create_issue, update_issue, list_sprints, get_project |
| Notion MCP | Productivity | get_page, create_page, update_page, query_database |
| Salesforce MCP | CRM | query_records, create_record, update_record, get_opportunity |
| Workday MCP | HR | get_employee, check_leave_balance, get_org_chart, list_positions |
| Snowflake MCP | Data | execute_query, list_databases, list_schemas, describe_table |

---

## User Workflows

> **For engineers setting up the app:** see [README.md](README.md) for installation and startup instructions.

These workflows describe what each persona does *inside the app* once it's running.

---

### Workflow 1 — Building an MCP server from scratch
*Primary persona: AI Engineer / Non-Engineer Builder*

1. Open MCPHub in the browser (`frontend/index.html` with the backend running on port 8002).
2. In the **LLM Provider** panel, select your provider. For Ollama, type the model name you have running locally. For cloud providers, enter model name and API key — stored only in your browser.
3. Stay on the **Build** tab.
4. Fill in: MCP Server Name, API Base URL, API Key Environment Variable Name, Category.
5. In the tools description box, describe what you need in plain English. Be specific about what each tool should do. Example: *"I need tools to get a Confluence page by ID, update a comment on a page, and search pages by keyword across a space."*
6. Click **Generate MCP Server**.
7. Four steps animate as they complete: Designing tools → Generating server code → Creating files → Building zip.
8. Three panels appear:
   - **Summary** — server name, category, tool count, Download ZIP button, Add to Registry button.
   - **View Code** — tabbed file viewer showing every generated file with syntax highlighting and copy button.
   - **Test Tools** — one card per tool with parameter inputs, per-tool API key field, and Run Test button.
9. Test each tool. Green = working. Red = see error + Fix with AI.
10. Download the zip. Follow the README inside to connect to Claude Desktop or Cursor.

---

### Workflow 2 — Finding an existing MCP server
*Primary persona: AI Engineer / Agent Builder*

1. Switch to the **Registry** tab.
2. Type what you need in the search bar — describe the action, not the tool name. *"send a slack message"*, *"query snowflake"*, *"get employee leave balance"*.
3. Filter by category pill if browsing rather than searching.
4. Find the server card. Check the tool names — confirm it does what you need.
5. Click **View Code** to inspect the implementation before trusting it.
6. Click **Test** to verify the tools work with your API key before connecting to your agent.
7. Click **Download** to get the zip, or note the API base URL and env var name for manual setup.

---

### Workflow 3 — Sharing an MCP server with your team
*Primary persona: Platform Engineer / Open Source Contributor*

1. Switch to the **Registry** tab.
2. Click **Register Existing MCP** in the top right.
3. Fill in: name, description, API base URL, API key env var, category.
4. Add tools one by one — tool name and a one-line description per tool.
5. Click **Register MCP**.
6. The server appears in the registry immediately, searchable by name, description, and all tool names.
7. Share the MCPHub URL with your team — they find it in the registry without needing to ask you.

---

### Workflow 4 — Testing a server from the registry before deploying
*Primary persona: AI Engineer*

1. Find the server in the Registry tab.
2. Click **Test** on the server card.
3. A test panel opens with one card per tool.
4. Fill in sample parameters for the tool you want to verify.
5. Enter your API key (used once for this test, never stored).
6. Click **Run Test** — see status code, response body, and latency.
7. If a tool fails, note the error. If the server was built on MCPHub, use **Fix with AI** to regenerate that tool.
8. Once satisfied, download and deploy.

---

## What's Not in v1

| Feature | Status |
|---|---|
| Semantic / vector search in the registry | Roadmap |
| One-click deploy to Railway / Fly.io / AWS Lambda | Roadmap |
| Auto-detection of available Ollama models via /health | Roadmap |
| MCP server versioning and changelogs | Roadmap |
| Team workspaces and private registries | Roadmap |
| Schema-aware tool generation (paste OpenAPI spec) | Roadmap |
| OAuth 2.0 and bearer token auth in generated servers | Roadmap |
| Automated tool testing on a schedule | Roadmap |
| Claude Desktop config auto-generator | Roadmap |
| Public cloud-hosted MCPHub instance | Roadmap |
