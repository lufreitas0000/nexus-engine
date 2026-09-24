import chromadb
from typing import List, Dict, Any
from research_graph.src.domain.ports import IVectorStore

class ChromaDBAdapter(IVectorStore):
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="research_embeddings",
            metadata={"hnsw:space": "cosine"}
        )

    def upsert_documents(self, doc_ids: List[str], embeddings: List[List[float]], documents: List[str], metadatas: List[Dict[str, Any]]) -> None:
        self.collection.upsert(ids=doc_ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

    def query_similar(self, query_embeddings: List[List[float]], n_results: int = 5) -> Dict[str, Any]:
        return self.collection.query(query_embeddings=query_embeddings, n_results=n_results)
