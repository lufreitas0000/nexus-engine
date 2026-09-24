import pytest

from semantic_pdf_splitter.spatial.infrastructure.adapters.sentence_transformer_adapter import SentenceTransformerAdapter

def test_sentence_transformer_adapter_generates_embeddings():
    # Use lightweight model for testing
    adapter = SentenceTransformerAdapter(model_name="all-MiniLM-L6-v2")

    texts = ["This is a test sentence.", "This is another test sentence."]
    embeddings = adapter.generate_embeddings(texts)

    assert len(embeddings) == 2
    assert len(embeddings[0]) > 0  # should be 384 for all-MiniLM-L6-v2
    assert len(embeddings[1]) == len(embeddings[0])

    assert isinstance(embeddings[0], list)
    assert isinstance(embeddings[0][0], float)

def test_sentence_transformer_adapter_handles_empty_input():
    adapter = SentenceTransformerAdapter(model_name="all-MiniLM-L6-v2")
    embeddings = adapter.generate_embeddings([])
    assert embeddings == []
