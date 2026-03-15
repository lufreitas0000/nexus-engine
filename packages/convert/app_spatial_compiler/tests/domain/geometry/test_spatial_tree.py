from app_spatial_compiler.src.domain.models import SpatialNode
from app_spatial_compiler.src.domain.geometry.spatial_tree import SpatialKDTree

def test_kdtree_constructs_and_queries_nearest_neighbors() -> None:
    """
    Instantiates a contiguous array of SpatialNode entities and constructs
    a 2D KD-Tree to assert O(log N) K-nearest neighbor query resolution.
    This validates the foundational geometry for LaTeX graph grammars.
    """
    # Define a synthetic manifold representing a mathematical tensor
    # Base tensor 'R'
    node_r = SpatialNode(char="R", x0=10.0, y0=20.0, x1=15.0, y1=25.0)
    
    # Subscript '\mu' (shifted right, shifted down)
    node_mu = SpatialNode(char="\\mu", x0=16.0, y0=24.0, x1=19.0, y1=28.0)
    
    # Superscript '2' (shifted right, shifted up)
    node_sq = SpatialNode(char="2", x0=16.0, y0=15.0, x1=18.0, y1=19.0)
    
    # Mathematically disconnected term 'g' (spatially distant)
    node_g = SpatialNode(char="g", x0=50.0, y0=20.0, x1=55.0, y1=25.0)

    manifold = [node_r, node_mu, node_sq, node_g]

    # Domain Morphism Application
    tree = SpatialKDTree(manifold)

    # Query the 2 nearest neighbors to the base tensor 'R'
    neighbors = tree.query_knn(target=node_r, k=2)

    # Topological Assertions
    assert len(neighbors) == 2
    
    # The KD-Tree must resolve the spatially local indices
    assert node_mu in neighbors
    assert node_sq in neighbors
    
    # The distant tensor component must be excluded
    assert node_g not in neighbors
