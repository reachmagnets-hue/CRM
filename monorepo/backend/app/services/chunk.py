from __future__ import annotations

from typing import List


def chunk_text(text: str, max_chars: int = 1200, overlap: int = 150) -> List[str]:
    chunks: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        end = min(i + max_chars, n)
        chunks.append(text[i:end])
        i = end - overlap
        if i < 0:
            i = 0
    return [c.strip() for c in chunks if c.strip()]
