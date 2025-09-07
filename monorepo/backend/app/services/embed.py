from __future__ import annotations

from typing import List

import httpx

from ..config import SETTINGS


async def embed_texts(texts: List[str]) -> List[List[float]]:
    url = f"{SETTINGS.ollama_base}/api/embeddings"
    async with httpx.AsyncClient(timeout=None) as client:
        res = await client.post(url, json={"model": SETTINGS.embed_model, "input": texts})
        res.raise_for_status()
        data = res.json()
        # Ollama returns one embedding for single input; batch emulate
        if isinstance(texts, list) and len(texts) == 1 and "embedding" in data:
            return [data["embedding"]]
        # If server supports batch, expect 'data': [{embedding: [...]}]
        if "data" in data:
            return [item["embedding"] for item in data["data"]]
        # Fallback single
        return [data.get("embedding", [])]
