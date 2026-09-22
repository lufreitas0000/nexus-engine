import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as pg_insert

from research_graph.domain.model import PaperMetadata
from research_graph.ports.interfaces import GraphRepository
from research_graph.infra.schema import PaperORM, citation_table

class PostgresGraphRepository(GraphRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_paper(self, paper: PaperMetadata) -> None:
        try:
            date_obj = datetime.datetime.strptime(paper.published_date, "%Y%m%d")
        except ValueError:
            date_obj = datetime.datetime.now() # Fallback

        # Use standard insert with checking or dialact specific later.
        # For simplicity and testability in both SQLite and PG, we can just merge or handle exception
        # if we strictly need ON CONFLICT DO NOTHING for performance, we should check dialect.
        # Here we'll check if the paper exists first for generic support, or use dialect check.
        from sqlalchemy import select

        result = await self.session.execute(select(PaperORM).where(PaperORM.arxiv_id == paper.arxiv_id))
        if not result.scalars().first():
            stmt = insert(PaperORM).values(
                arxiv_id=paper.arxiv_id,
                title=paper.title,
                abstract=paper.abstract,
                published_date=date_obj,
            )
            await self.session.execute(stmt)

    async def save_edge(self, citing_id: str, cited_id: str) -> None:
        from sqlalchemy import select

        # Ensure nodes exist (basic foreign key compliance check for tests, or insert dummies)
        # Note: in real scenarios we might just try to insert and catch IntegrityError if we don't care.
        # For simple ON CONFLICT DO NOTHING on edge:
        result = await self.session.execute(
            select(citation_table).where(
                citation_table.c.referrer_id == citing_id,
                citation_table.c.referee_id == cited_id
            )
        )
        if not result.first():
            stmt = insert(citation_table).values(
                referrer_id=citing_id,
                referee_id=cited_id
            )
            try:
                await self.session.execute(stmt)
            except Exception:
                # ignore integrity errors if nodes don't exist yet in this simplified setup
                pass

    async def get_edges(self, arxiv_ids: list[str]) -> list[tuple[str, str]]:
        from sqlalchemy import select

        stmt = select(citation_table).where(
            citation_table.c.referrer_id.in_(arxiv_ids) | citation_table.c.referee_id.in_(arxiv_ids)
        )

        result = await self.session.execute(stmt)
        return [(row.referrer_id, row.referee_id) for row in result.fetchall()]
