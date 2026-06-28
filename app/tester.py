import time
import ast
import os
import re
import httpx


async def test_tool(
    server_id: str,
    tool_name: str,
    parameters: dict,
    api_key: str,
) -> dict:
    tool_file = os.path.join("generated", server_id, "tools", f"{tool_name}.py")

    if not os.path.exists(tool_file):
        return {"success": False, "status_code": None, "response": None, "latency_ms": 0, "error": f"Tool file not found: {tool_file}"}

    try:
        with open(tool_file, "r") as f:
            source = f.read()

        api_endpoint, http_method, base_url = _extract_request_info(source, tool_name)

        url = _build_url(base_url, api_endpoint, parameters)
        query_params = {k: v for k, v in parameters.items() if f"{{{k}}}" not in api_endpoint}

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            if http_method.upper() in ("GET", "DELETE"):
                resp = await client.request(http_method.upper(), url, params=query_params, headers=headers)
            else:
                resp = await client.request(http_method.upper(), url, json=parameters, headers=headers)
        latency_ms = int((time.time() - start) * 1000)

        try:
            response_body = resp.json()
        except Exception:
            response_body = resp.text

        return {
            "success": resp.status_code < 400,
            "status_code": resp.status_code,
            "response": response_body,
            "latency_ms": latency_ms,
            "error": None if resp.status_code < 400 else f"{resp.status_code} {resp.reason_phrase}",
        }

    except Exception as e:
        return {"success": False, "status_code": None, "response": None, "latency_ms": 0, "error": str(e)}


async def test_all_tools(server_id: str, api_key: str, sample_params: dict) -> dict:
    tools_dir = os.path.join("generated", server_id, "tools")
    if not os.path.exists(tools_dir):
        return {"total": 0, "passed": 0, "failed": 0, "results": [], "error": "Server not found"}

    tool_names = [f[:-3] for f in os.listdir(tools_dir) if f.endswith(".py") and not f.startswith("_")]
    results = []

    for tool_name in tool_names:
        params = sample_params.get(tool_name, {})
        result = await test_tool(server_id, tool_name, params, api_key)
        results.append({
            "tool": tool_name,
            "success": result["success"],
            "latency_ms": result["latency_ms"],
            "error": result.get("error"),
        })

    passed = sum(1 for r in results if r["success"])
    return {
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
    }


def _extract_request_info(source: str, tool_name: str):
    endpoint_match = re.search(r'endpoint\s*=\s*["\']([^"\']+)["\']', source)
    method_match = re.search(r'method\s*=\s*["\']([^"\']+)["\']', source)
    base_match = re.search(r'BASE_URL\s*=\s*["\']([^"\']+)["\']|base_url\s*=\s*["\']([^"\']+)["\']', source)

    api_endpoint = endpoint_match.group(1) if endpoint_match else f"/{tool_name}"
    http_method = method_match.group(1) if method_match else "GET"
    base_url = (base_match.group(1) or base_match.group(2)) if base_match else ""

    return api_endpoint, http_method, base_url


def _build_url(base_url: str, endpoint: str, parameters: dict) -> str:
    url = base_url.rstrip("/") + "/" + endpoint.lstrip("/")
    for k, v in parameters.items():
        url = url.replace(f"{{{k}}}", str(v))
    return url
