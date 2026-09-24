from typing import List
from sentence_transformers import SentenceTransformer

from semantic_pdf_splitter.spatial.domain.ports import EmbeddingProvider

class SentenceTransformerAdapter(EmbeddingProvider):
    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
