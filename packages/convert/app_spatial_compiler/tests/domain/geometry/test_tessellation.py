from app_spatial_compiler.src.domain.models import SpatialNode
from app_spatial_compiler.src.domain.geometry.tessellation import recursive_xy_cut

def test_recursive_xy_cut_resolves_two_column_manifold() -> None:
    """
    Synthesizes a 2D Euclidean manifold representing a two-column layout.
    Column 1 resides in x in [10, 20]. Column 2 resides in x in [50, 60].
    A naive Y-sort would interleave the columns. The XY-Cut must project
    an empty vertical null-space between x=20 and x=50, partition the space,
    and establish a strict topological ordering: Column 1 -> Column 2.
    """
    # Column 1 (Left)
    node_a = SpatialNode(char="A", x0=10.0, y0=10.0, x1=20.0, y1=15.0)
    node_b = SpatialNode(char="B", x0=10.0, y0=20.0, x1=20.0, y1=25.0)
    
    # Column 2 (Right)
    node_c = SpatialNode(char="C", x0=50.0, y0=10.0, x1=60.0, y1=15.0)
    node_d = SpatialNode(char="D", x0=50.0, y0=20.0, x1=60.0, y1=25.0)
    
    # Deliberately shuffled input state
    manifold = [node_c, node_a, node_d, node_b] 
    
    # Morphism application
    ordered_nodes = recursive_xy_cut(manifold, min_dx=10.0, min_dy=2.0)
    
    # Assert the strict 1D topological reading order
    ordered_chars = [n.char for n in ordered_nodes]
    assert ordered_chars == ["A", "B", "C", "D"]

def test_recursive_xy_cut_preserves_single_column_topology() -> None:
    """
    Ensures the morphism functions identically to a standard topological sort
    when no orthogonal null-spaces exceed the delta threshold.
    """
    node_1 = SpatialNode(char="1", x0=10.0, y0=10.0, x1=20.0, y1=15.0)
    node_2 = SpatialNode(char="2", x0=12.0, y0=20.0, x1=22.0, y1=25.0)
    
    manifold = [node_2, node_1]
    
    ordered_nodes = recursive_xy_cut(manifold, min_dx=10.0, min_dy=10.0)
    
    ordered_chars = [n.char for n in ordered_nodes]
    assert ordered_chars == ["1", "2"]
