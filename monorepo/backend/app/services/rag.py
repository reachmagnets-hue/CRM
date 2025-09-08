from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Set

from ..config import SETTINGS
from .embed import embed_texts
from .vector import ChromaStore, VectorStore


def _get_store(tenant_id: str) -> VectorStore:
    if SETTINGS.store == "chroma":
        return ChromaStore(SETTINGS.chroma_dir, tenant_id)
    # Future: Pinecone adapter
    return ChromaStore(SETTINGS.chroma_dir, tenant_id)


async def retrieve(tenant_id: str, question: str, top_k: int = 5, where: Optional[Dict[str, Any]] = None) -> List[Dict]:
    [qvec] = await embed_texts([question])
    store = _get_store(tenant_id)
    hits = store.query(qvec, top_k=top_k, where=where)
    return hits


def build_prompt(
    question: str,
    hits: List[Dict],
    *,
    max_snippets: int = 8,
    max_chars: int = 4000,
) -> List[Dict]:
    """Build an instruction + context prompt for the LLM.

    - Deduplicates snippets by (doc_id, page) or (filename, page)
    - Caps total context length and number of snippets to keep prompts lean
    - Adds simple numeric citation markers [1], [2], ... to encourage grounded answers
    """
    def _norm_text(s: str) -> str:
        s = s.replace("\r", "")
        # collapse excessive newlines/spaces while keeping paragraphs
        lines = [ln.strip() for ln in s.split("\n")]
        return "\n".join([ln for ln in lines if ln])

    seen: Set[Tuple[Any, Any]] = set()
    context_lines: List[str] = []
    total_len = 0
    cite_idx = 1
    for h in hits:
        if len(context_lines) >= max_snippets or total_len >= max_chars:
            break
        meta = h.get("metadata", {}) or {}
        filename = meta.get("filename") or meta.get("doc_id") or "doc"
        page = meta.get("page", "?")
        key = (meta.get("doc_id") or filename, page)
        if key in seen:
            continue
        seen.add(key)
        text = _norm_text(str(meta.get("text", "")))
        if not text:
            continue
        snippet = f"[{cite_idx}] Source: {filename} p.{page}\n{text}"
        # If adding this snippet would exceed max_chars too much, trim text
        remaining = max_chars - total_len
        if remaining <= 0:
            break
        if len(snippet) > remaining:
            # keep header and truncate body
            header = f"[{cite_idx}] Source: {filename} p.{page}\n"
            body_budget = max(0, remaining - len(header))
            snippet = header + text[:body_budget]
        context_lines.append(snippet)
        total_len += len(snippet) + 2  # include spacing
        cite_idx += 1

    context = "\n\n".join(context_lines) if context_lines else "(no context found)"
    user_content = (
        "You are given CONTEXT snippets with citation markers like [1], [2]. "
        "Answer the QUESTION concisely and include citations by their markers when using information.\n\n"
        f"CONTEXT:\n{context}\n\nQUESTION: {question}"
    )
    messages = [
        {"role": "system", "content": "Use the provided CONTEXT to answer. If unsure, say you don't know."},
        {"role": "user", "content": user_content},
    ]
    return messages
