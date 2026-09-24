import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

from research_graph.src.domain.model import PaperMetadata
from research_graph.src.infra.schema import Base
from research_graph.src.infra.uow import PostgresUnitOfWork

import pytest_asyncio

# Using SQLite with asyncio for testing
@pytest_asyncio.fixture
async def sqlite_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
def session_factory(sqlite_engine):
    return async_sessionmaker(sqlite_engine, expire_on_commit=False)

@pytest.mark.asyncio
async def test_repository_save_paper(session_factory):
    uow = PostgresUnitOfWork(session_factory)

    paper = PaperMetadata(
        arxiv_id="1234.5678",
        title="Test Paper",
        abstract="Test Abstract",
        published_date="20230101",
        authors=["Author 1", "Author 2"]
    )

    async with uow:
        await uow.papers.save_paper(paper)
        await uow.commit()

    # Verify
    async with session_factory() as session:
        result = await session.execute(text("SELECT * FROM papers WHERE arxiv_id='1234.5678'"))
        row = result.fetchone()
        assert row is not None
        assert row.title == "Test Paper"

@pytest.mark.asyncio
async def test_repository_save_edge(session_factory):
    uow = PostgresUnitOfWork(session_factory)

    paper1 = PaperMetadata("1", "Title 1", "Abst 1", "20230101", ["Author 1"])
    paper2 = PaperMetadata("2", "Title 2", "Abst 2", "20230101", ["Author 2"])

    async with uow:
        await uow.papers.save_paper(paper1)
        await uow.papers.save_paper(paper2)
        await uow.papers.save_edge("1", "2")
        await uow.commit()

    # Verify
    async with session_factory() as session:
        result = await session.execute(text("SELECT * FROM citations WHERE referrer_id='1' AND referee_id='2'"))
        row = result.fetchone()
        assert row is not None
