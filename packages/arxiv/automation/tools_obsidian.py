import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from research_graph.src.infra.obsidian import ObsidianAdapter

async def export_graph_to_obsidian(graph_id: str, vault_path: str = "./vault") -> str:
    """Queries a complete graph from PostgreSQL and exports it to an Obsidian Markdown note."""
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/research_db"
    )
    engine = create_async_engine(db_url, echo=False)

    try:
        async with engine.connect() as conn:
            # Assumes the JSONB payload stores the extracted academic entities
            result = await conn.execute(
                text("SELECT payload FROM research_graph WHERE id = :graph_id"),
                {"graph_id": graph_id}
            )
            row = result.fetchone()

            if not row:
                return f"Graph ID {graph_id} not found."

            graph_data = row._mapping["payload"]

            exporter = ObsidianAdapter(vault_path=vault_path)
            filepath = exporter.export(graph_data)

            return f"Successfully exported graph {graph_id} to {filepath}"
    except Exception as e:
        return f"Export failed: {str(e)}"
    finally:
        await engine.dispose()
