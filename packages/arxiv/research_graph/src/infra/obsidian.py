import os
from typing import Dict, Any


class ObsidianAdapter:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        os.makedirs(self.vault_path, exist_ok=True)

    def export(self, graph_data: Dict[str, Any]) -> str:
        title = graph_data.get("title", "Untitled_Concept")
        safe_title = "".join([c for c in title if c.isalnum() or c == ' ']).rstrip()
        filename = f"{safe_title.replace(' ', '_')}.md"
        filepath = os.path.join(self.vault_path, filename)

        content = self._format_markdown(title, graph_data)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath

    def _format_markdown(self, title: str, data: Dict[str, Any]) -> str:
        return f"""# {title}

## Context
{data.get('context', 'N/A')}

## Definition
{data.get('definition', 'N/A')}

## Lemma / Theorem / Proof / Corollaries
{data.get('math_details', 'N/A')}

## Reflection / Connections
{data.get('connections', 'N/A')}

## Further Read
{data.get('references', 'N/A')}
"""
