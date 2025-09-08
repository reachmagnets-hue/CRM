from __future__ import annotations

from typing import Any, Dict, List, Tuple, Optional, cast


class VectorStore:
    """Abstract vector store interface."""

    def upsert(self, items: List[Tuple[str, List[float], Dict[str, Any]]]) -> int:  # returns count
        raise NotImplementedError

    def query(self, vector: List[float], top_k: int = 5, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError


class ChromaStore(VectorStore):
    def __init__(self, data_dir: str, tenant_id: str):
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        self._client = chromadb.Client(ChromaSettings(persist_directory=data_dir))
        self._collection = self._client.get_or_create_collection(name=f"docs-{tenant_id}")

    def upsert(self, items: List[Tuple[str, List[float], Dict[str, Any]]]) -> int:
        ids = [it[0] for it in items]
        embeddings = [it[1] for it in items]
        metadatas = [it[2] for it in items]
        documents = [m.get("text", "") for m in metadatas]
        # Chroma stubs have strict types; runtime accepts plain lists.
        self._collection.upsert(  # type: ignore[arg-type]
            ids=ids,
            embeddings=cast(Any, embeddings),
            metadatas=cast(Any, metadatas),
            documents=documents,
        )
        return len(items)

    def query(self, vector: List[float], top_k: int = 5, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {"query_embeddings": [vector], "n_results": top_k}
        if where:
            kwargs["where"] = where
        res = self._collection.query(**kwargs)
        out: List[Dict[str, Any]] = []
        ids = cast(Any, res.get("ids") or [[]])
        dists = cast(Any, res.get("distances") or [[]])
        metas = cast(Any, res.get("metadatas") or [[]])
        docs = cast(Any, res.get("documents") or [[]])
        row_len = len(ids[0]) if ids and len(ids) > 0 else 0
        for i in range(row_len):
            score = float(dists[0][i]) if (dists and len(dists) > 0 and len(dists[0]) > i) else 0.0
            meta = metas[0][i] if (metas and len(metas) > 0 and len(metas[0]) > i) else {}
            doc = docs[0][i] if (docs and len(docs) > 0 and len(docs[0]) > i) else ""
            out.append({"id": ids[0][i], "score": score, "metadata": meta, "document": doc})
        return out


class PineconeStore(VectorStore):
    def __init__(self, api_key: str, index: str, tenant_id: str):
        # TODO: Implement Pinecone serverless adapter when enabled.
        raise NotImplementedError("Pinecone adapter not implemented yet")
