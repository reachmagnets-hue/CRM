from __future__ import annotations

from typing import AsyncIterator, Dict, List

import httpx

from ..config import SETTINGS


async def stream_generate(messages: List[Dict], model: str | None = None) -> AsyncIterator[str]:
    """Stream text from Ollama generate endpoint."""
    url = f"{SETTINGS.ollama_base}/api/generate"
    payload = {
        "model": model or SETTINGS.ollama_model,
        "prompt": _messages_to_prompt(messages),
        "stream": True,
    }
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url, json=payload) as r:
            async for line in r.aiter_lines():
                if not line:
                    continue
                try:
                    import json

                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                except Exception:
                    continue


def _messages_to_prompt(messages: List[Dict]) -> str:
    system = "You are a helpful assistant. Cite sources when provided."
    lines: List[str] = [f"<SYSTEM> {system}"]
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        lines.append(f"<{role.upper()}> {content}")
    return "\n".join(lines)
