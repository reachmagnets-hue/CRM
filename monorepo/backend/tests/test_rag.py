from __future__ import annotations

from app.services.rag import build_prompt


def test_build_prompt_dedup_and_limits():
    hits = [
        {"metadata": {"doc_id": "A", "filename": "a.txt", "page": 1, "text": "Alpha content."}},
        # duplicate of same doc/page should be ignored
        {"metadata": {"doc_id": "A", "filename": "a.txt", "page": 1, "text": "Duplicate."}},
        {"metadata": {"doc_id": "B", "filename": "b.txt", "page": 2, "text": "Bravo"}},
    ]
    msgs = build_prompt("What is inside?", hits, max_snippets=10, max_chars=200)
    assert isinstance(msgs, list) and len(msgs) == 2
    user_msg = msgs[1]["content"]
    # Expect citations [1] and [2], but only two snippets due to dedup
    assert "[1]" in user_msg
    assert "[2]" in user_msg
    assert user_msg.count("Source:") == 2
