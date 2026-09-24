from typing import Optional
from types import TracebackType
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from research_graph.src.domain.interfaces import GraphRepository
from research_graph.src.infra.repository import PostgresGraphRepository

class PostgresUnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory
        self.session: Optional[AsyncSession] = None
        self.papers: Optional[GraphRepository] = None

    async def __aenter__(self) -> 'PostgresUnitOfWork':
        self.session = self.session_factory()
        self.papers = PostgresGraphRepository(self.session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None
    ) -> None:
        if self.session:
            if exc_type is not None:
                await self.rollback()
            else:
                await self.session.commit()
            await self.session.close()

    async def commit(self) -> None:
        if self.session:
            await self.session.commit()

    async def rollback(self) -> None:
        if self.session:
            await self.session.rollback()
