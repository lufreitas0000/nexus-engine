"""
Database schema initialization script.
Ensures PostgreSQL tables align with research_graph/infra/schema.py.
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from research_graph.infra.schema import metadata

async def init_models():
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/research_db"
    )
    engine = create_async_engine(db_url, echo=False)

    async with engine.begin() as conn:
        print("[INFO] Creating database schemas...")
        await conn.run_sync(metadata.create_all)

    await engine.dispose()
    print("[INFO] Database initialization complete.")

if __name__ == "__main__":
    asyncio.run(init_models())
