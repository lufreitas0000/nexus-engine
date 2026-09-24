import json
import redis.asyncio as redis
from arq import create_pool
from arq.connections import RedisSettings
from ingestion_engine.src.domain.model import IngestionTask, TaskType

async def push_arxiv_query(arxiv_id: str) -> str:
    """Push an arXiv ID into the local pipeline orchestrator queue."""
    redis_pool = await create_pool(RedisSettings())
    task = IngestionTask(
        task_id=f"arxiv_{arxiv_id}",
        task_type=TaskType.ARXIV_IDENTIFIER,
        payload=arxiv_id
    )

    from dataclasses import asdict
    task_dict = asdict(task)
    task_dict["task_type"] = task.task_type.value

    # Output dir logic copied from worker compatibility wrapper
    output_dir = "./output"

    # Use the correctly registered `process_ingestion_task` instead of the non-existent local route
    await redis_pool.enqueue_job("process_ingestion_task", task_dict, 3, output_dir)
    return f"Successfully queued arXiv ID: {arxiv_id} for ingestion."

async def read_dlq(limit: int = 5) -> str:
    """Read the top N failed tasks from the Redis Dead-Letter Queue."""
    client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    items = await client.lrange("pipeline_dlq", 0, limit - 1)
    await client.aclose()

    if not items:
        return "The DLQ is currently empty. No failed tasks."

    return json.dumps([json.loads(item) for item in items], indent=2)

async def check_completed_graphs(limit: int = 5) -> str:
    """Check the PostgreSQL database for recently completed research graphs."""
    import os
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/research_db"
    )
    engine = create_async_engine(db_url, echo=False)

    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT id, status FROM research_graph ORDER BY created_at DESC LIMIT :limit"), {"limit": limit})
            rows = result.fetchall()
            return f"Found {len(rows)} recent graphs: {[dict(r) for r in rows]}"
    except Exception as e:
        return f"Database query failed: {str(e)}"
    finally:
        await engine.dispose()

async def export_to_obsidian(arxiv_id: str, vault_path: str) -> str:
    """Format a completed research graph into Obsidian Markdown and save it."""
    import os

    # Check if the output markdown exists in the local sink
    markdown_path = os.path.join("./output/markdown", f"{arxiv_id}.md")
    if not os.path.exists(markdown_path):
        return f"Error: Processed markdown for {arxiv_id} not found."

    with open(markdown_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Format into Obsidian specific target structure
    obsidian_content = f"""# arXiv: {arxiv_id}

## Context
{content[:200]}...

## Definitions
-

## Lemmas & Theorems
-

## Proofs & Corollaries
-

## Reflections / Connections
-

---
### Raw Markdown Extracted:
{content}
"""

    os.makedirs(vault_path, exist_ok=True)
    target_path = os.path.join(vault_path, f"{arxiv_id}.md")

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(obsidian_content)

    return f"Successfully exported {arxiv_id} to Obsidian vault at {target_path}."

async def semantic_search_papers(query: str) -> str:
    """Query vector embeddings to synthesize literature or answer physics questions."""
    # Placeholder: In Step 10/11, this will connect to pgvector or Milvus
    return json.dumps({
        "query": query,
        "results": [
            {"arxiv_id": "mock_id", "snippet": f"Simulated semantic match for: {query}", "relevance": 0.95}
        ]
    })
