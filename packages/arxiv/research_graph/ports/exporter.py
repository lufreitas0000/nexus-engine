from typing import Protocol, Dict, Any

class GraphExporter(Protocol):
    def export(self, graph_data: Dict[str, Any]) -> str:
        ...
