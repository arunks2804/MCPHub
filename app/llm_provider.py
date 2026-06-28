import re
import httpx


def _strip_markdown(text: str) -> str:
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```\s*$", "", text, flags=re.MULTILINE)
    return text.strip()


async def call_llm(
    provider: str,
    model: str,
    api_key: str,
    system_prompt: str,
    user_prompt: str,
) -> str:
    provider = provider.lower()

    if provider == "ollama":
        return await _call_ollama(model, system_prompt, user_prompt)
    elif provider == "claude":
        return await _call_claude(model, api_key, system_prompt, user_prompt)
    elif provider == "openai":
        return await _call_openai(model, api_key, system_prompt, user_prompt)
    elif provider == "gemini":
        return await _call_gemini(model, api_key, system_prompt, user_prompt)
    elif provider == "mistral":
        return await _call_mistral(model, api_key, system_prompt, user_prompt)
    elif provider == "groq":
        return await _call_groq(model, api_key, system_prompt, user_prompt)
    else:
        raise ValueError(f"Unknown provider: {provider}")


async def _call_ollama(model: str, system_prompt: str, user_prompt: str) -> str:
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model or "mistral",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
            },
        )
        response.raise_for_status()
        return _strip_markdown(response.json()["message"]["content"])


async def _call_claude(model: str, api_key: str, system_prompt: str, user_prompt: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model or "claude-sonnet-4-6",
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return _strip_markdown(message.content[0].text)


async def _call_openai(model: str, api_key: str, system_prompt: str, user_prompt: str) -> str:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model=model or "gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return _strip_markdown(response.choices[0].message.content)


async def _call_gemini(model: str, api_key: str, system_prompt: str, user_prompt: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel(
        model_name=model or "gemini-1.5-pro",
        system_instruction=system_prompt,
    )
    response = gemini_model.generate_content(user_prompt)
    return _strip_markdown(response.text)


async def _call_mistral(model: str, api_key: str, system_prompt: str, user_prompt: str) -> str:
    from mistralai import Mistral

    client = Mistral(api_key=api_key)
    response = client.chat.complete(
        model=model or "mistral-large-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return _strip_markdown(response.choices[0].message.content)


async def _call_groq(model: str, api_key: str, system_prompt: str, user_prompt: str) -> str:
    from groq import AsyncGroq

    client = AsyncGroq(api_key=api_key)
    response = await client.chat.completions.create(
        model=model or "llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return _strip_markdown(response.choices[0].message.content)
