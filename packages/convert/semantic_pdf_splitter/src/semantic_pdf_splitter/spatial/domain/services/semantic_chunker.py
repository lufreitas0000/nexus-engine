from typing import List
import numpy as np

from semantic_pdf_splitter.spatial.domain.models import TextSegment, SemanticChunk
from semantic_pdf_splitter.spatial.domain.ports import EmbeddingProvider

class SemanticChunker:
    def __init__(self, embedding_provider: EmbeddingProvider, similarity_threshold: float = 0.75, overlap_window_size: int = 1):
        self.embedding_provider = embedding_provider
        self.similarity_threshold = similarity_threshold
        self.overlap_window_size = overlap_window_size

    def _aggregate_metadata(self, segments: List[TextSegment]) -> dict:
        headers = set()
        contains_tables = False
        contains_equations = False

        for seg in segments:
            if "section_header" in seg.metadata and seg.metadata["section_header"]:
                headers.add(seg.metadata["section_header"])
            if seg.metadata.get("contains_tables", False):
                contains_tables = True
            if seg.metadata.get("contains_equations", False):
                contains_equations = True

        return {
            "section_header": list(headers),
            "contains_tables": contains_tables,
            "contains_equations": contains_equations
        }

    def chunk_segments(self, segments: List[TextSegment]) -> List[SemanticChunk]:
        if not segments:
            return []

        # Only generate embeddings for segments that don't already have one
        texts_to_embed = [segment.text for segment in segments if segment.embedding is None]
        if texts_to_embed:
            new_embeddings = self.embedding_provider.generate_embeddings(texts_to_embed)
            embed_idx = 0
            for segment in segments:
                if segment.embedding is None:
                    segment.embedding = new_embeddings[embed_idx]
                    embed_idx += 1

        chunks = []
        current_chunk_segments = [segments[0]]

        for i in range(1, len(segments)):
            vec_u = np.array(segments[i-1].embedding)
            vec_v = np.array(segments[i].embedding)

            norm_u = np.linalg.norm(vec_u)
            norm_v = np.linalg.norm(vec_v)

            if norm_u == 0 or norm_v == 0:
                similarity = 0.0
            else:
                similarity = np.dot(vec_u, vec_v) / (norm_u * norm_v)

            if similarity >= self.similarity_threshold:
                current_chunk_segments.append(segments[i])
            else:
                # Chunk terminated
                chunk_embeddings = [seg.embedding for seg in current_chunk_segments if seg.embedding is not None]
                avg_embedding = np.mean(chunk_embeddings, axis=0).tolist() if chunk_embeddings else []
                aggregated_meta = self._aggregate_metadata(current_chunk_segments)

                chunks.append(SemanticChunk(
                    segments=current_chunk_segments,
                    average_embedding=avg_embedding,
                    aggregated_metadata=aggregated_meta
                ))

                # Start new chunk with overlap
                overlap_start_idx = max(0, len(current_chunk_segments) - self.overlap_window_size)
                overlap_segments = current_chunk_segments[overlap_start_idx:]
                current_chunk_segments = overlap_segments + [segments[i]]

        # Process the last chunk
        if current_chunk_segments:
            chunk_embeddings = [seg.embedding for seg in current_chunk_segments if seg.embedding is not None]
            avg_embedding = np.mean(chunk_embeddings, axis=0).tolist() if chunk_embeddings else []
            aggregated_meta = self._aggregate_metadata(current_chunk_segments)
            chunks.append(SemanticChunk(
                segments=current_chunk_segments,
                average_embedding=avg_embedding,
                aggregated_metadata=aggregated_meta
            ))

        return chunks
