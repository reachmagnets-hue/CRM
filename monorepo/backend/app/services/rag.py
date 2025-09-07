from __future__ import annotations

from typing import Dict, List, Tuple

from ..config import SETTINGS
from .embed import embed_texts
from .vector import ChromaStore, VectorStore


def _get_store(tenant_id: str) -> VectorStore:
    if SETTINGS.store == "chroma":
        return ChromaStore(SETTINGS.chroma_dir, tenant_id)
    # Future: Pinecone adapter
    return ChromaStore(SETTINGS.chroma_dir, tenant_id)


async def retrieve(tenant_id: str, question: str, top_k: int = 5) -> List[Dict]:
    [qvec] = await embed_texts([question])
    store = _get_store(tenant_id)
    hits = store.query(qvec, top_k=top_k)
    return hits


def build_prompt(question: str, hits: List[Dict]) -> List[Dict]:
    context_lines: List[str] = []
    for h in hits:
        meta = h.get("metadata", {})
        filename = meta.get("filename", "doc")
        page = meta.get("page", "?")
        text = meta.get("text", "")
        context_lines.append(f"[Source: {filename} p.{page}]\n{text}")
    context = "\n\n".join(context_lines) if context_lines else "(no context found)"
    messages = [
        {"role": "system", "content": "Use the provided CONTEXT to answer. If unsure, say you don't know."},
        {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {question}\n\nAnswer with citations."},
    ]
    return messages
