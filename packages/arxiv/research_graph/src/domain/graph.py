from typing import List, Tuple, Dict
import math

class CitationGraph:
    def __init__(self) -> None:
        self.vertices: set[str] = set()
        self.edges: List[Tuple[str, str]] = [] # (citing, cited) -> citing cites cited

    def add_vertex(self, arxiv_id: str) -> None:
        self.vertices.add(arxiv_id)

    def add_edge(self, citing_id: str, cited_id: str) -> None:
        self.vertices.add(citing_id)
        self.vertices.add(cited_id)
        self.edges.append((citing_id, cited_id))

    def calculate_eigenvector_centrality(self, num_iterations: int = 100, damping_factor: float = 0.85) -> Dict[str, float]:
        """
        Computes the priority score of each paper using Eigenvector Centrality.
        A higher score means the paper is cited by other highly central papers.

        Using power iteration method.
        """
        if not self.vertices:
            return {}

        nodes = list(self.vertices)
        n = len(nodes)
        node_to_idx = {node: i for i, node in enumerate(nodes)}

        # Initialize centrality vector
        centrality = [1.0 / n] * n

        # Adjacency lists for cited_by (incoming edges)
        # We need A^T for authority, so if A_ij = 1 means i cites j
        # We want centrality of j to depend on centrality of i.
        # So centrality(j) = sum_i( A_ij * centrality(i) )
        cited_by: Dict[int, List[int]] = {i: [] for i in range(n)}

        for citing, cited in self.edges:
            cited_by[node_to_idx[cited]].append(node_to_idx[citing])

        # Power iteration
        for _ in range(num_iterations):
            new_centrality = [0.0] * n
            for i in range(n):
                # Calculate sum of centralities of nodes citing node i
                s = sum(centrality[j] for j in cited_by[i])

                # Apply damping factor (PageRank-like behavior to ensure strongly connected/convergence)
                # Damping factor d: probability of following a citation.
                # (1-d) / n: probability of jumping randomly.
                new_centrality[i] = (1 - damping_factor) / n + damping_factor * s

            # Normalize the vector to prevent overflow
            norm = math.sqrt(sum(c * c for c in new_centrality))
            if norm == 0:
                norm = 1.0 # fallback

            centrality = [c / norm for c in new_centrality]

        # Convert back to dict mapping id -> score
        return {nodes[i]: centrality[i] for i in range(n)}
