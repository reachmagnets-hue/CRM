from __future__ import annotations

from typing import Any, Dict, List, Tuple


class VectorStore:
    """Abstract vector store interface."""

    def upsert(self, items: List[Tuple[str, List[float], Dict[str, Any]]]) -> int:  # returns count
        raise NotImplementedError

    def query(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
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
        self._collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)
        return len(items)

    def query(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        res = self._collection.query(query_embeddings=[vector], n_results=top_k)
        out: List[Dict[str, Any]] = []
        for i in range(len(res["ids"][0])):
            out.append(
                {
                    "id": res["ids"][0][i],
                    "score": res["distances"][0][i] if "distances" in res else 0.0,
                    "metadata": res["metadatas"][0][i],
                    "document": res["documents"][0][i] if "documents" in res else "",
                }
            )
        return out


class PineconeStore(VectorStore):
    def __init__(self, api_key: str, index: str, tenant_id: str):
        # TODO: Implement Pinecone serverless adapter when enabled.
        raise NotImplementedError("Pinecone adapter not implemented yet")
