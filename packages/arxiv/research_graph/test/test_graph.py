import pytest
from research_graph.src.domain.graph import CitationGraph

def test_empty_graph():
    graph = CitationGraph()
    scores = graph.calculate_eigenvector_centrality()
    assert scores == {}

def test_single_node():
    graph = CitationGraph()
    graph.add_vertex("1")
    scores = graph.calculate_eigenvector_centrality()
    assert "1" in scores
    assert scores["1"] == 1.0

def test_simple_chain():
    # 1 -> 2 -> 3
    # 3 is cited by 2, 2 is cited by 1
    # 3 should have highest centrality
    graph = CitationGraph()
    graph.add_edge("1", "2")
    graph.add_edge("2", "3")

    scores = graph.calculate_eigenvector_centrality(num_iterations=50)
    assert scores["3"] > scores["2"] > scores["1"]

def test_star_graph():
    # 1, 2, 3 all cite 4
    graph = CitationGraph()
    graph.add_edge("1", "4")
    graph.add_edge("2", "4")
    graph.add_edge("3", "4")

    scores = graph.calculate_eigenvector_centrality()
    # 4 should be the highest
    assert scores["4"] > scores["1"]
    assert scores["4"] > scores["2"]
    assert scores["4"] > scores["3"]
    # 1, 2, 3 should be equal
    assert abs(scores["1"] - scores["2"]) < 1e-6
    assert abs(scores["1"] - scores["3"]) < 1e-6
