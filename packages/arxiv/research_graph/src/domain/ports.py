from typing import Protocol, List, Dict, Any

class IVectorStore(Protocol):
    def upsert_documents(self, doc_ids: List[str], embeddings: List[List[float]], documents: List[str], metadatas: List[Dict[str, Any]]) -> None:
        pass

    def query_similar(self, query_embeddings: List[List[float]], n_results: int) -> Dict[str, Any]:
        pass

class IEmbeddingEngine(Protocol):
    async def generate_embedding(self, text: str) -> List[float]:
        pass
