import json
from research_graph.src.domain.ports import IVectorStore, IEmbeddingEngine

async def perform_semantic_search(
    query_text: str,
    vector_store: IVectorStore,
    embedding_engine: IEmbeddingEngine,
    n_results: int = 3
) -> str:
    """Morphism mapping a text query to formatted literature results."""
    query_embedding = await embedding_engine.generate_embedding(query_text)
    search_results = vector_store.query_similar([query_embedding], n_results)

    if not search_results.get("documents") or not search_results["documents"][0]:
        return f"No relevant literature found for query: '{query_text}'"

    formatted_results = [
        {"document": doc, "metadata": search_results["metadatas"][0][i]}
        for i, doc in enumerate(search_results["documents"][0])
    ]
    return json.dumps(formatted_results, indent=2)
